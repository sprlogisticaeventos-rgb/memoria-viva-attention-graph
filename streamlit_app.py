"""One-page judge demo for the deterministic Memoria Viva replay."""

from __future__ import annotations

from html import escape
import os
from pathlib import Path
from typing import Any, Mapping

import streamlit as st

from memoria_viva.canonical import canonical_json_bytes
from memoria_viva.chat import (
    GUIDED_QUESTION_OPTIONS,
    ChatAnswer,
    answer_question,
)
from memoria_viva.chat_explainer import (
    CHAT_RESPONSE_VERSION,
    GPT_RECOMMENDATION_QUESTIONS,
    safe_generate_chat_rewrite,
)
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
    if "demo_session" not in st.session_state:
        st.session_state.demo_session = run_canonical_demo(repository_root())
    session: DemoSession = st.session_state.demo_session
    view = session.view_model.to_plain_json()
    inspect_requested = _render_primary_composition(session, view)
    if inspect_requested:
        _render_inspector(session, view)


def _render_primary_composition(
    session: DemoSession, view: Mapping[str, Any]
) -> bool:
    if "gpt_chat_rewrites" not in st.session_state:
        st.session_state.gpt_chat_rewrites = {}
    goal_context = _public_goal_context(session, view)
    inspect_requested = False
    with st.container(key="primary-composition"):
        context_rail, decision_workspace = st.columns([4.2, 5.8], gap="large")
        with decision_workspace:
            st.markdown(
                '<div class="mv-product-headline">'
                '<div class="mv-brand">Memoria Viva</div>'
                '<h1>What should happen next?</h1>'
                '<p>Choose a verified question. The answer comes from a '
                'reproducible attention state.</p></div>',
                unsafe_allow_html=True,
            )
            selected_question = st.selectbox(
                "Verified question",
                GUIDED_QUESTION_OPTIONS,
                index=len(GUIDED_QUESTION_OPTIONS) - 1,
                key="guided-question",
            )
            answer = answer_question(selected_question, session)
            _render_guided_answer(
                answer,
                allow_gpt=selected_question in GPT_RECOMMENDATION_QUESTIONS,
            )
            inspect_requested = st.toggle(
                "Inspect deterministic system",
                value=False,
                key="inspect-deterministic-system",
            )

        with context_rail:
            _render_current_goal_context(goal_context)
            _render_verified_grounding(answer, view)
            st.markdown('<div class="mv-rail-heading">Compact attention map</div>', unsafe_allow_html=True)
            st.graphviz_chart(
                _attention_graph_dot(view, goal_context["affected_goal"]),
                width="stretch",
            )
            st.caption(
                "Conditional authorization exists. No movement was executed. "
                "Execution remains UNKNOWN."
            )
    return inspect_requested


