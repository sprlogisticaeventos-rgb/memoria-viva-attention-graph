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
    SnapshotT0,
    build_snapshot_t0,
    runtime_input_bundle_digest,
    snapshot_state_projection,
)

__all__ = [
    "BundleWarning",
    "CanonicalJsonError",
    "ContractIssue",
    "ContractValidationError",
    "FixtureBundleError",
    "FixtureBundleLoader",
    "OracleBundle",
    "MV_CANONICAL_JSON_V1",
    "RuntimeBundle",
    "SnapshotT0",
    "SchemaRegistrationError",
    "SchemaRegistry",
    "build_snapshot_t0",
    "canonical_json_bytes",
    "runtime_input_bundle_digest",
    "sha256_digest",
    "sha256_hex",
    "snapshot_state_projection",
    "to_plain_json_value",
]
