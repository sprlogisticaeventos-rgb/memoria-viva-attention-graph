"""Optional GPT-5.6 rewrite of an already-completed deterministic ChatAnswer."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal

from .canonical import canonical_json_bytes, to_plain_json_value
from .chat import GUIDED_QUESTION_OPTIONS, ChatAnswer, normalize_question
from .contracts import ContractValidationError, SchemaRegistry
from .explainer import DEFAULT_OPENAI_MODEL, _api_schema_projection
from .presentation import repository_root


CHAT_RESPONSE_SCHEMA_ID = (
    "urn:memoria-viva:attention-graph:schema:chat-response:1.0.0"
)
CHAT_RESPONSE_VERSION = "1.0.0"
MAX_RECOMMENDATION_WORDS = 130
GPT_RECOMMENDATION_QUESTIONS = (
    GUIDED_QUESTION_OPTIONS[0],
    GUIDED_QUESTION_OPTIONS[-1],
)
_NORMALIZED_GPT_RECOMMENDATION_QUESTIONS = frozenset(
    normalize_question(question) for question in GPT_RECOMMENDATION_QUESTIONS
)
_MODEL_AUTHORED_FIELDS = (
    "what_this_means",
    "recommended_next_move",
    "approval_or_uncertainty_note",
)
_APPROVED_NON_EXECUTION_STATEMENTS = (
    r"\bno\s+movement\s+was\s+executed\b",
    r"\bmovement\s+was\s+not\s+executed\b",
    r"\bmovement\s+has\s+not\s+been\s+executed\b",
    r"\bno\s+displacement\s+was\s+executed\b",
    r"\bdisplacement\s+was\s+not\s+executed\b",
    r"\bdisplacement\s+has\s+not\s+been\s+executed\b",
    r"\bconditional\s+movement\s+did\s+not\s+occur\b",
    r"\bconditional\s+movement\s+has\s+not\s+occurred\b",
    r"\bexecution\s+remains\s+unknown\b",
    r"\bexecution\s+is\s+unknown\b",
)


class ChatResponseValidationError(ValueError):
    """Safe structured-output error that never embeds generated or secret text."""

    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        super().__init__(message)


@dataclass(frozen=True)
class ChatRewriteResult:
    """Optional rewrite result; deterministic ChatAnswer always remains available."""

    status: Literal["SUCCESS", "FALLBACK"]
    model: str
    response: Mapping[str, Any] | None
    diagnostic: str | None

    def to_plain_json(self) -> dict[str, Any]:
        value = to_plain_json_value(self)
        if not isinstance(value, dict):
            raise TypeError("ChatRewriteResult must project to an object")
        return value


def generate_chat_rewrite(
    answer: ChatAnswer,
    client: Any,
    *,
    model: str = DEFAULT_OPENAI_MODEL,
    root: Path | None = None,
    timeout_seconds: float = 30.0,
) -> ChatRewriteResult:
    """Generate language only; all identity and grounding fields are code-owned."""

    if not isinstance(answer, ChatAnswer):
        raise TypeError("answer must be ChatAnswer")
    if client is None or not hasattr(client, "responses"):
        raise ChatResponseValidationError(
            "MISSING_OPENAI_CLIENT", "an initialized OpenAI client is required"
        )
    if not isinstance(model, str) or not model.strip():
        raise ChatResponseValidationError(
            "MISSING_MODEL", "a non-empty model identifier is required"
        )
    if normalize_question(answer.question) not in _NORMALIZED_GPT_RECOMMENDATION_QUESTIONS:
        raise ChatResponseValidationError(
            "UNSUPPORTED_RECOMMENDATION_QUESTION",
            "GPT recommendation is unavailable for this deterministic question",
        )

    project_root = (root or repository_root()).resolve()
    schema = _load_schema(project_root)
    model_input = _model_input(answer)
    response = client.responses.create(
        model=model,
        instructions=_instructions(),
        input=canonical_json_bytes(model_input).decode("utf-8"),
        text={
            "format": {
                "type": "json_schema",
                "name": "memoria_viva_grounded_chat_rewrite",
                "description": (
                    "Conversational language for a completed deterministic answer."
                ),
                "schema": _api_schema_projection(_model_authored_schema(schema)),
                "strict": True,
            }
        },
        max_output_tokens=900,
        store=False,
        timeout=timeout_seconds,
    )
    output_text = getattr(response, "output_text", None)
    if not isinstance(output_text, str) or not output_text.strip():
        raise ChatResponseValidationError(
            "EMPTY_MODEL_OUTPUT", "the model returned no structured chat rewrite"
        )
    try:
        generated = json.loads(output_text)
    except json.JSONDecodeError as error:
        raise ChatResponseValidationError(
            "INVALID_MODEL_JSON", "the model returned invalid structured JSON"
        ) from error
    if not isinstance(generated, dict):
        raise ChatResponseValidationError(
            "INVALID_MODEL_SHAPE", "the model output must be an object"
        )
    if not all(
        isinstance(generated.get(field), str) and generated[field].strip()
        for field in _MODEL_AUTHORED_FIELDS
    ):
        raise ChatResponseValidationError(
            "MODEL_LANGUAGE_FIELDS_MISSING",
            "the model omitted a required conversational field",
        )

    # The model can author only language. Receipt and grounding fields are copied
    # from the deterministic ChatAnswer regardless of similarly named model output.
    chat_response = {
        "chat_response_version": CHAT_RESPONSE_VERSION,
        "model": model,
        "answer_id": answer.answer_id,
        "replay_digest": answer.replay_digest,
        "intent": answer.intent,
        "what_this_means": generated["what_this_means"],
        "recommended_next_move": generated["recommended_next_move"],
        "approval_or_uncertainty_note": generated[
            "approval_or_uncertainty_note"
        ],
        "evidence_refs": list(answer.evidence_refs),
        "unknowns": list(answer.unknowns),
        "approval_required_items": list(answer.approval_required_items),
    }
    registry = SchemaRegistry(project_root / "schemas")
    try:
        registry.validate(
            CHAT_RESPONSE_SCHEMA_ID,
            chat_response,
            instance_path="memory/gpt-chat-response.json",
            object_id=answer.answer_id,
        )
    except ContractValidationError as error:
        raise ChatResponseValidationError(
            "CHAT_RESPONSE_SCHEMA_INVALID",
            "the generated rewrite did not satisfy the local chat contract",
        ) from error
    _validate_semantics(chat_response, answer, model)
    return ChatRewriteResult(
        status="SUCCESS",
        model=model,
        response=_deep_freeze(chat_response),
        diagnostic=None,
    )


def safe_generate_chat_rewrite(
    answer: ChatAnswer,
    client: Any | None,
    *,
    model: str = DEFAULT_OPENAI_MODEL,
    root: Path | None = None,
    timeout_seconds: float = 30.0,
) -> ChatRewriteResult:
    """Fail closed while leaving the deterministic answer immediately usable."""

    if client is None:
        return ChatRewriteResult(
            status="FALLBACK",
            model=model,
            response=None,
            diagnostic=(
                "GPT-5.6 conversational rewrite unavailable: no API credential "
                "is configured. The deterministic answer remains available."
            ),
        )
    try:
        return generate_chat_rewrite(
            answer,
            client,
            model=model,
            root=root,
            timeout_seconds=timeout_seconds,
        )
    except ChatResponseValidationError:
        return ChatRewriteResult(
            status="FALLBACK",
            model=model,
            response=None,
            diagnostic=(
                "GPT-5.6 returned an invalid grounded rewrite. The deterministic "
                "answer remains authoritative."
            ),
        )
    except TimeoutError:
        return ChatRewriteResult(
            status="FALLBACK",
            model=model,
            response=None,
            diagnostic=(
                "GPT-5.6 conversational rewrite timed out. The deterministic "
                "answer is unchanged."
            ),
        )
    except Exception as error:
        if type(error).__name__ in {"APITimeoutError", "ReadTimeout"}:
            return ChatRewriteResult(
                status="FALLBACK",
                model=model,
                response=None,
                diagnostic=(
                    "GPT-5.6 conversational rewrite timed out. The deterministic "
                    "answer is unchanged."
                ),
            )
        return ChatRewriteResult(
            status="FALLBACK",
            model=model,
            response=None,
            diagnostic=(
                "GPT-5.6 conversational rewrite is unavailable. The deterministic "
                "answer remains complete and authoritative."
            ),
        )


def _model_input(answer: ChatAnswer) -> dict[str, Any]:
    plain = answer.to_plain_json()
    normalized_question = normalize_question(answer.question)
    # The free-form browser text is not forwarded twice. The completed answer
    # remains intact semantically, but its question field uses the same bounded
    # normalization as the explicit model input field.
    plain["question"] = normalized_question
    return {
        "normalized_question": normalized_question,
        "deterministic_answer": plain,
        "public_safe_item_labels": [
            item["public_label"] for item in plain["attention_items"]
        ],
        "evidence_refs": plain["evidence_refs"],
        "unknowns": plain["unknowns"],
        "approval_required_items": plain["approval_required_items"],
        "replay_digest": plain["replay_digest"],
    }


def _instructions() -> str:
    return (
        "Explain only the supplied deterministic ChatAnswer. Return exactly "
        "what_this_means, recommended_next_move, and "
        "approval_or_uncertainty_note, with no more than 130 words across all "
        "three fields. The recommendation must be the next "
        "smallest action consistent with the verified ranking, dependency order, "
        "execution states, uncertainty, and approvals. Do not rerank, change "
        "scores or restate rank or score numbers, predict future events, claim "
        "completion, claim compliance, claim executed displacement, introduce an "
        "unsupported entity or evidence reference, or bypass approval. Preserve "
        "uncertainty. "
        "If both the demonstration and submission package are present, recommend "
        "the demonstration before the dependent package. Conditional displacement "
        "may be authorized, but execution remains UNKNOWN and no movement was "
        "executed."
    )


def _model_authored_schema(schema: Mapping[str, Any]) -> dict[str, Any]:
    properties = schema.get("properties")
    if not isinstance(properties, Mapping):
        raise ChatResponseValidationError(
            "CHAT_RESPONSE_SCHEMA_INVALID", "chat schema properties are unavailable"
        )
    return {
        "type": "object",
        "properties": {
            field: to_plain_json_value(properties[field])
            for field in _MODEL_AUTHORED_FIELDS
        },
        "required": list(_MODEL_AUTHORED_FIELDS),
        "additionalProperties": False,
    }


def _load_schema(root: Path) -> dict[str, Any]:
    path = root / "schemas" / "chat-response.schema.json"
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ChatResponseValidationError(
            "CHAT_RESPONSE_SCHEMA_UNAVAILABLE", "the chat schema is unavailable"
        ) from error
    if not isinstance(schema, dict):
        raise ChatResponseValidationError(
            "CHAT_RESPONSE_SCHEMA_INVALID", "the chat schema is invalid"
        )
    return schema


def _validate_semantics(
    response: Mapping[str, Any], answer: ChatAnswer, model: str
) -> None:
    if response["model"] != model:
        raise ChatResponseValidationError(
            "MODEL_ID_MISMATCH", "chat response model identity is invalid"
        )
    if response["answer_id"] != answer.answer_id:
        raise ChatResponseValidationError(
            "ANSWER_ID_MISMATCH", "chat response answer identity is invalid"
        )
    if response["replay_digest"] != answer.replay_digest:
        raise ChatResponseValidationError(
            "REPLAY_DIGEST_MISMATCH", "chat response replay identity is invalid"
        )
    if response["intent"] != answer.intent:
        raise ChatResponseValidationError(
            "INTENT_MISMATCH", "chat response intent is invalid"
        )
    if tuple(response["evidence_refs"]) != answer.evidence_refs:
        raise ChatResponseValidationError(
            "EVIDENCE_BOUNDARY_CHANGED", "chat response changed evidence references"
        )
    if tuple(response["unknowns"]) != answer.unknowns:
        raise ChatResponseValidationError(
            "UNCERTAINTY_BOUNDARY_CHANGED", "chat response changed uncertainty"
        )
    if tuple(response["approval_required_items"]) != answer.approval_required_items:
        raise ChatResponseValidationError(
            "APPROVAL_BOUNDARY_CHANGED", "chat response changed approval requirements"
        )
    text = " ".join(
        (
            response["what_this_means"],
            response["recommended_next_move"],
            response["approval_or_uncertainty_note"],
        )
    )
    lowered = text.casefold()
    if len(text.split()) > MAX_RECOMMENDATION_WORDS:
        raise ChatResponseValidationError(
            "RECOMMENDATION_TOO_LONG",
            "chat response exceeded the concise recommendation boundary",
        )
    evidence_mentions = set(re.findall(r"\bEV-[A-Z0-9-]+\b", text))
    if not evidence_mentions.issubset(set(answer.evidence_refs)):
        raise ChatResponseValidationError(
            "UNSUPPORTED_EVIDENCE", "chat response introduced unsupported evidence"
        )
    if answer.unknowns and not any(
        word in lowered
        for word in (
            "unknown",
            "uncertain",
            "unverified",
            "unresolved",
            "pending",
            "not established",
            "not confirmed",
            "requires verification",
        )
    ):
        raise ChatResponseValidationError(
            "UNCERTAINTY_OMITTED", "chat response omitted deterministic uncertainty"
        )
    if answer.approval_required_items and not any(
        word in response["approval_or_uncertainty_note"].casefold()
        for word in ("approval", "confirm", "authority")
    ):
        raise ChatResponseValidationError(
            "APPROVAL_GUARDRAIL_OMITTED",
            "chat response omitted the approval boundary",
        )
    deterministic_text = canonical_json_bytes(answer.to_plain_json()).decode(
        "utf-8"
    ).casefold()
    entity_mentions = set(
        re.findall(
            r"\b(?:CMT(?:-T0)?-\d+|GC-\d+|ATTN-[A-Z0-9-]+)\b",
            text,
            flags=re.IGNORECASE,
        )
    )
    unsupported_entities = {
        entity
        for entity in entity_mentions
        if entity.casefold() not in deterministic_text
    }
    if unsupported_entities:
        raise ChatResponseValidationError(
            "UNSUPPORTED_ENTITY", "chat response introduced an unsupported entity"
        )
    recommendation = response["recommended_next_move"].casefold()
    reversed_dependency = re.search(
        r"\bsubmission(?: package)?\b.{0,90}"
        r"\b(?:before|then|ahead of)\b.{0,90}\bdemonstration\b",
        recommendation,
    )
    if reversed_dependency:
        raise ChatResponseValidationError(
            "DEPENDENCY_ORDER_CHANGED",
            "chat response reversed the verified prerequisite order",
        )
    prohibited_claims = (
        "movement was executed",
        "movement has been executed",
        "displacement was executed",
        "pending bounded validation moved",
        "movement will occur",
        "displacement will occur",
        "conditional movement occurred",
        "conditional movement has occurred",
        "execution is known",
        "execution is confirmed",
        "execution has been confirmed",
        "will be completed",
        "will be submitted",
        "will succeed",
        "will pass",
        "is guaranteed",
        "can proceed immediately",
        "proceed without approval",
        "no approval is required",
        "approval can be bypassed",
        "goal is complete",
        "goal was completed",
        "submission is complete",
        "compliance is verified",
        "public release is approved",
    )
    strong_claim_projection = _strip_approved_non_execution_statements(text)
    if any(claim in strong_claim_projection for claim in prohibited_claims):
        raise ChatResponseValidationError(
            "UNSUPPORTED_STRONG_CLAIM",
            "chat response introduced an unsupported stronger claim",
        )
    if re.search(r"(?:\brank\s+\d+\b|#\d+)", lowered):
        raise ChatResponseValidationError(
            "RANK_RESTATED", "chat response must not restate or change rank values"
        )
    if re.search(r"\bscore(?:d|s)?\s+(?:of\s+)?\d+(?:\.\d+)?\b", lowered):
        raise ChatResponseValidationError(
            "SCORE_RESTATED", "chat response must not restate or change score values"
        )
    if re.search(r"\bsk-[A-Za-z0-9_-]+", text):
        raise ChatResponseValidationError(
            "SECRET_LIKE_OUTPUT", "chat response contains secret-like content"
        )
    if re.search(r"(?:^|\s)(?:/Users/|/home/|[A-Za-z]:\\\\)", text):
        raise ChatResponseValidationError(
            "PATH_LIKE_OUTPUT", "chat response contains a private path"
        )


def _strip_approved_non_execution_statements(value: str) -> str:
    """Remove only approved non-execution clauses from claim-scan text."""

    projection = value.casefold()
    for pattern in _APPROVED_NON_EXECUTION_STATEMENTS:
        projection = re.sub(pattern, " ", projection)
    return projection


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {key: _deep_freeze(child) for key, child in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_deep_freeze(child) for child in value)
    return value
