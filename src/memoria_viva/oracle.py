"""Isolated comparison of production outputs with human-authored oracles."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal

from .attention import AttentionRankingResult
from .canonical import canonical_json_bytes, sha256_digest, to_plain_json_value
from .contracts import SchemaRegistry
from .graph_delta import GRAPH_DELTA_SCHEMA_ID, GraphDelta


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
    oracle_version: str
    oracle_digest: str
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


@dataclass(frozen=True)
class GraphDeltaOracleIssue:
    """One stable semantic GraphDelta comparison finding."""

    result: OracleStatus
    error_code: str
    semantic_key: str | None
    pointer: str
    message: str


@dataclass(frozen=True)
class GraphDeltaComparison:
    """Immutable semantic comparison kept outside production generation."""

    status: OracleStatus
    oracle_id: str
    oracle_version: str
    oracle_digest: str
    computed_graph_delta_id: str
    expected_change_count: int
    computed_change_count: int
    matched_change_count: int
    first_divergence: str | None
    issues: tuple[GraphDeltaOracleIssue, ...]

    def to_plain_json(self) -> dict[str, Any]:
        plain = to_plain_json_value(self)
        if not isinstance(plain, dict):
            raise TypeError("GraphDelta comparison must project to a JSON object")
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
        oracle_version=str(
            expected_oracle.get("schema_version", "UNVERSIONED-TEST-ORACLE")
        ),
        oracle_digest=sha256_digest(expected_oracle),
        computed_ranking_id=computed.ranking["attention_ranking_id"],
        expected_order=expected_order,
        computed_order=computed_order,
        first_divergence=first_divergence,
        assertion_count=assertion_count,
        issues=tuple(issues),
    )


def compare_graph_delta_oracle(
    computed: GraphDelta | Mapping[str, Any],
    expected_oracle: Mapping[str, Any],
) -> GraphDeltaComparison:
    """Compare semantic change tuples after production GraphDelta completion.

    Oracle change IDs and placeholder digests are intentionally ignored. Human
    expectation evidence marks oracle provenance and is not required as a
    production-generation input.
    """

    if isinstance(computed, GraphDelta):
        production = computed.to_plain_json()
        relationship_semantics = computed.relationship_semantics
    elif isinstance(computed, Mapping):
        production = to_plain_json_value(computed)
        relationship_semantics = {}
    else:
        raise TypeError("computed must be GraphDelta or a GraphDelta mapping")
    if not isinstance(expected_oracle, Mapping):
        raise TypeError("expected_oracle must be a validated mapping")

    oracle_id = str(expected_oracle.get("graph_delta_id", "UNKNOWN-ORACLE"))
    oracle_version = str(expected_oracle.get("schema_version", "UNKNOWN"))
    oracle_digest = _graph_oracle_digest(expected_oracle)
    computed_id = str(production.get("graph_delta_id", "UNKNOWN-GRAPH-DELTA"))
    issues: list[GraphDeltaOracleIssue] = []

    production_errors = _graph_contract_registry().validation_errors(
        GRAPH_DELTA_SCHEMA_ID,
        production,
        instance_path="memory/graph-delta",
        object_id=computed_id,
    )
    if production_errors:
        issues.extend(
            _graph_issue(
                "BLOCKED",
                "INVALID_PRODUCTION_GRAPH_DELTA",
                None,
                error.pointer,
                error.message,
            )
            for error in production_errors
        )
        return _graph_comparison_result(
            oracle_id,
            oracle_version,
            oracle_digest,
            computed_id,
            len(expected_oracle.get("changes", ())),
            len(production.get("changes", ())),
            0,
            issues,
        )

    expected_changes = tuple(expected_oracle.get("changes", ()))
    production_changes = tuple(production["changes"])
    expected_descriptors = _graph_descriptors(expected_changes, {}, oracle=True)
    production_descriptors = _graph_descriptors(
        production_changes,
        relationship_semantics,
        oracle=False,
    )
    if expected_descriptors is None or production_descriptors is None:
        issues.append(
            _graph_issue(
                "BLOCKED",
                "UNRESOLVED_RELATIONSHIP_SEMANTICS",
                None,
                "/changes",
                "one or more relationship changes cannot be reduced to typed endpoints",
            )
        )
        return _graph_comparison_result(
            oracle_id,
            oracle_version,
            oracle_digest,
            computed_id,
            len(expected_changes),
            len(production_changes),
            0,
            issues,
        )

    production_by_key: dict[tuple[str, ...], list[tuple[int, Mapping[str, Any]]]] = {}
    for index, (key, change) in enumerate(production_descriptors):
        production_by_key.setdefault(key, []).append((index, change))

    matched_production: set[int] = set()
    matched_count = 0
    for expected_index, (key, expected) in enumerate(expected_descriptors):
        pointer = f"/changes/{expected_index}"
        candidates = production_by_key.get(key, ())
        available = tuple(item for item in candidates if item[0] not in matched_production)
        if not available:
            issues.append(
                _graph_issue(
                    "FAIL",
                    "EXPECTED_GRAPH_CHANGE_MISSING",
                    _semantic_key_text(key),
                    pointer,
                    "expected semantic change is absent from production GraphDelta",
                )
            )
            continue
        production_index, actual = available[0]
        matched_production.add(production_index)
        matched_count += 1
        _compare_graph_change_fields(
            key,
            expected,
            actual,
            pointer,
            issues,
        )

    for index, (key, change) in enumerate(production_descriptors):
        if index in matched_production:
            continue
        result: OracleStatus = (
            "FAIL" if change["affected_kind"] == "RELATIONSHIP" else "HUMAN_REVIEW_REQUIRED"
        )
        issues.append(
            _graph_issue(
                result,
                (
                    "UNAPPROVED_RELATIONSHIP_CHANGE"
                    if result == "FAIL"
                    else "STRONGER_UNSUPPORTED_OBJECT_CHANGE"
                ),
                _semantic_key_text(key),
                f"/production/changes/{index}",
                "production GraphDelta contains a semantic change absent from the human oracle",
            )
        )

    return _graph_comparison_result(
        oracle_id,
        oracle_version,
        oracle_digest,
        computed_id,
        len(expected_changes),
        len(production_changes),
        matched_count,
        issues,
    )


def _graph_descriptors(
    changes: tuple[Mapping[str, Any], ...],
    relationship_semantics: Mapping[str, Mapping[str, str]],
    *,
    oracle: bool,
) -> tuple[tuple[tuple[str, ...], Mapping[str, Any]], ...] | None:
    descriptors: list[tuple[tuple[str, ...], Mapping[str, Any]]] = []
    for change in changes:
        category = change["category"]
        if change["affected_kind"] == "OBJECT":
            affected = change["affected_ref"]
            entity_type = affected["entity_type"]
            entity_id = affected["entity_id"]
            if category == "UPDATED" and entity_type in {
                "AttentionRanking",
                "ExpectedAttentionRanking",
            }:
                key = (category, "OBJECT", "RANKING_TRANSITION")
            elif category == "UPDATED" and entity_type == "Snapshot":
                key = (category, "OBJECT", "SNAPSHOT_CAPACITY_TRANSITION")
            else:
                key = (category, "OBJECT", entity_type, entity_id)
        else:
            relationship_id = change["affected_relationship_id"]
            semantics = (
                _parse_expected_relationship(relationship_id)
                if oracle
                else relationship_semantics.get(relationship_id)
            )
            if semantics is None:
                return None
            key = (
                category,
                "RELATIONSHIP",
                semantics["relationship_type"],
                semantics["from_id"],
                semantics["to_id"],
            )
        descriptors.append((key, change))
    return tuple(descriptors)


def _parse_expected_relationship(
    relationship_id: str,
) -> Mapping[str, str] | None:
    if not relationship_id.startswith("REL-"):
        return None
    body = relationship_id[4:]
    for marker, relationship_type in (
        ("-DEPENDS-ON-", "depends_on"),
        ("-CONFLICTS-", "conflicts_with"),
        ("-DISPLACES-", "displaces"),
    ):
        if marker in body:
            from_id, to_id = body.split(marker, 1)
            return {
                "relationship_type": relationship_type,
                "from_id": from_id,
                "to_id": to_id,
            }
    return None


def _compare_graph_change_fields(
    key: tuple[str, ...],
    expected: Mapping[str, Any],
    actual: Mapping[str, Any],
    pointer: str,
    issues: list[GraphDeltaOracleIssue],
) -> None:
    key_text = _semantic_key_text(key)
    if actual["conditionality"] != expected["conditionality"]:
        result: OracleStatus = (
            "HUMAN_REVIEW_REQUIRED"
            if expected["conditionality"] == "CONDITIONAL"
            and actual["conditionality"] != "CONDITIONAL"
            else "FAIL"
        )
        issues.append(
            _graph_issue(
                result,
                "CONDITIONALITY_MISMATCH",
                key_text,
                f"{pointer}/conditionality",
                f"expected {expected['conditionality']}, computed {actual['conditionality']}",
            )
        )

    expected_execution = expected["actual_execution_state"]
    actual_execution = actual["actual_execution_state"]
    if actual_execution != expected_execution:
        stronger = (
            expected_execution in {"UNKNOWN", "NOT_EXECUTED"}
            and actual_execution in {"AUTHORIZED", "EXECUTED"}
        )
        issues.append(
            _graph_issue(
                "HUMAN_REVIEW_REQUIRED" if stronger else "FAIL",
                "EXECUTION_STATE_MISMATCH",
                key_text,
                f"{pointer}/actual_execution_state",
                f"expected {expected_execution}, computed {actual_execution}",
            )
        )

    expected_evidence = {
        reference
        for reference in expected["evidence_refs"]
        if reference != "EV-HUMAN-EXPECTATION"
    }
    missing_evidence = sorted(expected_evidence - set(actual["evidence_refs"]))
    if missing_evidence:
        issues.append(
            _graph_issue(
                "FAIL",
                "REQUIRED_EVIDENCE_MISSING",
                key_text,
                f"{pointer}/evidence_refs",
                "production evidence is missing: " + ", ".join(missing_evidence),
            )
        )

    if expected["uncertainty"] and not actual["uncertainty"]:
        issues.append(
            _graph_issue(
                "FAIL",
                "EXPECTED_UNCERTAINTY_NOT_PRESERVED",
                key_text,
                f"{pointer}/uncertainty",
                "expected uncertainty is absent from production output",
            )
        )
    elif not expected["uncertainty"] and actual["uncertainty"]:
        issues.append(
            _graph_issue(
                "HUMAN_REVIEW_REQUIRED",
                "STRONGER_UNSUPPORTED_UNCERTAINTY",
                key_text,
                f"{pointer}/uncertainty",
                "production introduces uncertainty absent from the oracle",
            )
        )

    if expected["condition_state"] in {"PENDING", "UNKNOWN"} and actual[
        "condition_state"
    ] == "SATISFIED":
        issues.append(
            _graph_issue(
                "HUMAN_REVIEW_REQUIRED",
                "STRONGER_UNSUPPORTED_CONDITION_CLAIM",
                key_text,
                f"{pointer}/condition_state",
                "production claims a condition is satisfied where the oracle does not",
            )
        )

    category = expected["category"]
    if category == "DISPLACED":
        required = {
            "condition": actual["condition"],
            "opportunity_cost": actual["opportunity_cost"],
            "repair_requirement": actual["repair_requirement"],
            "authority_scope": actual["authority_scope"],
            "uncertainty": actual["uncertainty"],
        }
        missing = [name for name, value in required.items() if not value or value == "UNKNOWN"]
        if missing:
            issues.append(
                _graph_issue(
                    "BLOCKED",
                    "DISPLACEMENT_SEMANTICS_INCOMPLETE",
                    key_text,
                    pointer,
                    "conditional displacement is missing: " + ", ".join(missing),
                )
            )
        if actual_execution == "EXECUTED":
            issues.append(
                _graph_issue(
                    "HUMAN_REVIEW_REQUIRED",
                    "UNSUPPORTED_EXECUTED_DISPLACEMENT",
                    key_text,
                    f"{pointer}/actual_execution_state",
                    "human expectation does not authorize an executed-displacement claim",
                )
            )

    state_label = str(actual["expected_new_state"].get("state_label") or "")
    if any(token in state_label.upper() for token in ("COMPLETED", "VERIFIED")) and not any(
        token in str(expected["expected_new_state"].get("state_label") or "").upper()
        for token in ("COMPLETED", "VERIFIED")
    ):
        issues.append(
            _graph_issue(
                "HUMAN_REVIEW_REQUIRED",
                "STRONGER_UNSUPPORTED_STATE_CLAIM",
                key_text,
                f"{pointer}/expected_new_state/state_label",
                "production state label introduces unsupported completion or verification",
            )
        )


def _graph_comparison_result(
    oracle_id: str,
    oracle_version: str,
    oracle_digest: str,
    computed_id: str,
    expected_count: int,
    computed_count: int,
    matched_count: int,
    issues: list[GraphDeltaOracleIssue],
) -> GraphDeltaComparison:
    status = _overall_graph_status(issues)
    first_divergence = issues[0].message if issues else None
    return GraphDeltaComparison(
        status=status,
        oracle_id=oracle_id,
        oracle_version=oracle_version,
        oracle_digest=oracle_digest,
        computed_graph_delta_id=computed_id,
        expected_change_count=expected_count,
        computed_change_count=computed_count,
        matched_change_count=matched_count,
        first_divergence=first_divergence,
        issues=tuple(issues),
    )


def _overall_graph_status(issues: list[GraphDeltaOracleIssue]) -> OracleStatus:
    statuses = {issue.result for issue in issues}
    if "BLOCKED" in statuses:
        return "BLOCKED"
    if "FAIL" in statuses:
        return "FAIL"
    if "HUMAN_REVIEW_REQUIRED" in statuses:
        return "HUMAN_REVIEW_REQUIRED"
    return "PASS"


def _graph_issue(
    result: OracleStatus,
    error_code: str,
    semantic_key: str | None,
    pointer: str,
    message: str,
) -> GraphDeltaOracleIssue:
    return GraphDeltaOracleIssue(result, error_code, semantic_key, pointer, message)


def _semantic_key_text(key: tuple[str, ...]) -> str:
    return "|".join(key)


def _graph_oracle_digest(expected_oracle: Mapping[str, Any]) -> str:
    projection = to_plain_json_value(expected_oracle)
    placeholder = projection.get("transition_digest")
    if isinstance(placeholder, str) and placeholder.startswith("UNKNOWN"):
        projection.pop("transition_digest")
    return sha256_digest(projection)


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


@lru_cache(maxsize=1)
def _graph_contract_registry() -> SchemaRegistry:
    return SchemaRegistry(Path(__file__).resolve().parents[2] / "schemas")
