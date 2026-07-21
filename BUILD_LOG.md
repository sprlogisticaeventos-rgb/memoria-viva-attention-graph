# Build Log

Entries are append-only construction events. Product execution belongs in
RunRecords, not in this file.

## MV-BUILD-001 — Phase 0B contracts

| Field | Value |
|---|---|
| Date | 2026-07-18 |
| Event | OpenAI Build Week 2026 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/phase-0-contracts` |
| Starting commit | `953d572c7ba0e81fc408895833cd9fc4f808dfc8` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Phase 0B — Contracts only |
| Status | `STAGED_FOR_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Event summary

- Preserved blueprint bytes while moving it to the canonical `docs/` path.
- Established repository instructions, baseline, decision, ontology, privacy,
  compliance, policy, schema, and fixture contracts.
- Added a shared schema-definition registry and recorded its ownership decision.
- Created no application code, integrations, APIs, databases, agents, Skills,
  runtime, public event fixtures, or expected replay outputs.

### Validation evidence

- JSON syntax and Draft 2020-12 metaschema validation completed with the
  already-installed Python `jsonschema` package.
- All schema references resolved through the shared registry.
- Policy and Goal instances validated against their schemas.
- Policy component weights totaled exactly `1.00`.
- Git ignore, link, blueprint-integrity, and staged-boundary checks were run.

### Open questions

- Official hackathon sources remain uncaptured.
- Public replay fixtures and human privacy approval remain pending.
- Source-specific component normalization and numeric status thresholds remain
  future human product decisions.

## MV-BUILD-002 — Phase 0C1 official hackathon evidence

| Field | Value |
|---|---|
| Date | 2026-07-18 |
| Event | OpenAI Build Week 2026 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/phase-0c-evidence-fixture` |
| Starting commit | `1c2a0cbe8eab45d5489f47fec35c9cc616f50220` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Phase 0C1 — Official hackathon evidence only |
| Status | `STAGED_FOR_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Event summary

- Accessed only the authorized Official Rules, Official FAQ, and Official
  Updates pages.
- Captured sourced facts separately from internal interpretations and planned
  controls.
- Mapped dates, eligibility, project, submission, judging, rights, privacy, and
  optional-plugin requirements without claiming compliance.
- Added an operational submission checklist with an internal target three hours
  before the official deadline.
- Created no product code, fixtures, integrations, API calls, or Phase 1 work.

### Source evidence

- Official Rules: https://openai.devpost.com/rules — accessible at
  `2026-07-18T18:39:47Z`.
- Official FAQ: https://openai.devpost.com/details/faqs — accessible at
  `2026-07-18T18:39:47Z`.
- Official Updates: https://openai.devpost.com/updates — accessible at
  `2026-07-18T18:39:47Z`.
- Official Rules remained controlling wherever official wording differed.

### Open questions

- Entrant eligibility, representative status, and supported territory require
  private human verification.
- Video duration and YouTube visibility wording differ across official sources;
  the current internal controls use below three minutes and YouTube Public.
- No functional project, GPT-5.6 integration, demo, video, final README, test
  path, repository-license decision, or Devpost submission evidence exists yet.
- Human review is required before any requirement can be marked `VERIFIED`.

## MV-BUILD-003 — Phase 0C1 targeted compliance amendment

| Field | Value |
|---|---|
| Date | 2026-07-18 |
| Event | OpenAI Build Week 2026 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/phase-0c-evidence-fixture` |
| Starting commit | `1c2a0cbe8eab45d5489f47fec35c9cc616f50220` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Phase 0C1 — Eligibility source and schedule conflict amendment |
| Status | `STAGED_FOR_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Event summary

- Followed the Official Rules eligibility link to OpenAI's current
  `Supported countries and territories` API documentation without copying the
  country list.
- Required a privacy-preserving human attestation for legal residence,
  age-of-majority eligibility, and absence of applicable exclusions.
- Captured the Official Schedule conflict: Rules end judging on August 5,
  while Schedule ends it on August 9; Rules remain controlling.
- Added a conservative internal control to keep demo, repository access,
  sample data, and judge test path available through at least the end of
  August 12 in `America/Los_Angeles`.
- Changed no product contract, schema, ontology, fixture, policy, privacy
  architecture, application file, or secret file.

### Source evidence

- Official Schedule: https://openai.devpost.com/details/dates — accessible at
  `2026-07-18T19:01:58Z`.
- OpenAI `Supported countries and territories`:
  https://developers.openai.com/api/docs/supported-countries — reached through
  Official Rules and accessible at `2026-07-18T19:01:58Z`.

### Open questions

- Eligibility remains `HUMAN_ELIGIBILITY_ATTESTATION_REQUIRED`; no entrant
  residence, age, or exclusion status has been inferred or verified.
- The Rules-versus-Schedule discrepancy remains `DISPUTED` and requires a final
  official-source recheck before submission.

## MV-BUILD-004 — Phase 0D2 approved contract reconciliation

| Field | Value |
|---|---|
| Date | 2026-07-18 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/phase-0d-contract-reconciliation` |
| Starting commit | `bd9711d` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Phase 0D2 — Approved contract reconciliation only |
| Status | `STAGED_FOR_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Authority and objective

- Reconciled canonical product contracts against
  `LANE_A_V2_FOUNDER_APPROVAL.md`, `CODEX_PRIMARY_HANDOFF_V1.md`,
  `LANE_A_V2_HANDOFF(1).md`, and accepted `MV-ADR-009`.
- Translated approved founder semantics into generic documentation and JSON
  Schema capabilities without encoding fixture-specific Goal, Commitment,
  candidate, count, or rank assertions in generic schemas.

### Files changed

- Updated `docs/CONSTRUCTION_BLUEPRINT.md`, `docs/ontology.md`, and
  `docs/privacy.md`.
- Updated shared, source, event, evidence, constraint, Goal, Commitment,
  Snapshot, production ranking, GraphDelta, and RunRecord schemas.
- Added `schemas/public-goal-set.schema.json`,
  `schemas/expected-attention-ranking.schema.json`, and
  `schemas/privacy-manifest.schema.json`.
- Updated only the future-fixture contract guidance in
  `fixtures/founder-hackathon/README.md`.

### Semantic effects

- Separated operational Goal lifecycle from controlled-demo visibility and
  enforced evidence-backed completion authority.
- Separated trigger/follow-up roles, temporal fields, Calendar and operational
  identities, commitment dimensions, Snapshot membership, conditional
  authorization, and actual execution.
- Preserved the fixed attention policy while separating computed numeric
  rankings from the human ordinal test oracle.
- Added the approved GraphDelta categories, bounded relationship vocabulary,
  historical transition provenance, replay identities, claim guards, and
  per-publication-surface privacy approval with `LOW_MEDIUM` residual risk.
- Kept `attempts_to_resolve` deferred for a versioned repair-loop extension.

### Validation evidence

- Parsed every repository JSON file; validated all schemas against Draft
  2020-12; resolved all `$ref` values; checked unique `$id` values and closed
  object declarations.
- Validated in-memory examples for the public Goal set, trigger SourceEvent,
  lineage, conditional Commitment, Snapshot membership, production ranking,
  human oracle, GraphDelta, Replay RunRecord, and privacy manifest.
- Confirmed the oracle rejects production scores, non-initial Snapshots require
  predecessors, conditional execution requires a satisfied condition, and
  completion or executed-displacement claims require evidence and validation.
- Confirmed policy weights total `1.00`, the policy file is byte-unchanged,
  local Markdown links resolve, and Git whitespace checks pass.

### Compatibility and boundaries

- `EXPECTED_SUPERSEDED_FIXTURE_BREAK`: the untouched
  `goal-hackathon.json` scaffold does not validate against the corrected Goal
  contract and requires the authorized Phase 0C2 Git-aware migration to
  `public-goals.json`.
- `EXPECTED_SUPERSEDED_FIXTURE_BREAK`: the untouched privacy-manifest scaffold
  requires an authorized Phase 0C2 field-level, per-surface migration.
- No fixture payload, application code, test framework, API call, UI, runtime,
  Phase 1 implementation, or external handoff artifact was created or changed.

### Unresolved risks and next step

- Fixture-specific quantities, identities, ranks, exact relationships, and the
  T0 → T1 oracle still require Phase 0C2 fixture construction and validation.
- Cross-artifact replay and no-silent-disappearance checks remain deterministic
  Phase 1 validators after the approved fixture exists.
