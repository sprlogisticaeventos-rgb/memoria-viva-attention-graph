# Phase 0 Ontology

## Contract metadata

| Field | Value |
|---|---|
| Ontology ID | `mv_attention_graph` |
| Ontology version | `1.0.0` |
| Status | `phase_0_reconciled_contract` |
| Effective date | 2026-07-18 |
| Machine authority | `../schemas/` |
| Decision authority | `../DECISIONS.md#mv-adr-009--human-accelerator-supersession-of-goal-relationship-and-ranking-oracle-semantics` |

This document is the canonical semantic contract for Phase 0. JSON Schemas own
serialized field shapes. The construction blueprint owns broader product intent.
Fixture-specific identities, quantities, ranks, and transitions do not belong in
generic ontology or schema definitions.

## Contracted concepts

| Concept | Kind | Stable identity | Phase 0 responsibility |
|---|---|---|---|
| `Source` | Entity | `source_id` | Identifies a public-safe evidence-producing boundary |
| `SourceEvent` | Entity | `source_event_id` | Records one normalized external observation and its causal role |
| `Evidence` | Entity | `evidence_id` | Supports a claim with non-reversible provenance, authority, state, and confidence |
| `Goal` | Entity | `goal_id` + `goal_version` | Defines a persistent outcome, visibility, and evidence-based completion contract |
| `PublicGoalSet` | Versioned contract | `public_goal_set_id` + `model_version` | Groups public Goals and neutral controlled-demo omissions |
| `Constraint` | Entity | `constraint_id` + `constraint_version` | Defines a sourced condition and its authority boundary |
| `CalendarCandidate` | Reference identity | synthetic candidate ID | Preserves Calendar evidence identity without equating it to an operational commitment |
| `Commitment` | Entity | `commitment_id` + `commitment_version` | Defines an obligation across independent lifecycle, mobility, authority, eligibility, repair, and execution dimensions |
| `Snapshot` | Immutable state | `snapshot_id` + `snapshot_version` | Captures known active and excluded-but-retained state and points to its predecessor |
| `AttentionItem` | Computed entity | `attention_item_id` + `attention_item_version` | Stores one deterministic scored production item |
| `AttentionRanking` | Immutable computed projection | `attention_ranking_id` + `ranking_version` | Orders computed AttentionItems under an exact policy |
| `ExpectedAttentionRanking` | Human test oracle | `oracle_id` | Stores ordinal human expectations without production scores |
| `Relationship` | Provenanced edge | `relationship_id` | Connects typed references with evidence, confidence, explanation, and creator type |
| `GraphDelta` | Immutable transition | `graph_delta_id` + `graph_delta_version` | Records categorized expected and executed changes between Snapshots |
| `RunRecord` | Immutable receipt | `run_id` + `run_version` | Receipts inputs, outputs, policy, approvals, claims, warnings, and replay identity |
| `PrivacyManifest` | Review contract | `manifest_id` + `manifest_version` | Records field transformations and publication-surface approvals |

## Deferred concepts

The following terms remain documented but have no independent Phase 0 lifecycle
or schema:

| Concept | Phase 0 treatment | Promotion trigger |
|---|---|---|
| `Decision` | Lightweight typed reference only | Acceptance and supersession require product lifecycle |
| `Blocker` | Lightweight typed reference only | Resolution and ownership require product lifecycle |
| `Artifact` | Lightweight typed reference only | Assets require independent lineage or publication lifecycle |
| `Actor` | Authority or owner reference | Cross-source identity resolution is authorized |
| `Project` | Boundary string or typed reference | Multiple project graphs are required |
| `Finding` | RunRecord observation | Repair-loop implementation is authorized |
| `RepairAction` | RunRecord recommendation | Repair execution lifecycle is authorized |
| `ValidationCase` | RunRecord validation | Reusable validation catalogs are authorized |
| `ValidationResult` | RunRecord validation | Results need independent lineage |
| `RemainingDelta` | GraphDelta or validation detail | Iterative repair is implemented |
| `Preference` | Evidence-backed note only | Explicit preference management is authorized |
| `Notification` | Not represented | Delivery channels are authorized |

Lightweight Decision, Blocker, and Artifact references identify a stable type,
ID, optional version, and label. They do not carry shadow lifecycle state.

## Identity, lineage, and version rules

1. IDs are stable synthetic or repository-safe strings. Display-name changes do
   not change identity.
