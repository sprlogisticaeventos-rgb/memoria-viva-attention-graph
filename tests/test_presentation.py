from __future__ import annotations

import json
import unittest
from pathlib import Path

from memoria_viva.canonical import canonical_json_bytes
from memoria_viva.presentation import (
    DETERMINISTIC_BRIEF_LABEL,
    build_demo_view_model,
    run_canonical_demo,
)


ROOT = Path(__file__).resolve().parents[1]


class PresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.session = run_canonical_demo(ROOT)
        cls.view = cls.session.view_model.to_plain_json()

    def test_view_model_is_deterministic(self) -> None:
        second = run_canonical_demo(ROOT)
        self.assertEqual(
            self.session.view_model.canonical_bytes(),
            second.view_model.canonical_bytes(),
        )
        self.assertEqual(self.view["technical_proof"]["validated_test_count"], 260)

    def test_before_and_after_order_is_judge_readable(self) -> None:
        self.assertEqual(
            [row["subject_id"] for row in self.view["before_ranking"]],
            [
                "CMT-T0-10",
                "CMT-03",
                "CMT-05",
                "CMT-T0-01",
                "CMT-04",
                "CMT-T0-06",
                "CMT-T0-09",
            ],
        )
        self.assertEqual(
            [row["subject_id"] for row in self.view["after_ranking"][:3]],
            ["CMT-01", "CMT-02", "CMT-T0-10"],
        )

    def test_rank_movements_and_new_entries_are_explicit(self) -> None:
        movements = {
            row["subject_id"]: row for row in self.view["rank_movements"]
        }
        self.assertEqual(movements["CMT-01"]["direction"], "NEW")
        self.assertEqual(movements["CMT-02"]["rank_after"], 2)
        self.assertEqual(movements["CMT-T0-10"]["rank_after"], 3)

    def test_all_graph_delta_categories_are_present(self) -> None:
        self.assertEqual(
            set(self.view["graph_delta_by_category"]),
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
        self.assertTrue(
            all(self.view["graph_delta_by_category"][category] for category in self.view["graph_delta_by_category"])
        )

    def test_protection_confirmation_and_conditionality_are_visible(self) -> None:
        protected = {item["subject_id"] for item in self.view["protected_items"]}
        confirmation = {
            item["subject_id"]
            for item in self.view["confirmation_required_items"]
        }
        displacement = self.view["conditional_displacements"][0]
        self.assertEqual(protected, {"CMT-01", "CMT-02", "CMT-T0-10"})
        self.assertEqual(confirmation, {"CMT-05", "CMT-T0-01"})
        self.assertEqual(displacement["conditionality"], "CONDITIONAL")
        self.assertEqual(displacement["execution_state"], "UNKNOWN")

    def test_every_ranked_item_has_resolved_evidence(self) -> None:
        evidence_ids = {item["evidence_id"] for item in self.view["evidence"]}
        for item in (*self.view["before_ranking"], *self.view["after_ranking"]):
            self.assertTrue(item["evidence_refs"])
            self.assertTrue(set(item["evidence_refs"]).issubset(evidence_ids))

    def test_public_projection_contains_no_secret_or_private_path(self) -> None:
        rendered = self.session.view_model.canonical_bytes().decode("utf-8")
        self.assertNotIn("/Users/", rendered)
        self.assertNotIn("../handoff", rendered)
        self.assertNotIn("OPENAI_API_KEY", rendered)
        self.assertNotIn("sk-proj-", rendered)
        self.assertNotIn(".env.local", rendered)

    def test_plain_projection_is_detached(self) -> None:
        first = self.session.view_model.to_plain_json()
        first["before_ranking"][0]["label"] = "mutated"
        second = self.session.view_model.to_plain_json()
        self.assertEqual(second["before_ranking"][0]["label"], "Protected documentation review")

    def test_download_projection_is_deterministic_public_json(self) -> None:
        first = canonical_json_bytes(self.session.view_model.download_projection())
        second = canonical_json_bytes(
            run_canonical_demo(ROOT).view_model.download_projection()
        )
        self.assertEqual(first, second)
        json.loads(first)
        self.assertNotIn(b"component_table", first)

    def test_deterministic_fallback_brief_is_always_available(self) -> None:
        brief = self.view["deterministic_brief"]
        self.assertEqual(brief["label"], DETERMINISTIC_BRIEF_LABEL)
        self.assertIn("conditionally", brief["next_smallest_action"].lower())
        self.assertTrue(brief["what_remains_unknown"])

    def test_rebuilding_view_does_not_mutate_replay(self) -> None:
        before = self.session.replay.canonical_bytes()
        loader_session = run_canonical_demo(ROOT)
        build_demo_view_model(loader_session.replay, _runtime(ROOT))
        self.assertEqual(before, self.session.replay.canonical_bytes())


def _runtime(root: Path):
    from memoria_viva.fixtures import FixtureBundleLoader

    return FixtureBundleLoader(root).load_runtime_bundle()


if __name__ == "__main__":
    unittest.main()
