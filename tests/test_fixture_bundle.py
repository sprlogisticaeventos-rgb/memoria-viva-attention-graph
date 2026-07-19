from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from dataclasses import fields
from pathlib import Path

from memoria_viva.contracts import SchemaRegistry
from memoria_viva.fixtures import (
    APPROVED_NON_LOCAL_SOURCE_IDS,
    FixtureBundleError,
    FixtureBundleLoader,
    OracleBundle,
    RuntimeBundle,
)


ROOT = Path(__file__).resolve().parents[1]


class FixtureBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = SchemaRegistry(ROOT / "schemas")
        cls.loader = FixtureBundleLoader(ROOT, schema_registry=cls.registry)
        cls.runtime = cls.loader.load_runtime_bundle()
        cls.oracle = cls.loader.load_oracle_bundle(cls.runtime)

    def test_runtime_bundle_loads_and_is_immutable(self) -> None:
        self.assertIsInstance(self.runtime, RuntimeBundle)
        with self.assertRaises(TypeError):
            self.runtime.public_goal_set["new"] = "not allowed"  # type: ignore[index]
        with self.assertRaises(TypeError):
            self.runtime.indexes.goals["GC-01"]["public_title"] = "changed"  # type: ignore[index]

    def test_oracle_bundle_loads_separately(self) -> None:
        self.assertIsInstance(self.oracle, OracleBundle)
        runtime_fields = {field.name for field in fields(RuntimeBundle)}
        oracle_fields = {field.name for field in fields(OracleBundle)}
        self.assertFalse(
            {
                "expected_ranking_before",
                "expected_ranking_after",
                "expected_graph_delta",
            }.intersection(runtime_fields)
        )
        self.assertFalse(
            {
                "public_goal_set",
                "calendar_t0",
                "operational_commitments",
                "source_event",
                "attention_policy",
            }.intersection(oracle_fields)
        )

    def test_goal_index_contains_exactly_three_goals(self) -> None:
        self.assertEqual(tuple(self.runtime.indexes.goals), ("GC-01", "GC-02", "GC-03"))

    def test_calendar_membership_is_eight_active_two_retained_excluded(self) -> None:
        calendar = self.runtime.calendar_t0
        self.assertEqual(len(self.runtime.indexes.calendar_candidates), 10)
        self.assertEqual(len(calendar["active_ranking_candidate_refs"]), 8)
        self.assertEqual(
            tuple(calendar["excluded_but_retained_refs"]),
            ("CMT-T0-07", "CMT-T0-08"),
        )
        for candidate_id in ("CMT-T0-07", "CMT-T0-08"):
            candidate = self.runtime.indexes.calendar_candidates[candidate_id]
            self.assertEqual(candidate["inclusion_state"], "EXCLUDED_BUT_RETAINED")

    def test_commitments_and_lineage_are_complete(self) -> None:
        self.assertEqual(
            tuple(self.runtime.indexes.commitments),
            ("CMT-01", "CMT-02", "CMT-03", "CMT-04", "CMT-05"),
        )
        self.assertEqual(len(self.runtime.indexes.lineage_mappings), 9)
        self.assertFalse(
            set(self.runtime.indexes.commitments).intersection(
                self.runtime.indexes.calendar_candidates
            )
        )

    def test_exactly_one_trigger_preserves_unknown_occurred_at(self) -> None:
        self.assertEqual(len(self.runtime.indexes.source_events), 1)
        event = next(iter(self.runtime.indexes.source_events.values()))
        self.assertEqual(event["event_role"], "TRIGGER")
        self.assertIsNone(event["occurred_at"])
        self.assertIsNone(event["follow_up_to"])

    def test_commitment_policy_invariants(self) -> None:
        commitments = self.runtime.indexes.commitments
        conditional_displacements = [
            commitment_id
            for commitment_id, commitment in commitments.items()
            if commitment["mobility_policy"] == "DISPLACEABLE"
            and commitment["conditionality"] == "CONDITIONAL"
        ]
        self.assertEqual(conditional_displacements, ["CMT-04"])
        self.assertEqual(commitments["CMT-04"]["execution_state"], "UNKNOWN")
        self.assertEqual(commitments["CMT-05"]["mobility_policy"], "NEEDS_CONFIRMATION")
        self.assertEqual(commitments["CMT-05"]["authority_mode"], "JOINT")
        self.assertEqual(commitments["CMT-05"]["approval_requirement"], "PENDING")

    def test_all_evidence_references_resolve(self) -> None:
        evidence_ids = set(self.runtime.indexes.evidence)
        for document in (
            self.runtime.public_goal_set,
            self.runtime.calendar_t0,
            self.runtime.evidence_catalog,
            self.runtime.operational_commitments,
            self.runtime.constraints_catalog,
            self.runtime.source_event,
            self.runtime.privacy_manifest,
            self.oracle.expected_ranking_before,
            self.oracle.expected_ranking_after,
            self.oracle.expected_graph_delta,
        ):
            self.assertTrue(_evidence_references(document).issubset(evidence_ids))

    def test_unresolved_evidence_is_rejected(self) -> None:
        with self._temporary_repository() as root:
            path = root / "fixtures" / "founder-hackathon" / "calendar-t0.json"
            document = json.loads(path.read_text(encoding="utf-8"))
            document["candidates"][0]["evidence_ref"] = "EV-NOT-PRESENT"
            path.write_text(json.dumps(document), encoding="utf-8")
            loader = FixtureBundleLoader(root, schema_registry=self.registry)
            with self.assertRaises(FixtureBundleError) as caught:
                loader.load_runtime_bundle()
        self.assertIn(
            "UNRESOLVED_EVIDENCE_REFERENCE",
            {issue.error_code for issue in caught.exception.issues},
        )

    def test_duplicate_object_identity_is_rejected(self) -> None:
        with self._temporary_repository() as root:
            path = (
                root
                / "fixtures"
                / "founder-hackathon"
                / "operational-commitments.json"
            )
            document = json.loads(path.read_text(encoding="utf-8"))
            document["commitments"].append(copy.deepcopy(document["commitments"][0]))
            path.write_text(json.dumps(document), encoding="utf-8")
            loader = FixtureBundleLoader(root, schema_registry=self.registry)
            with self.assertRaises(FixtureBundleError) as caught:
                loader.load_runtime_bundle()
        self.assertIn(
            "DUPLICATE_OBJECT_ID",
            {issue.error_code for issue in caught.exception.issues},
        )

    def test_non_local_source_ids_warn_instead_of_failing(self) -> None:
        warnings = {
            warning.object_id
            for warning in self.runtime.warnings
            if warning.warning_code == "NON_LOCAL_SOURCE_REFERENCE"
        }
        self.assertEqual(warnings, set(APPROVED_NON_LOCAL_SOURCE_IDS))

    def test_publication_and_residual_risk_remain_pending(self) -> None:
        manifest = self.runtime.privacy_manifest
        self.assertEqual(manifest["residual_aggregation_risk"], "LOW_MEDIUM")
        self.assertEqual(
            {item["approval_state"] for item in manifest["publication_approvals"]},
            {"PENDING"},
        )

    def test_oracle_has_no_numeric_production_score_fields(self) -> None:
        forbidden = {
            "score",
            "previous_score",
            "score_delta",
            "component_breakdown",
            "component_contributions",
            "calculation_digest",
            "policy_digest",
        }
        for document in (
            self.oracle.expected_ranking_before,
            self.oracle.expected_ranking_after,
        ):
            self.assertFalse(forbidden.intersection(_all_keys(document)))

    def test_loading_creates_no_output_artifact(self) -> None:
        runs = ROOT / "runs"
        before = tuple(sorted(path.relative_to(runs) for path in runs.rglob("*")))
        runtime = self.loader.load_runtime_bundle()
        self.loader.load_oracle_bundle(runtime)
        after = tuple(sorted(path.relative_to(runs) for path in runs.rglob("*")))
        self.assertEqual(before, after)

    def test_repeated_loading_is_deterministic(self) -> None:
        second_runtime = self.loader.load_runtime_bundle()
        second_oracle = self.loader.load_oracle_bundle(second_runtime)
        self.assertEqual(tuple(self.runtime.indexes.goals), tuple(second_runtime.indexes.goals))
        self.assertEqual(
            tuple(self.runtime.indexes.calendar_candidates),
            tuple(second_runtime.indexes.calendar_candidates),
        )
        self.assertEqual(
            tuple(self.runtime.indexes.attention_item_references),
            tuple(second_runtime.indexes.attention_item_references),
        )
        self.assertEqual(self.runtime.warnings, second_runtime.warnings)
        self.assertEqual(
            self.oracle.attention_item_references,
            second_oracle.attention_item_references,
        )
        self.assertEqual(
            self.oracle.prospective_relationship_references,
            second_oracle.prospective_relationship_references,
        )

    def _temporary_repository(self) -> tempfile.TemporaryDirectory[str]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        fixture_target = root / "fixtures" / "founder-hackathon"
        fixture_target.parent.mkdir(parents=True)
        shutil.copytree(ROOT / "fixtures" / "founder-hackathon", fixture_target)
        config_target = root / "config"
        config_target.mkdir()
        shutil.copy2(
            ROOT / "config" / "attention-policy.v1.json",
            config_target / "attention-policy.v1.json",
        )
        return _TemporaryRepository(temporary)


class _TemporaryRepository:
    def __init__(self, temporary: tempfile.TemporaryDirectory[str]):
        self._temporary = temporary

    def __enter__(self) -> Path:
        return Path(self._temporary.name)

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._temporary.cleanup()


def _evidence_references(value: object) -> set[str]:
    references: set[str] = set()
    if isinstance(value, dict) or hasattr(value, "items"):
        for key, child in value.items():  # type: ignore[union-attr]
            if key == "evidence_ref" and isinstance(child, str):
                references.add(child)
            elif key == "evidence_refs" and isinstance(child, (list, tuple)):
                references.update(item for item in child if isinstance(item, str))
            references.update(_evidence_references(child))
    elif isinstance(value, (list, tuple)):
        for child in value:
            references.update(_evidence_references(child))
    return references


def _all_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict) or hasattr(value, "items"):
        for key, child in value.items():  # type: ignore[union-attr]
            keys.add(key)
            keys.update(_all_keys(child))
    elif isinstance(value, (list, tuple)):
        for child in value:
            keys.update(_all_keys(child))
    return keys


if __name__ == "__main__":
    unittest.main()