2. Calendar candidate identity and operational commitment identity are distinct.
   A Calendar record is temporal evidence, not complete operational truth.
3. An operational-to-source mapping is explicit and records the operational
   object, source candidate IDs, derivation type, confidence, uncertainty, and
   evidence.
4. Approved derivation types are `DIRECT_DERIVATION`,
   `AGGREGATED_DERIVATION`, `TRIGGER_CREATED`, `CONTEXT_SUPPORTED`, and
   `NO_DIRECT_CALENDAR_SOURCE`.
5. Title similarity alone is never identity evidence.
6. Aggregation may map several Calendar candidates to one operational object; it
   must not duplicate attention.
7. `schema_version`, `ontology_version`, entity versions, and policy versions
   identify different authorities and must remain explicit.
8. A material state correction creates a new version. Historical versions remain
   addressable.
9. Content digests identify exact artifacts or canonicalized records but never
   replace source and evidence references.

## Goal dimensions and completion authority

A Goal keeps these dimensions separate:

- **Operational lifecycle:** draft, active, paused, completed, blocked,
  budget-limited, or cleared.
- **Controlled-demo visibility:** included, omitted from the controlled demo,
  not applicable, or unknown.
- **Verification surfaces:** independently evidenced acceptance conditions.
- **Completion authority:** the declared authority and deterministic validation
  that accept completion.

`OMITTED_FROM_CONTROLLED_DEMO` is visibility, never completion, invalidation,
deletion, rejection, or clearing. A controlled public Goal set may record a
neutral omission without publishing private Goal content.

A Goal cannot be accepted as completed because a file, fixture, conversation,
registration, submission, demo, or other artifact exists. Completion requires
every required verification surface to be verified with evidence and the
completion validator to pass. Model or input claims cannot bypass that rule.

The controlled founder fixture will later contain exactly three approved public
Goals and one neutral omission record. Those exact IDs and quantities belong to
Phase 0C2 fixture validation, not the generic Goal contracts.

## SourceEvent and temporal semantics

- `event_role` distinguishes one causal `TRIGGER`, a `FOLLOW_UP`, and a
  non-causal `CONTEXT_EVENT`.
- A follow-up retains an explicit nullable link to its trigger; it is never
  merged into the trigger.
- `received_at` is when the communication entered the capture boundary.
- `occurred_at` is when the represented event actually happened.
- `deadline_at` is an external deadline carried by the observation.
- Unknown temporal values are explicit `null`. `occurred_at` is never copied
  from `received_at` for convenience.
- `authority_scope` limits what the event can establish. Communication evidence
  cannot establish official rules, eligibility, compliance, or completion.

The approved controlled transition defines T0 immediately before its canonical
trigger and T1 immediately after that trigger is normalized and evaluated.
Follow-ups occur outside T1 and cannot affect it.

## Commitment dimensions

A Commitment represents these dimensions independently:

- `lifecycle_status` — operational existence and progress;
- `mobility_policy` — protected, flexible, displaceable, confirmation-required,
  cancelable, or unknown;
- `authority_mode` — who may decide or execute movement;
- `eligibility_state` — whether the item may participate in ranking;
- `protection_state` — whether automatic displacement is prohibited;
- `conditionality` — whether movement depends on an explicit condition;
- `condition_state` — whether that condition is pending, satisfied, not
  satisfied, not applicable, or unknown;
- `execution_state` — planned, authorized, executed, blocked, or unknown;
- displacement cost, repair requirement, reactivation condition, supported Goal,
  lineage, evidence, uncertainty, and approval requirement.

Conditional authorization is not executed movement. A conditionally displaceable
commitment remains present, carries opportunity cost and repair, and stays
`NOT_EXECUTED` or `UNKNOWN` until evidence establishes execution. Joint authority
cannot become unilateral authority, and `NEEDS_CONFIRMATION` is not approval.

## Snapshot membership and chaining

A Snapshot records:

- immutable identity, temporal role, capture time, and state digest;
- exactly one predecessor when it is not initial;
- active object references;
- excluded-but-retained object references with reasons and evidence;
- Goals, Commitments, Constraints, Relationships, ranking and GraphDelta links;
- explicit capacity epistemic state;
- privacy and review state.

Exclusion is not deletion. No T0 obligation may disappear silently from T1.
Calendar absence never establishes free capacity. The latest validated Snapshot
is current known persisted state; Calendar remains evidence of scheduling rather
than complete strategic truth.

## Ranking contracts

