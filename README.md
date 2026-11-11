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

**End to end**: `docs/running-the-procedure.md` gives the full sequence -- corpus
assembly, extraction, verification, ontology construction -- with the decision
points marked and the places it currently stops.
`docs/annotation-and-ontology-handoff.md` carries the reasoning behind it: what
each check is for, which numbers mean what, and the failure modes to expect.

The sections below document the corpus and extraction commands. The rest of the
surface, not documented here:

| command | what it does |
|---|---|
| `backend-check` | one trivial completion proving auth + model access |
| `python -m paperext.structured_output.mdl.verify` | prompt-level CHECK / PROBE / MEASURE over a bucket of extractions |
| `python -m paperext.structured_output.mdl.check` | per-record invariants (unresolved references, run/mode contradictions) |
| `python -m paperext.annotate_pdf` | highlight a paper's PDF with what each extraction arm claimed |
| `python -m paperext.adjudication_report` | agreement between a session's recommendations and the decisions taken |
| `categorize-items` | fold the extraction corpus into one decidable item per distinct name |
| `python -m paperext.ontology.convert_axes` | authored axis TSVs -> loadable ontology snapshots |
| `python -m paperext.ontology.migrate` | build the legacy `v0` snapshots |
| `categorize` | place names into a dimension's ontology (`--interactive` to review each) |
| `categorize-eval` | held-out categorization eval and decision gate |
| `categorize-report` | read back what a `categorize` run did, from its `decisions.jsonl` |

Each takes `--help`.

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
- with OpenReview credentials, `SERIEUX_PASSWORD` exported in the environment
  (any passphrase, always the same one): paperoni encrypts its cached
  OpenReview token with it, and without it the login is discarded.

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
  --delay SECONDS   Minimum seconds between two papers starting to download (pacing
                    for hourly quotas; OpenReview allows ~140 PDFs/hour:
                    --concurrency 1 --delay 27)
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

