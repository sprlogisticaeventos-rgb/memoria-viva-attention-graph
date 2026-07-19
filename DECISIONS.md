# Decision Ledger

This file is the canonical ledger for accepted repository architecture
decisions. A later decision must name the record it supersedes.

## MV-ADR-001 — Canonical JSON Schema

- **Status:** Accepted
- **Date:** 2026-07-18
- **Context:** Phase 0 needs readable contracts, runtime validation, generated
  TypeScript types, and future strict Structured Outputs without independently
  maintained schema copies.
- **Decision:** JSON Schema is the canonical machine-readable authority.
  TypeScript and model-request projections must be generated or derived.
- **Alternatives:** Canonical runtime TypeScript schemas; a
  JSON-Schema-producing TypeScript library.
- **Consequences:** Schemas remain language-neutral. Runtime and strict-subset
  validation must test derived consumers.
- **Supersession:** None.

## MV-ADR-002 — Minimal Phase 0 ontology

- **Status:** Accepted
- **Date:** 2026-07-18
- **Context:** The blueprint contains a broader ontology than the first replay
  needs.
- **Decision:** Contract only Source, SourceEvent, Evidence, Goal, Constraint,
  Commitment, Snapshot, AttentionItem, AttentionRanking, Relationship,
  GraphDelta, and RunRecord in Phase 0.
- **Alternatives:** Contract the full blueprint ontology; define only file
  shapes without semantic entities.
- **Consequences:** The first transition is complete without committing early
  to repair-loop or notification lifecycles.
- **Supersession:** None.

## MV-ADR-003 — Evidence authority versus persisted-state authority

- **Status:** Accepted
- **Date:** 2026-07-18
- **Context:** Calendar observations are temporal evidence but do not represent
  complete strategic truth.
- **Decision:** Sources and the event log are authoritative for what was
  observed. Versioned Snapshots and Graph state are canonical persisted state;
  RunRecords receipt every transition back to evidence.
- **Alternatives:** Treat Calendar as complete truth; treat snapshots as truth
  without preserving source authority.
- **Consequences:** Conflicts, uncertainty, and corrections remain auditable.
- **Supersession:** None.

## MV-ADR-004 — Versioned JSON attention policy

- **Status:** Accepted
- **Date:** 2026-07-18
- **Context:** Ranking must be deterministic, explainable, and comparable.
- **Decision:** Store weights and scoring guardrails in a schema-validated,
  versioned JSON policy. Every RunRecord stores its policy version and digest.
- **Alternatives:** Hard-coded weights; documentation-only weights.
- **Consequences:** Any weight change requires a new policy version and human
  approval. Any threshold change requires a new policy version and human
  approval.
- **Supersession:** None.

## MV-ADR-005 — Privacy and fixture separation

- **Status:** Accepted
- **Date:** 2026-07-18
- **Context:** Raw founder evidence and generated runs may contain sensitive
  data, while the demo requires reproducible public fixtures.
- **Decision:** Separate ignored raw private inputs, tracked sanitized fixtures,
  ignored local runs, tracked expected outputs, and ignored secrets.
- **Alternatives:** Keep all data together under ignore rules; externalize all
  data and lose public replay fixtures.
- **Consequences:** Promotion into public fixtures requires sanitization,
  manifest review, and explicit approval.
- **Supersession:** None.

## MV-ADR-006 — Separate rankings and GraphDelta output

- **Status:** Accepted
- **Date:** 2026-07-18
- **Context:** The blueprint groups ranking comparison and diff concepts, while
  the first replay requires explicit artifact boundaries.
- **Decision:** Produce separate `attention-ranking-before.json`,
  `attention-ranking-after.json`, and `graph-delta.json` artifacts.
- **Alternatives:** One combined ranking artifact; a free-form snapshot diff.
- **Consequences:** Each handoff has a distinct schema and can be validated or
  replayed independently.
- **Supersession:** None.

## MV-ADR-007 — Deferred lifecycle entities

- **Status:** Accepted
- **Date:** 2026-07-18
- **Context:** Decision, Blocker, and Artifact matter to later product behavior
  but do not need independent Phase 0 lifecycles.
- **Decision:** Defer them as first-class entities and independent schemas.
  Permit only lightweight typed references where a Phase 0 contract needs one.
- **Alternatives:** Create full schemas now; omit all references until later.
- **Consequences:** Current handoffs remain traceable without freezing premature
  lifecycle semantics.
- **Supersession:** None.

## MV-ADR-008 — Shared schema definitions

- **Status:** Accepted
- **Date:** 2026-07-18
- **Context:** Identifiers, references, epistemic states, relationship
  provenance, and audit records recur across canonical schemas.
- **Decision:** Own reusable value objects in `schemas/common.schema.json` and
  reference them by stable `$id`. Entity schemas own only entity-specific
  fields.
- **Alternatives:** Repeat local `$defs` in each schema; create manually synced
  copies.
