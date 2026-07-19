"""Repository canonical JSON and SHA-256 contract.

``MV_CANONICAL_JSON_V1`` is intentionally scoped to Python 3.12. It is not an
RFC 8785 implementation. The contract uses UTF-8, lexicographically sorted
object keys, no insignificant whitespace, unescaped Unicode, semantic array
order, and Python 3.12's finite JSON-number rendering.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from typing import Any


MV_CANONICAL_JSON_V1 = "MV_CANONICAL_JSON_V1"


class CanonicalJsonError(ValueError):
    """Raised when a value cannot be represented by canonical JSON V1."""


def to_plain_json_value(value: Any) -> Any:
    """Return a detached JSON-compatible projection without mutating input."""

    if value is None or isinstance(value, (bool, str, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CanonicalJsonError("canonical JSON requires finite numbers")
        return value
    if isinstance(value, Mapping):
        keys = tuple(value.keys())
        if not all(isinstance(key, str) for key in keys):
            raise CanonicalJsonError("canonical JSON object keys must be strings")
        return {key: to_plain_json_value(value[key]) for key in sorted(keys)}
    if isinstance(value, (list, tuple)):
        return [to_plain_json_value(item) for item in value]
    if is_dataclass(value) and not isinstance(value, type):
        parameters = getattr(type(value), "__dataclass_params__", None)
        if parameters is None or not parameters.frozen:
            raise CanonicalJsonError("only frozen dataclasses are supported")
        return {
            field.name: to_plain_json_value(getattr(value, field.name))
            for field in fields(value)
        }
    raise CanonicalJsonError(
        f"unsupported canonical JSON type: {type(value).__name__}"
    )


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize a semantic value according to ``MV_CANONICAL_JSON_V1``."""

    plain = to_plain_json_value(value)
    return json.dumps(
        plain,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_hex(value: Any) -> str:
    """Return the lowercase SHA-256 hexadecimal digest of canonical bytes."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_digest(value: Any) -> str:
    """Return a stable digest in ``sha256:<64 lowercase hex>`` form."""

    return f"sha256:{sha256_hex(value)}"
