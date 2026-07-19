"""Deterministic GraphDelta generation for the bounded T0-to-T1 replay."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .attention import AttentionRankingResult
from .canonical import canonical_json_bytes, sha256_digest, sha256_hex, to_plain_json_value
from .contracts import ContractIssue, ContractValidationError, SchemaRegistry
from .fixtures import RuntimeBundle
from .snapshot import Snapshot
from .transition import MV_TRIGGER_TRANSITION_V1


GRAPH_DELTA_SCHEMA_ID = (
    "urn:memoria-viva:attention-graph:schema:graph-delta:1.0.0"
)
GRAPH_DELTA_CONTRACT = "MV_GRAPH_DELTA_V1"
GRAPH_DELTA_POLICY_ID = "mv.graph-delta"
GRAPH_DELTA_POLICY_VERSION = "1.0.0"


class GraphDeltaValidationError(ContractValidationError):
    """Raised when replay state cannot produce a valid deterministic delta."""


@dataclass(frozen=True)
class GraphDelta:
    """Immutable schema-valid delta plus a comparator-only relationship index."""

    value: Mapping[str, Any]
    relationship_semantics: Mapping[str, Mapping[str, str]]

    @property
    def graph_delta_id(self) -> str:
        return self.value["graph_delta_id"]

    @property
    def transition_digest(self) -> str:
        return self.value["transition_digest"]

    @property
    def changes(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(self.value["changes"])

    def to_plain_json(self) -> dict[str, Any]:
        plain = to_plain_json_value(self.value)
        if not isinstance(plain, dict):
            raise TypeError("GraphDelta must project to a JSON object")
        return plain

    def canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.value)


def graph_delta_digest_projection(value: GraphDelta | Mapping[str, Any]) -> dict[str, Any]:
    """Return complete GraphDelta semantics except its self-digest field."""

    plain = value.to_plain_json() if isinstance(value, GraphDelta) else to_plain_json_value(value)
    if not isinstance(plain, dict):
        raise TypeError("GraphDelta digest projection must be a JSON object")
    plain.pop("transition_digest", None)
    return plain


def build_graph_delta(
    runtime_bundle: RuntimeBundle,
    snapshot_t0: Snapshot,
    snapshot_t1: Snapshot,
    ranking_before: AttentionRankingResult,
    ranking_after: AttentionRankingResult,
) -> GraphDelta:
    """Build the production GraphDelta without reading any human oracle."""

    _validate_inputs(
        runtime_bundle,
        snapshot_t0,
        snapshot_t1,
        ranking_before,
        ranking_after,
    )
    event = runtime_bundle.source_event
    commitments = runtime_bundle.indexes.commitments
    constraints = runtime_bundle.indexes.constraints
    candidates = runtime_bundle.indexes.calendar_candidates
    goal = runtime_bundle.indexes.goals["GC-01"]
    recorded_at = snapshot_t1.captured_at
    before_ranks = _rank_index(ranking_before)
    after_ranks = _rank_index(ranking_after)
    relationships = {
        (
            relationship["relationship_type"],
            relationship["from_ref"]["entity_id"],
            relationship["to_ref"]["entity_id"],
        ): relationship
        for relationship in snapshot_t1.relationships
    }

    changes: list[dict[str, Any]] = []
    relationship_semantics: dict[str, Mapping[str, str]] = {}

    changes.append(
        _object_change(
            rule_id="MVGD-001-TRIGGER-ADDED",
            category="ADDED",
            entity_ref=_entity_ref(
                "SourceEvent",
                event["source_event_id"],
                event["source_event_version"],
                event["title"],
            ),
            previous_label="ABSENT_AT_T0",
            new_label="NORMALIZED_TRIGGER_AT_T1",
            actual_execution_state="UNKNOWN",
            conditionality="UNCONDITIONAL",
            condition_state="NOT_APPLICABLE",
            condition=None,
            reason="The one validated communication event is normalized as the canonical T1 trigger.",
            opportunity_cost=(),
            repair_requirement=None,
            authority_scope=event["authority_scope"],
            evidence_refs=event["evidence_refs"],
            confidence=_evidence_confidence(runtime_bundle, event["evidence_refs"]),
            uncertainty=event["uncertainty"],
            explanation="The trigger is added as communication evidence only; it does not establish official rules, eligibility, compliance, or completion.",
            recorded_at=recorded_at,
            snapshot_t0=snapshot_t0,
            snapshot_t1=snapshot_t1,
        )
    )
    for rule_id, constraint_id, conditionality, condition_state, new_label in (
        (
            "MVGD-002-DEADLINE-CONSTRAINT-ADDED",
            "D-0",
            "UNCONDITIONAL",
            "NOT_APPLICABLE",
            "ACTIVE_COMMUNICATION_DERIVED_CONSTRAINT",
        ),
        (
            "MVGD-003-ARTIFACT-CONSTRAINT-ADDED",
            "C-PUBLIC-ARTIFACT-REQUIREMENTS",
            "CONDITIONAL",
            "PENDING",
            "PROPOSED_UNKNOWN_OFFICIAL_VERIFICATION",
        ),
    ):
        constraint = constraints[constraint_id]
        changes.append(
            _object_change(
                rule_id=rule_id,
                category="ADDED",
                entity_ref=_entity_ref(
                    "Constraint",
                    constraint_id,
                    constraint["constraint_version"],
                    constraint["condition"],
                ),
                previous_label="ABSENT_AT_T0",
                new_label=new_label,
                actual_execution_state="UNKNOWN",
                conditionality=conditionality,
                condition_state=condition_state,
                condition=constraint["condition"] if conditionality == "CONDITIONAL" else None,
                reason="The canonical trigger activates only the approved communication-derived constraint catalog entry.",
                opportunity_cost=(),
                repair_requirement=None,
                authority_scope=constraint["authority_scope"],
                evidence_refs=constraint["evidence_refs"],
                confidence=_evidence_confidence(
                    runtime_bundle, constraint["evidence_refs"]
                ),
                uncertainty=constraint["uncertainty"],
                explanation="The constraint remains bounded by communication evidence and does not claim official verification or completion.",
                recorded_at=recorded_at,
                snapshot_t0=snapshot_t0,
                snapshot_t1=snapshot_t1,
            )
        )

    for rule_id, commitment_id in (
        ("MVGD-004-CMT-01-ADDED", "CMT-01"),
        ("MVGD-005-CMT-02-ADDED", "CMT-02"),
    ):
        commitment = commitments[commitment_id]
        changes.append(
            _object_change(
                rule_id=rule_id,
                category="ADDED",
                entity_ref=_commitment_ref(commitment),
                previous_label="DOES_NOT_EXIST_AT_T0",
                new_label="ACTIVE_PROTECTED_ELIGIBLE_AT_T1",
                actual_execution_state="UNKNOWN",
                conditionality="UNCONDITIONAL",
                condition_state="NOT_APPLICABLE",
                condition=None,
                reason="The canonical trigger creates the approved bounded operational commitment without claiming execution or completion.",
                opportunity_cost=(commitment["displacement_cost"]["summary"],),
                repair_requirement=commitment["repair_requirement"],
                authority_scope=commitment["authority_mode"],
                evidence_refs=commitment["evidence_refs"],
                confidence=_evidence_confidence(
                    runtime_bundle, commitment["evidence_refs"]
                ),
                uncertainty=commitment["uncertainty"],
                explanation=f"{commitment_id} enters T1 as a distinct protected, eligible, non-completed commitment.",
                recorded_at=recorded_at,
                snapshot_t0=snapshot_t0,
                snapshot_t1=snapshot_t1,
            )
        )

    dependency = _required_relationship(
        relationships,
        "depends_on",
        "CMT-02",
        "CMT-01",
    )
    dependency_change = _relationship_change(
        rule_id="MVGD-006-BUILD-FIRST-DEPENDENCY-ADDED",
        category="ADDED",
        relationship=dependency,
        previous_label="ABSENT_AT_T0",
        new_label="ACTIVE_DEPENDS_ON",
        actual_execution_state="UNKNOWN",
        conditionality="UNCONDITIONAL",
        condition_state="NOT_APPLICABLE",
        condition=None,
        reason="BUILD_FIRST requires the minimum verifiable demonstration before the dependent submission package.",
        opportunity_cost=(),
        repair_requirement=None,
        authority_scope="EXPLICIT_HUMAN_DECISION",
        recorded_at=recorded_at,
        snapshot_t0=snapshot_t0,
        snapshot_t1=snapshot_t1,
    )
    changes.append(dependency_change)
    _record_relationship_semantics(relationship_semantics, dependency)

    changes.append(
        _object_change(
            rule_id="MVGD-007-GC-01-SALIENCE-UPDATED",
            category="UPDATED",
            entity_ref=_entity_ref(
                "Goal",
                goal["goal_id"],
                goal["goal_version"],
                goal["public_title"],
            ),
            previous_label="ACTIVE_PRE_TRIGGER_SALIENCE",
            new_label="ACTIVE_TRIGGER_INCREASED_SALIENCE",
            actual_execution_state="UNKNOWN",
            conditionality="UNCONDITIONAL",
            condition_state="NOT_APPLICABLE",
            condition=None,
            reason="New trigger-created commitments and constraints increase GC-01 operational relevance without changing its lifecycle.",
            opportunity_cost=(),
            repair_requirement=None,
            authority_scope="EXPLICIT_HUMAN_DECISION",
            evidence_refs=tuple(sorted({*goal["evidence_refs"], *event["evidence_refs"]})),
            confidence=1.0,
            uncertainty=goal["uncertainty"],
            explanation="GC-01 remains active and incomplete; artifact existence is not completion evidence.",
            recorded_at=recorded_at,
            snapshot_t0=snapshot_t0,
            snapshot_t1=snapshot_t1,
        )
    )
    changes.append(
        _object_change(
            rule_id="MVGD-008-CAPACITY-UPDATED",
            category="UPDATED",
            entity_ref=_entity_ref(
                "Snapshot",
                snapshot_t1.snapshot_id,
                snapshot_t1.snapshot_version,
                "T1 capacity boundary",
            ),
            previous_label="FINITE_UNKNOWN",
            new_label="MORE_CONSTRAINED_BUT_STILL_UNKNOWN",
            previous_state_id=snapshot_t0.snapshot_id,
            previous_state_version=snapshot_t0.snapshot_version,
            previous_state_digest=snapshot_t0.state_digest,
            new_state_id=snapshot_t1.snapshot_id,
            new_state_version=snapshot_t1.snapshot_version,
            new_state_digest=snapshot_t1.state_digest,
            actual_execution_state="UNKNOWN",
            conditionality="UNCONDITIONAL",
            condition_state="NOT_APPLICABLE",
            condition=None,
            reason="The trigger adds deadline and artifact pressure while exact capacity remains epistemically unknown.",
            opportunity_cost=(),
            repair_requirement=None,
            authority_scope="SYSTEM",
            evidence_refs=tuple(sorted(snapshot_t1.capacity_state["evidence_refs"])),
            confidence=1.0,
            uncertainty=snapshot_t1.capacity_state["uncertainty"],
            explanation="Calendar absence is not converted into free capacity; the qualitative change preserves UNKNOWN.",
            recorded_at=recorded_at,
            snapshot_t0=snapshot_t0,
            snapshot_t1=snapshot_t1,
        )
    )
    changes.append(
        _object_change(
            rule_id="MVGD-009-RANKING-UPDATED",
            category="UPDATED",
            entity_ref=_entity_ref(
                "AttentionRanking",
                ranking_after.ranking["attention_ranking_id"],
                ranking_after.ranking["ranking_version"],
                "Computed attention ranking after trigger",
            ),
            previous_label=f"{len(before_ranks)}_ORDERED_ITEMS",
            new_label=f"{len(after_ranks)}_ORDERED_ITEMS_BUILD_FIRST",
            previous_state_id=ranking_before.ranking["attention_ranking_id"],
            previous_state_version=ranking_before.ranking["ranking_version"],
            previous_state_digest=ranking_before.ranking_digest,
            new_state_id=ranking_after.ranking["attention_ranking_id"],
            new_state_version=ranking_after.ranking["ranking_version"],
            new_state_digest=ranking_after.ranking_digest,
            actual_execution_state="UNKNOWN",
            conditionality="UNCONDITIONAL",
            condition_state="NOT_APPLICABLE",
            condition=None,
            reason="Deterministic scoring changes ranking membership and positions after the trigger.",
            opportunity_cost=(),
            repair_requirement=None,
            authority_scope="POLICY",
            evidence_refs=tuple(sorted(ranking_after.ranking["evidence_refs"])),
            confidence=1.0,
            uncertainty=tuple(
                sorted(
                    {
                        uncertainty
                        for item in ranking_after.ranking["items"]
                        for uncertainty in item["uncertainty"]
                    }
                )
            ),
            explanation="The computed T1 ranking adds CMT-01 and CMT-02 under BUILD_FIRST while preserving every T0 obligation.",
            recorded_at=recorded_at,
            snapshot_t0=snapshot_t0,
            snapshot_t1=snapshot_t1,
        )
    )

    for rule_id, relationship_type, from_id, to_id, confidence in (
        ("MVGD-010-CMT-01-CMT-04-CONFLICT", "conflicts_with", "CMT-01", "CMT-04", 1.0),
        ("MVGD-011-CMT-02-CALENDAR-06-CONFLICT", "conflicts_with", "CMT-02", "CMT-T0-06", 0.7),
        ("MVGD-012-CMT-02-CALENDAR-09-CONFLICT", "conflicts_with", "CMT-02", "CMT-T0-09", 0.7),
    ):
        relationship = _required_relationship(
            relationships, relationship_type, from_id, to_id
        )
        change = _relationship_change(
            rule_id=rule_id,
            category="CONFLICTED",
            relationship=relationship,
            previous_label="NO_PRE_TRIGGER_RELATIONSHIP",
            new_label=(
                "ACTIVE_CONFLICTS_WITH"
                if to_id == "CMT-04"
                else "ACTIVE_CAPACITY_CONFLICT"
            ),
            actual_execution_state="UNKNOWN",
            conditionality="UNCONDITIONAL",
            condition_state="NOT_APPLICABLE",
            condition=None,
            reason="The relationship is supported by explicit trigger, timing, mobility, and evidence semantics; coexistence alone is insufficient.",
            opportunity_cost=(),
            repair_requirement=None,
            authority_scope="EXPLICIT_HUMAN_DECISION",
            confidence=confidence,
            recorded_at=recorded_at,
            snapshot_t0=snapshot_t0,
            snapshot_t1=snapshot_t1,
        )
        changes.append(change)
        _record_relationship_semantics(relationship_semantics, relationship)

    cmt_04 = commitments["CMT-04"]
    displacement = _required_relationship(
        relationships,
        "displaces",
        "CMT-01",
        "CMT-04",
    )
    displacement_change = _relationship_change(
        rule_id="MVGD-013-CMT-04-CONDITIONAL-DISPLACEMENT",
        category="DISPLACED",
        relationship=displacement,
        previous_label=f"T0_RANK_{before_ranks['ATTN-CMT-04']}_UNRESOLVED",
        new_label=f"T1_RANK_{after_ranks['ATTN-CMT-04']}_CONDITIONAL_DISPLACEMENT",
        actual_execution_state=cmt_04["execution_state"],
        conditionality="CONDITIONAL",
        condition_state=cmt_04["condition_state"],
        condition=cmt_04["condition"],
        reason="CMT-04 is the only authorized conditional displacement target; authorization does not establish movement.",
        opportunity_cost=(cmt_04["displacement_cost"]["summary"],),
        repair_requirement=cmt_04["repair_requirement"],
        authority_scope=cmt_04["authority_mode"],
        confidence=_evidence_confidence(runtime_bundle, cmt_04["evidence_refs"]),
        uncertainty=cmt_04["uncertainty"],
        recorded_at=recorded_at,
        snapshot_t0=snapshot_t0,
        snapshot_t1=snapshot_t1,
    )
    changes.append(displacement_change)
    _record_relationship_semantics(relationship_semantics, displacement)

    for rule_id, entity_ref, evidence_refs, uncertainty, previous_label, new_label in (
        (
            "MVGD-014-CMT-01-PROTECTED",
            _commitment_ref(commitments["CMT-01"]),
            commitments["CMT-01"]["evidence_refs"],
            commitments["CMT-01"]["uncertainty"],
            "DOES_NOT_EXIST_AT_T0",
            "PROTECTED_AT_T1",
        ),
        (
            "MVGD-015-CMT-02-PROTECTED",
            _commitment_ref(commitments["CMT-02"]),
            commitments["CMT-02"]["evidence_refs"],
            commitments["CMT-02"]["uncertainty"],
            "DOES_NOT_EXIST_AT_T0",
            "PROTECTED_AT_T1",
        ),
        (
            "MVGD-016-CALENDAR-10-PROTECTED",
            _calendar_ref(candidates["CMT-T0-10"]),
            (candidates["CMT-T0-10"]["evidence_ref"],),
            candidates["CMT-T0-10"]["uncertainty"],
            f"T0_RANK_{before_ranks['ATTN-CALENDAR-CMT-T0-10']}_PROTECTED",
            f"T1_RANK_{after_ranks['ATTN-CALENDAR-CMT-T0-10']}_PROTECTED",
        ),
    ):
        changes.append(
            _object_change(
                rule_id=rule_id,
                category="PROTECTED",
                entity_ref=entity_ref,
                previous_label=previous_label,
                new_label=new_label,
                actual_execution_state="UNKNOWN",
                conditionality="UNCONDITIONAL",
                condition_state="NOT_APPLICABLE",
                condition=None,
                reason="The approved protected state remains a precedence guardrail and is not a numeric score contribution.",
                opportunity_cost=(),
                repair_requirement=None,
                authority_scope="EXPLICIT_HUMAN_DECISION",
                evidence_refs=evidence_refs,
                confidence=1.0,
                uncertainty=uncertainty,
                explanation="Protection remains visible without claiming execution or completion.",
                recorded_at=recorded_at,
                snapshot_t0=snapshot_t0,
                snapshot_t1=snapshot_t1,
            )
        )

    cmt_05 = commitments["CMT-05"]
    calendar_01 = candidates["CMT-T0-01"]
    for rule_id, entity_ref, evidence_refs, uncertainty, condition, repair, authority, previous_rank, after_rank in (
        (
            "MVGD-017-CMT-05-REQUIRES-CONFIRMATION",
            _commitment_ref(cmt_05),
            cmt_05["evidence_refs"],
            cmt_05["uncertainty"],
            cmt_05["condition"],
            cmt_05["repair_requirement"],
            cmt_05["authority_mode"],
            before_ranks["ATTN-CMT-05"],
            after_ranks["ATTN-CMT-05"],
        ),
        (
            "MVGD-018-CALENDAR-01-REQUIRES-CONFIRMATION",
            _calendar_ref(calendar_01),
            (calendar_01["evidence_ref"],),
            calendar_01["uncertainty"],
            "Movement requires confirmation from the other authority holder.",
            None,
            "JOINT",
            before_ranks["ATTN-CALENDAR-CMT-T0-01"],
            after_ranks["ATTN-CALENDAR-CMT-T0-01"],
        ),
    ):
        changes.append(
            _object_change(
                rule_id=rule_id,
                category="REQUIRES_CONFIRMATION",
                entity_ref=entity_ref,
                previous_label=f"T0_RANK_{previous_rank}_NEEDS_CONFIRMATION",
                new_label=f"T1_RANK_{after_rank}_NEEDS_CONFIRMATION",
                actual_execution_state="NOT_EXECUTED",
                conditionality="CONDITIONAL",
                condition_state="PENDING",
                condition=condition,
                reason="Incomplete movement authority preserves the confirmation requirement and prevents automatic action.",
                opportunity_cost=(),
                repair_requirement=repair,
                authority_scope=authority,
                evidence_refs=evidence_refs,
                confidence=1.0,
                uncertainty=uncertainty,
                explanation="The item remains ranking-eligible but no movement or approval is inferred.",
                recorded_at=recorded_at,
                snapshot_t0=snapshot_t0,
                snapshot_t1=snapshot_t1,
            )
        )

    cmt_03 = commitments["CMT-03"]
    changes.append(
        _object_change(
            rule_id="MVGD-019-CMT-03-UNCHANGED",
            category="UNCHANGED",
            entity_ref=_commitment_ref(cmt_03),
            previous_label="UNRESOLVED_VISIBLE_AT_T0",
            new_label="UNRESOLVED_VISIBLE_AT_T1",
            actual_execution_state=cmt_03["execution_state"],
            conditionality="UNCONDITIONAL",
            condition_state="NOT_APPLICABLE",
            condition=None,
            reason="The trigger does not resolve or remove the missed carryover commitment.",
            opportunity_cost=(cmt_03["displacement_cost"]["summary"],),
            repair_requirement=cmt_03["repair_requirement"],
            authority_scope=cmt_03["authority_mode"],
            evidence_refs=cmt_03["evidence_refs"],
            confidence=_evidence_confidence(runtime_bundle, cmt_03["evidence_refs"]),
            uncertainty=cmt_03["uncertainty"],
            explanation="CMT-03 remains visible and unresolved after the trigger.",
            recorded_at=recorded_at,
            snapshot_t0=snapshot_t0,
            snapshot_t1=snapshot_t1,
        )
    )
    for rule_id, candidate_id in (
        ("MVGD-020-CALENDAR-07-UNCHANGED", "CMT-T0-07"),
        ("MVGD-021-CALENDAR-08-UNCHANGED", "CMT-T0-08"),
    ):
        candidate = candidates[candidate_id]
        changes.append(
            _object_change(
                rule_id=rule_id,
                category="UNCHANGED",
                entity_ref=_calendar_ref(candidate),
                previous_label="EXCLUDED_BUT_RETAINED_AT_T0",
                new_label="EXCLUDED_BUT_RETAINED_AT_T1",
                actual_execution_state="UNKNOWN",
                conditionality="UNCONDITIONAL",
                condition_state="NOT_APPLICABLE",
                condition=None,
                reason="The controlled transition does not reactivate, delete, or infer completion for excluded evidence.",
                opportunity_cost=(),
                repair_requirement=None,
                authority_scope="EXPLICIT_HUMAN_DECISION",
                evidence_refs=(candidate["evidence_ref"],),
                confidence=1.0,
                uncertainty=candidate["uncertainty"],
                explanation=f"{candidate_id} remains excluded but retained across the transition.",
                recorded_at=recorded_at,
                snapshot_t0=snapshot_t0,
                snapshot_t1=snapshot_t1,
            )
        )

    identity_projection = {
        "contract": GRAPH_DELTA_CONTRACT,
        "policy_id": GRAPH_DELTA_POLICY_ID,
        "policy_version": GRAPH_DELTA_POLICY_VERSION,
        "previous_snapshot_id": snapshot_t0.snapshot_id,
        "previous_snapshot_digest": snapshot_t0.state_digest,
        "new_snapshot_id": snapshot_t1.snapshot_id,
        "new_snapshot_digest": snapshot_t1.state_digest,
        "ranking_before_id": ranking_before.ranking["attention_ranking_id"],
        "ranking_before_digest": ranking_before.ranking_digest,
        "ranking_after_id": ranking_after.ranking["attention_ranking_id"],
        "ranking_after_digest": ranking_after.ranking_digest,
        "changes": changes,
    }
    graph_delta_id = f"GRAPH-DELTA-T0-T1-{sha256_hex(identity_projection)[:20]}"
    value: dict[str, Any] = {
        "schema_version": "1.0.0",
        "ontology_version": snapshot_t1.ontology_version,
        "graph_delta_id": graph_delta_id,
        "graph_delta_version": 1,
        "previous_snapshot_id": snapshot_t0.snapshot_id,
        "previous_snapshot_digest": snapshot_t0.state_digest,
        "new_snapshot_id": snapshot_t1.snapshot_id,
        "new_snapshot_digest": snapshot_t1.state_digest,
        "changes": changes,
        "explanation": "Deterministic evidence-backed T0-to-T1 transition receipt. Conditionality, UNKNOWN values, exclusions, and incomplete claims remain visible.",
        "evidence_refs": sorted(
            {
                evidence_ref
                for change in changes
                for evidence_ref in change["evidence_refs"]
            }
        ),
        "generated_at": recorded_at,
    }
    value["transition_digest"] = sha256_digest(graph_delta_digest_projection(value))
    _contract_registry().validate(
        GRAPH_DELTA_SCHEMA_ID,
        value,
        instance_path="memory/graph-delta",
        object_id=graph_delta_id,
    )
    return GraphDelta(
        value=_deep_freeze(value),
        relationship_semantics=_deep_freeze(relationship_semantics),
    )


def _validate_inputs(
    runtime_bundle: RuntimeBundle,
    snapshot_t0: Snapshot,
    snapshot_t1: Snapshot,
    ranking_before: AttentionRankingResult,
    ranking_after: AttentionRankingResult,
) -> None:
    issues: list[ContractIssue] = []
    if not isinstance(runtime_bundle, RuntimeBundle):
        issues.append(_issue("INVALID_RUNTIME_BUNDLE", "runtime", "", "GraphDelta requires RuntimeBundle"))
    if not isinstance(snapshot_t0, Snapshot) or snapshot_t0.temporal_role != "T0":
        issues.append(_issue("INVALID_T0_SNAPSHOT", "snapshot-t0", "/temporal_role", "GraphDelta requires Snapshot T0"))
    if not isinstance(snapshot_t1, Snapshot) or snapshot_t1.temporal_role != "T1":
        issues.append(_issue("INVALID_T1_SNAPSHOT", "snapshot-t1", "/temporal_role", "GraphDelta requires Snapshot T1"))
    if isinstance(snapshot_t0, Snapshot) and isinstance(snapshot_t1, Snapshot):
        if snapshot_t1.previous_snapshot_id != snapshot_t0.snapshot_id:
            issues.append(_issue("SNAPSHOT_CHAIN_MISMATCH", "snapshot-t1", "/previous_snapshot_id", "T1 must reference T0"))
    for label, ranking, snapshot in (
        ("before", ranking_before, snapshot_t0),
        ("after", ranking_after, snapshot_t1),
    ):
        if not isinstance(ranking, AttentionRankingResult):
            issues.append(_issue("INVALID_RANKING_TYPE", f"ranking-{label}", "", "GraphDelta requires AttentionRankingResult"))
        elif isinstance(snapshot, Snapshot) and ranking.ranking["snapshot_id"] != snapshot.snapshot_id:
            issues.append(_issue("RANKING_SNAPSHOT_MISMATCH", f"ranking-{label}", "/snapshot_id", "ranking must reference its Snapshot"))
    if issues:
        raise GraphDeltaValidationError(issues)


def _object_change(
    *,
    rule_id: str,
    category: str,
    entity_ref: Mapping[str, Any],
    previous_label: str,
    new_label: str,
    actual_execution_state: str,
    conditionality: str,
    condition_state: str,
    condition: str | None,
    reason: str,
    opportunity_cost: Sequence[str],
    repair_requirement: str | None,
    authority_scope: str,
    evidence_refs: Sequence[str],
    confidence: float,
    uncertainty: Sequence[str],
    explanation: str,
    recorded_at: str,
    snapshot_t0: Snapshot,
    snapshot_t1: Snapshot,
    previous_state_id: str | None = None,
    previous_state_version: int | None = None,
    previous_state_digest: str | None = None,
    new_state_id: str | None = None,
    new_state_version: int | None = None,
    new_state_digest: str | None = None,
) -> dict[str, Any]:
    return _change(
        rule_id=rule_id,
        category=category,
        affected_kind="OBJECT",
        affected_ref=entity_ref,
        affected_relationship_id=None,
        previous_label=previous_label,
        new_label=new_label,
        previous_state_id=previous_state_id or entity_ref["entity_id"],
        previous_state_version=previous_state_version if previous_state_version is not None else entity_ref["entity_version"],
        previous_state_digest=previous_state_digest,
        new_state_id=new_state_id or entity_ref["entity_id"],
        new_state_version=new_state_version if new_state_version is not None else entity_ref["entity_version"],
        new_state_digest=new_state_digest,
        actual_execution_state=actual_execution_state,
        conditionality=conditionality,
        condition_state=condition_state,
        condition=condition,
        reason=reason,
        opportunity_cost=opportunity_cost,
        repair_requirement=repair_requirement,
        authority_scope=authority_scope,
        evidence_refs=evidence_refs,
        confidence=confidence,
        uncertainty=uncertainty,
        explanation=explanation,
        recorded_at=recorded_at,
        snapshot_t0=snapshot_t0,
        snapshot_t1=snapshot_t1,
    )


def _relationship_change(
    *,
    rule_id: str,
    category: str,
    relationship: Mapping[str, Any],
    previous_label: str,
    new_label: str,
    actual_execution_state: str,
    conditionality: str,
    condition_state: str,
    condition: str | None,
    reason: str,
    opportunity_cost: Sequence[str],
    repair_requirement: str | None,
    authority_scope: str,
    recorded_at: str,
    snapshot_t0: Snapshot,
    snapshot_t1: Snapshot,
    confidence: float | None = None,
    uncertainty: Sequence[str] | None = None,
) -> dict[str, Any]:
    return _change(
        rule_id=rule_id,
        category=category,
        affected_kind="RELATIONSHIP",
        affected_ref=None,
        affected_relationship_id=relationship["relationship_id"],
        previous_label=previous_label,
        new_label=new_label,
        previous_state_id=relationship["relationship_id"],
        previous_state_version=1,
        previous_state_digest=None,
        new_state_id=relationship["relationship_id"],
        new_state_version=1,
        new_state_digest=sha256_digest(relationship),
        actual_execution_state=actual_execution_state,
        conditionality=conditionality,
        condition_state=condition_state,
        condition=condition,
        reason=reason,
        opportunity_cost=opportunity_cost,
        repair_requirement=repair_requirement,
        authority_scope=authority_scope,
        evidence_refs=relationship["evidence_refs"],
        confidence=confidence if confidence is not None else relationship["confidence"],
        uncertainty=uncertainty if uncertainty is not None else _relationship_uncertainty(relationship),
        explanation=relationship["explanation"],
        recorded_at=recorded_at,
        snapshot_t0=snapshot_t0,
        snapshot_t1=snapshot_t1,
    )


def _change(
    *,
    rule_id: str,
    category: str,
    affected_kind: str,
    affected_ref: Mapping[str, Any] | None,
    affected_relationship_id: str | None,
    previous_label: str,
    new_label: str,
    previous_state_id: str | None,
    previous_state_version: int | None,
    previous_state_digest: str | None,
    new_state_id: str | None,
    new_state_version: int | None,
    new_state_digest: str | None,
    actual_execution_state: str,
    conditionality: str,
    condition_state: str,
    condition: str | None,
    reason: str,
    opportunity_cost: Sequence[str],
    repair_requirement: str | None,
    authority_scope: str,
    evidence_refs: Sequence[str],
    confidence: float,
    uncertainty: Sequence[str],
    explanation: str,
    recorded_at: str,
    snapshot_t0: Snapshot,
    snapshot_t1: Snapshot,
) -> dict[str, Any]:
    identity = {
        "contract": GRAPH_DELTA_CONTRACT,
        "rule_id": rule_id,
        "category": category,
        "affected_kind": affected_kind,
        "affected_ref": affected_ref,
        "affected_relationship_id": affected_relationship_id,
        "previous_snapshot_id": snapshot_t0.snapshot_id,
        "new_snapshot_id": snapshot_t1.snapshot_id,
    }
    return {
        "change_id": f"CHANGE-T1-{sha256_hex(identity)[:20]}",
        "category": category,
        "affected_kind": affected_kind,
        "affected_ref": dict(affected_ref) if affected_ref is not None else None,
        "affected_relationship_id": affected_relationship_id,
        "previous_state": {
            "state_id": previous_state_id,
            "state_version": previous_state_version,
            "state_digest": previous_state_digest,
            "state_label": previous_label,
        },
        "expected_new_state": {
            "state_id": new_state_id,
            "state_version": new_state_version,
            "state_digest": new_state_digest,
            "state_label": new_label,
        },
        "actual_execution_state": actual_execution_state,
        "conditionality": conditionality,
        "condition_state": condition_state,
        "condition": condition,
        "reason": reason,
        "opportunity_cost": list(opportunity_cost),
        "repair_requirement": repair_requirement,
        "authority_scope": authority_scope,
        "evidence_refs": sorted(set(evidence_refs)),
        "confidence": confidence,
        "uncertainty": sorted(set(uncertainty)),
        "explanation": explanation,
        "creator_type": "DETERMINISTIC_RULE",
        "ontology_version": snapshot_t1.ontology_version,
        "recorded_at": recorded_at,
    }


def _rank_index(result: AttentionRankingResult) -> dict[str, int]:
    return {
        item["attention_item_id"]: item["rank"]
        for item in result.ranking["items"]
    }


def _evidence_confidence(
    runtime_bundle: RuntimeBundle,
    evidence_refs: Sequence[str],
) -> float:
    values = [
        float(runtime_bundle.indexes.evidence[evidence_ref]["confidence"])
        for evidence_ref in evidence_refs
    ]
    if not values:
        raise GraphDeltaValidationError(
            [
                _issue(
                    "GRAPH_CHANGE_EVIDENCE_MISSING",
                    "runtime/evidence",
                    "",
                    "GraphDelta changes require evidence-backed confidence",
                )
            ]
        )
    return min(values)


def _required_relationship(
    relationships: Mapping[tuple[str, str, str], Mapping[str, Any]],
    relationship_type: str,
    from_id: str,
    to_id: str,
) -> Mapping[str, Any]:
    try:
        return relationships[(relationship_type, from_id, to_id)]
    except KeyError as error:
        raise GraphDeltaValidationError(
            [
                _issue(
                    "REQUIRED_RELATIONSHIP_MISSING",
                    "snapshot-t1",
                    "/relationships",
                    f"missing {from_id} {relationship_type} {to_id}",
                )
            ]
        ) from error


def _record_relationship_semantics(
    target: dict[str, Mapping[str, str]],
    relationship: Mapping[str, Any],
) -> None:
    target[relationship["relationship_id"]] = {
        "relationship_type": relationship["relationship_type"],
        "from_id": relationship["from_ref"]["entity_id"],
        "to_id": relationship["to_ref"]["entity_id"],
    }


def _relationship_uncertainty(relationship: Mapping[str, Any]) -> tuple[str, ...]:
    explanation = relationship["explanation"]
    marker = " Uncertainty: "
    if marker not in explanation:
        return ()
    return tuple(part.strip() for part in explanation.split(marker, 1)[1].split(" | "))


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


def _calendar_ref(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return _entity_ref(
        "CalendarCandidate",
        candidate["candidate_id"],
        None,
        candidate["public_title"],
    )


def _issue(error_code: str, path: str, pointer: str, message: str) -> ContractIssue:
    return ContractIssue(error_code, path, None, pointer, message)


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {key: _deep_freeze(child) for key, child in sorted(value.items())}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_deep_freeze(child) for child in value)
    return value


@lru_cache(maxsize=1)
def _contract_registry() -> SchemaRegistry:
    return SchemaRegistry(Path(__file__).resolve().parents[2] / "schemas")
