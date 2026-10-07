import json
import logging
from pathlib import Path

import pydantic_core
import yaml
from pydantic import BaseModel

from paperext import CFG
from paperext.structured_output.mdl import (
    model_v1,
    model_v2,
    model_v3,
    model_v4,
    model_v5,
)
from paperext.structured_output.utils import model_dump_yaml
from paperext.utils import split_entry, str_eq


def _model_dump(m):
    if isinstance(m, list):
        return [_model_dump(field) for field in m]

    if isinstance(m, dict):
        return {field_name: _model_dump(field) for field_name, field in m.items()}

    if isinstance(m, BaseModel):
        return m.model_dump()

    return m


def convert_model_v1(extractions: model_v1.PaperExtractions):
    from paperext.structured_output.mdl import model_v2 as dest_model

    fields = {}

    for field_name, field in extractions:
        if field_name in (
            "title",
            "description",
            "type",
        ):
            fields[field_name] = field

        # We want a primary research field as well as a list of
        # sub_research_fields. Each field can have multiple aliases. v1 however
        # has only a single string value for the research_field and a single
        # string value for sub_research_field. Aliases should be extracted from
        # the strings
        elif field_name in ("research_field",):
            name, *aliases = split_entry(
                extractions.research_field.value, sep_left="(", sep_right=")"
            )
            fields["primary_research_field"] = dest_model.ResearchField(
                name={**extractions.research_field.model_dump(), "value": name},
                aliases=aliases,
            )
            logging.info(
                f"Extracted name and aliases from "
                f"{extractions.research_field.value} are: ({name}, {aliases})"
            )

        elif field_name in ("sub_research_field",):
            fields["sub_research_fields"] = []
            sub_research_fields = fields["sub_research_fields"]

            log_msg = (
                f"Extracted name and aliases from "
                f"{extractions.sub_research_field.value} are:"
            )
            for i, srf in enumerate(split_entry(extractions.sub_research_field.value)):
                name, *aliases = split_entry(srf, sep_left="(", sep_right=")")
                srf = dest_model.ResearchField(
                    name={
                        **extractions.sub_research_field.model_dump(),
                        "value": name,
                        **({"justification": "", "quote": ""} if i > 0 else {}),
                    },
                    aliases=aliases,
                )
                sub_research_fields.append(srf)
                log_msg += f" ({name}, {aliases})"

            logging.info(log_msg)

        elif field_name in ("models",):
            fields[field_name] = []
            for m in extractions.models:
                name, *aliases = split_entry(m.name.value, sep_left="(", sep_right=")")
                m = dest_model.Model(
                    name={**m.name.model_dump(), "value": name},
                    aliases=aliases,
                    is_contributed=dest_model.Explained(
                        value=str_eq(m.role, model_v1.Role.CONTRIBUTED.value),
                        justification=f"Role:{[_r.value for _r in model_v1.Role]}",
                        quote=m.role,
                    ).model_dump(),
                    # is_executed is uncertain except when the model is
                    # contributed
                    is_executed=dest_model.Explained(
                        value=str_eq(m.role, model_v1.Role.CONTRIBUTED.value),
                        justification=f"ModelMode:{[_m.value for _m in model_v1.ModelMode]}",
                        quote=m.mode,
                    ).model_dump(),
                    # is_compared is uncertain except when the model is
                    # contributed
                    is_compared=dest_model.Explained(
                        value=str_eq(m.role, model_v1.Role.CONTRIBUTED.value),
                        justification="",
                        quote="",
                    ).model_dump(),
                    referenced_paper_title=dest_model.Explained(
                        value="", justification="", quote=""
                    ).model_dump(),
                )
                fields[field_name].append(m)

                logging.info(
                    f"Extracted name and aliases from "
                    f"{m.name.value} are: ({name}, {aliases})"
                )

        elif field_name in ("datasets",):
            fields[field_name] = []
            for d in extractions.datasets:
                name, *aliases = split_entry(d.name.value, sep_left="(", sep_right=")")
                d = dest_model.Dataset(
                    name={**d.name.model_dump(), "value": name},
                    aliases=aliases,
                    role=d.role,
                    referenced_paper_title=dest_model.Explained(
                        value="", justification="", quote=""
                    ).model_dump(),
                )
                fields[field_name].append(d)

                logging.info(
                    f"Extracted name and aliases from "
                    f"{d.name.value} are: ({name}, {aliases})"
                )

        elif field_name in ("libraries",):
            fields[field_name] = []
            for l in extractions.libraries:
                name, *aliases = split_entry(l.name.value, sep_left="(", sep_right=")")
                l = dest_model.Library(
                    name={**l.name.model_dump(), "value": name},
                    aliases=aliases,
                    role=l.role,
                    referenced_paper_title=dest_model.Explained(
                        value="", justification="", quote=""
                    ).model_dump(),
                )
                fields[field_name].append(l)

                logging.info(
                    f"Extracted name and aliases from "
                    f"{l.name.value} are: ({name}, {aliases})"
                )

    return dest_model.PaperExtractions(**{k: _model_dump(v) for k, v in fields.items()})


