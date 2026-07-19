from __future__ import annotations

import hashlib
import inspect
import unittest
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from unittest import mock

import memoria_viva.attention as attention_module
from memoria_viva.attention import (
    ATTENTION_ITEM_SCHEMA_ID,
    ATTENTION_RANKING_SCHEMA_ID,
    COMPONENT_IDS,
    FEATURE_POLICY_SCHEMA_ID,
    compute_attention_rankings,
    load_attention_feature_policy,
)
from memoria_viva.canonical import canonical_json_bytes, to_plain_json_value
from memoria_viva.contracts import SchemaRegistry
from memoria_viva.fixtures import FixtureBundleLoader
from memoria_viva.snapshot import build_snapshot_t0, finalize_snapshot
from memoria_viva.transition import apply_canonical_trigger


ROOT = Path(__file__).resolve().parents[1]
BASE_POLICY_SHA256 = "bdc3276016bf3a325ff2941679b6d91cc59babb044c610882825ebb590650037"


class AttentionScoringTests(unittest.TestCase):
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

    def test_feature_policy_validates_and_contains_no_weights(self) -> None:
        plain = to_plain_json_value(self.feature_policy)
        self.registry.validate(
            FEATURE_POLICY_SCHEMA_ID,
            plain,
            instance_path="config/attention-feature-policy.v1.json",
            object_id=plain["policy_id"],
        )
        self.assertEqual(plain["status"], "APPROVED_FOR_BOUNDED_REPLAY")
        self.assertEqual(plain["authorized_mode"], "REPLAY")
        self.assertEqual(plain["version"], "1.1.0")
        self.assertFalse(_contains_key(plain, {"weight", "weights"}))

    def test_base_policy_remains_draft_byte_unchanged_and_totals_one(self) -> None:
        policy_bytes = (ROOT / "config" / "attention-policy.v1.json").read_bytes()
        self.assertEqual(hashlib.sha256(policy_bytes).hexdigest(), BASE_POLICY_SHA256)
        self.assertEqual(self.runtime.attention_policy["status"], "draft")
        self.assertIsNone(self.runtime.attention_policy["effective_at"])
        self.assertEqual(
            sum(
                Decimal(str(component["weight"]))
                for component in self.runtime.attention_policy["components"]
            ),
            Decimal("1.00"),
        )

    def test_complete_items_have_six_bounded_explained_components(self) -> None:
        for result in (self.before, self.after):
            for item in result.ranking["items"]:
                components = item["component_breakdown"]
                self.assertEqual(
                    tuple(component["component_id"] for component in components),
                    COMPONENT_IDS,
                )
                for component in components:
                    self.assertGreaterEqual(component["normalized_value"], 0)
                    self.assertLessEqual(component["normalized_value"], 1)
                    self.assertTrue(component["explanation"])
                    self.assertTrue(component["evidence_refs"])

    def test_calendar_only_mobility_fallback_matrix(self) -> None:
        expected = {
            "PROTECTED": ("HIGH", Decimal("0.80")),
            "NEEDS_CONFIRMATION": ("MEDIUM_HIGH", Decimal("0.65")),
            "FLEXIBLE": ("LOW", Decimal("0.25")),
            "DISPLACEABLE": ("LOW", Decimal("0.25")),
            "CANCELABLE": ("NONE", Decimal("0.00")),
        }
        for mobility, (impact_level, value) in expected.items():
            with self.subTest(mobility=mobility):
                subject = _synthetic_subject("CalendarCandidate", mobility=mobility)
                extracted = attention_module._downstream_component(
                    subject, self.feature_policy
                )
                component = attention_module._annotate_component(
                    extracted, subject, self.feature_policy
                )
                self.assertEqual(component.normalized_value, value)
                self.assertEqual(
                    component.decision_source, "CALENDAR_MOBILITY_FALLBACK"
                )
                self.assertIn(f"mobility {mobility}", component.explanation)
                self.assertIn(f"impact level {impact_level}", component.explanation)
                self.assertEqual(component.feature_policy_version, "1.1.0")
                self.assertTrue(component.evidence_refs)
                self.assertTrue(component.uncertainty)

    def test_unsupported_calendar_mobility_remains_unknown(self) -> None:
        subject = _synthetic_subject("CalendarCandidate", mobility="UNKNOWN")
        component = attention_module._downstream_component(
            subject, self.feature_policy
        )
        self.assertIsNone(component.normalized_value)
        self.assertNotEqual(component.normalized_value, Decimal("0"))

    def test_ineligible_calendar_item_does_not_receive_fallback(self) -> None:
        subject = _synthetic_subject("CalendarCandidate", mobility="PROTECTED")
        subject.value["ranking_eligibility"] = "INELIGIBLE"
        component = attention_module._downstream_component(
            subject, self.feature_policy
        )
        self.assertIsNone(component.normalized_value)

    def test_explicit_impact_overrides_calendar_mobility_fallback(self) -> None:
        subject = _synthetic_subject(
            "CalendarCandidate",
            mobility="CANCELABLE",
            downstream_impact={"level": "VERY_HIGH"},
        )
        component = attention_module._downstream_component(
            subject, self.feature_policy
        )
        self.assertEqual(component.normalized_value, Decimal("1.0"))
        self.assertEqual(component.decision_source, "EXPLICIT_IMPACT_SIGNAL")

    def test_operational_commitment_never_uses_calendar_fallback(self) -> None:
        subject = _synthetic_subject("Commitment", mobility="PROTECTED")
        component = attention_module._downstream_component(
            subject, self.feature_policy
        )
        self.assertIsNone(component.normalized_value)
        self.assertNotEqual(
            component.decision_source, "CALENDAR_MOBILITY_FALLBACK"
        )
        for item_id in (
            "ATTN-CMT-01",
            "ATTN-CMT-02",
            "ATTN-CMT-03",
            "ATTN-CMT-04",
            "ATTN-CMT-05",
        ):
            self.assertEqual(
                _component(self.after, item_id, "downstream_impact")[
                    "decision_source"
                ],
                "EXPLICIT_IMPACT_SIGNAL",
            )

    def test_all_fixture_items_now_have_complete_scores(self) -> None:
        self.assertEqual(self.before.blocked_items, ())
        self.assertEqual(self.after.blocked_items, ())
        self.assertEqual(len(self.before.ranking["items"]), 7)
        self.assertEqual(len(self.after.ranking["items"]), 9)

    def test_evidence_confidence_uses_conservative_minimum(self) -> None:
        item_id = "ATTN-CMT-01"
        component = _component(self.after, item_id, "evidence_confidence")
        values = []
        caps = self.feature_policy["component_rules"]["evidence_confidence"][
            "epistemic_caps"
        ]
        for evidence_id in component["evidence_refs"]:
            evidence = self.runtime.indexes.evidence[evidence_id]
            values.append(
                min(
                    Decimal(str(evidence["confidence"])),
                    Decimal(str(caps[evidence["epistemic_state"]])),
                )
            )
        self.assertEqual(
            Decimal(str(component["normalized_value"])), min(values)
        )

    def test_rankings_and_items_validate_with_numeric_scores(self) -> None:
        for result in (self.before, self.after):
            self.registry.validate(
                ATTENTION_RANKING_SCHEMA_ID,
                to_plain_json_value(result.ranking),
                instance_path="memory/ranking.json",
                object_id=result.ranking["attention_ranking_id"],
            )
            for item in result.ranking["items"]:
                self.registry.validate(
                    ATTENTION_ITEM_SCHEMA_ID,
                    to_plain_json_value(item),
                    instance_path="memory/attention-item.json",
                    object_id=item["attention_item_id"],
                )
                self.assertIsInstance(item["score"], float)

    def test_protection_is_a_band_without_numeric_bonus(self) -> None:
        protected = [
            item
            for item in self.after.ranking["items"]
            if item["protection_at_rank"] == "PROTECTED"
        ]
        self.assertEqual(
            [item["attention_item_id"] for item in protected],
            ["ATTN-CMT-01", "ATTN-CMT-02", "ATTN-CALENDAR-CMT-T0-10"],
        )
        self.assertTrue(
            all(
                component["component_id"] != "protection"
                for item in protected
                for component in item["component_breakdown"]
            )
        )
        self.assertEqual(
            set(self.feature_policy["protection_guardrail"]["bands"]),
            {"PROTECTED", "STANDARD"},
        )
        first_standard_rank = min(
            item["rank"]
            for item in self.after.ranking["items"]
            if item["protection_at_rank"] != "PROTECTED"
        )
        self.assertGreater(first_standard_rank, max(item["rank"] for item in protected))

    def test_dependency_prerequisite_precedes_higher_scored_dependent(self) -> None:
        items = {
            item["attention_item_id"]: item for item in self.after.ranking["items"]
        }
        self.assertGreater(
            Decimal(self.after.raw_scores["ATTN-CMT-02"]),
            Decimal(self.after.raw_scores["ATTN-CMT-01"]),
        )
        self.assertLess(items["ATTN-CMT-01"]["rank"], items["ATTN-CMT-02"]["rank"])
        self.assertEqual(
            self.after.dependency_precedence,
            (("ATTN-CMT-01", "ATTN-CMT-02"),),
        )

    def test_confirmation_changes_actionability_not_numeric_formula_or_band(self) -> None:
        item = next(
            item
            for item in self.after.ranking["items"]
            if item["attention_item_id"] == "ATTN-CMT-05"
        )
        self.assertEqual(item["status"], "needs_confirmation")
        self.assertEqual(item["confirmation_required_refs"], ("CMT-05",))
        self.assertEqual(self.after.ranking_bands["ATTN-CMT-05"], "STANDARD")
        self.assertNotIn(
            "confirmation",
            {component["component_id"] for component in item["component_breakdown"]},
        )
        self.assertEqual(
            Decimal(self.after.raw_scores["ATTN-CMT-05"]),
            sum(
                Decimal(str(component["weighted_value"]))
                for component in item["component_breakdown"]
            ),
        )

    def test_cmt04_displacement_is_conditional_and_not_executed(self) -> None:
        item = next(
            item
            for item in self.after.ranking["items"]
            if item["attention_item_id"] == "ATTN-CMT-04"
        )
        self.assertEqual(item["displaced_commitment_refs"], ("CMT-04",))
        self.assertEqual(item["execution_state"], "UNKNOWN")
        self.assertEqual(item["status"], "monitor")
        component = _component(
            self.after, "ATTN-CMT-04", "conflict_or_displacement"
        )
        self.assertEqual(component["normalized_value"], 0.0)
        self.assertEqual(
            component["decision_source"],
            "CONDITIONAL_DISPLACEMENT_TARGET_NO_BONUS",
        )
        for required_text in (
            "Condition:",
            "Opportunity cost:",
            "Repair requirement:",
            "Authority:",
            "Uncertainty:",
        ):
            self.assertIn(required_text, component["explanation"])
        self.assertTrue(item["opportunity_cost"])
        self.assertTrue(item["repair_requirement"])
        self.assertEqual(item["authority_at_rank"], "FOUNDER")
        self.assertTrue(item["uncertainty"])

    def test_ordinary_supported_conflict_target_receives_point_six(self) -> None:
        component = _component(
            self.after,
            "ATTN-CALENDAR-CMT-T0-06",
            "conflict_or_displacement",
        )
        self.assertEqual(component["normalized_value"], 0.6)
        self.assertEqual(
            component["decision_source"],
            "SUPPORTED_UNRESOLVED_CONFLICT_TARGET",
        )

    def test_event_novelty_uses_own_state_materiality(self) -> None:
        self.assertEqual(
            _component(self.after, "ATTN-CMT-01", "event_novelty")[
                "normalized_value"
            ],
            1.0,
        )
        relationship_only = _component(
            self.after, "ATTN-CALENDAR-CMT-T0-06", "event_novelty"
        )
        self.assertEqual(relationship_only["normalized_value"], 0.0)
        self.assertEqual(
            relationship_only["decision_source"], "RELATIONSHIP_ONLY_UPDATE"
        )

        changed = self.t1.to_plain_json()
        changed.pop("state_digest")
        commitment = next(
            value
            for value in changed["commitments"]
            if value["commitment_id"] == "CMT-03"
        )
        commitment["lifecycle_status"] = "ACTIVE"
        changed_t1 = finalize_snapshot(changed, instance_path="memory/material-t1")
        changed_subject = next(
            subject
            for subject in attention_module._select_subjects(self.runtime, changed_t1)
            if subject.subject_id == "CMT-03"
        )
        novelty = attention_module._novelty_component(
            changed_t1,
            self.t0,
            changed_subject,
            self.feature_policy,
            "after",
        )
        self.assertEqual(novelty.normalized_value, Decimal("0.5"))
        self.assertEqual(novelty.decision_source, "OWN_SEMANTIC_STATE_CHANGE")

    def test_display_rounding_is_half_up_and_internal_order_is_unrounded(self) -> None:
        items = {
            item["attention_item_id"]: item for item in self.before.ranking["items"]
        }
        for item_id, raw in self.before.raw_scores.items():
            if raw is None:
                continue
            self.assertEqual(
                Decimal(str(items[item_id]["score"])),
                Decimal(raw).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            )
        self.assertGreater(
            Decimal(self.before.raw_scores["ATTN-CMT-03"]),
            Decimal(self.before.raw_scores["ATTN-CMT-05"]),
        )
        self.assertLess(items["ATTN-CMT-03"]["rank"], items["ATTN-CMT-05"]["rank"])

    def test_repeated_scoring_and_tie_order_are_deterministic(self) -> None:
        second_before, second_after = compute_attention_rankings(
            self.runtime, self.t0, self.t1, self.feature_policy
        )
        self.assertEqual(self.before.canonical_bytes(), second_before.canonical_bytes())
        self.assertEqual(self.after.canonical_bytes(), second_after.canonical_bytes())
        self.assertIn("attention item ID ascending", self.after.ranking["tie_break_method"])

    def test_calculation_digest_changes_with_snapshot_semantics(self) -> None:
        original = {
            item["attention_item_id"]: item["calculation_digest"]
            for item in self.after.ranking["items"]
        }
        changed = self.t1.to_plain_json()
        changed.pop("state_digest")
        changed["capacity_state"]["uncertainty"].append(
            "A deterministic test-only semantic change."
        )
        changed_t1 = finalize_snapshot(changed, instance_path="memory/changed-t1")
        _, changed_after = compute_attention_rankings(
            self.runtime, self.t0, changed_t1, self.feature_policy
        )
        self.assertNotEqual(
            original,
            {
                item["attention_item_id"]: item["calculation_digest"]
                for item in changed_after.ranking["items"]
            },
        )

    def test_production_source_has_no_oracle_dependency(self) -> None:
        source = inspect.getsource(__import__("memoria_viva.attention", fromlist=["*"]))
        self.assertNotIn("OracleBundle", source)
        self.assertNotIn("from .oracle", source)
        self.assertNotIn("expected-ranking", source)
        self.assertNotIn("expected-graph-delta", source)
        self.assertNotIn("expected_rank", source)
        self.assertNotIn("expected_score_direction", source)
        self.assertNotIn("CMT-", source)
        self.assertNotIn("GC-", source)

    def test_oracle_loading_and_mutation_cannot_change_production_output(self) -> None:
        before_bytes = self.before.canonical_bytes()
        after_bytes = self.after.canonical_bytes()
        oracle = self.loader.load_oracle_bundle(self.runtime)
        modified = to_plain_json_value(oracle.expected_ranking_after)
        modified["expected_ordered_items"][0]["expected_rank"] = 99
        recomputed = compute_attention_rankings(
            self.runtime, self.t0, self.t1, self.feature_policy
        )
        self.assertEqual(before_bytes, recomputed[0].canonical_bytes())
        self.assertEqual(after_bytes, recomputed[1].canonical_bytes())

    def test_scoring_needs_no_oracle_file_access_or_runs_output(self) -> None:
        runs_before = tuple(sorted((ROOT / "runs").glob("**/*")))
        with mock.patch.object(
            Path,
            "read_text",
            side_effect=AssertionError("production scoring attempted file access"),
        ):
            compute_attention_rankings(
                self.runtime, self.t0, self.t1, self.feature_policy
            )
        self.assertEqual(runs_before, tuple(sorted((ROOT / "runs").glob("**/*"))))


def _component(result, item_id: str, component_id: str):
    return next(
        component
        for component in result.component_table[item_id]
        if component["component_id"] == component_id
    )


def _synthetic_subject(
    subject_kind: str,
    *,
    mobility: str,
    downstream_impact=None,
):
    value = {
        "mobility_policy": mobility,
        "uncertainty": ("Synthetic uncertainty remains explicit.",),
    }
    if subject_kind == "CalendarCandidate":
        value["evidence_ref"] = "EV-SYNTHETIC"
        value["ranking_eligibility"] = "ELIGIBLE"
    else:
        value["evidence_refs"] = ("EV-SYNTHETIC",)
    if downstream_impact is not None:
        value["downstream_impact"] = downstream_impact
    return attention_module._Subject(
        attention_item_id="ATTN-SYNTHETIC",
        subject_kind=subject_kind,
        subject_id="SYNTHETIC-SUBJECT",
        subject_ref={},
        value=value,
    )


def _contains_key(value, forbidden: set[str]) -> bool:
    if isinstance(value, dict):
        return any(key in forbidden or _contains_key(child, forbidden) for key, child in value.items())
    if isinstance(value, list):
        return any(_contains_key(child, forbidden) for child in value)
    return False


if __name__ == "__main__":
    unittest.main()