When stderr is a terminal, a live dashboard is shown: the tail of the logs
(including paperoni's download progress), a table of hits / misses / total per
venue (largest first, folded to what fits), and a progress bar with elapsed
time and ETA; the complete venue table is left on screen when it exits. The
venue is the one `paperoni-report` selected the paper on (its peer-reviewed
release inside the window, stamped as `venue` in the JSON).
stdout lists the converted text files; the report records, per paper, the refs
tried, which resolver produced the PDF (`source`) and the error otherwise, so
download drop-out can be quantified per publisher. Re-runs are cheap: papers
with an existing text are skipped, and paperoni keeps its own PDF cache under
`data_path` (see the config).

### paperoni-enrich

Stamps, in place, what the extraction tiers below the fulltext need (#72):
an `abstract` for papers whose record has none, and an OpenAlex research
classification for every paper.

```console
usage: paperoni-enrich [-h] [--output JSON] [--cache-dir DIR] [--mailto EMAIL]
                       [--refresh] [--report JSON] JSON

positional arguments:
  JSON             paperoni-report output to enrich

options:
  --output JSON    Where to write the enriched list (default: in place)
  --cache-dir DIR  Responses are cached under DIR/enrich (default: the config's cache)
  --mailto EMAIL   Contact for OpenAlex's polite pool (default: the paperoni config's mailto)
  --refresh        Ignore cached responses and query the services again
  --report JSON    Per-paper report (keys tried, OpenAlex id, topic, abstract source)

Example:
  $ PAPEREXT_LOGGING_LEVEL=INFO paperoni-enrich data/paperoni-2026-01-01-2026-02-01-PR_2026-09-16.json --report logs/enrich-2026.json
    ...
    Abstracts: 22/45 before, 42/45 after (openalex:20)
    OpenAlex topics: 42/45
```

Each paper is looked up on OpenAlex by publisher DOI, OpenAlex id
(`openalex` links, `info.discovered_by.openalex`) or arXiv id, in that order,
and gets:

- `openalex`: `{id, domain, field, subfield, topic, is_oa, keywords, concepts}`
  from the work's `primary_topic` (OpenAlex's hierarchy, e.g. *Health Sciences
  > Medicine > Oncology > ...*), `open_access` and keyword / concept lists.
  When the first work found has no topic yet (a freshly indexed publisher
  version), the paper's other handles -- typically its preprint -- fill it in.
- `abstract` when missing, rebuilt from OpenAlex's `abstract_inverted_index`,
  else from Semantic Scholar, else from the arXiv API; `abstract_source` says
  which (`paperoni` for abstracts the record already had).

Every response (200 or 404) is cached under `<cache>/enrich/<service>/`, so a
rerun is offline, an interrupted run resumes, and a paper that already has
both an abstract and a topic is not looked up again. Requests are paced per
service (OpenAlex 0.1 s, Semantic Scholar and arXiv 3 s); a service that keeps
answering 429 is skipped for a minute rather than stalling the run. The same
dashboard as `download-convert` shows progress (hit = the paper has an
abstract), and the run ends with the coverage summary above.

### query

Credentials for the selected backend are required. Which variable depends on
`--platform` (`[env]` in the config holds blank placeholders; supply the value at
runtime):

```console
export OPENAI_API_KEY=...        # --platform openai
export ANTHROPIC_API_KEY=...     # --platform anthropic
```

`backend-check` (below) proves the credentials and model access in one trivial
completion before a run spends anything.

**`PAPEREXT_DIR_CACHE` must point at the directory holding the converted
fulltexts** (`<cache>/fulltext/<paper_id>/`). `Paper._pdfs` globs `CFG.dir.cache`,
so with the wrong value every paper resolves to `None` and the run has nothing to
query. `query` refuses an empty list rather than succeeding at nothing, but verify
first -- `docs/running-the-procedure.md` §2b has the one-liner.

```console
usage: query [-h] [--platform {anthropic,claude,gemini,local,openai}]
             [--papers [PAPERS ...]] [--input TXT] [--concurrency CONCURRENCY]
             [--paperoni JSON]

Utility to query Chat-GPT on papers

Queries logs will be written in ${PAPEREXT_DIR_LOG}/DATE.query.dbg

options:
  -h, --help            show this help message and exit
  --platform {anthropic,claude,gemini,local,openai}
                        Platform to use
  --papers [PAPERS ...]
                        Papers to analyse
  --input TXT           List of papers to analyse
  --concurrency CONCURRENCY
                        papers in flight at once (default 4); the ceiling is
                        the provider's rate limit, not this code
  --paperoni JSON       Paperoni json output of papers to query on converted
                        pdfs -> txts

Example:
  $ query --platform anthropic --concurrency 4 --paperoni data/papers.json
```

Output lands under `data/mdl/queries/<provider>/<model-slug>/`. The provider comes
from `--platform` and **the model half comes from that backend's own config
section, not from the flag** -- so changing `[anthropic] model` changes the output
directory with it. Omitting `--platform` uses `[platform] select`.

The run is resumable: re-running queries only what is missing or stale, and says
how many papers are already extracted versus how many it will query (the ETA
covers only the second number).

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

Interactive field-by-field merge of several arms' extractions for one paper into
a human-validated reference annotation under `data/mdl/merged/<paper_id>.yaml`.
Each field where the arms disagree is opened in `$EDITOR`; fields they agree on
are collapsed automatically.

```console
usage: merge-papers [-h] [--papers [PAPERS ...]] [--input INPUT]
                    [--bucket PROVIDER/MODEL [PROVIDER/MODEL ...]]

options:
  -h, --help            show this help message and exit
  --papers [PAPERS ...] Papers to merge
  --input INPUT         List of papers to merge
  --bucket PROVIDER/MODEL [PROVIDER/MODEL ...]
                        query buckets to merge, e.g. anthropic/claude-opus-5
                        openai/gpt-5.6-sol. Several arms are the point: the
                        merge collapses every field they agree on. Default
                        openai/legacy-2024

Example:
  $ merge-papers --bucket anthropic/claude-opus-5 openai/gpt-5.6-sol --papers <paper_id>
```

The conversational alternative -- adjudicating with the evidence in front of you
and writing the YAML directly -- is described in
`data/ontology/design/c0_verification/ANNOTATION_SESSION.md`, together with
`annotate_pdf` and `adjudication_report`, which exist for that workflow.

### analysis

The entry point is `evaluate` (it was named `perf-analysis` in an earlier
release). It scores extractions against the human-validated annotations in
`data/mdl/merged/`.

```console
usage: evaluate [-h] [--papers [PAPERS ...]] [--input TXT]

Utility to analyses Chat-GPT responses on papers

Confidence and multi-label confidence matrices will be dumped into data/analysis

options:
  -h, --help            show this help message and exit
  --papers [PAPERS ...]
                        Papers to analyse
  --input TXT           List of papers to analyse

Example:
  $ evaluate --input data/validation_set.txt
```

Frequency and workload aggregation live in `paperext.analysis` and have no console
scripts; invoke them with `python -m paperext.analysis.frequency` /
`python -m paperext.analysis.workload`.

## License

`paperext` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
