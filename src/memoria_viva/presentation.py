"""Public-safe presentation adapter for the canonical Memoria Viva replay."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .attention import load_attention_feature_policy
from .canonical import canonical_json_bytes, sha256_digest, to_plain_json_value
from .fixtures import FixtureBundleLoader, RuntimeBundle
from .replay import ReplayResult, run_replay


DEMO_VIEW_CONTRACT = "MV_DEMO_VIEW_V1"
DETERMINISTIC_BRIEF_LABEL = "Deterministic Engine Brief"
DETERMINISTIC_AUTHORITY_STATEMENT = (
    "The deterministic engine produced the state transition, scores, rankings, "
    "GraphDelta, and claims. GPT-5.6 generated only this human-readable "
    "explanation."
)

# Static build metadata from the Phase 2 validation gate. Streamlit must never
# run subprocess tests inside a web request.
VALIDATED_TEST_COUNT = 260


@dataclass(frozen=True)
class DemoViewModel:
    """Deeply immutable, sanitized projection consumed by UI and explainer."""

    value: Mapping[str, Any]

    @property
    def replay_digest(self) -> str:
        return str(self.value["replay_digest"])

    def to_plain_json(self) -> dict[str, Any]:
        plain = to_plain_json_value(self.value)
        if not isinstance(plain, dict):
            raise TypeError("DemoViewModel must project to an object")
        return plain

    def canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.value)

    def download_projection(self) -> dict[str, Any]:
        """Return the public-safe deterministic download payload."""

        value = self.to_plain_json()
        return {
            "view_contract": value["view_contract"],
            "replay_digest": value["replay_digest"],
            "headline_metrics": value["headline_metrics"],
            "event": value["event"],
            "before_ranking": value["before_ranking"],
            "after_ranking": value["after_ranking"],
            "rank_movements": value["rank_movements"],
            "graph_delta_by_category": value["graph_delta_by_category"],
            "deterministic_brief": value["deterministic_brief"],
            "oracle_statuses": value["oracle_statuses"],
            "technical_proof": value["technical_proof"],
            "privacy": value["privacy"],
            "warnings": value["warnings"],
        }

    def explainer_projection(self) -> dict[str, Any]:
        """Return the minimum sanitized context allowed to reach GPT-5.6."""

        value = self.to_plain_json()
        return {
            "replay_digest": value["replay_digest"],
            "event": value["event"],
            "before_top_three": value["before_ranking"][:3],
            "after_top_three": value["after_ranking"][:3],
            "new_attention_items": value["new_attention_items"],
            "protected_items": value["protected_items"],
            "conditional_displacements": value["conditional_displacements"],
            "confirmation_required_items": value[
                "confirmation_required_items"
            ],
            "unresolved_uncertainties": value["critical_uncertainties"],
            "evidence": value["evidence"],
            "oracle_statuses": value["oracle_statuses"],
            "policy_warnings": value["policy_warnings"],
            "deterministic_authority_statement": DETERMINISTIC_AUTHORITY_STATEMENT,
        }


@dataclass(frozen=True)
class DemoSession:
    """In-memory replay plus its public-safe view; never persisted here."""

    replay: ReplayResult
    view_model: DemoViewModel


def repository_root() -> Path:
    """Resolve a deployment checkout without exposing it in public projections."""

    candidates = (Path.cwd().resolve(), Path(__file__).resolve().parents[2])
    for candidate in candidates:
        if all(
            (candidate / path).exists()
            for path in (
                "schemas",
                "config/attention-policy.v1.json",
                "fixtures/founder-hackathon/public-goals.json",
            )
        ):
            return candidate
    raise RuntimeError("Memoria Viva repository data is unavailable")


def run_canonical_demo(root: Path | None = None) -> DemoSession:
    """Run the one committed scenario and build its sanitized presentation."""

    project_root = (root or repository_root()).resolve()
    loader = FixtureBundleLoader(project_root)
    runtime = loader.load_runtime_bundle()
    oracle = loader.load_oracle_bundle(runtime)
    feature_policy = load_attention_feature_policy(project_root)
    replay = run_replay(runtime, oracle, feature_policy)
    return DemoSession(
        replay=replay,
        view_model=build_demo_view_model(replay, runtime),
    )


def build_demo_view_model(
    replay: ReplayResult,
    runtime: RuntimeBundle,
) -> DemoViewModel:
    """Derive a public-safe view from replay output and sanitized metadata."""

    if not isinstance(replay, ReplayResult):
        raise TypeError("replay must be ReplayResult")
    if not isinstance(runtime, RuntimeBundle):
        raise TypeError("runtime must be RuntimeBundle")

    replay_digest = sha256_digest(replay.to_plain_json())
    before_rows = _ranking_rows(replay.ranking_before)
    after_rows = _ranking_rows(replay.ranking_after)
    before_by_subject = {row["subject_id"]: row for row in before_rows}
    movements = _rank_movements(before_rows, after_rows)
    new_items = tuple(
        row for row in after_rows if row["subject_id"] not in before_by_subject
    )
    protected = tuple(row for row in after_rows if row["band"] == "PROTECTED")
    confirmation = tuple(
        row for row in after_rows if row["confirmation_required"]
    )

    relationship_index = {
        relation["relationship_id"]: relation
        for relation in replay.snapshot_t1.relationships
    }
    graph_groups = _graph_delta_groups(replay, relationship_index)
    conditional_displacements = tuple(graph_groups["DISPLACED"])
    evidence = _evidence_rows(runtime)
    evidence_ids = {row["evidence_id"] for row in evidence}
    critical_uncertainties = _critical_uncertainties(
        runtime, after_rows, conditional_displacements
    )
    publications = tuple(
        {
            "surface": item["publication_surface"],
            "status": item["approval_state"],
        }
        for item in runtime.privacy_manifest["publication_approvals"]
    )
    oracle_statuses = {
        "ranking_before": replay.ranking_before_comparison.status,
        "ranking_after": replay.ranking_after_comparison.status,
        "graph_delta": replay.graph_delta_comparison.status,
    }
    warnings = tuple(
        {
            "code": item["code"],
            "message": item["message"],
            "severity": item["severity"],
        }
        for item in replay.run_record.to_plain_json()["warnings"]
    )
    policy_warnings = tuple(
        warning
        for warning in warnings
        if warning["code"]
        in {
            "POLICY_EFFECTIVE_AT_UNKNOWN",
            "POLICY_STATUS_DRAFT",
            "BOUNDED_REPLAY_ONLY",
        }
    )

    event = {
        "title": runtime.source_event["title"],
        "summary": runtime.source_event["summary"],
        "goal_affected": "GC-01 — PRODUCT_VALIDATION",
        "authority_limitation": runtime.source_event["authority_scope"],
        "received_at": runtime.source_event["received_at"],
        "occurred_at": runtime.source_event["occurred_at"],
        "deadline_anchor": runtime.source_event["deadline_at"],
        "deadline_label": "Synthetic fixture deadline anchor — not the official deadline",
        "evidence_refs": tuple(runtime.source_event["evidence_refs"]),
        "uncertainty": tuple(runtime.source_event["uncertainty"]),
        "authority_statement": (
            "Communication evidence is not official-rule authority and does not "
            "establish eligibility, compliance, or completion."
        ),
    }

    deterministic_brief = _deterministic_brief(
        before_rows,
        after_rows,
        new_items,
        protected,
        conditional_displacements,
        confirmation,
        critical_uncertainties,
    )
    technical = {
        "validated_test_count": VALIDATED_TEST_COUNT,
        "execution_mode": "REPLAY",
        "model_metadata": None,
        "replay_digest": replay_digest,
        "snapshot_t0": {
            "id": replay.snapshot_t0.snapshot_id,
            "digest": replay.snapshot_t0.state_digest,
        },
        "snapshot_t1": {
            "id": replay.snapshot_t1.snapshot_id,
            "digest": replay.snapshot_t1.state_digest,
        },
        "ranking_before": {
            "id": replay.ranking_before.ranking["attention_ranking_id"],
            "digest": replay.ranking_before.ranking_digest,
        },
        "ranking_after": {
            "id": replay.ranking_after.ranking["attention_ranking_id"],
            "digest": replay.ranking_after.ranking_digest,
        },
        "graph_delta": {
            "id": replay.graph_delta.graph_delta_id,
            "digest": replay.graph_delta.transition_digest,
        },
        "run_record": {
            "id": replay.run_record.run_id,
            "digest": replay.run_record.run_digest,
        },
        "base_policy": {
            "id": replay.ranking_after.ranking["policy_id"],
            "version": replay.ranking_after.ranking["policy_version"],
            "digest": replay.ranking_after.base_policy_digest,
            "status": runtime.attention_policy["status"],
        },
        "feature_policy": {
            "id": replay.ranking_after.feature_policy_id,
            "version": replay.ranking_after.feature_policy_version,
            "digest": replay.ranking_after.feature_policy_digest,
            "authorized_mode": "REPLAY",
        },
        "oracle_statuses": oracle_statuses,
        "determinism_statement": (
            "The same committed fixture produces byte-identical deterministic outputs."
        ),
    }

    all_referenced_evidence = {
        ref
        for row in (*before_rows, *after_rows)
        for ref in row["evidence_refs"]
    }
    if not all_referenced_evidence.issubset(evidence_ids):
        raise ValueError("presentation contains an unresolved evidence reference")

    value = {
        "view_contract": DEMO_VIEW_CONTRACT,
        "replay_digest": replay_digest,
        "headline_metrics": {
            "attention_items_before": len(before_rows),
            "attention_items_after": len(after_rows),
            "new_protected_commitments": len(
                [row for row in new_items if row["band"] == "PROTECTED"]
            ),
            "oracle_checks_passed": sum(
                status == "PASS" for status in oracle_statuses.values()
            ),
        },
        "before_ranking": before_rows,
        "event": event,
        "after_ranking": after_rows,
        "rank_movements": movements,
        "new_attention_items": new_items,
        "graph_delta_by_category": graph_groups,
        "protected_items": protected,
        "conditional_displacements": conditional_displacements,
        "confirmation_required_items": confirmation,
        "critical_uncertainties": critical_uncertainties,
        "evidence": evidence,
        "oracle_statuses": oracle_statuses,
        "technical_proof": technical,
        "policy_warnings": policy_warnings,
        "warnings": warnings,
        "privacy": {
            "fixture_review_state": runtime.privacy_manifest[
                "privacy_review_state"
            ],
            "founder_approval_state": runtime.privacy_manifest[
                "founder_approval_state"
            ],
            "residual_aggregation_risk": runtime.privacy_manifest[
                "residual_aggregation_risk"
            ],
            "generated_output_review": "NOT_REVIEWED",
            "publication_surfaces": publications,
            "statement": (
                "Private-repository approval does not authorize any public surface."
            ),
        },
        "deterministic_brief": deterministic_brief,
    }
    return DemoViewModel(value=_deep_freeze(value))


def _ranking_rows(ranking: Any) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    for item in ranking.ranking["items"]:
        item_id = item["attention_item_id"]
        rows.append(
            {
                "rank": item["rank"],
                "attention_item_id": item_id,
                "subject_id": item["subject_ref"]["entity_id"],
                "label": item["subject_ref"]["label"],
                "displayed_score": f"{item['score']:.2f}",
                "band": ranking.ranking_bands[item_id],
                "status": item["status"],
                "mobility": item["mobility_at_rank"],
                "execution_state": item["execution_state"],
                "protected": ranking.ranking_bands[item_id] == "PROTECTED",
                "confirmation_required": bool(item["confirmation_required_refs"]),
                "approval_requirement": ranking.approval_requirements[item_id],
                "displaced_refs": tuple(item["displaced_commitment_refs"]),
                "evidence_refs": tuple(item["evidence_refs"]),
                "uncertainty": tuple(item["uncertainty"]),
                "explanation": item["explanation"],
            }
        )
    return tuple(rows)


def _rank_movements(
    before: tuple[dict[str, Any], ...],
    after: tuple[dict[str, Any], ...],
) -> tuple[dict[str, Any], ...]:
    previous = {row["subject_id"]: row["rank"] for row in before}
    movements: list[dict[str, Any]] = []
    for row in after:
        old_rank = previous.get(row["subject_id"])
        if old_rank is None:
            direction = "NEW"
            delta = None
        else:
            delta = old_rank - row["rank"]
            direction = "UP" if delta > 0 else "DOWN" if delta < 0 else "UNCHANGED"
        movements.append(
            {
                "subject_id": row["subject_id"],
                "label": row["label"],
                "rank_before": old_rank,
                "rank_after": row["rank"],
                "direction": direction,
                "rank_delta": delta,
            }
        )
    return tuple(movements)


def _graph_delta_groups(
    replay: ReplayResult,
    relationships: Mapping[str, Any],
) -> dict[str, tuple[dict[str, Any], ...]]:
    categories = (
        "ADDED",
        "UPDATED",
        "CONFLICTED",
        "DISPLACED",
        "PROTECTED",
        "REQUIRES_CONFIRMATION",
        "UNCHANGED",
    )
    groups: dict[str, list[dict[str, Any]]] = {category: [] for category in categories}
    for change in replay.graph_delta.changes:
        affected_ref = change["affected_ref"]
        relationship_id = change["affected_relationship_id"]
        relationship = relationships.get(relationship_id) if relationship_id else None
        if affected_ref is not None:
            label = affected_ref["label"]
            affected_id = affected_ref["entity_id"]
        elif relationship is not None:
            label = (
                f"{relationship['from_ref']['label']} "
                f"{relationship['relationship_type']} "
                f"{relationship['to_ref']['label']}"
            )
            affected_id = relationship_id
        else:
            label = change["expected_new_state"]["state_label"]
            affected_id = relationship_id
        groups[change["category"]].append(
            {
                "affected_id": affected_id,
                "affected_kind": change["affected_kind"],
                "label": label,
                "explanation": change["explanation"],
                "reason": change["reason"],
                "condition": change["condition"],
                "execution_state": change["actual_execution_state"],
                "conditionality": change["conditionality"],
                "authority": change["authority_scope"],
                "evidence_refs": tuple(change["evidence_refs"]),
                "uncertainty": tuple(change["uncertainty"]),
                "statement_kind": (
                    "FACT"
                    if change["category"] == "ADDED"
                    and affected_ref is not None
                    and affected_ref["entity_type"] == "SourceEvent"
                    else "INFERENCE"
                ),
            }
        )
    return {category: tuple(groups[category]) for category in categories}


def _evidence_rows(runtime: RuntimeBundle) -> tuple[dict[str, Any], ...]:
    rows = []
    for evidence_id in sorted(runtime.indexes.evidence):
        item = runtime.indexes.evidence[evidence_id]
        rows.append(
            {
                "evidence_id": evidence_id,
                "category": item["public_evidence_category"],
                "summary": item["structured_observation"]
                or item["factual_observation"],
                "epistemic_state": item["epistemic_state"],
                "confidence": item["confidence"],
                "authority": item["authority_scope"],
                "uncertainty": tuple(item["uncertainty"]),
                "statement_kind": "FACT",
            }
        )
    return tuple(rows)


def _critical_uncertainties(
    runtime: RuntimeBundle,
    after_rows: tuple[dict[str, Any], ...],
    displacements: tuple[dict[str, Any], ...],
) -> tuple[str, ...]:
    candidates = [
        *runtime.source_event["uncertainty"],
        *(
            uncertainty
            for row in after_rows
            if row["subject_id"] in {"CMT-04", "CMT-05"}
            for uncertainty in row["uncertainty"]
        ),
        *(
            uncertainty
            for change in displacements
            for uncertainty in change["uncertainty"]
        ),
        "Final compliance remains unknown.",
        "Generated replay output has not completed publication review.",
    ]
    return tuple(dict.fromkeys(candidates))


def _deterministic_brief(
    before: tuple[dict[str, Any], ...],
    after: tuple[dict[str, Any], ...],
    new_items: tuple[dict[str, Any], ...],
    protected: tuple[dict[str, Any], ...],
    displacements: tuple[dict[str, Any], ...],
    confirmation: tuple[dict[str, Any], ...],
    uncertainties: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "label": DETERMINISTIC_BRIEF_LABEL,
        "headline": "The trigger creates two protected commitments without erasing prior obligations.",
        "what_changed": (
            f"Attention expands from {len(before)} to {len(after)} ranked items.",
            "Public product demonstration ready enters rank 1.",
            "Submission package finalization enters rank 2 and depends on the demonstration.",
            "Protected documentation review remains in the top three.",
        ),
        "new_top_three": tuple(row["label"] for row in after[:3]),
        "new_attention_items": tuple(row["label"] for row in new_items),
        "what_remains_protected": tuple(row["label"] for row in protected),
        "conditionally_displaced": tuple(change["label"] for change in displacements),
        "requires_confirmation": tuple(row["label"] for row in confirmation),
        "what_remains_unknown": uncertainties,
        "next_smallest_action": (
            "Protect the minimum verifiable demonstration, then review the "
            "conditionally displaced item and joint-authority items before any "
            "external action."
        ),
        "auditability": (
            "Every rank, change, uncertainty, policy, and evidence reference is tied "
            "to immutable deterministic replay receipts."
        ),
        "authority_statement": DETERMINISTIC_AUTHORITY_STATEMENT,
    }


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _deep_freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_deep_freeze(item) for item in value)
    return value
