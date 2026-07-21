"""Deterministic conversational adapter for the Memoria Viva demo."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


CHAT_RESPONSE_CONTRACT = "MV_CHAT_RESPONSE_V1"
SUGGESTED_PROMPTS = (
    "What changed after the trigger?",
    "What should I pay attention to?",
    "Why is CMT-04 still conditional?",
    "Show me what the system remembers.",
    "Replay this decision.",
)


@dataclass(frozen=True)
class ChatResponse:
    """Public-safe deterministic answer grounded in one replay view."""

    intent: str
    answer: str
    evidence_refs: tuple[str, ...]
    replay_digest: str
    source_count: int
    graph_change_count: int
    replay_verified: bool

    def to_plain_json(self) -> dict[str, Any]:
        return {
            "contract": CHAT_RESPONSE_CONTRACT,
            "intent": self.intent,
            "answer": self.answer,
            "evidence_refs": list(self.evidence_refs),
            "replay_digest": self.replay_digest,
            "source_count": self.source_count,
            "graph_change_count": self.graph_change_count,
            "replay_verified": self.replay_verified,
        }


def answer_question(question: str, view: Mapping[str, Any]) -> ChatResponse:
    """Answer from deterministic replay state without changing that state."""

    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string")
    if not isinstance(view, Mapping):
        raise TypeError("view must be a mapping")

    normalized = _normalize(question)
    if "cmt 04" in normalized or "conditional" in normalized:
        intent = "CONDITIONALITY"
        answer, refs = _conditionality_answer(view)
    elif _contains_any(normalized, ("replay", "digest", "verify", "reproducir", "verificar")):
        intent = "REPLAY"
        answer, refs = _replay_answer(view)
    elif _contains_any(
        normalized,
        ("what changed", "after the trigger", "trigger", "que cambio", "disparador"),
    ):
        intent = "CHANGE"
        answer, refs = _change_answer(view)
    elif _contains_any(
        normalized,
        (
            "attention",
            "pay attention",
            "focus",
            "priority",
            "prioridad",
            "enfocar",
            "atencion",
        ),
    ):
        intent = "ATTENTION"
        answer, refs = _attention_answer(view)
    elif _contains_any(
        normalized,
        ("remember", "memory", "memories", "recuerda", "memoria"),
    ):
        intent = "MEMORY"
        answer, refs = _memory_answer(view)
    else:
        intent = "SCOPE"
        answer, refs = _scope_answer(view)

    all_changes = sum(
        len(items) for items in view["graph_delta_by_category"].values()
    )
    replay_verified = all(
        status == "PASS" for status in view["oracle_statuses"].values()
    )
    unique_refs = tuple(dict.fromkeys(refs))
    return ChatResponse(
        intent=intent,
        answer=answer,
        evidence_refs=unique_refs,
        replay_digest=str(view["replay_digest"]),
        source_count=len(unique_refs),
        graph_change_count=all_changes,
        replay_verified=replay_verified,
    )


def _attention_answer(view: Mapping[str, Any]) -> tuple[str, tuple[str, ...]]:
    rows = tuple(view["after_ranking"][:3])
    lines = ["The deterministic ranking says your top three are:"]
    for row in rows:
        indicators = [row["band"]]
        if row["confirmation_required"]:
            indicators.append("confirmation required")
        lines.append(
            f"{row['rank']}. **{row['label']}** — score {row['displayed_score']} "
            f"· {' · '.join(indicators)}. {row['explanation']}"
        )
    lines.extend(
        (
            "",
            "**Next smallest action:** "
            + view["deterministic_brief"]["next_smallest_action"],
            "The language layer is explaining the ranking; it is not recalculating it.",
        )
    )
    return "\n\n".join(lines), _refs_from_rows(rows)


def _change_answer(view: Mapping[str, Any]) -> tuple[str, tuple[str, ...]]:
    event = view["event"]
    brief = view["deterministic_brief"]
    lines = [
        f"**Trigger:** {event['title']}",
        event["summary"],
        f"**Result:** {brief['headline']}",
    ]
    lines.extend(f"- {item}" for item in brief["what_changed"])
    lines.append(
        "No previous obligation was deleted; displaced and excluded records remain visible."
    )
    new_items = tuple(view["new_attention_items"])
    refs = (*event["evidence_refs"], *_refs_from_rows(new_items))
    return "\n\n".join(lines), tuple(refs)


def _conditionality_answer(view: Mapping[str, Any]) -> tuple[str, tuple[str, ...]]:
    item = next(
        (row for row in view["after_ranking"] if row["subject_id"] == "CMT-04"),
        None,
    )
    if item is None:
        return (
            "CMT-04 is not available in the current sanitized replay view.",
            (),
        )
    change = next(
        (
            row
            for row in view["graph_delta_by_category"]["DISPLACED"]
            if row["affected_id"] == "CMT-04"
            or "CMT-04" in str(row["affected_id"])
            or item["label"] in row["label"]
        ),
        None,
    )
    if change is None:
        return (
            "CMT-04 is not available in the current sanitized replay view.",
            (),
        )

    unknowns = " | ".join(item["uncertainty"] or change["uncertainty"])
    lines = [
        "**CMT-04 is conditional, not executed.**",
        f"- Current item: **{item['label']}**",
        f"- Mobility: `{item['mobility']}`",
        f"- Execution state: `{change['execution_state']}`",
        f"- Conditionality: `{change['conditionality']}`",
        f"- Condition: {change['condition']}",
        f"- Why: {change['explanation']}",
        f"- Approval boundary: {item['approval_requirement']}",
    ]
    if unknowns:
        lines.append(f"- Still unknown: {unknowns}")
    lines.append(
        "Memoria Viva preserves the uncertainty instead of silently converting it "
        "into an executed displacement."
    )
    refs = (*item["evidence_refs"], *change["evidence_refs"])
    return "\n".join(lines), tuple(refs)


def _memory_answer(view: Mapping[str, Any]) -> tuple[str, tuple[str, ...]]:
    metrics = view["headline_metrics"]
    protected = tuple(view["protected_items"])
    confirmation = tuple(view["confirmation_required_items"])
    uncertainties = tuple(view["critical_uncertainties"])
    event = view["event"]
    lines = [
        "The current replay remembers a bounded, sanitized decision state:",
        f"- One triggering event: **{event['title']}**.",
        f"- {metrics['attention_items_before']} ranked items before and "
        f"{metrics['attention_items_after']} after.",
        "- Protected work: "
        + ", ".join(row["label"] for row in protected),
        "- Confirmation required: "
        + ", ".join(row["label"] for row in confirmation),
        f"- {len(uncertainties)} explicit unknowns remain unresolved.",
        "It does not remember raw private messages, real provider IDs, or unapproved "
        "external source material in this MVP.",
    ]
    refs = (
        *event["evidence_refs"],
        *_refs_from_rows(protected),
        *_refs_from_rows(confirmation),
    )
    return "\n".join(lines), tuple(refs)


def _replay_answer(view: Mapping[str, Any]) -> tuple[str, tuple[str, ...]]:
    proof = view["technical_proof"]
    statuses = view["oracle_statuses"]
    status_lines = "\n".join(
        f"- {name.replace('_', ' ').title()}: `{status}`"
        for name, status in statuses.items()
    )
    answer = (
        "**Replay verified.** The committed fixture was reconstructed through "
        "Snapshot T0 → trigger → Snapshot T1 → ranking → GraphDelta.\n\n"
        f"{status_lines}\n\n"
        f"**Replay digest:** `{view['replay_digest']}`\n\n"
        f"{proof['determinism_statement']}"
    )
    refs = tuple(
        ref
        for row in view["after_ranking"]
        for ref in row["evidence_refs"]
    )
    return answer, refs


def _scope_answer(view: Mapping[str, Any]) -> tuple[str, tuple[str, ...]]:
    top = view["after_ranking"][0]
    prompts = "\n".join(f"- {prompt}" for prompt in SUGGESTED_PROMPTS)
    answer = (
        "I can answer from the current sanitized deterministic replay, but I will "
        "not invent state that is outside it.\n\n"
        f"The current top-ranked item is **{top['label']}** at score "
        f"{top['displayed_score']}.\n\n"
        "Try one of these questions:\n" + prompts
    )
    return answer, tuple(top["evidence_refs"])


def _refs_from_rows(rows: Iterable[Mapping[str, Any]]) -> tuple[str, ...]:
    return tuple(
        ref
        for row in rows
        for ref in row.get("evidence_refs", ())
    )


def _normalize(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value.casefold())
    ascii_text = "".join(char for char in folded if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", ascii_text).strip()


def _contains_any(value: str, candidates: tuple[str, ...]) -> bool:
    return any(candidate in value for candidate in candidates)
