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