- Next smallest executable step: after review, commit, merge, and explicit
  authorization, perform the Git-aware `goal-hackathon.json` →
  `public-goals.json` migration and construct only the approved Phase 0C2
  sanitized fixture and human oracle.

## MV-BUILD-005 — Lineage mapping provenance correction

| Field | Value |
|---|---|
| Date | 2026-07-19 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/phase-0d-lineage-contract-fix` |
| Starting commit | `7942371` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Targeted contract correction — lineage mapping provenance only |
| Status | `STAGED_FOR_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Correction

- Added required `explanation`, `creator_type`, and `ontology_version` fields to
  the canonical shared `lineage_mapping` definition.
- Reused the existing `relationship_explanation` and
  `relationship_creator_type` definitions and preserved the approved derivation
  vocabulary, closed-object rule, stable schema identity, and all existing
  lineage semantics.

### Validation and boundary

- Parsed repository JSON, validated schemas and references, and exercised
  positive and required-field rejection examples for the corrected mapping.
- Confirmed dependent schemas remain valid and no fixture, policy, handoff,
  product implementation, or Phase 0C2 payload was changed.
- Phase 0C2 remains paused until this targeted correction is reviewed,
  committed, merged, and separately authorized for resumption.

## MV-BUILD-006 — Phase 0C2 approved sanitized fixture construction

| Field | Value |
|---|---|
| Date | 2026-07-19 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/phase-0c2-fixture` |
| Starting commit | `9bf2329` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Phase 0C2 — Approved sanitized fixture and human oracle |
| Status | `STAGED_FOR_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Authority and objective

- Translated the approved bounded founder semantics into repository-safe input
  fixtures and separate human-authored ordinal and GraphDelta oracles.
- Used the three controlling Human Accelerator artifacts and the explicitly
  authorized sanitized Calendar candidate support artifact through stable,
  non-path artifact references only.

### Files created or migrated

- Migrated `goal-hackathon.json` to `public-goals.json` with Git history
  preserved and replaced the scaffold with the approved three-Goal model.
- Added the Calendar T0 candidate set, public-safe evidence, five operational
  commitments, communication-bounded constraints, one canonical trigger,
  before/after ranking oracles, and expected GraphDelta semantics.
- Migrated the privacy manifest and expanded the fixture README into the replay
  and validation contract.

### Sanitization and review state

- Applied removal, generalization, pseudonymization, a consistently shifted
  synthetic chronology, synthetic evidence summaries, and explicitly safe
  retained contract values.
- Preserved non-reversible artifact-level provenance, all required UNKNOWN
  values, and `LOW_MEDIUM` residual aggregation risk.
- The concrete package remains `PENDING_FIXTURE_LEVEL_HUMAN_REVIEW`; every
  publication surface remains separately pending.

### Validation and boundaries

- Parsed all fixture JSON, validated canonical entities and oracles against the
  repository schemas, resolved schema references, and exercised the complete
  Phase 0C2 semantic and privacy gate set.
- Confirmed the policy is byte-unchanged and totals `1.00`, local Markdown links
  resolve, secrets and raw locators are absent, and Git whitespace checks pass.
- Created no generated Snapshot, computed ranking, runtime GraphDelta,
  RunRecord, application code, integration, model output, or Phase 1 behavior.

### Unresolved unknowns and next step

- Production scores and tie-breaks, exact capacity, CMT-04 execution and repair,
  CMT-05 joint outcome, follow-up outcomes, submission completion, demo
  availability, and final compliance remain unknown.
- Next smallest executable step after human review, commit, merge, and explicit
  authorization: define the Phase 1 deterministic replay input loader and
  validators without changing the human oracle.

## MV-BUILD-007 — Phase 0C2 privacy and wording correction

| Field | Value |
|---|---|
| Date | 2026-07-19 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/phase-0c2-fixture` |
| Milestone | Phase 0C2 — Targeted privacy and wording remediation |
| Status | `STAGED_FOR_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Correction and supersession

- Supersedes only the chronology-safety claim in MV-BUILD-006. The rejected
  constant-offset chronology is no longer the concrete fixture method and must
  not be treated as non-reversible.
- Replaced it with `INDEPENDENT_SYNTHETIC_COARSE_WINDOWS`: whole-hour fixture
  timestamps, independently synthesized Calendar intervals, representative
  duration classes, and a synthetic fixture D-0 that is not the official
  deadline.
- The corrected chronology preserves only required ordering, crossing-T0,
  coarse overlap or conflict, and urgency. It does not retain a common offset,
  exact private gaps, unusual minute values, or exact private durations.
- Generalized candidate, commitment, evidence, ranking, and expected
  GraphDelta wording while preserving approved identities, lifecycle,
  mobility, authority, eligibility, protection, lineage, ordering,
  conditionality, and UNKNOWN states.
- Normalized CMT-04 to the public label `Pending bounded validation`.

### Review state and known input consideration

- The concrete package remains `PENDING_FIXTURE_LEVEL_HUMAN_REVIEW`, residual
  aggregation risk remains `LOW_MEDIUM`, and every public surface remains
  `PENDING`.
- Four repository-safe synthetic Source IDs intentionally remain non-local in
  Phase 0C2. Resolving them as explicit replay inputs is a non-blocking Phase 1
  input-resolution consideration; they are not raw or private locators.
- No fixture semantics, production policy, schema, generated runtime output,
  application code, or Phase 1 behavior was added or changed by this
  correction.

## MV-BUILD-008 — Phase 1A schema registry and fixture-bundle loader

| Field | Value |
|---|---|
| Date | 2026-07-19 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/phase-1a-loader` |
| Starting commit | `cac71a4` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Phase 1A — Schema registry and fixture-bundle loader only |
| Status | `STAGED_FOR_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Objective and stack

- Added the first deterministic executable foundation using Python 3.12,
  `jsonschema` 4.x, Draft 2020-12, and standard-library `unittest`.
- Created `pyproject.toml`, the `src/memoria_viva` contract and fixture-loading
  modules, and focused contract and bundle tests.
- Kept canonical definitions in JSON Schema; no independently maintained
  Python schema copy or application framework was introduced.

### Contract boundaries

- The schema registry discovers every canonical schema, rejects invalid or
  duplicate identities, resolves references through a closed local registry,
  and returns deterministic public-safe validation issues.
- `RuntimeBundle` loads only the approved Goals, Calendar candidates,
  evidence, commitments, constraints, canonical trigger, privacy manifest, and
  attention policy.
- `OracleBundle` separately loads the before/after ordinal rankings and
  expected GraphDelta. There is no combined production-input bundle.
- Deterministic read-only indexes enforce identity, lineage, evidence, Goal,
  constraint, SourceEvent, Calendar, commitment, and attention-reference
  integrity without changing case or identifier syntax.

### Validation and preserved warnings

- Ran 23 `unittest` cases covering registry closure, schema and instance
  rejection, no-network reference behavior, fixture validation, immutability,
  bundle separation, structural invariants, duplicate IDs, unresolved
  evidence, warning behavior, and repeatable loading.
- Ran Python bytecode compilation for `src` and `tests`; loading creates no
  artifact under `runs/`.
- Preserved structured warnings for the four approved non-local synthetic
  Source IDs, draft policy status, null policy effective time, pending
  publication surfaces, and unknown final compliance.

### Scope boundary and next step

- Created no Snapshot, state transition, score, computed ranking, GraphDelta,
  RunRecord, oracle comparison, API call, UI, service, database, agent,
  integration, or Phase 1B behavior.
- Next smallest executable step after review, commit, merge, and explicit
  authorization: define the bounded deterministic Snapshot T0 construction
  rules and tests while keeping scoring and transition behavior out of scope.

## MV-BUILD-009 — Phase 1B canonical serialization and Snapshot T0

| Field | Value |
|---|---|
| Date | 2026-07-19 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/phase-1b-snapshot-t0` |
| Starting commit | `49a641d` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Phase 1B — Canonical serialization and immutable Snapshot T0 only |
| Status | `STAGED_FOR_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Objective and canonicalization contract

- Added the repository-versioned `MV_CANONICAL_JSON_V1` contract, explicitly
  scoped to Python 3.12 and not claimed as RFC 8785.
- Canonical bytes use UTF-8, lexicographically sorted object keys, preserved
  array order, unescaped Unicode, no insignificant whitespace, and finite JSON
  numbers only. Unsupported values, NaN, and Infinity are rejected.
- SHA-256 values use `sha256:<64 lowercase hexadecimal characters>`.

