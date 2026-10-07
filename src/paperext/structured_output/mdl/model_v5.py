from __future__ import annotations

import enum
import logging
import typing
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from paperext.utils import str_normalize

logging.basicConfig(level=logging.DEBUG)

# v5 adds `runs[]` (#94), `algorithms[]` (#94), dataset compute fields (#93) and
# `research_fields[]` (#89). The structural decision behind `runs[]` is recorded
# in `data/ontology/design/SCHEMA_V5_STRUCTURE.md`: entity lists stay top-level
# and carry identity, `runs[]` is a fact table that references them by name.

# The first two sentences state what the work is: a bibliometric survey of the
# computational artifacts a research institute's published papers used, run to
# size AI compute needs. Without them, models with strict safety classifiers
# refuse papers on the strength of their subject matter alone -- Opus 5.5
# declined a biology paper outright (`stop_reason: refusal`, `category='bio'`),
# and the corpus is full of clinical and biomedical work. Nothing here asks for
# the papers' scientific content: the output is names of software and data.
SYSTEM_MESSAGE = (
    "You are cataloguing the computational artifacts used by published research "
    "papers, for a bibliometric survey that sizes a research institute's AI "
    "compute needs. The papers come from every field -- medicine, biology, "
    "chemistry, the social sciences -- and their subject matter is not what is "
    "being catalogued: you report only the names of the software, data and "
    "procedures a paper used, never its scientific content, findings or "
    "methods.\n\n"
    "Your role is to extract, from a given research paper, its Research Fields, "
    "Models, Data Sources, Libraries, Algorithms, and the Runs it executed.\n\n"
    "DATA SOURCES. A Data Source is a NAMED SOURCE OF THE EXAMPLES A RUN "
    "CONSUMES. That covers a fixed dataset (ImageNet), an interactive "
    "environment whose observations depend on the actions taken in it "
    "(MuJoCo, Atari, a driving simulator), and a generator that produces "
    "examples on demand (a physics simulator, a procedural generator). All "
    "three are Data Sources -- a fixed dataset is a frozen sample of what a "
    "generator would produce -- so do NOT omit an environment or a simulator "
    "because it is not a dataset.\n"
    "Out of scope: UNNAMED descriptions, so 'synthetic data' and 'our "
    "simulated dataset' are not entries while 'Moving MNIST' is; the "
    "SOFTWARE that implements a source, which is a Library (the MuJoCo "
    "physics engine is a Library, the MuJoCo benchmark environments are Data "
    "Sources); and a source that is itself a Model, such as a teacher "
    "network whose outputs are used for training -- report that Model in the "
    "Run instead.\n"
    "If the paper names a Data Source it built FROM another named one -- "
    "Moving MNIST from MNIST, an offline RL dataset from a simulator -- "
    "report both and name the original in the derived one's derived_from. A "
    "transformation the paper does not name is NOT a new Data Source: 'we "
    "trained on rotated MNIST' is MNIST plus an augmentation Algorithm, and "
    "a subset or split of a source is the same source with a different "
    "size.\n\n"
    "RESEARCH FIELDS. Report every field as one list entry with a role: "
    "'contributed' if the paper advances that field or addresses a claim to it "
    "(several fields may be contributed -- do not rank them, and do not force a "
    "single primary one), 'used' if the paper works in the field as a setting, "
    "benchmark or evaluation venue without advancing it, 'referenced' if it is "
    "named as related context only.\n\n"
    "ALGORITHMS. An Algorithm is a NAMED PROCEDURE A RUN EXECUTES: preparing "
    "the data, producing or adapting the learned object, or using it to produce "
    "outputs. In scope: data preprocessing and augmentation, experience "
    "generation, training objectives and gradient estimators, parameter update "
    "rules, which parameters are adapted, coordination across workers, "
    "configuration and architecture search, post-training compression, decoding "
    "and test-time search, and evaluation procedures such as cross-validation "
    "or bootstrap intervals. Out of scope: things that are not procedures "
    "(datasets, libraries, hardware, the learned object itself) and UNNAMED "
    "descriptions of procedures -- 'CutMix' is an entry, 'we normalised the "
    "images' is not.\n"
    "Two boundaries to apply rather than guess at:\n"
    "- A model component is not an Algorithm. Ask whether specifying the "
    "NETWORK requires it or specifying the RUN requires it. Dropout and batch "
    "normalisation are model components, not Algorithms. Weight decay, label "
    "smoothing and gradient clipping are Algorithms. R-Drop and VAT are "
    "Algorithms even though both are built out of dropout, because each adds a "
    "term to the objective.\n"
    "- A procedure is not its implementation. FlashAttention is an Algorithm; "
    "the `flash-attn` package is a Library. When one string names both, record "
    "the procedure as the Algorithm and the package as the Library.\n"
    "Report the Algorithm's name EXACTLY AS THE PAPER WRITES IT, including the "
    "paper's own abbreviation, and describe its role in the paper's own words. "
    "Do not translate a name into a standard or canonical term, do not pick "
    "from any list, and do not resolve an ambiguous abbreviation -- if the "
    "paper writes 'IQL', report 'IQL' with the quote around it and leave the "
    "ambiguity in place.\n\n"
    "RUNS. A Run is a distinct COMPUTE CONFIGURATION, not a distinct execution. "
    "Two executions are the SAME run when they share a compute profile, and "
    "DIFFERENT runs only when one of these differs: execution mode, precision, "
    "parallelism, accelerator count or type, scale, or dataset. Positive test: "
    "a paper that trains one model on one dataset with 5 seeds and 20 learning "
    "rates is ONE run with repetitions=100, because none of those six things "
    "changes. Negative test: a paper that trains the same model at 7B and 70B, "
    "or finetunes then evaluates it, has TWO runs, because scale and execution "
    "mode are among the six. Hyperparameter variation that moves none of the "
    "six -- learning rate, seed, dropout rate, weight decay -- stays in ONE run "
    "and is counted in `repetitions`.\n"
    "A run is ONE COUPLED OPTIMISATION LOOP. Networks whose parameters are "
    "updated from a shared backward pass belong to the SAME run, however many "
    "networks that is: a generator and its discriminator are ONE run, because "
    "the generator's gradient flows through the discriminator; an actor and its "
    "critic are ONE run; an encoder and its decoder are ONE run. A network that "
    "is FROZEN and only supplies targets or scores is a participant of the run, "
    "not a run of its own -- a distillation teacher is reported in the run's "
    "models with role_in_run='teacher', not as a second run.\n"
    "A multi-stage procedure is several runs when the stages are separate "
    "loops: reporting supervised finetuning, then reward model fitting, then "
    "PPO against a FROZEN reward model is three runs, because no gradient "
    "crosses between them. You are not required to decompose a procedure the "
    "paper only names -- if the paper says only 'we used RLHF' and describes no "
    "stages, report the Algorithm and whatever runs the paper actually "
    "describes.\n"
    "Reference Models, Datasets and Algorithms from a Run by repeating the name "
    "EXACTLY as you reported it in the corresponding list.\n"
    "Only Models the paper actually executed get a Run. A baseline whose "
    "numbers are quoted from another paper is reported with is_executed=false "
    "and gets no Run.\n\n"
    "NEVER INFER. Report the parameter count, the dataset size, the per-sample "
    "measures, the epochs, the accelerator, the precision, the parallelism "
    "strategy, the duration, the utilisation and the repetitions ONLY when the "
    "paper states them, with a quote containing the stated value; otherwise "
    "report 'unknown'. Do not infer a parameter count from a model name, a "
    "dataset size from the dataset's reputation, a parallelism strategy from "
    "the libraries used, or a utilisation figure from hardware specifications. "
    "'unknown' is the correct answer far more often than a plausible number is, "
    "and repetitions in particular is 'unknown' rather than 1 when the paper "
    "does not say."
)
FIRST_MESSAGE = (
    "Which Research Fields, Models, Data Sources, Libraries, Algorithms and "
    "Runs "
    "can you find in the following research paper:\n"
    "{}"
)
RETRY_MESSAGE = (
    "Given your previous list of Models\n"
    "{}\n"
    "your previous list of Data Sources\n"
    "{}\n"
    "your previous list of Libraries\n"
    "{}\n"
    "your previous list of Algorithms\n"
    "{}\n"
    "and your previous list of Runs\n"
    "{}\n"
    "which might be incomplete or erroneous, please find more Models, Data "
    "Sources, "
    "Libraries, Algorithms and Runs in the same research paper:\n"
    "{}"
)
_EMPTY_FLAG = "__EMPTY__"


