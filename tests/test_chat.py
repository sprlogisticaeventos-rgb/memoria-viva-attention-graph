from __future__ import annotations

import copy
import unittest

from memoria_viva.chat import SUGGESTED_PROMPTS, answer_question


class ChatAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.view = _view()

    def test_attention_answer_preserves_computed_order(self) -> None:
        before = copy.deepcopy(self.view)
        response = answer_question("What should I pay attention to?", self.view)
        self.assertEqual(response.intent, "ATTENTION")
        self.assertLess(
            response.answer.index("Public product demonstration ready"),
            response.answer.index("Submission package finalization"),
        )
        self.assertLess(
            response.answer.index("Submission package finalization"),
            response.answer.index("Protected documentation review"),
        )
        self.assertEqual(self.view, before)

    def test_conditional_answer_never_claims_execution(self) -> None:
        response = answer_question("Why is CMT-04 still conditional?", self.view)
        self.assertEqual(response.intent, "CONDITIONALITY")
        self.assertIn("conditional, not executed", response.answer)
        self.assertIn("`UNKNOWN`", response.answer)
        self.assertIn("human review", response.answer)

    def test_replay_answer_reports_oracle_statuses_and_digest(self) -> None:
        response = answer_question("Replay this decision.", self.view)
        self.assertEqual(response.intent, "REPLAY")
        self.assertTrue(response.replay_verified)
        self.assertIn("Replay verified", response.answer)
        self.assertIn(self.view["replay_digest"], response.answer)
        self.assertEqual(response.graph_change_count, 3)

    def test_memory_answer_preserves_privacy_boundary(self) -> None:
        response = answer_question("Show me what the system remembers.", self.view)
        self.assertEqual(response.intent, "MEMORY")
        self.assertIn("sanitized decision state", response.answer)
        self.assertIn("does not remember raw private messages", response.answer)

    def test_unknown_question_returns_bounded_scope(self) -> None:
        response = answer_question("Tell me tomorrow's weather", self.view)
        self.assertEqual(response.intent, "SCOPE")
        self.assertIn("will not invent state", response.answer)
        for prompt in SUGGESTED_PROMPTS:
            self.assertIn(prompt, response.answer)

    def test_empty_question_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            answer_question("   ", self.view)


def _row(
    rank: int,
    subject_id: str,
    label: str,
    score: str,
    *,
    band: str = "ACTIVE",
    confirmation_required: bool = False,
    mobility: str = "MOVABLE",
    execution_state: str = "UNKNOWN",
    uncertainty: tuple[str, ...] = (),
) -> dict[str, object]:
    return {
        "rank": rank,
        "subject_id": subject_id,
        "label": label,
        "displayed_score": score,
        "band": band,
        "confirmation_required": confirmation_required,
        "approval_requirement": "human review required",
        "mobility": mobility,
        "execution_state": execution_state,
        "evidence_refs": (f"EV-{subject_id}",),
        "uncertainty": uncertainty,
        "explanation": f"Deterministic explanation for {label}.",
    }


def _view() -> dict[str, object]:
    after = [
        _row(1, "CMT-01", "Public product demonstration ready", "0.91", band="PROTECTED"),
        _row(2, "CMT-02", "Submission package finalization", "0.88", band="PROTECTED"),
        _row(3, "CMT-03", "Protected documentation review", "0.76", band="PROTECTED"),
        _row(
            4,
            "CMT-04",
            "Pending bounded validation",
            "0.62",
            mobility="CONDITIONALLY_DISPLACEABLE",
            uncertainty=("Repair slot remains unknown.",),
        ),
        _row(
            5,
            "CMT-05",
            "Shared release readiness",
            "0.58",
            confirmation_required=True,
        ),
    ]
    return {
        "replay_digest": "sha256:test-replay",
        "after_ranking": after,
        "new_attention_items": after[:2],
        "protected_items": after[:3],
        "confirmation_required_items": [after[4]],
        "critical_uncertainties": [
            "Repair slot remains unknown.",
            "Final compliance remains unknown.",
        ],
        "headline_metrics": {
            "attention_items_before": 3,
            "attention_items_after": 5,
            "new_protected_commitments": 2,
            "oracle_checks_passed": 3,
        },
        "event": {
            "title": "OpenAI Build Week opportunity",
            "summary": "A bounded external event changes the current attention state.",
            "evidence_refs": ("EV-EVENT",),
        },
        "deterministic_brief": {
            "headline": "The trigger creates two protected commitments without erasing prior obligations.",
            "what_changed": (
                "Attention expands from 3 to 5 ranked items.",
                "Public product demonstration ready enters rank 1.",
            ),
            "next_smallest_action": "Protect the minimum verifiable demonstration.",
        },
        "graph_delta_by_category": {
            "ADDED": [{"affected_id": "CMT-01"}],
            "UPDATED": [],
            "CONFLICTED": [],
            "DISPLACED": [
                {
                    "affected_id": "REL-CMT-01-DISPLACES-CMT-04",
                    "label": "Public product demonstration ready displaces Pending bounded validation",
                    "execution_state": "UNKNOWN",
                    "conditionality": "CONDITIONAL",
                    "condition": "Review capacity and obtain human approval.",
                    "explanation": "The item may move only after bounded review.",
                    "evidence_refs": ("EV-CMT-04",),
                    "uncertainty": ("Repair slot remains unknown.",),
                }
            ],
            "PROTECTED": [{"affected_id": "CMT-03"}],
            "REQUIRES_CONFIRMATION": [],
            "UNCHANGED": [],
        },
        "oracle_statuses": {
            "ranking_before": "PASS",
            "ranking_after": "PASS",
            "graph_delta": "PASS",
        },
        "technical_proof": {
            "determinism_statement": "The same committed fixture produces byte-identical deterministic outputs."
        },
    }


if __name__ == "__main__":
    unittest.main()