### Digest and identity rules

- The runtime input digest covers exactly the public Goals, Calendar T0,
  evidence, operational commitments, constraints, canonical event, privacy
  manifest, and attention policy under stable logical keys. It excludes
  oracles, filesystem metadata, wall-clock state, and non-semantic warnings.
- The Snapshot state digest covers the complete serialized Snapshot state
  except `state_digest` itself, preventing self-reference.
- Snapshot T0 identity uses `MV_SNAPSHOT_IDENTITY_V1`, the fixture scenario
  identity, temporal role `T0`, and runtime input digest. Its stable form is
  `SNAPSHOT-T0-<20 lowercase digest characters>` and does not depend on the
  final state digest.

### T0 temporal and membership projection

- `captured_at` uses the fixture README's canonical Calendar
  `synthetic_anchor_at`, `2030-02-10T12:00:00Z`; no system or Git time is read.
- Active membership contains three Goals, eight active Calendar candidates,
  and CMT-03 through CMT-05. CMT-T0-07 and CMT-T0-08 remain explicitly
  excluded but retained with their approved evidence, reason, and uncertainty.
- CMT-01 and CMT-02, the canonical trigger, follow-ups, and trigger-derived
  constraints are absent from applied T0 state. Goal catalog references do not
  activate D-0 or candidate artifact requirements.
- Existing lineage stays attached to embedded Commitment records and is not
  converted into graph edges. No qualifying independent T0 relationship is
  present, so the relationship collection is empty.
- Capacity remains `UNKNOWN`; ranking and GraphDelta references remain null.
  Generated-output privacy and review states remain unapproved, while the
  runtime privacy manifest retains `LOW_MEDIUM` risk and pending surfaces.

### Files and validation

- Added `src/memoria_viva/canonical.py`, `src/memoria_viva/snapshot.py`,
  `tests/test_canonical.py`, and `tests/test_snapshot_t0.py`.
- Exported the bounded public functions from `src/memoria_viva/__init__.py`.
- The one-argument Snapshot builder resolves only the repository's closed local
  schema registry for output validation. It accepts no path, reads no fixture
  file, performs no network retrieval, and copies no schema definition.
- Ran 58 `unittest` cases and Python bytecode compilation successfully.
- Two independent processes produced identical 16,192-byte canonical
  Snapshots, Snapshot identity, state digest, active ordering, and excluded
  ordering. No artifact was written under `runs/`.

### Scope boundary and next step

- Implemented no trigger transition, Snapshot T1, score, ranking, GraphDelta,
  RunRecord, oracle comparison, persistence, replay CLI, API, UI, integration,
  agent, or Phase 1C behavior.
- Next smallest executable step after review, commit, merge, and explicit
  authorization: implement the pure trigger application that constructs
  immutable Snapshot T1 from RuntimeBundle and Snapshot T0, without scoring or
  output persistence.

## MV-BUILD-010 — Phase 1C canonical trigger and Snapshot T1

| Field | Value |
|---|---|
| Date | 2026-07-19 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/phase-1c-trigger-t1` |
| Starting commit | `a4c8fd5` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Phase 1C — Pure trigger application and immutable Snapshot T1 only |
| Status | `STAGED_FOR_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Objective and transition contract

- Added the repository-versioned `MV_TRIGGER_TRANSITION_V1` contract with
  policy ID `mv.canonical-trigger-transition`, version `1.0.0`, stable rule
  IDs, deterministic rule ordering, and no model, oracle, network, random,
  wall-clock, or caller-path input.
- `apply_canonical_trigger(runtime_bundle, snapshot_t0)` accepts only the
  validated immutable RuntimeBundle and Snapshot T0. It reads no fixture file
  and performs no automatic correction.
- Input validation requires the canonical T0 role, initial/predecessor state,
  runtime-derived identity and state, exact T0 commitment and exclusion
  membership, no trigger-derived T0 constraints, one normalized TRIGGER,
  null `occurred_at`, communication-only authority, and the approved
  trigger-created catalog objects.

### T1 time, identity, and state

- `captured_at` uses the trigger's synthetic `received_at`,
  `2030-02-10T12:00:00Z`. T0 and T1 may share that synthetic boundary;
  temporal role and the explicit predecessor chain establish ordering.
- Snapshot identity uses scenario identity, role `T1`, runtime input digest,
  predecessor ID, transition contract, policy ID, and policy version. The
  golden deterministic ID is `SNAPSHOT-T1-8280b33463a480998d3e`.
- Activated CMT-01 and CMT-02 while preserving CMT-03 through CMT-05, all
  three Goals, all eight active Calendar candidates, and the two
  excluded-but-retained candidates. No prior T0 object or evidence silently
  disappears.
- Added D-0 and the bounded artifact-requirement constraint to Snapshot
  membership without changing their cataloged status or
  `COMMUNICATION_EVIDENCE_ONLY` authority. The latter remains `PROPOSED`, so
  membership does not claim verified official requirements.

### Relationships and execution safeguards

- Materialized seven stable deterministic relationships in rule order:
  CMT-02 `depends_on` CMT-01; CMT-01 and CMT-02 each `constrained_by` D-0;
  CMT-01 `conflicts_with` CMT-04; CMT-01 conditionally `displaces` CMT-04;
  and CMT-02 conflicts with the two active flexible Calendar windows whose
  committed synthetic intervals fall between trigger receipt and D-0.
- Flexible-capacity conflicts are derived from runtime inclusion, eligibility,
  mobility, and temporal fields. Coexistence alone never creates an edge.
- Every edge records evidence, confidence, epistemic state, stable rule
  identity, deterministic creator type, uncertainty in its schema-supported
  explanation, ontology version, and trigger-derived creation time.
- CMT-04 retains its structured condition, opportunity cost, repair,
  founder authority, uncertainty, and `UNKNOWN` execution. Its displacement
  relationship explicitly states that policy authorization is not movement;
  `displaced_by_refs` remains empty. CMT-05 remains confirmation-required
  under JOINT authority.

### Immutability, privacy, digests, and validation

- Reused the Phase 1B frozen, recursively immutable Snapshot representation
  and centralized schema validation/finalization without changing its JSON
  shape. Applying the trigger mutates neither RuntimeBundle nor Snapshot T0.
- Snapshot T1 state digest covers every semantic field except
  `state_digest` itself. Tests prove sensitivity to commitment and constraint
  membership, relationships, predecessor, evidence, privacy, and uncertainty.
- Capacity remains `UNKNOWN`; ranking and GraphDelta references remain null.
  Generated-output privacy and review states remain unapproved, runtime
  residual risk remains `LOW_MEDIUM`, and every publication surface remains
  `PENDING`.
- Ran 90 `unittest` cases and Python bytecode compilation successfully. Two
  independent processes produced identical 30,921-byte canonical Snapshots,
  ID, state digest, active/excluded ordering, and relationship ordering. No
  output was written under `runs/`.

### Scope boundary and next step

- Implemented no component extraction, score, computed ranking, GraphDelta
  output, RunRecord, oracle comparison, persistence, replay CLI, API, model,
  UI, service, database, agent, integration, scheduling, or deployment work.
- Next smallest executable step after review, commit, merge, and explicit
  authorization: define deterministic attention-component extraction from the
  immutable T0/T1 state while keeping ranking, GraphDelta, and persistence out
  of scope until separately authorized.

## MV-BUILD-011 — Phase 1D bounded replay attention scoring

