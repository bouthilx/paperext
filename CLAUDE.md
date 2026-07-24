# CLAUDE.md

Guidance for Claude Code and contributors working in this repository.

## Development guidelines

### Type annotations (required for new code)

New code **must** be typed. Annotate every function/method signature you add or
substantially edit — parameters **and** return type — plus public class
attributes. Prefer precise types over `Any` where practical.

The project targets **Python >= 3.10**, so use built-in generics and unions:
`list[str]`, `dict[str, Any]`, `tuple[int, ...]`, `str | None` — not
`typing.List` / `Optional`. Add `from __future__ import annotations` to new
modules so annotations stay cheap and forward references just work.

Existing untyped code can stay as-is, but don't add new untyped functions.

Check types before committing:

```console
hatch run types:check
```

### Formatting

Format with black + isort (isort uses the black profile):

```console
hatch run lint:lint
```

### Tests

```console
hatch run tests:tests
```
