import argparse
import asyncio
import bdb
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple

import instructor
import pydantic_core

from paperext import CFG
from paperext.backends import available, get_backend
from paperext.log import logger
from paperext.paths import platform_bucket
from paperext.structured_output import STRUCT_MODULES, ai4hcat, mdl
from paperext.utils import Paper, build_validation_set


def get_first_message() -> str:
    return STRUCT_MODULES[CFG.platform.struct].FIRST_MESSAGE


def get_system_message() -> str:
    return STRUCT_MODULES[CFG.platform.struct].SYSTEM_MESSAGE


def get_extraction_response() -> (
    ai4hcat.model.ExtractionResponse | mdl.model.ExtractionResponse
):
    return STRUCT_MODULES[CFG.platform.struct].ExtractionResponse


def get_paper_extractions() -> (
    ai4hcat.model.PaperExtractions | mdl.model.PaperExtractions
):
    return STRUCT_MODULES[CFG.platform.struct].PaperExtractions


PROG = f"{Path(__file__).stem.replace('_', '-')}"

DESCRIPTION = """
Utility to query Chat-GPT on papers

Queries logs will be written in ${PAPEREXT_DIR_LOG}/DATE.query.dbg
"""

EPILOG = f"""
Example:
  $ {PROG} --input data/query_set.txt
"""

# Backends register themselves in paperext.backends (SDK-guarded). query() picks
# one via get_backend(CFG.platform.select); see paperext/backends/.


async def extract_from_research_paper(
    client: instructor.client.AsyncInstructor,
    message: str,
    rate_limit_errors: Tuple[type[BaseException], ...] = (),
) -> Tuple[Any, Any]:
    """Extract Models, Datasets and Frameworks names from a research paper."""
    retries = [True] * 1
    while True:
        try:
            extractions, usage = await client.chat.completions.create_with_completion(
                response_model=get_paper_extractions(),
                messages=[
                    {
                        "role": "system",
                        "content": get_system_message(),
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
                max_retries=1,
            )
            return extractions, usage
        except rate_limit_errors as e:
            asyncio.sleep(60)
            if retries:
                retries.pop()
                continue
            raise e


async def batch_extract_models_names(
    client: instructor.client.AsyncInstructor,
    papers_fn: List[Path],
    destination: Path = CFG.dir.queries,
    rate_limit_errors: Tuple[type[BaseException], ...] = (),
) -> List:
    destination.mkdir(parents=True, exist_ok=True)

    for paper_fn in papers_fn:
        paper = paper_fn.name

        count = 0
        for line in paper_fn.read_text().splitlines():
            count += len([w for w in line.strip().split() if w])

        data = []

        for i, message in enumerate((get_first_message(),)):
            f = destination / paper
            f = f.with_stem(f"{f.stem}_{i:02}").with_suffix(".json")

            try:
                response = get_extraction_response().model_validate_json(f.read_text())
            except (
                FileNotFoundError,
                pydantic_core._pydantic_core.ValidationError,
            ) as e:
                logger.error(e, exc_info=True)
                logging.error(e, exc_info=True)

                message = message.format(*data, paper_fn.read_text())

                extractions, usage = await extract_from_research_paper(
                    client, message, rate_limit_errors=rate_limit_errors
                )

                f.parent.mkdir(parents=True, exist_ok=True)

                try:
                    response = get_extraction_response()(
                        paper=paper,
                        words=count,
                        extractions=extractions,
                        usage=usage,
                    )
                    f.write_text(response.model_dump_json(indent=2))

                except pydantic_core._pydantic_core.PydanticSerializationError:
                    response = get_extraction_response()(
                        paper=paper,
                        words=count,
                        extractions=extractions,
                        usage=None,
                    )
                    f.write_text(response.model_dump_json(indent=2))

            logger.info(response.model_dump_json(indent=2))

            models = [m.name.value for m in response.extractions.models]
            datasets = [d.name.value for d in response.extractions.datasets]
            libraries = [f.name.value for f in response.extractions.libraries]

            data = [models, datasets, libraries]


async def ignore_exceptions(
    client: instructor.client.AsyncInstructor,
    validation_set: List[Path],
    *args,
    **kwargs,
):
    for paper in validation_set:
        try:
            await batch_extract_models_names(client, [paper], *args, **kwargs)
        except bdb.BdbQuit:
            raise
        except Exception as e:
            logger.error(
                f"Failed to extract paper information from {paper.name}: {e}",
                exc_info=True,
            )
            logging.error(
                f"Failed to extract paper information from {paper.name}: {e}",
                exc_info=True,
            )


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--platform",
        type=str,
        choices=available() or None,
        default=CFG.platform.select,
        help="Platform to use",
    )
    parser.add_argument(
        "--papers", nargs="*", type=str, default=None, help="Papers to analyse"
    )
    parser.add_argument(
        "--input",
        metavar="TXT",
        type=Path,
        default=None,
        help="List of papers to analyse",
    )
    parser.add_argument(
        "--paperoni",
        metavar="JSON",
        type=Path,
        default=None,
        help="Paperoni json output of papers to query on converted pdfs -> txts",
    )
    options = parser.parse_args(argv)

    CFG.platform.select = options.platform

    if options.paperoni:
        papers = [Paper(p) for p in json.loads(options.paperoni.read_text())]
        papers = [p.get_link_id_pdf() for p in papers]
        papers = [p for p in papers if p is not None]
    elif options.input:
        papers = [
            Path(paper)
            for paper in Path(options.input).read_text().splitlines()
            if paper.strip()
        ]
    elif options.papers:
        papers = [Path(paper) for paper in options.papers if paper.strip()]
    else:
        papers = build_validation_set()
        for p in papers:
            logger.info(p)

    if not all([p.exists() for p in papers]):
        papers = [Path(CFG.dir.cache / f"arxiv/{paper}.txt") for paper in papers]

    assert all([p.exists() for p in papers])

    backend = get_backend(CFG.platform.select)
    client = backend.make_client()

    # Set logging to DEBUG to print OpenAI requests
    # TODO: there must be a better way that would not impact other usage of
    # logging
    LOG_FILE = CFG.dir.log / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logging.basicConfig(
        filename=LOG_FILE.with_suffix(f".{PROG}.dbg"), level=logging.DEBUG, force=True
    )

    asyncio.run(
        ignore_exceptions(
            client,
            [paper.absolute() for paper in papers],
            destination=platform_bucket(CFG.dir.queries),
            rate_limit_errors=backend.rate_limit_errors,
        )
    )


if __name__ == "__main__":
    main()
