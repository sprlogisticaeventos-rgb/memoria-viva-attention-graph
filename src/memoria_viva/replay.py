"""Pure in-memory orchestration for the deterministic Memoria Viva replay."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .attention import AttentionRankingResult, compute_attention_rankings
from .canonical import canonical_json_bytes
from .fixtures import OracleBundle, RuntimeBundle
from .graph_delta import GraphDelta, build_graph_delta
from .oracle import (
    GraphDeltaComparison,
    OracleComparison,
    compare_graph_delta_oracle,
    compare_ordinal_oracle,
)
from .run_record import RunRecord, build_run_record
from .snapshot import Snapshot, build_snapshot_t0
from .transition import apply_canonical_trigger


REPLAY_CONTRACT = "MV_DETERMINISTIC_REPLAY_V1"


@dataclass(frozen=True)
class ReplayResult:
    """Immutable complete replay result; no member is persisted by this module."""

    snapshot_t0: Snapshot
    ranking_before: AttentionRankingResult
    snapshot_t1: Snapshot
    ranking_after: AttentionRankingResult
    graph_delta: GraphDelta
    ranking_before_comparison: OracleComparison
    ranking_after_comparison: OracleComparison
    graph_delta_comparison: GraphDeltaComparison
    run_record: RunRecord

    def to_plain_json(self) -> dict[str, Any]:
        return {
            "replay_contract": REPLAY_CONTRACT,
            "snapshot_t0": self.snapshot_t0.to_plain_json(),
            "ranking_before": self.ranking_before.to_plain_json(),
            "snapshot_t1": self.snapshot_t1.to_plain_json(),
            "ranking_after": self.ranking_after.to_plain_json(),
            "graph_delta": {
                "value": self.graph_delta.to_plain_json(),
                "transition_digest": self.graph_delta.transition_digest,
            },
            "ranking_before_comparison": self.ranking_before_comparison.to_plain_json(),
            "ranking_after_comparison": self.ranking_after_comparison.to_plain_json(),
            "graph_delta_comparison": self.graph_delta_comparison.to_plain_json(),
            "run_record": {
                "value": self.run_record.to_plain_json(),
                "run_digest": self.run_record.run_digest,
            },
        }

    def canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.to_plain_json())


def run_replay(
    runtime_bundle: RuntimeBundle,
    oracle_bundle: OracleBundle,
    feature_policy: Mapping[str, Any],
) -> ReplayResult:
    """Run production stages first, isolated comparisons second, receipt last."""

    if not isinstance(runtime_bundle, RuntimeBundle):
        raise TypeError("runtime_bundle must be RuntimeBundle")
    if not isinstance(oracle_bundle, OracleBundle):
        raise TypeError("oracle_bundle must be OracleBundle")
    if not isinstance(feature_policy, Mapping):
        raise TypeError("feature_policy must be an immutable validated mapping")

    # Production sequence. OracleBundle is not passed to any function in this block.
    snapshot_t0 = build_snapshot_t0(runtime_bundle)
    snapshot_t1 = apply_canonical_trigger(runtime_bundle, snapshot_t0)
    ranking_before, ranking_after = compute_attention_rankings(
        runtime_bundle,
        snapshot_t0,
        snapshot_t1,
        feature_policy,
    )
    graph_delta = build_graph_delta(
        runtime_bundle,
        snapshot_t0,
        snapshot_t1,
        ranking_before,
        ranking_after,
    )

    # Human-oracle access starts only after every production output is complete.
    ranking_before_comparison = compare_ordinal_oracle(
        ranking_before,
        oracle_bundle.expected_ranking_before,
    )
    ranking_after_comparison = compare_ordinal_oracle(
        ranking_after,
        oracle_bundle.expected_ranking_after,
        previous_computed=ranking_before,
    )
    graph_delta_comparison = compare_graph_delta_oracle(
        graph_delta,
        oracle_bundle.expected_graph_delta,
    )

    run_record = build_run_record(
        runtime_bundle,
        feature_policy,
        snapshot_t0,
        snapshot_t1,
        ranking_before,
        ranking_after,
        graph_delta,
        ranking_before_comparison,
        ranking_after_comparison,
        graph_delta_comparison,
    )
    return ReplayResult(
        snapshot_t0=snapshot_t0,
        ranking_before=ranking_before,
        snapshot_t1=snapshot_t1,
        ranking_after=ranking_after,
        graph_delta=graph_delta,
        ranking_before_comparison=ranking_before_comparison,
        ranking_after_comparison=ranking_after_comparison,
        graph_delta_comparison=graph_delta_comparison,
        run_record=run_record,
    )
