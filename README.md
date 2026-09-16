# paperext

[![PyPI - Version](https://img.shields.io/pypi/v/paperext.svg)](https://pypi.org/project/paperext)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/paperext.svg)](https://pypi.org/project/paperext)

-----

## Table of Contents

- [Installation](#installation)
- [Configuration](#Configuration)
- [Usage](#usage)
- [License](#license)

## Installation

Requires Python >= 3.14 (`uv` installs it on demand; see `.python-version`).

With [uv](https://docs.astral.sh/uv/) (recommended -- `uv.lock` pins the
resolution):

```console
uv sync --extra openai        # or --extra vertexai, --extra fulltext, or --all-extras
uv run [command]
```

The `fulltext` extra pulls in [paperoni](https://github.com/mila-iqia/paperoni)
for PDF location/download (`download-convert`).

Or with pip:

```console
pip install -e ".[openai]"
pip install -e ".[vertexai]"
```

## Configuration

Set the environment variable `PAPEREXT_CONFIG` to point to your configuration
file. A default configuration file is provided in
[config.mdl.ini](./config.mdl.ini).

```console
export PAPEREXT_CONFIG=config.ini
```

> [!NOTE]
> All configuration can be overwritten with environment variables in the form of
`PAPEREXT_{SECTION}_{OPTION}` such as:
>
> ```console
> export PAPEREXT_DIR_DATA=path/to/data
> ```

### OpenAI setup

The OpenAI backend runs against the OpenAI API directly (no Google Cloud
required). Install the extra and provide credentials at runtime:

```console
pip install "paperext[openai]"
export OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Optional, if your account requires them:
export OPENAI_ORG_ID=org-XXXXXXXXXXXX
export OPENAI_PROJECT_ID=proj-XXXXXXXXXXXX
```

`[platform] select = openai` is the default. The model defaults to
`[openai] model` (a GPT-5.6 tier) and can be overridden at runtime:

```console
export PAPEREXT_OPENAI_MODEL=gpt-5.6-terra
```

Results are stored per `<provider>/<model>/`, e.g.
`data/mdl/queries/openai/gpt-5.6-sol/`.

Verify connectivity with the backend smoke-check (one trivial completion, no
pipeline — works for any backend):

```console
OPENAI_API_KEY=... backend-check --platform openai                 # uses CFG.openai.model
OPENAI_API_KEY=... backend-check --platform openai --model gpt-5.6-terra
# OK: platform='openai' model='gpt-5.6-sol' reply='ok' usage=CompletionUsage(...)
```

### Local OpenAI-compatible server

The `local` backend talks to any self-hosted model behind an OpenAI-compatible
`/v1/chat/completions` endpoint (vLLM, SGLang, llama.cpp, ...). It only needs
the `openai` extra. Point it at the server and the model id as served:

```console
export PAPEREXT_PLATFORM_SELECT=local
export PAPEREXT_LOCAL_BASE_URL=http://host:8888/v1
export PAPEREXT_LOCAL_MODEL=<served model id>
export LOCAL_API_KEY=...          # bearer token; any non-empty value if unchecked
backend-check --platform local
```

Like `OPENAI_API_KEY`, `LOCAL_API_KEY` is listed under `[env]` and provided at
runtime, never in the tracked config file. `[local] mode` selects how the
structured output is requested: `tools` (one forced tool call -- the server
must parse tool calls, e.g. vLLM `--enable-auto-tool-choice --tool-call-parser
...`) or `json_schema` (`response_format` structured outputs, the fallback when
the tool-call parser is unreliable). Results are stored under
`local/<model>/`; token counts come from the local tokenizer and are not
comparable with the cloud backends'.

## Usage

### download-convert

Locates and downloads each paper's PDF with paperoni's fulltext resolver
(arxiv, openreview, mlr, direct pdf links, and DOIs through CrossRef, OpenAlex
and publisher APIs), then converts it with `pdftotext` (from
https://poppler.freedesktop.org/) into `<cache>/fulltext/<paper_id>/fulltext.txt`.

Requirements:

- the `fulltext` extra (`uv sync --extra fulltext`);
- a paperoni config at `paperoni/config.yaml` (gitignored; `[env]
  PAPERONI_CONFIG` in `config.mdl.ini` points there). Start from
  [paperoni/config.example.yaml](./paperoni/config.example.yaml): set `mailto`,
  and add `api_keys` (Elsevier / Wiley TDM, ScraperAPI) and the OpenReview
  credentials if you have them -- without them, paywalled DOIs, Cloudflare-fronted
  publishers and OpenReview-only papers are reported as failures.

```console
usage: download-convert [-h] [--paperoni JSON] [--arxiv STR [STR ...]]
                        [--url STR [STR ...]] [--cache-dir DIR]
                        [--concurrency N] [--report JSON]

options:
  --paperoni JSON   Paperoni json output of papers to download and convert pdfs -> txts
  --arxiv STR ...   List of arXiv ids use to download and convert pdfs -> txts
  --url STR ...     List of pdf urls to download and convert pdfs -> txts
  --cache-dir DIR   Directory to store downloaded and converted pdfs -> txts
  --concurrency N   Papers downloaded in parallel (default 8; requests to one host
                    are further capped by the paperoni config's fetch.simultaneous)
  --report JSON     Per-paper outcome report (default: logs/download-convert_<timestamp>.json)

Example:
  $ PAPEREXT_LOGGING_LEVEL=INFO download-convert --paperoni data/paperoni-2026-01-01-2026-12-31-PR_2026-09-16.json > data/query_set.txt
    ...
    Successfully downloaded and converted 23 out of 45 papers
    arxiv:20/20
    doi.crossref:1/1
    doi.openalex:2/2
    no-fulltext:0/22
```

A progress bar (count, elapsed, ETA) is drawn on stderr when it is a terminal.
stdout lists the converted text files; the report records, per paper, the refs
tried, which resolver produced the PDF (`source`) and the error otherwise, so
download drop-out can be quantified per publisher. Re-runs are cheap: papers
with an existing text are skipped, and paperoni keeps its own PDF cache under
`data_path` (see the config).

### query

An OpenAI API Key is required to run this utility:

```console
export OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

```console
usage: query [-h] [--platform {openai}] [--papers [PAPERS ...]] [--input TXT] [--paperoni JSON]

Utility to query Chat-GPT on papers

Queries logs will be written in ${PAPEREXT_DIR_LOG}/DATE.query.dbg

options:
  -h, --help            show this help message and exit
  --platform {openai}   Platform to use
  --papers [PAPERS ...]
                        Papers to analyse
  --input TXT           List of papers to analyse
  --paperoni JSON       Paperoni json output of papers to query on converted pdfs -> txts

Example:
  $ query --input data/query_set.txt
```

### parse-validation-errors

```console
usage: parse-validation-errors [-h] TXT

Utility to parse and gather stats on query logs

positional arguments:
  TXT         query stdout file to parse

options:
  -h, --help  show this help message and exit

Example:
  $ parse-validation-errors ${PAPEREXT_DIR_LOG}/DATE.query.dbg
    Per paper errors
    ================
    Failures count for paper: 1
    ---------------------------
    primary_research_field.aliases      1 ~1
    primary_research_field.name         1 ~1
    sub_research_fields.*.aliases       2 ~1
    sub_research_fields.*.name          2 ~1

    [...]
    Failures count for paper: 2
    ---------------------------
    datasets                            1 ~1
    models.*                           13 ~1
    sub_research_fields.*.aliases       1 ~1
    sub_research_fields.*.name          1 ~1

    libraries.*.aliases                 1 ~1
    libraries.*.referenced_paper_title  1 ~1
    libraries.*.role                    1 ~1

    [...]
    Failures count for paper: 2
    ---------------------------
    Generic Error: 
      Invalid JSON: control character (\u0000-\u001F) found while parsing a string at line 1 column 2885 [...]
        For further information visit https://errors.pydantic.dev/2.7/v/json_invalid,)

    Generic Error: 
      Invalid JSON: control character (\u0000-\u001F) found while parsing a string at line 1 column 2885 [...]
        For further information visit https://errors.pydantic.dev/2.7/v/json_invalid,)

    [...]
    Error type involved in a paper validation
    =========================================
    Generic Error                       2 /62
    datasets                            5 /62
    libraries.*.aliases                10 /62
    libraries.*.referenced_paper_title  9 /62
    libraries.*.role                    9 /62
    models.*                            3 /62
    primary_research_field.aliases     40 /62
    primary_research_field.name        42 /62
    sub_research_fields.*.aliases      32 /62
    sub_research_fields.*.name         37 /62

    Queries Stats
    =============
    Requests cnt                          204
    Errors cnt                            62
    1 failure(s)                          46
    2 failure(s)                          8
```

### merge-papers

### analysis

```console
usage: perf-analysis [-h] [--papers [PAPERS ...]] [--input TXT]

Utility to analyses Chat-GPT responses on papers

Confidence and multi-label confidence matrices will be dumped into data/analysis

options:
  -h, --help            show this help message and exit
  --papers [PAPERS ...]
                        Papers to analyse
  --input TXT           List of papers to analyse

Example:
  $ perf-analysis --input data/validation_set.txt
```

## License

`paperext` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
