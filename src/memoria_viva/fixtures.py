"""Immutable runtime and human-oracle fixture bundle loaders."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from .contracts import ContractError, ContractIssue, SchemaRegistry


COMMON_ID = "urn:memoria-viva:attention-graph:schema:common:1.0.0"
GOAL_ID = "urn:memoria-viva:attention-graph:schema:goal:1.0.0"
PUBLIC_GOAL_SET_ID = (
    "urn:memoria-viva:attention-graph:schema:public-goal-set:1.0.0"
)
EVIDENCE_ID = "urn:memoria-viva:attention-graph:schema:evidence:1.0.0"
COMMITMENT_ID = "urn:memoria-viva:attention-graph:schema:commitment:1.0.0"
CONSTRAINT_ID = "urn:memoria-viva:attention-graph:schema:constraint:1.0.0"
SOURCE_EVENT_ID = "urn:memoria-viva:attention-graph:schema:source-event:1.0.0"
PRIVACY_MANIFEST_ID = (
    "urn:memoria-viva:attention-graph:schema:privacy-manifest:1.0.0"
)
ATTENTION_POLICY_ID = (
    "urn:memoria-viva:attention-graph:schema:attention-policy:1.0.0"
)
EXPECTED_RANKING_ID = (
    "urn:memoria-viva:attention-graph:schema:expected-attention-ranking:1.0.0"
)
GRAPH_DELTA_ID = "urn:memoria-viva:attention-graph:schema:graph-delta:1.0.0"

RUNTIME_FILES = (
    "public-goals.json",
    "calendar-t0.json",
    "evidence.json",
    "operational-commitments.json",
    "constraints.json",
    "openai-event.json",
    "privacy-manifest.json",
)
ORACLE_FILES = (
    "expected-ranking-before.json",
    "expected-ranking-after.json",
    "expected-graph-delta.json",
)
APPROVED_NON_LOCAL_SOURCE_IDS = (
    "SRC-CALENDAR-PUBLIC-T0",
    "SRC-COMMUNICATION-PUBLIC",
    "SRC-FOUNDER-APPROVAL",
    "SRC-GOAL-PUBLIC-COMPRESSION",
)


@dataclass(frozen=True)
class BundleWarning:
    """A stable warning that preserves an approved unknown or open boundary."""

    warning_code: str
    path: str
    object_id: str | None
    pointer: str
    message: str


@dataclass(frozen=True)
class AttentionReference:
    """An attention identity derived without loading human oracle content."""

    attention_item_id: str
    subject_kind: str
    subject_id: str


@dataclass(frozen=True)
class RuntimeIndexes:
    goals: Mapping[str, Any]
    calendar_candidates: Mapping[str, Any]
    commitments: Mapping[str, Any]
    evidence: Mapping[str, Any]
    constraints: Mapping[str, Any]
    source_events: Mapping[str, Any]
    lineage_mappings: Mapping[str, Any]
    attention_item_references: Mapping[str, AttentionReference]


@dataclass(frozen=True)
class RuntimeBundle:
    """Production input boundary. It intentionally contains no human oracle."""

    public_goal_set: Mapping[str, Any]
    calendar_t0: Mapping[str, Any]
    evidence_catalog: Mapping[str, Any]
    operational_commitments: Mapping[str, Any]
    constraints_catalog: Mapping[str, Any]
    source_event: Mapping[str, Any]
    privacy_manifest: Mapping[str, Any]
    attention_policy: Mapping[str, Any]
    indexes: RuntimeIndexes
    t0_commitment_ids: tuple[str, ...]
    prospective_t1_commitment_ids: tuple[str, ...]
    warnings: tuple[BundleWarning, ...]


@dataclass(frozen=True)
class OracleBundle:
    """Human-authored expectations, isolated from production runtime input."""

    expected_ranking_before: Mapping[str, Any]
    expected_ranking_after: Mapping[str, Any]
    expected_graph_delta: Mapping[str, Any]
    attention_item_references: Mapping[str, tuple[str, ...]]
    prospective_relationship_references: tuple[str, ...]


class FixtureBundleError(ContractError):
    """Raised when fixture structure, identity, or references are invalid."""


class FixtureBundleLoader:
    """Load the committed fixture into separate immutable input boundaries."""

    def __init__(
        self,
        repository_root: Path,
        *,
        schema_registry: SchemaRegistry | None = None,
    ):
        self._root = Path(repository_root).resolve()
        self._fixture_directory = self._root / "fixtures" / "founder-hackathon"
        self._registry = schema_registry or SchemaRegistry(self._root / "schemas")

    def load_runtime_bundle(self) -> RuntimeBundle:
        """Load and validate only inputs available to future production runtime."""

        documents = {
            name: self._load_json(self._fixture_directory / name)
            for name in RUNTIME_FILES
        }
        policy = self._load_json(self._root / "config" / "attention-policy.v1.json")

        issues: list[ContractIssue] = []
        self._validate_runtime_contracts(documents, policy, issues)
        if issues:
            raise FixtureBundleError(issues)

        indexes = self._build_runtime_indexes(documents, issues)
        self._validate_runtime_references(documents, indexes, issues)
        self._validate_runtime_invariants(documents, policy, indexes, issues)
        if issues:
            raise FixtureBundleError(issues)

        warnings = self._runtime_warnings(documents, policy)
        return RuntimeBundle(
            public_goal_set=_deep_freeze(documents["public-goals.json"]),
            calendar_t0=_deep_freeze(documents["calendar-t0.json"]),
            evidence_catalog=_deep_freeze(documents["evidence.json"]),
            operational_commitments=_deep_freeze(
                documents["operational-commitments.json"]
            ),
            constraints_catalog=_deep_freeze(documents["constraints.json"]),
            source_event=_deep_freeze(documents["openai-event.json"]),
            privacy_manifest=_deep_freeze(documents["privacy-manifest.json"]),
            attention_policy=_deep_freeze(policy),
            indexes=_freeze_runtime_indexes(indexes),
            t0_commitment_ids=("CMT-03", "CMT-04", "CMT-05"),
            prospective_t1_commitment_ids=("CMT-01", "CMT-02"),
            warnings=warnings,
        )

    def load_oracle_bundle(self, runtime: RuntimeBundle) -> OracleBundle:
        """Load human expectations separately and validate their stable references."""

        documents = {
            name: self._load_json(self._fixture_directory / name)
            for name in ORACLE_FILES
        }
        issues: list[ContractIssue] = []
        self._validate_oracle_contracts(documents, issues)
        if issues:
            raise FixtureBundleError(issues)
        attention_index, relationships = self._validate_oracle_references(
            documents, runtime, issues
        )
        self._validate_oracle_invariants(documents, issues)
        if issues:
            raise FixtureBundleError(issues)
        return OracleBundle(
            expected_ranking_before=_deep_freeze(
                documents["expected-ranking-before.json"]
            ),
            expected_ranking_after=_deep_freeze(
                documents["expected-ranking-after.json"]
            ),
            expected_graph_delta=_deep_freeze(
                documents["expected-graph-delta.json"]
            ),
            attention_item_references=_deep_freeze(attention_index),
            prospective_relationship_references=relationships,
        )

    def _load_json(self, path: Path) -> Any:
        display_path = self._display_path(path)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise FixtureBundleError(
                [
                    ContractIssue(
                        "MISSING_FIXTURE_FILE",
                        display_path,
                        None,
                        "",
                        "required fixture-bundle file is missing",
                    )
                ]
            ) from error
        except json.JSONDecodeError as error:
            raise FixtureBundleError(
                [
                    ContractIssue(
                        "INVALID_JSON",
                        display_path,
                        None,
                        "",
                        f"fixture is not valid JSON at line {error.lineno}, column {error.colno}",
                    )
                ]
            ) from error

    def _validate_runtime_contracts(
        self,
        documents: Mapping[str, Any],
        policy: Any,
        issues: list[ContractIssue],
    ) -> None:
        public_goals = documents["public-goals.json"]
        self._collect_validation(
            PUBLIC_GOAL_SET_ID, public_goals, "fixtures/founder-hackathon/public-goals.json", issues
        )
        for index, goal in enumerate(public_goals.get("goals", ())):
            self._collect_validation(
                GOAL_ID,
                goal,
                "fixtures/founder-hackathon/public-goals.json",
                issues,
                pointer_prefix=("goals", index),
            )

        calendar = documents["calendar-t0.json"]
        candidates = calendar.get("candidates")
        if not isinstance(candidates, list):
            issues.append(
                _issue(
                    "INVALID_THIN_CONTAINER",
                    "fixtures/founder-hackathon/calendar-t0.json",
                    None,
                    ("candidates",),
                    "candidates must be an array",
                )
            )
        else:
            for index, candidate in enumerate(candidates):
                self._validate_calendar_candidate(candidate, index, issues)

        self._validate_entity_container(
            documents["evidence.json"],
            "evidence",
            EVIDENCE_ID,
            "fixtures/founder-hackathon/evidence.json",
            issues,
        )
        self._validate_entity_container(
            documents["operational-commitments.json"],
            "commitments",
            COMMITMENT_ID,
            "fixtures/founder-hackathon/operational-commitments.json",
            issues,
        )
        self._validate_entity_container(
            documents["constraints.json"],
            "constraints",
            CONSTRAINT_ID,
            "fixtures/founder-hackathon/constraints.json",
            issues,
        )
        self._collect_validation(
            SOURCE_EVENT_ID,
            documents["openai-event.json"],
            "fixtures/founder-hackathon/openai-event.json",
            issues,
        )
        self._collect_validation(
            PRIVACY_MANIFEST_ID,
            documents["privacy-manifest.json"],
            "fixtures/founder-hackathon/privacy-manifest.json",
            issues,
        )
        self._collect_validation(
            ATTENTION_POLICY_ID,
            policy,
            "config/attention-policy.v1.json",
            issues,
        )

    def _validate_oracle_contracts(
        self, documents: Mapping[str, Any], issues: list[ContractIssue]
    ) -> None:
        for name in ("expected-ranking-before.json", "expected-ranking-after.json"):
            self._collect_validation(
                EXPECTED_RANKING_ID,
                documents[name],
                f"fixtures/founder-hackathon/{name}",
                issues,
            )
        self._collect_validation(
            GRAPH_DELTA_ID,
            documents["expected-graph-delta.json"],
            "fixtures/founder-hackathon/expected-graph-delta.json",
            issues,
        )

    def _validate_calendar_candidate(
        self, candidate: Any, index: int, issues: list[ContractIssue]
    ) -> None:
        path = "fixtures/founder-hackathon/calendar-t0.json"
        prefix = ("candidates", index)
        required = (
            "candidate_id",
            "public_title",
            "scheduled_start",
            "scheduled_end",
            "duration_class",
            "lifecycle_status",
            "mobility_policy",
            "ranking_eligibility",
            "inclusion_state",
            "exclusion_reason",
            "evidence_ref",
            "public_evidence_summary",
            "supported_goal_ref",
            "epistemic_state",
            "uncertainty",
            "privacy_classification",
            "source_classification",
            "eligibility_scope",
            "timestamp_provenance",
            "attention_lineage_mapping",
        )
        if not isinstance(candidate, dict):
            issues.append(
                _issue(
                    "INVALID_CALENDAR_CANDIDATE",
                    path,
                    None,
                    prefix,
                    "Calendar candidate must be an object",
                )
            )
            return
        missing = [field for field in required if field not in candidate]
        if missing:
            issues.append(
                _issue(
                    "MISSING_CALENDAR_FIELD",
                    path,
                    candidate.get("candidate_id"),
                    prefix,
                    "Calendar candidate is missing required structural fields",
                )
            )
            return
        value_contracts = (
            ("candidate_id", f"{COMMON_ID}#/$defs/repository_safe_reference"),
            ("scheduled_start", f"{COMMON_ID}#/$defs/timestamp"),
            ("scheduled_end", f"{COMMON_ID}#/$defs/timestamp"),
            ("mobility_policy", f"{COMMON_ID}#/$defs/mobility_state"),
            ("evidence_ref", f"{COMMON_ID}#/$defs/repository_safe_reference"),
            (
                "supported_goal_ref",
                f"{COMMON_ID}#/$defs/nullable_repository_safe_reference",
            ),
            ("epistemic_state", f"{COMMON_ID}#/$defs/epistemic_state"),
            ("uncertainty", f"{COMMON_ID}#/$defs/uncertainty"),
            (
                "privacy_classification",
                f"{COMMON_ID}#/$defs/privacy_classification",
            ),
        )
        for field, schema_id in value_contracts:
            self._collect_validation(
                schema_id,
                candidate[field],
                path,
                issues,
                object_id=candidate["candidate_id"],
                pointer_prefix=(*prefix, field),
            )
        lineage = candidate["attention_lineage_mapping"]
        if lineage is not None:
            self._collect_validation(
                f"{COMMON_ID}#/$defs/lineage_mapping",
                lineage,
                path,
                issues,
                object_id=lineage.get("mapping_id") if isinstance(lineage, dict) else None,
                pointer_prefix=(*prefix, "attention_lineage_mapping"),
            )
        allowed_values = {
            "duration_class": {"SHORT", "MEDIUM", "LONG", "MULTI_DAY_WINDOW"},
            "lifecycle_status": {"ACTIVE", "UNRESOLVED"},
            "ranking_eligibility": {"ELIGIBLE", "INELIGIBLE"},
            "inclusion_state": {
                "ACTIVE_RANKING_CANDIDATE",
                "EXCLUDED_BUT_RETAINED",
            },
            "source_classification": {"CALENDAR_T0_PUBLIC_CANDIDATE"},
            "eligibility_scope": {"CONTROLLED_T0_RANKING"},
            "timestamp_provenance": {"SYNTHETIC"},
        }
        for field, allowed in allowed_values.items():
            if candidate[field] not in allowed:
                issues.append(
                    _issue(
                        "INVALID_CALENDAR_VALUE",
                        path,
                        candidate["candidate_id"],
                        (*prefix, field),
                        f"{field} is outside the approved fixture vocabulary",
                    )
                )
        for field in ("public_title", "public_evidence_summary"):
            if not isinstance(candidate[field], str) or not candidate[field].strip():
                issues.append(
                    _issue(
                        "INVALID_CALENDAR_VALUE",
                        path,
                        candidate["candidate_id"],
                        (*prefix, field),
                        f"{field} must be a non-empty public-safe string",
                    )
                )

    def _validate_entity_container(
        self,
        container: Any,
        collection_name: str,
        schema_id: str,
        path: str,
        issues: list[ContractIssue],
    ) -> None:
        if not isinstance(container, dict) or not isinstance(
            container.get(collection_name), list
        ):
            issues.append(
                _issue(
                    "INVALID_THIN_CONTAINER",
                    path,
                    None,
                    (collection_name,),
                    f"{collection_name} must be an array",
                )
            )
            return
        for index, entity in enumerate(container[collection_name]):
            self._collect_validation(
                schema_id,
                entity,
                path,
                issues,
                pointer_prefix=(collection_name, index),
            )

    def _collect_validation(
        self,
        schema_id: str,
        instance: Any,
        path: str,
        issues: list[ContractIssue],
        *,
        object_id: str | None = None,
        pointer_prefix: Sequence[str | int] = (),
    ) -> None:
        for issue in self._registry.validation_errors(
            schema_id,
            instance,
            instance_path=path,
            object_id=object_id,
        ):
            issues.append(
                ContractIssue(
                    issue.error_code,
                    issue.path,
                    issue.object_id,
                    _join_pointer(pointer_prefix, issue.pointer),
                    issue.message,
                )
            )

    def _build_runtime_indexes(
        self, documents: Mapping[str, Any], issues: list[ContractIssue]
    ) -> dict[str, dict[str, Any]]:
        groups = {
            "goals": _index_entities(
                documents["public-goals.json"]["goals"],
                "goal_id",
                "fixtures/founder-hackathon/public-goals.json",
                issues,
            ),
            "calendar_candidates": _index_entities(
                documents["calendar-t0.json"]["candidates"],
                "candidate_id",
                "fixtures/founder-hackathon/calendar-t0.json",
                issues,
            ),
            "commitments": _index_entities(
                documents["operational-commitments.json"]["commitments"],
                "commitment_id",
                "fixtures/founder-hackathon/operational-commitments.json",
                issues,
            ),
            "evidence": _index_entities(
                documents["evidence.json"]["evidence"],
                "evidence_id",
                "fixtures/founder-hackathon/evidence.json",
                issues,
            ),
            "constraints": _index_entities(
                documents["constraints.json"]["constraints"],
                "constraint_id",
                "fixtures/founder-hackathon/constraints.json",
                issues,
            ),
            "source_events": _index_entities(
                [documents["openai-event.json"]],
                "source_event_id",
                "fixtures/founder-hackathon/openai-event.json",
                issues,
            ),
        }
        seen: dict[str, str] = {}
        for group_name, group in groups.items():
            for object_id in group:
                if object_id in seen:
                    issues.append(
                        _issue(
                            "DUPLICATE_OBJECT_ID",
                            "fixtures/founder-hackathon",
                            object_id,
                            (),
                            f"identity is duplicated across {seen[object_id]} and {group_name}",
                        )
                    )
                seen[object_id] = group_name

        lineage_items: list[Mapping[str, Any]] = []
        for candidate in groups["calendar_candidates"].values():
            if candidate["attention_lineage_mapping"] is not None:
                lineage_items.append(candidate["attention_lineage_mapping"])
        for commitment in groups["commitments"].values():
            lineage_items.extend(commitment["lineage_mappings"])
        groups["lineage_mappings"] = _index_entities(
            lineage_items,
            "mapping_id",
            "fixtures/founder-hackathon",
            issues,
        )

        attention: dict[str, AttentionReference] = {}
        for commitment_id in sorted(groups["commitments"]):
            reference = AttentionReference(
                attention_item_id=f"ATTN-{commitment_id}",
                subject_kind="Commitment",
                subject_id=commitment_id,
            )
            attention[reference.attention_item_id] = reference
        for candidate in groups["calendar_candidates"].values():
            lineage = candidate["attention_lineage_mapping"]
            if lineage is None:
                continue
            operational_ref = lineage["operational_object_ref"]
            attention_id = operational_ref["entity_id"]
            if attention_id in attention:
                issues.append(
                    _issue(
                        "DUPLICATE_ATTENTION_ID",
                        "fixtures/founder-hackathon/calendar-t0.json",
                        attention_id,
                        (),
                        "attention identity is duplicated",
                    )
                )
            attention[attention_id] = AttentionReference(
                attention_item_id=attention_id,
                subject_kind="CalendarCandidate",
                subject_id=candidate["candidate_id"],
            )
        groups["attention_item_references"] = dict(sorted(attention.items()))
        return groups

    def _validate_runtime_references(
        self,
        documents: Mapping[str, Any],
        indexes: Mapping[str, Mapping[str, Any]],
        issues: list[ContractIssue],
    ) -> None:
        for name, document in documents.items():
            for reference, pointer in _named_references(
                document, singular="evidence_ref", plural="evidence_refs"
            ):
                _require_reference(
                    reference,
                    indexes["evidence"],
                    "UNRESOLVED_EVIDENCE_REFERENCE",
                    f"fixtures/founder-hackathon/{name}",
                    pointer,
                    issues,
                )

        for goal_index, goal in enumerate(documents["public-goals.json"]["goals"]):
            for constraint_index, reference in enumerate(goal["constraint_refs"]):
                _require_reference(
                    reference,
                    indexes["constraints"],
                    "UNRESOLVED_CONSTRAINT_REFERENCE",
                    "fixtures/founder-hackathon/public-goals.json",
                    ("goals", goal_index, "constraint_refs", constraint_index),
                    issues,
                )
        for candidate_index, candidate in enumerate(
            documents["calendar-t0.json"]["candidates"]
        ):
            reference = candidate["supported_goal_ref"]
            if reference is not None:
                _require_reference(
                    reference,
                    indexes["goals"],
                    "UNRESOLVED_GOAL_REFERENCE",
                    "fixtures/founder-hackathon/calendar-t0.json",
                    ("candidates", candidate_index, "supported_goal_ref"),
                    issues,
                )
        for commitment_index, commitment in enumerate(
            documents["operational-commitments.json"]["commitments"]
        ):
            for goal_index, reference in enumerate(commitment["supported_goal_refs"]):
                _require_reference(
                    reference,
                    indexes["goals"],
                    "UNRESOLVED_GOAL_REFERENCE",
                    "fixtures/founder-hackathon/operational-commitments.json",
                    ("commitments", commitment_index, "supported_goal_refs", goal_index),
                    issues,
                )
        for goal_index, reference in enumerate(
            documents["openai-event.json"]["related_goal_refs"]
        ):
            _require_reference(
                reference,
                indexes["goals"],
                "UNRESOLVED_GOAL_REFERENCE",
                "fixtures/founder-hackathon/openai-event.json",
                ("related_goal_refs", goal_index),
                issues,
            )
        known_scope = {**indexes["goals"], **indexes["commitments"]}
        for constraint_index, constraint in enumerate(
            documents["constraints.json"]["constraints"]
        ):
            for scope_index, reference in enumerate(constraint["scope"]):
                _require_reference(
                    reference,
                    known_scope,
                    "UNRESOLVED_SCOPE_REFERENCE",
                    "fixtures/founder-hackathon/constraints.json",
                    ("constraints", constraint_index, "scope", scope_index),
                    issues,
                )
        for evidence_index, evidence in enumerate(documents["evidence.json"]["evidence"]):
            event_id = evidence["source_event_id"]
            if event_id is not None:
                _require_reference(
                    event_id,
                    indexes["source_events"],
                    "UNRESOLVED_SOURCE_EVENT_REFERENCE",
                    "fixtures/founder-hackathon/evidence.json",
                    ("evidence", evidence_index, "source_event_id"),
                    issues,
                )
        source_ids = {
            evidence["source_id"]
            for evidence in documents["evidence.json"]["evidence"]
        } | {documents["openai-event.json"]["source_id"]}
        for source_id in sorted(source_ids):
            if source_id not in APPROVED_NON_LOCAL_SOURCE_IDS:
                issues.append(
                    _issue(
                        "UNRESOLVED_SOURCE_REFERENCE",
                        "fixtures/founder-hackathon",
                        source_id,
                        (),
                        "non-local Source identity is not in the approved synthetic set",
                    )
                )
        for mapping_id, mapping in indexes["lineage_mappings"].items():
            for source_index, source_ref in enumerate(mapping["source_candidate_refs"]):
                _require_reference(
                    source_ref,
                    indexes["calendar_candidates"],
                    "UNRESOLVED_CALENDAR_REFERENCE",
                    "fixtures/founder-hackathon",
                    ("lineage_mappings", mapping_id, "source_candidate_refs", source_index),
                    issues,
                )
            operational_ref = mapping["operational_object_ref"]
            target = (
                indexes["commitments"]
                if operational_ref["entity_type"] == "Commitment"
                else indexes["attention_item_references"]
                if operational_ref["entity_type"] == "AttentionItem"
                else {}
            )
            _require_reference(
                operational_ref["entity_id"],
                target,
                "UNRESOLVED_OPERATIONAL_REFERENCE",
                "fixtures/founder-hackathon",
                ("lineage_mappings", mapping_id, "operational_object_ref", "entity_id"),
                issues,
            )

    def _validate_runtime_invariants(
        self,
        documents: Mapping[str, Any],
        policy: Mapping[str, Any],
        indexes: Mapping[str, Mapping[str, Any]],
        issues: list[ContractIssue],
    ) -> None:
        goals = indexes["goals"]
        _expect(
            tuple(goals) == ("GC-01", "GC-02", "GC-03"),
            "PUBLIC_GOAL_SET_INVALID",
            "fixtures/founder-hackathon/public-goals.json",
            "controlled public Goal set must contain exactly GC-01, GC-02, and GC-03",
            issues,
        )
        omissions = documents["public-goals.json"]["controlled_demo_omissions"]
        _expect(
            len(omissions) == 1
            and omissions[0].get("goal_reference") == "G5"
            and omissions[0].get("controlled_demo_visibility")
            == "OMITTED_FROM_CONTROLLED_DEMO"
            and omissions[0].get("operational_lifecycle_effect") == "NONE",
            "G5_OMISSION_INVALID",
            "fixtures/founder-hackathon/public-goals.json",
            "G5 must be neutrally omitted with no lifecycle effect",
            issues,
        )
        for goal in goals.values():
            completion = goal["completion_authority"]
            _expect(
                completion["artifact_existence_sufficient"] is False
                and completion["requires_all_verification_surfaces_evidenced"] is True,
                "GOAL_COMPLETION_AUTHORITY_INVALID",
                "fixtures/founder-hackathon/public-goals.json",
                "artifact existence cannot complete a Goal",
                issues,
                goal["goal_id"],
            )
            _expect(
                goal["operational_lifecycle"] != "COMPLETED",
                "UNSUPPORTED_GOAL_COMPLETION",
                "fixtures/founder-hackathon/public-goals.json",
                "fixture must not claim Goal completion",
                issues,
                goal["goal_id"],
            )

        calendar = documents["calendar-t0.json"]
        candidates = indexes["calendar_candidates"]
        active = tuple(sorted(calendar["active_ranking_candidate_refs"]))
        excluded = tuple(sorted(calendar["excluded_but_retained_refs"]))
        _expect(calendar["candidate_count"] == 10, "CALENDAR_DECLARED_COUNT_INVALID", "fixtures/founder-hackathon/calendar-t0.json", "declared Calendar candidate count must be ten", issues)
        _expect(len(candidates) == 10, "CALENDAR_COUNT_INVALID", "fixtures/founder-hackathon/calendar-t0.json", "Calendar must retain exactly ten candidates", issues)
        _expect(len(active) == 8, "ACTIVE_CALENDAR_COUNT_INVALID", "fixtures/founder-hackathon/calendar-t0.json", "Calendar must contain exactly eight active ranking candidates", issues)
        _expect(excluded == ("CMT-T0-07", "CMT-T0-08"), "EXCLUDED_CALENDAR_SET_INVALID", "fixtures/founder-hackathon/calendar-t0.json", "CMT-T0-07 and CMT-T0-08 must be excluded but retained", issues)
        _expect(
            not set(active).intersection(excluded)
            and set(active).union(excluded) == set(candidates),
            "CALENDAR_PARTITION_INVALID",
            "fixtures/founder-hackathon/calendar-t0.json",
            "active and excluded references must form a complete disjoint partition",
            issues,
        )
        for candidate_id, candidate in candidates.items():
            expected_active = candidate["inclusion_state"] == "ACTIVE_RANKING_CANDIDATE"
            _expect(
                (candidate_id in active) == expected_active,
                "CALENDAR_MEMBERSHIP_MISMATCH",
                "fixtures/founder-hackathon/calendar-t0.json",
                "candidate inclusion state must match the active/excluded indexes",
                issues,
                candidate_id,
            )
            _expect(
                (
                    candidate["ranking_eligibility"] == "ELIGIBLE"
                    and candidate["exclusion_reason"] is None
                )
                if expected_active
                else (
                    candidate["ranking_eligibility"] == "INELIGIBLE"
                    and isinstance(candidate["exclusion_reason"], str)
                    and bool(candidate["exclusion_reason"].strip())
                ),
                "CALENDAR_ELIGIBILITY_MISMATCH",
                "fixtures/founder-hackathon/calendar-t0.json",
                "ranking eligibility and exclusion reason must match membership",
                issues,
                candidate_id,
            )

        commitments = indexes["commitments"]
        _expect(
            tuple(commitments) == ("CMT-01", "CMT-02", "CMT-03", "CMT-04", "CMT-05"),
            "COMMITMENT_SET_INVALID",
            "fixtures/founder-hackathon/operational-commitments.json",
            "operational catalog must contain exactly CMT-01 through CMT-05",
            issues,
        )
        _expect(
            not set(candidates).intersection(commitments),
            "IDENTITY_DOMAIN_COLLISION",
            "fixtures/founder-hackathon",
            "Calendar and operational identities must remain distinct",
            issues,
        )
        _expect(len(indexes["lineage_mappings"]) == 9, "LINEAGE_COUNT_INVALID", "fixtures/founder-hackathon", "fixture must contain exactly nine lineage mappings", issues)
        for commitment_id in ("CMT-01", "CMT-02"):
            _expect(
                any(
                    mapping["derivation_type"] == "TRIGGER_CREATED"
                    for mapping in commitments[commitment_id]["lineage_mappings"]
                ),
                "TRIGGER_LINEAGE_MISSING",
                "fixtures/founder-hackathon/operational-commitments.json",
                "CMT-01 and CMT-02 must be trigger-created",
                issues,
                commitment_id,
            )
        for commitment_id in ("CMT-03", "CMT-04", "CMT-05"):
            _expect(
                all(
                    mapping["derivation_type"] != "TRIGGER_CREATED"
                    for mapping in commitments[commitment_id]["lineage_mappings"]
                ),
                "T0_COMMITMENT_LINEAGE_INVALID",
                "fixtures/founder-hackathon/operational-commitments.json",
                "CMT-03 through CMT-05 must exist before the trigger",
                issues,
                commitment_id,
            )
        conditional_displaceable = tuple(
            commitment_id
            for commitment_id, commitment in commitments.items()
            if commitment["mobility_policy"] == "DISPLACEABLE"
            and commitment["conditionality"] == "CONDITIONAL"
        )
        _expect(conditional_displaceable == ("CMT-04",), "CONDITIONAL_DISPLACEMENT_INVALID", "fixtures/founder-hackathon/operational-commitments.json", "CMT-04 must be the only conditionally displaceable commitment", issues)
        cmt05 = commitments["CMT-05"]
        _expect(
            cmt05["mobility_policy"] == "NEEDS_CONFIRMATION"
            and cmt05["authority_mode"] == "JOINT"
            and cmt05["approval_requirement"] == "PENDING",
            "CMT_05_CONFIRMATION_INVALID",
            "fixtures/founder-hackathon/operational-commitments.json",
            "CMT-05 must remain confirmation-required under JOINT authority",
            issues,
            "CMT-05",
        )

        events = indexes["source_events"]
        triggers = [event for event in events.values() if event["event_role"] == "TRIGGER"]
        _expect(len(events) == 1 and len(triggers) == 1, "TRIGGER_COUNT_INVALID", "fixtures/founder-hackathon/openai-event.json", "runtime bundle must contain exactly one canonical trigger and no follow-ups", issues)
        if triggers:
            _expect(
                triggers[0]["occurred_at"] is None
                and any("unknown" in value.lower() for value in triggers[0]["uncertainty"]),
                "OCCURRED_AT_UNKNOWN_NOT_PRESERVED",
                "fixtures/founder-hackathon/openai-event.json",
                "unknown occurred_at must remain null with explicit uncertainty",
                issues,
                triggers[0]["source_event_id"],
            )

        manifest = documents["privacy-manifest.json"]
        approvals = {
            item["publication_surface"]: item["approval_state"]
            for item in manifest["publication_approvals"]
        }
        required_surfaces = {
            "PUBLIC_FIXTURE",
            "REPOSITORY_DOCS",
            "DEMO_UI",
            "DEMO_VIDEO",
            "DEVPOST_SUBMISSION",
        }
        _expect(set(approvals) == required_surfaces and set(approvals.values()) == {"PENDING"}, "PUBLICATION_STATE_INVALID", "fixtures/founder-hackathon/privacy-manifest.json", "all five publication surfaces must remain PENDING", issues)
        _expect(manifest["residual_aggregation_risk"] == "LOW_MEDIUM", "RESIDUAL_RISK_INVALID", "fixtures/founder-hackathon/privacy-manifest.json", "residual aggregation risk must remain LOW_MEDIUM", issues)

        try:
            weight_total = sum(
                Decimal(str(component["weight"])) for component in policy["components"]
            )
        except (KeyError, TypeError, ValueError):
            weight_total = Decimal("NaN")
        _expect(weight_total == Decimal("1.00"), "POLICY_WEIGHT_TOTAL_INVALID", "config/attention-policy.v1.json", "policy weights must total exactly 1.00", issues)
        source_ids = {
            evidence["source_id"]
            for evidence in documents["evidence.json"]["evidence"]
        } | {documents["openai-event.json"]["source_id"]}
        _expect(
            source_ids == set(APPROVED_NON_LOCAL_SOURCE_IDS),
            "SOURCE_REFERENCE_SET_INVALID",
            "fixtures/founder-hackathon",
            "runtime bundle must preserve exactly the four approved non-local Source IDs",
            issues,
        )
        _expect(
            "attempts_to_resolve" not in json.dumps(documents, sort_keys=True),
            "DEFERRED_RELATIONSHIP_PRESENT",
            "fixtures/founder-hackathon",
            "attempts_to_resolve must not appear in the bounded fixture",
            issues,
        )

    def _validate_oracle_references(
        self,
        documents: Mapping[str, Any],
        runtime: RuntimeBundle,
        issues: list[ContractIssue],
    ) -> tuple[dict[str, tuple[str, ...]], tuple[str, ...]]:
        evidence = runtime.indexes.evidence
        for name, document in documents.items():
            for reference, pointer in _named_references(
                document, singular="evidence_ref", plural="evidence_refs"
            ):
                _require_reference(
                    reference,
                    evidence,
                    "UNRESOLVED_EVIDENCE_REFERENCE",
                    f"fixtures/founder-hackathon/{name}",
                    pointer,
                    issues,
                )

        attention: dict[str, list[str]] = {}
        object_references = {
            "Goal": runtime.indexes.goals,
            "Commitment": runtime.indexes.commitments,
            "CalendarCandidate": runtime.indexes.calendar_candidates,
            "Constraint": runtime.indexes.constraints,
            "SourceEvent": runtime.indexes.source_events,
        }
        oracle_ids = {
            documents["expected-ranking-before.json"]["oracle_id"],
            documents["expected-ranking-after.json"]["oracle_id"],
        }
        snapshot_ids = {
            documents["expected-graph-delta.json"]["previous_snapshot_id"],
            documents["expected-graph-delta.json"]["new_snapshot_id"],
        }
        for name in ("expected-ranking-before.json", "expected-ranking-after.json"):
            for index, item in enumerate(documents[name]["expected_ordered_items"]):
                reference = item["stable_attention_item_reference"]
                _require_reference(
                    reference,
                    runtime.indexes.attention_item_references,
                    "UNRESOLVED_ATTENTION_REFERENCE",
                    f"fixtures/founder-hackathon/{name}",
                    ("expected_ordered_items", index, "stable_attention_item_reference"),
                    issues,
                )
                attention.setdefault(reference, []).append(name)
                known_protected = {
                    **runtime.indexes.commitments,
                    **runtime.indexes.calendar_candidates,
                }
                for field in (
                    "expected_protected_references",
                    "expected_displaced_references",
                ):
                    for ref_index, object_ref in enumerate(item[field]):
                        _require_reference(
                            object_ref,
                            known_protected,
                            "UNRESOLVED_ORACLE_OBJECT_REFERENCE",
                            f"fixtures/founder-hackathon/{name}",
                            ("expected_ordered_items", index, field, ref_index),
                            issues,
                        )

        relationships: set[str] = set()
        delta = documents["expected-graph-delta.json"]
        for index, change in enumerate(delta["changes"]):
            if change["affected_kind"] == "RELATIONSHIP":
                relationship_id = change["affected_relationship_id"]
                if not relationship_id:
                    issues.append(_issue("MISSING_PROSPECTIVE_RELATIONSHIP", "fixtures/founder-hackathon/expected-graph-delta.json", change["change_id"], ("changes", index, "affected_relationship_id"), "relationship change requires a stable prospective relationship ID"))
                elif relationship_id in relationships:
                    issues.append(_issue("DUPLICATE_PROSPECTIVE_RELATIONSHIP", "fixtures/founder-hackathon/expected-graph-delta.json", relationship_id, ("changes", index, "affected_relationship_id"), "prospective relationship identity is duplicated"))
                else:
                    relationships.add(relationship_id)
                continue
            affected = change["affected_ref"]
            if not affected:
                issues.append(_issue("MISSING_GRAPH_OBJECT_REFERENCE", "fixtures/founder-hackathon/expected-graph-delta.json", change["change_id"], ("changes", index, "affected_ref"), "object change requires an affected object reference"))
                continue
            entity_type = affected["entity_type"]
            entity_id = affected["entity_id"]
            if entity_type == "Snapshot":
                target = {value: value for value in snapshot_ids}
            elif entity_type == "ExpectedAttentionRanking":
                target = {value: value for value in oracle_ids}
            else:
                target = object_references.get(entity_type, {})
            _require_reference(
                entity_id,
                target,
                "UNRESOLVED_GRAPH_OBJECT_REFERENCE",
                "fixtures/founder-hackathon/expected-graph-delta.json",
                ("changes", index, "affected_ref", "entity_id"),
                issues,
            )
        return (
            {key: tuple(sorted(value)) for key, value in sorted(attention.items())},
            tuple(sorted(relationships)),
        )

    def _validate_oracle_invariants(
        self, documents: Mapping[str, Any], issues: list[ContractIssue]
    ) -> None:
        forbidden_keys = {
            "score",
            "previous_score",
            "score_delta",
            "component_breakdown",
            "component_contributions",
            "calculation_digest",
            "policy_digest",
        }
        for name in ("expected-ranking-before.json", "expected-ranking-after.json"):
            found = sorted(forbidden_keys.intersection(_all_keys(documents[name])))
            _expect(
                not found,
                "PRODUCTION_SCORE_IN_HUMAN_ORACLE",
                f"fixtures/founder-hackathon/{name}",
                "human ordinal oracle must contain no numeric production-score fields",
                issues,
            )
        _expect(
            "attempts_to_resolve" not in json.dumps(documents, sort_keys=True),
            "DEFERRED_RELATIONSHIP_PRESENT",
            "fixtures/founder-hackathon",
            "attempts_to_resolve must not appear in the human oracle bundle",
            issues,
        )

    def _runtime_warnings(
        self, documents: Mapping[str, Any], policy: Mapping[str, Any]
    ) -> tuple[BundleWarning, ...]:
        source_ids = sorted(
            {
                evidence["source_id"]
                for evidence in documents["evidence.json"]["evidence"]
            }
            | {documents["openai-event.json"]["source_id"]}
        )
        warnings = [
            BundleWarning(
                "NON_LOCAL_SOURCE_REFERENCE",
                "fixtures/founder-hackathon/evidence.json",
                source_id,
                "/evidence/source_id",
                "approved synthetic Source identity has no local Source instance",
            )
            for source_id in source_ids
            if source_id in APPROVED_NON_LOCAL_SOURCE_IDS
        ]
        if policy["status"] == "draft":
            warnings.append(
                BundleWarning(
                    "POLICY_STATUS_DRAFT",
                    "config/attention-policy.v1.json",
                    policy["policy_id"],
                    "/status",
                    "attention policy remains draft",
                )
            )
        if policy["effective_at"] is None:
            warnings.append(
                BundleWarning(
                    "POLICY_EFFECTIVE_AT_UNKNOWN",
                    "config/attention-policy.v1.json",
                    policy["policy_id"],
                    "/effective_at",
                    "attention policy effective_at remains null",
                )
            )
        if all(
            approval["approval_state"] == "PENDING"
            for approval in documents["privacy-manifest.json"]["publication_approvals"]
        ):
            warnings.append(
                BundleWarning(
                    "PUBLICATION_SURFACES_PENDING",
                    "fixtures/founder-hackathon/privacy-manifest.json",
                    documents["privacy-manifest.json"]["manifest_id"],
                    "/publication_approvals",
                    "all publication surfaces remain pending",
                )
            )
        warnings.append(
            BundleWarning(
                "FINAL_COMPLIANCE_UNKNOWN",
                "fixtures/founder-hackathon/openai-event.json",
                documents["openai-event.json"]["source_event_id"],
                "/uncertainty",
                "final official compliance remains unknown",
            )
        )
        return tuple(sorted(warnings, key=_warning_sort_key))

    def _display_path(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self._root).as_posix()
        except ValueError:
            return path.name


def _index_entities(
    entities: Iterable[Mapping[str, Any]],
    identity_field: str,
    path: str,
    issues: list[ContractIssue],
) -> dict[str, Any]:
    index: dict[str, Any] = {}
    for position, entity in enumerate(entities):
        identity = entity.get(identity_field)
        if not isinstance(identity, str):
            issues.append(_issue("MISSING_OBJECT_ID", path, None, (position, identity_field), "object requires a stable string identity"))
            continue
        if identity in index:
            issues.append(_issue("DUPLICATE_OBJECT_ID", path, identity, (position, identity_field), "object identity is duplicated"))
            continue
        index[identity] = entity
    return dict(sorted(index.items()))


def _require_reference(
    reference: Any,
    index: Mapping[str, Any],
    code: str,
    path: str,
    pointer: Sequence[str | int],
    issues: list[ContractIssue],
) -> None:
    if not isinstance(reference, str) or reference not in index:
        issues.append(_issue(code, path, reference if isinstance(reference, str) else None, pointer, "stable reference does not resolve in the approved bundle"))


def _named_references(
    value: Any,
    *,
    singular: str,
    plural: str,
    path: tuple[str | int, ...] = (),
) -> Iterable[tuple[str, tuple[str | int, ...]]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = (*path, key)
            if key == singular and isinstance(child, str):
                yield child, child_path
            elif key == plural and isinstance(child, list):
                for index, reference in enumerate(child):
                    if isinstance(reference, str):
                        yield reference, (*child_path, index)
            yield from _named_references(
                child, singular=singular, plural=plural, path=child_path
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _named_references(
                child, singular=singular, plural=plural, path=(*path, index)
            )


def _all_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(key)
            keys.update(_all_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_all_keys(child))
    return keys


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType(
            {key: _deep_freeze(child) for key, child in sorted(value.items())}
        )
    if isinstance(value, list):
        return tuple(_deep_freeze(child) for child in value)
    return value


def _freeze_runtime_indexes(indexes: Mapping[str, Mapping[str, Any]]) -> RuntimeIndexes:
    return RuntimeIndexes(
        goals=_deep_freeze(indexes["goals"]),
        calendar_candidates=_deep_freeze(indexes["calendar_candidates"]),
        commitments=_deep_freeze(indexes["commitments"]),
        evidence=_deep_freeze(indexes["evidence"]),
        constraints=_deep_freeze(indexes["constraints"]),
        source_events=_deep_freeze(indexes["source_events"]),
        lineage_mappings=_deep_freeze(indexes["lineage_mappings"]),
        attention_item_references=MappingProxyType(
            dict(sorted(indexes["attention_item_references"].items()))
        ),
    )


def _expect(
    condition: bool,
    code: str,
    path: str,
    message: str,
    issues: list[ContractIssue],
    object_id: str | None = None,
) -> None:
    if not condition:
        issues.append(_issue(code, path, object_id, (), message))


def _issue(
    code: str,
    path: str,
    object_id: str | None,
    pointer: Sequence[str | int],
    message: str,
) -> ContractIssue:
    return ContractIssue(code, path, object_id, _pointer(pointer), message)


def _pointer(path: Sequence[str | int]) -> str:
    if not path:
        return ""
    return "/" + "/".join(
        str(part).replace("~", "~0").replace("/", "~1") for part in path
    )


def _join_pointer(prefix: Sequence[str | int], suffix: str) -> str:
    start = _pointer(prefix)
    return f"{start}{suffix}" if suffix else start


def _warning_sort_key(warning: BundleWarning) -> tuple[str, str, str, str]:
    return (
        warning.warning_code,
        warning.path,
        warning.object_id or "",
        warning.pointer,
    )
