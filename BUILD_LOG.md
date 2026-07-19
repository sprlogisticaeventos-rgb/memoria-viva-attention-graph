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
