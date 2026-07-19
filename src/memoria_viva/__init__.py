"""Deterministic contract-loading foundation for Memoria Viva."""

from .contracts import (
    ContractIssue,
    ContractValidationError,
    SchemaRegistrationError,
    SchemaRegistry,
)
from .fixtures import (
    BundleWarning,
    FixtureBundleError,
    FixtureBundleLoader,
    OracleBundle,
    RuntimeBundle,
)
from .canonical import (
    MV_CANONICAL_JSON_V1,
    CanonicalJsonError,
    canonical_json_bytes,
    sha256_digest,
    sha256_hex,
    to_plain_json_value,
)
from .snapshot import (
    Snapshot,
    SnapshotT0,
    build_snapshot_t0,
    finalize_snapshot,
    runtime_input_bundle_digest,
    snapshot_state_projection,
    validate_snapshot_instance,
)
from .transition import (
    MV_TRIGGER_TRANSITION_V1,
    TRANSITION_POLICY_ID,
    TRANSITION_POLICY_VERSION,
    TransitionValidationError,
    apply_canonical_trigger,
)
from .attention import (
    ATTENTION_COMPUTATION_V1,
    AttentionComputationError,
    AttentionRankingResult,
    ComponentExtraction,
    compute_attention_rankings,
    load_attention_feature_policy,
)
from .oracle import (
    GraphDeltaComparison,
    GraphDeltaOracleIssue,
    OracleComparison,
    OracleIssue,
    compare_graph_delta_oracle,
    compare_ordinal_oracle,
)
from .graph_delta import (
    GRAPH_DELTA_CONTRACT,
    GRAPH_DELTA_POLICY_ID,
    GRAPH_DELTA_POLICY_VERSION,
    GraphDelta,
    GraphDeltaValidationError,
    build_graph_delta,
)
from .run_record import (
    RUN_RECORD_CONTRACT,
    RunRecord,
    build_run_record,
)
from .replay import (
    REPLAY_CONTRACT,
    ReplayResult,
    run_replay,
)

__all__ = [
    "BundleWarning",
    "ATTENTION_COMPUTATION_V1",
    "AttentionComputationError",
    "AttentionRankingResult",
    "CanonicalJsonError",
    "ContractIssue",
    "ContractValidationError",
    "ComponentExtraction",
    "FixtureBundleError",
    "FixtureBundleLoader",
    "GRAPH_DELTA_CONTRACT",
    "GRAPH_DELTA_POLICY_ID",
    "GRAPH_DELTA_POLICY_VERSION",
    "GraphDelta",
    "GraphDeltaComparison",
    "GraphDeltaOracleIssue",
    "GraphDeltaValidationError",
    "OracleBundle",
    "OracleComparison",
    "OracleIssue",
    "REPLAY_CONTRACT",
    "RUN_RECORD_CONTRACT",
    "ReplayResult",
    "RunRecord",
    "MV_CANONICAL_JSON_V1",
    "RuntimeBundle",
    "Snapshot",
    "SnapshotT0",
    "SchemaRegistrationError",
    "SchemaRegistry",
    "MV_TRIGGER_TRANSITION_V1",
    "TRANSITION_POLICY_ID",
    "TRANSITION_POLICY_VERSION",
    "TransitionValidationError",
    "apply_canonical_trigger",
    "build_snapshot_t0",
    "build_graph_delta",
    "build_run_record",
    "canonical_json_bytes",
    "compare_graph_delta_oracle",
    "compare_ordinal_oracle",
    "compute_attention_rankings",
    "finalize_snapshot",
    "runtime_input_bundle_digest",
    "run_replay",
    "load_attention_feature_policy",
    "sha256_digest",
    "sha256_hex",
    "snapshot_state_projection",
    "to_plain_json_value",
    "validate_snapshot_instance",
]
