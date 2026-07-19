from __future__ import annotations

import inspect
import unittest
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from types import MappingProxyType

from memoria_viva.canonical import canonical_json_bytes, sha256_digest, to_plain_json_value
from memoria_viva.contracts import ContractValidationError, SchemaRegistry
from memoria_viva.fixtures import FixtureBundleLoader, OracleBundle, RuntimeBundle
from memoria_viva.snapshot import (
    SNAPSHOT_SCHEMA_ID,
    SnapshotT0,
    build_snapshot_t0,
    runtime_input_bundle_digest,
    snapshot_state_projection,
)


ROOT = Path(__file__).resolve().parents[1]


class SnapshotT0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = SchemaRegistry(ROOT / "schemas")
        cls.loader = FixtureBundleLoader(ROOT, schema_registry=cls.registry)
        cls.runtime = cls.loader.load_runtime_bundle()
        cls.snapshot = build_snapshot_t0(cls.runtime)

    def test_builder_accepts_runtime_bundle_only(self) -> None:
        parameters = inspect.signature(build_snapshot_t0).parameters
        self.assertEqual(tuple(parameters), ("runtime_bundle",))
        self.assertIsInstance(self.snapshot, SnapshotT0)
        oracle = self.loader.load_oracle_bundle(self.runtime)
        self.assertIsInstance(oracle, OracleBundle)
        with self.assertRaises(TypeError):
            build_snapshot_t0(oracle)  # type: ignore[arg-type]

    def test_snapshot_validates_against_canonical_schema(self) -> None:
        self.registry.validate(
            SNAPSHOT_SCHEMA_ID,
            self.snapshot.to_plain_json(),
            instance_path="memory/snapshot-t0",
            object_id=self.snapshot.snapshot_id,
        )

    def test_initial_temporal_semantics_use_fixture_anchor(self) -> None:
        self.assertTrue(self.snapshot.is_initial)
        self.assertIsNone(self.snapshot.previous_snapshot_id)
        self.assertEqual(self.snapshot.temporal_role, "T0")
        self.assertEqual(
            self.snapshot.captured_at, self.runtime.calendar_t0["synthetic_anchor_at"]
        )
        self.assertEqual(self.snapshot.captured_at, "2030-02-10T12:00:00Z")

    def test_exact_goal_membership(self) -> None:
        self.assertEqual(
            tuple(goal["goal_id"] for goal in self.snapshot.goals),
            ("GC-01", "GC-02", "GC-03"),
        )
        self.assertTrue(
            all(goal["operational_lifecycle"] != "COMPLETED" for goal in self.snapshot.goals)
        )
        self.assertTrue(
            all(
                goal["completion_authority"]["artifact_existence_sufficient"] is False
                for goal in self.snapshot.goals
            )
        )

    def test_calendar_membership_is_eight_active_two_excluded_retained(self) -> None:
        active = tuple(
            ref["entity_id"]
            for ref in self.snapshot.active_object_refs
            if ref["entity_type"] == "CalendarCandidate"
        )
        excluded = tuple(
            item["object_ref"]["entity_id"]
            for item in self.snapshot.excluded_but_retained_objects
        )
        self.assertEqual(active, tuple(self.runtime.calendar_t0["active_ranking_candidate_refs"]))
        self.assertEqual(excluded, ("CMT-T0-07", "CMT-T0-08"))
        self.assertEqual(set(active) | set(excluded), set(self.runtime.indexes.calendar_candidates))
        self.assertTrue(
            all(item["exclusion_reason"] for item in self.snapshot.excluded_but_retained_objects)
        )

    def test_only_pre_trigger_operational_commitments_exist(self) -> None:
        commitment_ids = tuple(
            commitment["commitment_id"] for commitment in self.snapshot.commitments
        )
        self.assertEqual(commitment_ids, ("CMT-03", "CMT-04", "CMT-05"))
        self.assertNotIn("CMT-01", commitment_ids)
        self.assertNotIn("CMT-02", commitment_ids)

    def test_trigger_constraints_events_and_relationships_are_not_active(self) -> None:
        self.assertEqual(self.snapshot.constraints, ())
        self.assertEqual(self.snapshot.source_event_refs, ())
        self.assertEqual(self.snapshot.relationships, ())
        self.assertNotIn("D-0", {constraint.get("constraint_id") for constraint in self.snapshot.constraints})
        self.assertNotIn(
            "C-PUBLIC-ARTIFACT-REQUIREMENTS",
            {constraint.get("constraint_id") for constraint in self.snapshot.constraints},
        )

    def test_t0_evidence_excludes_trigger_and_oracle_evidence(self) -> None:
        self.assertNotIn("EV-EVENT-TRIGGER", self.snapshot.evidence_refs)
        self.assertNotIn("EV-HUMAN-EXPECTATION", self.snapshot.evidence_refs)
        self.assertTrue(
            {
                candidate["evidence_ref"]
                for candidate in self.runtime.indexes.calendar_candidates.values()
            }.issubset(self.snapshot.evidence_refs)
        )

    def test_capacity_remains_unknown(self) -> None:
        self.assertEqual(self.snapshot.capacity_state["availability"], "UNKNOWN")
        self.assertEqual(self.snapshot.capacity_state["epistemic_state"], "uncertain")
        self.assertFalse(
            self.snapshot.capacity_state["calendar_absence_implies_availability"]
        )

    def test_generated_output_privacy_review_remains_pending(self) -> None:
        self.assertEqual(self.snapshot.privacy_classification, "SANITIZED_PRIVATE")
        self.assertEqual(self.snapshot.privacy_review_state, "NOT_REVIEWED")
        self.assertEqual(self.snapshot.review_state, "NOT_REVIEWED")
        self.assertEqual(
            self.runtime.privacy_manifest["residual_aggregation_risk"], "LOW_MEDIUM"
        )
        self.assertEqual(
            {
                approval["approval_state"]
                for approval in self.runtime.privacy_manifest["publication_approvals"]
            },
            {"PENDING"},
        )

    def test_ranking_and_graph_delta_are_absent(self) -> None:
        self.assertIsNone(self.snapshot.attention_ranking_id)
        self.assertIsNone(self.snapshot.graph_delta_id)
        keys = _all_keys(self.snapshot.to_plain_json())
        self.assertFalse(
            {"score", "component_breakdown", "policy_digest"}.intersection(keys)
        )

    def test_oracle_values_are_not_copied(self) -> None:
        serialized = canonical_json_bytes(self.snapshot).decode("utf-8")
        self.assertNotIn("ORACLE", serialized)
        self.assertNotIn("HUMAN_EXPECTATION", serialized)
        self.assertNotIn("EV-HUMAN-EXPECTATION", serialized)

    def test_no_silent_object_loss(self) -> None:
        active_refs = {
            (ref["entity_type"], ref["entity_id"])
            for ref in self.snapshot.active_object_refs
        }
        self.assertEqual(
            {object_id for kind, object_id in active_refs if kind == "Goal"},
            set(self.runtime.indexes.goals),
        )
        self.assertEqual(
            {object_id for kind, object_id in active_refs if kind == "Commitment"},
            set(self.runtime.t0_commitment_ids),
        )
        self.assertEqual(
            set(self.runtime.indexes.commitments) - set(self.runtime.t0_commitment_ids),
            set(self.runtime.prospective_t1_commitment_ids),
        )

    def test_state_digest_excludes_only_its_own_field(self) -> None:
        projection = snapshot_state_projection(self.snapshot)
        self.assertNotIn("state_digest", projection)
        self.assertEqual(sha256_digest(projection), self.snapshot.state_digest)
        changed_digest_field = self.snapshot.to_plain_json()
        changed_digest_field["state_digest"] = "sha256:" + "0" * 64
        self.assertEqual(
            snapshot_state_projection(changed_digest_field),
            snapshot_state_projection(self.snapshot),
        )

    def test_same_runtime_bundle_is_byte_identical(self) -> None:
        second = build_snapshot_t0(self.runtime)
        self.assertEqual(self.snapshot.snapshot_id, second.snapshot_id)
        self.assertEqual(self.snapshot.state_digest, second.state_digest)
        self.assertEqual(self.snapshot.canonical_bytes(), second.canonical_bytes())
        self.assertEqual(self.snapshot.active_object_refs, second.active_object_refs)

    def test_semantic_input_change_changes_identity_and_digest(self) -> None:
        changed_calendar = to_plain_json_value(self.runtime.calendar_t0)
        changed_calendar["fixture_version"] = "1.0.1"
        changed_runtime = replace(self.runtime, calendar_t0=changed_calendar)
        changed = build_snapshot_t0(changed_runtime)
        self.assertNotEqual(
            runtime_input_bundle_digest(self.runtime),
            runtime_input_bundle_digest(changed_runtime),
        )
        self.assertNotEqual(self.snapshot.snapshot_id, changed.snapshot_id)
        self.assertNotEqual(self.snapshot.state_digest, changed.state_digest)

    def test_dictionary_insertion_order_does_not_change_snapshot(self) -> None:
        plain = to_plain_json_value(self.runtime.calendar_t0)
        reversed_calendar = MappingProxyType(dict(reversed(tuple(plain.items()))))
        reordered_runtime = replace(self.runtime, calendar_t0=reversed_calendar)
        reordered = build_snapshot_t0(reordered_runtime)
        self.assertEqual(self.snapshot.snapshot_id, reordered.snapshot_id)
        self.assertEqual(self.snapshot.state_digest, reordered.state_digest)
        self.assertEqual(self.snapshot.canonical_bytes(), reordered.canonical_bytes())

    def test_invalid_snapshot_raises_typed_contract_error(self) -> None:
        calendar = to_plain_json_value(self.runtime.calendar_t0)
        calendar["synthetic_anchor_at"] = "not-a-timestamp"
        invalid_runtime = replace(self.runtime, calendar_t0=calendar)
        with self.assertRaises(ContractValidationError) as caught:
            build_snapshot_t0(invalid_runtime)
        self.assertTrue(
            all(issue.error_code == "INVALID_INSTANCE" for issue in caught.exception.issues)
        )
        self.assertIn("/captured_at", {issue.pointer for issue in caught.exception.issues})

    def test_public_snapshot_interface_is_deeply_immutable(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            self.snapshot.snapshot_id = "changed"  # type: ignore[misc]
        with self.assertRaises(TypeError):
            self.snapshot.goals[0]["public_title"] = "changed"  # type: ignore[index]
        with self.assertRaises(TypeError):
            self.snapshot.capacity_state["availability"] = "AVAILABLE"  # type: ignore[index]

    def test_plain_projection_mutation_does_not_change_snapshot(self) -> None:
        projection = self.snapshot.to_plain_json()
        projection["goals"][0]["public_title"] = "changed"
        projection["capacity_state"]["availability"] = "AVAILABLE"
        self.assertEqual(self.snapshot.goals[0]["public_title"], "PRODUCT_VALIDATION")
        self.assertEqual(self.snapshot.capacity_state["availability"], "UNKNOWN")

    def test_snapshot_construction_writes_nothing_under_runs(self) -> None:
        runs = ROOT / "runs"
        before = tuple(sorted(path.relative_to(runs) for path in runs.rglob("*")))
        build_snapshot_t0(self.runtime)
        after = tuple(sorted(path.relative_to(runs) for path in runs.rglob("*")))
        self.assertEqual(before, after)


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
