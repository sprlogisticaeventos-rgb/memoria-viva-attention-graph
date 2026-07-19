"""Pure canonical-trigger application for immutable Snapshot T1."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .canonical import canonical_json_bytes, sha256_digest, sha256_hex, to_plain_json_value
from .contracts import ContractIssue, ContractValidationError
from .fixtures import RuntimeBundle
from .snapshot import (
    Snapshot,
    build_snapshot_t0,
    finalize_snapshot,
    runtime_input_bundle_digest,
    snapshot_state_projection,
    validate_snapshot_instance,
)


MV_TRIGGER_TRANSITION_V1 = "MV_TRIGGER_TRANSITION_V1"
TRANSITION_POLICY_ID = "mv.canonical-trigger-transition"
TRANSITION_POLICY_VERSION = "1.0.0"

_TRIGGER_CONSTRAINT_IDS = (
    "D-0",
    "C-PUBLIC-ARTIFACT-REQUIREMENTS",
)
_T0_COMMITMENT_IDS = ("CMT-03", "CMT-04", "CMT-05")
_T1_COMMITMENT_IDS = ("CMT-01", "CMT-02", "CMT-03", "CMT-04", "CMT-05")
_EXCLUDED_CALENDAR_IDS = ("CMT-T0-07", "CMT-T0-08")


class TransitionValidationError(ContractValidationError):
    """Raised when a runtime input cannot satisfy the T0-to-T1 contract."""


@dataclass(frozen=True)
class _RelationshipRule:
    rule_id: str
    relationship_type: str
    from_ref: Mapping[str, Any]
    to_ref: Mapping[str, Any]
    evidence_refs: tuple[str, ...]
    epistemic_state: str
    confidence: float
    uncertainty: tuple[str, ...]
    explanation: str


def apply_canonical_trigger(
    runtime_bundle: RuntimeBundle,
    snapshot_t0: Snapshot,
) -> Snapshot:
    """Apply the one validated runtime trigger and return immutable Snapshot T1."""

    _validate_transition_inputs(runtime_bundle, snapshot_t0)
    event = runtime_bundle.source_event
    runtime_digest = runtime_input_bundle_digest(runtime_bundle)
    scenario_id = runtime_bundle.privacy_manifest["fixture_identity"]["artifact_id"]
    snapshot_id = _snapshot_t1_identity(
        scenario_id,
        runtime_digest,
        snapshot_t0.snapshot_id,
    )

    goals = tuple(
        runtime_bundle.indexes.goals[goal_id]
        for goal_id in sorted(runtime_bundle.indexes.goals)
    )
    commitments = tuple(
        runtime_bundle.indexes.commitments[commitment_id]
        for commitment_id in _T1_COMMITMENT_IDS
    )
    constraints = tuple(
        runtime_bundle.indexes.constraints[constraint_id]
        for constraint_id in _TRIGGER_CONSTRAINT_IDS
    )
    active_calendar_ids = tuple(
        runtime_bundle.calendar_t0["active_ranking_candidate_refs"]
    )
    relationships = _materialize_relationships(runtime_bundle)

    active_object_refs = (
        *(_entity_ref("Goal", goal["goal_id"], goal["goal_version"], goal["public_title"]) for goal in goals),
        *(
            _entity_ref(
                "CalendarCandidate",
                candidate_id,
                None,
                runtime_bundle.indexes.calendar_candidates[candidate_id]["public_title"],
            )
            for candidate_id in active_calendar_ids
        ),
        *(
            _entity_ref(
                "Commitment",
                commitment["commitment_id"],
                commitment["commitment_version"],
                commitment["title"],
            )
            for commitment in commitments
        ),
        *(
            _entity_ref(
                "Constraint",
                constraint["constraint_id"],
                constraint["constraint_version"],
                constraint["condition"],
            )
            for constraint in constraints
        ),
    )

    evidence_refs = _t1_evidence_refs(
        snapshot_t0,
        event,
        commitments,
        constraints,
        relationships,
    )
    capacity_evidence_refs = tuple(
        sorted(
            {
                *snapshot_t0.capacity_state["evidence_refs"],
                *event["evidence_refs"],
            }
        )
    )

    state: dict[str, Any] = {
        "schema_version": snapshot_t0.schema_version,
        "ontology_version": snapshot_t0.ontology_version,
        "snapshot_id": snapshot_id,
        "snapshot_version": snapshot_t0.snapshot_version + 1,
        "is_initial": False,
        "temporal_role": "T1",
        "captured_at": event["received_at"],
        "previous_snapshot_id": snapshot_t0.snapshot_id,
        "source_event_refs": [event["source_event_id"]],
        "active_object_refs": list(active_object_refs),
        "excluded_but_retained_objects": list(snapshot_t0.excluded_but_retained_objects),
        "goals": list(goals),
        "commitments": list(commitments),
        "constraints": list(constraints),
        "decision_refs": list(snapshot_t0.decision_refs),
        "blocker_refs": list(snapshot_t0.blocker_refs),
        "artifact_refs": list(snapshot_t0.artifact_refs),
        "relationships": list(relationships),
        "attention_ranking_id": None,
        "graph_delta_id": None,
        "evidence_refs": list(evidence_refs),
        "capacity_state": {
            "availability": "UNKNOWN",
            "epistemic_state": "uncertain",
            "calendar_absence_implies_availability": False,
            "evidence_refs": list(capacity_evidence_refs),
            "uncertainty": [
                "The trigger adds bounded deadline pressure, but exact founder capacity remains unknown.",
                "Calendar evidence is incomplete and absence does not imply available capacity.",
                "Conditional displacement and confirmation-required outcomes remain unresolved.",
            ],
        },
        "privacy_classification": snapshot_t0.privacy_classification,
        "privacy_review_state": snapshot_t0.privacy_review_state,
        "review_state": snapshot_t0.review_state,
    }
    return finalize_snapshot(state, instance_path="generated/snapshot-t1")


def _validate_transition_inputs(
    runtime_bundle: RuntimeBundle,
    snapshot_t0: Snapshot,
) -> None:
    issues: list[ContractIssue] = []
    if not isinstance(runtime_bundle, RuntimeBundle):
        raise TransitionValidationError(
            [
                _issue(
                    "INVALID_RUNTIME_BUNDLE_TYPE",
                    "runtime",
                    "",
                    "transition requires an immutable RuntimeBundle",
                )
            ]
        )
    if not isinstance(snapshot_t0, Snapshot):
        raise TransitionValidationError(
            [
                _issue(
                    "INVALID_SNAPSHOT_TYPE",
                    "snapshot-t0",
                    "",
                    "transition requires the immutable Snapshot representation",
                )
            ]
        )

    validate_snapshot_instance(
        snapshot_t0,
        instance_path="memory/snapshot-t0",
        object_id=snapshot_t0.snapshot_id,
    )
    expected_t0 = build_snapshot_t0(runtime_bundle)

    if snapshot_t0.temporal_role != "T0":
        issues.append(
            _issue(
                "INVALID_T0_ROLE",
                "snapshot-t0",
                "/temporal_role",
                "transition input must have temporal role T0",
                snapshot_t0.snapshot_id,
            )
        )
    if not snapshot_t0.is_initial:
        issues.append(
            _issue(
                "INVALID_T0_INITIAL_STATE",
                "snapshot-t0",
                "/is_initial",
                "transition input must be the initial Snapshot",
                snapshot_t0.snapshot_id,
            )
        )
    if snapshot_t0.previous_snapshot_id is not None:
        issues.append(
            _issue(
                "INVALID_T0_PREDECESSOR",
                "snapshot-t0",
                "/previous_snapshot_id",
                "initial T0 must not have a predecessor",
                snapshot_t0.snapshot_id,
            )
        )
    if snapshot_t0.snapshot_id != expected_t0.snapshot_id:
        issues.append(
            _issue(
                "RUNTIME_INPUT_DIGEST_MISMATCH",
                "snapshot-t0",
                "/snapshot_id",
                "Snapshot T0 identity does not match the RuntimeBundle digest",
                snapshot_t0.snapshot_id,
            )
        )
    if sha256_digest(snapshot_state_projection(snapshot_t0)) != snapshot_t0.state_digest:
        issues.append(
            _issue(
                "INVALID_T0_STATE_DIGEST",
                "snapshot-t0",
                "/state_digest",
                "Snapshot T0 state digest does not match its semantic state",
                snapshot_t0.snapshot_id,
            )
        )

    _validate_t0_membership(snapshot_t0, issues)
    _validate_trigger(runtime_bundle, issues)
    _validate_trigger_objects(runtime_bundle, issues)

    if canonical_json_bytes(snapshot_t0) != canonical_json_bytes(expected_t0):
        issues.append(
            _issue(
                "T0_SNAPSHOT_MISMATCH",
                "snapshot-t0",
                "",
                "Snapshot T0 differs from the canonical RuntimeBundle projection",
                snapshot_t0.snapshot_id,
            )
        )
    if issues:
        raise TransitionValidationError(issues)


def _validate_t0_membership(
    snapshot_t0: Snapshot,
    issues: list[ContractIssue],
) -> None:
    commitment_ids = tuple(item["commitment_id"] for item in snapshot_t0.commitments)
    if commitment_ids != _T0_COMMITMENT_IDS:
        issues.append(
            _issue(
                "T0_COMMITMENT_MEMBERSHIP_MISMATCH",
                "snapshot-t0",
                "/commitments",
                "T0 must contain exactly CMT-03 through CMT-05",
                snapshot_t0.snapshot_id,
            )
        )
    excluded_ids = tuple(
        item["object_ref"]["entity_id"]
        for item in snapshot_t0.excluded_but_retained_objects
    )
    if excluded_ids != _EXCLUDED_CALENDAR_IDS:
        issues.append(
            _issue(
                "T0_EXCLUSION_MISMATCH",
                "snapshot-t0",
                "/excluded_but_retained_objects",
                "T0 must retain CMT-T0-07 and CMT-T0-08 as excluded",
                snapshot_t0.snapshot_id,
            )
        )
    if snapshot_t0.constraints:
        issues.append(
            _issue(
                "TRIGGER_CONSTRAINT_ACTIVE_AT_T0",
                "snapshot-t0",
                "/constraints",
                "trigger-derived constraints must not be active at T0",
                snapshot_t0.snapshot_id,
            )
        )
    if snapshot_t0.source_event_refs:
        issues.append(
            _issue(
                "TRIGGER_APPLIED_AT_T0",
                "snapshot-t0",
                "/source_event_refs",
                "the canonical trigger must not be applied at T0",
                snapshot_t0.snapshot_id,
            )
        )


def _validate_trigger(
    runtime_bundle: RuntimeBundle,
    issues: list[ContractIssue],
) -> None:
    events = runtime_bundle.indexes.source_events
    event = runtime_bundle.source_event
    event_id = event.get("source_event_id")
    if len(events) != 1 or event_id not in events:
        issues.append(
            _issue(
                "INVALID_TRIGGER_COUNT",
                "runtime/openai-event.json",
                "",
                "runtime must contain exactly one indexed SourceEvent",
                event_id,
            )
        )
    elif to_plain_json_value(events[event_id]) != to_plain_json_value(event):
        issues.append(
            _issue(
                "TRIGGER_INDEX_MISMATCH",
                "runtime/openai-event.json",
                "",
                "runtime SourceEvent and its index entry must be identical",
                event_id,
            )
        )
    if event.get("event_role") != "TRIGGER":
        issues.append(
            _issue(
                "INVALID_TRIGGER_ROLE",
                "runtime/openai-event.json",
                "/event_role",
                "canonical SourceEvent role must be TRIGGER",
                event_id,
            )
        )
    if event.get("follow_up_to") is not None:
        issues.append(
            _issue(
                "TRIGGER_FOLLOW_UP_NOT_ALLOWED",
                "runtime/openai-event.json",
                "/follow_up_to",
                "canonical trigger cannot be a follow-up",
                event_id,
            )
        )
    if event.get("occurred_at") is not None:
        issues.append(
            _issue(
                "TRIGGER_OCCURRED_AT_NOT_UNKNOWN",
                "runtime/openai-event.json",
                "/occurred_at",
                "unknown occurred_at must remain null",
                event_id,
            )
        )
    if not event.get("received_at") or not event.get("deadline_at"):
        issues.append(
            _issue(
                "TRIGGER_TIME_REQUIRED",
                "runtime/openai-event.json",
                "/received_at",
                "trigger requires distinct received_at and deadline_at values",
                event_id,
            )
        )
    elif event["received_at"] == event["deadline_at"]:
        issues.append(
            _issue(
                "TRIGGER_TIME_COLLISION",
                "runtime/openai-event.json",
                "/deadline_at",
                "deadline_at must remain distinct from received_at",
                event_id,
            )
        )
    if event.get("authority_scope") != "COMMUNICATION_EVIDENCE_ONLY":
        issues.append(
            _issue(
                "INVALID_TRIGGER_AUTHORITY",
                "runtime/openai-event.json",
                "/authority_scope",
                "communication trigger cannot establish official authority",
                event_id,
            )
        )
    if tuple(event.get("related_goal_refs", ())) != ("GC-01",):
        issues.append(
            _issue(
                "INVALID_TRIGGER_GOAL_SCOPE",
                "runtime/openai-event.json",
                "/related_goal_refs",
                "canonical trigger must serve GC-01 only",
                event_id,
            )
        )
    if event.get("normalization_status") != "normalized":
        issues.append(
            _issue(
                "TRIGGER_NOT_NORMALIZED",
                "runtime/openai-event.json",
                "/normalization_status",
                "canonical trigger must already be normalized",
                event_id,
            )
        )


def _validate_trigger_objects(
    runtime_bundle: RuntimeBundle,
    issues: list[ContractIssue],
) -> None:
    event_id = runtime_bundle.source_event["source_event_id"]
    constraint_ids = tuple(runtime_bundle.indexes.constraints)
    if set(constraint_ids) != set(_TRIGGER_CONSTRAINT_IDS):
        issues.append(
            _issue(
                "TRIGGER_CONSTRAINT_SET_MISMATCH",
                "runtime/constraints.json",
                "/constraints",
                "runtime must contain only the two approved trigger constraints",
            )
        )
    for constraint_id in _TRIGGER_CONSTRAINT_IDS:
        constraint = runtime_bundle.indexes.constraints.get(constraint_id)
        if constraint is None:
            continue
        if (
            constraint.get("authority_reference") != event_id
            or constraint.get("authority_scope") != "COMMUNICATION_EVIDENCE_ONLY"
        ):
            issues.append(
                _issue(
                    "TRIGGER_CONSTRAINT_AUTHORITY_MISMATCH",
                    "runtime/constraints.json",
                    "/constraints",
                    "trigger constraint must retain communication-only authority",
                    constraint_id,
                )
            )

    for commitment_id in ("CMT-01", "CMT-02"):
        commitment = runtime_bundle.indexes.commitments.get(commitment_id)
        if commitment is None:
            issues.append(
                _issue(
                    "TRIGGER_COMMITMENT_MISSING",
                    "runtime/operational-commitments.json",
                    "/commitments",
                    "trigger-created commitment is missing",
                    commitment_id,
                )
            )
            continue
        expected_dimensions = {
            "lifecycle_status": "ACTIVE",
            "mobility_policy": "PROTECTED",
            "authority_mode": "FOUNDER",
            "eligibility_state": "ELIGIBLE",
            "protection_state": "PROTECTED",
        }
        if any(commitment.get(key) != value for key, value in expected_dimensions.items()):
            issues.append(
                _issue(
                    "TRIGGER_COMMITMENT_STATE_MISMATCH",
                    "runtime/operational-commitments.json",
                    "/commitments",
                    "trigger-created commitment dimensions do not match the approved catalog",
                    commitment_id,
                )
            )
        if commitment.get("execution_state") in {"EXECUTED"}:
            issues.append(
                _issue(
                    "TRIGGER_COMMITMENT_ALREADY_EXECUTED",
                    "runtime/operational-commitments.json",
                    "/commitments",
                    "trigger creation cannot establish execution",
                    commitment_id,
                )
            )
        if not any(
            mapping.get("derivation_type") == "TRIGGER_CREATED"
            for mapping in commitment.get("lineage_mappings", ())
        ):
            issues.append(
                _issue(
                    "TRIGGER_LINEAGE_MISSING",
                    "runtime/operational-commitments.json",
                    "/commitments",
                    "trigger-created commitment requires explicit trigger lineage",
                    commitment_id,
                )
            )


def _materialize_relationships(
    runtime_bundle: RuntimeBundle,
) -> tuple[Mapping[str, Any], ...]:
    event = runtime_bundle.source_event
    commitments = runtime_bundle.indexes.commitments
    constraints = runtime_bundle.indexes.constraints
    cmt_01 = commitments["CMT-01"]
    cmt_02 = commitments["CMT-02"]
    cmt_04 = commitments["CMT-04"]
    d0 = constraints["D-0"]

    cmt_01_ref = _commitment_ref(cmt_01)
    cmt_02_ref = _commitment_ref(cmt_02)
    cmt_04_ref = _commitment_ref(cmt_04)
    d0_ref = _constraint_ref(d0)
    trigger_evidence = tuple(event["evidence_refs"])
    approved_commitment_evidence = tuple(
        sorted({*cmt_01["evidence_refs"], *cmt_02["evidence_refs"]})
    )

    rules: list[_RelationshipRule] = [
        _RelationshipRule(
            rule_id="MVTR-001-BUILD-FIRST-DEPENDENCY",
            relationship_type="depends_on",
            from_ref=cmt_02_ref,
            to_ref=cmt_01_ref,
            evidence_refs=approved_commitment_evidence,
            epistemic_state="confirmed",
            confidence=1.0,
            uncertainty=tuple(cmt_02["uncertainty"]),
            explanation="BUILD_FIRST requires the distinct submission package to depend on the minimum verifiable product demonstration; neither artifact is thereby completed.",
        ),
        _RelationshipRule(
            rule_id="MVTR-002-CMT-01-DEADLINE",
            relationship_type="constrained_by",
            from_ref=cmt_01_ref,
            to_ref=d0_ref,
            evidence_refs=tuple(sorted({*trigger_evidence, *cmt_01["evidence_refs"], *d0["evidence_refs"]})),
            epistemic_state="inferred",
            confidence=1.0,
            uncertainty=tuple(d0["uncertainty"]),
            explanation="The trigger-created demonstration commitment is bounded by the synthetic D-0 communication constraint; official requirements remain unverified.",
        ),
        _RelationshipRule(
            rule_id="MVTR-003-CMT-02-DEADLINE",
            relationship_type="constrained_by",
            from_ref=cmt_02_ref,
            to_ref=d0_ref,
            evidence_refs=tuple(sorted({*trigger_evidence, *cmt_02["evidence_refs"], *d0["evidence_refs"]})),
            epistemic_state="inferred",
            confidence=1.0,
            uncertainty=tuple(d0["uncertainty"]),
            explanation="The distinct submission-package commitment is bounded by the synthetic D-0 communication constraint; official requirements remain unverified.",
        ),
        _RelationshipRule(
            rule_id="MVTR-004-CMT-01-CMT-04-CONFLICT",
            relationship_type="conflicts_with",
            from_ref=cmt_01_ref,
            to_ref=cmt_04_ref,
            evidence_refs=tuple(sorted({*trigger_evidence, *cmt_01["evidence_refs"], *cmt_04["evidence_refs"]})),
            epistemic_state="inferred",
            confidence=1.0,
            uncertainty=tuple(cmt_04["uncertainty"]),
            explanation="The approved bounded transition identifies a capacity conflict between minimum demonstration work and Pending bounded validation; coexistence alone is not used as conflict evidence.",
        ),
        _RelationshipRule(
            rule_id="MVTR-005-CMT-01-CMT-04-CONDITIONAL-DISPLACEMENT",
            relationship_type="displaces",
            from_ref=cmt_01_ref,
            to_ref=cmt_04_ref,
            evidence_refs=tuple(sorted({*trigger_evidence, *cmt_01["evidence_refs"], *cmt_04["evidence_refs"]})),
            epistemic_state="uncertain",
            confidence=1.0,
            uncertainty=tuple(cmt_04["uncertainty"]),
            explanation=_conditional_displacement_explanation(cmt_04),
        ),
    ]
    rules.extend(_flexible_capacity_rules(runtime_bundle, cmt_02_ref, cmt_02))
    return tuple(_materialize_relationship(rule, event) for rule in rules)


def _flexible_capacity_rules(
    runtime_bundle: RuntimeBundle,
    cmt_02_ref: Mapping[str, Any],
    cmt_02: Mapping[str, Any],
) -> tuple[_RelationshipRule, ...]:
    event = runtime_bundle.source_event
    rules: list[_RelationshipRule] = []
    for candidate_id in sorted(runtime_bundle.indexes.calendar_candidates):
        candidate = runtime_bundle.indexes.calendar_candidates[candidate_id]
        if not _is_explicit_flexible_capacity(candidate, event):
            continue
        rules.append(
            _RelationshipRule(
                rule_id=f"MVTR-006-CMT-02-FLEXIBLE-CAPACITY-{candidate_id}",
                relationship_type="conflicts_with",
                from_ref=cmt_02_ref,
                to_ref=_calendar_candidate_ref(candidate),
                evidence_refs=tuple(
                    sorted(
                        {
                            *event["evidence_refs"],
                            *cmt_02["evidence_refs"],
                            candidate["evidence_ref"],
                        }
                    )
                ),
                epistemic_state="inferred",
                confidence=0.7,
                uncertainty=tuple(
                    sorted({*cmt_02["uncertainty"], *candidate["uncertainty"]})
                ),
                explanation=(
                    "The active flexible Calendar window falls after trigger receipt and before synthetic D-0, so it is an explicit bounded capacity conflict for CMT-02. Coexistence without this timing and mobility evidence does not create a conflict."
                ),
            )
        )
    return tuple(rules)


def _is_explicit_flexible_capacity(
    candidate: Mapping[str, Any],
    event: Mapping[str, Any],
) -> bool:
    if (
        candidate.get("inclusion_state") != "ACTIVE_RANKING_CANDIDATE"
        or candidate.get("ranking_eligibility") != "ELIGIBLE"
        or candidate.get("mobility_policy") != "FLEXIBLE"
    ):
        return False
    start = candidate.get("scheduled_start")
    end = candidate.get("scheduled_end")
    received = event.get("received_at")
    deadline = event.get("deadline_at")
    if not all(isinstance(value, str) for value in (start, end, received, deadline)):
        return False
    return _parse_timestamp(received) <= _parse_timestamp(start) < _parse_timestamp(end) <= _parse_timestamp(deadline)


def _materialize_relationship(
    rule: _RelationshipRule,
    event: Mapping[str, Any],
) -> Mapping[str, Any]:
    relationship_id = _relationship_identity(rule)
    explanation = rule.explanation
    if rule.uncertainty:
        explanation = f"{explanation} Uncertainty: {' | '.join(rule.uncertainty)}"
    return {
        "relationship_id": relationship_id,
        "relationship_type": rule.relationship_type,
        "from_ref": dict(rule.from_ref),
        "to_ref": dict(rule.to_ref),
        "epistemic_state": rule.epistemic_state,
        "confidence": rule.confidence,
        "evidence_refs": list(rule.evidence_refs),
        "created_by": rule.rule_id,
        "creator_type": "DETERMINISTIC_RULE",
        "explanation": explanation,
        "created_at": event["received_at"],
        "ontology_version": "1.0.0",
        "status": "active",
        "supersedes_relationship_id": None,
    }


def _relationship_identity(rule: _RelationshipRule) -> str:
    projection = {
        "transition_contract": MV_TRIGGER_TRANSITION_V1,
        "transition_policy_id": TRANSITION_POLICY_ID,
        "transition_policy_version": TRANSITION_POLICY_VERSION,
        "rule_id": rule.rule_id,
        "relationship_type": rule.relationship_type,
        "from_ref": rule.from_ref,
        "to_ref": rule.to_ref,
    }
    return f"REL-T1-{sha256_hex(projection)[:20]}"


def _snapshot_t1_identity(
    scenario_id: str,
    runtime_digest: str,
    previous_snapshot_id: str,
) -> str:
    projection = {
        "identity_contract": "MV_SNAPSHOT_IDENTITY_V1",
        "scenario_id": scenario_id,
        "temporal_role": "T1",
        "runtime_input_bundle_digest": runtime_digest,
        "previous_snapshot_id": previous_snapshot_id,
        "transition_contract": MV_TRIGGER_TRANSITION_V1,
        "transition_policy_id": TRANSITION_POLICY_ID,
        "transition_policy_version": TRANSITION_POLICY_VERSION,
    }
    return f"SNAPSHOT-T1-{sha256_hex(projection)[:20]}"


def _conditional_displacement_explanation(cmt_04: Mapping[str, Any]) -> str:
    cost = cmt_04["displacement_cost"]
    return (
        "This is a conditional policy relationship, not executed movement. "
        f"Execution remains {cmt_04['execution_state']}. "
        f"Condition: {cmt_04['condition']} "
        f"Opportunity cost: {cost['level']} — {cost['summary']} "
        f"Repair requirement: {cmt_04['repair_requirement']} "
        f"Authority: {cmt_04['authority_mode']}."
    )


def _t1_evidence_refs(
    snapshot_t0: Snapshot,
    event: Mapping[str, Any],
    commitments: tuple[Mapping[str, Any], ...],
    constraints: tuple[Mapping[str, Any], ...],
    relationships: tuple[Mapping[str, Any], ...],
) -> tuple[str, ...]:
    references = set(snapshot_t0.evidence_refs)
    references.update(event["evidence_refs"])
    references.update(
        reference for commitment in commitments for reference in commitment["evidence_refs"]
    )
    references.update(
        reference for constraint in constraints for reference in constraint["evidence_refs"]
    )
    references.update(
        reference for relationship in relationships for reference in relationship["evidence_refs"]
    )
    return tuple(sorted(references))


def _entity_ref(
    entity_type: str,
    entity_id: str,
    entity_version: int | None,
    label: str | None,
) -> dict[str, Any]:
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "entity_version": entity_version,
        "label": label,
    }


def _commitment_ref(commitment: Mapping[str, Any]) -> dict[str, Any]:
    return _entity_ref(
        "Commitment",
        commitment["commitment_id"],
        commitment["commitment_version"],
        commitment["title"],
    )


def _constraint_ref(constraint: Mapping[str, Any]) -> dict[str, Any]:
    return _entity_ref(
        "Constraint",
        constraint["constraint_id"],
        constraint["constraint_version"],
        constraint["condition"],
    )


def _calendar_candidate_ref(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return _entity_ref(
        "CalendarCandidate",
        candidate["candidate_id"],
        None,
        candidate["public_title"],
    )


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