| Field | Value |
|---|---|
| Date | 2026-07-19 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/phase-1d-attention-scoring` |
| Starting commit | `844c924` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Phase 1D — Versioned extraction, scoring, ranking, and ordinal comparison |
| Status | `SCORING_ORACLE_MISMATCH` |
| Commit | None |
| Push | None |

### Human policy decisions and versioned authority

- Recorded MV-ADR-010 and added feature policy
  `mv.attention-feature-policy@1.0.0`, digest
  `sha256:5b33221baa9eab0093f96f981eaa64fd90e1d0d4278a0d83f6e6181a9c547990`.
  Its schema-validated authority is limited to Replay Mode. The compatible
  base attention policy remains `draft`, has null `effective_at`, and is not
  claimed as production-active.
- The feature policy owns the approved deterministic extraction rules for
  temporal urgency, downstream impact, strategic alignment, conflict or
  displacement, event novelty, and conservative evidence confidence. It
  references rather than duplicates the six base-policy weights.
- `UNKNOWN` is never coerced to zero. Protection and dependency are precedence
  guardrails without numeric bonuses. Confirmation changes actionability and
  approval metadata without creating a numeric bonus or protected band.
- Production arithmetic uses `Decimal`, retains unrounded scores for ordering,
  rounds display scores only with two-place `ROUND_HALF_UP`, and identifies
  each calculation from Snapshot, base-policy, feature-policy, item, and
  normalized-component semantics.

### Computed rankings and isolated oracle result

- T0 computed complete order is ATTN-CMT-03 (`0.660`), ATTN-CMT-05
  (`0.6525`), and ATTN-CMT-04 (`0.600`). T1 computed complete order is
  ATTN-CMT-01 (`0.840`), ATTN-CMT-02 (`0.870`), ATTN-CMT-04 (`0.740`),
  ATTN-CMT-03 (`0.660`), and ATTN-CMT-05 (`0.6525`). Dependency precedence
  correctly places CMT-01 before its higher-scored dependent CMT-02.
- Four Calendar-only items have explicit Goal, temporal, conflict,
  novelty, and evidence signals but no explicit downstream-impact or
  opportunity-cost level. The approved rule therefore leaves
  `downstream_impact` `UNKNOWN` and produces no numeric score or rank for
  ATTN-CALENDAR-CMT-T0-01, -06, -09, or -10.
- The independently loaded before oracle is `BLOCKED` first at expected rank 1
  because ATTN-CALENDAR-CMT-T0-10 is unscored. The after oracle is `BLOCKED`
  first at expected rank 3 for the same reason. No weight, extraction value,
  guardrail, fixture, or human expectation was changed to force a match.
- Production extraction and ranking import no OracleBundle, comparator module,
  expectation filename, expected rank, or expected direction. Comparator
  access begins only after both production rankings are complete.

### Files, tests, and scope boundary

- Added the feature-policy schema and configuration, production attention
  module, isolated ordinal comparator, and focused scoring/comparator tests;
  updated public package exports and the canonical schema-count assertion.
- Ran 114 `unittest` cases, bytecode compilation, closed-schema registration,
  and two independent scoring processes. Production components, raw
  contributions, displayed scores, calculation digests, ranking identities,
  order, and comparator outcomes were deterministic. No file was written under
  `runs/`.
- Implemented no GraphDelta output, RunRecord, persistence, replay CLI, model
  call, API, UI, service, database, agent, integration, scheduling, or
  deployment behavior.
- Next smallest task requires a bounded human product decision: add an explicit
  generic downstream-impact or opportunity-cost signal for Calendar-only
  attention candidates, or define a separately versioned incomplete-item
  ranking policy. Until then, the oracle mismatch must remain visible and this
  Phase 1D set must not be staged for commit.

## MV-BUILD-012 — Phase 1D bounded scoring policy resolution

| Field | Value |
|---|---|
| Date | 2026-07-19 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/phase-1d-attention-scoring` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Phase 1D — Targeted human policy resolution |
| Status | `STAGED_FOR_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Human decision and policy version

- Preserved MV-BUILD-011 as the truthful initial `SCORING_ORACLE_MISMATCH`.
  The evaluated but uncommitted feature-policy `1.0.0` digest was
  `sha256:5b33221baa9eab0093f96f981eaa64fd90e1d0d4278a0d83f6e6181a9c547990`.
- Applied the founder-approved bounded-Replay amendment as
  `mv.attention-feature-policy@1.1.0`, digest
  `sha256:fd091478b350d8f66e3fa031a9efa179f2908bceba6061c20276f45fd27a8a72`.
  The base policy remains byte-identical, draft, null-effective, and weighted
  exactly as before; this is not a production-activation claim.
- Eligible Calendar-only items without stronger explicit impact now use the
  approved mobility fallback: `PROTECTED → HIGH/0.80`,
  `NEEDS_CONFIRMATION → MEDIUM_HIGH/0.65`, `FLEXIBLE → LOW/0.25`,
  `DISPLACEABLE → LOW/0.25`, and `CANCELABLE → NONE/0.00`. Unsupported
  mobility remains `UNKNOWN`; operational commitments retain their explicit
  cost semantics.
- Ordered conflict extraction now assigns `0.00` to an explicitly
  DISPLACEABLE conditional-displacement target while execution remains
  UNKNOWN or not executed. This removes only a numeric deferment-target bonus;
  relationship, condition, cost, repair, authority, evidence, and uncertainty
  remain visible. Other supported unresolved conflict targets remain `0.60`.
- Event novelty now reflects material changes to an object's own semantic
  state. Trigger-created objects remain `1.00`; own-state material changes are
  `0.50`; relationship-only or unchanged pre-existing state is `0.00`.

### Computed component tables

Component order is temporal urgency, downstream impact, strategic alignment,
conflict/displacement, event novelty, and evidence confidence. Scores shown are
unrounded internal scores.

| T0 item | Components | Score | Band | Rank |
|---|---|---:|---|---:|
| ATTN-CALENDAR-CMT-T0-10 | `.35, .80, .70, .00, .00, .70` | .4575 | PROTECTED | 1 |
| ATTN-CMT-03 | `1.00, .80, .85, .00, .00, .80` | .660 | STANDARD | 2 |
| ATTN-CMT-05 | `.85, .65, .85, .40, .00, .80` | .6525 | STANDARD | 3 |
| ATTN-CALENDAR-CMT-T0-01 | `.85, .65, .70, .40, .00, .80` | .6225 | STANDARD | 4 |
| ATTN-CMT-04 | `1.00, .50, .85, .00, .00, .80` | .600 | STANDARD | 5 |
| ATTN-CALENDAR-CMT-T0-06 | `.75, .25, .70, .00, .00, .70` | .4475 | STANDARD | 6 |
| ATTN-CALENDAR-CMT-T0-09 | `.55, .25, .70, .00, .00, .70` | .3975 | STANDARD | 7 |

| T1 item | Components | Score | Band | Rank |
|---|---|---:|---|---:|
| ATTN-CMT-01 | `.60, .80, 1.00, 1.00, 1.00, .80` | .840 | PROTECTED | 1 |
| ATTN-CMT-02 | `.60, 1.00, 1.00, 1.00, 1.00, .70` | .870 | PROTECTED | 2 |
| ATTN-CALENDAR-CMT-T0-10 | `.35, .80, .70, .00, .00, .70` | .4575 | PROTECTED | 3 |
| ATTN-CMT-03 | `1.00, .80, .85, .00, .00, .80` | .660 | STANDARD | 4 |
| ATTN-CMT-05 | `.85, .65, .85, .40, .00, .80` | .6525 | STANDARD | 5 |
| ATTN-CALENDAR-CMT-T0-01 | `.85, .65, .70, .40, .00, .80` | .6225 | STANDARD | 6 |
| ATTN-CMT-04 | `1.00, .50, .85, .00, .00, .80` | .600 | STANDARD | 7 |
| ATTN-CALENDAR-CMT-T0-06 | `.75, .25, .70, .60, .00, .70` | .5375 | STANDARD | 8 |
| ATTN-CALENDAR-CMT-T0-09 | `.55, .25, .70, .60, .00, .70` | .4875 | STANDARD | 9 |

### Comparison, validation, and boundaries

- Computed T0 ranking ID is `RANKING-BEFORE-20f7aefbef267eb77463`;
  the committed before oracle comparison is `PASS`.
- Computed T1 ranking ID is `RANKING-AFTER-02c6078edf0b8c522cf1`;
  the committed after oracle comparison is `PASS`. Dependency precedence still
  places CMT-01 before its higher-scored dependent CMT-02.
- Production ranking completed before OracleBundle loading. Source and
  behavior guards confirm no oracle import, filename, expected rank, expected
  direction, or fixture-specific identity enters extraction or scoring.
- Ran 122 `unittest` cases, bytecode compilation, all 17 schema validations,
  closed reference resolution, and independent-process determinism checks.
  Components, contributions, scores, calculation digests, ranking identities,
  orders, and comparator results match across processes.
- No base weight, fixture, Snapshot, transition, ontology, blueprint, privacy
  contract, or oracle changed. No automatic tuning occurred and no file was
  written under `runs/`.
- Remaining risk: the mobility fallback is authorized only for bounded Replay
  Mode and requires later empirical recalibration before any production claim.
  Next smallest task after review and commit is deterministic GraphDelta
  generation from T0 and T1, kept separate from persistence and RunRecord work.

## MV-BUILD-013 — Phase 1E deterministic replay core

| Field | Value |
|---|---|
| Date | 2026-07-19 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/phase-1e-replay-core` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Phase 1E — GraphDelta, RunRecord, and in-memory replay |
| Status | `STAGED_FOR_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Objective and deterministic production outputs

- Added one pure in-memory replay sequence that keeps `RuntimeBundle` and
  `OracleBundle` separate, constructs the known T0 and T1 Snapshots and
  rankings, completes the production GraphDelta, runs isolated comparisons,
  and creates the RunRecord last. It performs no persistence, CLI operation,
  network access, model call, or UI behavior.
- `MV_GRAPH_DELTA_V1` emits 21 deterministic evidence-backed changes across
  `ADDED`, `UPDATED`, `CONFLICTED`, `DISPLACED`, `PROTECTED`,
  `REQUIRES_CONFIRMATION`, and `UNCHANGED`. The resulting identity is
  `GRAPH-DELTA-T0-T1-f9f16318c40137871a5c`, with transition digest
  `sha256:f104401e976ddd187971a884ba1d1d0565cbf4ca253fb40d34465f54dae41ccc`.
- Production delta generation uses only RuntimeBundle, immutable Snapshots, and
  computed rankings. It retains actual T1 relationship identities in the
  delta and exposes a deterministic semantic index to the comparator. It never
  imports OracleBundle, reads the expected GraphDelta, or copies human change
  IDs or placeholder digests.

### Comparator, receipt, and replay identity

- The GraphDelta comparator matches semantic tuples for typed objects and
  relationship endpoints rather than oracle change IDs. It checks required
  evidence subsets, conditionality, execution, displacement safeguards,
  uncertainty, missing expected semantics, unapproved relationships, invalid
  production data, and stronger unsupported claims. The human-expectation
  evidence reference remains oracle provenance rather than a production
  generation input.
- The immutable RunRecord receipts runtime, base and feature policy,
  transition-contract, and oracle identities and digests; both Snapshots, both
  rankings, and GraphDelta; schema and ontology versions; all comparison
  results; approvals; unresolved questions; warnings; privacy state; and null
  model metadata for Replay Mode. Its ID is
  `RUN-REPLAY-b2fcd51d239acf29f5c3`, and its record digest is
  `sha256:379d8cae3e0203531f9ab752873dc8de61920050692b92c4a0cc0ca9830adfc8`.
- RunRecord excludes itself from `output_artifacts` and the replay-output
  digest. Human-oracle placeholder digests are excluded from semantic input
  identity. The complete ReplayResult canonical digest is
  `sha256:3ae0d566fef04029972e1875f2026e11cd9a60d39208241f030330e6237c6f15`.

### Claims, warnings, validation, and boundary

- Ranking-before, ranking-after, and GraphDelta comparisons are all `PASS`.
  CMT-04 displacement remains conditional with execution `UNKNOWN`; CMT-05
  and CMT-T0-01 remain confirmation-required; excluded objects remain retained;
  and `attempts_to_resolve` is absent.
- Compliance, submission completion, and Goal completion remain
  `NOT_CLAIMED`; executed displacement remains `UNKNOWN` and explicitly
  `NOT_CLAIMED`. The generated output remains `SANITIZED_PRIVATE` and
  `NOT_REVIEWED`. All five publication surfaces remain `PENDING`.
- Preserved warnings that the base policy is draft, execution is bounded Replay
  Mode only, four repository-safe Source identities are non-local, publication
  remains pending, final compliance is unknown, and generated output has not
  completed publication review.
- Added focused GraphDelta, comparator, RunRecord, replay, immutability,
  no-oracle-leakage, and independent-process tests. All 158 `unittest` cases
  pass, every generated instance validates against the existing closed schema
  registry, and independent replay processes produce byte-identical IDs,
  digests, comparisons, and canonical ReplayResult bytes.
- Implemented no output persistence, replay CLI, model call, GPT-5.6 use, API,
  UI, web service, database, agent, integration, scheduler, or deployment. No
  file was written under `runs/`.
- Next smallest task after review and commit is a separate read-only boundary
  decision for an explicit replay CLI and local ignored persistence, without
  adding model calls or a service architecture.

## MV-BUILD-014 — Phase 2 judge-ready replay experience

| Field | Value |
|---|---|
| Date | 2026-07-19 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/phase-2-demo` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Phase 2 — CLI, presentation, Streamlit, and explanation layer |
| Status | `STAGED_FOR_LOCAL_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Objective and judge path

- Added one bounded judge path around the unchanged deterministic replay core:
  a no-write-by-default CLI, an immutable public-safe presentation adapter,
  and a single-page Streamlit experience centered on **Run deterministic
  replay**. The story is presented as before, external event, after, and why
  attention changed, while technical receipts remain available separately.
- The CLI prints a concise replay summary or a deterministic JSON projection.
  An explicit export is restricted to a caller-selected directory beneath
  `runs/`, uses canonical JSON and atomic replacement, and refuses overwrite
  unless `--force` is supplied. Exported artifacts remain unapproved for
  publication.
- The presentation adapter derives all display state from `ReplayResult` and
  committed public-safe metadata. It exposes rank movement, all seven
  GraphDelta categories, evidence and uncertainty, oracle status, receipts,
  warnings, and publication state without exposing mutable core objects,
  filesystem paths, credentials, or private source data.

### Explanation boundary and dependencies

- Added the closed Draft 2020-12 DecisionBrief contract and an optional
  GPT-5.6 explanation adapter using the official OpenAI Python SDK Responses
  API with strict structured output. The model receives only the sanitized
  DemoViewModel explanation projection and cannot alter deterministic state,
  scores, rankings, GraphDelta, or claims.
- GPT generation is user-triggered and never runs during import or initial
  render. Environment credentials take precedence; `.env.local` is a local
  non-overriding fallback and Streamlit secrets remain server-side. Missing
  credentials, API failure, timeout, or invalid output leaves the replay fully
  usable and returns a non-secret diagnostic with the always-available
  **Deterministic Engine Brief**.
- Declared the tested Python 3.12 demo dependency set through the editable
  local package target `-e .[demo]`, preserving repository-relative canonical
  contracts and fixture loading in both local and Streamlit environments:
  `jsonschema==4.26.0`, `openai==2.46.0`, `python-dotenv==1.2.2`, and
  `streamlit==1.54.0`. No framework, data library, graph library, or second AI
  SDK was added.

### Validation, publication, and next action

- Added CLI, presentation, explainer, and Streamlit tests, including export
  containment, immutability, deterministic JSON, no-secret behavior, mocked
  Responses API structured output, failure fallback, no model call on initial
  render, and Streamlit AppTest coverage. The complete suite contains 197
  tests; bytecode compilation, schema registration, clean dependency install,
  CLI smoke, and local Streamlit health checks were included in the gate.
- The known Snapshot, ranking, GraphDelta, RunRecord, and Replay identities and
  digests remain unchanged. The deterministic engine still passes all three
  human-oracle comparisons. No core module, fixture, base or feature policy,
  existing contract, ontology, blueprint, or privacy contract changed.
- No paid or live GPT-5.6 request was made. Status remains
  `LIVE_GPT_5_6_SMOKE_PENDING`. No deployment occurred, no persistent output
  remains under `runs/`, and `PUBLIC_FIXTURE`, `REPOSITORY_DOCS`, `DEMO_UI`,
  `DEMO_VIDEO`, and `DEVPOST_SUBMISSION` remain `PENDING`.
- Next exact action after commit is local founder review: run the CLI, inspect
  the four Streamlit tabs, explicitly request one GPT-5.6 brief, and review the
  rendered public surface before any deployment or publication authorization.

### Live GPT-5.6 smoke and wording clarification

- `LIVE_GPT_5_6_SMOKE: PASS`. This supersedes the earlier pending smoke status.
  The explicit founder-run request preserved exact rankings and displayed
  scores; `PLANNED`, `UNKNOWN`, and `NOT_EXECUTED` execution states;
  conditional displacement as not executed; confirmation and approval
  requirements; uncertainty; evidence boundaries; and deterministic-engine
  authority.
- Clarified the explanation instruction boundary: the conditional displacement
  relationship is authorized and established, while its execution remains
  `UNKNOWN`. Explanations must not say that no conditional relationship exists;
  they must state that conditional movement was not executed or that execution
  remains unknown.
- No schema, model, deterministic core semantic, ranking, evidence, validation,
  fixture, policy, GraphDelta, or UI behavior changed. No additional live API
  request was made during this correction.

## MV-BUILD-015 — Public demo release validation

| Field | Value |
|---|---|
| Date | 2026-07-19 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/release-metadata` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Final release metadata — deployed demo validation |
| Status | `STAGED_FOR_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Deployment and verified release surface

- Public deployment URL:
  <https://memoria-viva-attention-graph-kmhfgbtexurbgcqvhaht8v.streamlit.app/>
- Deployment platform is Streamlit Community Cloud; deployment branch is
  `main`.
- `DEPLOYED_SMOKE: PASS` and `PUBLIC_APP_ACCESS: PASS`. Human verification in
  incognito/no-login mode confirmed that the public app loads, all four tabs
  render, deterministic replay works, and the GPT-5.6 Decision Brief works.
- `LIVE_GPT_5_6_SMOKE: PASS`. The deterministic-engine authority boundary and
  exact ranking, score, execution-state, conditionality, evidence,
  uncertainty, confirmation, and approval semantics remained intact.
- Sanitized JSON download review is `PASS`. No secret, private path, raw private
  evidence, or external source material was exposed.
- The deployed ReplayResult digest remains
  `sha256:3ae0d566fef04029972e1875f2026e11cd9a60d39208241f030330e6237c6f15`.
- Release validation remains 200 passing tests, with CLI smoke, Streamlit local
  smoke, deployed smoke, and all three oracle comparisons at `PASS`.

### Publication authority and remaining gates

- `PUBLIC_FIXTURE: APPROVED` only for the committed sanitized canonical fixture
  and sanitized replay projection reviewed through the deployed UI and
  downloadable JSON. This approval does not include raw private evidence or
  external source material.
- `DEMO_UI: APPROVED`.
- `REPOSITORY_DOCS: PENDING_FINAL_REVIEW`.
- `DEMO_VIDEO: PENDING`.
- `DEVPOST_SUBMISSION: PENDING`.
- `FINAL_COMPLIANCE: UNVERIFIED`.
- GPT-5.6 remains an explanation layer over deterministic results. The feature
  policy remains bounded-Replay only; communication evidence remains distinct
  from official-rule authority; and no real Gmail or Calendar integration was
  introduced.
- This milestone changes release metadata only. No deterministic core, replay,
  scoring, GraphDelta, schema, fixture, policy, Streamlit behavior, explainer
  behavior, test, dependency, or generated output changed.

## MV-BUILD-016 — Grounded conversational interface

| Field | Value |
|---|---|
| Date | 2026-07-20 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/final-ux-chat` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Final UX pass — grounded conversational interface |
| Status | `STAGED_FOR_LOCAL_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Conversation architecture and product boundary

- Grounded conversation is now the primary presentation surface:
  `question → deterministic intent → verified state selection → immutable
  ChatAnswer → optional GPT-5.6 language rewrite → evidence and replay receipt`.
- The deterministic router supports exactly `CURRENT_ATTENTION`,
  `WHAT_CHANGED`, `WHY_ITEM`, `PROTECTED_ITEMS`, `REQUIRES_CONFIRMATION`,
  `EVIDENCE`, `UNKNOWNS`, `REPLAY_PROOF`, `MEMORY_STATE`, and the bounded
  `UNSUPPORTED` response. Intent precedence and public-subject matching are
  explicit and versioned in code.
- A question selects an explanation from the committed replay. It is never
  passed to component extraction, scoring, ranking, transition, GraphDelta, or
  RunRecord generation. No contextual reranking or policy recalibration was
  introduced.
- `MV_CHAT_ANSWER_V1` derives a stable answer identity from normalized question,
  intent, matched public item, ReplayResult digest, and contract version. Its
  public attention rows preserve exact rank, displayed score, status,
  protection, confirmation, execution, and evidence state.
- GPT-5.6 receives only a sanitized completed ChatAnswer projection. It may
  author three conversational strings; model identity, answer identity, intent,
  replay digest, evidence, unknowns, and approval fields are controlled by the
  application and validated locally. The deterministic answer remains visible
  after every credential, API, timeout, or validation failure.

### User experience and verification

- Streamlit now opens with the grounded conversation, six suggested prompts,
  current-session-only history, a clear control, and a top-three current
  attention rail. The detailed before/event/after experience remains available
  under `Inspect deterministic system` with all four prior technical tabs.
- The UI does not call GPT-5.6 on import, page load, deterministic question
  submission, or suggested-prompt click. A separate per-answer button is the
  only GPT chat trigger. Conversation is not persisted or written under
  `runs/`.
- Added the closed Draft 2020-12 `GroundedChatResponse` contract, deterministic
  chat tests, mocked strict Responses API tests, and expanded Streamlit AppTest
  coverage. All **232 tests pass**; `compileall`, CLI replay, schema registration,
  AppTest, and a localhost Streamlit health check pass without a GPT request.
- The canonical replay remains `PASS` for all three oracle comparisons with
  ReplayResult digest
  `sha256:3ae0d566fef04029972e1875f2026e11cd9a60d39208241f030330e6237c6f15`.
- No fixture, policy, deterministic core module, existing core schema,
  ontology, blueprint, privacy contract, publication data, score, ranking,
  Snapshot, transition, GraphDelta, RunRecord, oracle, or dependency changed.
  Public deployment review of the new UX remains pending until after human
  local review, commit, merge, and deployment.

### Next exact action

- Run the six suggested questions locally, inspect one conditional-item answer,
  optionally test one GPT-5.6 rewrite, and confirm the preserved deterministic
  inspector before authorizing commit and deployment review.

## MV-BUILD-017 — Guided single-question UX simplification

| Field | Value |
|---|---|
| Date | 2026-07-20 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/final-ux-chat` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Final UX pass — guided verified question interface |
| Status | `STAGED_FOR_LOCAL_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Simplified product surface and preserved architecture

- Superseded the visible chat history, arbitrary text input, clear-conversation
  control, and permanent attention rail with one centered select-only control.
  The six public questions continue through the existing deterministic intent
  router and immutable `MV_CHAT_ANSWER_V1`; no scoring or contextual reranking
  path was introduced.
- The primary view now renders one concise answer at a time: headline, direct
  answer, relevant ranked items, evidence count, replay verification, and only
  the approval or uncertainty warning that applies. Detailed receipts remain
  available in compact expanders.
- Added a deterministic public-safe Graphviz projection of the principal story:
  event creation, dependency order, protected continuity, conditional
  displacement with execution `UNKNOWN` and not executed, and the two
  confirmation-required items. The complete 21-change GraphDelta remains in
  `Inspect deterministic system` rather than the primary graph.
- Preserved the full four-tab deterministic inspector, deterministic replay,
  GPT-5.6 Decision Brief, and sanitized JSON download.

### Optional explanation boundary and verification

- The optional GPT-5.6 response now authors only `what_this_means`,
  `recommended_next_move`, and `approval_or_uncertainty_note`. Application code
  still controls model identity, answer identity, intent, ranks, scores,
  evidence, uncertainty, approvals, and replay identity.
- The recommendation is constrained to the next smallest action allowed by the
  verified rank, prerequisite order, execution state, uncertainty, and approval
  boundaries. It cannot rerank, predict future events, claim completion or
  executed displacement, invent evidence, or bypass approval.
- Added `graphviz==0.21` to the pinned demo dependency set. No graph library is
  used by the deterministic replay core.
- All **241 tests pass**, including focused guided-question, GPT semantic guard,
  Graphviz principal-story, no-GPT-on-load, and narrow-layout checks. Bytecode
  compilation, CLI replay, schema registration, core digest comparison,
  public replay JSON comparison, AppTest, and local Streamlit health are part of
  the final gate. A real local Playwright pass at `390 × 844` confirmed the
  centered selector, single-answer hierarchy, compact ranked rows, collapsed
  inspector, and rendered attention graph with zero browser-console errors.
- No fixture, policy, deterministic core module, replay output, score, rank,
  Snapshot, transition, GraphDelta, RunRecord, oracle, ontology, blueprint, or
  privacy boundary changed. No output is written under `runs/`.

### Next exact action

- Locally select each of the six verified questions, inspect the compact graph
  at desktop and narrow width, optionally request one GPT-5.6 recommendation,
  and verify the complete hidden inspector before authorizing commit and a new
  deployed-surface review.

## MV-BUILD-018 — Final guided UX and recommendation reliability correction

| Field | Value |
|---|---|
| Date | 2026-07-20 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/final-ux-chat` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Non-empty guided experience and bounded GPT recommendation |
| Status | `STAGED_FOR_LOCAL_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Final product correction

- Preselected **What matters now?** so the primary surface always opens with a
  complete deterministic answer. The same six-option router remains available;
  no arbitrary input, history, or contextual reranking was introduced.
- Added a public-safe Goal context derived from Snapshot T1 and the existing
  event Goal reference. All three Goals appear as compact chips; `GC-01 —
  Product validation` is highlighted as `Active`, `Incomplete`, and `Official
  requirements unverified`. The UI explicitly states that changed attention
  does not prove Goal completion.
- Added one primary-view clarification that rank is the verified attention
  order while score is a supporting signal and protection or dependency may
  determine final order.
- Restricted the optional GPT-5.6 recommendation control to **What matters
  now?** and **What should happen next?** only. The three authored language
  fields share a 130-word semantic ceiling, and existing guards continue to
  reject reranking, score changes, completion, compliance, future outcomes,
  executed displacement, unsupported evidence, and approval bypass.
- Strengthened the model-free **What should happen next?** answer to freeze the
  minimum verifiable demonstration scope, verify the public demo, then complete
  the dependent package while reviewing conditional displacement and human
  approvals separately. No action is represented as executed.
- Reworked the public graph into a compact top-to-bottom Goal → event → verified
  attention narrative. Confirmation-required items now connect to a single
  `Human confirmation required` lane; conditional authorization, no execution,
  and `UNKNOWN` remain explicit.

### Verification and unchanged authority

- The complete suite contains **247 passing tests**, including the non-empty
  initial state, Goal derivation, incomplete Goal state, single order-versus-
  score explanation, two-question GPT gate, 130-word recommendation ceiling,
  deterministic next action, and connected confirmation lane.
- No live GPT request was made. The deterministic answer remains sufficient for
  every question, and no GPT client is created on page load or selection.
- AppTest and a real local Playwright pass at `390 × 844` confirmed the
  preselected answer, Goal chips, single order-versus-score explanation,
  two-question GPT gate, connected vertical Graphviz narrative, and collapsed
  technical inspector with zero browser-console errors.
- ReplayResult, public replay JSON, fixture, policy, Snapshot, score, ranking,
  transition, GraphDelta, RunRecord, oracle, ontology, blueprint, and privacy
  semantics remain unchanged. No output is written under `runs/`.

### Next exact action

- Review the preselected first answer, all six selector states, the two allowed
  GPT recommendation controls, the compact Goal context, and the connected
  vertical graph locally before authorizing commit and deployed-surface review.

## MV-BUILD-019 — Final release UX composition and GPT reliability pass

| Field | Value |
|---|---|
| Date | 2026-07-20 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/final-ux-chat` |
| Logical thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Milestone | Release composition — context rail, decision workspace, grounded GPT recommendation |
| Status | `STAGED_FOR_LOCAL_HUMAN_REVIEW` |
| Commit | None |
| Push | None |

