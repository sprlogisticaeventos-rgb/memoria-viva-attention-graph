"""Optional GPT-5.6 explanation layer over deterministic replay outputs."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal

from .canonical import canonical_json_bytes, to_plain_json_value
from .contracts import ContractValidationError, SchemaRegistry
from .presentation import (
    DETERMINISTIC_AUTHORITY_STATEMENT,
    DemoViewModel,
    repository_root,
)


DECISION_BRIEF_SCHEMA_ID = (
    "urn:memoria-viva:attention-graph:schema:decision-brief:1.0.0"
)
DECISION_BRIEF_VERSION = "1.0.0"
DEFAULT_OPENAI_MODEL = "gpt-5.6"


class DecisionBriefValidationError(ValueError):
    """A safe structured-output failure that never embeds model output."""

    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        super().__init__(message)


@dataclass(frozen=True)
class DecisionBriefResult:
    """Safe model result; fallback status leaves deterministic output intact."""

    status: Literal["SUCCESS", "FALLBACK"]
    model: str
    brief: Mapping[str, Any] | None
    diagnostic: str | None

    def to_plain_json(self) -> dict[str, Any]:
        return to_plain_json_value(self)


def create_openai_client(api_key: str, *, timeout_seconds: float = 30.0) -> Any:
    """Initialize the official SDK lazily at the application boundary."""

    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("a non-empty API key is required")
    from openai import OpenAI

    return OpenAI(api_key=api_key, timeout=timeout_seconds)


def generate_decision_brief(
    view_model: DemoViewModel,
    client: Any,
    *,
    model: str = DEFAULT_OPENAI_MODEL,
    root: Path | None = None,
    timeout_seconds: float = 30.0,
) -> DecisionBriefResult:
    """Request and validate one strict explanation through Responses API."""

    if not isinstance(view_model, DemoViewModel):
        raise TypeError("view_model must be DemoViewModel")
    if client is None or not hasattr(client, "responses"):
        raise DecisionBriefValidationError(
            "MISSING_OPENAI_CLIENT", "an initialized OpenAI client is required"
        )
    if not isinstance(model, str) or not model.strip():
        raise DecisionBriefValidationError(
            "MISSING_MODEL", "a non-empty model identifier is required"
        )

    project_root = (root or repository_root()).resolve()
    schema = _load_schema(project_root)
    model_input = view_model.explainer_projection()
    response = client.responses.create(
        model=model,
        instructions=_instructions(),
        input=canonical_json_bytes(model_input).decode("utf-8"),
        text={
            "format": {
                "type": "json_schema",
                "name": "memoria_viva_decision_brief",
                "description": (
                    "A human-readable explanation of deterministic replay output."
                ),
                "schema": _api_schema_projection(schema),
                "strict": True,
            }
        },
        max_output_tokens=1800,
        store=False,
        timeout=timeout_seconds,
    )
    output_text = getattr(response, "output_text", None)
    if not isinstance(output_text, str) or not output_text.strip():
        raise DecisionBriefValidationError(
            "EMPTY_MODEL_OUTPUT", "the model returned no structured brief"
        )
    try:
        brief = json.loads(output_text)
    except json.JSONDecodeError as error:
        raise DecisionBriefValidationError(
            "INVALID_MODEL_JSON", "the model returned invalid structured JSON"
        ) from error
    if not isinstance(brief, dict):
        raise DecisionBriefValidationError(
            "INVALID_MODEL_SHAPE", "the model output must be an object"
        )

    # Model identity is application-controlled request metadata, not model-authored
    # semantic content. Canonicalize it to the exact requested identifier before
    # contract and semantic validation.
    brief["model"] = model

    registry = SchemaRegistry(project_root / "schemas")
    try:
        registry.validate(
            DECISION_BRIEF_SCHEMA_ID,
            brief,
            instance_path="memory/gpt-decision-brief.json",
            object_id=None,
        )
    except ContractValidationError as error:
        raise DecisionBriefValidationError(
            "DECISION_BRIEF_SCHEMA_INVALID",
            "the model output did not satisfy the DecisionBrief contract",
        ) from error
    _validate_semantics(brief, view_model, model)
    return DecisionBriefResult(
        status="SUCCESS",
        model=model,
        brief=_deep_freeze(brief),
        diagnostic=None,
    )


def safe_generate_decision_brief(
    view_model: DemoViewModel,
    client: Any | None,
    *,
    model: str = DEFAULT_OPENAI_MODEL,
    root: Path | None = None,
    timeout_seconds: float = 30.0,
) -> DecisionBriefResult:
    """Return a safe fallback status for any credential, API, or output failure."""

    if client is None:
        return DecisionBriefResult(
            status="FALLBACK",
            model=model,
            brief=None,
            diagnostic=(
                "GPT-5.6 brief unavailable: no API credential is configured. "
                "The deterministic engine brief remains available."
            ),
        )
    try:
        return generate_decision_brief(
            view_model,
            client,
            model=model,
            root=root,
            timeout_seconds=timeout_seconds,
        )
    except DecisionBriefValidationError:
        return DecisionBriefResult(
            status="FALLBACK",
            model=model,
            brief=None,
            diagnostic=(
                "GPT-5.6 returned an invalid structured brief. The deterministic "
                "engine brief remains authoritative."
            ),
        )
    except TimeoutError:
        return DecisionBriefResult(
            status="FALLBACK",
            model=model,
            brief=None,
            diagnostic=(
                "GPT-5.6 brief request timed out. The deterministic replay is unchanged."
            ),
        )
    except Exception as error:
        if type(error).__name__ in {"APITimeoutError", "ReadTimeout"}:
            return DecisionBriefResult(
                status="FALLBACK",
                model=model,
                brief=None,
                diagnostic=(
                    "GPT-5.6 brief request timed out. The deterministic replay "
                    "is unchanged."
                ),
            )
        return DecisionBriefResult(
            status="FALLBACK",
            model=model,
            brief=None,
            diagnostic=(
                "GPT-5.6 brief is unavailable. The deterministic replay remains "
                "complete and authoritative."
            ),
        )


def _load_schema(root: Path) -> dict[str, Any]:
    path = root / "schemas" / "decision-brief.schema.json"
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DecisionBriefValidationError(
            "DECISION_BRIEF_SCHEMA_UNAVAILABLE",
            "the DecisionBrief schema is unavailable",
        ) from error
    if not isinstance(schema, dict):
        raise DecisionBriefValidationError(
            "DECISION_BRIEF_SCHEMA_INVALID", "the DecisionBrief schema is invalid"
        )
    return schema


def _api_schema_projection(schema: Mapping[str, Any]) -> dict[str, Any]:
    """Project the repository schema into the strict API-supported subset."""

    omitted = {"$schema", "$id", "title", "description", "x-schema-version"}
    repository_projection = {
        key: to_plain_json_value(value)
        for key, value in schema.items()
        if key not in omitted
    }

    def strip_unsupported_keywords(value: Any) -> Any:
        if isinstance(value, Mapping):
            return {
                key: strip_unsupported_keywords(child)
                for key, child in value.items()
                if key != "uniqueItems"
            }
        if isinstance(value, list):
            return [strip_unsupported_keywords(child) for child in value]
        return value

    return strip_unsupported_keywords(repository_projection)


def _instructions() -> str:
    return (
        "Explain only the supplied sanitized DemoViewModel projection. The "
        "deterministic engine is authoritative. Do not change ranks, scores, "
        "lifecycle, execution, claims, evidence, or uncertainty. State that a "
        "conditional displacement is authorized while execution remains UNKNOWN; "
        "do not claim that conditional movement was executed. Do not claim completion, "
        "compliance, publication approval, or private context. Use only supplied "
        "evidence references. Preserve every supplied critical uncertainty. Any "
        "recommended external action must state that human approval is required."
    )


def _validate_semantics(
    brief: Mapping[str, Any],
    view_model: DemoViewModel,
    model: str,
) -> None:
    projection = view_model.explainer_projection()
    if brief["model"] != model:
        raise DecisionBriefValidationError(
            "MODEL_ID_MISMATCH", "brief model identity does not match the request"
        )
    if brief["replay_digest"] != view_model.replay_digest:
        raise DecisionBriefValidationError(
            "REPLAY_DIGEST_MISMATCH", "brief replay identity is invalid"
        )
    if brief["deterministic_authority_statement"] != DETERMINISTIC_AUTHORITY_STATEMENT:
        raise DecisionBriefValidationError(
            "AUTHORITY_STATEMENT_MISMATCH",
            "brief does not preserve deterministic authority",
        )

    allowed_evidence = {
        item["evidence_id"] for item in projection["evidence"]
    }
    if not set(brief["evidence_refs"]).issubset(allowed_evidence):
        raise DecisionBriefValidationError(
            "UNSUPPORTED_EVIDENCE", "brief references evidence outside the supplied view"
        )
    required_uncertainty = set(projection["unresolved_uncertainties"])
    if not required_uncertainty.issubset(set(brief["uncertainties"])):
        raise DecisionBriefValidationError(
            "UNCERTAINTY_OMITTED", "brief omitted deterministic uncertainty"
        )
    next_action = brief["next_smallest_action"].lower()
    if "approval" not in next_action and "review" not in next_action:
        raise DecisionBriefValidationError(
            "APPROVAL_GUARDRAIL_MISSING",
            "brief action does not preserve its human approval boundary",
        )

    text = " ".join(_all_strings(brief)).lower()
    prohibited_claims = (
        "cmt-04 was moved",
        "cmt-04 has moved",
        "movement was executed",
        "displacement was executed",
        "goal is complete",
        "goal was completed",
        "submission is complete",
        "compliance is verified",
        "public release is approved",
    )
    if any(claim in text for claim in prohibited_claims):
        raise DecisionBriefValidationError(
            "UNSUPPORTED_STRONG_CLAIM", "brief introduces an unsupported stronger claim"
        )
    if re.search(r"\bsk-[A-Za-z0-9_-]+", text):
        raise DecisionBriefValidationError(
            "SECRET_LIKE_OUTPUT", "brief contains secret-like content"
        )
    if re.search(r"(?:^|\s)(?:/Users/|/home/|[A-Za-z]:\\\\)", text):
        raise DecisionBriefValidationError(
            "PATH_LIKE_OUTPUT", "brief contains a private path"
        )


def _all_strings(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Mapping):
        return tuple(
            string for item in value.values() for string in _all_strings(item)
        )
    if isinstance(value, (list, tuple)):
        return tuple(string for item in value for string in _all_strings(item))
    return ()


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _deep_freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_deep_freeze(item) for item in value)
    return value
