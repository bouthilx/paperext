import shlex

from paperext.config import CFG


def parse_curl_headers():
    """Extract request headers from curl_tokens (a Firefox "Copy as cURL" dump).
    https://firefox-source-docs.mozilla.org/devtools-user/network_monitor/request_list/index.html#context-menu

    Returns a ``{name: value}`` dict of headers (including auth) suitable for an
    HTTP request. The request URL and non-header curl flags are ignored;
    ``report.py`` builds its own request URL against ``CFG.paperoni.url``.
    """
    cmd, *tokens = shlex.split((CFG.dir.paperoni / "curl_tokens").read_text())

    assert cmd == "curl", (
        f"{CFG.dir.paperoni / 'curl_tokens'} must be a Firefox 'Copy as cURL' command"
    )
    assert any(token.startswith(CFG.paperoni.url) for token in tokens), (
        f"No {CFG.paperoni.url} request URL found in "
        f"{CFG.dir.paperoni / 'curl_tokens'}; is this a 'Copy as cURL' of a "
        "paperoni request?"
    )

    headers = {}
    tokens = iter(tokens)
    for token in tokens:
        if token in ("-H", "--header"):
            name, _, value = next(tokens).partition(":")
            headers[name.strip()] = value.strip()
        elif token in ("-b", "--cookie"):
            headers["Cookie"] = next(tokens)

    return headers