### Release composition

- Replaced the centered single-column presentation with a responsive 38/62
  composition: Current Goal, verified grounding, and the compact attention map
  occupy the left context rail; the product headline, default **What should
  happen next?** selector, deterministic answer, basis, warning, next action,
  and optional GPT recommendation occupy the right decision workspace.
- Narrow layouts reorder the workspace before the context rail. The full
  inspector is controlled from the decision workspace but renders below both
  columns at page width, preserving The shift, Why it changed, Evidence &
  uncertainty, Technical proof, deterministic replay, GPT Decision Brief, and
  sanitized JSON download.
- Simplified the Current Goal surface so `Product validation` is visually
  primary and remains `Active · Incomplete` with official requirements
  unverified. The other two approved Goals remain secondary public chips.
- Added deterministic answer-level grounding: relevant attention-item count,
  evidence-reference count, all three oracle PASS states, replay verification,
  and relevant confirmation or conditional-displacement counts. Exact evidence
  and receipts remain available in a compact expander.
- Reduced the primary Graphviz story to seven connected concepts with short
  vertical relationships. It preserves the affected Goal, event, top three,
  conditional authorization, no execution, `UNKNOWN`, and one two-item human
  confirmation boundary without exposing raw IDs as primary labels.

### GPT recommendation boundary and verification

