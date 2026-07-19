"""Deterministic immutable RunRecord construction for in-memory Replay Mode."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .attention import AttentionRankingResult
from .canonical import canonical_json_bytes, sha256_digest, sha256_hex, to_plain_json_value
from .contracts import SchemaRegistry
from .fixtures import RuntimeBundle
from .graph_delta import GraphDelta
from .oracle import GraphDeltaComparison, OracleComparison
from .snapshot import Snapshot, runtime_input_bundle_digest
from .transition import (
    MV_TRIGGER_TRANSITION_V1,
    TRANSITION_POLICY_ID,
    TRANSITION_POLICY_VERSION,
)


RUN_RECORD_SCHEMA_ID = (
    "urn:memoria-viva:attention-graph:schema:run-record:1.0.0"
)
RUN_RECORD_CONTRACT = "MV_RUN_RECORD_V1"


@dataclass(frozen=True)
class RunRecord:
    """Schema-valid receipt with a detached deterministic record digest."""

    value: Mapping[str, Any]
    run_digest: str

    @property
    def run_id(self) -> str:
        return self.value["run_id"]

    def to_plain_json(self) -> dict[str, Any]:
        plain = to_plain_json_value(self.value)
        if not isinstance(plain, dict):
            raise TypeError("RunRecord must project to a JSON object")
        return plain

    def canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.value)


def build_run_record(
    runtime_bundle: RuntimeBundle,
    feature_policy: Mapping[str, Any],
    snapshot_t0: Snapshot,
    snapshot_t1: Snapshot,
    ranking_before: AttentionRankingResult,
    ranking_after: AttentionRankingResult,
    graph_delta: GraphDelta,
    ranking_before_comparison: OracleComparison,
    ranking_after_comparison: OracleComparison,
    graph_delta_comparison: GraphDeltaComparison,
) -> RunRecord:
    """Receipt production artifacts and completed oracle comparisons.

    The RunRecord itself is intentionally excluded from ``output_artifacts``
    and from the replay-output digest, preventing a self-reference cycle.
    """

    runtime_digest = runtime_input_bundle_digest(runtime_bundle)
    base_policy = runtime_bundle.attention_policy
    base_policy_digest = sha256_digest(base_policy)
    feature_policy_digest = sha256_digest(feature_policy)
    transition_digest = sha256_digest(
        {
            "transition_contract": MV_TRIGGER_TRANSITION_V1,
            "transition_policy_id": TRANSITION_POLICY_ID,
            "transition_policy_version": TRANSITION_POLICY_VERSION,
        }
    )
    input_artifacts = [
        _artifact(
            runtime_bundle.privacy_manifest["fixture_identity"]["artifact_id"],
            runtime_bundle.privacy_manifest["fixture_identity"]["artifact_version"],
            runtime_digest,
        ),
        _artifact(base_policy["policy_id"], base_policy["version"], base_policy_digest),
        _artifact(
            feature_policy["policy_id"],
            feature_policy["version"],
            feature_policy_digest,
        ),
        _artifact(
            TRANSITION_POLICY_ID,
            TRANSITION_POLICY_VERSION,
            transition_digest,
        ),
        _artifact(
            ranking_before_comparison.oracle_id,
            ranking_before_comparison.oracle_version,
            ranking_before_comparison.oracle_digest,
        ),
        _artifact(
            ranking_after_comparison.oracle_id,
            ranking_after_comparison.oracle_version,
            ranking_after_comparison.oracle_digest,
        ),
        _artifact(
            graph_delta_comparison.oracle_id,
            graph_delta_comparison.oracle_version,
            graph_delta_comparison.oracle_digest,
        ),
    ]
    input_artifacts = sorted(input_artifacts, key=lambda item: item["artifact_id"])
    replay_input_identity = _artifact(
        "REPLAY-INPUT-BUNDLE",
        "1.0.0",
        sha256_digest(input_artifacts),
    )

    output_artifacts = [
        _artifact(snapshot_t0.snapshot_id, str(snapshot_t0.snapshot_version), snapshot_t0.state_digest),
        _artifact(
            ranking_before.ranking["attention_ranking_id"],
            str(ranking_before.ranking["ranking_version"]),
            ranking_before.ranking_digest,
        ),
        _artifact(snapshot_t1.snapshot_id, str(snapshot_t1.snapshot_version), snapshot_t1.state_digest),
        _artifact(
            ranking_after.ranking["attention_ranking_id"],
            str(ranking_after.ranking["ranking_version"]),
            ranking_after.ranking_digest,
        ),
        _artifact(
            graph_delta.graph_delta_id,
            str(graph_delta.value["graph_delta_version"]),
            graph_delta.transition_digest,
        ),
    ]
    output_artifacts = sorted(output_artifacts, key=lambda item: item["artifact_id"])
    replay_output_identity = _artifact(
        "REPLAY-OUTPUT-BUNDLE",
        "1.0.0",
        sha256_digest(output_artifacts),
    )

    comparison_projection = {
        "ranking_before": ranking_before_comparison.to_plain_json(),
        "ranking_after": ranking_after_comparison.to_plain_json(),
        "graph_delta": graph_delta_comparison.to_plain_json(),
    }
    run_identity_projection = {
        "contract": RUN_RECORD_CONTRACT,
        "replay_input_identity": replay_input_identity,
        "replay_output_identity": replay_output_identity,
        "comparisons": comparison_projection,
    }
    run_id = f"RUN-REPLAY-{sha256_hex(run_identity_projection)[:20]}"

    validations = (
        _validation(
            "VALIDATION-RANKING-BEFORE-ORACLE",
            "Computed T0 attention ranking satisfies its human ordinal oracle.",
            ranking_before_comparison.status,
            ranking_before_comparison.first_divergence,
            ("EV-HUMAN-EXPECTATION",),
        ),
        _validation(
            "VALIDATION-RANKING-AFTER-ORACLE",
            "Computed T1 attention ranking satisfies its human ordinal oracle.",
            ranking_after_comparison.status,
            ranking_after_comparison.first_divergence,
            ("EV-HUMAN-EXPECTATION",),
        ),
        _validation(
            "VALIDATION-GRAPH-DELTA-ORACLE",
            "Computed GraphDelta satisfies the human semantic oracle.",
            graph_delta_comparison.status,
            graph_delta_comparison.first_divergence,
            ("EV-HUMAN-EXPECTATION",),
        ),
    )
    status = (
        "completed"
        if all(validation["status"] == "passed" for validation in validations)
        else "blocked"
        if any(validation["status"] == "blocked" for validation in validations)
        else "failed"
    )
    warnings = _run_warnings(runtime_bundle, snapshot_t1.captured_at)
    source_ids = tuple(
        sorted(
            {
                evidence["source_id"]
                for evidence in runtime_bundle.indexes.evidence.values()
            }
        )
    )
    record: dict[str, Any] = {
        "schema_version": "1.0.0",
        "run_id": run_id,
        "run_version": 1,
        "execution_mode": "REPLAY",
        "started_at": snapshot_t0.captured_at,
        "completed_at": snapshot_t1.captured_at,
        "input_artifacts": input_artifacts,
        "output_artifacts": output_artifacts,
        "replay_input_identity": replay_input_identity,
        "replay_output_identity": replay_output_identity,
        "previous_snapshot_id": snapshot_t0.snapshot_id,
        "new_snapshot_id": snapshot_t1.snapshot_id,
        "trigger_event_id": runtime_bundle.source_event["source_event_id"],
        "goal_ids": sorted(runtime_bundle.indexes.goals),
        "source_ids": list(source_ids),
        "graph_delta_id": graph_delta.graph_delta_id,
        "ranking_before_id": ranking_before.ranking["attention_ranking_id"],
        "ranking_after_id": ranking_after.ranking["attention_ranking_id"],
        "observations": [
            {
                "observation_id": "OBS-T0-T1-REPLAY",
                "summary": "The canonical trigger deterministically changes state and attention while preserving conditionality, exclusions, and UNKNOWN values.",
                "epistemic_state": "confirmed",
                "evidence_refs": ["EV-EVENT-TRIGGER", "EV-COMMITMENT-APPROVAL"],
            }
        ],
        "recommendations": [],
        "validations": list(validations),
        "warnings": list(warnings),
        "approvals": [
            {
                "approval_id": "APPROVAL-PRIVATE-FIXTURE-COMMIT",
                "approval_state": "APPROVED",
                "authority_scope": "FOUNDER",
                "evidence_refs": ["EV-GOAL-APPROVAL", "EV-COMMITMENT-APPROVAL"],
                "recorded_at": snapshot_t1.captured_at,
            },
            {
                "approval_id": "APPROVAL-HUMAN-ORACLE",
                "approval_state": "APPROVED",
                "authority_scope": "EXPLICIT_HUMAN_DECISION",
                "evidence_refs": ["EV-HUMAN-EXPECTATION"],
                "recorded_at": snapshot_t1.captured_at,
            },
            *(
                {
                    "approval_id": "APPROVAL-"
                    + approval["publication_surface"].replace("_", "-"),
                    "approval_state": approval["approval_state"],
                    "authority_scope": "FOUNDER",
                    "evidence_refs": list(approval["evidence_refs"]),
                    "recorded_at": snapshot_t1.captured_at,
                }
                for approval in runtime_bundle.privacy_manifest[
                    "publication_approvals"
                ]
            ),
        ],
        "unresolved_questions": [
            _question(
                "QUESTION-OFFICIAL-COMPLIANCE",
                "Are final official requirements and compliance independently verified?",
                ("EV-EVENT-TRIGGER",),
            ),
            _question(
                "QUESTION-CMT-04-EXECUTION",
                "Was the conditional CMT-04 displacement executed and repaired?",
                ("EV-COMMITMENT-APPROVAL",),
            ),
            _question(
                "QUESTION-CMT-05-JOINT-OUTCOME",
                "Has the CMT-05 joint-authority outcome been confirmed?",
                ("EV-COMMITMENT-APPROVAL",),
            ),
            _question(
                "QUESTION-GENERATED-OUTPUT-PUBLICATION",
                "Has this generated replay output completed publication-surface review?",
                (),
            ),
        ],
        "decision_refs": [
            {
                "reference_type": "Decision",
                "reference_id": "MV-ADR-009",
                "reference_version": None,
                "label": "Human Accelerator semantic supersession",
            },
            {
                "reference_type": "Decision",
                "reference_id": "MV-ADR-010",
                "reference_version": None,
                "label": "Bounded replay attention extraction and ranking policy",
            },
        ],
        "blocker_refs": [],
        "artifact_refs": [],
        "official_rules_verification": _not_claimed(
            "Official rules are outside communication-evidence authority and remain unverified in Replay Mode."
        ),
        "claim_states": {
            "compliance": _not_claimed("Replay does not claim official compliance."),
            "submission_completion": _not_claimed(
                "Replay does not claim submission completion."
            ),
            "goal_completion": _not_claimed(
                "Artifact existence and replay success do not establish Goal completion."
            ),
            "displacement_execution": {
                "execution_state": "UNKNOWN",
                "evidence_refs": [],
                "validation_refs": [],
                "explanation": "Executed displacement is NOT_CLAIMED; CMT-04 movement remains UNKNOWN.",
            },
        },
        "status": status,
        "schema_versions": [
            _schema_reference("snapshot", "1.0.0"),
            _schema_reference("attention-ranking", "1.0.0"),
            _schema_reference("attention-item", "1.0.0"),
            _schema_reference("graph-delta", "1.0.0"),
            _schema_reference("run-record", "1.0.0"),
            _schema_reference("attention-feature-policy", "1.0.0"),
        ],
        "ontology_version": snapshot_t1.ontology_version,
        "policy_id": base_policy["policy_id"],
        "policy_version": base_policy["version"],
        "policy_digest": base_policy_digest,
        "privacy_classification": "SANITIZED_PRIVATE",
        "privacy_review_state": "NOT_REVIEWED",
        "model_metadata": None,
    }
    _contract_registry().validate(
        RUN_RECORD_SCHEMA_ID,
        record,
        instance_path="memory/run-record",
        object_id=run_id,
    )
    run_digest = sha256_digest(record)
    return RunRecord(value=_deep_freeze(record), run_digest=run_digest)


def _run_warnings(
    runtime_bundle: RuntimeBundle,
    recorded_at: str,
) -> tuple[Mapping[str, Any], ...]:
    del recorded_at  # Warning schema has no timestamp; ordering remains deterministic.
    warnings = [
        {
            "warning_id": f"WARNING-{index:02d}-{warning.warning_code}",
            "severity": "warning",
            "code": warning.warning_code,
            "message": warning.message,
            "evidence_refs": (
                ["EV-EVENT-TRIGGER"]
                if warning.warning_code == "FINAL_COMPLIANCE_UNKNOWN"
                else []
            ),
        }
        for index, warning in enumerate(runtime_bundle.warnings, start=1)
    ]
    warnings.extend(
        (
            {
                "warning_id": "WARNING-BOUNDED-REPLAY-ONLY",
                "severity": "warning",
                "code": "BOUNDED_REPLAY_ONLY",
                "message": "The draft base policy and approved feature policy are authorized only for bounded Replay Mode, not production activation.",
                "evidence_refs": [],
            },
            {
                "warning_id": "WARNING-GENERATED-OUTPUT-NOT-REVIEWED",
                "severity": "warning",
                "code": "GENERATED_OUTPUT_NOT_REVIEWED",
                "message": "Generated replay output has not completed publication-surface privacy review.",
                "evidence_refs": [],
            },
        )
    )
    return tuple(warnings)


def _artifact(artifact_id: str, version: str | None, digest: str | None) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "artifact_version": version,
        "artifact_digest": digest,
    }


def _validation(
    validation_id: str,
    criterion: str,
    comparison_status: str,
    details: str | None,
    evidence_refs: Sequence[str],
) -> dict[str, Any]:
    status = {
        "PASS": "passed",
        "FAIL": "failed",
        "BLOCKED": "blocked",
        "HUMAN_REVIEW_REQUIRED": "blocked",
    }[comparison_status]
    return {
        "validation_id": validation_id,
        "criterion": criterion,
        "status": status,
        "details": details,
        "evidence_refs": list(evidence_refs),
    }


def _question(
    question_id: str,
    question: str,
    evidence_refs: Sequence[str],
) -> dict[str, Any]:
    return {
        "question_id": question_id,
        "question": question,
        "status": "OPEN",
        "evidence_refs": list(evidence_refs),
    }


def _not_claimed(explanation: str) -> dict[str, Any]:
    return {
        "state": "NOT_CLAIMED",
        "evidence_refs": [],
        "validation_refs": [],
        "explanation": explanation,
    }


def _schema_reference(name: str, version: str) -> dict[str, str]:
    return {
        "schema_id": f"urn:memoria-viva:attention-graph:schema:{name}:{version}",
        "schema_version": version,
    }


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
