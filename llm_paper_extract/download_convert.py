from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from .utils import python_module

# Avoid hanging forever on unresponsive / paywalled hosts. urlretrieve() has no
# per-call timeout parameter, so it relies on this process-wide default.
socket.setdefaulttimeout(30)

# Minimum delay between download attempts and retry/backoff settings for
# transient network failures (unreachable network, DNS hiccups, resets,
# timeouts). Hammering a single host (e.g. arxiv.org) with hundreds of
# back-to-back requests triggers exactly these errors as throttling, even
# though the host is otherwise reachable.
REQUEST_DELAY_SECONDS = 1.0
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5

PROG = f"python3 -m {python_module(__file__)}"

DESCRIPTION = """
Utility to download and convert a list of papers' pdfs -> "txts.

stdout will contain the list of files successfully converted separated by '\\n'.
"""

EPILOG = f"""
Example:
  $ {PROG} paperoni-2024-07-04.json
    [DEBUG]
    data/cache/arxiv/1901.07186.txt
    data/cache/arxiv/1906.05433.txt
    ...
    data/cache/html/874f823e6462acbbb07cc57d32e09217.txt
    data/cache/html/8a46fcbc0c34ea85102920cba7039290.txt
    ...
    data/cache/openreview/0k_DN90uWF.txt
    data/cache/openreview/2Q8TZWAHv4.txt
    ...
    data/cache/pdf/80c62591b54231aa42e4418fe3d45e8f.txt
    data/cache/pdf/81709b4783324a59fd2632ee694e9071.txt
    ...
    Successfully downloaded and converted 587 out of 867 papers
    arxiv:455/455
    html:3/3
    openreview:52/52
    pdf:77/145
  $ {PROG} paperoni-2024-07-04.json > data/query_set.txt
    [DEBUG]
    Successfully downloaded and converted 587 out of 867 papers
    arxiv:455/455
    html:3/3
    openreview:52/52
    pdf:77/145
"""


def _is_transient(e: Exception) -> bool:
    # HTTPError with a definitive status code (403 Forbidden, 404 Not Found, ...)
    # won't change on retry. Everything else funneled through OSError -
    # connection reset, DNS resolution failure, timeout, "unreachable network" -
    # tends to be throttling/transient, especially when it appears only after
    # many rapid requests to the same host.
    if isinstance(e, urllib.error.HTTPError):
        return e.code in (429, 500, 502, 503, 504)
    return isinstance(e, OSError)


def convert_pdf(pdf, text, pdf_link):
    pdf.parent.mkdir(parents=True, exist_ok=True)
    if not pdf.exists():
        print("Downloading from", pdf_link, "to", str(pdf), file=sys.stderr)
        for attempt in range(1, MAX_RETRIES + 1):
            time.sleep(REQUEST_DELAY_SECONDS)
            try:
                urllib.request.urlretrieve(pdf_link, str(pdf))
                break
            except (OSError, ValueError) as e:
                # OSError covers urllib.error.URLError/HTTPError as well as lower-level
                # network failures (connection reset, timeout, DNS failure, SSL errors)
                # that the original except clause didn't catch and that crashed the
                # whole batch instead of being logged as a single paper failure.
                if attempt < MAX_RETRIES and _is_transient(e):
                    wait = RETRY_BACKOFF_SECONDS * attempt
                    print(
                        f"Transient failure downloading {pdf_link} "
                        f"(attempt {attempt}/{MAX_RETRIES}): {e}. Retrying in {wait}s...",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                    continue
                print(f"Failed to download {pdf_link}: {e}", file=sys.stderr)
                pdf.unlink(missing_ok=True)
                return None
    if not text.exists():
        # pdftotext comes from https://poppler.freedesktop.org/
        try:
            cmd = ["pdftotext", str(pdf), str(text)]
            cp = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            print(cp.stdout, file=sys.stderr)
            if cp.returncode:
                raise subprocess.CalledProcessError(
                    cp.returncode, cmd, cp.stdout, cp.stderr
                )
        except subprocess.CalledProcessError as e:
            print(f"Failed to convert {pdf} to {text}: {e}", file=sys.stderr)
            pdf.unlink(missing_ok=True)
            text.unlink(missing_ok=True)
            return None
    return text


def download_and_convert_paper(
    paper_id: str | None, links: list, cache_dir: Path, check_only=False
):
    text = None
    link_types = []
    while links:
        l: dict = links.pop(0)
        link_type = l["type"].split(".")[0]
        sources = [
            (
                l["type"].lower().startswith("arxiv"),
                cache_dir / f"arxiv/{l['link']}.pdf",
                f"https://arxiv.org/pdf/{l['link']}",
            ),
            (
                "url" in l,
                cache_dir / link_type / f"{l['link']}.pdf",
                l.get("url", None),
            ),
        ]
        if paper_id is not None:
            sources.append((True, cache_dir / link_type / f"{paper_id}.pdf", l["link"]))
        for _if, pdf, pdf_link in sources:
            if not _if:
                continue
            text = pdf.with_suffix(".txt")
            link_types.append(link_type)
            if text.exists():
                print(f"Found existing {text}", file=sys.stderr)
                links[:] = []
                break
            if check_only:
                continue
            if convert_pdf(pdf, text, pdf_link) is not None:
                links[:] = []
                break
            print("retrying...", file=sys.stderr)
        else:
            text = None
    if text is not None:
        link_types = link_types[-1:]
    return text, sorted(set(link_types))


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input",
        metavar="JSON",
        type=Path,
        help="Paperoni json output of papers to download and convert pdfs -> txts",
    )
    parser.add_argument(
        "--cache-dir",
        metavar="DIR",
        type=Path,
        default=Path("data/cache/"),
        help="Directory to store downloaded and converted pdfs -> txts",
    )
    options = parser.parse_args(argv)

    paperoni = json.loads(options.input.read_text())

    options.cache_dir.mkdir(parents=True, exist_ok=True)

    completed = []
    failed = []
    for p in paperoni:
        text = None
        links = [l for l in p["links"] if l["type"].lower().startswith("arxiv")]
        links.extend(
            [
                l
                for l in p["links"]
                if "pdf" in l["type"].lower().split(".")
                and l["type"].lower().startswith("openreview")
            ]
        )
        links.extend([l for l in p["links"] if "pdf" in l["type"].lower().split(".")])
        links.extend([l for l in p["links"] if "pdf" in l["link"].lower()])
        if not links:
            print(
                f"Could not find any pdf links for paper {p['links']} in",
                *p["links"],
                sep="\n",
                file=sys.stderr,
            )
        else:
            print(f'Downloading and converting {p["title"]}', file=sys.stderr)

        for check_only in (True, False):
            text, link_types = download_and_convert_paper(
                p["paper_id"], links[:], options.cache_dir, check_only=check_only
            )
            if text is not None:
                completed.append((p["paper_id"], text, link_types))
                break
        else:
            failed.append((p["paper_id"], text, link_types))
            print(
                f'Failed to download or convert {p["paper_id"]}:{p["title"]} with links {link_types}',
                file=sys.stderr,
            )

    print(*sorted(str(text) for _, text, _ in completed), sep="\n")

    print(
        f"Successfully downloaded and converted {len(completed)} out of "
        f"{len(completed) + len(failed)} papers",
        file=sys.stderr,
    )
    for t in sorted(
        set(sum([l for _, _, l in completed] + [l for _, _, l in failed], []))
    ):
        c, f = (sum(t in l for _, _, l in completed), sum(t in l for _, _, l in failed))
        print(f"{t}:{c}/{c+f}", file=sys.stderr)


if __name__ == "__main__":
    main()