- GPT-5.6 remains available only for **What matters now?** and **What should
  happen next?**. Its strict model-authored payload contains only the required
  non-empty strings `what_this_means`, `recommended_next_move`, and
  `approval_or_uncertainty_note`; application code attaches and validates all
  model, answer, intent, replay, evidence, uncertainty, and approval metadata.
- Semantic validation now allows legitimate paraphrase while rejecting rank or
  score restatement, reversed dependency, unsupported entity or evidence IDs,
  completion or compliance claims, known/executed displacement, invented future
  outcomes, and approval bypass. A failed optional call renders only the compact
  public message while retaining a developer-safe diagnostic and the complete
  deterministic next action.
- All **255 tests pass**. The suite covers layout composition, Goal and
  grounding derivation, compact graph semantics, full-width inspector gating,
  strict three-field GPT output, application-controlled metadata, paraphrase
  acceptance, stronger-claim rejection, compact failure presentation, no GPT
  call on load, and no private context.
- Local Playwright review passed at `1440 × 1100` and `390 × 900`: desktop uses
  the intended asymmetric context/workspace composition, mobile puts the
  question and answer first, the graph fits without stray edge labels, and the
  opened inspector spans the page below both columns. Browser console errors
  were zero; the one warning was the renderer's benign worker fallback.