def convert_model_v2(extractions: model_v2.PaperExtractions):
    from paperext.structured_output.mdl import model_v3 as dest_model

    def convert_enum(enum_cls, value):
        try:
            v = enum_cls(value)
        except ValueError:
            v = enum_cls(str(value).lower().split()[0])
            logging.info(f"Converted enum from {value} to {v}")
        return v

    fields = {}

    for field_name, field in extractions:
        if field_name in (
            "title",
            "description",
            "primary_research_field",
            "sub_research_fields",
        ):
            fields[field_name] = field

        elif field_name in ("type",):
            value = convert_enum(dest_model.ResearchType, extractions.type.value)
            fields[field_name] = {**extractions.type.model_dump(), "value": value}

        elif field_name in ("models",):
            fields[field_name] = []
            for m in extractions.models:
                attributes = [
                    m.is_contributed.value,
                    m.is_executed.value,
                    m.is_compared.value,
                ]
                for i, a in enumerate(attributes):
                    if isinstance(a, bool):
                        continue
                    elif isinstance(a, int):
                        assert a in (0, 1)
                        attributes[i] = a == 1
                    elif isinstance(a, str):
                        assert a.lower().strip() in ("true", "false", "1", "0")
                        attributes[i] = a.lower().strip() == "true"
                    else:
                        assert False

                    logging.info(f"Converted enum from {a} to {attributes[i]}")

                is_contributed, is_executed, is_compared = attributes

                m = dest_model.RefModel(
                    name=m.name.model_dump(),
                    aliases=m.aliases,
                    is_contributed={
                        **m.is_contributed.model_dump(),
                        "value": is_contributed,
                    },
                    is_executed={**m.is_executed.model_dump(), "value": is_executed},
                    is_compared={**m.is_compared.model_dump(), "value": is_compared},
                    referenced_paper_title=m.referenced_paper_title.model_dump(),
                )
                fields[field_name].append(m)

        elif field_name in ("datasets",):
            fields[field_name] = []
            for d in extractions.datasets:
                role = convert_enum(dest_model.Role, d.role)

                d = dest_model.RefDataset(
                    name=d.name.model_dump(),
                    aliases=d.aliases,
                    role=role,
                    referenced_paper_title=d.referenced_paper_title.model_dump(),
                )
                fields[field_name].append(d)

        elif field_name in ("libraries",):
            fields[field_name] = []
            for l in extractions.libraries:
                role = convert_enum(dest_model.Role, l.role)

                l = dest_model.RefDataset(
                    name=l.name.model_dump(),
                    aliases=l.aliases,
                    role=role,
                    referenced_paper_title=l.referenced_paper_title.model_dump(),
                )
                fields[field_name].append(l)

    return dest_model.PaperExtractions(**{k: _model_dump(v) for k, v in fields.items()})


