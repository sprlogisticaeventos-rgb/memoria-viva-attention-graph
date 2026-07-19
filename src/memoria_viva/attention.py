"""Versioned deterministic attention extraction, scoring, and ranking."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .canonical import canonical_json_bytes, sha256_digest, sha256_hex, to_plain_json_value
from .contracts import ContractIssue, ContractValidationError, SchemaRegistry
from .fixtures import RuntimeBundle
from .snapshot import Snapshot


FEATURE_POLICY_SCHEMA_ID = (
    "urn:memoria-viva:attention-graph:schema:attention-feature-policy:1.0.0"
)
ATTENTION_ITEM_SCHEMA_ID = (
    "urn:memoria-viva:attention-graph:schema:attention-item:1.0.0"
)
ATTENTION_RANKING_SCHEMA_ID = (
    "urn:memoria-viva:attention-graph:schema:attention-ranking:1.0.0"
)
ATTENTION_COMPUTATION_V1 = "MV_ATTENTION_COMPUTATION_V1"
COMPONENT_IDS = (
    "temporal_urgency",
    "downstream_impact",
    "strategic_alignment",
    "conflict_or_displacement",
    "event_novelty",
    "evidence_confidence",
)


class AttentionComputationError(ContractValidationError):
    """Raised when policy or runtime state cannot support deterministic scoring."""


@dataclass(frozen=True)
class ComponentExtraction:
    component_id: str
    normalized_value: Decimal | None
    evidence_refs: tuple[str, ...]
    explanation: str
    missing_reason: str | None
    decision_source: str = "DETERMINISTIC_FEATURE_RULE"
    uncertainty: tuple[str, ...] = ()
    feature_policy_version: str = ""

    def to_plain_json(self) -> dict[str, Any]:
        return {
            "component_id": self.component_id,
            "normalized_value": (
                float(self.normalized_value)
                if self.normalized_value is not None
                else None
            ),
            "evidence_refs": list(self.evidence_refs),
            "explanation": self.explanation,
            "missing_reason": self.missing_reason,
            "decision_source": self.decision_source,
            "uncertainty": list(self.uncertainty),
            "feature_policy_version": self.feature_policy_version,
        }


@dataclass(frozen=True)
class _Subject:
    attention_item_id: str
    subject_kind: str
    subject_id: str
    subject_ref: Mapping[str, Any]
    value: Mapping[str, Any]


@dataclass(frozen=True)
class _Candidate:
    subject: _Subject
    components: tuple[ComponentExtraction, ...]
    raw_score: Decimal | None
    display_score: Decimal | None
    band: str
    due_at: str | None
    evidence_refs: tuple[str, ...]
    missing_components: tuple[str, ...]
    evidence_gaps: tuple[str, ...]
    approval_requirement: str


@dataclass(frozen=True)
class AttentionRankingResult:
    """Immutable production ranking plus explicit unscored-item diagnostics."""

    ranking: Mapping[str, Any]
    blocked_items: tuple[Mapping[str, Any], ...]
    component_table: Mapping[str, tuple[Mapping[str, Any], ...]]
    raw_scores: Mapping[str, str | None]
    ranking_bands: Mapping[str, str]
    effective_due_times: Mapping[str, str | None]
    approval_requirements: Mapping[str, str]
    dependency_precedence: tuple[tuple[str, str], ...]
    base_policy_digest: str
    feature_policy_id: str
    feature_policy_version: str
    feature_policy_digest: str
    ranking_digest: str
    warnings: tuple[str, ...]

    def to_plain_json(self) -> dict[str, Any]:
        return to_plain_json_value(
            {
                "ranking": self.ranking,
                "blocked_items": self.blocked_items,
                "component_table": self.component_table,
                "raw_scores": self.raw_scores,
                "ranking_bands": self.ranking_bands,
                "effective_due_times": self.effective_due_times,
                "approval_requirements": self.approval_requirements,
                "dependency_precedence": self.dependency_precedence,
                "base_policy_digest": self.base_policy_digest,
                "feature_policy_id": self.feature_policy_id,
                "feature_policy_version": self.feature_policy_version,
                "feature_policy_digest": self.feature_policy_digest,
                "ranking_digest": self.ranking_digest,
                "warnings": self.warnings,
            }
        )

    def canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.to_plain_json())


def load_attention_feature_policy(
    repository_root: Path,
    *,
    schema_registry: SchemaRegistry | None = None,
) -> Mapping[str, Any]:
    """Load and validate the separate immutable feature-policy input."""

    root = Path(repository_root).resolve()
    path = root / "config" / "attention-feature-policy.v1.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AttentionComputationError(
            [
                ContractIssue(
                    "INVALID_FEATURE_POLICY_JSON",
                    "config/attention-feature-policy.v1.json",
                    None,
                    "",
                    "feature policy must be readable valid JSON",
                )
            ]
        ) from error
    registry = schema_registry or SchemaRegistry(root / "schemas")
    registry.validate(
        FEATURE_POLICY_SCHEMA_ID,
        value,
        instance_path="config/attention-feature-policy.v1.json",
        object_id=value.get("policy_id") if isinstance(value, dict) else None,
    )
    if _contains_weight_key(value):
        raise AttentionComputationError(
            [
                ContractIssue(
                    "FEATURE_POLICY_DUPLICATES_WEIGHTS",
                    "config/attention-feature-policy.v1.json",
                    value.get("policy_id"),
                    "",
                    "feature policy must reference base-policy weights instead of duplicating them",
                )
            ]
        )
    return _deep_freeze(value)


def compute_attention_rankings(
    runtime_bundle: RuntimeBundle,
    snapshot_t0: Snapshot,
    snapshot_t1: Snapshot,
    feature_policy: Mapping[str, Any],
) -> tuple[AttentionRankingResult, AttentionRankingResult]:
    """Compute before and after production rankings without expectation input."""

    _validate_computation_inputs(
        runtime_bundle,
        snapshot_t0,
        snapshot_t1,
        feature_policy,
    )
    before = _compute_one_ranking(
        runtime_bundle,
        snapshot_t0,
        feature_policy,
        ranking_context="before",
        previous=None,
        previous_snapshot=None,
    )
    after = _compute_one_ranking(
        runtime_bundle,
        snapshot_t1,
        feature_policy,
        ranking_context="after",
        previous=before,
        previous_snapshot=snapshot_t0,
    )
    return before, after


def _compute_one_ranking(
    runtime_bundle: RuntimeBundle,
    snapshot: Snapshot,
    feature_policy: Mapping[str, Any],
    *,
    ranking_context: str,
    previous: AttentionRankingResult | None,
    previous_snapshot: Snapshot | None,
) -> AttentionRankingResult:
    base_policy = runtime_bundle.attention_policy
    base_policy_digest = sha256_digest(base_policy)
    feature_policy_digest = sha256_digest(feature_policy)
    weights = {
        component["component_id"]: Decimal(str(component["weight"]))
        for component in base_policy["components"]
    }
    subjects = _select_subjects(runtime_bundle, snapshot)
    candidates = tuple(
        _extract_candidate(
            runtime_bundle,
            snapshot,
            subject,
            feature_policy,
            weights,
            ranking_context,
            previous_snapshot,
        )
        for subject in subjects
    )
    complete = tuple(candidate for candidate in candidates if candidate.raw_score is not None)
    blocked = tuple(candidate for candidate in candidates if candidate.raw_score is None)
    ordered, dependency_pairs = _order_complete_candidates(complete, snapshot)

    previous_items = (
        {item["attention_item_id"]: item for item in previous.ranking["items"]}
        if previous is not None
        else {}
    )
    previous_raw = previous.raw_scores if previous is not None else {}
    production_items = tuple(
        _production_item(
            runtime_bundle,
            snapshot,
            candidate,
            rank,
            weights,
            base_policy_digest,
            feature_policy,
            feature_policy_digest,
            previous_items,
            previous_raw,
        )
        for rank, candidate in enumerate(ordered, start=1)
    )
    for item in production_items:
        _contract_registry().validate(
            ATTENTION_ITEM_SCHEMA_ID,
            item,
            instance_path=f"generated/attention-{ranking_context}/{item['attention_item_id']}",
            object_id=item["attention_item_id"],
        )

    deterministic_input_digest = sha256_digest(
        {
            "computation_contract": ATTENTION_COMPUTATION_V1,
            "snapshot_state_digest": snapshot.state_digest,
            "base_policy_digest": base_policy_digest,
            "feature_policy_digest": feature_policy_digest,
            "ranking_context": ranking_context,
            "candidate_ids": [candidate.subject.attention_item_id for candidate in candidates],
        }
    )
    ranking_id = _ranking_identity(
        ranking_context,
        snapshot.snapshot_id,
        deterministic_input_digest,
        production_items,
    )
    warning = feature_policy["compatible_attention_policy"]["authorization_warning"]
    ranking = {
        "schema_version": "1.0.0",
        "contract_kind": "COMPUTED_PRODUCTION_RANKING",
        "attention_ranking_id": ranking_id,
        "ranking_version": 1,
        "ranking_context": ranking_context,
        "snapshot_id": snapshot.snapshot_id,
        "policy_id": base_policy["policy_id"],
        "policy_version": base_policy["version"],
        "policy_digest": base_policy_digest,
        "deterministic_input_digest": deterministic_input_digest,
        "items": list(production_items),
        "evidence_refs": sorted(
            {reference for item in production_items for reference in item["evidence_refs"]}
        ),
        "generated_at": snapshot.captured_at,
        "tie_break_method": (
            "PROTECTED band; dependency prerequisite within band; unrounded score descending; "
            "effective due time ascending null last; attention item ID ascending. "
            f"Feature policy {feature_policy['policy_id']}@{feature_policy['version']}. WARNING: {warning}"
        ),
    }
    _contract_registry().validate(
        ATTENTION_RANKING_SCHEMA_ID,
        ranking,
        instance_path=f"generated/attention-ranking-{ranking_context}",
        object_id=ranking_id,
    )
    ranking_digest = sha256_digest(ranking)

    blocked_items = tuple(_blocked_projection(candidate) for candidate in blocked)
    component_table = {
        candidate.subject.attention_item_id: tuple(
            _deep_freeze(component.to_plain_json()) for component in candidate.components
        )
        for candidate in candidates
    }
    raw_scores = {
        candidate.subject.attention_item_id: (
            _decimal_text(candidate.raw_score) if candidate.raw_score is not None else None
        )
        for candidate in candidates
    }
    ranking_bands = {
        candidate.subject.attention_item_id: candidate.band for candidate in candidates
    }
    due_times = {
        candidate.subject.attention_item_id: candidate.due_at for candidate in candidates
    }
    approvals = {
        candidate.subject.attention_item_id: candidate.approval_requirement
        for candidate in candidates
    }
    return AttentionRankingResult(
        ranking=_deep_freeze(ranking),
        blocked_items=tuple(_deep_freeze(item) for item in blocked_items),
        component_table=_deep_freeze(component_table),
        raw_scores=_deep_freeze(raw_scores),
        ranking_bands=_deep_freeze(ranking_bands),
        effective_due_times=_deep_freeze(due_times),
        approval_requirements=_deep_freeze(approvals),
        dependency_precedence=dependency_pairs,
        base_policy_digest=base_policy_digest,
        feature_policy_id=feature_policy["policy_id"],
        feature_policy_version=feature_policy["version"],
        feature_policy_digest=feature_policy_digest,
        ranking_digest=ranking_digest,
        warnings=(warning,),
    )


def _validate_computation_inputs(
    runtime_bundle: RuntimeBundle,
    snapshot_t0: Snapshot,
    snapshot_t1: Snapshot,
    feature_policy: Mapping[str, Any],
) -> None:
    issues: list[ContractIssue] = []
    if not isinstance(runtime_bundle, RuntimeBundle):
        issues.append(_issue("INVALID_RUNTIME_BUNDLE", "runtime", "", "RuntimeBundle is required"))
    if not isinstance(snapshot_t0, Snapshot) or snapshot_t0.temporal_role != "T0":
        issues.append(_issue("INVALID_BEFORE_SNAPSHOT", "snapshot-t0", "/temporal_role", "T0 Snapshot is required"))
    if not isinstance(snapshot_t1, Snapshot) or snapshot_t1.temporal_role != "T1":
        issues.append(_issue("INVALID_AFTER_SNAPSHOT", "snapshot-t1", "/temporal_role", "T1 Snapshot is required"))
    if issues:
        raise AttentionComputationError(issues)

    compatible = feature_policy["compatible_attention_policy"]
    base_policy = runtime_bundle.attention_policy
    if not (
        feature_policy["status"] == "APPROVED_FOR_BOUNDED_REPLAY"
        and feature_policy["authorized_mode"] == "REPLAY"
        and compatible["policy_id"] == base_policy["policy_id"]
        and compatible["version"] == base_policy["version"]
        and base_policy["status"] == "draft"
        and base_policy["effective_at"] is None
    ):
        raise AttentionComputationError(
            [
                _issue(
                    "POLICY_COMPATIBILITY_MISMATCH",
                    "config/attention-feature-policy.v1.json",
                    "/compatible_attention_policy",
                    "bounded feature policy requires the exact draft base policy",
                    feature_policy["policy_id"],
                )
            ]
        )
    component_ids = tuple(component["component_id"] for component in base_policy["components"])
    weight_total = sum(
        (Decimal(str(component["weight"])) for component in base_policy["components"]),
        Decimal("0"),
    )
    if component_ids != COMPONENT_IDS or weight_total != Decimal("1.00"):
        raise AttentionComputationError(
            [
                _issue(
                    "INVALID_BASE_POLICY_COMPONENTS",
                    "config/attention-policy.v1.json",
                    "/components",
                    "base policy must provide the six ordered weights totaling 1.00",
                    base_policy["policy_id"],
                )
            ]
        )


def _select_subjects(
    runtime_bundle: RuntimeBundle,
    snapshot: Snapshot,
) -> tuple[_Subject, ...]:
    commitments = {item["commitment_id"]: item for item in snapshot.commitments}
    active_calendar = {
        item["entity_id"]
        for item in snapshot.active_object_refs
        if item["entity_type"] == "CalendarCandidate"
    }
    subjects: list[_Subject] = []
    for attention_id, reference in sorted(runtime_bundle.indexes.attention_item_references.items()):
        if reference.subject_kind == "Commitment" and reference.subject_id in commitments:
            value = commitments[reference.subject_id]
            subjects.append(
                _Subject(
                    attention_id,
                    "Commitment",
                    reference.subject_id,
                    _entity_ref("Commitment", reference.subject_id, value["commitment_version"], value["title"]),
                    value,
                )
            )
        elif reference.subject_kind == "CalendarCandidate" and reference.subject_id in active_calendar:
            value = runtime_bundle.indexes.calendar_candidates[reference.subject_id]
            if value["attention_lineage_mapping"] is None:
                continue
            subjects.append(
                _Subject(
                    attention_id,
                    "CalendarCandidate",
                    reference.subject_id,
                    _entity_ref("CalendarCandidate", reference.subject_id, None, value["public_title"]),
                    value,
                )
            )
    return tuple(subjects)


def _extract_candidate(
    runtime_bundle: RuntimeBundle,
    snapshot: Snapshot,
    subject: _Subject,
    feature_policy: Mapping[str, Any],
    weights: Mapping[str, Decimal],
    ranking_context: str,
    previous_snapshot: Snapshot | None,
) -> _Candidate:
    temporal, due_at = _temporal_component(runtime_bundle, snapshot, subject, feature_policy)
    downstream = _downstream_component(subject, feature_policy)
    strategic = _strategic_component(snapshot, subject, feature_policy)
    conflict = _conflict_component(snapshot, subject, feature_policy)
    novelty = _novelty_component(
        snapshot,
        previous_snapshot,
        subject,
        feature_policy,
        ranking_context,
    )
    required_evidence = tuple(
        sorted(
            {
                reference
                for component in (temporal, downstream, strategic, conflict, novelty)
                for reference in component.evidence_refs
            }
        )
    )
    confidence = _evidence_confidence_component(
        runtime_bundle,
        required_evidence,
        feature_policy,
    )
    components = tuple(
        _annotate_component(component, subject, feature_policy)
        for component in (temporal, downstream, strategic, conflict, novelty, confidence)
    )
    missing = tuple(
        component.component_id
        for component in components
        if component.normalized_value is None
    )
    gaps = tuple(
        component.missing_reason
        for component in components
        if component.missing_reason is not None
    )
    if missing:
        raw_score = None
        display_score = None
    else:
        raw_score = sum(
            (
                component.normalized_value * weights[component.component_id]
                for component in components
                if component.normalized_value is not None
            ),
            Decimal("0"),
        )
        if not Decimal("0") <= raw_score <= Decimal("1"):
            raise AttentionComputationError(
                [
                    _issue(
                        "SCORE_OUT_OF_RANGE",
                        f"generated/{subject.attention_item_id}",
                        "/score",
                        "weighted score must remain within zero and one",
                        subject.attention_item_id,
                    )
                ]
            )
        display_score = raw_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    evidence_refs = tuple(
        sorted({reference for component in components for reference in component.evidence_refs})
    )
    return _Candidate(
        subject=subject,
        components=components,
        raw_score=raw_score,
        display_score=display_score,
        band=_ranking_band(subject),
        due_at=due_at,
        evidence_refs=evidence_refs,
        missing_components=missing,
        evidence_gaps=gaps,
        approval_requirement=_approval_requirement(snapshot, subject),
    )


def _temporal_component(
    runtime_bundle: RuntimeBundle,
    snapshot: Snapshot,
    subject: _Subject,
    feature_policy: Mapping[str, Any],
) -> tuple[ComponentExtraction, str | None]:
    rule = feature_policy["component_rules"]["temporal_urgency"]
    now = _parse_timestamp(snapshot.captured_at)
    evidence = _subject_evidence(subject)
    windows = _subject_calendar_windows(runtime_bundle, subject)
    lifecycle = subject.value.get("lifecycle_status")
    if lifecycle == "UNRESOLVED_MISSED_CARRYOVER" or (
        lifecycle == "UNRESOLVED"
        and any(_parse_timestamp(window["scheduled_end"]) < now for window in windows)
    ):
        due = _latest_window_end(windows)
        return (
            _component(
                "temporal_urgency",
                rule["unresolved_missed_or_past_interval"],
                evidence,
                "Unresolved carryover or an unresolved supporting interval ended before Snapshot time.",
            ),
            due,
        )

    constrained = _constrained_deadline(snapshot, subject.subject_id)
    if constrained is not None:
        due, constraint_evidence = constrained
        value = _deadline_value(now, due, rule["deadline_bands"])
        return (
            _component(
                "temporal_urgency",
                value,
                (*evidence, *constraint_evidence),
                "An active constrained deadline is evaluated against Snapshot time.",
            ),
            due,
        )
    explicit_due = subject.value.get("deadline_at")
    if isinstance(explicit_due, str):
        value = _deadline_value(now, explicit_due, rule["deadline_bands"])
        return (
            _component(
                "temporal_urgency",
                value,
                evidence,
                "The explicit commitment due time is evaluated against Snapshot time.",
            ),
            explicit_due,
        )
    if windows:
        crossing = [
            window
            for window in windows
            if _parse_timestamp(window["scheduled_start"]) <= now <= _parse_timestamp(window["scheduled_end"])
        ]
        if crossing:
            due = min(window["scheduled_end"] for window in crossing)
            return (
                _component(
                    "temporal_urgency",
                    rule["crosses_snapshot"],
                    evidence,
                    "A supporting synthetic Calendar interval crosses Snapshot time.",
                ),
                due,
            )
        future = [
            window for window in windows if _parse_timestamp(window["scheduled_start"]) > now
        ]
        if future:
            due = min(window["scheduled_start"] for window in future)
            value = _future_value(now, due, rule["future_start_bands"])
            return (
                _component(
                    "temporal_urgency",
                    value,
                    evidence,
                    "The earliest future synthetic Calendar start is evaluated against Snapshot time.",
                ),
                due,
            )
    return (
        _unknown_component(
            "temporal_urgency",
            evidence,
            "No defensible deadline, Calendar window, or unresolved carryover temporal evidence exists.",
        ),
        None,
    )


def _downstream_component(
    subject: _Subject,
    feature_policy: Mapping[str, Any],
) -> ComponentExtraction:
    rule = feature_policy["component_rules"]["downstream_impact"]
    for source_field in (
        "downstream_impact",
        "displacement_cost",
        "opportunity_cost",
    ):
        explicit_signal = subject.value.get(source_field)
        level = (
            explicit_signal.get("level")
            if isinstance(explicit_signal, Mapping)
            else explicit_signal
        )
        if level in rule["values"]:
            return _component(
                "downstream_impact",
                rule["values"][level],
                _subject_evidence(subject),
                f"Explicit {source_field} level {level} supplies downstream impact.",
                decision_source="EXPLICIT_IMPACT_SIGNAL",
            )
    if (
        subject.subject_kind == "CalendarCandidate"
        and subject.value.get("ranking_eligibility") == "ELIGIBLE"
    ):
        mobility = subject.value.get("mobility_policy")
        fallback = rule["calendar_only_mobility_fallback"]["values"].get(
            mobility
        )
        if fallback is not None:
            return _component(
                "downstream_impact",
                fallback["normalized_value"],
                _subject_evidence(subject),
                (
                    "Calendar-only fallback source mobility_policy; "
                    f"mobility {mobility} maps to impact level "
                    f"{fallback['impact_level']}. This is not a protection "
                    "bonus and applies only because no explicit impact signal exists."
                ),
                decision_source="CALENDAR_MOBILITY_FALLBACK",
            )
    return _unknown_component(
        "downstream_impact",
        _subject_evidence(subject),
        (
            "No explicit downstream-impact, displacement-cost, or opportunity-cost "
            "level exists, and no approved Calendar-only mobility fallback applies."
        ),
        decision_source="MISSING_APPROVED_IMPACT_SIGNAL",
    )


def _strategic_component(
    snapshot: Snapshot,
    subject: _Subject,
    feature_policy: Mapping[str, Any],
) -> ComponentExtraction:
    rule = feature_policy["component_rules"]["strategic_alignment"]
    active_goals = {
        goal["goal_id"]
        for goal in snapshot.goals
        if goal["operational_lifecycle"] == "ACTIVE"
        and goal["controlled_demo_visibility"] == "INCLUDED"
    }
    if subject.subject_kind == "Commitment":
        goal_refs = set(subject.value["supported_goal_refs"])
        lineage = subject.value["lineage_mappings"]
        if goal_refs & active_goals:
            if any(item["derivation_type"] == "TRIGGER_CREATED" for item in lineage):
                value = rule["trigger_created_direct"]
                reason = "Trigger-created commitment directly serves an included active Goal."
            elif any(item["derivation_type"] == "CONTEXT_SUPPORTED" for item in lineage):
                value = rule["context_supported_indirect"]
                reason = "Context-supported lineage indirectly serves an included active Goal."
            else:
                value = rule["operational_direct"]
                reason = "Operational commitment explicitly supports an included active Goal."
            return _component(
                "strategic_alignment",
                value,
                _subject_evidence(subject),
                reason,
            )
    elif subject.value.get("supported_goal_ref") in active_goals:
        return _component(
            "strategic_alignment",
            rule["calendar_direct"],
            _subject_evidence(subject),
            "Calendar-only attention item explicitly supports an included active Goal.",
        )
    return _unknown_component(
        "strategic_alignment",
        _subject_evidence(subject),
        "No explicit relation to an included active Goal is present.",
    )


def _conflict_component(
    snapshot: Snapshot,
    subject: _Subject,
    feature_policy: Mapping[str, Any],
) -> ComponentExtraction:
    rule = feature_policy["component_rules"]["conflict_or_displacement"]
    relationships = tuple(
        relationship
        for relationship in snapshot.relationships
        if relationship["relationship_type"] in {"conflicts_with", "displaces"}
        and subject.subject_id
        in {
            relationship["from_ref"]["entity_id"],
            relationship["to_ref"]["entity_id"],
        }
    )
    initiated = tuple(
        item for item in relationships if item["from_ref"]["entity_id"] == subject.subject_id
    )
    targeted = tuple(
        item for item in relationships if item["to_ref"]["entity_id"] == subject.subject_id
    )
    relation_evidence = tuple(
        sorted({reference for item in relationships for reference in item["evidence_refs"]})
    )
    if initiated:
        return _component(
            "conflict_or_displacement",
            rule["initiates_supported_conflict_or_displacement"],
            (*_subject_evidence(subject), *relation_evidence),
            "The item initiates an active evidence-supported conflict or conditional displacement relationship.",
            decision_source="SUPPORTED_CONFLICT_INITIATOR",
        )
    conditional_displacement_target = tuple(
        item
        for item in targeted
        if item["relationship_type"] == "displaces"
    )
    if (
        conditional_displacement_target
        and _mobility(subject) == "DISPLACEABLE"
        and _execution(subject) in {"UNKNOWN", "NOT_EXECUTED"}
    ):
        displacement_cost = subject.value.get("displacement_cost")
        cost_text = (
            f"{displacement_cost.get('level')}: {displacement_cost.get('summary')}"
            if isinstance(displacement_cost, Mapping)
            else "UNKNOWN"
        )
        return _component(
            "conflict_or_displacement",
            rule["conditional_displaceable_target_not_executed"],
            (*_subject_evidence(subject), *relation_evidence),
            (
                "The item is an explicitly DISPLACEABLE target of conditional "
                "displacement whose execution remains UNKNOWN or NOT_EXECUTED. "
                "Numeric zero adds no deferment-target bonus; the relationship, "
                "condition, opportunity cost, repair, authority, and uncertainty remain visible. "
                f"Condition: {subject.value.get('condition')}. "
                f"Opportunity cost: {cost_text}. "
                f"Repair requirement: {subject.value.get('repair_requirement')}. "
                f"Authority: {_authority(subject)}."
            ),
            decision_source="CONDITIONAL_DISPLACEMENT_TARGET_NO_BONUS",
        )
    if targeted:
        return _component(
            "conflict_or_displacement",
            rule["other_unresolved_conflict_target"],
            (*_subject_evidence(subject), *relation_evidence),
            "The item is another unresolved target of an active evidence-supported conflict.",
            decision_source="SUPPORTED_UNRESOLVED_CONFLICT_TARGET",
        )
    if _requires_confirmation(subject):
        return _component(
            "conflict_or_displacement",
            rule["confirmation_authority_incomplete"],
            _subject_evidence(subject),
            "Movement authority is incomplete and requires confirmation; no separate confirmation bonus is added.",
            decision_source="INCOMPLETE_MOVEMENT_AUTHORITY",
        )
    return _component(
        "conflict_or_displacement",
        rule["no_supported_condition"],
        _subject_evidence(subject),
        "No evidence-supported conflict, displacement, or incomplete-authority condition exists.",
        decision_source="NO_SUPPORTED_CONDITION",
    )


def _novelty_component(
    snapshot: Snapshot,
    previous_snapshot: Snapshot | None,
    subject: _Subject,
    feature_policy: Mapping[str, Any],
    ranking_context: str,
) -> ComponentExtraction:
    rule = feature_policy["component_rules"]["event_novelty"]
    evidence = _subject_evidence(subject)
    if ranking_context == "before":
        return _component(
            "event_novelty",
            rule["t0_existing"],
            evidence,
            "All selected T0 items pre-exist the canonical trigger.",
            decision_source="T0_EXISTING",
        )
    if subject.subject_kind == "Commitment" and any(
        item["derivation_type"] == "TRIGGER_CREATED"
        for item in subject.value["lineage_mappings"]
    ):
        return _component(
            "event_novelty",
            rule["trigger_created"],
            evidence,
            "The current trigger creates this commitment at T1.",
            decision_source="TRIGGER_CREATED",
        )
    if previous_snapshot is not None and _own_semantic_state_changed(
        previous_snapshot,
        snapshot,
        subject,
    ):
        return _component(
            "event_novelty",
            rule["preexisting_own_state_materially_updated"],
            evidence,
            "The pre-existing item's own approved semantic state materially changed in the current transition.",
            decision_source="OWN_SEMANTIC_STATE_CHANGE",
        )
    has_relationship_only_update = any(
        subject.subject_id
        in {
            relationship["from_ref"]["entity_id"],
            relationship["to_ref"]["entity_id"],
        }
        for relationship in snapshot.relationships
    )
    if has_relationship_only_update:
        return _component(
            "event_novelty",
            rule["relationship_only_update"],
            evidence,
            "Only relationship or explanatory context changed; the item's own semantic state is unchanged, so novelty is zero.",
            decision_source="RELATIONSHIP_ONLY_UPDATE",
        )
    return _component(
        "event_novelty",
        rule["preexisting_unchanged"],
        evidence,
        "The pre-existing item has no material current-trigger update.",
        decision_source="PREEXISTING_UNCHANGED",
    )


def _evidence_confidence_component(
    runtime_bundle: RuntimeBundle,
    evidence_refs: tuple[str, ...],
    feature_policy: Mapping[str, Any],
) -> ComponentExtraction:
    rule = feature_policy["component_rules"]["evidence_confidence"]
    if not evidence_refs:
        return _unknown_component(
            "evidence_confidence",
            (),
            "No required evidence reference exists.",
        )
    values: list[Decimal] = []
    for reference in evidence_refs:
        evidence = runtime_bundle.indexes.evidence.get(reference)
        if evidence is None:
            raise AttentionComputationError(
                [
                    _issue(
                        "UNRESOLVED_SCORING_EVIDENCE",
                        "runtime/evidence",
                        "",
                        "every scoring evidence reference must resolve",
                        reference,
                    )
                ]
            )
        cap = rule["epistemic_caps"][evidence["epistemic_state"]]
        if cap == "UNKNOWN":
            return _unknown_component(
                "evidence_confidence",
                evidence_refs,
                f"Evidence {reference} is blocked and cannot produce confidence.",
            )
        values.append(min(Decimal(str(evidence["confidence"])), Decimal(str(cap))))
    value = min(values)
    return _component(
        "evidence_confidence",
        value,
        evidence_refs,
        "Each evidence confidence is capped by epistemic state, then all required references are aggregated by minimum.",
    )


def _order_complete_candidates(
    candidates: tuple[_Candidate, ...],
    snapshot: Snapshot,
) -> tuple[tuple[_Candidate, ...], tuple[tuple[str, str], ...]]:
    ordered: list[_Candidate] = []
    applied_pairs: list[tuple[str, str]] = []
    by_subject = {candidate.subject.subject_id: candidate for candidate in candidates}
    for band in ("PROTECTED", "STANDARD"):
        band_candidates = tuple(candidate for candidate in candidates if candidate.band == band)
        base_order = tuple(sorted(band_candidates, key=_candidate_sort_key))
        base_position = {
            candidate.subject.attention_item_id: index
            for index, candidate in enumerate(base_order)
        }
        edges: dict[str, set[str]] = {
            candidate.subject.attention_item_id: set() for candidate in band_candidates
        }
        indegree = {key: 0 for key in edges}
        for relationship in snapshot.relationships:
            if relationship["relationship_type"] != "depends_on":
                continue
            dependent = by_subject.get(relationship["from_ref"]["entity_id"])
            prerequisite = by_subject.get(relationship["to_ref"]["entity_id"])
            if (
                dependent is None
                or prerequisite is None
                or dependent.band != band
                or prerequisite.band != band
            ):
                continue
            source = prerequisite.subject.attention_item_id
            target = dependent.subject.attention_item_id
            if target not in edges[source]:
                edges[source].add(target)
                indegree[target] += 1
                applied_pairs.append((source, target))
        available = sorted(
            (item_id for item_id, degree in indegree.items() if degree == 0),
            key=base_position.get,
        )
        band_result: list[_Candidate] = []
        candidate_by_id = {
            candidate.subject.attention_item_id: candidate for candidate in band_candidates
        }
        while available:
            item_id = available.pop(0)
            band_result.append(candidate_by_id[item_id])
            for target in sorted(edges[item_id], key=base_position.get):
                indegree[target] -= 1
                if indegree[target] == 0:
                    available.append(target)
                    available.sort(key=base_position.get)
        if len(band_result) != len(band_candidates):
            raise AttentionComputationError(
                [
                    _issue(
                        "DEPENDENCY_CYCLE",
                        "snapshot/relationships",
                        "/relationships",
                        "dependency precedence requires an acyclic within-band graph",
                    )
                ]
            )
        ordered.extend(band_result)
    return tuple(ordered), tuple(applied_pairs)


def _production_item(
    runtime_bundle: RuntimeBundle,
    snapshot: Snapshot,
    candidate: _Candidate,
    rank: int,
    weights: Mapping[str, Decimal],
    base_policy_digest: str,
    feature_policy: Mapping[str, Any],
    feature_policy_digest: str,
    previous_items: Mapping[str, Mapping[str, Any]],
    previous_raw: Mapping[str, str | None],
) -> dict[str, Any]:
    if candidate.raw_score is None or candidate.display_score is None:
        raise ValueError("production item requires a complete score")
    previous = previous_items.get(candidate.subject.attention_item_id)
    previous_raw_value = previous_raw.get(candidate.subject.attention_item_id)
    previous_raw_decimal = (
        Decimal(previous_raw_value) if previous_raw_value is not None else None
    )
    component_breakdown = [
        {
            "component_id": component.component_id,
            "normalized_value": float(component.normalized_value),
            "weight": float(weights[component.component_id]),
            "weighted_value": float(component.normalized_value * weights[component.component_id]),
            "explanation": component.explanation,
            "evidence_refs": list(component.evidence_refs),
        }
        for component in candidate.components
        if component.normalized_value is not None
    ]
    calculation_digest = sha256_digest(
        {
            "computation_contract": ATTENTION_COMPUTATION_V1,
            "snapshot_state_digest": snapshot.state_digest,
            "base_policy_digest": base_policy_digest,
            "feature_policy_digest": feature_policy_digest,
            "attention_item_id": candidate.subject.attention_item_id,
            "normalized_components": {
                component.component_id: _decimal_text(component.normalized_value)
                for component in candidate.components
                if component.normalized_value is not None
            },
        }
    )
    displaced = tuple(
        sorted(
            {
                candidate.subject.subject_id
                for relationship in snapshot.relationships
                if relationship["relationship_type"] == "displaces"
                and relationship["to_ref"]["entity_id"]
                == candidate.subject.subject_id
            }
        )
    )
    protected = (
        (candidate.subject.subject_id,) if candidate.band == "PROTECTED" else ()
    )
    confirmation = (
        (candidate.subject.subject_id,)
        if _requires_confirmation(candidate.subject)
        else ()
    )
    opportunity_cost, repair_requirement = _opportunity_cost(candidate.subject)
    confidence = next(
        component.normalized_value
        for component in candidate.components
        if component.component_id == "evidence_confidence"
    )
    warning = feature_policy["compatible_attention_policy"]["authorization_warning"]
    return {
        "schema_version": "1.0.0",
        "contract_kind": "COMPUTED_PRODUCTION_ATTENTION_ITEM",
        "attention_item_id": candidate.subject.attention_item_id,
        "attention_item_version": 1,
        "snapshot_id": snapshot.snapshot_id,
        "subject_ref": dict(candidate.subject.subject_ref),
        "policy_id": runtime_bundle.attention_policy["policy_id"],
        "policy_version": runtime_bundle.attention_policy["version"],
        "policy_digest": base_policy_digest,
        "rank": rank,
        "score": float(candidate.display_score),
        "previous_rank": previous["rank"] if previous is not None else None,
        "previous_score": previous["score"] if previous is not None else None,
        "score_delta": (
            float(candidate.raw_score - previous_raw_decimal)
            if previous_raw_decimal is not None
            else None
        ),
        "due_at": candidate.due_at,
        "status": (
            "needs_confirmation"
            if _requires_confirmation(candidate.subject)
            else "monitor"
        ),
        "component_breakdown": component_breakdown,
        "mobility_at_rank": _mobility(candidate.subject),
        "protection_at_rank": _protection(candidate.subject),
        "eligibility_at_rank": _eligibility(candidate.subject),
        "authority_at_rank": _authority(candidate.subject),
        "execution_state": _execution(candidate.subject),
        "evidence_refs": list(candidate.evidence_refs),
        "displaced_commitment_refs": list(displaced),
        "protected_commitment_refs": list(protected),
        "confirmation_required_refs": list(confirmation),
        "blocked_refs": [],
        "opportunity_cost": list(opportunity_cost),
        "repair_requirement": repair_requirement,
        "confidence": float(confidence),
        "uncertainty": list(_subject_uncertainty(candidate.subject)),
        "explanation": (
            f"Deterministic weighted score under feature policy {feature_policy['policy_id']}@{feature_policy['version']} "
            f"({feature_policy_digest}). Protection and dependency affect ordering without numeric bonuses. WARNING: {warning}"
        ),
        "calculation_digest": calculation_digest,
    }


def _blocked_projection(candidate: _Candidate) -> dict[str, Any]:
    return {
        "attention_item_id": candidate.subject.attention_item_id,
        "subject_ref": dict(candidate.subject.subject_ref),
        "status": "NEEDS_CONFIRMATION",
        "missing_components": list(candidate.missing_components),
        "evidence_refs": list(candidate.evidence_refs),
        "evidence_gaps": list(candidate.evidence_gaps),
        "ranking_band": candidate.band,
        "effective_due_time": candidate.due_at,
        "approval_requirement": candidate.approval_requirement,
        "uncertainty": list(_subject_uncertainty(candidate.subject)),
        "explanation": "A required component is UNKNOWN, so no production score or rank was computed.",
    }


def _subject_calendar_windows(
    runtime_bundle: RuntimeBundle,
    subject: _Subject,
) -> tuple[Mapping[str, Any], ...]:
    if subject.subject_kind == "CalendarCandidate":
        return (subject.value,)
    candidate_ids = {
        candidate_id
        for mapping in subject.value["lineage_mappings"]
        for candidate_id in mapping["source_candidate_refs"]
    }
    return tuple(
        runtime_bundle.indexes.calendar_candidates[candidate_id]
        for candidate_id in sorted(candidate_ids)
    )


def _constrained_deadline(
    snapshot: Snapshot,
    subject_id: str,
) -> tuple[str, tuple[str, ...]] | None:
    constraints = {item["constraint_id"]: item for item in snapshot.constraints}
    for relationship in snapshot.relationships:
        if (
            relationship["relationship_type"] == "constrained_by"
            and relationship["from_ref"]["entity_id"] == subject_id
        ):
            constraint = constraints.get(relationship["to_ref"]["entity_id"])
            if constraint is None:
                continue
            due = constraint.get("expires_at") or constraint.get("effective_at")
            if due is not None:
                evidence = tuple(
                    sorted({*relationship["evidence_refs"], *constraint["evidence_refs"]})
                )
                return due, evidence
    return None


def _deadline_value(
    now: datetime,
    due: str,
    bands: tuple[Mapping[str, Any], ...],
) -> Decimal:
    hours = Decimal(str((_parse_timestamp(due) - now).total_seconds())) / Decimal("3600")
    for band in bands:
        maximum = band["maximum_hours"]
        if maximum is None or hours <= Decimal(str(maximum)):
            return Decimal(str(band["value"]))
    raise AssertionError("deadline bands require a terminal null maximum")


def _future_value(
    now: datetime,
    start: str,
    bands: tuple[Mapping[str, Any], ...],
) -> Decimal:
    hours = Decimal(str((_parse_timestamp(start) - now).total_seconds())) / Decimal("3600")
    for band in bands:
        maximum = band["maximum_hours"]
        if maximum is None or hours <= Decimal(str(maximum)):
            return Decimal(str(band["value"]))
    raise AssertionError("future bands require a terminal null maximum")


def _latest_window_end(windows: tuple[Mapping[str, Any], ...]) -> str | None:
    return max((window["scheduled_end"] for window in windows), default=None)


def _subject_evidence(subject: _Subject) -> tuple[str, ...]:
    if subject.subject_kind == "Commitment":
        return tuple(subject.value["evidence_refs"])
    return (subject.value["evidence_ref"],)


def _subject_uncertainty(subject: _Subject) -> tuple[str, ...]:
    return tuple(dict.fromkeys(subject.value["uncertainty"]))


def _own_semantic_state_changed(
    previous_snapshot: Snapshot,
    current_snapshot: Snapshot,
    subject: _Subject,
) -> bool:
    previous_value = _snapshot_subject_value(previous_snapshot, subject)
    if previous_value is None:
        return False
    current_value = subject.value
    tracked_projection = lambda value: {
        "lifecycle": value.get("lifecycle_status"),
        "mobility": value.get("mobility_policy"),
        "eligibility": value.get("eligibility_state", value.get("ranking_eligibility")),
        "authority": value.get("authority_mode"),
        "protection": value.get("protection_state"),
        "condition_state": {
            "conditionality": value.get("conditionality"),
            "condition": value.get("condition"),
            "condition_state": value.get("condition_state"),
        },
        "execution_state": value.get("execution_state"),
        "verified_object_status": {
            key: value.get(key)
            for key in ("status", "evidence_status", "verification_status")
            if key in value
        },
    }
    if tracked_projection(previous_value) != tracked_projection(current_value):
        return True
    return _active_constraint_membership(
        previous_snapshot,
        subject.subject_id,
    ) != _active_constraint_membership(current_snapshot, subject.subject_id)


def _snapshot_subject_value(
    snapshot: Snapshot,
    subject: _Subject,
) -> Mapping[str, Any] | None:
    if subject.subject_kind == "Commitment":
        return next(
            (
                commitment
                for commitment in snapshot.commitments
                if commitment["commitment_id"] == subject.subject_id
            ),
            None,
        )
    if any(
        reference["entity_type"] == "CalendarCandidate"
        and reference["entity_id"] == subject.subject_id
        for reference in snapshot.active_object_refs
    ):
        return subject.value
    return None


def _active_constraint_membership(
    snapshot: Snapshot,
    subject_id: str,
) -> tuple[str, ...]:
    active_catalog = {
        constraint["constraint_id"]
        for constraint in snapshot.constraints
        if constraint["status"] == "ACTIVE"
    }
    active_constraints = {
        constraint["constraint_id"]
        for constraint in snapshot.constraints
        if constraint["constraint_id"] in active_catalog
        and subject_id in constraint["scope"]
    }
    active_constraints.update(
        relationship["to_ref"]["entity_id"]
        for relationship in snapshot.relationships
        if relationship["relationship_type"] == "constrained_by"
        and relationship["from_ref"]["entity_id"] == subject_id
        and relationship["to_ref"]["entity_id"] in active_catalog
    )
    return tuple(
        sorted(active_constraints)
    )


def _ranking_band(subject: _Subject) -> str:
    return "PROTECTED" if _protection(subject) == "PROTECTED" else "STANDARD"


def _requires_confirmation(subject: _Subject) -> bool:
    return (
        _mobility(subject) == "NEEDS_CONFIRMATION"
        or _authority(subject) == "JOINT"
        or subject.value.get("approval_requirement") == "PENDING"
    )


def _approval_requirement(snapshot: Snapshot, subject: _Subject) -> str:
    if subject.subject_kind == "Commitment":
        approval = subject.value["approval_requirement"]
        if approval == "APPROVED" and not any(
            relationship["relationship_type"] == "displaces"
            and relationship["to_ref"]["entity_id"] == subject.subject_id
            for relationship in snapshot.relationships
        ):
            return "NOT_REQUIRED"
        return approval
    return "PENDING" if subject.value["mobility_policy"] == "NEEDS_CONFIRMATION" else "NOT_REQUIRED"


def _mobility(subject: _Subject) -> str | None:
    return subject.value.get("mobility_policy")


def _protection(subject: _Subject) -> str | None:
    if subject.subject_kind == "Commitment":
        return subject.value["protection_state"]
    mobility = subject.value["mobility_policy"]
    if mobility == "PROTECTED":
        return "PROTECTED"
    if mobility == "NEEDS_CONFIRMATION":
        return "NEEDS_CONFIRMATION"
    return "NOT_PROTECTED"


def _eligibility(subject: _Subject) -> str | None:
    return (
        subject.value["eligibility_state"]
        if subject.subject_kind == "Commitment"
        else subject.value["ranking_eligibility"]
    )


def _authority(subject: _Subject) -> str | None:
    return subject.value["authority_mode"] if subject.subject_kind == "Commitment" else None


def _execution(subject: _Subject) -> str:
    return subject.value["execution_state"] if subject.subject_kind == "Commitment" else "UNKNOWN"


def _opportunity_cost(subject: _Subject) -> tuple[tuple[str, ...], str | None]:
    if subject.subject_kind != "Commitment":
        return (), None
    cost = subject.value["displacement_cost"]
    summary = cost["summary"]
    opportunity = (summary,) if isinstance(summary, str) and summary else ()
    return opportunity, subject.value["repair_requirement"]


def _candidate_sort_key(candidate: _Candidate) -> tuple[Any, ...]:
    if candidate.raw_score is None:
        raise ValueError("blocked candidate cannot enter production ordering")
    due_key = (1, "") if candidate.due_at is None else (0, candidate.due_at)
    return (-candidate.raw_score, due_key, candidate.subject.attention_item_id)


def _ranking_identity(
    ranking_context: str,
    snapshot_id: str,
    deterministic_input_digest: str,
    production_items: tuple[Mapping[str, Any], ...],
) -> str:
    projection = {
        "computation_contract": ATTENTION_COMPUTATION_V1,
        "ranking_context": ranking_context,
        "snapshot_id": snapshot_id,
        "deterministic_input_digest": deterministic_input_digest,
        "ordered_calculation_digests": [item["calculation_digest"] for item in production_items],
    }
    return f"RANKING-{ranking_context.upper()}-{sha256_hex(projection)[:20]}"


def _component(
    component_id: str,
    value: Decimal | float | int,
    evidence_refs: tuple[str, ...],
    explanation: str,
    *,
    decision_source: str = "DETERMINISTIC_FEATURE_RULE",
) -> ComponentExtraction:
    normalized = value if isinstance(value, Decimal) else Decimal(str(value))
    if not Decimal("0") <= normalized <= Decimal("1"):
        raise ValueError(f"component {component_id} is outside zero and one")
    return ComponentExtraction(
        component_id,
        normalized,
        tuple(sorted(set(evidence_refs))),
        explanation,
        None,
        decision_source,
    )


def _unknown_component(
    component_id: str,
    evidence_refs: tuple[str, ...],
    reason: str,
    *,
    decision_source: str = "MISSING_DETERMINISTIC_INPUT",
) -> ComponentExtraction:
    return ComponentExtraction(
        component_id,
        None,
        tuple(sorted(set(evidence_refs))),
        reason,
        reason,
        decision_source,
    )


def _annotate_component(
    component: ComponentExtraction,
    subject: _Subject,
    feature_policy: Mapping[str, Any],
) -> ComponentExtraction:
    uncertainty = _subject_uncertainty(subject)
    uncertainty_text = " | ".join(uncertainty) if uncertainty else "None recorded."
    return ComponentExtraction(
        component_id=component.component_id,
        normalized_value=component.normalized_value,
        evidence_refs=component.evidence_refs,
        explanation=(
            f"{component.explanation} Feature policy "
            f"{feature_policy['policy_id']}@{feature_policy['version']}. "
            f"Uncertainty: {uncertainty_text}"
        ),
        missing_reason=component.missing_reason,
        decision_source=component.decision_source,
        uncertainty=uncertainty,
        feature_policy_version=feature_policy["version"],
    )


def _entity_ref(
    entity_type: str,
    entity_id: str,
    entity_version: int | None,
    label: str | None,
) -> Mapping[str, Any]:
    return MappingProxyType(
        {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity_version": entity_version,
            "label": label,
        }
    )


def _decimal_text(value: Decimal | None) -> str:
    if value is None:
        raise ValueError("decimal text requires a value")
    return format(value, "f")


def _contains_weight_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            key in {"weight", "weights"} or _contains_weight_key(child)
            for key, child in value.items()
        )
    if isinstance(value, (list, tuple)):
        return any(_contains_weight_key(child) for child in value)
    return False


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {key: _deep_freeze(child) for key, child in sorted(value.items())}
        )
    if isinstance(value, list):
        return tuple(_deep_freeze(child) for child in value)
    if isinstance(value, tuple):
        return tuple(_deep_freeze(child) for child in value)
    return value


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _issue(
    error_code: str,
    path: str,
    pointer: str,
    message: str,
    object_id: str | None = None,
) -> ContractIssue:
    return ContractIssue(error_code, path, object_id, pointer, message)


@lru_cache(maxsize=1)
def _contract_registry() -> SchemaRegistry:
    repository_root = Path(__file__).resolve().parents[2]
    return SchemaRegistry(repository_root / "schemas")
