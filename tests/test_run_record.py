from __future__ import annotations

import unittest
from dataclasses import replace
from pathlib import Path

from memoria_viva.attention import load_attention_feature_policy
from memoria_viva.canonical import sha256_digest, to_plain_json_value
from memoria_viva.contracts import SchemaRegistry
from memoria_viva.fixtures import FixtureBundleLoader
from memoria_viva.replay import run_replay
from memoria_viva.run_record import RUN_RECORD_SCHEMA_ID


ROOT = Path(__file__).resolve().parents[1]


class RunRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = SchemaRegistry(ROOT / "schemas")
        cls.loader = FixtureBundleLoader(ROOT, schema_registry=cls.registry)
        cls.runtime = cls.loader.load_runtime_bundle()
        cls.oracle = cls.loader.load_oracle_bundle(cls.runtime)
        cls.feature_policy = load_attention_feature_policy(
            ROOT, schema_registry=cls.registry
        )
        cls.replay = run_replay(cls.runtime, cls.oracle, cls.feature_policy)
        cls.run_record = cls.replay.run_record

    def test_run_record_validates_as_replay_with_null_model_metadata(self) -> None:
        value = self.run_record.to_plain_json()
        self.registry.validate(
            RUN_RECORD_SCHEMA_ID,
            value,
            instance_path="memory/run-record",
            object_id=self.run_record.run_id,
        )
        self.assertEqual(value["execution_mode"], "REPLAY")
        self.assertIsNone(value["model_metadata"])
        self.assertEqual(value["status"], "completed")

    def test_input_and_output_identities_are_complete(self) -> None:
        value = self.run_record.value
        input_ids = {artifact["artifact_id"] for artifact in value["input_artifacts"]}
        self.assertTrue(
            {
                "FOUNDER-HACKATHON-PHASE-0C2",
                "mv_attention_policy",
                "mv.attention-feature-policy",
                "mv.canonical-trigger-transition",
                "ORACLE-ATTENTION-T0-BEFORE",
                "ORACLE-ATTENTION-T1-AFTER",
                "ORACLE-GRAPH-DELTA-T0-T1",
            }.issubset(input_ids)
        )
        output_ids = {
            artifact["artifact_id"] for artifact in value["output_artifacts"]
        }
        self.assertEqual(
            output_ids,
            {
                self.replay.snapshot_t0.snapshot_id,
                self.replay.snapshot_t1.snapshot_id,
                self.replay.ranking_before.ranking["attention_ranking_id"],
                self.replay.ranking_after.ranking["attention_ranking_id"],
                self.replay.graph_delta.graph_delta_id,
            },
        )
        for artifact in (*value["input_artifacts"], *value["output_artifacts"]):
            self.assertTrue(artifact["artifact_digest"].startswith("sha256:"))

    def test_run_record_excludes_itself_from_outputs_and_output_digest(self) -> None:
        value = self.run_record.value
        self.assertNotIn(
            self.run_record.run_id,
            {artifact["artifact_id"] for artifact in value["output_artifacts"]},
        )
        self.assertEqual(
            value["replay_output_identity"]["artifact_digest"],
            sha256_digest(to_plain_json_value(value["output_artifacts"])),
        )

    def test_claims_are_not_claimed_and_displacement_remains_unknown(self) -> None:
        value = self.run_record.value
        self.assertEqual(value["official_rules_verification"]["state"], "NOT_CLAIMED")
        for claim in ("compliance", "submission_completion", "goal_completion"):
            self.assertEqual(value["claim_states"][claim]["state"], "NOT_CLAIMED")
        displacement = value["claim_states"]["displacement_execution"]
        self.assertEqual(displacement["execution_state"], "UNKNOWN")
        self.assertIn("NOT_CLAIMED", displacement["explanation"])

    def test_required_warnings_are_preserved(self) -> None:
        codes = [warning["code"] for warning in self.run_record.value["warnings"]]
        self.assertIn("POLICY_STATUS_DRAFT", codes)
        self.assertIn("BOUNDED_REPLAY_ONLY", codes)
        self.assertIn("PUBLICATION_SURFACES_PENDING", codes)
        self.assertIn("FINAL_COMPLIANCE_UNKNOWN", codes)
        self.assertIn("GENERATED_OUTPUT_NOT_REVIEWED", codes)
        self.assertEqual(codes.count("NON_LOCAL_SOURCE_REFERENCE"), 4)

    def test_privacy_and_all_publication_surfaces_remain_pending(self) -> None:
        value = self.run_record.value
        self.assertEqual(value["privacy_classification"], "SANITIZED_PRIVATE")
        self.assertEqual(value["privacy_review_state"], "NOT_REVIEWED")
        publication = {
            approval["approval_id"]: approval["approval_state"]
            for approval in value["approvals"]
            if approval["approval_id"].startswith("APPROVAL-")
            and approval["approval_id"]
            not in {"APPROVAL-PRIVATE-FIXTURE-COMMIT", "APPROVAL-HUMAN-ORACLE"}
        }
        self.assertEqual(len(publication), 5)
        self.assertEqual(set(publication.values()), {"PENDING"})

    def test_policy_transition_schema_and_oracle_metadata_are_receipted(self) -> None:
        value = self.run_record.value
        self.assertEqual(value["policy_id"], "mv_attention_policy")
        self.assertEqual(value["policy_version"], "1.0.0")
        self.assertTrue(value["policy_digest"].startswith("sha256:"))
        schema_ids = {item["schema_id"] for item in value["schema_versions"]}
        self.assertIn(RUN_RECORD_SCHEMA_ID, schema_ids)
        self.assertIn(
            "urn:memoria-viva:attention-graph:schema:graph-delta:1.0.0",
            schema_ids,
        )
        self.assertEqual(
            [validation["status"] for validation in value["validations"]],
            ["passed", "passed", "passed"],
        )

    def test_run_id_and_digest_are_deterministic(self) -> None:
        repeated = run_replay(self.runtime, self.oracle, self.feature_policy).run_record
        self.assertEqual(repeated.run_id, self.run_record.run_id)
        self.assertEqual(repeated.run_digest, self.run_record.run_digest)
        self.assertEqual(repeated.canonical_bytes(), self.run_record.canonical_bytes())

    def test_oracle_semantic_change_changes_run_id_and_digest(self) -> None:
        changed_graph = to_plain_json_value(self.oracle.expected_graph_delta)
        changed_graph["changes"].pop()
        changed_oracle = replace(self.oracle, expected_graph_delta=changed_graph)
        changed = run_replay(
            self.runtime, changed_oracle, self.feature_policy
        ).run_record
        self.assertNotEqual(changed.run_id, self.run_record.run_id)
        self.assertNotEqual(changed.run_digest, self.run_record.run_digest)

    def test_run_record_is_immutable_and_plain_projection_is_detached(self) -> None:
        with self.assertRaises(TypeError):
            self.run_record.value["status"] = "failed"
        with self.assertRaises(TypeError):
            self.run_record.value["claim_states"]["compliance"]["state"] = "VERIFIED"
        plain = self.run_record.to_plain_json()
        plain["status"] = "failed"
        self.assertEqual(self.run_record.value["status"], "completed")


if __name__ == "__main__":
    unittest.main()