- **Consequences:** Validators must register the common schema, and future
  model-facing projections may bundle external references mechanically.
- **Supersession:** None.

## MV-ADR-009 — Human Accelerator supersession of Goal, relationship, and ranking-oracle semantics

- **Status:** ACCEPTED
- **Date:** 2026-07-18
- **Authority artifacts:** `CODEX_PRIMARY_HANDOFF_V1.md` as the controlling
  bounded engineering handoff; `LANE_A_V2_FOUNDER_APPROVAL.md` as the
  highest-authority founder approval record; `LANE_A_V2_HANDOFF(1).md` as the
  approved T0 to T1 expectation and ordinal test oracle; and the explicit
  targeted human re-review decision dated 2026-07-18.
- **Context:** The Phase 0 repository contracts predate the approved Human
  Accelerator package. The handoff audit found three incompatible
  representations: the hackathon modeled as a Goal, `attempts_to_resolve` in
  the active bounded relationship vocabulary, and a computed ranking contract
  that cannot also serve as a score-free human ordinal oracle without becoming
  ambiguous.
- **Decision — public Goal model:** The controlled public model contains exactly
  `GC-01 — PRODUCT_VALIDATION`,
  `GC-02 — FINANCIAL_AND_OPERATIONAL_CONTINUITY`, and
  `GC-03 — PERSONAL_AND_LEGAL_CONTINUITY`. The hackathon is a bounded
  experiment serving `GC-01`, not a fourth Goal. `G5` remains
  `OMITTED_FROM_CONTROLLED_DEMO`; it is not deleted, rejected, invalidated,
  completed, or cleared. Controlled-demo visibility and operational lifecycle
  are separate dimensions. The existing `goal-hackathon.json` is a superseded
  Phase 0 scaffold; a later authorized Phase 0C2 step will preserve Git history
  while renaming it to `public-goals.json` and replacing its content with the
  approved public model and neutral G5 omission metadata.
- **Decision — relationship vocabulary:** Current bounded Phase 0 fixture,
  GraphDelta, relationship, and replay contracts may use only the relationship
  vocabulary approved by the controlling handoff. `attempts_to_resolve` is
  removed from the active bounded vocabulary and recorded as
  `DEFERRED_FOR_REPAIR_LOOP_EXTENSION`. It is not permanently invalid and may
  return only through a future versioned ontology decision after the repair
  loop is authorized.
- **Decision — ranking contracts:** Computed production rankings and the human
  ordinal test oracle remain separate contracts. Production AttentionItems
  require numeric scores, all six weighted components, deterministic
  calculation, and policy ID, version, and digest; no human-authored score may
  be presented as computed output. The human oracle has no numeric production
  score and instead records expected rank, ordinal invariants, evidence
  references, expected direction, protected and displaced references,
  uncertainty, approval requirements, and human-authored provenance. A later
  authorized revision will create
  `schemas/expected-attention-ranking.schema.json`; tests will compare its
  ordinal expectations with deterministic computed output without combining
  the two representations.
- **Alternatives considered:** Retain `hackathon_submission` as a fourth Goal;
  treat controlled-demo omission as Goal lifecycle; keep
  `attempts_to_resolve` active before the repair loop exists; make production
  scores optional in one shared ranking schema; or store the human oracle and
  computed result in one ambiguous object. All were rejected because they
  weaken approved semantics, temporal traceability, or deterministic
  validation.
- **Consequences:** Later contract work must preserve exactly three public
  Goals, neutral G5 omission, the bounded relationship vocabulary, and a hard
  separation between human expectations and computed results. Existing
  production score requirements remain strict. Fixture migration must preserve
  Git history and must not imply that artifact existence proves completion.
- **Deferred work:** Update the blueprint, ontology, shared definitions, Goal
  and ranking contracts; create the expected-attention-ranking schema; migrate
  the superseded Goal scaffold during authorized Phase 0C2; add contract and
  oracle comparison tests; and version any later repair-loop relationship
  extension.
- **Superseded representations:** The blueprint and Goal scaffold representation
  of the hackathon as a Goal; `attempts_to_resolve` as an active bounded Phase 0
  relationship; and use of the computed AttentionItem/AttentionRanking shape as
  the human-authored expected-ranking oracle. This ADR does not supersede the
  production requirement for deterministic numeric scoring.
- **Files likely affected later:** `docs/CONSTRUCTION_BLUEPRINT.md`,
  `docs/ontology.md`, `schemas/common.schema.json`, `schemas/goal.schema.json`,
  `schemas/expected-attention-ranking.schema.json`, applicable production
  ranking schemas, `fixtures/founder-hackathon/goal-hackathon.json`, and
  `fixtures/founder-hackathon/public-goals.json`.
- **Authorization boundary:** This ADR-only step authorizes no schema, blueprint,
  ontology, fixture, policy, README, test, application, or other repository
  change. Those changes require a later explicit instruction.
