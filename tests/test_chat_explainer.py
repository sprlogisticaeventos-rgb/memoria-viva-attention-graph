from __future__ import annotations

import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from memoria_viva.chat import (
    GUIDED_QUESTION_OPTIONS,
    answer_question,
)
from memoria_viva.chat_explainer import (
    CHAT_RESPONSE_SCHEMA_ID,
    MAX_RECOMMENDATION_WORDS,
    ChatResponseValidationError,
    generate_chat_rewrite,
    safe_generate_chat_rewrite,
)
from memoria_viva.contracts import SchemaRegistry
from memoria_viva.explainer import DEFAULT_OPENAI_MODEL
from memoria_viva.presentation import run_canonical_demo


ROOT = Path(__file__).resolve().parents[1]


class FakeResponses:
    def __init__(self, output: dict | str | Exception):
        self.output = output
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if isinstance(self.output, Exception):
            raise self.output
        text = self.output if isinstance(self.output, str) else json.dumps(self.output)
        return SimpleNamespace(output_text=text)


class FakeClient:
    def __init__(self, output: dict | str | Exception):
        self.responses = FakeResponses(output)


class ChatExplainerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.session = run_canonical_demo(ROOT)
        cls.answer = answer_question(GUIDED_QUESTION_OPTIONS[0], cls.session)

    def test_mocked_responses_api_uses_strict_language_only_schema(self) -> None:
        client = FakeClient(_valid_rewrite(self.answer))
        result = generate_chat_rewrite(self.answer, client, root=ROOT)
        self.assertEqual(result.status, "SUCCESS")
        request = client.responses.calls[0]
        self.assertTrue(request["text"]["format"]["strict"])
        self.assertEqual(request["text"]["format"]["type"], "json_schema")
        self.assertEqual(
            set(request["text"]["format"]["schema"]["properties"]),
            {
                "what_this_means",
                "recommended_next_move",
                "approval_or_uncertainty_note",
            },
        )
        self.assertFalse(request["store"])

    def test_application_controlled_fields_override_generated_values(self) -> None:
        output = _valid_rewrite(self.answer)
        output.update(
            {
                "model": "not-the-requested-model",
                "answer_id": "invented",
                "replay_digest": "invented",
                "intent": "UNSUPPORTED",
                "evidence_refs": ["EV-NOT-SUPPLIED"],
                "unknowns": [],
                "approval_required_items": ["invented"],
            }
        )
        result = generate_chat_rewrite(
            self.answer,
            FakeClient(output),
            model="gpt-5.6",
            root=ROOT,
        )
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(result.response["model"], "gpt-5.6")
        self.assertEqual(result.response["answer_id"], self.answer.answer_id)
        self.assertEqual(result.response["replay_digest"], self.answer.replay_digest)
        self.assertEqual(result.response["intent"], self.answer.intent)
        self.assertEqual(tuple(result.response["evidence_refs"]), self.answer.evidence_refs)

    def test_model_identity_is_canonicalized(self) -> None:
        output = _valid_rewrite(self.answer)
        output["model"] = "GPT-5.6"
        result = generate_chat_rewrite(
            self.answer,
            FakeClient(output),
            model="gpt-5.6",
            root=ROOT,
        )
        self.assertEqual(result.model, "gpt-5.6")
        self.assertEqual(result.response["model"], "gpt-5.6")

    def test_full_local_schema_validates_application_completed_response(self) -> None:
        result = generate_chat_rewrite(
            self.answer, FakeClient(_valid_rewrite(self.answer)), root=ROOT
        )
        SchemaRegistry(ROOT / "schemas").validate(
            CHAT_RESPONSE_SCHEMA_ID,
            result.to_plain_json()["response"],
            instance_path="memory/test-chat-response.json",
            object_id=self.answer.answer_id,
        )

    def test_two_guided_recommendation_paths_validate(self) -> None:
        for question in (GUIDED_QUESTION_OPTIONS[0], GUIDED_QUESTION_OPTIONS[-1]):
            with self.subTest(question=question):
                answer = answer_question(question, self.session)
                result = generate_chat_rewrite(
                    answer, FakeClient(_valid_rewrite(answer)), root=ROOT
                )
                self.assertEqual(result.status, "SUCCESS")
                rendered = " ".join(
                    result.response[field]
                    for field in (
                        "what_this_means",
                        "recommended_next_move",
                        "approval_or_uncertainty_note",
                    )
                )
                self.assertLessEqual(
                    len(rendered.split()), MAX_RECOMMENDATION_WORDS
                )

    def test_input_contains_only_grounded_chat_projection(self) -> None:
        client = FakeClient(_valid_rewrite(self.answer))
        generate_chat_rewrite(self.answer, client, root=ROOT)
        payload = json.loads(client.responses.calls[0]["input"])
        self.assertEqual(payload["replay_digest"], self.answer.replay_digest)
        self.assertEqual(
            payload["normalized_question"], "what matters now"
        )
        self.assertEqual(
            payload["deterministic_answer"]["question"],
            payload["normalized_question"],
        )
        rendered = client.responses.calls[0]["input"]
        self.assertNotIn("/Users/", rendered)
        self.assertNotIn(".env.local", rendered)
        self.assertNotIn("BUILD_LOG", rendered)

    def test_model_cannot_introduce_rank_or_score(self) -> None:
        output = _valid_rewrite(self.answer)
        output["what_this_means"] = (
            "The first item is rank 99 with score 0.01; uncertainty remains unknown."
        )
        result = safe_generate_chat_rewrite(
            self.answer, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")

    def test_valid_paraphrase_passes_without_exact_prose_matching(self) -> None:
        output = {
            "what_this_means": (
                "The verified protected order establishes the sequence while "
                "some requirements still need verification."
            ),
            "recommended_next_move": (
                "Start with the prerequisite product proof, then prepare its "
                "dependent package."
            ),
            "approval_or_uncertainty_note": (
                "Unverified execution and requirements remain subject to the "
                "recorded approval boundaries."
            ),
        }
        result = generate_chat_rewrite(
            self.answer, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "SUCCESS")

    def test_unsupported_entity_is_rejected(self) -> None:
        output = _valid_rewrite(self.answer)
        output["what_this_means"] += " CMT-99 should also be included."
        result = safe_generate_chat_rewrite(
            self.answer, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")

    def test_unknown_execution_cannot_be_changed_to_known(self) -> None:
        output = _valid_rewrite(self.answer)
        output["approval_or_uncertainty_note"] = (
            "Execution is known and all requirements are verified."
        )
        result = safe_generate_chat_rewrite(
            self.answer, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")

    def test_unsupported_evidence_is_rejected(self) -> None:
        output = _valid_rewrite(self.answer)
        output["what_this_means"] += " Evidence EV-NOT-SUPPLIED proves it."
        result = safe_generate_chat_rewrite(
            self.answer, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")

    def test_omitted_uncertainty_is_rejected(self) -> None:
        output = _valid_rewrite(self.answer)
        output["what_this_means"] = "The verified items retain their order."
        output["recommended_next_move"] = (
            "Complete the demonstration before the submission package."
        )
        output["approval_or_uncertainty_note"] = "No further note is needed."
        result = safe_generate_chat_rewrite(
            self.answer, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")

    def test_executed_displacement_claim_is_rejected(self) -> None:
        conditional = answer_question(GUIDED_QUESTION_OPTIONS[-1], self.session)
        output = _valid_rewrite(conditional)
        output["what_this_means"] = (
            "The displacement was executed, although other details remain unknown."
        )
        result = safe_generate_chat_rewrite(
            conditional, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")

    def test_approved_non_execution_statements_pass_strong_claim_guard(self) -> None:
        safe_statements = (
            "No movement was executed.",
            "Movement was not executed.",
            "Movement has not been executed.",
            "No displacement was executed.",
            "Displacement was not executed.",
            "Displacement has not been executed.",
            "Conditional movement did not occur.",
            "Conditional movement has not occurred.",
            "Execution is UNKNOWN.",
            "Execution remains UNKNOWN; no movement was executed.",
            (
                "Conditional displacement is authorized, but execution remains "
                "UNKNOWN; no movement was executed."
            ),
        )
        for statement in safe_statements:
            with self.subTest(statement=statement):
                output = _valid_rewrite(self.answer)
                output["what_this_means"] = (
                    f"{statement} Other requirements remain unverified."
                )
                result = generate_chat_rewrite(
                    self.answer, FakeClient(output), root=ROOT
                )
                self.assertEqual(result.status, "SUCCESS")

    def test_positive_and_mixed_execution_claims_remain_rejected(self) -> None:
        unsupported_statements = (
            "Movement was executed.",
            "Movement has been executed.",
            "Displacement was executed.",
            "Conditional movement occurred.",
            "Conditional movement has occurred.",
            "Execution is known.",
            "Execution is confirmed.",
            "No movement was executed, but displacement was executed.",
            "Execution remains UNKNOWN, although movement was executed.",
        )
        for statement in unsupported_statements:
            with self.subTest(statement=statement):
                output = _valid_rewrite(self.answer)
                output["what_this_means"] = (
                    f"{statement} Other requirements remain unverified."
                )
                with self.assertRaises(ChatResponseValidationError) as raised:
                    generate_chat_rewrite(
                        self.answer, FakeClient(output), root=ROOT
                    )
                self.assertEqual(
                    raised.exception.error_code, "UNSUPPORTED_STRONG_CLAIM"
                )

    def test_dependency_order_change_is_rejected(self) -> None:
        output = _valid_rewrite(self.answer)
        output["recommended_next_move"] = (
            "Finish the submission package, then complete the demonstration."
        )
        result = safe_generate_chat_rewrite(
            self.answer, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")

    def test_future_completion_claim_is_rejected(self) -> None:
        output = _valid_rewrite(self.answer)
        output["what_this_means"] = (
            "The submission will be completed while uncertainty remains unknown."
        )
        result = safe_generate_chat_rewrite(
            self.answer, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")

    def test_overlong_recommendation_is_rejected(self) -> None:
        output = _valid_rewrite(self.answer)
        output["what_this_means"] = " ".join(
            "unknown" for _ in range(MAX_RECOMMENDATION_WORDS + 1)
        )
        result = safe_generate_chat_rewrite(
            self.answer, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")

    def test_required_approval_cannot_be_bypassed(self) -> None:
        confirmation = answer_question(GUIDED_QUESTION_OPTIONS[-1], self.session)
        output = _valid_rewrite(confirmation)
        output["approval_or_uncertainty_note"] = (
            "The outcome remains unknown, so the action can proceed immediately."
        )
        result = safe_generate_chat_rewrite(
            confirmation, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")

    def test_non_recommendation_question_is_rejected_before_api_call(self) -> None:
        answer = answer_question(GUIDED_QUESTION_OPTIONS[1], self.session)
        client = FakeClient(_valid_rewrite(answer))
        result = safe_generate_chat_rewrite(answer, client, root=ROOT)
        self.assertEqual(result.status, "FALLBACK")
        self.assertEqual(client.responses.calls, [])

    def test_missing_key_or_client_fails_safely_with_answer_available(self) -> None:
        before = self.answer.canonical_bytes()
        result = safe_generate_chat_rewrite(self.answer, None, root=ROOT)
        self.assertEqual(result.status, "FALLBACK")
        self.assertIsNone(result.response)
        self.assertIn("deterministic answer", result.diagnostic.lower())
        self.assertEqual(self.answer.canonical_bytes(), before)

    def test_api_error_is_safe_and_does_not_echo_secret(self) -> None:
        secret = "sk-proj-do-not-display"
        result = safe_generate_chat_rewrite(
            self.answer,
            FakeClient(RuntimeError(f"request failed with {secret}")),
            root=ROOT,
        )
        self.assertEqual(result.status, "FALLBACK")
        self.assertNotIn(secret, result.diagnostic)
        self.assertNotIn("RuntimeError", result.diagnostic)

    def test_invalid_json_fails_safely_and_answer_is_unchanged(self) -> None:
        before = self.answer.canonical_bytes()
        result = safe_generate_chat_rewrite(
            self.answer, FakeClient("not-json"), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")
        self.assertEqual(self.answer.canonical_bytes(), before)

    def test_no_live_api_is_required_for_tests(self) -> None:
        client = FakeClient(_valid_rewrite(self.answer))
        result = generate_chat_rewrite(self.answer, client, root=ROOT)
        self.assertEqual(result.model, DEFAULT_OPENAI_MODEL)
        self.assertEqual(len(client.responses.calls), 1)


def _valid_rewrite(answer) -> dict:
    return {
        "what_this_means": (
            "The protected precedence band and dependency rule explain the "
            "verified order. Important details remain unknown or unverified."
        ),
        "recommended_next_move": (
            "Complete the demonstration first, then finalize the submission package."
        ),
        "approval_or_uncertainty_note": (
            "Execution and official requirements remain unknown; preserve every "
            "required approval before external action."
        ),
    }


if __name__ == "__main__":
    unittest.main()
