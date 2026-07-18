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
