# Phase 0 Ontology

## Contract metadata

| Field | Value |
|---|---|
| Ontology ID | `mv_attention_graph` |
| Ontology version | `1.0.0` |
| Status | `phase_0_contract` |
| Effective date | 2026-07-18 |
| Machine authority | `../schemas/` |

This document is the canonical semantic contract for Phase 0. JSON Schemas
own serialized field shapes. The blueprint owns broader product intent.

## Contracted concepts

| Concept | Kind | Identity | Phase 0 responsibility |
|---|---|---|---|
| `Source` | Entity | `source_id` | Identifies an evidence-producing system, document, or explicit input |
| `SourceEvent` | Entity | `source_event_id` | Records one normalized external observation |
| `Evidence` | Entity | `evidence_id` | Supports a claim with a source, locator, state, and confidence |
| `Goal` | Entity | `goal_id` + `goal_version` | Defines a persistent outcome and its verification contract |
| `Constraint` | Entity | `constraint_id` + `constraint_version` | Defines a condition that cannot be violated within a scope |
| `Commitment` | Entity | `commitment_id` + `commitment_version` | Defines an obligation and its protection/displacement state |
| `Snapshot` | Immutable state | `snapshot_id` + `snapshot_version` | Captures known state at one instant and points to its predecessor |
| `AttentionItem` | Derived entity | `attention_item_id` + `attention_item_version` | Explains one scored unit of attention |
| `AttentionRanking` | Immutable projection | `attention_ranking_id` + `ranking_version` | Orders AttentionItems for one Snapshot under one policy |
| `Relationship` | Provenanced edge | `relationship_id` | Connects two typed references with evidence and confidence |
| `GraphDelta` | Immutable transition | `graph_delta_id` + `graph_delta_version` | Records object and relationship changes between Snapshots |
| `RunRecord` | Immutable receipt | `run_id` + `run_version` | Receipts observations, recommendations, validation, and outputs |

## Deferred concepts

The following terms are documented for continuity but have no independent
Phase 0 lifecycle or schema:

| Concept | Phase 0 treatment | Promotion trigger |
|---|---|---|
| `Decision` | Lightweight typed reference only | Acceptance, rationale, and supersession need product lifecycle |
| `Blocker` | Lightweight typed reference only | Blocking conditions need ownership and resolution lifecycle |
| `Artifact` | Lightweight typed reference only | Assets need lineage, approval, or publication lifecycle |
| `Actor` | String owner/authority or typed reference | Cross-source identity resolution is required |
| `Project` | Boundary string or typed reference | Multiple project graphs are present |
| `Finding` | RunRecord observation | Review/repair loops are implemented |
| `RepairAction` | RunRecord recommendation | Execution and approval lifecycle is implemented |
| `ValidationCase` | RunRecord validation record | Reusable validation catalogs exist |
| `ValidationResult` | RunRecord validation record | Results need independent lineage |
| `RemainingDelta` | GraphDelta or validation detail | Iterative repair is implemented |
| `Preference` | Evidence-backed note only | Explicit preference management is implemented |
| `Notification` | Not represented | Delivery channels are implemented |

Lightweight references identify `reference_type`, `reference_id`, optional
`reference_version`, and a human-readable label. They must not carry lifecycle
state that would make them shadow schemas.

## Identity and version rules

1. IDs are stable, opaque strings. A display-name change never changes an ID.
2. IDs are unique within their entity type. Cross-type references always carry
   the referenced type.
3. `schema_version` identifies the serialization contract.
4. `ontology_version` identifies semantic meaning.
5. Entity versions are positive integers. A material state change creates a
   new entity version; historical versions remain addressable.
6. Policy versions are independent of schema and ontology versions.
7. Content digests identify exact bytes or canonicalized records; they never
   replace source or evidence references.

## Timestamp rules

- Timestamps use RFC 3339 UTC strings with a `Z` suffix.
- `occurred_at` describes when a source event happened.
- `received_at` describes when it entered the capture boundary.
- `observed_at` describes when a source was inspected.
- `recorded_at` describes when Memoria Viva persisted the record.
- `captured_at` describes the state boundary represented by a Snapshot.
- Unknown times are explicit `null`; they are never replaced with ingestion
  time without labeling the substitution.

## Epistemic states

| State | Meaning |
|---|---|
| `confirmed` | Observed directly in an identified source |
| `approximate` | Reconstructed from partial but relevant evidence |
| `inferred` | Derived from other observations or rules |
| `blocked` | Cannot be verified because required access, data, or authority is missing |
| `uncertain` | Evidence is insufficient, ambiguous, or contradictory |

An epistemic state is not workflow status. Confidence does not promote an
inference into a confirmed fact.

## Provenance contract

Every factual or derived record must identify its source or supporting
`evidence_refs`. Evidence records preserve a locator, capture timestamps,
epistemic state, and bounded confidence. Derived records also identify the rule,
policy, model, or human action that created them when applicable.

Source absence is represented as `blocked` or `uncertain`; it is never filled
with invented content.

## Relationship contract

Phase 0 relationship types are:

- `derived_from`
- `supports`
- `conflicts_with`
- `blocks`
- `depends_on`
- `supersedes`
- `displaces`
- `scheduled_for`
- `owned_by`
- `constrained_by`
- `verified_by`
- `produced_by`
- `attempts_to_resolve`
- `changes_between`

Every relationship stores typed endpoints, evidence references, epistemic
state, confidence, creator identity, creation time, ontology version, status,
and an optional superseded relationship reference. Removing a relationship
creates a GraphDelta record; it does not erase the previous edge.

## Immutability and snapshot chaining

- Source captures, Evidence, Snapshots, GraphDeltas, AttentionRankings, and
  RunRecords are immutable once finalized.
- Corrections create a new version linked with `supersedes` or a new Snapshot.
- Every non-initial Snapshot must reference exactly one previous Snapshot.
- A GraphDelta names both the previous and new Snapshot.
- Attention rankings name their Snapshot and exact policy identity.
- A RunRecord names both rankings and the GraphDelta for the transition.
- The latest validated Snapshot is current known state; Calendar remains
  evidence of scheduling, not complete strategic truth.

## No-silent-overwrite invariants

1. Historical records are append-only.
2. Conflicting evidence is preserved and connected with `conflicts_with`.
3. Supersession is explicit and directional.
4. A score change preserves previous rank, previous score, and component delta.
5. A displaced commitment remains identifiable in both the ranking and delta.
6. Every material output is traceable through a RunRecord to source evidence.
7. Deterministic code may enforce cross-field invariants that strict model
   schemas cannot express; those invariants must not redefine ontology terms.

## Required cross-field validation

Phase 1 deterministic validators must enforce the following rules in addition
to JSON Schema validation:

- A Source has at least one non-null `stable_reference` or `content_hash`.
- Evidence has a non-null excerpt or structured observation appropriate to its
  observation type.
- Category-specific lightweight reference arrays contain only their named type:
  Decision, Blocker, or Artifact.
- Every AttentionItem has each policy component exactly once; component weights
  match the referenced policy and weighted values are recomputed, not trusted.
- Ranking array order, item `rank`, and deterministic tie-break order agree.
- GraphDelta object buckets agree with each record's `change_type`, and removed
  relationships carry `removed` status.
- Snapshot predecessor, GraphDelta endpoints, ranking Snapshot references, and
  RunRecord artifact references form one consistent transition.
- A Goal cannot become `completed` while its evidence status or required
  verification surface remains unverified.
