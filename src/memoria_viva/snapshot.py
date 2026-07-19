"""Deterministic immutable Snapshot T0 construction."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .canonical import (
    MV_CANONICAL_JSON_V1,
    canonical_json_bytes,
    sha256_digest,
    sha256_hex,
    to_plain_json_value,
)
from .contracts import SchemaRegistry
from .fixtures import RuntimeBundle


SNAPSHOT_SCHEMA_ID = "urn:memoria-viva:attention-graph:schema:snapshot:1.0.0"
RUNTIME_INPUT_BUNDLE_CONTRACT = "MV_RUNTIME_INPUT_BUNDLE_V1"
SNAPSHOT_IDENTITY_CONTRACT = "MV_SNAPSHOT_IDENTITY_V1"


@dataclass(frozen=True)
class SnapshotT0:
    """Immutable public representation shared by controlled Snapshots."""

    schema_version: str
    ontology_version: str
    snapshot_id: str
    snapshot_version: int
    is_initial: bool
    temporal_role: str
    captured_at: str
    previous_snapshot_id: str | None
    source_event_refs: tuple[str, ...]
    active_object_refs: tuple[Mapping[str, Any], ...]
    excluded_but_retained_objects: tuple[Mapping[str, Any], ...]
    goals: tuple[Mapping[str, Any], ...]
    commitments: tuple[Mapping[str, Any], ...]
    constraints: tuple[Mapping[str, Any], ...]
    decision_refs: tuple[Mapping[str, Any], ...]
    blocker_refs: tuple[Mapping[str, Any], ...]
    artifact_refs: tuple[Mapping[str, Any], ...]
    relationships: tuple[Mapping[str, Any], ...]
    attention_ranking_id: str | None
    graph_delta_id: str | None
    evidence_refs: tuple[str, ...]
    capacity_state: Mapping[str, Any]
    privacy_classification: str
    privacy_review_state: str
    review_state: str
    state_digest: str

    def to_plain_json(self) -> dict[str, Any]:
        """Return a new mutable projection detached from Snapshot state."""

        plain = to_plain_json_value(self)
        if not isinstance(plain, dict):  # Defensive: dataclasses project to objects.
            raise TypeError("Snapshot projection must be a JSON object")
        return plain

    def canonical_bytes(self) -> bytes:
        """Return canonical bytes without exposing mutable internal values."""

        return canonical_json_bytes(self)


# Backward-compatible generic name used by post-T0 transition code. The
# underlying frozen representation remains exactly the Phase 1B contract.
Snapshot = SnapshotT0


def runtime_input_bundle_projection(runtime_bundle: RuntimeBundle) -> dict[str, Any]:
    """Project exactly the eight semantic runtime documents under stable keys."""

    _require_runtime_bundle(runtime_bundle)
    return {
        "canonicalization_contract": MV_CANONICAL_JSON_V1,
        "runtime_bundle_contract": RUNTIME_INPUT_BUNDLE_CONTRACT,
        "public_goals": to_plain_json_value(runtime_bundle.public_goal_set),
        "calendar_t0": to_plain_json_value(runtime_bundle.calendar_t0),
        "evidence": to_plain_json_value(runtime_bundle.evidence_catalog),
        "operational_commitments": to_plain_json_value(
            runtime_bundle.operational_commitments
        ),
        "constraints": to_plain_json_value(runtime_bundle.constraints_catalog),
        "canonical_event": to_plain_json_value(runtime_bundle.source_event),
        "privacy_manifest": to_plain_json_value(runtime_bundle.privacy_manifest),
        "attention_policy": to_plain_json_value(runtime_bundle.attention_policy),
    }


def runtime_input_bundle_digest(runtime_bundle: RuntimeBundle) -> str:
    """Digest the versioned semantic runtime-input projection."""

    return sha256_digest(runtime_input_bundle_projection(runtime_bundle))


def snapshot_state_projection(snapshot: SnapshotT0 | Mapping[str, Any]) -> dict[str, Any]:
    """Project complete Snapshot semantics except ``state_digest``.

    ``state_digest`` is the sole excluded field because including it would make
    the digest self-referential. Snapshot identity remains in the projection.
    """

    plain = to_plain_json_value(snapshot)
    if not isinstance(plain, dict):
        raise TypeError("Snapshot state projection must be a JSON object")
    plain.pop("state_digest", None)
    return plain


def build_snapshot_t0(runtime_bundle: RuntimeBundle) -> SnapshotT0:
    """Build, digest, schema-validate, and freeze Snapshot T0 from runtime only."""

    _require_runtime_bundle(runtime_bundle)
    runtime_digest = runtime_input_bundle_digest(runtime_bundle)
    scenario_id = runtime_bundle.privacy_manifest["fixture_identity"]["artifact_id"]
    snapshot_id = _snapshot_identity(scenario_id, runtime_digest)

    goals = tuple(
        runtime_bundle.indexes.goals[goal_id]
        for goal_id in sorted(runtime_bundle.indexes.goals)
    )
    commitments = tuple(
        runtime_bundle.indexes.commitments[commitment_id]
        for commitment_id in runtime_bundle.t0_commitment_ids
    )
    active_calendar_ids = tuple(
        runtime_bundle.calendar_t0["active_ranking_candidate_refs"]
    )
    excluded_calendar_ids = tuple(
        runtime_bundle.calendar_t0["excluded_but_retained_refs"]
    )

    active_object_refs = (
        *(_goal_ref(goal) for goal in goals),
        *(
            _calendar_ref(runtime_bundle.indexes.calendar_candidates[candidate_id])
            for candidate_id in active_calendar_ids
        ),
        *(_commitment_ref(commitment) for commitment in commitments),
    )
    excluded_objects = tuple(
        _excluded_calendar_record(
            runtime_bundle.indexes.calendar_candidates[candidate_id]
        )
        for candidate_id in excluded_calendar_ids
    )
    evidence_refs = tuple(
        sorted(_t0_evidence_refs(goals, commitments, runtime_bundle))
    )
    calendar_evidence_refs = tuple(
        sorted(
            candidate["evidence_ref"]
            for candidate in runtime_bundle.indexes.calendar_candidates.values()
        )
    )

    state: dict[str, Any] = {
        "schema_version": "1.0.0",
        "ontology_version": runtime_bundle.calendar_t0["ontology_version"],
        "snapshot_id": snapshot_id,
        "snapshot_version": 1,
        "is_initial": True,
        "temporal_role": "T0",
        "captured_at": runtime_bundle.calendar_t0["synthetic_anchor_at"],
        "previous_snapshot_id": None,
        "source_event_refs": [],
        "active_object_refs": list(active_object_refs),
        "excluded_but_retained_objects": list(excluded_objects),
        "goals": list(goals),
        "commitments": list(commitments),
        "constraints": [],
        "decision_refs": [],
        "blocker_refs": [],
        "artifact_refs": [],
        "relationships": [],
        "attention_ranking_id": None,
        "graph_delta_id": None,
        "evidence_refs": list(evidence_refs),
        "capacity_state": {
            "availability": "UNKNOWN",
            "epistemic_state": "uncertain",
            "calendar_absence_implies_availability": False,
            "evidence_refs": list(calendar_evidence_refs),
            "uncertainty": [
                "Calendar evidence is incomplete and absence does not imply available capacity.",
                "Exact founder capacity remains unknown.",
            ],
        },
        "privacy_classification": "SANITIZED_PRIVATE",
        "privacy_review_state": "NOT_REVIEWED",
        "review_state": "NOT_REVIEWED",
    }
    return finalize_snapshot(state, instance_path="generated/snapshot-t0")


def finalize_snapshot(
    state: Mapping[str, Any],
    *,
    instance_path: str,
) -> Snapshot:
    """Digest, validate, and recursively freeze one complete Snapshot state."""

    plain = to_plain_json_value(state)
    if not isinstance(plain, dict):
        raise TypeError("Snapshot state must be a JSON object")
    if "state_digest" in plain:
        raise ValueError("Snapshot finalization requires an undigested state")
    plain["state_digest"] = sha256_digest(snapshot_state_projection(plain))
    validate_snapshot_instance(
        plain,
        instance_path=instance_path,
        object_id=plain.get("snapshot_id"),
    )
    return _snapshot_from_plain(plain)


def validate_snapshot_instance(
    instance: Snapshot | Mapping[str, Any],
    *,
    instance_path: str,
    object_id: str | None = None,
) -> None:
    """Validate a Snapshot through the closed canonical schema registry."""

    _contract_registry().validate(
        SNAPSHOT_SCHEMA_ID,
        to_plain_json_value(instance),
        instance_path=instance_path,
        object_id=object_id,
    )


def _snapshot_identity(scenario_id: str, runtime_digest: str) -> str:
    identity_projection = {
        "identity_contract": SNAPSHOT_IDENTITY_CONTRACT,
        "scenario_id": scenario_id,
        "temporal_role": "T0",
        "runtime_input_bundle_digest": runtime_digest,
    }
    return f"SNAPSHOT-T0-{sha256_hex(identity_projection)[:20]}"


def _goal_ref(goal: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "entity_type": "Goal",
        "entity_id": goal["goal_id"],
        "entity_version": goal["goal_version"],
        "label": goal["public_title"],
    }


def _calendar_ref(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "entity_type": "CalendarCandidate",
        "entity_id": candidate["candidate_id"],
        "entity_version": None,
        "label": candidate["public_title"],
    }


def _commitment_ref(commitment: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "entity_type": "Commitment",
        "entity_id": commitment["commitment_id"],
        "entity_version": commitment["commitment_version"],
        "label": commitment["title"],
    }


def _excluded_calendar_record(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "object_ref": _calendar_ref(candidate),
        "exclusion_reason": candidate["exclusion_reason"],
        "evidence_refs": [candidate["evidence_ref"]],
        "uncertainty": list(candidate["uncertainty"]),
    }


def _t0_evidence_refs(
    goals: tuple[Mapping[str, Any], ...],
    commitments: tuple[Mapping[str, Any], ...],
    runtime_bundle: RuntimeBundle,
) -> set[str]:
    references = {
        reference for goal in goals for reference in goal["evidence_refs"]
    }
    references.update(
        reference
        for commitment in commitments
        for reference in commitment["evidence_refs"]
    )
    references.update(
        candidate["evidence_ref"]
        for candidate in runtime_bundle.indexes.calendar_candidates.values()
    )
    return references


def _snapshot_from_plain(state: Mapping[str, Any]) -> SnapshotT0:
    frozen = {key: _freeze(value) for key, value in state.items()}
    return SnapshotT0(**frozen)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {key: _freeze(child) for key, child in sorted(value.items())}
        )
    if isinstance(value, list):
        return tuple(_freeze(child) for child in value)
    return value


def _require_runtime_bundle(value: Any) -> None:
    if not isinstance(value, RuntimeBundle):
        raise TypeError("Snapshot T0 construction accepts RuntimeBundle only")


@lru_cache(maxsize=1)
def _contract_registry() -> SchemaRegistry:
    """Load only canonical repository schemas; no fixture or caller path is read."""

    repository_root = Path(__file__).resolve().parents[2]
    return SchemaRegistry(repository_root / "schemas")