- No deterministic core module, fixture, policy, Goal contract, score, ranking,
  Snapshot, transition, GraphDelta, RunRecord, oracle expectation, replay JSON,
  or core digest changed. No output is written under `runs/`; no live GPT call
  was made.

### Next exact action

- Review the default deterministic recommendation, Goal and grounding rail,
  compact graph, both GPT-eligible questions, one forced GPT failure, narrow
  stacking order, and the full-width inspector before authorizing commit and a
  deployed-surface review.

## MV-BUILD-020 — Final deployed-demo validation and submission readiness

| Field | Value |
|---|---|
| Date | 2026-07-21 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/submission-metadata` |
| Milestone | Submission metadata and code freeze |
| Status | `DOCUMENTATION_READY_FOR_REVIEW` |
| Commit | None |
| Push | None |

### Deployed validation

- The Streamlit application is publicly deployed and passed no-login public
  access, deployed smoke, responsive desktop/narrow review, deterministic
  replay, and both live GPT-5.6 recommendation paths.
- `DEMO_UI: APPROVED`, `PUBLIC_APP_ACCESS: PASS`,
  `DEPLOYED_SMOKE: PASS`, `LIVE_GPT_5_6_RECOMMENDATIONS: PASS`, and
  `RESPONSIVE_REVIEW: PASS`.
- `TESTS: 260 PASS`, `ORACLE_CHECKS: 3/3 PASS`, and `CODE_FREEZE: ACTIVE`.
- ReplayResult digest:
  `sha256:3ae0d566fef04029972e1875f2026e11cd9a60d39208241f030330e6237c6f15`.
- Public replay JSON hash:
  `4c74a94a7fd9258b16129edb8952b306975d0d99e4c1750653f744d2f2837bca`.

### Submission and publication boundaries

- `DEMO_VIDEO: PENDING`, `CODEX_FEEDBACK_SESSION_ID: PENDING`,
  `DEVPOST_SUBMISSION: PENDING`, and `FINAL_COMPLIANCE_REVIEW: PENDING`.
- Public deployment and smoke validation do not authorize any canonical
  artifact or publication surface that remains `PENDING` in the replay or
  privacy contract. No Session ID, video URL, Devpost URL, or compliance
  approval is claimed.
- This milestone changes documentation only. It does not modify application
  behavior, canonical replay output, dependencies, fixtures, policies, schemas,
  tests, or any deterministic core module.

## MV-BUILD-021 — Submission documentation reconciliation

| Field | Value |
|---|---|
| Date | 2026-07-21 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/submission-metadata` |
| Milestone | Final public repository documentation review |
| Status | `READY_FOR_HUMAN_DEVPOST_SUBMISSION` |
| Commit | None |
| Push | None |

### Validated release state

- The validated-test-count presentation hotfix is deployed: the Technical
  proof now reports `260` instead of the stale `197`.
- The complete suite remains `260 PASS`, and all three oracle comparisons
  remain `PASS`.
