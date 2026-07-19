"""Judge-readable command line entrypoint for the canonical replay."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, TextIO

from .canonical import canonical_json_bytes, to_plain_json_value
from .presentation import DemoSession, repository_root, run_canonical_demo


EXPORT_FILENAMES = (
    "snapshot-t0.json",
    "attention-ranking-before.json",
    "snapshot-t1.json",
    "attention-ranking-after.json",
    "graph-delta.json",
    "run-record.json",
    "replay-summary.json",
)


class CliUsageError(ValueError):
    """A safe, user-actionable CLI error without internal path disclosure."""


def main(
    argv: Sequence[str] | None = None,
    *,
    root: Path | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the CLI and return a deterministic process exit code."""

    output = stdout or sys.stdout
    errors = stderr or sys.stderr
    parser = _parser()
    try:
        args = parser.parse_args(argv)
        if args.command != "replay":
            raise CliUsageError("a supported command is required")
        project_root = (root or repository_root()).resolve()
        session = run_canonical_demo(project_root)
        summary = _summary_projection(session)
        all_pass = summary["replay_status"] == "PASS"
        if args.format == "json":
            output.write(canonical_json_bytes(summary).decode("utf-8") + "\n")
        else:
            output.write(_text_summary(summary))
        if args.output_dir is not None:
            exported = export_replay(
                session,
                project_root,
                args.output_dir,
                force=args.force,
            )
            output.write(f"Exported {len(exported)} sanitized files under runs/.\n")
        return 0 if all_pass else 1
    except CliUsageError as error:
        errors.write(f"Replay not run: {error}\n")
        return 2
    except Exception:
        errors.write(
            "Replay unavailable: deterministic validation failed. No secret or "
            "internal traceback was displayed.\n"
        )
        return 1


def export_replay(
    session: DemoSession,
    root: Path,
    output_directory: str | Path,
    *,
    force: bool = False,
) -> tuple[Path, ...]:
    """Explicitly export canonical artifacts beneath ignored ``runs/`` only."""

    project_root = root.resolve()
    runs_root = (project_root / "runs").resolve()
    raw_target = Path(output_directory)
    target = (
        raw_target.resolve()
        if raw_target.is_absolute()
        else (project_root / raw_target).resolve()
    )
    if target == runs_root or not target.is_relative_to(runs_root):
        raise CliUsageError("--output-dir must resolve to a subdirectory of runs/")

    payloads = _export_payloads(session)
    destinations = tuple(target / name for name in EXPORT_FILENAMES)
    if not force:
        existing = [path.name for path in destinations if path.exists()]
        if existing:
            raise CliUsageError(
                "export target already contains replay files; pass --force to replace them"
            )
    target.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for destination in destinations:
        _atomic_write(destination, canonical_json_bytes(payloads[destination.name]))
        written.append(destination)
    return tuple(written)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m memoria_viva.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)
    replay = subparsers.add_parser("replay", help="run the canonical sanitized replay")
    replay.add_argument("--format", choices=("text", "json"), default="text")
    replay.add_argument("--output-dir")
    replay.add_argument("--force", action="store_true")
    return parser


def _summary_projection(session: DemoSession) -> dict[str, Any]:
    view = session.view_model.to_plain_json()
    statuses = view["oracle_statuses"]
    replay_status = "PASS" if all(value == "PASS" for value in statuses.values()) else "FAIL"
    return {
        "summary_contract": "MV_REPLAY_SUMMARY_V1",
        "replay_status": replay_status,
        "attention_items_before": view["headline_metrics"]["attention_items_before"],
        "attention_items_after": view["headline_metrics"]["attention_items_after"],
        "canonical_event": view["event"],
        "top_three_before": view["before_ranking"][:3],
        "top_three_after": view["after_ranking"][:3],
        "new_attention_items": view["new_attention_items"],
        "conditional_displacements": view["conditional_displacements"],
        "confirmation_required_items": view["confirmation_required_items"],
        "oracle_statuses": statuses,
        "replay_digest": view["replay_digest"],
        "privacy": view["privacy"],
    }


def _text_summary(summary: Mapping[str, Any]) -> str:
    lines = [
        "Memoria Viva — deterministic founder-attention replay",
        f"Replay status: {summary['replay_status']}",
        (
            "Ranked attention items: "
            f"{summary['attention_items_before']} before → "
            f"{summary['attention_items_after']} after"
        ),
        f"New event: {summary['canonical_event']['title']}",
        "",
        "Top three before:",
        *(
            f"  {row['rank']}. {row['label']} — {row['displayed_score']}"
            for row in summary["top_three_before"]
        ),
        "",
        "Top three after:",
        *(
            f"  {row['rank']}. {row['label']} — {row['displayed_score']}"
            for row in summary["top_three_after"]
        ),
        "",
        "New attention items: "
        + ", ".join(row["label"] for row in summary["new_attention_items"]),
        "Conditional displacement: "
        + ", ".join(row["label"] for row in summary["conditional_displacements"]),
        "Requires confirmation: "
        + ", ".join(row["label"] for row in summary["confirmation_required_items"]),
        (
            "Oracle checks: before={ranking_before}, after={ranking_after}, "
            "GraphDelta={graph_delta}"
        ).format(**summary["oracle_statuses"]),
        f"ReplayResult digest: {summary['replay_digest']}",
        "Publication status: PENDING on every public surface.",
    ]
    return "\n".join(lines) + "\n"


def _export_payloads(session: DemoSession) -> dict[str, Any]:
    replay = session.replay
    return {
        "snapshot-t0.json": replay.snapshot_t0.to_plain_json(),
        "attention-ranking-before.json": to_plain_json_value(
            replay.ranking_before.ranking
        ),
        "snapshot-t1.json": replay.snapshot_t1.to_plain_json(),
        "attention-ranking-after.json": to_plain_json_value(
            replay.ranking_after.ranking
        ),
        "graph-delta.json": replay.graph_delta.to_plain_json(),
        "run-record.json": replay.run_record.to_plain_json(),
        "replay-summary.json": session.view_model.download_projection(),
    }


def _atomic_write(destination: Path, payload: bytes) -> None:
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