class ResearchType(str, enum.Enum):
    EMPIRICAL = "empirical"
    THEORETICAL = "theoretical"


# `UNKNOWN` is new in v5. #89 moves research fields from a forced
# `primary`/`sub` rank to this role, and the v4 -> v5 converter cannot invent a
# role for a field extracted before the question was asked. A converter that
# guessed `used` or `referenced` would manufacture the very distinction the
# issue exists to measure, so it needs a value meaning "not asked". Datasets and
# libraries gain the value too, where it reads as "the paper does not say".
class Role(str, enum.Enum):
    CONTRIBUTED = "contributed"
    USED = "used"
    REFERENCED = "referenced"
    UNKNOWN = "unknown"


class ExecutionMode(str, enum.Enum):
    TRAIN = "train"
    FINETUNE = "finetune"
    INFERENCE = "inference"
    UNKNOWN = "unknown"


class Precision(str, enum.Enum):
    FP64 = "fp64"
    FP32 = "fp32"
    TF32 = "tf32"
    FP16 = "fp16"
    BF16 = "bf16"
    FP8 = "fp8"
    INT8 = "int8"
    INT4 = "int4"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class AcceleratorType(str, enum.Enum):
    GPU = "gpu"
    CPU = "cpu"
    TPU = "tpu"
    OTHER = "other"
    UNKNOWN = "unknown"


