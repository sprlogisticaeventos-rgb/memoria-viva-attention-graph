from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from memoria_viva.contracts import (
    ContractValidationError,
    SchemaRegistrationError,
    SchemaRegistry,
)
from memoria_viva.fixtures import FixtureBundleLoader


ROOT = Path(__file__).resolve().parents[1]
GOAL_SCHEMA_ID = "urn:memoria-viva:attention-graph:schema:goal:1.0.0"
DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"


class SchemaRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = SchemaRegistry(ROOT / "schemas")

    def test_all_canonical_schemas_register(self) -> None:
        discovered = tuple(
            sorted(
                json.loads(path.read_text(encoding="utf-8"))["$id"]
                for path in (ROOT / "schemas").glob("*.schema.json")
            )
        )
        self.assertEqual(self.registry.schema_ids, discovered)
        self.assertEqual(len(self.registry.schema_ids), 17)

    def test_stable_schema_ids_are_unique(self) -> None:
        self.assertEqual(
            len(self.registry.schema_ids), len(set(self.registry.schema_ids))
        )
        self.assertTrue(all(schema_id.strip() for schema_id in self.registry.schema_ids))

    def test_all_refs_resolve_in_closed_local_registry(self) -> None:
        reloaded = SchemaRegistry(ROOT / "schemas")
        self.assertEqual(reloaded.schema_ids, self.registry.schema_ids)

    def test_fixture_instances_validate(self) -> None:
        loader = FixtureBundleLoader(ROOT, schema_registry=self.registry)
        runtime = loader.load_runtime_bundle()
        oracle = loader.load_oracle_bundle(runtime)
        self.assertEqual(len(runtime.indexes.goals), 3)
        self.assertEqual(len(oracle.attention_item_references), 9)

    def test_invalid_schema_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.schema.json"
            path.write_text(
                json.dumps(
                    {
                        "$schema": DRAFT_2020_12,
                        "$id": "urn:test:invalid-schema",
                        "type": "not-a-json-schema-type",
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(SchemaRegistrationError) as caught:
                SchemaRegistry(Path(directory))
        self.assertEqual(caught.exception.issues[0].error_code, "INVALID_SCHEMA")

    def test_duplicate_schema_id_is_rejected(self) -> None:
        schema = {
            "$schema": DRAFT_2020_12,
            "$id": "urn:test:duplicate",
            "type": "object",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "one.schema.json").write_text(json.dumps(schema), encoding="utf-8")
            (root / "two.schema.json").write_text(json.dumps(schema), encoding="utf-8")
            with self.assertRaises(SchemaRegistrationError) as caught:
                SchemaRegistry(root)
        self.assertEqual(
            caught.exception.issues[0].error_code, "DUPLICATE_SCHEMA_ID"
        )

    def test_invalid_instance_errors_are_complete_and_deterministic(self) -> None:
        first = self.registry.validation_errors(
            GOAL_SCHEMA_ID,
            {},
            instance_path="memory/invalid-goal.json",
            object_id="GOAL-INVALID",
        )
        second = self.registry.validation_errors(
            GOAL_SCHEMA_ID,
            {},
            instance_path="memory/invalid-goal.json",
            object_id="GOAL-INVALID",
        )
        self.assertEqual(first, second)
        self.assertGreater(len(first), 1)
        self.assertTrue(all(issue.error_code == "INVALID_INSTANCE" for issue in first))
        with self.assertRaises(ContractValidationError) as caught:
            self.registry.validate(
                GOAL_SCHEMA_ID,
                {},
                instance_path="memory/invalid-goal.json",
                object_id="GOAL-INVALID",
            )
        self.assertEqual(caught.exception.issues, first)

    def test_remote_reference_is_rejected_without_network_use(self) -> None:
        schema = {
            "$schema": DRAFT_2020_12,
            "$id": "urn:test:remote-reference",
            "$ref": "https://example.invalid/never-fetch.schema.json",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "remote.schema.json"
            path.write_text(json.dumps(schema), encoding="utf-8")
            with mock.patch(
                "urllib.request.urlopen",
                side_effect=AssertionError("network access attempted"),
            ) as urlopen:
                with self.assertRaises(SchemaRegistrationError) as caught:
                    SchemaRegistry(Path(directory))
                urlopen.assert_not_called()
        self.assertEqual(
            caught.exception.issues[0].error_code, "UNRESOLVED_REFERENCE"
        )


if __name__ == "__main__":
    unittest.main()