- ReplayResult digest remained unchanged at
  `sha256:3ae0d566fef04029972e1875f2026e11cd9a60d39208241f030330e6237c6f15`.
- The sanitized public replay JSON was recalculated after the presentation
  hotfix. The prior hash is superseded by
  `18be9783b470b0fb738b2c8be82a76b76d302d88346c22443f19346b3cbaeb37`.
- The public demo video is ready at <https://youtu.be/a7Ri_qCfxc0>.
- The primary `/feedback` Session ID was captured and is provided privately in
  the Devpost submission form. No literal Session ID is stored publicly.
- Repository documentation was reviewed. `DEVPOST_SUBMISSION` remains
  `PENDING`, and `FINAL_COMPLIANCE_REVIEW` remains `PENDING`.

### Change boundary

- This correction changes `README.md` and appends this entry to `BUILD_LOG.md`
  only. No application, deterministic core, schema, fixture, policy,
  dependency, or test file changed.
- Existing surface-specific privacy and publication restrictions remain in
  force. Raw private evidence and unauthorized publication surfaces remain
  prohibited.

## MV-BUILD-022 — OpenAI Build Week submission closure

| Field | Value |
|---|---|
| Date | 2026-07-21 |
| Project | Memoria Viva — Attention Graph for Founders |
| Branch | `build-week/final-submission-close` |
| Milestone | OpenAI Build Week submission closure |
| Status | `SUBMITTED_AND_PUBLISHED` |
| Commit | None |
| Push | None |

### External submission receipts

- The OpenAI Build Week Devpost submission was successfully submitted, and the
  Memoria Viva project is publicly published at
  <https://devpost.com/software/memoria-viva>.
- The submission confirmation email was received. No private email address or
  message identifier is recorded here.
- The public demo remains available at
  <https://memoria-viva-attention-graph-kmhfgbtexurbgcqvhaht8v.streamlit.app/>,
  and the public video is available at <https://youtu.be/a7Ri_qCfxc0>.
- The repository remained public under the MIT License. The primary
  `/feedback` Session ID was provided privately in Devpost and is not recorded
  in public repository files.

### Final deterministic receipts and boundary

- `260` tests remain the final validated count, and all three oracle
  comparisons remain `PASS`.
- ReplayResult digest remained unchanged at
  `sha256:3ae0d566fef04029972e1875f2026e11cd9a60d39208241f030330e6237c6f15`.
- Public replay JSON hash remained unchanged at
  `18be9783b470b0fb738b2c8be82a76b76d302d88346c22443f19346b3cbaeb37`.
- `CODE_FREEZE` became `FINAL`.
- This closure changes `README.md` and appends this entry to `BUILD_LOG.md`
  only. No application, deterministic core, schema, fixture, policy,
  dependency, or test file changed.
- Approved sanitized-surface privacy boundaries remain in force. Submission
  does not authorize raw private evidence or any publication surface outside
  the approved sanitized scope.

## MV-BUILD-023 — Final repository inconsistency remediation and compliance reconciliation

| Field | Value |
|---|---|
| Date | 2026-07-21 |
| Project | Memoria Viva — Attention Graph for Founder Decisions |
| Branch | `build-week/final-repo-reconciliation` |
| Milestone | Final release-integrity remediation and compliance reconciliation |
| Status | `VALIDATED_AND_READY_FOR_COMMIT` |
| Commit | None |
| Push | None |

### Active inconsistency remediation

- Corrected the active replay-proof statement that reported `200` tests. It
  now derives the final count from the existing public DemoViewModel field
  `proof["validated_test_count"]`, rendering `260` without introducing another
  independent constant.
- Updated the regression assertion to require `260 tests`.
- Corrected the devcontainer to Python 3.12 Bookworm, preserved the existing
  Streamlit launch/port behavior, and made all tracked `.json` files strict
  JSON.
- Reconciled `.env.example` with the current optional GPT-5.6 explanation and
  recommendation layer. Deterministic operation remains independent of an API
  key, and no secret was added.

### Compliance reconciliation

- Reconciled all 51 existing requirements and added the three newly indexed
  Official Rules controls: Multiple Submissions, proprietary/third-party
  hardware access, and Financial or Preferential Support.
- Reconciled the submission checklist, clarified the historical/current-state
  boundary in the Rules baseline, appended `MV-RULE-CHANGE-003`, and created
  the final compliance review.
- Final matrix disposition: `20 VERIFIED`, `18 EVIDENCED`, `3 IN_PROGRESS`,
  `4 NOT_APPLICABLE`, and `9 BLOCKED` across 54 requirements.
- Remaining human-only blockers concern eligibility and entrant structure,
  media and third-party rights, original-work ownership/authority, multiple
  submissions, and financial or preferential support. No such fact was
  inferred or exposed.
- Continuing public demo/repository access and post-deadline freeze monitoring
  remain `IN_PROGRESS` through the governing and conservative review windows.

### Validation receipts and change boundary

- The complete suite passes: `Ran 260 tests` and `OK`.
- Ranking-before, ranking-after, and GraphDelta comparisons remain `3/3 PASS`.
- ReplayResult digest remains unchanged at
  `sha256:3ae0d566fef04029972e1875f2026e11cd9a60d39208241f030330e6237c6f15`.
- Public replay JSON hash remains unchanged at
  `18be9783b470b0fb738b2c8be82a76b76d302d88346c22443f19346b3cbaeb37`.
- No secret, literal Session ID, UUID, PII, merge marker, or actual private
  filesystem path was introduced.
- No score, ranking, Snapshot, transition, GraphDelta, RunRecord, replay,
  oracle, schema, fixture, policy, GPT behavior, deployment behavior, or
  dependency changed. Devpost was not modified.

## MV-BUILD-024 — Second repository integrity reconciliation

| Field | Value |
|---|---|
| Date | 2026-07-21 |
| Project | Memoria Viva — Attention Graph for Founder Decisions |
| Branch | `build-week/final-repo-reconciliation-2` |
| Milestone | Second repository integrity and compliance reconciliation |
| Status | `VALIDATED_AND_READY_FOR_COMMIT` |
| Commit | None |
| Push | None |

### Integrity remediation

- Detected that authenticated remote reconstruction of the first reconciliation
  had truncated `BUILD_LOG.md` in the merged repository commit. The validated
  local reconciliation retained the complete append-only history.
- Restored `BUILD_LOG.md` byte-for-byte from the validated local commit before
  appending this next sequential entry. `MV-BUILD-001` through `MV-BUILD-023`
  remain unchanged.
- Compared the complete merged tree with the intended reconciliation tree. The
  other nine files were byte-identical; no second content discrepancy existed.
- Re-audited `README.md`; its current facts, URLs, counts, hashes, submission
  state, license, private Session-ID wording, and privacy boundaries remain
  accurate, so it was intentionally unchanged.
- Updated the final compliance review with the second review identity, current
  official-source recheck, and repository-integrity receipt.

### Current-source and public-surface review

- Rechecked Official Rules, FAQ, Updates, Dates, and the supported-country
  source read-only. No material source change or contradiction with the
  submitted browser project was found.
- Logged-out browser checks loaded the public repository, demo, video, and
  Devpost URLs. The repository page metadata still requires separate owner
  review; its inappropriate description is not repeated in Git.
- Requirements remain `20 VERIFIED`, `18 EVIDENCED`, `3 IN_PROGRESS`,
  `4 NOT_APPLICABLE`, and `9 BLOCKED`. Human-only blockers and continuing
  judge-access obligations remain unchanged.

### Validation receipts and change boundary

- The complete suite passes: `Ran 260 tests` and `OK`.
- Ranking-before, ranking-after, and GraphDelta comparisons remain `3/3 PASS`.
- ReplayResult digest remains unchanged at
  `sha256:3ae0d566fef04029972e1875f2026e11cd9a60d39208241f030330e6237c6f15`.
- Public replay JSON hash remains unchanged at
  `18be9783b470b0fb738b2c8be82a76b76d302d88346c22443f19346b3cbaeb37`.
- Strict tracked JSON parsing remains `32/32 PASS`; all 52 repository-relative
  Markdown links resolve.
- No secret, literal Session ID, UUID, PII, merge marker, or actual private
  filesystem path was introduced.
- No application, deterministic core, schema, fixture, policy, dependency,
  test, score, ranking, GraphDelta, RunRecord, ReplayResult, oracle, GPT, or
  deployment behavior changed. Devpost was not modified.
