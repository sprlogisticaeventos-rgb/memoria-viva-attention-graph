from __future__ import annotations

import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from memoria_viva.contracts import ContractValidationError, SchemaRegistry
from memoria_viva.explainer import (
    DEFAULT_OPENAI_MODEL,
    _api_schema_projection,
    generate_decision_brief,
    safe_generate_decision_brief,
)
from memoria_viva.presentation import (
    DETERMINISTIC_AUTHORITY_STATEMENT,
    run_canonical_demo,
)


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


class ExplainerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.session = run_canonical_demo(ROOT)
        cls.view = cls.session.view_model

    def test_mocked_responses_api_returns_valid_strict_brief(self) -> None:
        client = FakeClient(_valid_brief(self.view))
        result = generate_decision_brief(self.view, client, root=ROOT)
        self.assertEqual(result.status, "SUCCESS")
        request = client.responses.calls[0]
        self.assertEqual(request["model"], DEFAULT_OPENAI_MODEL)
        self.assertFalse(request["store"])
        self.assertTrue(request["text"]["format"]["strict"])
        self.assertEqual(request["text"]["format"]["type"], "json_schema")
        self.assertFalse(request["text"]["format"]["schema"]["additionalProperties"])

    def test_model_identity_is_canonicalized_to_requested_identifier(self) -> None:
        output = _valid_brief(self.view)
        output["model"] = "GPT-5.6"
        client = FakeClient(output)

        result = generate_decision_brief(
            self.view,
            client,
            model="gpt-5.6",
            root=ROOT,
        )

        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(result.model, "gpt-5.6")
        self.assertEqual(result.brief["model"], "gpt-5.6")

    def test_api_schema_projection_strips_unique_items_recursively(self) -> None:
        schema = {
            "type": "object",
            "properties": {
                "top_level_array": {
                    "type": "array",
                    "items": {"type": "string"},
                    "uniqueItems": True,
                },
                "nested_array": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "uniqueItems": True,
                    },
                },
            },
            "required": ["top_level_array", "nested_array"],
            "additionalProperties": False,
        }
        original = json.loads(json.dumps(schema))

        projected = _api_schema_projection(schema)

        top_level = projected["properties"]["top_level_array"]
        nested = projected["properties"]["nested_array"]["items"]
        self.assertNotIn("uniqueItems", top_level)
        self.assertNotIn("uniqueItems", nested)
        self.assertEqual(top_level["type"], "array")
        self.assertEqual(top_level["items"], {"type": "string"})
        self.assertEqual(projected["required"], schema["required"])
        self.assertFalse(projected["additionalProperties"])
        self.assertEqual(schema, original)

    def test_local_schema_retains_unique_items_and_rejects_duplicates(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "decision-brief.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(schema["properties"]["evidence_refs"]["uniqueItems"])
        duplicate_evidence = _valid_brief(self.view)
        duplicate_evidence["evidence_refs"] = [
            duplicate_evidence["evidence_refs"][0],
            duplicate_evidence["evidence_refs"][0],
        ]

        with self.assertRaises(ContractValidationError):
            SchemaRegistry(ROOT / "schemas").validate(
                schema["$id"],
                duplicate_evidence,
                instance_path="generated/duplicate-decision-brief",
                object_id=None,
            )

    def test_input_is_only_sanitized_demo_view_projection(self) -> None:
        client = FakeClient(_valid_brief(self.view))
        generate_decision_brief(self.view, client, root=ROOT)
        payload = json.loads(client.responses.calls[0]["input"])
        self.assertEqual(payload, self.view.explainer_projection())
        rendered = client.responses.calls[0]["input"]
        self.assertNotIn("/Users/", rendered)
        self.assertNotIn(".env.local", rendered)
        self.assertNotIn("BUILD_LOG", rendered)
        self.assertNotIn("snapshot_t0", rendered)

    def test_model_output_cannot_mutate_oracle_or_replay(self) -> None:
        replay_before = self.session.replay.canonical_bytes()
        client = FakeClient(_valid_brief(self.view))
        generate_decision_brief(self.view, client, root=ROOT)
        self.assertEqual(replay_before, self.session.replay.canonical_bytes())

    def test_extra_rank_or_score_fields_are_rejected(self) -> None:
        output = _valid_brief(self.view)
        output["rank"] = 99
        output["score"] = 1.0
        result = safe_generate_decision_brief(
            self.view, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")
        self.assertIn("invalid structured brief", result.diagnostic)

    def test_unsupported_evidence_is_rejected(self) -> None:
        output = _valid_brief(self.view)
        output["evidence_refs"].append("EV-NOT-SUPPLIED")
        result = safe_generate_decision_brief(
            self.view, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")

    def test_omitted_uncertainty_is_rejected(self) -> None:
        output = _valid_brief(self.view)
        output["uncertainties"] = [output["uncertainties"][0]]
        result = safe_generate_decision_brief(
            self.view, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")

    def test_deterministic_fallback_always_works_without_key_or_client(self) -> None:
        result = safe_generate_decision_brief(self.view, None, root=ROOT)
        self.assertEqual(result.status, "FALLBACK")
        self.assertIsNone(result.brief)
        self.assertIn("deterministic engine brief", result.diagnostic.lower())
        self.assertTrue(self.view.to_plain_json()["deterministic_brief"])

    def test_api_error_is_safe_and_never_echoes_secret(self) -> None:
        secret = "sk-proj-do-not-display"
        result = safe_generate_decision_brief(
            self.view,
            FakeClient(RuntimeError(f"request failed with {secret}")),
            root=ROOT,
        )
        self.assertEqual(result.status, "FALLBACK")
        self.assertNotIn(secret, result.diagnostic)
        self.assertNotIn("RuntimeError", result.diagnostic)

    def test_timeout_is_safe(self) -> None:
        result = safe_generate_decision_brief(
            self.view, FakeClient(TimeoutError("late")), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")
        self.assertIn("timed out", result.diagnostic)

    def test_invalid_json_fails_safely(self) -> None:
        result = safe_generate_decision_brief(
            self.view, FakeClient("not-json"), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")

    def test_unsupported_completion_claim_is_rejected(self) -> None:
        output = _valid_brief(self.view)
        output["executive_summary"] = "The submission is complete."
        result = safe_generate_decision_brief(
            self.view, FakeClient(output), root=ROOT
        )
        self.assertEqual(result.status, "FALLBACK")

    def test_no_live_openai_import_or_request_is_needed_for_unit_tests(self) -> None:
        client = FakeClient(_valid_brief(self.view))
        result = generate_decision_brief(self.view, client, root=ROOT)
        self.assertEqual(result.model, DEFAULT_OPENAI_MODEL)
        self.assertEqual(len(client.responses.calls), 1)


def _valid_brief(view) -> dict:
    projection = view.explainer_projection()
    return {
        "brief_version": "1.0.0",
        "model": DEFAULT_OPENAI_MODEL,
        "replay_digest": view.replay_digest,
        "headline": "Two protected commitments reshape attention.",
        "executive_summary": (
            "The bounded event adds a demonstration and its dependent submission "
            "package while preserving prior obligations and uncertainty."
        ),
        "what_changed": [
            "The demonstration enters first and the dependent package enters second."
        ],
        "what_to_protect": [
            "Protect the minimum demonstration and protected continuity."
        ],
        "what_to_review_or_move": [
            "Review the conditional displacement before any movement."
        ],
        "what_requires_confirmation": [
            "The shared release-readiness gate requires joint confirmation."
        ],
        "next_smallest_action": (
            "Complete the minimum demonstration, then obtain human approval before "
            "any external movement."
        ),
        "uncertainties": list(projection["unresolved_uncertainties"]),
        "evidence_refs": [item["evidence_id"] for item in projection["evidence"]],
        "deterministic_authority_statement": DETERMINISTIC_AUTHORITY_STATEMENT,
    }


if __name__ == "__main__":
    unittest.main()