The production and human expectation contracts are intentionally separate:

1. **Computed production ranking:** numeric score, all six weighted components,
   exact policy ID/version/digest, deterministic input digest, evidence,
   uncertainty, and calculation digest are required.
2. **Human ordinal oracle:** expected rank, ordinal invariants, expected direction,
   protected/displaced references, uncertainty, approval requirements, and
   human-authored provenance are required. Numeric production scores and
   component contributions are not permitted.

Tests may compare computed ordering with the human oracle. They must not copy
human expectations into production score fields or change policy weights to
force an ordering.

The attention-policy schema owns the component identifier vocabulary, and the
versioned policy instance owns the weights. The shared score-contribution value
object references that authority rather than maintaining a second enum.

## GraphDelta contract

The active categories are:

- `ADDED`
- `UPDATED`
- `CONFLICTED`
- `DISPLACED`
- `PROTECTED`
- `REQUIRES_CONFIRMATION`
- `UNCHANGED`

Each change identifies an affected object or relationship, previous state,
expected new state, actual execution state, conditionality, condition state,
condition, reason,
opportunity cost, repair, authority, evidence, confidence, uncertainty,
explanation, creator type, ontology version, and timestamp.

Coexistence alone is not conflict. Conditional displacement remains distinguishable
from executed displacement. Previous and new Snapshot identities and digests
make historical state reconstructable.

## Relationship contract

The active bounded Phase 0 vocabulary is limited to:

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
- `changes_between`

`attempts_to_resolve` is `DEFERRED_FOR_REPAIR_LOOP_EXTENSION`. It is not
permanently invalid, but it cannot appear in current fixtures, GraphDeltas,
relationships, or replay contracts. Reintroduction requires an authorized,
versioned ontology decision.

Every relationship stores typed endpoints, non-empty evidence, epistemic state,
confidence, creator identity and type, explanation, timestamp, ontology version,
status, and explicit supersession when applicable. Removing or superseding an
edge creates a versioned `deactivated` or `superseded` transition that references
the prior relationship; it never erases the historical edge.

## Provenance, privacy, and epistemic rules

Epistemic states are `confirmed`, `approximate`, `inferred`, `blocked`, and
`uncertain`. Confidence does not promote inference into fact. Missing data stays
unknown and is never replaced by zero.

Public provenance uses synthetic repository-safe references and approved
evidence categories. It cannot contain URLs, filesystem paths, email or Calendar
provider IDs, account or submission IDs, raw source locators, or reversible
mappings. Publication approval is recorded as a separate state per surface at
both manifest and field-transformation level; approval for one surface does not
imply approval for another. Residual aggregation risk includes the approved
`LOW_MEDIUM` state.

## Immutability and no-silent-overwrite invariants

1. Source captures, Evidence, Snapshots, GraphDeltas, AttentionRankings, and
   RunRecords are immutable once finalized.
2. Corrections create a new version linked through supersession or a new Snapshot.
3. Conflicting evidence remains preserved and connected.
4. Score changes retain previous rank, previous score, and component evidence.
5. Displaced and excluded commitments remain identifiable.
6. Every material output is traceable through a RunRecord to inputs, policy, and
   evidence.
7. RunRecords cannot claim compliance, submission completion, Goal completion,
   or executed displacement without evidence and validation references.
8. Replay Mode retains input and output identity or digest and permits null model
   metadata.

## Required deterministic validation

Phase 1 validators must additionally enforce:

- trigger/follow-up linkage and the approved T0/T1 causal boundary;
- observation-type compatibility and non-empty public-safe evidence;
- unique lineage mappings and prohibition of title-only identity inference;
- commitment authorization, conditionality, execution, protection, and repair
  invariants;
- no silent object disappearance across Snapshot chains;
- each policy component exactly once with recomputed weighted values;
- ranking array order, item rank, item policy identity, and deterministic
  tie-break agreement;
- GraphDelta category semantics and historical reconstruction;
- RunRecord artifact, snapshot, ranking, delta, policy, claim, approval, and
  replay consistency;
- Goal completion only after every verification surface is evidenced and
  verified;
- field-level privacy approval for every intended publication surface.

## Deferred roadmap

Repair-loop lifecycle entities, subagents, prompt caching, reasoning continuity,
Programmatic Tool Calling, notifications, autonomous actions, and application
runtime are not active Phase 0 contracts. They may be introduced only by later
authorized, versioned decisions after the deterministic vertical slice exists.
