"""Ordinal-only comparison of computed rankings with human expectations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal

from .attention import AttentionRankingResult
from .canonical import canonical_json_bytes, to_plain_json_value


OracleStatus = Literal["PASS", "FAIL", "BLOCKED", "HUMAN_REVIEW_REQUIRED"]


@dataclass(frozen=True)
class OracleIssue:
    """One deterministic comparison finding."""

    result: OracleStatus
    error_code: str
    attention_item_id: str | None
    pointer: str
    message: str


@dataclass(frozen=True)
class OracleComparison:
    """Immutable ordinal comparison; never an input to production scoring."""

    status: OracleStatus
    oracle_id: str
    computed_ranking_id: str
    expected_order: tuple[str, ...]
    computed_order: tuple[str, ...]
    first_divergence: str | None
    assertion_count: int
    issues: tuple[OracleIssue, ...]

    def to_plain_json(self) -> dict[str, Any]:
        plain = to_plain_json_value(self)
        if not isinstance(plain, dict):
            raise TypeError("oracle comparison must project to a JSON object")
        return plain

    def canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self)


def compare_ordinal_oracle(
    computed: AttentionRankingResult,
    expected_oracle: Mapping[str, Any],
    *,
    previous_computed: AttentionRankingResult | None = None,
) -> OracleComparison:
    """Compare structured ordinal assertions after production computation.

    Human narrative is not interpreted as a scoring rule. Structured fields are
    compared directly. Free-text uncertainty is compared as preserved-vs-absent
    because the current contracts do not provide stable uncertainty identities.
    """

    if not isinstance(computed, AttentionRankingResult):
        raise TypeError("computed must be an AttentionRankingResult")
    if not isinstance(expected_oracle, Mapping):
        raise TypeError("expected_oracle must be a validated mapping")

    expected_items = tuple(expected_oracle["expected_ordered_items"])
    expected_order = tuple(
        item["stable_attention_item_reference"] for item in expected_items
    )
    computed_items = {
        item["attention_item_id"]: item for item in computed.ranking["items"]
    }
    computed_order = tuple(
        item["attention_item_id"] for item in computed.ranking["items"]
    )
    blocked = {
        item["attention_item_id"]: item for item in computed.blocked_items
    }
    previous_items = (
        {
            item["attention_item_id"]: item
            for item in previous_computed.ranking["items"]
        }
        if previous_computed is not None
        else {}
    )
    issues: list[OracleIssue] = []
    assertion_count = 0

    expected_role = "T0" if computed.ranking["ranking_context"] == "before" else "T1"
    assertion_count += 1
    if expected_oracle["snapshot_role"] != expected_role:
        issues.append(
            _issue(
                "FAIL",
                "ORACLE_SNAPSHOT_ROLE_MISMATCH",
                None,
                "/snapshot_role",
                f"expected role {expected_role}, received {expected_oracle['snapshot_role']}",
            )
        )

    for index, expected in enumerate(expected_items):
        item_id = expected["stable_attention_item_reference"]
        pointer = f"/expected_ordered_items/{index}"
        actual = computed_items.get(item_id)
        blocked_item = blocked.get(item_id)

        assertion_count += 1
        if blocked_item is not None:
            issues.append(
                _issue(
                    "BLOCKED",
                    "REQUIRED_ITEM_HAS_UNKNOWN_COMPONENT",
                    item_id,
                    pointer,
                    "required production item has no score or rank; missing components: "
                    + ", ".join(blocked_item["missing_components"]),
                )
            )
        elif actual is None:
            issues.append(
                _issue(
                    "FAIL",
                    "EXPECTED_ITEM_MISSING",
                    item_id,
                    pointer,
                    "expected attention item is absent from both computed and blocked results",
                )
            )
        else:
            if actual["rank"] != expected["expected_rank"]:
                issues.append(
                    _issue(
                        "FAIL",
                        "EXPECTED_RANK_MISMATCH",
                        item_id,
                        f"{pointer}/expected_rank",
                        f"expected rank {expected['expected_rank']}, computed rank {actual['rank']}",
                    )
                )

        assertion_count += 1
        direction_holds, direction_reason = _direction_holds(
            expected["expected_score_direction"],
            actual,
            previous_items.get(item_id),
            computed.ranking["ranking_context"],
        )
        if not direction_holds:
            result: OracleStatus = "BLOCKED" if blocked_item is not None else "FAIL"
            issues.append(
                _issue(
                    result,
                    "EXPECTED_DIRECTION_MISMATCH",
                    item_id,
                    f"{pointer}/expected_score_direction",
                    direction_reason,
                )
            )

        assertion_count += 1
        actual_protected = _actual_protected_refs(computed, item_id, actual, blocked_item)
        if set(actual_protected) != set(expected["expected_protected_references"]):
            issues.append(
                _issue(
                    "BLOCKED" if blocked_item is not None else "FAIL",
                    "EXPECTED_PROTECTION_MISMATCH",
                    item_id,
                    f"{pointer}/expected_protected_references",
                    f"expected {expected['expected_protected_references']}, computed {list(actual_protected)}",
                )
            )

        assertion_count += 1
        actual_displaced = tuple(actual["displaced_commitment_refs"]) if actual else ()
        if set(actual_displaced) != set(expected["expected_displaced_references"]):
            issues.append(
                _issue(
                    "BLOCKED" if blocked_item is not None else "FAIL",
                    "EXPECTED_DISPLACEMENT_MISMATCH",
                    item_id,
                    f"{pointer}/expected_displaced_references",
                    f"expected {expected['expected_displaced_references']}, computed {list(actual_displaced)}",
                )
            )

        assertion_count += 1
        expected_uncertainty = tuple(expected["expected_uncertainty"])
        actual_uncertainty = (
            tuple(actual["uncertainty"])
            if actual is not None
            else tuple(blocked_item["uncertainty"])
            if blocked_item is not None
            else ()
        )
        if expected_uncertainty and not actual_uncertainty:
            issues.append(
                _issue(
                    "BLOCKED" if blocked_item is not None else "FAIL",
                    "EXPECTED_UNCERTAINTY_NOT_PRESERVED",
                    item_id,
                    f"{pointer}/expected_uncertainty",
                    "oracle requires visible uncertainty, but computed item has none",
                )
            )
        elif not expected_uncertainty and actual_uncertainty:
            issues.append(
                _issue(
                    "HUMAN_REVIEW_REQUIRED",
                    "STRONGER_UNSUPPORTED_UNCERTAINTY",
                    item_id,
                    f"{pointer}/expected_uncertainty",
                    "computed output introduces uncertainty not represented by the oracle",
                )
            )

        assertion_count += 1
        actual_approval = computed.approval_requirements.get(item_id)
        if actual_approval != expected["expected_approval_requirement"]:
            issues.append(
                _issue(
                    "BLOCKED" if blocked_item is not None else "FAIL",
                    "EXPECTED_APPROVAL_MISMATCH",
                    item_id,
                    f"{pointer}/expected_approval_requirement",
                    f"expected {expected['expected_approval_requirement']}, computed {actual_approval}",
                )
            )

    extra = tuple(item_id for item_id in computed_order if item_id not in expected_order)
    assertion_count += 1
    if extra:
        issues.append(
            _issue(
                "FAIL",
                "UNEXPECTED_COMPUTED_ITEMS",
                None,
                "/expected_ordered_items",
                "computed ranking includes unexpected items: " + ", ".join(extra),
            )
        )

    assertion_count += 1
    if computed_order != expected_order:
        issues.append(
            _issue(
                "BLOCKED" if any(item_id in blocked for item_id in expected_order) else "FAIL",
                "EXPECTED_ORDER_MISMATCH",
                None,
                "/expected_ordered_items",
                f"expected ordered references {list(expected_order)}, computed {list(computed_order)}",
            )
        )

    first_divergence = _first_divergence(expected_order, computed_order, blocked)
    status = _overall_status(issues)
    return OracleComparison(
        status=status,
        oracle_id=expected_oracle["oracle_id"],
        computed_ranking_id=computed.ranking["attention_ranking_id"],
        expected_order=expected_order,
        computed_order=computed_order,
        first_divergence=first_divergence,
        assertion_count=assertion_count,
        issues=tuple(issues),
    )


def _direction_holds(
    direction: str,
    actual: Mapping[str, Any] | None,
    previous: Mapping[str, Any] | None,
    ranking_context: str,
) -> tuple[bool, str]:
    if ranking_context == "before" and direction == "UNCHANGED":
        return actual is not None, "baseline item must have a computed rank"
    if direction == "NEW_ENTRY":
        holds = actual is not None and previous is None
    elif direction == "REMOVED":
        holds = actual is None and previous is not None
    elif actual is None or previous is None:
        holds = False
    elif direction == "INCREASE":
        holds = actual["rank"] < previous["rank"]
    elif direction == "DECREASE":
        holds = actual["rank"] > previous["rank"]
    elif direction == "UNCHANGED":
        holds = actual["rank"] == previous["rank"]
    else:
        holds = False
    return holds, f"expected direction {direction} is not satisfied by computed and prior ranks"


def _actual_protected_refs(
    computed: AttentionRankingResult,
    item_id: str,
    actual: Mapping[str, Any] | None,
    blocked: Mapping[str, Any] | None,
) -> tuple[str, ...]:
    if actual is not None:
        return tuple(actual["protected_commitment_refs"])
    if blocked is not None and computed.ranking_bands.get(item_id) == "PROTECTED":
        return (blocked["subject_ref"]["entity_id"],)
    return ()


def _first_divergence(
    expected: tuple[str, ...],
    computed: tuple[str, ...],
    blocked: Mapping[str, Mapping[str, Any]],
) -> str | None:
    for index, expected_id in enumerate(expected):
        if expected_id in blocked:
            missing = ", ".join(blocked[expected_id]["missing_components"])
            return (
                f"rank {index + 1}: {expected_id} is unscored because required "
                f"component(s) {missing} are UNKNOWN"
            )
        actual_id = computed[index] if index < len(computed) else None
        if actual_id != expected_id:
            return f"rank {index + 1}: expected {expected_id}, computed {actual_id}"
    if len(computed) > len(expected):
        return f"rank {len(expected) + 1}: unexpected computed item {computed[len(expected)]}"
    return None


def _overall_status(issues: list[OracleIssue]) -> OracleStatus:
    statuses = {issue.result for issue in issues}
    if "BLOCKED" in statuses:
        return "BLOCKED"
    if "FAIL" in statuses:
        return "FAIL"
    if "HUMAN_REVIEW_REQUIRED" in statuses:
        return "HUMAN_REVIEW_REQUIRED"
    return "PASS"


def _issue(
    result: OracleStatus,
    error_code: str,
    attention_item_id: str | None,
    pointer: str,
    message: str,
) -> OracleIssue:
    return OracleIssue(result, error_code, attention_item_id, pointer, message)


def freeze_expected_oracle(value: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return a detached immutable expectation for comparator tests or callers."""

    return _deep_freeze(to_plain_json_value(value))


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {key: _deep_freeze(child) for key, child in sorted(value.items())}
        )
    if isinstance(value, list):
        return tuple(_deep_freeze(child) for child in value)
    if isinstance(value, tuple):
        return tuple(_deep_freeze(child) for child in value)
    return value
