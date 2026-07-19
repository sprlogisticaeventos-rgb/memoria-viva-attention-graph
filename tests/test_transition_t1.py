from __future__ import annotations

import inspect
import unittest
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from types import MappingProxyType

from memoria_viva.canonical import (
    canonical_json_bytes,
    sha256_digest,
    to_plain_json_value,
)
from memoria_viva.contracts import SchemaRegistry
from memoria_viva.fixtures import FixtureBundleLoader
from memoria_viva.snapshot import (
    SNAPSHOT_SCHEMA_ID,
    build_snapshot_t0,
    snapshot_state_projection,
)
from memoria_viva.transition import (
    MV_TRIGGER_TRANSITION_V1,
    TRANSITION_POLICY_ID,
    TRANSITION_POLICY_VERSION,
    TransitionValidationError,
    apply_canonical_trigger,
)


ROOT = Path(__file__).resolve().parents[1]


class TransitionT1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = SchemaRegistry(ROOT / "schemas")
        cls.loader = FixtureBundleLoader(ROOT, schema_registry=cls.registry)
        cls.runtime = cls.loader.load_runtime_bundle()
        cls.t0 = build_snapshot_t0(cls.runtime)
        cls.t1 = apply_canonical_trigger(cls.runtime, cls.t0)

    def test_transition_contract_identity_is_explicit(self) -> None:
        self.assertEqual(MV_TRIGGER_TRANSITION_V1, "MV_TRIGGER_TRANSITION_V1")
        self.assertEqual(TRANSITION_POLICY_ID, "mv.canonical-trigger-transition")
        self.assertEqual(TRANSITION_POLICY_VERSION, "1.0.0")

    def test_transition_accepts_runtime_and_snapshot_only(self) -> None:
        self.assertEqual(
            tuple(inspect.signature(apply_canonical_trigger).parameters),
            ("runtime_bundle", "snapshot_t0"),
        )
        with self.assertRaises(TransitionValidationError) as runtime_error:
            apply_canonical_trigger(object(), self.t0)  # type: ignore[arg-type]
        self.assertEqual(
            runtime_error.exception.issues[0].error_code,
            "INVALID_RUNTIME_BUNDLE_TYPE",
        )
        with self.assertRaises(TransitionValidationError) as snapshot_error:
            apply_canonical_trigger(self.runtime, object())  # type: ignore[arg-type]
        self.assertEqual(
            snapshot_error.exception.issues[0].error_code,
            "INVALID_SNAPSHOT_TYPE",
        )

    def test_transition_source_has_no_human_oracle_dependency(self) -> None:
        source = (ROOT / "src" / "memoria_viva" / "transition.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("OracleBundle", source)
        self.assertNotIn("expected-ranking", source)
        self.assertNotIn("expected-graph-delta", source)

    def test_invalid_non_t0_snapshot_is_rejected(self) -> None:
        invalid = replace(self.t0, temporal_role="T1")
        with self.assertRaises(TransitionValidationError) as caught:
            apply_canonical_trigger(self.runtime, invalid)
        self.assertIn(
            "INVALID_T0_ROLE",
            {issue.error_code for issue in caught.exception.issues},
        )

    def test_mismatched_runtime_input_digest_is_rejected(self) -> None:
        changed_runtime = _runtime_with_event_summary(
            self.runtime,
            f"{self.runtime.source_event['summary']} Deterministic test change.",
        )
        with self.assertRaises(TransitionValidationError) as caught:
            apply_canonical_trigger(changed_runtime, self.t0)
        self.assertIn(
            "RUNTIME_INPUT_DIGEST_MISMATCH",
            {issue.error_code for issue in caught.exception.issues},
        )

    def test_t1_validates_against_snapshot_schema(self) -> None:
        self.registry.validate(
            SNAPSHOT_SCHEMA_ID,
            self.t1.to_plain_json(),
            instance_path="memory/snapshot-t1",
            object_id=self.t1.snapshot_id,
        )

    def test_t1_identity_and_chain_are_deterministic(self) -> None:
        self.assertEqual(self.t1.snapshot_id, "SNAPSHOT-T1-8280b33463a480998d3e")
        self.assertFalse(self.t1.is_initial)
        self.assertEqual(self.t1.previous_snapshot_id, self.t0.snapshot_id)
        self.assertEqual(self.t1.snapshot_version, self.t0.snapshot_version + 1)
        self.assertEqual(self.t1.temporal_role, "T1")

    def test_t1_time_is_trigger_received_at(self) -> None:
        self.assertEqual(self.t1.captured_at, self.runtime.source_event["received_at"])
        self.assertEqual(self.t1.captured_at, self.t0.captured_at)
        self.assertIsNone(self.runtime.source_event["occurred_at"])
        self.assertNotEqual(
            self.runtime.source_event["received_at"],
            self.runtime.source_event["deadline_at"],
        )

    def test_exactly_one_trigger_is_applied_and_followups_are_absent(self) -> None:
        self.assertEqual(
            self.t1.source_event_refs,
            (self.runtime.source_event["source_event_id"],),
        )
        self.assertEqual(self.runtime.source_event["event_role"], "TRIGGER")
        self.assertIsNone(self.runtime.source_event["follow_up_to"])
        self.assertEqual(self.runtime.source_event["authority_scope"], "COMMUNICATION_EVIDENCE_ONLY")

    def test_t0_and_runtime_are_not_mutated(self) -> None:
        t0_before = self.t0.canonical_bytes()
        runtime_before = canonical_json_bytes(_runtime_semantics(self.runtime))
        warnings_before = self.runtime.warnings
        apply_canonical_trigger(self.runtime, self.t0)
        self.assertEqual(self.t0.canonical_bytes(), t0_before)
        self.assertEqual(
            canonical_json_bytes(_runtime_semantics(self.runtime)), runtime_before
        )
        self.assertEqual(self.runtime.warnings, warnings_before)

    def test_exact_three_goals_remain_without_hackathon_goal(self) -> None:
        goal_ids = tuple(goal["goal_id"] for goal in self.t1.goals)
        self.assertEqual(goal_ids, ("GC-01", "GC-02", "GC-03"))
        self.assertNotIn("hackathon", " ".join(goal_ids).lower())

    def test_trigger_created_commitments_appear_only_in_t1(self) -> None:
        t0_ids = tuple(item["commitment_id"] for item in self.t0.commitments)
        t1_ids = tuple(item["commitment_id"] for item in self.t1.commitments)
        self.assertEqual(t0_ids, ("CMT-03", "CMT-04", "CMT-05"))
        self.assertEqual(
            t1_ids,
            ("CMT-01", "CMT-02", "CMT-03", "CMT-04", "CMT-05"),
        )
        self.assertEqual(len(t1_ids), len(set(t1_ids)))

    def test_trigger_created_commitment_dimensions_are_preserved(self) -> None:
        commitments = _commitment_index(self.t1)
        for commitment_id in ("CMT-01", "CMT-02"):
            item = commitments[commitment_id]
            self.assertEqual(item["lifecycle_status"], "ACTIVE")
            self.assertEqual(item["mobility_policy"], "PROTECTED")
            self.assertEqual(item["eligibility_state"], "ELIGIBLE")
            self.assertEqual(item["authority_mode"], "FOUNDER")
            self.assertEqual(item["protection_state"], "PROTECTED")
            self.assertNotEqual(item["execution_state"], "EXECUTED")

    def test_all_calendar_candidates_are_preserved(self) -> None:
        active = {
            ref["entity_id"]
            for ref in self.t1.active_object_refs
            if ref["entity_type"] == "CalendarCandidate"
        }
        excluded = {
            item["object_ref"]["entity_id"]
            for item in self.t1.excluded_but_retained_objects
        }
        self.assertEqual(len(active), 8)
        self.assertEqual(excluded, {"CMT-T0-07", "CMT-T0-08"})
        self.assertEqual(
            active | excluded,
            set(self.runtime.indexes.calendar_candidates),
        )
        self.assertEqual(
            self.t1.excluded_but_retained_objects,
            self.t0.excluded_but_retained_objects,
        )

    def test_only_approved_trigger_constraints_are_members(self) -> None:
        constraints = tuple(item["constraint_id"] for item in self.t1.constraints)
        self.assertEqual(
            constraints,
            ("D-0", "C-PUBLIC-ARTIFACT-REQUIREMENTS"),
        )
        statuses = {item["constraint_id"]: item["status"] for item in self.t1.constraints}
        self.assertEqual(statuses["D-0"], "ACTIVE")
        self.assertEqual(statuses["C-PUBLIC-ARTIFACT-REQUIREMENTS"], "PROPOSED")
        self.assertTrue(
            all(
                item["authority_scope"] == "COMMUNICATION_EVIDENCE_ONLY"
                for item in self.t1.constraints
            )
        )

    def test_build_first_dependency_is_materialized(self) -> None:
        relationship = _relationship(
            self.t1,
            "depends_on",
            "CMT-02",
            "CMT-01",
        )
        self.assertEqual(relationship["creator_type"], "DETERMINISTIC_RULE")

    def test_both_trigger_commitments_are_constrained_by_d0(self) -> None:
        for commitment_id in ("CMT-01", "CMT-02"):
            _relationship(self.t1, "constrained_by", commitment_id, "D-0")

    def test_cmt_01_conflicts_with_cmt_04(self) -> None:
        _relationship(self.t1, "conflicts_with", "CMT-01", "CMT-04")

    def test_cmt_01_displacement_is_conditional_and_not_executed(self) -> None:
        relationship = _relationship(self.t1, "displaces", "CMT-01", "CMT-04")
        cmt_04 = _commitment_index(self.t1)["CMT-04"]
        self.assertEqual(cmt_04["conditionality"], "CONDITIONAL")
        self.assertEqual(cmt_04["condition_state"], "PENDING")
        self.assertEqual(cmt_04["execution_state"], "UNKNOWN")
        self.assertEqual(cmt_04["displaced_by_refs"], ())
        self.assertIn("not executed movement", relationship["explanation"])
        self.assertIn("Execution remains UNKNOWN", relationship["explanation"])
        self.assertIn(cmt_04["condition"], relationship["explanation"])
        self.assertIn(cmt_04["repair_requirement"], relationship["explanation"])
        self.assertIn(cmt_04["displacement_cost"]["summary"], relationship["explanation"])
        self.assertIn("Authority: FOUNDER", relationship["explanation"])

    def test_cmt_05_remains_confirmation_required(self) -> None:
        cmt_05 = _commitment_index(self.t1)["CMT-05"]
        self.assertEqual(cmt_05["mobility_policy"], "NEEDS_CONFIRMATION")
        self.assertEqual(cmt_05["authority_mode"], "JOINT")
        self.assertEqual(cmt_05["approval_requirement"], "PENDING")
        self.assertEqual(cmt_05["execution_state"], "NOT_EXECUTED")

    def test_only_explicit_flexible_capacity_conflicts_are_materialized(self) -> None:
        targets = {
            item["to_ref"]["entity_id"]
            for item in self.t1.relationships
            if item["relationship_type"] == "conflicts_with"
            and item["from_ref"]["entity_id"] == "CMT-02"
        }
        self.assertEqual(targets, {"CMT-T0-06", "CMT-T0-09"})
        for target in targets:
            candidate = self.runtime.indexes.calendar_candidates[target]
            self.assertEqual(candidate["mobility_policy"], "FLEXIBLE")
            self.assertGreaterEqual(
                candidate["scheduled_start"], self.runtime.source_event["received_at"]
            )
            self.assertLessEqual(
                candidate["scheduled_end"], self.runtime.source_event["deadline_at"]
            )

    def test_coexistence_alone_does_not_create_conflict(self) -> None:
        conflict_pairs = {
            (item["from_ref"]["entity_id"], item["to_ref"]["entity_id"])
            for item in self.t1.relationships
            if item["relationship_type"] == "conflicts_with"
        }
        self.assertEqual(
            conflict_pairs,
            {
                ("CMT-01", "CMT-04"),
                ("CMT-02", "CMT-T0-06"),
                ("CMT-02", "CMT-T0-09"),
            },
        )

    def test_relationship_vocabulary_and_provenance_are_complete(self) -> None:
        required = {
            "relationship_id",
            "relationship_type",
            "from_ref",
            "to_ref",
            "epistemic_state",
            "confidence",
            "evidence_refs",
            "created_by",
            "creator_type",
            "explanation",
            "created_at",
            "ontology_version",
            "status",
            "supersedes_relationship_id",
        }
        self.assertEqual(len(self.t1.relationships), 7)
        self.assertEqual(
            len({item["relationship_id"] for item in self.t1.relationships}),
            7,
        )
        for item in self.t1.relationships:
            self.assertEqual(set(item), required)
            self.assertTrue(item["evidence_refs"])
            self.assertEqual(item["creator_type"], "DETERMINISTIC_RULE")
            self.assertTrue(item["created_by"].startswith("MVTR-"))
            self.assertEqual(item["created_at"], self.t1.captured_at)
            self.assertEqual(item["ontology_version"], "1.0.0")
            self.assertIn("Uncertainty:", item["explanation"])
        self.assertNotIn(
            "attempts_to_resolve",
            {item["relationship_type"] for item in self.t1.relationships},
        )

    def test_capacity_ranking_and_graph_delta_remain_uncomputed(self) -> None:
        self.assertEqual(self.t1.capacity_state["availability"], "UNKNOWN")
        self.assertEqual(self.t1.capacity_state["epistemic_state"], "uncertain")
        self.assertFalse(
            self.t1.capacity_state["calendar_absence_implies_availability"]
        )
        self.assertIsNone(self.t1.attention_ranking_id)
        self.assertIsNone(self.t1.graph_delta_id)
        self.assertFalse(
            {"score", "component_breakdown", "weighted_value"}
            & _all_keys(self.t1.to_plain_json())
        )

    def test_no_goal_completion_or_publication_claim_is_created(self) -> None:
        for goal in self.t1.goals:
            self.assertNotEqual(goal["operational_lifecycle"], "COMPLETED")
            self.assertFalse(
                goal["completion_authority"]["artifact_existence_sufficient"]
            )
            self.assertNotEqual(
                goal["completion_authority"]["completion_validation_state"],
                "PASSED",
            )
        self.assertEqual(self.t1.privacy_classification, "SANITIZED_PRIVATE")
        self.assertEqual(self.t1.privacy_review_state, "NOT_REVIEWED")
        self.assertEqual(self.t1.review_state, "NOT_REVIEWED")
        self.assertEqual(
            {
                item["approval_state"]
                for item in self.runtime.privacy_manifest["publication_approvals"]
            },
            {"PENDING"},
        )

    def test_no_t0_object_or_evidence_silently_disappears(self) -> None:
        t0_active = {
            (item["entity_type"], item["entity_id"])
            for item in self.t0.active_object_refs
        }
        t1_active = {
            (item["entity_type"], item["entity_id"])
            for item in self.t1.active_object_refs
        }
        self.assertTrue(t0_active.issubset(t1_active))
        self.assertTrue(set(self.t0.evidence_refs).issubset(self.t1.evidence_refs))
        self.assertEqual(self.t0.goals, self.t1.goals)
        self.assertEqual(
            self.t0.commitments,
            tuple(_commitment_index(self.t1)[item["commitment_id"]] for item in self.t0.commitments),
        )

    def test_same_input_produces_identical_t1(self) -> None:
        repeated = apply_canonical_trigger(self.runtime, self.t0)
        self.assertEqual(self.t1.snapshot_id, repeated.snapshot_id)
        self.assertEqual(self.t1.state_digest, repeated.state_digest)
        self.assertEqual(self.t1.canonical_bytes(), repeated.canonical_bytes())
        self.assertEqual(self.t1.active_object_refs, repeated.active_object_refs)
        self.assertEqual(self.t1.relationships, repeated.relationships)

    def test_semantic_input_change_changes_t1_digest(self) -> None:
        changed_runtime = _runtime_with_event_summary(
            self.runtime,
            f"{self.runtime.source_event['summary']} Deterministic semantic change.",
        )
        changed_t0 = build_snapshot_t0(changed_runtime)
        changed_t1 = apply_canonical_trigger(changed_runtime, changed_t0)
        self.assertNotEqual(self.t1.snapshot_id, changed_t1.snapshot_id)
        self.assertNotEqual(self.t1.state_digest, changed_t1.state_digest)
        self.assertNotEqual(self.t1.canonical_bytes(), changed_t1.canonical_bytes())

    def test_t1_digest_covers_every_material_transition_dimension(self) -> None:
        baseline = snapshot_state_projection(self.t1)
        mutations = {
            "active commitment membership": lambda value: value["commitments"].pop(),
            "active constraint membership": lambda value: value["constraints"].pop(),
            "relationship semantics": lambda value: value["relationships"][0].update(
                {"explanation": "changed"}
            ),
            "predecessor": lambda value: value.update(
                {"previous_snapshot_id": "SNAPSHOT-T0-CHANGED"}
            ),
            "evidence": lambda value: value["evidence_refs"].pop(),
            "privacy": lambda value: value.update(
                {"privacy_review_state": "IN_REVIEW"}
            ),
            "uncertainty": lambda value: value["capacity_state"]["uncertainty"].append(
                "changed"
            ),
        }
        baseline_digest = sha256_digest(baseline)
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                changed = to_plain_json_value(baseline)
                mutate(changed)
                self.assertNotEqual(sha256_digest(changed), baseline_digest)

    def test_t1_interface_is_deeply_immutable(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            self.t1.snapshot_id = "changed"  # type: ignore[misc]
        with self.assertRaises(TypeError):
            self.t1.commitments[0]["title"] = "changed"  # type: ignore[index]
        with self.assertRaises(TypeError):
            self.t1.relationships[0]["status"] = "deactivated"  # type: ignore[index]

    def test_plain_projection_is_detached(self) -> None:
        projection = self.t1.to_plain_json()
        projection["commitments"][0]["title"] = "changed"
        projection["relationships"][0]["status"] = "deactivated"
        self.assertNotEqual(self.t1.commitments[0]["title"], "changed")
        self.assertEqual(self.t1.relationships[0]["status"], "active")

    def test_transition_writes_nothing_under_runs(self) -> None:
        runs = ROOT / "runs"
        before = tuple(sorted(path.relative_to(runs) for path in runs.rglob("*")))
        apply_canonical_trigger(self.runtime, self.t0)
        after = tuple(sorted(path.relative_to(runs) for path in runs.rglob("*")))
        self.assertEqual(before, after)


def _relationship(snapshot, relationship_type: str, from_id: str, to_id: str):
    matches = [
        item
        for item in snapshot.relationships
        if item["relationship_type"] == relationship_type
        and item["from_ref"]["entity_id"] == from_id
        and item["to_ref"]["entity_id"] == to_id
    ]
    if len(matches) != 1:
        raise AssertionError(
            f"expected one {relationship_type} relationship {from_id}->{to_id}, got {len(matches)}"
        )
    return matches[0]


def _commitment_index(snapshot):
    return {item["commitment_id"]: item for item in snapshot.commitments}


def _runtime_with_event_summary(runtime, summary: str):
    event = to_plain_json_value(runtime.source_event)
    event["summary"] = summary
    source_events = MappingProxyType({event["source_event_id"]: event})
    indexes = replace(runtime.indexes, source_events=source_events)
    return replace(runtime, source_event=MappingProxyType(event), indexes=indexes)


def _runtime_semantics(runtime):
    return {
        "public_goal_set": runtime.public_goal_set,
        "calendar_t0": runtime.calendar_t0,
        "evidence_catalog": runtime.evidence_catalog,
        "operational_commitments": runtime.operational_commitments,
        "constraints_catalog": runtime.constraints_catalog,
        "source_event": runtime.source_event,
        "privacy_manifest": runtime.privacy_manifest,
        "attention_policy": runtime.attention_policy,
    }


def _all_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(key)
            keys.update(_all_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_all_keys(child))
    return keys


if __name__ == "__main__":
    unittest.main()
