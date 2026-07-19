from __future__ import annotations

import inspect
import os
import subprocess
import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

from memoria_viva.attention import load_attention_feature_policy
from memoria_viva.canonical import canonical_json_bytes, sha256_digest, to_plain_json_value
from memoria_viva.fixtures import FixtureBundleLoader
from memoria_viva.replay import REPLAY_CONTRACT, ReplayResult, run_replay


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.loader = FixtureBundleLoader(ROOT)
        cls.runtime = cls.loader.load_runtime_bundle()
        cls.oracle = cls.loader.load_oracle_bundle(cls.runtime)
        cls.feature_policy = load_attention_feature_policy(ROOT)
        cls.result = run_replay(cls.runtime, cls.oracle, cls.feature_policy)

    def test_full_replay_returns_every_artifact(self) -> None:
        result = self.result
        self.assertIsInstance(result, ReplayResult)
        self.assertEqual(result.snapshot_t0.temporal_role, "T0")
        self.assertEqual(result.snapshot_t1.temporal_role, "T1")
        self.assertTrue(result.ranking_before.ranking["items"])
        self.assertTrue(result.ranking_after.ranking["items"])
        self.assertTrue(result.graph_delta.changes)
        self.assertTrue(result.run_record.value["output_artifacts"])
        self.assertEqual(result.to_plain_json()["replay_contract"], REPLAY_CONTRACT)

    def test_all_three_oracle_comparisons_pass(self) -> None:
        self.assertEqual(self.result.ranking_before_comparison.status, "PASS")
        self.assertEqual(self.result.ranking_after_comparison.status, "PASS")
        self.assertEqual(self.result.graph_delta_comparison.status, "PASS")

    def test_known_snapshot_and_ranking_identities_remain_unchanged(self) -> None:
        self.assertEqual(
            self.result.snapshot_t0.snapshot_id,
            "SNAPSHOT-T0-dac640bbb893407fa5df",
        )
        self.assertEqual(
            self.result.snapshot_t0.state_digest,
            "sha256:55bde2f8a9321ba1a79d05fe1ab15cad33bacbbb156566f52a8b5d29ed780efd",
        )
        self.assertEqual(
            self.result.snapshot_t1.snapshot_id,
            "SNAPSHOT-T1-8280b33463a480998d3e",
        )
        self.assertEqual(
            self.result.snapshot_t1.state_digest,
            "sha256:455d1c04b59e9dc5a66bcf3d58b2c02fde555b395dc150dbff32ef1f42cc910a",
        )
        self.assertEqual(
            self.result.ranking_before.ranking["attention_ranking_id"],
            "RANKING-BEFORE-20f7aefbef267eb77463",
        )
        self.assertEqual(
            self.result.ranking_after.ranking["attention_ranking_id"],
            "RANKING-AFTER-02c6078edf0b8c522cf1",
        )

    def test_production_outputs_do_not_depend_on_oracle_content(self) -> None:
        changed_before = to_plain_json_value(self.oracle.expected_ranking_before)
        changed_before["expected_ordered_items"].reverse()
        changed_oracle = replace(
            self.oracle,
            expected_ranking_before=changed_before,
        )
        changed = run_replay(self.runtime, changed_oracle, self.feature_policy)
        self.assertEqual(
            changed.snapshot_t0.canonical_bytes(),
            self.result.snapshot_t0.canonical_bytes(),
        )
        self.assertEqual(
            changed.snapshot_t1.canonical_bytes(),
            self.result.snapshot_t1.canonical_bytes(),
        )
        self.assertEqual(
            changed.ranking_before.canonical_bytes(),
            self.result.ranking_before.canonical_bytes(),
        )
        self.assertEqual(
            changed.ranking_after.canonical_bytes(),
            self.result.ranking_after.canonical_bytes(),
        )
        self.assertEqual(
            changed.graph_delta.canonical_bytes(),
            self.result.graph_delta.canonical_bytes(),
        )

    def test_source_guards_preserve_oracle_boundary(self) -> None:
        import memoria_viva.graph_delta as graph_delta_module
        import memoria_viva.replay as replay_module
        import memoria_viva.run_record as run_record_module

        graph_source = inspect.getsource(graph_delta_module)
        self.assertNotIn("OracleBundle", graph_source)
        self.assertNotIn("expected_graph_delta", graph_source)
        run_source = inspect.getsource(run_record_module)
        self.assertNotIn("OracleBundle", run_source)
        self.assertNotIn("expected-ranking", run_source)
        self.assertNotIn("expected-graph-delta", run_source)
        replay_source = inspect.getsource(replay_module)
        self.assertNotIn("_oracle_input_artifacts", replay_source)
        self.assertEqual(replay_source.count("oracle_bundle.expected_"), 3)
        production_block, comparison_block = replay_source.split(
            "# Human-oracle access starts only after every production output is complete.",
            1,
        )
        self.assertNotIn("oracle_bundle.expected_", production_block)
        self.assertIn("compare_ordinal_oracle", comparison_block)
        self.assertIn("compare_graph_delta_oracle", comparison_block)

    def test_repeated_replay_is_byte_identical(self) -> None:
        repeated = run_replay(self.runtime, self.oracle, self.feature_policy)
        self.assertEqual(repeated.canonical_bytes(), self.result.canonical_bytes())
        self.assertEqual(repeated.graph_delta.graph_delta_id, self.result.graph_delta.graph_delta_id)
        self.assertEqual(repeated.run_record.run_id, self.result.run_record.run_id)
        self.assertEqual(repeated.run_record.run_digest, self.result.run_record.run_digest)

    def test_two_independent_processes_produce_identical_replay(self) -> None:
        code = (
            "from pathlib import Path;"
            "from memoria_viva.fixtures import FixtureBundleLoader;"
            "from memoria_viva.attention import load_attention_feature_policy;"
            "from memoria_viva.replay import run_replay;"
            "from memoria_viva.canonical import sha256_digest;"
            "p=Path('.').resolve();l=FixtureBundleLoader(p);r=l.load_runtime_bundle();"
            "o=l.load_oracle_bundle(r);f=load_attention_feature_policy(p);x=run_replay(r,o,f);"
            "print(sha256_digest(x.to_plain_json()),x.graph_delta.graph_delta_id,"
            "x.graph_delta.transition_digest,x.run_record.run_id,x.run_record.run_digest)"
        )
        environment = dict(os.environ)
        environment["PYTHONPATH"] = "src"
        first = subprocess.check_output(
            [sys.executable, "-c", code], cwd=ROOT, env=environment
        )
        second = subprocess.check_output(
            [sys.executable, "-c", code], cwd=ROOT, env=environment
        )
        self.assertEqual(first, second)

    def test_replay_does_not_mutate_inputs_or_intermediate_values(self) -> None:
        runtime_before = canonical_json_bytes(self.runtime)
        oracle_before = canonical_json_bytes(self.oracle)
        t0_before = self.result.snapshot_t0.canonical_bytes()
        t1_before = self.result.snapshot_t1.canonical_bytes()
        before_ranking = self.result.ranking_before.canonical_bytes()
        after_ranking = self.result.ranking_after.canonical_bytes()
        run_replay(self.runtime, self.oracle, self.feature_policy)
        self.assertEqual(canonical_json_bytes(self.runtime), runtime_before)
        self.assertEqual(canonical_json_bytes(self.oracle), oracle_before)
        self.assertEqual(self.result.snapshot_t0.canonical_bytes(), t0_before)
        self.assertEqual(self.result.snapshot_t1.canonical_bytes(), t1_before)
        self.assertEqual(self.result.ranking_before.canonical_bytes(), before_ranking)
        self.assertEqual(self.result.ranking_after.canonical_bytes(), after_ranking)

    def test_replay_result_is_immutable_and_projection_is_detached(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            self.result.snapshot_t0 = self.result.snapshot_t1
        plain = self.result.to_plain_json()
        plain["snapshot_t0"]["snapshot_id"] = "changed"
        self.assertNotEqual(
            plain["snapshot_t0"]["snapshot_id"],
            self.result.snapshot_t0.snapshot_id,
        )

    def test_oracle_placeholder_digest_is_excluded_from_run_identity(self) -> None:
        changed_graph = to_plain_json_value(self.oracle.expected_graph_delta)
        changed_graph["transition_digest"] = "UNKNOWN-ANOTHER-PLACEHOLDER"
        changed = run_replay(
            self.runtime,
            replace(self.oracle, expected_graph_delta=changed_graph),
            self.feature_policy,
        )
        self.assertEqual(changed.run_record.run_id, self.result.run_record.run_id)
        self.assertEqual(changed.run_record.run_digest, self.result.run_record.run_digest)

    def test_no_output_file_is_created_under_runs(self) -> None:
        before = _runs_entries()
        run_replay(self.runtime, self.oracle, self.feature_policy)
        self.assertEqual(_runs_entries(), before)
        self.assertEqual(before, (".gitkeep",))


def _runs_entries() -> tuple[str, ...]:
    return tuple(
        sorted(str(path.relative_to(RUNS)) for path in RUNS.rglob("*") if path.is_file())
    )


if __name__ == "__main__":
    unittest.main()