def _render_inspector(session: DemoSession, view: Mapping[str, Any]) -> None:
    """Render the complete technical surface below the primary composition."""

    st.divider()
    st.markdown("## Inspect deterministic system")
    if st.button(
        "Run deterministic replay",
        type="primary",
        use_container_width=True,
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
    columns[3].metric(
        "Oracle checks passed", f"{metrics['oracle_checks_passed']}/3"
    )

    shift, why, evidence, proof = st.tabs(
        [
            "The shift",
            "Why it changed",
            "Evidence & uncertainty",
            "Technical proof",
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

    st.download_button(
        "Download sanitized replay summary",
        data=canonical_json_bytes(session.view_model.download_projection()),
        file_name="memoria-viva-sanitized-replay-summary.json",
        mime="application/json",
        use_container_width=True,
    )
    st.caption(
        "This generated view preserves the committed sanitized replay and its "
        "surface-specific publication boundaries."
    )
def _render_guided_answer(answer: ChatAnswer, *, allow_gpt: bool) -> None:
    st.markdown('<div class="mv-workspace-label">Verified answer</div>', unsafe_allow_html=True)
    st.markdown(f"## {answer.headline}")
    st.markdown(
        f'<div class="mv-direct-answer">{escape(answer.direct_answer)}</div>',
        unsafe_allow_html=True,
    )

    if answer.attention_items:
        st.markdown("### Verified basis")
        for item in answer.attention_items:
            st.markdown(
                (
                    '<div class="mv-basis-row">'
                    f'<span class="mv-rank">{item["rank"]}</span>'
                    f'<strong>{escape(str(item["public_label"]))}</strong>'
                    f'<span class="mv-score">{escape(str(item["displayed_score"]))}</span>'
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
        st.caption(
            "Ranks are the verified attention order. Scores are supporting "
            "signals; protection and dependency rules can determine final order."
        )

    if answer.approval_required_items:
        st.warning(
            "Human approval required: "
            + ", ".join(answer.approval_required_items)
            + "."
        )
    elif answer.matched_subject_id == "CMT-04":
        st.warning(
            "Conditional displacement is authorized. Execution remains UNKNOWN; "
            "no movement was executed."
        )
    elif answer.unknowns:
        st.info(
            f"{len(answer.unknowns)} verified uncertainties remain. Details are "
            "preserved in the grounding receipt."
        )

    st.markdown("### Next smallest action")
    st.markdown(
        f'<div class="mv-next-action">{escape(_next_smallest_action(answer))}</div>',
        unsafe_allow_html=True,
    )

    if allow_gpt:
        st.caption("GPT recommends. The deterministic engine decides.")
        cache = st.session_state.gpt_chat_rewrites
        rewrite = _cached_successful_chat_rewrite(answer, cache)
        if st.button(
            "Recommend the next move with GPT-5.6",
            key=f"gpt-chat-{answer.answer_id}",
        ):
            rewrite = _request_chat_rewrite(answer, cache)
        if rewrite:
            _render_chat_rewrite(rewrite)


def _render_chat_rewrite(rewrite: Mapping[str, Any]) -> None:
    """Render a successful recommendation or one compact fallback message."""

    if rewrite["status"] == "SUCCESS":
        st.markdown("### Recommended next move — GPT-5.6")
        st.markdown("#### What this means")
        st.write(rewrite["response"]["what_this_means"])
        st.markdown("#### Recommended next move")
        st.write(rewrite["response"]["recommended_next_move"])
        st.markdown("#### Approval or uncertainty")
        st.write(rewrite["response"]["approval_or_uncertainty_note"])
        return
    st.markdown(
        '<div class="mv-gpt-unavailable">'
        '<strong>GPT recommendation unavailable.</strong><br>'
        'The verified recommendation above remains complete.</div>',
        unsafe_allow_html=True,
    )


def _chat_rewrite_cache_key(
    answer: ChatAnswer,
    model: str,
    *,
    contract_version: str = CHAT_RESPONSE_VERSION,
) -> tuple[str, str, str, str]:
    """Identify one successful rewrite without coupling questions or contracts."""

    return (
        answer.replay_digest,
        answer.answer_id,
        model,
        contract_version,
    )


def _cached_successful_chat_rewrite(
    answer: ChatAnswer,
    cache: Mapping[Any, Any],
    *,
    contract_version: str = CHAT_RESPONSE_VERSION,
) -> dict[str, Any] | None:
    """Return a current-contract success; legacy and fallback entries are ignored."""

    for key, value in cache.items():
        if not isinstance(key, tuple) or len(key) != 4:
            continue
        replay_digest, answer_id, _model, version = key
        if (
            replay_digest == answer.replay_digest
            and answer_id == answer.answer_id
            and version == contract_version
            and isinstance(value, Mapping)
            and value.get("status") == "SUCCESS"
        ):
            return dict(value)
    return None


def _request_chat_rewrite(
    answer: ChatAnswer,
    cache: dict[Any, Any],
    *,
    contract_version: str = CHAT_RESPONSE_VERSION,
    config_resolver: Any = None,
    client_factory: Any = None,
    generator: Any = None,
) -> dict[str, Any]:
    """Reuse successes and leave failures transient so the request can be retried."""

    resolve_config = config_resolver or _resolve_openai_config
    make_client = client_factory or create_openai_client
    generate = generator or safe_generate_chat_rewrite
    api_key, model = resolve_config()
    cache_key = _chat_rewrite_cache_key(
        answer, model, contract_version=contract_version
    )
    cached = cache.get(cache_key)
    if isinstance(cached, Mapping) and cached.get("status") == "SUCCESS":
        return dict(cached)
    client = make_client(api_key) if api_key else None
    result = generate(
        answer,
        client,
        model=model,
        root=repository_root(),
    ).to_plain_json()
    if result["status"] == "SUCCESS":
        cache[cache_key] = result
    return result


def _next_smallest_action(answer: ChatAnswer) -> str:
    """Select a bounded action from the deterministic answer semantics."""

    normalized = answer.question.casefold()
    if normalized in {"what matters now?", "what should happen next?"}:
        return (
            "Freeze the minimum verifiable demonstration scope and verify the "
            "public demo. Then complete the dependent submission package. Review "
            "conditional displacement separately and obtain required human "
            "confirmation before any approval-bound action."
        )
    if answer.intent == "WHAT_CHANGED":
        return (
            "Use the new verified order while preserving the conditional and "
            "confirmation boundaries before any movement."
        )
    if answer.intent == "REQUIRES_CONFIRMATION":
        return (
            "Obtain the required human authority for both confirmation items "
            "before changing either item."
        )
    if answer.matched_subject_id == "CMT-04":
        return (
            "Review the displacement condition, opportunity cost, repair, and "
            "reactivation terms without treating authorization as execution."
        )
    if answer.intent == "EVIDENCE":
        return (
            "Review the cited public-safe evidence and unresolved uncertainty "
            "before acting on the verified order."
        )
    return (
        "Use the verified order without changing it, and resolve any displayed "
        "uncertainty or required approval before action."
    )


def _public_goal_context(
    session: DemoSession, view: Mapping[str, Any]
) -> dict[str, Any]:
    """Project public Goal state without extending the DemoViewModel contract."""

    affected_goal_id = str(view["event"]["goal_affected"]).split(" — ", 1)[0]
    goals = []
    for goal in session.replay.snapshot_t1.goals:
        completion_state = goal["completion_authority"][
            "completion_validation_state"
        ]
        verification_states = {
            surface["status"] for surface in goal["verification_surfaces"]
        }
        goals.append(
            {
                "goal_id": goal["goal_id"],
                "public_title": str(goal["public_title"])
                .replace("_", " ")
                .lower()
                .capitalize(),
                "lifecycle": str(goal["operational_lifecycle"]).title(),
                "completion_state": (
                    "Complete" if completion_state == "VERIFIED" else "Incomplete"
                ),
                "official_requirements_state": (
                    "Verified"
                    if verification_states == {"VERIFIED"}
                    else "Official requirements unverified"
                ),
                "is_affected": goal["goal_id"] == affected_goal_id,
            }
        )
    affected = next((goal for goal in goals if goal["is_affected"]), None)
    if affected is None:
        raise ValueError("event-affected Goal is not present in Snapshot T1")
    return {"goals": tuple(goals), "affected_goal": affected}


def _render_current_goal_context(goal_context: Mapping[str, Any]) -> None:
    affected = goal_context["affected_goal"]
    chips = "".join(
        '<span class="mv-goal-chip">'
        + escape(str(goal["public_title"]))
        + "</span>"
        for goal in goal_context["goals"]
        if not goal["is_affected"]
    )
    st.markdown(
        (
            '<section class="mv-goal-context">'
            '<div class="mv-eyebrow">Current goal</div>'
            f'<div class="mv-goal-title">{escape(affected["public_title"])}</div>'
            '<div class="mv-goal-primary-state">'
            f'{escape(affected["lifecycle"])} · '
            f'{escape(affected["completion_state"])}</div>'
            f'<div class="mv-goal-verification">'
            f'{escape(affected["official_requirements_state"])}</div>'
            '<p>This event changes attention inside this goal.<br>'
            'It does not prove goal completion.</p></section>'
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        (
            '<section class="mv-other-goals">'
            '<div class="mv-goal-secondary-label">Other public goals</div>'
            f'<div class="mv-goal-chips">{chips}</div></section>'
        ),
        unsafe_allow_html=True,
    )


def _render_verified_grounding(
    answer: ChatAnswer, view: Mapping[str, Any]
) -> None:
    summary = _grounding_summary(answer, view)
    optional_metrics = ""
    if summary["confirmation_required_count"]:
        optional_metrics += (
            '<div><strong>'
            f'{summary["confirmation_required_count"]}'
            '</strong><span>Confirmation required</span></div>'
        )
    if summary["conditional_displacement_count"]:
        optional_metrics += (
            '<div><strong>'
            f'{summary["conditional_displacement_count"]}'
            '</strong><span>Conditional displacement</span></div>'
        )
    st.markdown(
        (
            '<section class="mv-grounding-card">'
            '<div class="mv-eyebrow">Verified grounding</div>'
            '<div class="mv-grounding-grid">'
            f'<div><strong>{summary["attention_item_count"]}</strong>'
            '<span>Relevant attention items</span></div>'
            f'<div><strong>{summary["evidence_reference_count"]}</strong>'
            '<span>Evidence references</span></div>'
            f'<div><strong>{summary["oracle_pass_count"]} / 3</strong>'
            '<span>Oracle checks passed</span></div>'
            '<div><strong>PASS</strong><span>Replay verified</span></div>'
            f'{optional_metrics}</div></section>'
        ),
        unsafe_allow_html=True,
    )
    with st.expander("Evidence references and receipt"):
        if answer.evidence_refs:
            for reference in answer.evidence_refs:
                st.markdown(f"- `{reference}`")
        else:
            st.caption("No item-level evidence reference is needed for this answer.")
        st.caption(
            f"Intent {answer.intent} · Answer {answer.answer_id} · "
            f"Replay {answer.replay_digest}"
        )
        st.json(dict(answer.oracle_statuses))


def _grounding_summary(
    answer: ChatAnswer, view: Mapping[str, Any]
) -> dict[str, int]:
    conditional_relevant = (
        answer.intent in {"CURRENT_ATTENTION", "WHAT_CHANGED", "MEMORY_STATE"}
        or answer.matched_subject_id == "CMT-04"
    )
    return {
        "attention_item_count": len(answer.attention_items),
        "evidence_reference_count": len(answer.evidence_refs),
        "oracle_pass_count": sum(
            status == "PASS" for status in answer.oracle_statuses.values()
        ),
        "confirmation_required_count": len(answer.approval_required_items),
        "conditional_displacement_count": (
            len(view["conditional_displacements"]) if conditional_relevant else 0
        ),
    }


def _attention_graph_dot(
    view: Mapping[str, Any], affected_goal: Mapping[str, Any]
) -> str:
    """Return one deterministic public-safe principal-story DOT projection."""

    rows = {row["subject_id"]: row for row in view["after_ranking"]}
    labels = {
        "goal": affected_goal["public_title"],
        "cmt01": rows["CMT-01"]["label"],
        "cmt02": rows["CMT-02"]["label"],
        "doc": rows["CMT-T0-10"]["label"],
        "cmt04": rows["CMT-04"]["label"],
    }
    escaped = {key: _dot_escape(value) for key, value in labels.items()}
    confirmation_count = len(view["confirmation_required_items"])
    return f'''digraph MemoriaViva {{
  graph [rankdir=TB, bgcolor="transparent", pad="0.02", nodesep="0.10", ranksep="0.22", splines=polyline];
  node [shape=box, style="rounded,filled", fontname="Arial", fontsize=9.5, margin="0.10,0.07", color="#CBD5E0", fillcolor="#FFFFFF", fontcolor="#1A202C", width=2.65];
  edge [fontname="Arial", fontsize=8, color="#718096", fontcolor="#4A5568", arrowsize=0.55];

  goal [label="{escaped['goal'].upper()}\\nACTIVE · INCOMPLETE", color="#6B46C1", fillcolor="#FAF5FF"];
  event [label="NEW BUILD WEEK EVENT", color="#3182CE", fillcolor="#EBF8FF"];
  cmt01 [label="#1 {escaped['cmt01'].upper()}\\nPROTECTED · PLANNED", color="#2F855A", fillcolor="#F0FFF4"];
  cmt02 [label="#2 {escaped['cmt02'].upper()}\\nDEPENDS ON #1", color="#2F855A", fillcolor="#F0FFF4"];
  doc [label="#3 {escaped['doc'].upper()}\\nREMAINS PROTECTED", color="#2F855A", fillcolor="#F0FFF4"];
  cmt04 [label="{escaped['cmt04'].upper()}\\nCONDITIONAL TARGET\\nAUTHORIZATION EXISTS\\nNO MOVEMENT EXECUTED\\nEXECUTION REMAINS UNKNOWN", color="#C05621", fillcolor="#FFFAF0"];
  confirm_lane [label="HUMAN CONFIRMATION REQUIRED\\n{confirmation_count} ITEMS · APPROVAL BEFORE ACTION", color="#D69E2E", fillcolor="#FFFFF0"];

  goal -> event [label="attention changes"];
  event -> cmt01 [label="creates"];
  cmt01 -> cmt02 [label="prerequisite for", color="#2F855A"];
  cmt01 -> cmt04 [label="conditional target", style=dashed, color="#C05621", fontcolor="#9C4221"];
  event -> doc [label="rank 3 protected", style=dotted, color="#2F855A"];
  event -> confirm_lane [label="{confirmation_count} items", color="#D69E2E"];
}}'''


def _dot_escape(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


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
    if st.button("Generate GPT-5.6 Decision Brief"):
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
        .block-container {max-width: 1360px; padding-top: 2.3rem; padding-bottom: 5rem;}
        h1 {letter-spacing: -0.035em;}
        h2 {letter-spacing: -0.02em; margin-top: 0.7rem;}
        .st-key-primary-composition [data-testid="stHorizontalBlock"] {align-items: flex-start;}
        .mv-product-headline {margin: 0 0 1.35rem 0; max-width: 760px;}
        .mv-product-headline h1 {font-size: clamp(2.15rem, 4vw, 3.45rem); line-height: 1.03; margin: 0.28rem 0 0.75rem 0;}
        .mv-product-headline p {font-size: 1.08rem; color: #4A5568; line-height: 1.55; margin: 0;}
        .mv-brand {font-size: 0.83rem; font-weight: 800; letter-spacing: 0.10em; text-transform: uppercase; color: #1F5FA9;}
        .mv-workspace-label, .mv-rail-heading {font-size: 0.76rem; font-weight: 780; letter-spacing: 0.08em; text-transform: uppercase; color: #4A5568; margin-top: 1.15rem;}
        .mv-goal-context {border: 1px solid #D6BCFA; background: #FAF5FF; border-radius: 16px; padding: 1.15rem 1.2rem; margin: 0 0 0.55rem 0; height: auto; overflow: visible; white-space: normal;}
        .mv-eyebrow {font-size: 0.76rem; font-weight: 760; letter-spacing: 0.08em; text-transform: uppercase; color: #6B46C1;}
        .mv-goal-title {font-size: 1.42rem; font-weight: 780; margin: 0.28rem 0 0.18rem 0;}
        .mv-goal-primary-state {font-size: 0.92rem; font-weight: 700; color: #553C9A;}
        .mv-goal-verification {font-size: 0.88rem; margin-top: 0.72rem; color: #4A5568;}
        .mv-goal-context p {font-size: 0.92rem; line-height: 1.48; margin: 0.9rem 0 0.85rem 0;}
        .mv-other-goals {margin: 0 0 1rem 0; padding: 0 0.15rem; height: auto; overflow: visible;}
        .mv-goal-secondary-label {font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #718096;}
        .mv-goal-chips {display: flex; flex-wrap: wrap; gap: 0.36rem; margin-top: 0.38rem;}
        .mv-goal-chip {font-size: 0.75rem; padding: 0.18rem 0.45rem; border-radius: 999px; border: 1px solid #CBD5E0; color: #4A5568; background: #FFFFFF;}
        .mv-grounding-card {border: 1px solid #CBD5E0; border-radius: 16px; padding: 1.05rem 1.1rem; margin: 0 0 0.75rem 0; background: #FFFFFF;}
        .mv-grounding-grid {display: grid; grid-template-columns: 1fr 1fr; gap: 0.68rem; margin-top: 0.72rem;}
        .mv-grounding-grid > div {border-top: 1px solid #E2E8F0; padding-top: 0.55rem;}
        .mv-grounding-grid strong {display: block; font-size: 1.12rem; color: #1F5FA9;}
        .mv-grounding-grid span {display: block; font-size: 0.74rem; line-height: 1.25; color: #4A5568;}
        .mv-direct-answer {font-size: 1.18rem; line-height: 1.66; margin: 0.55rem 0 1.5rem 0; max-width: 760px;}
        .mv-basis-row {display: grid; grid-template-columns: 2rem 1fr auto; gap: 0.7rem; align-items: center; border-bottom: 1px solid #E2E8F0; padding: 0.72rem 0;}
        .mv-rank {font-size: 1.35rem; font-weight: 760; color: #1F5FA9;}
        .mv-score {font-variant-numeric: tabular-nums; color: #4A5568; font-size: 0.92rem;}
        .mv-next-action {border-left: 4px solid #3182CE; background: #EBF8FF; border-radius: 0 12px 12px 0; padding: 0.95rem 1rem; font-size: 1rem; line-height: 1.55; margin-bottom: 1rem;}
        .mv-gpt-unavailable {font-size: 0.84rem; color: #4A5568; border-left: 3px solid #CBD5E0; padding: 0.35rem 0.7rem; margin-top: 0.6rem;}
        .st-key-primary-composition [data-testid="stGraphVizChart"] {margin-top: 0.35rem; overflow: hidden;}
        .st-key-primary-composition [data-testid="stGraphVizChart"] svg {max-width: 100%; height: auto;}
        [data-testid="stMetric"] {border: 1px solid #d9dee7; border-radius: 10px; padding: 12px;}
        [data-testid="stExpander"] {border-color: #d9dee7;}
        @media (prefers-color-scheme: dark) {
          .mv-product-headline p, .mv-score, .mv-goal-chip, .mv-goal-verification, .mv-grounding-grid span, .mv-gpt-unavailable {color: #B8C0CC;}
          .mv-basis-row {border-color: #4A5568;}
          .mv-goal-context {background: #2D2340;}
          .mv-goal-chip, .mv-grounding-card {background: #1A202C;}
          .mv-grounding-grid > div {border-color: #4A5568;}
          .mv-next-action {background: #183B56;}
        }
        @media (max-width: 767px) {
          .block-container {padding-top: 1.25rem;}
          .st-key-primary-composition [data-testid="stHorizontalBlock"] {flex-direction: column !important; gap: 1.4rem !important;}
          .st-key-primary-composition [data-testid="stColumn"]:first-child {order: 2; width: 100% !important; flex: 1 1 100% !important;}
          .st-key-primary-composition [data-testid="stColumn"]:nth-child(2) {order: 1; width: 100% !important; flex: 1 1 100% !important;}
          .mv-product-headline h1 {font-size: 2.35rem;}
          .mv-product-headline {margin-bottom: 0.9rem;}
          .mv-basis-row {grid-template-columns: 1.7rem 1fr;}
          .mv-score {grid-column: 2;}
          .mv-grounding-grid {grid-template-columns: 1fr 1fr;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
