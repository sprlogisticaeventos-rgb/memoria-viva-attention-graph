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
    OracleComparison,
    OracleIssue,
    compare_ordinal_oracle,
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
    "OracleBundle",
    "OracleComparison",
    "OracleIssue",
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
    "canonical_json_bytes",
    "compare_ordinal_oracle",
    "compute_attention_rankings",
    "finalize_snapshot",
    "runtime_input_bundle_digest",
    "load_attention_feature_policy",
    "sha256_digest",
    "sha256_hex",
    "snapshot_state_projection",
    "to_plain_json_value",
    "validate_snapshot_instance",
]
