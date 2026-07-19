from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from memoria_viva.cli import EXPORT_FILENAMES, main
from memoria_viva.contracts import SchemaRegistry
from memoria_viva.presentation import run_canonical_demo


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "snapshot-t0.json": "urn:memoria-viva:attention-graph:schema:snapshot:1.0.0",
    "attention-ranking-before.json": "urn:memoria-viva:attention-graph:schema:attention-ranking:1.0.0",
    "snapshot-t1.json": "urn:memoria-viva:attention-graph:schema:snapshot:1.0.0",
    "attention-ranking-after.json": "urn:memoria-viva:attention-graph:schema:attention-ranking:1.0.0",
    "graph-delta.json": "urn:memoria-viva:attention-graph:schema:graph-delta:1.0.0",
    "run-record.json": "urn:memoria-viva:attention-graph:schema:run-record:1.0.0",
}


class CliTests(unittest.TestCase):
    def test_text_summary_exits_zero_and_shows_all_pass_states(self) -> None:
        stdout, stderr = io.StringIO(), io.StringIO()
        code = main(["replay"], root=ROOT, stdout=stdout, stderr=stderr)
        self.assertEqual(code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertIn("Replay status: PASS", stdout.getvalue())
        self.assertIn("before=PASS, after=PASS, GraphDelta=PASS", stdout.getvalue())
        self.assertIn("Public product demonstration ready", stdout.getvalue())

    def test_json_output_is_deterministic(self) -> None:
        outputs = []
        for _ in range(2):
            stdout = io.StringIO()
            self.assertEqual(
                main(["replay", "--format", "json"], root=ROOT, stdout=stdout),
                0,
            )
            outputs.append(stdout.getvalue())
        self.assertEqual(outputs[0], outputs[1])
        payload = json.loads(outputs[0])
        self.assertEqual(payload["replay_status"], "PASS")

    def test_default_mode_writes_nothing_under_runs(self) -> None:
        before = _runs_state()
        self.assertEqual(main(["replay"], root=ROOT, stdout=io.StringIO()), 0)
        self.assertEqual(before, _runs_state())

    def test_export_is_restricted_to_runs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stderr = io.StringIO()
            code = main(
                ["replay", "--output-dir", directory],
                root=ROOT,
                stdout=io.StringIO(),
                stderr=stderr,
            )
        self.assertEqual(code, 2)
        self.assertIn("subdirectory of runs", stderr.getvalue())

    def test_path_traversal_is_rejected(self) -> None:
        stderr = io.StringIO()
        code = main(
            ["replay", "--output-dir", "runs/../../outside"],
            root=ROOT,
            stdout=io.StringIO(),
            stderr=stderr,
        )
        self.assertEqual(code, 2)
        self.assertFalse((ROOT.parent / "outside").exists())

    def test_export_overwrite_requires_force(self) -> None:
        session = run_canonical_demo(ROOT)
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            target = temporary_root / "runs" / "demo"
            with patch("memoria_viva.cli.run_canonical_demo", return_value=session):
                args = ["replay", "--output-dir", str(target)]
                self.assertEqual(
                    main(args, root=temporary_root, stdout=io.StringIO()), 0
                )
                self.assertEqual(
                    main(
                        args,
                        root=temporary_root,
                        stdout=io.StringIO(),
                        stderr=io.StringIO(),
                    ),
                    2,
                )
                self.assertEqual(
                    main(
                        [*args, "--force"],
                        root=temporary_root,
                        stdout=io.StringIO(),
                    ),
                    0,
                )

    def test_exported_contract_artifacts_validate(self) -> None:
        registry = SchemaRegistry(ROOT / "schemas")
        session = run_canonical_demo(ROOT)
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            target = temporary_root / "runs" / "demo"
            with patch("memoria_viva.cli.run_canonical_demo", return_value=session):
                code = main(
                    ["replay", "--output-dir", str(target)],
                    root=temporary_root,
                    stdout=io.StringIO(),
                )
            self.assertEqual(code, 0)
            self.assertEqual(
                sorted(path.name for path in target.iterdir()),
                sorted(EXPORT_FILENAMES),
            )
            for filename, schema_id in SCHEMAS.items():
                instance = json.loads(
                    (target / filename).read_text(encoding="utf-8")
                )
                registry.validate(
                    schema_id,
                    instance,
                    instance_path=f"runs/test/{filename}",
                    object_id=None,
                )

    def test_cli_never_outputs_secret_material(self) -> None:
        stdout, stderr = io.StringIO(), io.StringIO()
        main(["replay"], root=ROOT, stdout=stdout, stderr=stderr)
        combined = stdout.getvalue() + stderr.getvalue()
        self.assertNotIn("OPENAI_API_KEY", combined)
        self.assertNotIn("sk-proj-", combined)
        self.assertNotIn(".env.local", combined)


def _runs_state() -> tuple[str, ...]:
    return tuple(
        sorted(
            str(path.relative_to(ROOT / "runs"))
            for path in (ROOT / "runs").rglob("*")
        )
    )


if __name__ == "__main__":
    unittest.main()
