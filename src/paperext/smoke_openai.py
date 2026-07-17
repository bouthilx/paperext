"""Connectivity smoke-check for the OpenAI backend.

Makes one trivial chat completion to prove authentication + model access,
without touching the extraction pipeline. Parallels the ``vertexai-check``
smoke-check (A2 #7) for the Vertex backend.

Requires ``OPENAI_API_KEY`` in the environment (see the ``[env]`` config
section / ``PAPEREXT_OPENAI_*`` overrides):

    OPENAI_API_KEY=... openai-check                 # uses CFG.openai.model
    OPENAI_API_KEY=... openai-check --model gpt-5.6-terra
"""

import argparse
import sys

from paperext import CFG
from paperext.log import logger

PROG = "openai-check"


def _default_client():
    # Imported lazily so the module (and its tests) load without the optional
    # ``openai`` dependency installed.
    import openai

    return openai.OpenAI()


def run_check(model, message="Reply with the single word: ok.", client=None):
    """Make one trivial completion and return ``(reply_text, usage)``.

    ``client`` defaults to a fresh ``openai.OpenAI()`` (reads ``OPENAI_API_KEY``
    from the environment); it is injectable so the check can be exercised
    offline with a mock.
    """
    client = client if client is not None else _default_client()
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": message}],
    )
    reply = completion.choices[0].message.content
    usage = getattr(completion, "usage", None)
    return reply, usage


def main(argv=None):
    parser = argparse.ArgumentParser(prog=PROG, description=__doc__)
    parser.add_argument(
        "--model",
        default=CFG.openai.model,
        help="OpenAI model to test (default: CFG.openai.model = %(default)r)",
    )
    options = parser.parse_args(argv)

    try:
        reply, usage = run_check(options.model)
    except Exception as e:  # noqa: BLE001 - surface any failure as a failed check
        logger.error(f"OpenAI smoke-check failed for model {options.model!r}: {e}")
        print(f"FAIL: {e}", file=sys.stderr)
        return 1

    print(f"OK: model={options.model!r} reply={reply!r} usage={usage}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
