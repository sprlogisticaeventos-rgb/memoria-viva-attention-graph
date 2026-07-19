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

## MV-ADR-010 — Bounded replay attention extraction and ranking policy

- **Status:** ACCEPTED
- **Date:** 2026-07-19
- **Context:** The versioned base attention policy owns six fixed weights and
  score guardrails but intentionally does not define how runtime state becomes
  normalized component values. Phase 1D requires deterministic extraction,
  scoring, ranking, and independent comparison with the human ordinal oracle
  without using expectations as production inputs.
- **Decision — authorization:** `config/attention-policy.v1.json` remains
  `draft` with `effective_at: null`. It is authorized only for
  `BOUNDED_REPLAY_MODE`; this decision makes no production-active policy claim.
  Every computed item and ranking must preserve that warning.
- **Decision — feature authority:**
  `config/attention-feature-policy.v1.json`, validated by its canonical schema,
  is the single versioned authority for deterministic feature extraction and
  ranking guardrails. It references the base policy for weights and must not
  duplicate them. Changes require a new version and human approval.
- **Decision — temporal urgency:** First map an unresolved missed carryover or
  unresolved item whose supporting interval ended before Snapshot time to
  `1.00`. For remaining items, apply evidence precedence in this order: active
  constrained deadline, explicit commitment due time, direct or aggregated
  lineage Calendar windows, Calendar-only windows, and unresolved-carryover
  lifecycle. Map deadline windows to `1.00`, `0.95`,
  `0.80`, `0.60`, or `0.40`; a window crossing Snapshot time to `0.85`; and
  future starts to `0.75`, `0.55`, `0.35`, or `0.20`. No defensible temporal
  evidence remains `UNKNOWN`.
- **Decision — downstream impact:** Read explicit displacement-cost or
  opportunity-cost semantics only: `VERY_HIGH=1.00`, `HIGH=0.80`,
  `MEDIUM_HIGH=0.65`, `MEDIUM=0.50`, `LOW=0.25`, and `NONE=0.00`. Missing or
  ambiguous impact remains `UNKNOWN`; title and protection do not supply it.
- **Decision — strategic alignment:** Trigger-created direct service to an
  included active Goal is `1.00`; an operational commitment's explicit direct
  support is `0.85`; Calendar-only direct support is `0.70`; indirect
  context-supported alignment is `0.50`; and no supported relation is
  `UNKNOWN`. GC-01, GC-02, and GC-03 receive no intrinsic importance ordering.
- **Decision — conflict or displacement:** An item initiating an active
  supported conflict or conditional displacement is `1.00`; an unresolved
  target is `0.60`; incomplete movement authority is `0.40`; and no supported
  condition is `0.00`. Coexistence is not conflict, and conditional movement
  is not execution.
- **Decision — event novelty:** A commitment created by the current trigger is
  `1.00`; a pre-existing item materially updated by that trigger is `0.50`;
  pre-existing unchanged state is `0.00`; and every T0 item is `0.00`.
- **Decision — evidence confidence:** For every required evidence reference,
  cap numeric confidence by epistemic state (`confirmed=1.00`,
  `approximate=0.80`, `inferred=0.65`, `uncertain=0.40`, `blocked=UNKNOWN`),
  then aggregate by minimum. Missing evidence is `UNKNOWN`; an unresolved
  evidence reference is a validation failure.
- **Decision — UNKNOWN:** `UNKNOWN` never becomes zero. Any required unknown
  component prevents a production score, records a confirmation-required
  blocked computation with the missing component and evidence gap, and blocks
  oracle assertions that require that item.
- **Decision — ranking guardrails:** `PROTECTED` adds no numeric value and
  creates a precedence band before standard items. Within a band, dependency
  prerequisites precede dependents, followed by unrounded score descending,
  effective due time ascending with null last, and stable attention-item ID.
  `NEEDS_CONFIRMATION` changes actionability and approval metadata only; it adds
  no score and creates no protected band.
- **Decision — arithmetic:** Use `Decimal`, retain unrounded normalized values
  and contributions for ranking, and round only display score to two decimal
  places with `ROUND_HALF_UP`. Calculation identity includes Snapshot digest,
  base-policy digest, feature-policy digest, item identity, and normalized
  components.
- **Decision — oracle isolation:** Production extraction and scoring may receive
  RuntimeBundle and immutable Snapshots only. Human ordinal files are read only
  by the comparator after production rankings are final. Oracle rank,
  direction, protected/displaced expectations, and uncertainty cannot become a
  feature, target, calibration input, tie-break, fallback, or training signal.
- **Alternatives:** Encode extraction thresholds in Python only; default missing
  values to zero; add protection or confirmation bonuses; tune weights against
  the oracle; or merge the oracle into RuntimeBundle. These were rejected as
  unauditable, epistemically unsafe, or incompatible with MV-ADR-009.
- **Consequences:** Replay results are deterministic, explainable, and policy
  versioned. Some items may remain unscored until explicit runtime evidence is
  added; oracle comparison must expose that blockage rather than auto-tune.
  Base and feature policy digests become required calculation inputs.
- **Deferred recalibration:** Production activation, threshold calibration,
  alternative evidence aggregation, weight changes, feature-value changes,
  and fixture evidence enrichment require separate human review and versioned
  decisions after bounded Replay Mode evaluation.
- **Supersession:** None.

### Bounded-evaluation amendment — 2026-07-19

- **Initial result preserved:** The uncommitted feature-policy `1.0.0`
  candidate produced valid deterministic rankings but correctly returned a
  `BLOCKED` oracle comparison. Four eligible Calendar-only attention items had
  no explicit downstream-impact or opportunity-cost value, and the approved
  UNKNOWN rule prohibited a numeric score.
- **Calendar-only mobility fallback:** When and only when an eligible
  Calendar-only item has no stronger explicit impact signal, its explicit
  mobility maps as follows: `PROTECTED → HIGH/0.80`,
  `NEEDS_CONFIRMATION → MEDIUM_HIGH/0.65`, `FLEXIBLE → LOW/0.25`,
  `DISPLACEABLE → LOW/0.25`, and `CANCELABLE → NONE/0.00`. Missing or
  unsupported mobility remains `UNKNOWN`. This fallback is neither a
  protection bonus nor authority to score excluded or ineligible items.
- **Conditional-displacement target:** Apply conflict/displacement rules in
  ordered precedence. An initiator remains `1.00`. An explicitly DISPLACEABLE
  target of conditional displacement whose execution is `UNKNOWN` or
  `NOT_EXECUTED` receives `0.00`, meaning no additional numeric deferment-target
  bonus while condition, evidence, opportunity cost, repair, authority, and
  uncertainty remain visible. Other supported unresolved conflict targets
  remain `0.60`; incomplete movement authority remains `0.40` absent a stronger
  rule.
- **Novelty materiality:** Trigger-created state remains `1.00`. A pre-existing
  item receives `0.50` only when its own lifecycle, mobility, eligibility,
  authority, protection, condition, execution, active-constraint membership,
  or verified object status materially changes. Relationship-only,
  explanatory, expected-conflict, or conditional-displacement changes remain
  `0.00` when the object's own semantic state is unchanged.
- **Version:** The corrected bounded-Replay feature policy is
  `mv.attention-feature-policy@1.1.0`. The base policy and all six weights are
  unchanged. No fixture or human oracle changed, no expected rank or direction
  became a calculation input, and no production-activation claim is made.
- **Continuing authority:** Future fallback mappings, materiality semantics,
  component values, thresholds, evidence aggregation, or production activation
  still require a new version and explicit human approval.
