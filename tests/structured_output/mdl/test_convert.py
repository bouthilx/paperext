import json
from types import ModuleType
from typing import Any, Callable

import pytest

from paperext.structured_output.mdl import (
    model,
    model_v1,
    model_v2,
    model_v3,
    model_v4,
    model_v5,
)
from paperext.structured_output.mdl.convert import (
    _model_dump,
    convert_model_v1,
    convert_model_v2,
    convert_model_v3,
    convert_model_v4,
)


def test_model_dump(cfg):
    """Test that _model_dump produces a valid pydantic model dump."""

    assert model.ExtractionResponse.model_validate_json(
        (cfg.dir.queries / "openai/gpt-4o/2401.14487_00.json").read_text()
    ) == model.ExtractionResponse(
        **_model_dump(
            json.loads(
                (cfg.dir.queries / "openai/gpt-4o/2401.14487_00.json").read_text()
            )
        )
    )


@pytest.mark.parametrize(
    "query_file,from_version,dest_version",
    [
        ["2401.14487_00", 1, 2],
        ["2401.14487_00", 2, 3],
        ["2402.04821_00", 2, 3],
        ["2401.14487_00", 3, 4],
        ["2402.04821_00", 3, 4],
        ["2401.14487_00", 4, 5],
        ["2402.04821_00", 4, 5],
    ],
)
def test_convert_model(cfg, query_file: str, from_version: int, dest_version: int):
    """Test that the model can be converted from a version to the next version."""

    convert_model: Callable[[Any], Any]
    from_model: ModuleType
    dest_model: ModuleType

    match from_version:
        case 1:
            convert_model = convert_model_v1
            from_model = model_v1
            dest_model = model_v2
        case 2:
            convert_model = convert_model_v2
            from_model = model_v2
            dest_model = model_v3
        case 3:
            convert_model = convert_model_v3
            from_model = model_v3
            # Explicitly v4, not the `model` proxy: a converter names its own
            # destination version, so that moving the proxy to v5 does not turn
            # this into a v3 -> v5 conversion that cannot work.
            dest_model = model_v4
        case 4:
            convert_model = convert_model_v4
            from_model = model_v4
            dest_model = model_v5
        case _:
            raise ValueError(f"Unknown version: {from_version}")

    m = from_model.ExtractionResponse.model_validate_json(
        (cfg.dir.queries / f"v{from_version}/{query_file}.json").read_text()
    )

    assert (
        convert_model(m.extractions)
        == dest_model.ExtractionResponse.model_validate_json(
            (cfg.dir.queries / f"v{dest_version}/{query_file}.json").read_text()
        ).extractions
    )
