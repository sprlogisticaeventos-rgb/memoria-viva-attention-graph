from __future__ import annotations

import inspect
import unittest
from dataclasses import replace
from pathlib import Path

from memoria_viva.attention import compute_attention_rankings, load_attention_feature_policy
from memoria_viva.canonical import canonical_json_bytes, to_plain_json_value
from memoria_viva.contracts import SchemaRegistry
from memoria_viva.fixtures import FixtureBundleLoader
from memoria_viva.graph_delta import (
    GRAPH_DELTA_SCHEMA_ID,
    GraphDelta,
    build_graph_delta,
)
from memoria_viva.oracle import compare_graph_delta_oracle
from memoria_viva.snapshot import build_snapshot_t0
from memoria_viva.transition import apply_canonical_trigger


ROOT = Path(__file__).resolve().parents[1]


class GraphDeltaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = SchemaRegistry(ROOT / "schemas")
        cls.loader = FixtureBundleLoader(ROOT, schema_registry=cls.registry)
        cls.runtime = cls.loader.load_runtime_bundle()
        cls.t0 = build_snapshot_t0(cls.runtime)
        cls.t1 = apply_canonical_trigger(cls.runtime, cls.t0)
        cls.feature_policy = load_attention_feature_policy(
            ROOT, schema_registry=cls.registry
        )
        cls.before, cls.after = compute_attention_rankings(
            cls.runtime, cls.t0, cls.t1, cls.feature_policy
        )
        cls.graph_delta = build_graph_delta(
            cls.runtime, cls.t0, cls.t1, cls.before, cls.after
        )
        cls.oracle = cls.loader.load_oracle_bundle(cls.runtime)

    def test_graph_delta_validates_and_contains_all_categories(self) -> None:
        self.registry.validate(
            GRAPH_DELTA_SCHEMA_ID,
            self.graph_delta.to_plain_json(),
            instance_path="memory/graph-delta",
            object_id=self.graph_delta.graph_delta_id,
        )
        self.assertEqual(
            {change["category"] for change in self.graph_delta.changes},
            {
                "ADDED",
                "UPDATED",
                "CONFLICTED",
                "DISPLACED",
                "PROTECTED",
                "REQUIRES_CONFIRMATION",
                "UNCHANGED",
            },
        )

    def test_relationship_changes_are_exactly_the_approved_semantics(self) -> None:
        actual = {
            (
                change["category"],
                semantics["relationship_type"],
                semantics["from_id"],
                semantics["to_id"],
            )
            for change in self.graph_delta.changes
            if change["affected_kind"] == "RELATIONSHIP"
            for semantics in (
                self.graph_delta.relationship_semantics[
                    change["affected_relationship_id"]
                ],
            )
        }
        self.assertEqual(
            actual,
            {
                ("ADDED", "depends_on", "CMT-02", "CMT-01"),
                ("CONFLICTED", "conflicts_with", "CMT-01", "CMT-04"),
                ("CONFLICTED", "conflicts_with", "CMT-02", "CMT-T0-06"),
                ("CONFLICTED", "conflicts_with", "CMT-02", "CMT-T0-09"),
                ("DISPLACED", "displaces", "CMT-01", "CMT-04"),
            },
        )

    def test_conditional_displacement_preserves_complete_nonexecution(self) -> None:
        change = _one_change(self.graph_delta, "DISPLACED", "RELATIONSHIP")
        self.assertEqual(change["conditionality"], "CONDITIONAL")
        self.assertEqual(change["actual_execution_state"], "UNKNOWN")
        self.assertEqual(change["condition_state"], "PENDING")
        self.assertTrue(change["condition"])
        self.assertTrue(change["opportunity_cost"])
        self.assertTrue(change["repair_requirement"])
        self.assertEqual(change["authority_scope"], "FOUNDER")
        self.assertTrue(change["uncertainty"])

    def test_confirmation_unchanged_and_retained_semantics(self) -> None:
        confirmations = {
            change["affected_ref"]["entity_id"]
            for change in self.graph_delta.changes
            if change["category"] == "REQUIRES_CONFIRMATION"
        }
        self.assertEqual(confirmations, {"CMT-05", "CMT-T0-01"})
        unchanged = {
            change["affected_ref"]["entity_id"]: change
            for change in self.graph_delta.changes
            if change["category"] == "UNCHANGED"
        }
        self.assertEqual(set(unchanged), {"CMT-03", "CMT-T0-07", "CMT-T0-08"})
        self.assertIn("VISIBLE", unchanged["CMT-03"]["expected_new_state"]["state_label"])
        for candidate_id in ("CMT-T0-07", "CMT-T0-08"):
            self.assertIn(
                "EXCLUDED_BUT_RETAINED",
                unchanged[candidate_id]["expected_new_state"]["state_label"],
            )

    def test_every_change_has_deterministic_provenance(self) -> None:
        required = {
            "change_id",
            "category",
            "affected_kind",
            "previous_state",
            "expected_new_state",
            "actual_execution_state",
            "conditionality",
            "condition_state",
            "condition",
            "reason",
            "opportunity_cost",
            "repair_requirement",
            "authority_scope",
            "evidence_refs",
            "confidence",
            "uncertainty",
            "explanation",
            "creator_type",
            "ontology_version",
            "recorded_at",
        }
        for change in self.graph_delta.changes:
            self.assertTrue(required.issubset(change))
            self.assertEqual(change["creator_type"], "DETERMINISTIC_RULE")
            self.assertTrue(change["evidence_refs"])
            self.assertEqual(change["ontology_version"], "1.0.0")
            self.assertEqual(change["recorded_at"], self.t1.captured_at)
        self.assertNotIn(
            "attempts_to_resolve",
            self.graph_delta.canonical_bytes().decode("utf-8"),
        )

    def test_graph_delta_has_no_oracle_dependency(self) -> None:
        import memoria_viva.graph_delta as graph_delta_module

        source = inspect.getsource(graph_delta_module)
        for forbidden in (
            "OracleBundle",
            "expected-graph-delta",
            "expected_graph_delta",
            "EV-HUMAN-EXPECTATION",
        ):
            self.assertNotIn(forbidden, source)

    def test_id_digest_and_bytes_are_stable(self) -> None:
        repeated = build_graph_delta(
            self.runtime, self.t0, self.t1, self.before, self.after
        )
        self.assertEqual(repeated.graph_delta_id, self.graph_delta.graph_delta_id)
        self.assertEqual(repeated.transition_digest, self.graph_delta.transition_digest)
        self.assertEqual(repeated.canonical_bytes(), self.graph_delta.canonical_bytes())

    def test_semantic_ranking_input_change_changes_delta_digest(self) -> None:
        changed_after = replace(
            self.after,
            ranking_digest="sha256:" + "0" * 64,
        )
        changed = build_graph_delta(
            self.runtime, self.t0, self.t1, self.before, changed_after
        )
        self.assertNotEqual(changed.graph_delta_id, self.graph_delta.graph_delta_id)
        self.assertNotEqual(changed.transition_digest, self.graph_delta.transition_digest)

    def test_expected_graph_delta_comparison_passes(self) -> None:
        comparison = compare_graph_delta_oracle(
            self.graph_delta, self.oracle.expected_graph_delta
        )
        self.assertEqual(comparison.status, "PASS")
        self.assertEqual(comparison.matched_change_count, 21)
        self.assertEqual(comparison.issues, ())

    def test_missing_expected_change_fails(self) -> None:
        expected = to_plain_json_value(self.oracle.expected_graph_delta)
        expected["changes"].pop()
        comparison = compare_graph_delta_oracle(self.graph_delta, expected)
        self.assertEqual(comparison.status, "HUMAN_REVIEW_REQUIRED")
        self.assertTrue(
            any(
                issue.error_code == "STRONGER_UNSUPPORTED_OBJECT_CHANGE"
                for issue in comparison.issues
            )
        )

    def test_missing_production_change_fails(self) -> None:
        value = self.graph_delta.to_plain_json()
        value["changes"].pop()
        value["transition_digest"] = "sha256:" + "0" * 64
        incomplete = GraphDelta(
            value=value,
            relationship_semantics=self.graph_delta.relationship_semantics,
        )
        comparison = compare_graph_delta_oracle(
            incomplete, self.oracle.expected_graph_delta
        )
        self.assertEqual(comparison.status, "FAIL")
        self.assertTrue(
            any(issue.error_code == "EXPECTED_GRAPH_CHANGE_MISSING" for issue in comparison.issues)
        )

    def test_invalid_incomplete_production_is_blocked(self) -> None:
        value = self.graph_delta.to_plain_json()
        value.pop("explanation")
        incomplete = GraphDelta(
            value=value,
            relationship_semantics=self.graph_delta.relationship_semantics,
        )
        comparison = compare_graph_delta_oracle(
            incomplete, self.oracle.expected_graph_delta
        )
        self.assertEqual(comparison.status, "BLOCKED")

    def test_stronger_executed_displacement_requires_human_review(self) -> None:
        value = self.graph_delta.to_plain_json()
        displaced = next(
            change for change in value["changes"] if change["category"] == "DISPLACED"
        )
        displaced["actual_execution_state"] = "EXECUTED"
        displaced["condition_state"] = "SATISFIED"
        stronger = GraphDelta(
            value=value,
            relationship_semantics=self.graph_delta.relationship_semantics,
        )
        comparison = compare_graph_delta_oracle(
            stronger, self.oracle.expected_graph_delta
        )
        self.assertEqual(comparison.status, "HUMAN_REVIEW_REQUIRED")

    def test_modified_oracle_never_changes_production_delta(self) -> None:
        before = self.graph_delta.canonical_bytes()
        expected = to_plain_json_value(self.oracle.expected_graph_delta)
        expected["changes"].reverse()
        compare_graph_delta_oracle(self.graph_delta, expected)
        self.assertEqual(self.graph_delta.canonical_bytes(), before)

    def test_graph_delta_is_deeply_immutable_and_projection_is_detached(self) -> None:
        with self.assertRaises(TypeError):
            self.graph_delta.value["graph_delta_id"] = "changed"
        with self.assertRaises(TypeError):
            self.graph_delta.changes[0]["category"] = "UPDATED"
        plain = self.graph_delta.to_plain_json()
        plain["changes"][0]["reason"] = "changed"
        self.assertNotEqual(plain, self.graph_delta.to_plain_json())


def _one_change(graph_delta: GraphDelta, category: str, kind: str):
    return next(
        change
        for change in graph_delta.changes
        if change["category"] == category and change["affected_kind"] == kind
    )


if __name__ == "__main__":
    unittest.main()