class Parallelism(str, enum.Enum):
    DATA = "data"
    TENSOR = "tensor"
    PIPELINE = "pipeline"
    EXPERT = "expert"
    NONE = "none"
    UNKNOWN = "unknown"


# How a Run used a Model it references. The values a run can distinguish, not
# the model's role in the paper -- that is `is_contributed`/`is_compared` on
# `RefModel`.
class ModelRunRole(str, enum.Enum):
    MAIN = "main"
    TEACHER = "teacher"
    STUDENT = "student"
    ENSEMBLE_MEMBER = "ensemble-member"
    # A second network co-optimised in the same loop, whose job is to score the
    # main one's output: a GAN discriminator, an RL value network. One value for
    # both, because the structural role is identical -- co-trained, scores, and
    # usually discarded. Whether the two objectives are adversarial or
    # cooperative is a question the algorithms `signal` axis already asks, and
    # asking it twice is the conflation these dimensions keep paying for.
    CRITIC = "critic"
    UNKNOWN = "unknown"


# Which split of a Dataset a Run consumed. This is a different question from
# `RefDataSource.role` (contributed/used/referenced, which is paper-level), and
# `6 x parameters x training examples x epochs` needs the TRAINING examples
# specifically, so the two cannot be collapsed.
class DataSourceRunRole(str, enum.Enum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"
    # Consumed by the run but not trained, validated or tested on: a retrieval
    # corpus or knowledge base queried at inference. Measured in the
    # legacy-2024 corpus as 12 names over 23 papers (`wikipedia`, `thepile`,
    # `commoncrawl`, `freebase`), all of which the other three values would
    # misreport -- and it must stay out of `training examples` in
    # `6 x parameters x training examples x epochs`.
    REFERENCE = "reference"
    UNKNOWN = "unknown"


T = TypeVar("T")


class Explained(BaseModel, Generic[T]):
    quote: str = Field(
        description="The best literal quote from the paper which supports the value",
    )
    justification: str = Field(
        description="Short justification for the choice of the value",
    )
    value: T

    def __eq__(self, other: "Explained"):
        return str_normalize(str(self.value)) == str_normalize(str(other.value))

    def __lt__(self, other: "Explained"):
        if isinstance(self.value, bool):
            return not self.value < other.value
        return str_normalize(str(self.value)) < str_normalize(str(other.value))


def _lt(this: BaseModel, other: BaseModel, skip: tuple[str, ...]) -> bool:
    for (k, v), (ok, ov) in zip(this, other):
        if k != ok:
            break
        if k in skip:
            continue
        if v == ov:
            continue
        return v < ov
    return False


# | contributed | executed    | compared    | result
# | X           | X           | X           | is a contribution to the research field
# |             | X           | X           | has been executed (trained or finetuned or inference) and compared to other models
# |             |             | X           | is compared to other models using only results from a referenced paper
# |             |             |             | is only referenced in the paper but is not used in any comparison
class RefModel(BaseModel):
    name: Explained[str] = Field(
        description="Name of the Model",
    )
    aliases: list[str] = Field(
        description="List of names or acronyms used to identify the Model",
    )
    is_contributed: Explained[bool] = Field(
        description="Was the Model a contribution to the research field in the scope of the paper",
    )
    is_executed: Explained[bool] = Field(
        description="Was the Model executed on GPU or CPU in the scope of the paper",
    )
    is_compared: Explained[bool] = Field(
        description="Was the Model compared numerically to other models in the scope of the paper",
    )
    # Kept in v5 even though `Run.execution_mode` exists, because a Model with
    # `is_executed=False` has no Run and this is the only place its mode can be
    # recorded. For an executed Model the two must agree, which is a free
    # consistency check rather than a duplication.
    execution_mode: Explained[ExecutionMode] = Field(
        description="How the Model was executed, following the precedence "
        "train > finetune > inference > unknown: 'train' if the Model was trained "
        "(from scratch) in the paper, else 'finetune' if it was finetuned, else "
        "'inference' ONLY if it was used for inference only (training and "
        "finetuning always imply later inference), else 'unknown' if the paper "
        "does not state how the Model was executed. Report the mode even when the "
        "Model is only referenced with results (is_executed=False).",
    )
    referenced_paper_title: Explained[str] = Field(
        description="Title of the reference paper of the Model, found in the references section",
    )

    def __lt__(self, other: "RefModel"):
        return _lt(self, other, ("referenced_paper_title",))


# One per-sample measure of a Dataset, with its unit NAMED rather than
# normalised. #93: `6 x parameters x examples` means different things per
# modality -- tokens for text, pixels for images, timesteps for audio -- and
# normalising at extraction time destroys the information needed to correct it
# later. `name` and `unit` label the measure and are not claims about the paper,
# so only `value` is quote-backed; `aliases` sets the same precedent.
class SampleProperty(BaseModel):
    name: str = Field(
        description="What is measured per sample, in the paper's terms: e.g. "
        "'average tokens per sample', 'image resolution', 'sequence length', "
        "'average number of nodes'",
    )
    value: Explained[str] = Field(
        description="The magnitude the paper states for this measure, as "
        "written: e.g. '512', '224x224', '30 seconds'. ONLY if the paper states "
        "it; never inferred from the Dataset's name or reputation",
    )
    unit: str = Field(
        description="The unit the value is in: e.g. 'tokens', 'pixels', "
        "'timesteps', 'nodes'. Report the paper's own unit; do not convert",
    )

    def __lt__(self, other: "SampleProperty"):
        return _lt(self, other, ())


# For some reason, `Dataset` or `DatasetRef` class name is incompatible with
# `instructor.Mode.TOOLS_STRICT` and will result in:
# instructor.exceptions.InstructorRetryException: Error code: 400 - {'error':
# {'message': "Invalid schema for function 'PaperExtractions': In
# context=('properties', 'name'), 'additionalProperties' is required to be
# supplied and to be false.", 'type': 'invalid_request_error', 'param':
# 'tools[0].function.parameters', 'code': 'invalid_function_parameters'}}
class RefDataSource(BaseModel):
    name: Explained[str] = Field(
        description="Name of the Dataset",
    )
    aliases: list[str] = Field(
        description="List of names or acronyms used to identify the Dataset",
    )
    role: Role = Field(
        description="Was the Dataset contributed, used or referenced in the "
        "scope of the paper, or unknown if the paper does not say"
    )
    # New in v5 (#93). Per dataset PER PAPER, not a global property of the
    # dataset: the same dataset is used at different scales and subsets by
    # different papers.
    size: Explained[str] = Field(
        description="Number of samples of this Dataset used in this paper, as "
        "the paper states it (e.g. '1.2M images', '50,000 training examples'); "
        "'unknown' if the paper does not state it. NEVER infer the size from "
        "the Dataset's name or from prior knowledge of the Dataset",
    )
    # The relation the owner's framing makes explicit (2026-10-07): a fixed
    # dataset is a frozen draw from a generator, so "this source's content
    # originates in that one" is a real edge. It propagates for provenance --
    # a paper using Moving MNIST did build on MNIST -- but NOT for compute
    # sizing, since the run consumed Moving MNIST's examples, not MNIST's.
    # Unlike `algorithms[].composed_of`, a derivation is not its source.
    derived_from: list[str] = Field(
        description="If this Data Source was built from other NAMED Data "
        "Sources, their names as the paper writes them -- Moving MNIST from "
        "MNIST, an offline RL dataset from a simulator. Empty otherwise. An "
        "unnamed transformation is not a derivation: 'rotated MNIST' is "
        "MNIST plus an augmentation, and a subset or split is the same "
        "source",
    )
    sample_properties: list[SampleProperty] = Field(
        description="Per-sample measures of this Dataset that the paper states, "
        "each with its own unit; empty if the paper states none",
    )
    referenced_paper_title: Explained[str] = Field(
        description="Title of the reference paper of the Dataset, found in the references section",
    )

    def __lt__(self, other: "RefDataSource"):
        return _lt(self, other, ("referenced_paper_title",))


class RefLibrary(BaseModel):
    name: Explained[str] = Field(
        description="Name of the Library",
    )
    aliases: list[str] = Field(
        description="List of names or acronyms used to identify the Library",
    )
    role: Role = Field(
        description="Was the Library contributed, used or referenced in the "
        "scope of the paper, or unknown if the paper does not say"
    )
    referenced_paper_title: Explained[str] = Field(
        description="Title of the reference paper of the Library, found in the references section",
    )

    def __lt__(self, other: "RefLibrary"):
        return _lt(self, other, ("referenced_paper_title",))


# New in v5 (#94). Mirrors `RefModel`: identity plus the paper-level role, with
# `is_executed` as the gate for whether a Run references it.
#
# `paper_role` and `composed_of` are deliberately FREE TEXT. The vocabulary of
# this list has to stay open: the algorithms ontology is used to define scope in
# the prompt, never handed to the extractor as a list to choose from, because a
# closed vocabulary makes the post-extraction ontology revision (#99) circular.
# See `data/ontology/design/ALGORITHMS_EXTRACTION_REQUIREMENTS.md` section 2.
class RefAlgorithm(BaseModel):
    name: Explained[str] = Field(
        description="Name of the Algorithm, EXACTLY as the paper writes it, "
        "including the paper's own abbreviation. Do not translate it into a "
        "canonical or standard term, and do not resolve an ambiguous "
        "abbreviation -- report what the paper wrote",
    )
    aliases: list[str] = Field(
        description="List of names or acronyms used to identify the Algorithm",
    )
    is_contributed: Explained[bool] = Field(
        description="Was the Algorithm a contribution to the research field in the scope of the paper",
    )
    is_executed: Explained[bool] = Field(
        description="Was the Algorithm executed in the scope of the paper, as "
        "opposed to only discussed or cited",
    )
    is_compared: Explained[bool] = Field(
        description="Was the Algorithm compared numerically to other algorithms in the scope of the paper",
    )
    paper_role: Explained[str] = Field(
        description="What the Algorithm does in this paper, IN THE PAPER'S OWN "
        "WORDS -- e.g. 'used to augment the training images', 'the policy "
        "optimisation objective', 'the decoding strategy at test time'. Free "
        "text; do not classify it into a category",
    )
    composed_of: list[str] = Field(
        description="If the paper says this Algorithm is made of other named "
        "procedures, their names as the paper writes them; empty otherwise. Do "
        "not decompose an Algorithm the paper only names",
    )
    referenced_paper_title: Explained[str] = Field(
        description="Title of the reference paper of the Algorithm, found in the references section",
    )

    def __lt__(self, other: "RefAlgorithm"):
        return _lt(self, other, ("referenced_paper_title",))


# `role` on a research field reads differently from `role` on a dataset or a
# library, which is why #89 states the reading here rather than reusing the
# enum's generic wording.
class ResearchField(BaseModel):
    name: Explained[str] = Field(
        description="Name of the Research Field or application domain",
    )
    aliases: list[str] = Field(
        description="List of names or acronyms used to identify the Research Field or application domain",
    )
    role: Role = Field(
        description="'contributed' if the paper advances this field or "
        "addresses a claim to it -- several fields may be contributed, and they "
        "are NOT ranked; 'used' if the paper works in this field as a setting, "
        "benchmark or evaluation venue without advancing it; 'referenced' if it "
        "is named as related context only; 'unknown' if the paper does not make "
        "this clear"
    )

    def __lt__(self, other: "ResearchField"):
        return _lt(self, other, ("aliases",))


# A reference from a Run into one of the top-level entity lists. The pointer
# runs run -> entity, matching `models` and `datasets`, because the cardinality
# is many-to-many and a run row is then self-describing. References are spelled
# as the VERBATIM NAME, not a synthetic id: asking a model to mint and maintain
# ids across two lists is a known failure mode, while asking it to repeat a
# string it just wrote is not. Unmatched names are reported by a check that runs
# after extraction, never by a validator here -- extraction runs inside an
# `instructor` retry loop, where raising would discard a whole paper's
# extraction over one mistyped name.
class RunModel(BaseModel):
    name: str = Field(
        description="Name of the Model, repeated EXACTLY as reported in the models list",
    )
    # `role_in_run`, not `role`: the referenced `RefModel` has a role too
    # (`is_contributed`/`is_compared` at paper level, and `RefDataSource.role`
    # literally spells it `role`), and two fields called `role` carrying
    # different vocabularies on the two ends of one reference is a conflation
    # waiting to be read as one thing.
    role_in_run: ModelRunRole = Field(
        description="How this Run used the Model: 'main' for the model the run "
        "produces or executes, 'critic' for a second network co-optimised in "
        "the same loop to score the first (a GAN discriminator, an RL value "
        "network), 'teacher'/'student' in a distillation run, "
        "'ensemble-member', or 'unknown'",
    )

    def __lt__(self, other: "RunModel"):
        return _lt(self, other, ())


class RunDataSource(BaseModel):
    name: str = Field(
        description="Name of the Dataset, repeated EXACTLY as reported in the datasets list",
    )
    roles_in_run: list[DataSourceRunRole] = Field(
        description="How this Run consumed the Dataset: 'train', 'validation' "
        "and/or 'test' for the splits it was fitted or scored on, or "
        "'reference' for a corpus it only queried at inference without "
        "training on it (a retrieval corpus, a knowledge base). Usually one. "
        "['unknown'] if the paper does not say",
    )

    def __lt__(self, other: "RunDataSource"):
        return _lt(self, other, ())


# No role field, deliberately. The ontology's `role` axis for an algorithm is
# assigned afterwards from the name and the quote, and asking the extractor to
# classify is exactly what would close the vocabulary. The one algorithm fact
# that genuinely varies per run -- what the algorithm did in this paper -- is
# recorded once, in free text, as `RefAlgorithm.paper_role`.
class RunAlgorithm(BaseModel):
    name: str = Field(
        description="Name of the Algorithm, repeated EXACTLY as reported in the algorithms list",
    )

    def __lt__(self, other: "RunAlgorithm"):
        return _lt(self, other, ())


class Run(BaseModel):
    models: list[RunModel] = Field(
        description="The Models this Run executed. Usually one; a list covers "
        "ensembles and student/teacher pairs",
    )
    data_sources: list[RunDataSource] = Field(
        description="The Data Sources this Run consumed",
    )
    algorithms: list[RunAlgorithm] = Field(
        description="The Algorithms this Run executed. May be empty: most "
        "papers name a procedure without tying it to a configuration",
    )
    execution_mode: Explained[ExecutionMode] = Field(
        description="What this Run did, following the precedence "
        "train > finetune > inference > unknown",
    )
    epochs: Explained[str] = Field(
        description="Number of passes over the training data, as the paper "
        "states it; 'unknown' if it does not",
    )
    parameter_count: Explained[str] = Field(
        description="Number of parameters (scale, e.g. '7B', '175B') of the "
        "Model as run in THIS configuration, ONLY if explicitly stated in the "
        "paper; otherwise 'unknown'. NEVER infer or guess it from the Model "
        "name or from prior knowledge; the quote must contain the value stated "
        "in the paper",
    )
    accelerator_type: Explained[AcceleratorType] = Field(
        description="What kind of hardware this Run used: gpu, cpu, tpu, other, "
        "or unknown if the paper does not say",
    )
    accelerator_model: Explained[str] = Field(
        description="The specific accelerator the paper names, e.g. 'A100 80GB', "
        "'TPU v3'; 'unknown' if it names none",
    )
    accelerator_count: Explained[str] = Field(
        description="How many accelerators this Run used, as the paper states "
        "it, e.g. '8', '4 nodes of 8 GPUs'; 'unknown' if it does not",
    )
    precision: Explained[Precision] = Field(
        description="The numerical precision this Run used; 'unknown' if the "
        "paper does not state it",
    )
    parallelism: Explained[list[Parallelism]] = Field(
        description="Which parallelism strategies this Run used: data, tensor, "
        "pipeline, expert, or none. ['unknown'] if the paper does not state it. "
        "NEVER infer this from the libraries the paper used -- DeepSpeed alone "
        "spans ZeRO-1/2/3 and offload variants",
    )
    duration: Explained[str] = Field(
        description="How long this Run took, as the paper states it, preferring "
        "chip-time, e.g. '384 GPU-hours', '3 days on 8 GPUs'; 'unknown' if the "
        "paper does not state it",
    )
    utilisation: Explained[str] = Field(
        description="The hardware utilisation the paper reports, e.g. '45% MFU'; "
        "'unknown' if it reports none. Do NOT substitute a typical or assumed "
        "figure -- an assumed utilisation is applied later, in analysis, and "
        "must not be recorded here as if the paper had stated it",
    )
    repetitions: Explained[str] = Field(
        description="How many executions shared this compute configuration -- "
        "seeds times hyperparameter settings, e.g. '100' for 5 seeds of 20 "
        "learning rates. Often stated ('mean over 5 seeds', 'we swept 20 "
        "configurations'). 'unknown' rather than 1 when the paper does not say",
    )

    def __lt__(self, other: "Run"):
        return _lt(self, other, ())


class PaperExtractions(BaseModel):
    title: Explained[str] = Field(
        description="Title of the paper",
    )
    description: str = Field(
        description="Short description of the paper",
    )
    type: Explained[ResearchType] = Field(
        description="Is the paper an empirical study or a theoretical study",
    )
    # #89: one list with a role, replacing `primary_research_field` plus
    # `sub_research_fields`. The forced rank put a vacuous field
    # (`deep learning`, `machine learning`) in the headline slot for 9.4% of the
    # 1999-paper legacy corpus, with an informative field sitting in the
    # optional list for 186 of those 187 papers.
    research_fields: list[ResearchField] = Field(
        description="All Research Fields and application domains of the paper, "
        "each with its role. Do not rank them",
    )
    models: list[RefModel] = Field(description="All Models found in the paper")
    data_sources: list[RefDataSource] = Field(
        description="All Data Sources found in the paper: fixed datasets, "
        "interactive environments and generators alike"
    )
    libraries: list[RefLibrary] = Field(
        description="All Libraries explicitely used or contributed according to the paper"
    )
    algorithms: list[RefAlgorithm] = Field(
        description="All Algorithms -- named procedures the paper's runs "
        "executed -- found in the paper"
    )
    # Last on purpose: a Run references the entity lists by name, so they have
    # to be written before it can point at them.
    runs: list[Run] = Field(
        description="The distinct compute configurations the paper executed. "
        "Empty if the paper executed nothing"
    )


class ExtractionResponse(BaseModel):
    paper: str
    words: int
    extractions: PaperExtractions
    usage: Any | None


def _is_base(cls, other):
    try:
        return cls.__base__ == other
    except AttributeError:
        return False


def _empty_fields(model_cls: BaseModel):
    try:
        iter_fields = model_cls.model_fields.items()
    except AttributeError:
        if typing.get_origin(model_cls) == list:
            return [_empty_fields(model_cls.__args__[0])]
        else:
            return _EMPTY_FLAG

    if _is_base(model_cls, Explained):
        fields = {k: (_empty_fields(v) if k == "value" else "") for k, v in iter_fields}
    else:
        fields = {}
        for k, field in iter_fields:
            fields[k] = _empty_fields(field.annotation)

    return fields


def empty_model(model_cls):
    empty_fields = _empty_fields(model_cls)
    empty_fields["type"]["value"] = "empirical"
    empty_fields["research_fields"][0]["role"] = "unknown"
    empty_fields["models"][0]["is_contributed"]["value"] = False
    empty_fields["models"][0]["is_executed"]["value"] = False
    empty_fields["models"][0]["is_compared"]["value"] = False
    empty_fields["models"][0]["execution_mode"]["value"] = "unknown"
    empty_fields["data_sources"][0]["role"] = "referenced"
    empty_fields["data_sources"][0]["size"]["value"] = "unknown"
    empty_fields["data_sources"][0]["derived_from"] = []
    empty_fields["data_sources"][0]["sample_properties"] = []
    empty_fields["libraries"][0]["role"] = "referenced"
    empty_fields["algorithms"][0]["is_contributed"]["value"] = False
    empty_fields["algorithms"][0]["is_executed"]["value"] = False
    empty_fields["algorithms"][0]["is_compared"]["value"] = False
    empty_fields["algorithms"][0]["composed_of"] = []
    empty_fields["runs"][0]["models"] = []
    empty_fields["runs"][0]["data_sources"] = []
    empty_fields["runs"][0]["algorithms"] = []
    empty_fields["runs"][0]["execution_mode"]["value"] = "unknown"
    empty_fields["runs"][0]["accelerator_type"]["value"] = "unknown"
    empty_fields["runs"][0]["precision"]["value"] = "unknown"
    empty_fields["runs"][0]["parallelism"]["value"] = ["unknown"]

    return model_cls(**empty_fields)
