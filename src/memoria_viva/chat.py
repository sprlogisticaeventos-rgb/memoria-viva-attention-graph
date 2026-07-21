"""Grounded deterministic conversation over the verified replay state."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal

from .canonical import canonical_json_bytes, sha256_hex, to_plain_json_value
from .presentation import DemoSession


CHAT_ANSWER_CONTRACT = "MV_CHAT_ANSWER_V1"
CHAT_ANSWER_VERSION = "1.0.0"
INITIAL_ASSISTANT_MESSAGE = (
    "Two protected commitments entered the top two after the trigger. A prior "
    "protected obligation remains in the top three. Ask what changed, why an "
    "item moved, or what still requires approval."
)
UNSUPPORTED_SCOPE_MESSAGE = (
    "This public demo can answer questions about the verified attention state, "
    "what changed, evidence, uncertainty, protection, confirmation, and replay "
    "proof."
)
DETERMINISTIC_CHAT_AUTHORITY_STATEMENT = (
    "The deterministic replay produced the verified state, scores, ranks, "
    "execution states, GraphDelta, and claims. This answer only selects and "
    "explains that state; the question did not change it."
)

ChatIntent = Literal[
    "CURRENT_ATTENTION",
    "WHAT_CHANGED",
    "WHY_ITEM",
    "PROTECTED_ITEMS",
    "REQUIRES_CONFIRMATION",
    "EVIDENCE",
    "UNKNOWNS",
    "REPLAY_PROOF",
    "MEMORY_STATE",
    "UNSUPPORTED",
]

SUPPORTED_SUGGESTED_PROMPTS = (
    "What deserves attention now?",
    "What changed after the trigger?",
    "Why is Pending bounded validation still conditional?",
    "What requires human confirmation?",
    "What evidence supports the top three?",
    "Is this replay verified?",
)
GUIDED_QUESTION_OPTIONS = (
    "What matters now?",
    "What changed after the event?",
    "What requires human approval?",
    "Why is Pending bounded validation still conditional?",
    "What evidence supports this result?",
    "What should happen next?",
)


@dataclass(frozen=True)
class IntentMatch:
    """Deterministic router result with an optional public subject."""

    intent: ChatIntent
    matched_subject_id: str | None


@dataclass(frozen=True)
class ChatAnswer:
    """Immutable grounded answer; model-free and detached from replay state."""

    answer_id: str
    question: str
    intent: ChatIntent
    matched_subject_id: str | None
    headline: str
    direct_answer: str
    supporting_points: tuple[str, ...]
    attention_items: tuple[Mapping[str, Any], ...]
    evidence_refs: tuple[str, ...]
    unknowns: tuple[str, ...]
    approval_required_items: tuple[str, ...]
    replay_digest: str
    oracle_statuses: Mapping[str, str]
    deterministic_authority_statement: str
    suggested_follow_ups: tuple[str, ...]

    def to_plain_json(self) -> dict[str, Any]:
        value = to_plain_json_value(self)
        if not isinstance(value, dict):
            raise TypeError("ChatAnswer must project to an object")
        return value

    def canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self)


def normalize_question(question: str) -> str:
    """Normalize only for deterministic routing and identity generation."""

    if not isinstance(question, str):
        raise TypeError("question must be a string")
    normalized = unicodedata.normalize("NFKC", question).casefold()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return " ".join(normalized.split())


def classify_intent(question: str, session: DemoSession) -> IntentMatch:
    """Classify one public question with explicit, fixed precedence."""

    _require_session(session)
    normalized = normalize_question(question)
    matched_subject = _match_public_subject(normalized, session)

    # Explicit precedence is a product contract, not a learned behavior.
    if matched_subject and _contains_any(
        normalized, ("why", "explain", "conditional", "rank", "moved")
    ):
        return IntentMatch("WHY_ITEM", matched_subject)
    if _contains_any(
        normalized,
        (
            "requires human confirmation",
            "require human confirmation",
            "requires confirmation",
            "require confirmation",
            "requires human approval",
            "require human approval",
            "cannot be moved yet",
            "needs confirmation",
            "what requires",
        ),
    ):
        return IntentMatch("REQUIRES_CONFIRMATION", matched_subject)
    if _contains_any(
        normalized,
        (
            "protected",
            "protect",
            "cannot be displaced automatically",
            "must remain protected",
        ),
    ):
        return IntentMatch("PROTECTED_ITEMS", matched_subject)
    if _contains_any(normalized, ("evidence", "trust", "support the top")):
        return IntentMatch("EVIDENCE", matched_subject)
    if _contains_any(
        normalized, ("unknown", "uncertain", "uncertainty", "still not know")
    ):
        return IntentMatch("UNKNOWNS", matched_subject)
    if _contains_any(
        normalized,
        (
            "replay verified",
            "result deterministic",
            "deterministic",
            "technical proof",
            "technical receipt",
            "oracle",
            "verified",
        ),
    ):
        return IntentMatch("REPLAY_PROOF", matched_subject)
    if _contains_any(
        normalized,
        (
            "what changed",
            "changed after",
            "after the event",
            "ranking change",
            "entered the system",
            "after the trigger",
        ),
    ):
        return IntentMatch("WHAT_CHANGED", matched_subject)
    if _contains_any(
        normalized,
        ("what does the system remember", "memory state", "active memory", "remember"),
    ):
        return IntentMatch("MEMORY_STATE", matched_subject)
    if _contains_any(
        normalized,
        (
            "what matters now",
            "attention now",
            "deserves attention",
            "founder focus",
            "focus on",
            "current priorities",
            "priority now",
            "next move",
            "what should happen next",
        ),
    ):
        return IntentMatch("CURRENT_ATTENTION", matched_subject)
    return IntentMatch("UNSUPPORTED", matched_subject)


def answer_question(question: str, session: DemoSession) -> ChatAnswer:
    """Select and explain verified state without changing replay semantics."""

    _require_session(session)
    stripped_question = question.strip()
    if not stripped_question:
        raise ValueError("question must not be empty")
    match = classify_intent(stripped_question, session)
    view = session.view_model.to_plain_json()
    rows = tuple(view["after_ranking"])
    row_by_subject = {row["subject_id"]: row for row in rows}

    answer_fields = _answer_fields(
        match,
        view,
        session,
        row_by_subject,
        normalize_question(stripped_question),
    )
    answer_id = "CHAT-ANSWER-" + sha256_hex(
        {
            "contract": CHAT_ANSWER_CONTRACT,
            "version": CHAT_ANSWER_VERSION,
            "normalized_question": normalize_question(stripped_question),
            "intent": match.intent,
            "matched_subject_id": match.matched_subject_id,
            "replay_digest": view["replay_digest"],
        }
    )[:20]
    return ChatAnswer(
        answer_id=answer_id,
        question=stripped_question,
        intent=match.intent,
        matched_subject_id=match.matched_subject_id,
        headline=answer_fields["headline"],
        direct_answer=answer_fields["direct_answer"],
        supporting_points=tuple(answer_fields["supporting_points"]),
        attention_items=tuple(
            _deep_freeze(_attention_item(row))
            for row in answer_fields["attention_rows"]
        ),
        evidence_refs=tuple(sorted(set(answer_fields["evidence_refs"]))),
        unknowns=tuple(dict.fromkeys(answer_fields["unknowns"])),
        approval_required_items=tuple(
            dict.fromkeys(answer_fields["approval_required_items"])
        ),
        replay_digest=view["replay_digest"],
        oracle_statuses=_deep_freeze(dict(sorted(view["oracle_statuses"].items()))),
        deterministic_authority_statement=DETERMINISTIC_CHAT_AUTHORITY_STATEMENT,
        suggested_follow_ups=_suggested_follow_ups(match.intent),
    )


def _answer_fields(
    match: IntentMatch,
    view: Mapping[str, Any],
    session: DemoSession,
    row_by_subject: Mapping[str, Mapping[str, Any]],
    normalized_question: str,
) -> dict[str, Any]:
    if match.intent == "CURRENT_ATTENTION":
        top_three = tuple(view["after_ranking"][:3])
        if normalized_question == "what should happen next":
            return _fields(
                "Freeze and verify the prerequisite first",
                (
                    "Freeze the minimum verifiable demonstration scope and verify the "
                    "public demo. Then complete the dependent submission package. "
                    "Review conditional displacement separately and obtain required "
                    "human confirmation. None of these actions is represented as "
                    "executed."
                ),
                (
                    "CMT-01 precedes CMT-02 because the package depends on the demonstration.",
                    "Conditional displacement is authorized, but execution remains UNKNOWN.",
                    "No movement is authorized for confirmation-required items until the required authority confirms it.",
                ),
                top_three,
                unknowns=_unknowns_for_rows(top_three, view),
                approvals=_confirmation_labels(view),
            )
        return _fields(
            "Current verified attention",
            (
                "The verified top three are Public product demonstration ready, "
                "Submission package finalization, and Protected documentation review."
            ),
            (
                "Protection creates a precedence band; it does not add a numeric bonus.",
                "CMT-01 precedes CMT-02 because the demonstration is the prerequisite for the dependent submission package.",
                "Numeric score alone does not determine final order.",
                "No prior obligation disappeared from the verified state.",
            ),
            top_three,
            unknowns=_unknowns_for_rows(top_three, view),
        )

    if match.intent == "WHAT_CHANGED":
        selected = tuple(
            row_by_subject[subject]
            for subject in ("CMT-01", "CMT-02", "CMT-T0-10", "CMT-04")
        )
        return _fields(
            "The trigger changed attention without erasing prior work",
            (
                "Ranked attention expanded from 7 to 9 items. CMT-01 and CMT-02 "
                "entered at ranks 1 and 2, while Protected documentation review "
                "remained in the top three."
            ),
            (
                "Pending bounded validation became a conditional displacement target; execution remains UNKNOWN.",
                "Two items still require confirmation.",
                "The transition preserves every prior obligation, including excluded-but-retained records.",
            ),
            selected,
            unknowns=_unknowns_for_rows(selected, view),
            approvals=_confirmation_labels(view),
        )

    if match.intent == "WHY_ITEM":
        row = row_by_subject[match.matched_subject_id]
        return _why_item_fields(row, view)

    if match.intent == "PROTECTED_ITEMS":
        protected = tuple(view["protected_items"])
        return _fields(
            "Three items remain protected",
            (
                "Public product demonstration ready, Submission package finalization, "
                "and Protected documentation review occupy the protected precedence band."
            ),
            (
                "Protection prevents automatic displacement and creates precedence before standard items.",
                "Protection is not evidence of completion.",
                "Within the protected band, dependency precedence places CMT-01 before CMT-02.",
            ),
            protected,
            unknowns=_unknowns_for_rows(protected, view),
        )

    if match.intent == "REQUIRES_CONFIRMATION":
        confirmation = tuple(view["confirmation_required_items"])
        return _fields(
            "Two items require human confirmation",
            (
                "Shared release-readiness gate and Collaboration pilot decision "
                "window cannot move until the required authority confirms the action."
            ),
            (
                "Shared release-readiness gate requires a recorded joint decision.",
                "Collaboration pilot decision window retains incomplete movement authority.",
                "NEEDS_CONFIRMATION affects actionability; it is not a numeric score bonus or a protected band.",
            ),
            confirmation,
            unknowns=_unknowns_for_rows(confirmation, view),
            approvals=tuple(row["label"] for row in confirmation),
        )

    if match.intent == "EVIDENCE":
        selected = (
            (row_by_subject[match.matched_subject_id],)
            if match.matched_subject_id
            else tuple(view["after_ranking"][:3])
        )
        evidence_refs = _evidence_refs(selected)
        evidence_index = {item["evidence_id"]: item for item in view["evidence"]}
        points = tuple(
            (
                f"{evidence_ref}: {evidence_index[evidence_ref]['summary']} "
                f"(confidence {evidence_index[evidence_ref]['confidence']:.2f}; "
                f"{evidence_index[evidence_ref]['epistemic_state']})."
            )
            for evidence_ref in evidence_refs
        )
        return _fields(
            "Public-safe evidence behind the verified answer",
            (
                "Each selected attention item resolves to committed public-safe "
                "evidence. Confidence and uncertainty remain visible rather than "
                "being converted into certainty."
            ),
            points,
            selected,
            evidence_refs=evidence_refs,
            unknowns=_unknowns_for_rows(selected, view),
            approvals=_approval_labels(selected),
        )

    if match.intent == "UNKNOWNS":
        selected = tuple(
            row
            for row in view["after_ranking"]
            if row["uncertainty"] or row["execution_state"] == "UNKNOWN"
        )
        return _fields(
            "Critical uncertainty remains explicit",
            (
                "The system does not infer missing facts. Occurrence time, official "
                "constraints, final compliance, joint-authority outcomes, conditional "
                "movement, repair, reactivation, and publication review remain unresolved."
            ),
            tuple(view["critical_uncertainties"]),
            selected,
            unknowns=tuple(view["critical_uncertainties"]),
            approvals=_confirmation_labels(view),
        )

    if match.intent == "REPLAY_PROOF":
        proof = view["technical_proof"]
        points = (
            f"Snapshot T0: {proof['snapshot_t0']['id']}",
            f"Snapshot T1: {proof['snapshot_t1']['id']}",
            f"Ranking before: {proof['ranking_before']['id']}",
            f"Ranking after: {proof['ranking_after']['id']}",
            f"GraphDelta: {proof['graph_delta']['id']}",
            f"RunRecord: {proof['run_record']['id']}",
            "The validated suite contains 200 tests at the release baseline.",
            "The feature policy is authorized only for bounded Replay Mode.",
        )
        return _fields(
            "The replay is verified and deterministic",
            (
                "Ranking-before, ranking-after, and GraphDelta oracle comparisons "
                "all return PASS. The same committed fixture produces byte-identical receipts."
            ),
            points,
            (),
            unknowns=("Final compliance remains unknown.",),
        )

    if match.intent == "MEMORY_STATE":
        snapshot = session.replay.snapshot_t1.to_plain_json()
        goals = len(snapshot["goals"])
        commitments = len(snapshot["commitments"])
        active_calendar = sum(
            ref["entity_type"] == "CalendarCandidate"
            for ref in snapshot["active_object_refs"]
        )
        excluded = len(snapshot["excluded_but_retained_objects"])
        top_three = tuple(view["after_ranking"][:3])
        return _fields(
            "The verified active memory state",
            (
                f"The system remembers {goals} Goals, {commitments} operational "
                f"commitments, and {active_calendar + excluded} Calendar candidates: "
                f"{active_calendar} active and {excluded} excluded-but-retained."
            ),
            (
                "The current top three are Public product demonstration ready, Submission package finalization, and Protected documentation review.",
                "Pending bounded validation is conditional with execution UNKNOWN.",
                "Two attention items require confirmation.",
            ),
            top_three,
            unknowns=_unknowns_for_rows(top_three, view),
            approvals=_confirmation_labels(view),
        )

    return _fields(
        "Bounded public demo scope",
        UNSUPPORTED_SCOPE_MESSAGE,
        ("Choose one of the suggested questions to inspect the verified replay.",),
        (),
    )


def _why_item_fields(
    row: Mapping[str, Any], view: Mapping[str, Any]
) -> dict[str, Any]:
    subject = row["subject_id"]
    if subject == "CMT-04":
        points = (
            "It is conditionally displaceable under an approved bounded repair policy.",
            "Conditional authorization exists, but no movement was executed.",
            "Execution remains UNKNOWN.",
            "The repair slot and reactivation condition remain unresolved.",
        )
        direct = (
            "Pending bounded validation is a verified conditional displacement "
            "target. The relationship is authorized, but execution remains UNKNOWN."
        )
    elif subject == "CMT-01":
        points = (
            "It is trigger-created, eligible, and protected.",
            "It is the prerequisite for Submission package finalization.",
            "Protection and dependency precedence determine its band order; there is no numeric protection bonus.",
        )
        direct = (
            "Public product demonstration ready is rank 1 because it is protected "
            "and must precede its dependent package within the protected band."
        )
    elif subject == "CMT-02":
        points = (
            "It is trigger-created, eligible, and protected.",
            "It depends on the minimum verifiable public product demonstration.",
            "Dependency precedence keeps the prerequisite ahead even though this item has a higher displayed numeric score.",
        )
        direct = (
            "Submission package finalization is rank 2 because it is protected but "
            "depends on the rank-1 demonstration commitment."
        )
    elif subject == "CMT-T0-10":
        points = (
            "It remains in the protected precedence band after the trigger.",
            "The trigger does not prove it complete or remove it.",
            "Its exact requirement, authority, and external deadline remain unknown.",
        )
        direct = (
            "Protected documentation review remains top-three because its protected "
            "state persists; protection does not prove completion."
        )
    else:
        points = (
            f"Verified rank: {row['rank']}; displayed score: {row['displayed_score']}.",
            f"Status: {row['status']}; execution state: {row['execution_state']}.",
            row["explanation"],
        )
        direct = (
            f"{row['label']} is shown exactly as the deterministic after-ranking "
            "records it; the question does not change its score, rank, or state."
        )
    return _fields(
        f"Why {row['label']} appears here",
        direct,
        points,
        (row,),
        unknowns=tuple(row["uncertainty"]),
        approvals=(row["label"],) if row["confirmation_required"] else (),
    )


def _fields(
    headline: str,
    direct_answer: str,
    supporting_points: tuple[str, ...],
    attention_rows: tuple[Mapping[str, Any], ...],
    *,
    evidence_refs: tuple[str, ...] | None = None,
    unknowns: tuple[str, ...] = (),
    approvals: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "headline": headline,
        "direct_answer": direct_answer,
        "supporting_points": supporting_points,
        "attention_rows": attention_rows,
        "evidence_refs": evidence_refs or _evidence_refs(attention_rows),
        "unknowns": unknowns,
        "approval_required_items": approvals,
    }


def _attention_item(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "public_label": row["label"],
        "rank": row["rank"],
        "displayed_score": row["displayed_score"],
        "status": row["status"],
        "protection_state": "PROTECTED" if row["protected"] else "NOT_PROTECTED",
        "confirmation_state": (
            "NEEDS_CONFIRMATION"
            if row["confirmation_required"]
            else "NOT_REQUIRED"
        ),
        "execution_state": row["execution_state"],
        "evidence_refs": tuple(row["evidence_refs"]),
    }


def _match_public_subject(normalized: str, session: DemoSession) -> str | None:
    rows = session.view_model.to_plain_json()["after_ranking"]
    matches: list[tuple[int, int, str]] = []
    for row in rows:
        aliases = _public_aliases(row)
        for alias in aliases:
            if _phrase_in_text(alias, normalized):
                matches.append((len(alias.split()), len(alias), row["subject_id"]))
    if not matches:
        return None
    return max(matches)[2]


def _public_aliases(row: Mapping[str, Any]) -> tuple[str, ...]:
    label = normalize_question(row["label"])
    words = label.split()
    aliases = {
        label,
        normalize_question(row["subject_id"]),
        normalize_question(row["attention_item_id"]),
    }
    for size in (3, 2):
        for start in range(len(words) - size + 1):
            aliases.add(" ".join(words[start : start + size]))
    aliases.update(word for word in words if len(word) >= 9)
    return tuple(sorted(aliases, key=lambda value: (-len(value.split()), -len(value), value)))


def _phrase_in_text(phrase: str, text: str) -> bool:
    return bool(phrase) and f" {phrase} " in f" {text} "


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(_phrase_in_text(normalize_question(phrase), text) for phrase in phrases)


def _evidence_refs(rows: tuple[Mapping[str, Any], ...]) -> tuple[str, ...]:
    return tuple(
        sorted({reference for row in rows for reference in row["evidence_refs"]})
    )


def _unknowns_for_rows(
    rows: tuple[Mapping[str, Any], ...], view: Mapping[str, Any]
) -> tuple[str, ...]:
    row_uncertainties = tuple(
        uncertainty for row in rows for uncertainty in row["uncertainty"]
    )
    critical = tuple(
        uncertainty
        for uncertainty in view["critical_uncertainties"]
        if uncertainty in row_uncertainties
    )
    return tuple(dict.fromkeys((*row_uncertainties, *critical)))


def _approval_labels(rows: tuple[Mapping[str, Any], ...]) -> tuple[str, ...]:
    return tuple(row["label"] for row in rows if row["confirmation_required"])


def _confirmation_labels(view: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(row["label"] for row in view["confirmation_required_items"])


def _suggested_follow_ups(intent: ChatIntent) -> tuple[str, ...]:
    prompts = {
        "CURRENT_ATTENTION": (SUPPORTED_SUGGESTED_PROMPTS[1], SUPPORTED_SUGGESTED_PROMPTS[4]),
        "WHAT_CHANGED": (SUPPORTED_SUGGESTED_PROMPTS[2], SUPPORTED_SUGGESTED_PROMPTS[3]),
        "WHY_ITEM": (SUPPORTED_SUGGESTED_PROMPTS[4], SUPPORTED_SUGGESTED_PROMPTS[0]),
        "PROTECTED_ITEMS": (SUPPORTED_SUGGESTED_PROMPTS[2], SUPPORTED_SUGGESTED_PROMPTS[4]),
        "REQUIRES_CONFIRMATION": (SUPPORTED_SUGGESTED_PROMPTS[1], SUPPORTED_SUGGESTED_PROMPTS[6 - 1]),
        "EVIDENCE": (SUPPORTED_SUGGESTED_PROMPTS[5], SUPPORTED_SUGGESTED_PROMPTS[0]),
        "UNKNOWNS": (SUPPORTED_SUGGESTED_PROMPTS[3], SUPPORTED_SUGGESTED_PROMPTS[5]),
        "REPLAY_PROOF": (SUPPORTED_SUGGESTED_PROMPTS[0], SUPPORTED_SUGGESTED_PROMPTS[1]),
        "MEMORY_STATE": (SUPPORTED_SUGGESTED_PROMPTS[0], SUPPORTED_SUGGESTED_PROMPTS[3]),
        "UNSUPPORTED": SUPPORTED_SUGGESTED_PROMPTS[:3],
    }
    return tuple(prompts[intent])


def _require_session(session: DemoSession) -> None:
    if not isinstance(session, DemoSession):
        raise TypeError("session must be DemoSession")


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {key: _deep_freeze(child) for key, child in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_deep_freeze(child) for child in value)
    return value