def convert_model_v3(extractions: model_v3.PaperExtractions):
    # Each converter names its destination version explicitly, never the `model`
    # proxy. Targeting the proxy works only while that version happens to be the
    # newest: when v5 landed, this function silently started emitting v5 and
    # every conversion from v3 or below failed on the v5 fields it does not set.
    from paperext.structured_output.mdl import model_v4 as dest_model

    fields = {}

    for field_name, field in extractions:
        if field_name in ("models",):
            fields[field_name] = []
            for m in extractions.models:
                m = dest_model.RefModel(
                    name=m.name.model_dump(),
                    aliases=m.aliases,
                    is_contributed=m.is_contributed.model_dump(),
                    is_executed=m.is_executed.model_dump(),
                    is_compared=m.is_compared.model_dump(),
                    # New in v4. The stored extraction was produced without these
                    # fields and the paper is not re-read here, so default to
                    # `unknown` with no grounding quote/justification.
                    execution_mode=dest_model.Explained(
                        value=dest_model.ExecutionMode.UNKNOWN,
                        justification="",
                        quote="",
                    ).model_dump(),
                    parameter_count=dest_model.Explained(
                        value="unknown",
                        justification="",
                        quote="",
                    ).model_dump(),
                    referenced_paper_title=m.referenced_paper_title.model_dump(),
                )
                fields[field_name].append(m)

        else:
            fields[field_name] = field

    return dest_model.PaperExtractions(**{k: _model_dump(v) for k, v in fields.items()})


def convert_model_v4(
    extractions: model_v4.PaperExtractions,
) -> model_v5.PaperExtractions:
    from paperext.structured_output.mdl import model_v5 as dest_model

    fields = {}

    for field_name, field in extractions:
        # #89: `primary_research_field` + `sub_research_fields` collapse into one
        # `research_fields` list with a role. The role is left `unknown`: these
        # extractions were produced before the question was asked, and the rank
        # does not answer it -- 187 of the 1999 legacy-2024 papers rank a vacuous
        # field (`deep learning`, `machine learning`) first, so `primary` is not
        # evidence of `contributed`. Guessing here would manufacture the
        # distinction #89 exists to measure. #14 re-extracts for the real roles.
        if field_name in ("primary_research_field",):
            fields["research_fields"] = [
                dest_model.ResearchField(
                    name=extractions.primary_research_field.name.model_dump(),
                    aliases=extractions.primary_research_field.aliases,
                    role=dest_model.Role.UNKNOWN,
                )
            ]

        elif field_name in ("sub_research_fields",):
            # `primary_research_field` is iterated first, so the list exists.
            fields["research_fields"].extend(
                dest_model.ResearchField(
                    name=srf.name.model_dump(),
                    aliases=srf.aliases,
                    role=dest_model.Role.UNKNOWN,
                )
                for srf in extractions.sub_research_fields
            )

        elif field_name in ("models",):
            fields[field_name] = []
            for m in extractions.models:
                # `parameter_count` moves to the run in v5. It has never been
                # populated by any extraction -- no corpus was ever produced with
                # v4 -- so there is no value to carry anywhere, and the run it
                # would belong to does not exist until re-extraction either.
                m = dest_model.RefModel(
                    name=m.name.model_dump(),
                    aliases=m.aliases,
                    is_contributed=m.is_contributed.model_dump(),
                    is_executed=m.is_executed.model_dump(),
                    is_compared=m.is_compared.model_dump(),
                    execution_mode=m.execution_mode.model_dump(),
                    referenced_paper_title=m.referenced_paper_title.model_dump(),
                )
                fields[field_name].append(m)

        elif field_name in ("datasets",):
            # v5 renames the list to `data_sources` (#102): the dimension covers
            # interactive environments and generators as well as fixed samples,
            # and a field called `datasets` invites an extractor to skip MuJoCo.
            fields["data_sources"] = []
            for d in extractions.datasets:
                # New in v5 (#93). The paper is not re-read here, so size,
                # per-sample measures and `derived_from` are empty or `unknown`
                # with no grounding quote rather than absent: the field has to be
                # distinguishable from one the extractor looked for and did not
                # find.
                fields["data_sources"].append(
                    dest_model.RefDataSource(
                        name=d.name.model_dump(),
                        aliases=d.aliases,
                        role=dest_model.Role(d.role.value),
                        size=dest_model.Explained(
                            value="unknown", justification="", quote=""
                        ).model_dump(),
                        derived_from=[],
                        sample_properties=[],
                        referenced_paper_title=d.referenced_paper_title.model_dump(),
                    )
                )

        elif field_name in ("libraries",):
            fields[field_name] = []
            for l in extractions.libraries:
                l = dest_model.RefLibrary(
                    name=l.name.model_dump(),
                    aliases=l.aliases,
                    role=dest_model.Role(l.role.value),
                    referenced_paper_title=l.referenced_paper_title.model_dump(),
                )
                fields[field_name].append(l)

        else:
            fields[field_name] = field

    # `algorithms` and `runs` are new entity lists, not reshaped ones. Nothing in
    # v4 holds an algorithm or a compute configuration, so a converter can only
    # leave them empty; they are filled by the v5 re-extraction (#13/#14). An
    # empty `runs` is also the honest value for a paper whose compute profile was
    # never asked about.
    fields["algorithms"] = []
    fields["runs"] = []

    return dest_model.PaperExtractions(**{k: _model_dump(v) for k, v in fields.items()})


