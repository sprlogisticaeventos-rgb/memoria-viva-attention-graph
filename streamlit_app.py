"""Chat-first judge demo for the deterministic Memoria Viva replay."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

import streamlit as st

from memoria_viva.canonical import canonical_json_bytes
from memoria_viva.chat import SUGGESTED_PROMPTS, answer_question
from memoria_viva.explainer import (
    DEFAULT_OPENAI_MODEL,
    create_openai_client,
    safe_generate_decision_brief,
)
from memoria_viva.presentation import DemoSession, repository_root, run_canonical_demo


st.set_page_config(
    page_title="Memoria Viva — Attention Graph",
    layout="wide",
)


def main() -> None:
    _styles()
    _ensure_demo_session()
    session: DemoSession = st.session_state.demo_session
    view = session.view_model.to_plain_json()

    st.title("Memoria Viva")
    st.markdown("## What deserves your attention now?")
    st.caption(
        "Ask the current deterministic memory state. The conversation can explain "
        "rankings, conditions, evidence, and replay receipts, but it cannot change them."
    )
    _render_system_status(view)
    _render_chat()

    st.divider()
    with st.expander("Inspect deterministic system", expanded=False):
        _render_inspector(st.session_state.demo_session)

    session = st.session_state.demo_session
    st.download_button(
        "Download sanitized replay summary",
        data=canonical_json_bytes(session.view_model.download_projection()),
        file_name="memoria-viva-sanitized-replay-summary.json",
        mime="application/json",
        use_container_width=True,
    )
    st.caption(
        "This branch changes the conversational presentation layer only. The "
        "deterministic engine and surface-specific publication gates remain authoritative."
    )


def _ensure_demo_session() -> None:
    if "demo_session" not in st.session_state:
        st.session_state.demo_session = run_canonical_demo(repository_root())
    st.session_state.setdefault("chat_messages", [])


def _render_system_status(view: Mapping[str, Any]) -> None:
    graph_change_count = sum(
        len(items) for items in view["graph_delta_by_category"].values()
    )
    verified = all(status == "PASS" for status in view["oracle_statuses"].values())
    verification_label = "Replay verified" if verified else "Replay requires review"
    st.caption(
        f"{view['headline_metrics']['attention_items_after']} attention items · "
        f"{graph_change_count} graph changes · {verification_label}"
    )


def _render_chat() -> None:
    history: list[dict[str, Any]] = st.session_state.chat_messages
    if not history:
        st.info(
            "The system is ready. Start with a suggested question or ask in your own words."
        )

    for index, message in enumerate(history):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                verified = (
                    "Replay verified"
                    if message["replay_verified"]
                    else "Replay requires review"
                )
                st.caption(
                    f"Based on: {message['source_count']} evidence refs · "
                    f"{message['graph_change_count']} graph changes · {verified}"
                )
                with st.expander(f"Inspect answer evidence · turn {index + 1}"):
                    if message["evidence_refs"]:
                        st.code("\n".join(message["evidence_refs"]), language=None)
                    else:
                        st.write("No evidence reference was required for this response.")
                    st.caption(f"Replay digest: {message['replay_digest']}")

    st.markdown("**Suggested**")
    suggestion_columns = st.columns(3)
    selected_prompt: str | None = None
    for index, prompt in enumerate(SUGGESTED_PROMPTS):
        if suggestion_columns[index % 3].button(
            prompt,
            key=f"suggested-prompt-{index}",
            use_container_width=True,
        ):
            selected_prompt = prompt

    typed_prompt = st.chat_input("Ask anything about the current memory state...")
    prompt = typed_prompt or selected_prompt
    if prompt:
        _submit_chat_prompt(prompt)


def _submit_chat_prompt(prompt: str) -> None:
    if "replay" in prompt.casefold() or "reproducir" in prompt.casefold():
        st.session_state.demo_session = run_canonical_demo(repository_root())

    session: DemoSession = st.session_state.demo_session
    response = answer_question(prompt, session.view_model.to_plain_json()).to_plain_json()
    st.session_state.chat_messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )
    st.session_state.chat_messages.append(
        {
            "role": "assistant",
            "content": response["answer"],
            "intent": response["intent"],
            "evidence_refs": response["evidence_refs"],
            "replay_digest": response["replay_digest"],
            "source_count": response["source_count"],
            "graph_change_count": response["graph_change_count"],
            "replay_verified": response["replay_verified"],
        }
    )
    st.rerun()


def _render_inspector(session: DemoSession) -> None:
    view = session.view_model.to_plain_json()
    if st.button(
        "Run deterministic replay",
        type="primary",
        use_container_width=True,
        key="inspector-replay",
    ):
        st.session_state.demo_session = run_canonical_demo(repository_root())
        st.rerun()

    metrics = view["headline_metrics"]
    columns = st.columns(4)
    columns[0].metric("Attention items before", metrics["attention_items_before"])
    columns[1].metric("Attention items after", metrics["attention_items_after"])
    columns[2].metric(
        "New protected commitments", metrics["new_protected_commitments"]
    )
    columns[3].metric("Oracle checks passed", f"{metrics['oracle_checks_passed']}/3")

    shift, why, evidence, proof = st.tabs(
        [
            "THE SHIFT",
            "WHY IT CHANGED",
            "EVIDENCE & UNCERTAINTY",
            "TECHNICAL PROOF",
        ]
    )
    with shift:
        _render_shift(view)
    with why:
        _render_why(view, session)
    with evidence:
        _render_evidence(view)
    with proof:
        _render_proof(view)


def _render_shift(view: Mapping[str, Any]) -> None:
    st.markdown("## Before → new external event → after")
    before_column, event_column, after_column = st.columns([1, 0.9, 1])
    with before_column:
        st.markdown("### Before")
        _ranking(view["before_ranking"])
    with event_column:
        event = view["event"]
        st.markdown("### New event")
        st.info(f"**{event['title']}**\n\n{event['summary']}")
        st.markdown(f"**Goal affected:** {event['goal_affected']}")
        st.markdown(f"**Authority:** `{event['authority_limitation']}`")
        st.markdown(f"**Deadline:** {event['deadline_label']}")
        st.warning(event["authority_statement"])
    with after_column:
        st.markdown("### After")
        _ranking(view["after_ranking"], movements=view["rank_movements"])

    st.success(
        "Public product demonstration ready enters rank 1; Submission package "
        "finalization enters rank 2; protected continuity remains rank 3."
    )
    st.caption("No previous obligation disappears; excluded records remain retained.")


def _render_why(view: Mapping[str, Any], session: DemoSession) -> None:
    brief = view["deterministic_brief"]
    st.markdown(f"## {brief['label']}")
    st.markdown(f"**{brief['headline']}**")
    for line in brief["what_changed"]:
        st.markdown(f"- {line}")
    st.markdown(
        f"**RECOMMENDATION — Next smallest action:** "
        f"{brief['next_smallest_action']}"
    )
    st.caption(brief["auditability"])

    st.markdown("## Why attention changed")
    for category in (
        "ADDED",
        "UPDATED",
        "CONFLICTED",
        "DISPLACED",
        "PROTECTED",
        "REQUIRES_CONFIRMATION",
        "UNCHANGED",
    ):
        changes = view["graph_delta_by_category"][category]
        with st.expander(f"{category} · {len(changes)}"):
            for change in changes:
                st.markdown(f"**{change['label']}** · `{change['statement_kind']}`")
                st.write(change["explanation"])
                if change["condition"]:
                    st.warning(f"Condition: {change['condition']}")
                st.caption(
                    f"Execution: {change['execution_state']} · "
                    f"Conditionality: {change['conditionality']} · "
                    f"Evidence: {', '.join(change['evidence_refs'])}"
                )
                if change["uncertainty"]:
                    st.caption("Uncertainty: " + " | ".join(change["uncertainty"]))
                st.divider()

    st.warning(
        "Pending bounded validation is conditionally displaceable; movement is "
        "not executed. Shared release-readiness requires joint confirmation. "
        "Coexistence alone is not treated as conflict."
    )
    st.markdown("## Optional GPT-5.6 explanation")
    st.caption(
        "GPT-5.6 explains the completed deterministic replay. It cannot change "
        "state, scores, rankings, GraphDelta, or claims."
    )
    digest = view["replay_digest"]
    cache = st.session_state.setdefault("gpt_decision_briefs", {})
    if st.button("Generate GPT-5.6 Decision Brief", key="gpt-decision-brief"):
        if digest not in cache:
            api_key, model = _resolve_openai_config()
            client = create_openai_client(api_key) if api_key else None
            cache[digest] = safe_generate_decision_brief(
                session.view_model,
                client,
                model=model,
                root=repository_root(),
            ).to_plain_json()
    result = cache.get(digest)
    if result:
        if result["status"] == "SUCCESS":
            _render_gpt_brief(result["brief"])
        else:
            st.warning(result["diagnostic"])


def _render_evidence(view: Mapping[str, Any]) -> None:
    st.markdown("## Facts and evidence")
    for item in view["evidence"]:
        with st.expander(f"{item['evidence_id']} · {item['category']}"):
            st.markdown(f"**FACT:** {item['summary']}")
            st.caption(
                f"Epistemic state: {item['epistemic_state']} · "
                f"Confidence: {item['confidence']:.2f} · Authority: {item['authority']}"
            )
            if item["uncertainty"]:
                st.caption("Uncertainty: " + " | ".join(item["uncertainty"]))

    st.markdown("## Unknowns and approvals")
    for uncertainty in view["critical_uncertainties"]:
        st.markdown(f"- **UNKNOWN:** {uncertainty}")
    for item in view["confirmation_required_items"]:
        st.markdown(
            f"- **APPROVAL REQUIRED:** {item['label']} — "
            f"{item['approval_requirement']}"
        )

    st.markdown("## Privacy and publication")
    privacy = view["privacy"]
    st.write(
        f"Residual aggregation risk: **{privacy['residual_aggregation_risk']}**"
    )
    for surface in privacy["publication_surfaces"]:
        st.markdown(f"- `{surface['surface']}` — **{surface['status']}**")
    st.warning(privacy["statement"])
    st.markdown("## Warnings")
    for warning in view["warnings"]:
        st.markdown(f"- `{warning['code']}` — {warning['message']}")


def _render_proof(view: Mapping[str, Any]) -> None:
    proof = view["technical_proof"]
    st.markdown("## Deterministic technical proof")
    st.write(f"Execution mode: **{proof['execution_mode']}**")
    st.write(f"Validated test count: **{proof['validated_test_count']}**")
    st.write("Model metadata for deterministic engine: **null**")
    st.success(proof["determinism_statement"])
    for name in (
        "snapshot_t0",
        "ranking_before",
        "snapshot_t1",
        "ranking_after",
        "graph_delta",
        "run_record",
    ):
        artifact = proof[name]
        st.markdown(f"**{name}:** `{artifact['id']}`")
        st.caption(artifact["digest"])
    st.markdown(f"**ReplayResult:** `{proof['replay_digest']}`")
    st.json(
        {
            "base_policy": proof["base_policy"],
            "feature_policy": proof["feature_policy"],
            "oracle_statuses": proof["oracle_statuses"],
        }
    )
    st.caption(
        "Technical IDs are secondary proof. The judge-facing story remains the "
        "before/event/after attention shift."
    )


def _ranking(
    rows: list[Mapping[str, Any]],
    *,
    movements: list[Mapping[str, Any]] | None = None,
) -> None:
    movement_index = {
        item["subject_id"]: item for item in movements or []
    }
    for row in rows:
        indicators = []
        if row["protected"]:
            indicators.append("PROTECTED")
        if row["confirmation_required"]:
            indicators.append("CONFIRM")
        movement = movement_index.get(row["subject_id"])
        if movement and movement["direction"] != "UNCHANGED":
            indicators.append(movement["direction"])
        suffix = " · ".join(indicators) if indicators else row["band"]
        st.markdown(
            f"**{row['rank']}. {row['label']}**  \n"
            f"Score {row['displayed_score']} · {suffix}"
        )


def _render_gpt_brief(brief: Mapping[str, Any]) -> None:
    st.success("GPT-5.6 Decision Brief")
    st.markdown(f"### {brief['headline']}")
    st.write(brief["executive_summary"])
    sections = (
        ("What changed", "what_changed"),
        ("What to protect", "what_to_protect"),
        ("What to review or move", "what_to_review_or_move"),
        ("What requires confirmation", "what_requires_confirmation"),
        ("Uncertainties", "uncertainties"),
    )
    for title, key in sections:
        st.markdown(f"**{title}**")
        for item in brief[key]:
            st.markdown(f"- {item}")
    st.markdown(f"**Next smallest action:** {brief['next_smallest_action']}")
    st.caption(brief["deterministic_authority_statement"])


def _resolve_openai_config() -> tuple[str | None, str]:
    """Resolve server-side credentials only after the explicit GPT button click."""

    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL")
    if not api_key or not model:
        try:
            secrets = st.secrets
            if not api_key:
                api_key = secrets.get("OPENAI_API_KEY")
            if not model:
                model = secrets.get("OPENAI_MODEL")
        except Exception:
            pass
    if not api_key:
        try:
            from dotenv import load_dotenv

            load_dotenv(repository_root() / ".env.local", override=False)
            api_key = os.environ.get("OPENAI_API_KEY")
            model = model or os.environ.get("OPENAI_MODEL")
        except Exception:
            api_key = None
    return api_key, model or DEFAULT_OPENAI_MODEL


def _styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width: 1080px; padding-top: 2rem;}
        [data-testid="stMetric"] {border: 1px solid #d9dee7; border-radius: 10px; padding: 12px;}
        [data-testid="stExpander"] {border-color: #d9dee7;}
        [data-testid="stChatMessage"] {border: 1px solid #e6e9ef; border-radius: 14px; padding: 0.35rem 0.7rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
