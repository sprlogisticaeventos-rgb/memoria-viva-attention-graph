from __future__ import annotations

import unittest
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path

from memoria_viva.attention import compute_attention_rankings, load_attention_feature_policy
from memoria_viva.canonical import to_plain_json_value
from memoria_viva.fixtures import FixtureBundleLoader
from memoria_viva.oracle import compare_ordinal_oracle
from memoria_viva.snapshot import build_snapshot_t0
from memoria_viva.transition import apply_canonical_trigger


ROOT = Path(__file__).resolve().parents[1]


class OrdinalOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.loader = FixtureBundleLoader(ROOT)
        cls.runtime = cls.loader.load_runtime_bundle()
        cls.t0 = build_snapshot_t0(cls.runtime)
        cls.t1 = apply_canonical_trigger(cls.runtime, cls.t0)
        cls.feature_policy = load_attention_feature_policy(ROOT)
        cls.before, cls.after = compute_attention_rankings(
            cls.runtime, cls.t0, cls.t1, cls.feature_policy
        )
        cls.oracle = cls.loader.load_oracle_bundle(cls.runtime)

    def test_before_comparison_passes(self) -> None:
        result = compare_ordinal_oracle(
            self.before, self.oracle.expected_ranking_before
        )
        self.assertEqual(result.status, "PASS")
        self.assertIsNone(result.first_divergence)
        self.assertEqual(result.issues, ())

    def test_after_comparison_passes(self) -> None:
        result = compare_ordinal_oracle(
            self.after,
            self.oracle.expected_ranking_after,
            previous_computed=self.before,
        )
        self.assertEqual(result.status, "PASS")
        self.assertIsNone(result.first_divergence)
        self.assertEqual(result.issues, ())

    def test_generic_missing_component_remains_blocked(self) -> None:
        plain_ranking = to_plain_json_value(self.before.ranking)
        blocked_item = plain_ranking["items"].pop(0)
        item_id = blocked_item["attention_item_id"]
        synthetic_result = replace(
            self.before,
            ranking=plain_ranking,
            blocked_items=(
                {
                    "attention_item_id": item_id,
                    "subject_ref": blocked_item["subject_ref"],
                    "status": "NEEDS_CONFIRMATION",
                    "missing_components": ("downstream_impact",),
                    "evidence_refs": blocked_item["evidence_refs"],
                    "evidence_gaps": ("Synthetic missing impact signal.",),
                    "ranking_band": self.before.ranking_bands[item_id],
                    "effective_due_time": self.before.effective_due_times[item_id],
                    "approval_requirement": self.before.approval_requirements[item_id],
                    "uncertainty": blocked_item["uncertainty"],
                    "explanation": "Synthetic BLOCKED comparator case.",
                },
            ),
        )
        result = compare_ordinal_oracle(
            synthetic_result, self.oracle.expected_ranking_before
        )
        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("downstream_impact", result.first_divergence)

    def test_comparator_can_pass_a_fully_deterministic_structured_oracle(self) -> None:
        expected = _structured_oracle_for(self.before, "T0")
        result = compare_ordinal_oracle(self.before, expected)
        self.assertEqual(result.status, "PASS")
        self.assertIsNone(result.first_divergence)

    def test_valid_rank_contradiction_fails(self) -> None:
        expected = _structured_oracle_for(self.before, "T0")
        expected["expected_ordered_items"][0]["expected_rank"] = 2
        result = compare_ordinal_oracle(self.before, expected)
        self.assertEqual(result.status, "FAIL")
        self.assertTrue(
            any(issue.error_code == "EXPECTED_RANK_MISMATCH" for issue in result.issues)
        )

    def test_stronger_unstructured_uncertainty_requires_human_review(self) -> None:
        expected = _structured_oracle_for(self.before, "T0")
        expected["expected_ordered_items"][0]["expected_uncertainty"] = []
        result = compare_ordinal_oracle(self.before, expected)
        self.assertEqual(result.status, "HUMAN_REVIEW_REQUIRED")

    def test_oracle_contains_no_numeric_production_score(self) -> None:
        for expected in (
            self.oracle.expected_ranking_before,
            self.oracle.expected_ranking_after,
        ):
            keys = _all_keys(expected)
            self.assertFalse(
                {"score", "previous_score", "score_delta", "component_breakdown"}
                & keys
            )

    def test_modified_oracle_does_not_change_computed_ranking(self) -> None:
        before_bytes = self.before.canonical_bytes()
        modified = to_plain_json_value(self.oracle.expected_ranking_before)
        modified["expected_ordered_items"].reverse()
        comparison = compare_ordinal_oracle(self.before, modified)
        self.assertEqual(comparison.status, "FAIL")
        self.assertEqual(before_bytes, self.before.canonical_bytes())

    def test_comparator_result_is_deterministic_and_immutable(self) -> None:
        first = compare_ordinal_oracle(
            self.after,
            self.oracle.expected_ranking_after,
            previous_computed=self.before,
        )
        second = compare_ordinal_oracle(
            self.after,
            self.oracle.expected_ranking_after,
            previous_computed=self.before,
        )
        self.assertEqual(first.canonical_bytes(), second.canonical_bytes())
        with self.assertRaises((AttributeError, TypeError)):
            first.status = "PASS"  # type: ignore[misc]


def _structured_oracle_for(result, snapshot_role: str) -> dict:
    items = []
    for item in result.ranking["items"]:
        items.append(
            {
                "expected_rank": item["rank"],
                "stable_attention_item_reference": item["attention_item_id"],
                "ordinal_invariants": [],
                "expected_score_direction": "UNCHANGED",
                "evidence_refs": ["EV-HUMAN-EXPECTATION"],
                "expected_protected_references": list(item["protected_commitment_refs"]),
                "expected_displaced_references": list(item["displaced_commitment_refs"]),
                "expected_uncertainty": list(item["uncertainty"]),
                "expected_approval_requirement": result.approval_requirements[
                    item["attention_item_id"]
                ],
                "approval_authority": None,
                "explanation": "Structured deterministic comparator test.",
            }
        )
    return {
        "oracle_id": "ORACLE-TEST",
        "snapshot_role": snapshot_role,
        "expected_ordered_items": items,
    }


def _all_keys(value) -> set[str]:
    if isinstance(value, Mapping):
        return set(value) | {
            key for child in value.values() for key in _all_keys(child)
        }
    if isinstance(value, (list, tuple)):
        return {key for child in value for key in _all_keys(child)}
    return set()


if __name__ == "__main__":
    unittest.main()