CONVERT_MODEL = {
    model_v1: convert_model_v1,
    model_v2: convert_model_v2,
    model_v3: convert_model_v3,
    model_v4: convert_model_v4,
}

# Ordered conversion chain: each module maps to a converter producing the next
# version, ending at the `model` proxy (currently v5).
CONVERT_CHAIN = [model_v1, model_v2, model_v3, model_v4]


def _detect_version(model_data):
    """Return (module, response, extractions) for the newest version that
    validates. `module` is the `model` proxy when the data is already up to date.
    `response` is the ExtractionResponse wrapper or None when the data is a bare
    PaperExtractions."""
    from paperext.structured_output.mdl import model as dest_model

    # Newest first: a newer file also validates as an older PaperExtractions
    # (extra fields are ignored), so the proxy must be tried before the older
    # versions. v4 and v5 are mutually exclusive in both directions -- v5 has no
    # `primary_research_field` and v4 has no `research_fields`, and both are
    # required -- but v5 still validates as v3 and below, so order matters.
    for module in (dest_model, *reversed(CONVERT_CHAIN)):
        try:
            response = module.ExtractionResponse.model_validate(model_data)
            return module, response, response.extractions
        except pydantic_core._pydantic_core.ValidationError:
            pass
        try:
            extractions = module.PaperExtractions.model_validate(model_data)
            return module, None, extractions
        except pydantic_core._pydantic_core.ValidationError:
            pass

    return None, None, None


if __name__ == "__main__":
    from paperext.structured_output.mdl import model as dest_model

    for path in sorted(
        sum(
            map(
                lambda p: sorted(
                    [
                        # Recursive: results are bucketed <provider>/<model>/
                        # (A7 #27), so extractions live several levels deep.
                        *p.rglob(f"*.json"),
                        *p.rglob(f"*.yaml"),
                    ]
                ),
                [CFG.dir.merged, CFG.dir.queries],
            ),
            [],
        )
    ):
        path: Path
        model_data = path.read_text()
        try:
            model_data = json.loads(model_data)
        except json.decoder.JSONDecodeError:
            model_data = yaml.safe_load(model_data)

        module, response, extractions = _detect_version(model_data)

        if module is None:
            raise ValueError(f"Could not validate {path} against any model version")

        if module is dest_model:
            logging.info(f"Model {path.relative_to(CFG.dir.root)} already updated")
            continue

        logging.info(f"Updating {path.relative_to(CFG.dir.root)}")
        # Chain converters from the detected version up to the proxy (v5).
        for src_model in CONVERT_CHAIN[CONVERT_CHAIN.index(module) :]:
            extractions = CONVERT_MODEL[src_model](extractions)

        if response is not None:
            src = dest_model.ExtractionResponse(
                paper=response.paper,
                words=response.words,
                extractions=extractions,
                usage=response.usage,
            )
        else:
            src = extractions

        try:
            json.loads(path.read_text())
            model_data = src.model_dump_json(indent=2)
        except json.decoder.JSONDecodeError:
            yaml.safe_load(path.read_text())
            model_data = model_dump_yaml(src)

        path.write_text(model_data)
