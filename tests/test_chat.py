from __future__ import annotations

import unittest
from pathlib import Path

from memoria_viva.chat import (
    DETERMINISTIC_CHAT_AUTHORITY_STATEMENT,
    GUIDED_QUESTION_OPTIONS,
    SUPPORTED_SUGGESTED_PROMPTS,
    UNSUPPORTED_SCOPE_MESSAGE,
    answer_question,
    classify_intent,
)
from memoria_viva.presentation import run_canonical_demo


ROOT = Path(__file__).resolve().parents[1]


class DeterministicChatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.session = run_canonical_demo(ROOT)

    def test_supported_suggested_prompts_route_deterministically(self) -> None:
        expected = (
            "CURRENT_ATTENTION",
            "WHAT_CHANGED",
            "WHY_ITEM",
            "REQUIRES_CONFIRMATION",
            "EVIDENCE",
            "REPLAY_PROOF",
        )
        actual = tuple(
            classify_intent(prompt, self.session).intent
            for prompt in SUPPORTED_SUGGESTED_PROMPTS
        )
        self.assertEqual(actual, expected)

    def test_guided_question_options_use_the_existing_router(self) -> None:
        self.assertEqual(
            tuple(
                classify_intent(prompt, self.session).intent
                for prompt in GUIDED_QUESTION_OPTIONS
            ),
            (
                "CURRENT_ATTENTION",
                "WHAT_CHANGED",
                "REQUIRES_CONFIRMATION",
                "WHY_ITEM",
                "EVIDENCE",
                "CURRENT_ATTENTION",
            ),
        )

    def test_guided_direct_answers_remain_concise(self) -> None:
        for prompt in GUIDED_QUESTION_OPTIONS:
            with self.subTest(prompt=prompt):
                answer = answer_question(prompt, self.session)
                self.assertLessEqual(len(answer.direct_answer.split()), 80)

    def test_next_action_preserves_dependency_and_approval_order(self) -> None:
        answer = answer_question(GUIDED_QUESTION_OPTIONS[-1], self.session)
        lowered = answer.direct_answer.casefold()
        self.assertIn("freeze the minimum verifiable demonstration scope", lowered)
        self.assertIn("verify the public demo", lowered)
        self.assertLess(lowered.index("demonstration"), lowered.index("submission"))
        self.assertIn("human confirmation", lowered)
        self.assertIn("none of these actions is represented as executed", lowered)
        self.assertEqual(answer.intent, "CURRENT_ATTENTION")

    def test_router_uses_required_precedence_and_public_subject(self) -> None:
        match = classify_intent(
            "Why is Pending bounded validation protected or conditional?",
            self.session,
        )
        self.assertEqual(match.intent, "WHY_ITEM")
        self.assertEqual(match.matched_subject_id, "CMT-04")

    def test_current_attention_returns_exact_verified_top_three(self) -> None:
        answer = answer_question(SUPPORTED_SUGGESTED_PROMPTS[0], self.session)
        self.assertEqual(answer.intent, "CURRENT_ATTENTION")
        self.assertEqual(
            [item["public_label"] for item in answer.attention_items],
            [
                "Public product demonstration ready",
                "Submission package finalization",
                "Protected documentation review",
            ],
        )
        self.assertEqual([item["rank"] for item in answer.attention_items], [1, 2, 3])
        self.assertIn("Numeric score alone", " ".join(answer.supporting_points))

    def test_attention_item_projection_has_only_approved_fields(self) -> None:
        answer = answer_question(SUPPORTED_SUGGESTED_PROMPTS[0], self.session)
        self.assertEqual(
            set(answer.attention_items[0]),
            {
                "public_label",
                "rank",
                "displayed_score",
                "status",
                "protection_state",
                "confirmation_state",
                "execution_state",
                "evidence_refs",
            },
        )

    def test_what_changed_reports_seven_to_nine(self) -> None:
        answer = answer_question(SUPPORTED_SUGGESTED_PROMPTS[1], self.session)
        self.assertEqual(answer.intent, "WHAT_CHANGED")
        self.assertIn("from 7 to 9", answer.direct_answer)
        self.assertIn("execution remains UNKNOWN", " ".join(answer.supporting_points))

    def test_why_item_resolves_public_label_and_stable_id(self) -> None:
        by_label = answer_question(
            "Why is the product demonstration rank 1?", self.session
        )
        by_id = answer_question("Why is CMT-01 rank 1?", self.session)
        self.assertEqual(by_label.matched_subject_id, "CMT-01")
        self.assertEqual(by_id.matched_subject_id, "CMT-01")
        self.assertEqual(by_label.attention_items, by_id.attention_items)

    def test_conditional_answer_preserves_authorization_and_unknown_execution(self) -> None:
        answer = answer_question(SUPPORTED_SUGGESTED_PROMPTS[2], self.session)
        rendered = " ".join((answer.direct_answer, *answer.supporting_points))
        self.assertIn("authorized", rendered)
        self.assertIn("no movement was executed", rendered.lower())
        self.assertIn("execution remains UNKNOWN", rendered)
        self.assertIn("repair slot", rendered)
        self.assertIn("reactivation condition", rendered)

    def test_confirmation_answer_returns_exactly_two_approved_items(self) -> None:
        answer = answer_question(SUPPORTED_SUGGESTED_PROMPTS[3], self.session)
        self.assertEqual(answer.intent, "REQUIRES_CONFIRMATION")
        self.assertEqual(
            [item["public_label"] for item in answer.attention_items],
            [
                "Shared release-readiness gate",
                "Collaboration pilot decision window",
            ],
        )
        self.assertEqual(
            answer.approval_required_items,
            (
                "Shared release-readiness gate",
                "Collaboration pilot decision window",
            ),
        )

    def test_replay_proof_contains_three_pass_results_and_receipts(self) -> None:
        answer = answer_question(SUPPORTED_SUGGESTED_PROMPTS[5], self.session)
        self.assertEqual(answer.intent, "REPLAY_PROOF")
        self.assertEqual(set(answer.oracle_statuses.values()), {"PASS"})
        rendered = " ".join(answer.supporting_points)
        self.assertIn("SNAPSHOT-T0-dac640bbb893407fa5df", rendered)
        self.assertIn("SNAPSHOT-T1-8280b33463a480998d3e", rendered)
        self.assertIn("260 tests", rendered)

    def test_memory_state_reports_verified_membership(self) -> None:
        answer = answer_question("What does the system remember?", self.session)
        self.assertEqual(answer.intent, "MEMORY_STATE")
        self.assertIn("3 Goals", answer.direct_answer)
        self.assertIn("5 operational commitments", answer.direct_answer)
        self.assertIn("10 Calendar candidates", answer.direct_answer)
        self.assertIn("8 active and 2 excluded-but-retained", answer.direct_answer)

    def test_unsupported_question_remains_bounded(self) -> None:
        answer = answer_question("Write a general marketing plan.", self.session)
        self.assertEqual(answer.intent, "UNSUPPORTED")
        self.assertEqual(answer.direct_answer, UNSUPPORTED_SCOPE_MESSAGE)
        self.assertEqual(
            answer.suggested_follow_ups, SUPPORTED_SUGGESTED_PROMPTS[:3]
        )

    def test_question_does_not_change_any_verified_output(self) -> None:
        before = self.session.replay.canonical_bytes()
        digest = self.session.view_model.replay_digest
        for prompt in (*SUPPORTED_SUGGESTED_PROMPTS, "What does the system remember?"):
            answer = answer_question(prompt, self.session)
            self.assertEqual(answer.replay_digest, digest)
        self.assertEqual(self.session.replay.canonical_bytes(), before)

    def test_same_question_produces_byte_identical_immutable_answer(self) -> None:
        first = answer_question(SUPPORTED_SUGGESTED_PROMPTS[0], self.session)
        second = answer_question(SUPPORTED_SUGGESTED_PROMPTS[0], self.session)
        self.assertEqual(first.canonical_bytes(), second.canonical_bytes())
        self.assertEqual(first.answer_id, second.answer_id)
        with self.assertRaises(TypeError):
            first.attention_items[0]["rank"] = 99
        self.assertEqual(first.deterministic_authority_statement, DETERMINISTIC_CHAT_AUTHORITY_STATEMENT)

    def test_chat_creates_no_persistence_or_runs_output(self) -> None:
        before = _runs_state()
        answer_question(SUPPORTED_SUGGESTED_PROMPTS[4], self.session)
        self.assertEqual(before, _runs_state())

    def test_public_answers_contain_no_private_example_context(self) -> None:
        rendered = b"\n".join(
            answer_question(prompt, self.session).canonical_bytes()
            for prompt in (
                *SUPPORTED_SUGGESTED_PROMPTS,
                "What does the system remember?",
            )
        ).decode("utf-8").casefold()
        prohibited = (
            "ga" + "by",
            "su" + "árez",
            "immigration" + " documents",
            "raw " + "gmail",
            "raw " + "calendar",
            "/users/",
            ".env.local",
        )
        self.assertTrue(all(value not in rendered for value in prohibited))


def _runs_state() -> tuple[str, ...]:
    return tuple(
        sorted(
            str(path.relative_to(ROOT / "runs"))
            for path in (ROOT / "runs").rglob("*")
        )
    )


if __name__ == "__main__":
    unittest.main()
