"""Connectivity smoke-check for any model backend.

Dispatches to the selected backend's ``smoke_check()`` -- one trivial completion
proving auth + model access, without touching the extraction pipeline.

    OPENAI_API_KEY=... backend-check --platform openai
    backend-check --platform vertexai --model models/gemini-1.5-pro
"""

import argparse
import sys

from paperext import CFG
from paperext.backends import available, get_backend
from paperext.log import logger

PROG = "backend-check"


def main(argv=None):
    parser = argparse.ArgumentParser(prog=PROG, description=__doc__)
    parser.add_argument(
        "--platform",
        default=CFG.platform.select,
        choices=available() or None,
        help="Backend to test (default: CFG.platform.select = %(default)r)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model to test (default: the backend's configured model)",
    )
    options = parser.parse_args(argv)

    try:
        backend = get_backend(options.platform)
        reply, usage = backend.smoke_check(model=options.model)
    except Exception as e:  # noqa: BLE001 - surface any failure as a failed check
        logger.error(
            f"Backend smoke-check failed for platform {options.platform!r}: {e}"
        )
        print(f"FAIL: {e}", file=sys.stderr)
        return 1

    model = options.model or backend.model
    print(
        f"OK: platform={options.platform!r} model={model!r} "
        f"reply={reply!r} usage={usage}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
