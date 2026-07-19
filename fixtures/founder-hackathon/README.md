# Founder Hackathon Fixture

## Fixture record

| Field | Value |
|---|---|
| Fixture ID | `FOUNDER-HACKATHON-PHASE-0C2` |
| Status | `APPROVED_FOR_PRIVATE_REPOSITORY_COMMIT` |
| Temporal boundary | T0 immediately before one trigger; T1 immediately after only that trigger is normalized and evaluated |
| Chronology | Independently synthesized coarse UTC windows with whole-hour boundaries; T0 is `2030-02-10T12:00:00Z` and fixture D-0 is `2030-02-15T18:00:00Z` |
| Residual aggregation risk | `LOW_MEDIUM` |
| Generated runtime outputs | None |

This directory is the public, sanitized input and human-oracle boundary for the
first deterministic Memoria Viva replay. It contains approved semantic inputs,
not a generated Snapshot, computed ranking, executed GraphDelta, RunRecord, or
proof that a Goal, project, submission, or action is complete.

## File map and schema mapping

| File | Role | Canonical validation |
|---|---|---|
| `public-goals.json` | Three approved public Goals plus neutral G5 omission | `schemas/public-goal-set.schema.json` |
| `calendar-t0.json` | Ten sanitized Calendar candidates, T0 selection, exclusions, and Calendar-only attention mappings | Container invariants in this README; each non-null lineage mapping validates against `schemas/common.schema.json#/$defs/lineage_mapping` |
| `evidence.json` | Public-safe evidence summaries and artifact-level provenance | Every item validates against `schemas/evidence.schema.json` |
| `operational-commitments.json` | CMT-01 through CMT-05 with independent lifecycle, mobility, authority, eligibility, repair, execution, and lineage | Every item validates against `schemas/commitment.schema.json` |
| `constraints.json` | Synthetic fixture D-0 anchor and candidate artifact requirements | Every item validates against `schemas/constraint.schema.json` |
| `openai-event.json` | One canonical public-safe trigger | `schemas/source-event.schema.json` |
| `expected-ranking-before.json` | Human-authored T0 ordinal oracle | `schemas/expected-attention-ranking.schema.json` |
| `expected-ranking-after.json` | Human-authored T1 ordinal oracle | `schemas/expected-attention-ranking.schema.json` |
| `expected-graph-delta.json` | Human-authored expected transition semantics | `schemas/graph-delta.schema.json`; all execution fields preserve expected or unknown state |
| `privacy-manifest.json` | Field transformations and publication-surface review state | `schemas/privacy-manifest.schema.json` |

The Calendar, evidence, commitment, and constraint files use thin collection
containers because Phase 0 defines canonical entity schemas rather than
fixture-specific collection schemas. Validation applies the canonical schema to
every contained entity and applies the explicit collection invariants below.

## Replay order

1. Load `public-goals.json`, `evidence.json`, and `calendar-t0.json`.
2. Construct the T0 input boundary from the eight active Calendar candidates,
   the approved CMT-03 through CMT-05 operational objects, and the four
   Calendar-only AttentionItem mappings. CMT-01 and CMT-02 definitions are
   cataloged in `operational-commitments.json` but do not exist in T0.
3. Compare the initial ordinal ordering with
   `expected-ranking-before.json`.
4. Apply only `openai-event.json`. Its synthetic `received_at` anchors the
   transition; `occurred_at` remains unknown and `deadline_at` remains a
   distinct synthetic fixture anchor rather than the official deadline.
5. Activate the trigger-created CMT-01 and CMT-02 definitions and the
   communication-derived constraints. Do not ingest participation confirmation,
   submission-draft-started evidence, or a deadline reminder into T1.
6. Compare the deterministic transition with
   `expected-graph-delta.json` and the resulting ranking with
   `expected-ranking-after.json`.
7. Write any future computed Snapshots, GraphDelta, ranking, or RunRecord only
   to the authorized Phase 1 output boundary; do not overwrite these oracles.

## Controlled semantic invariants

- The public model contains exactly GC-01, GC-02, and GC-03.
- The Build Week effort is a bounded experiment serving GC-01, not a fourth
  Goal.
- G5 is `OMITTED_FROM_CONTROLLED_DEMO` with no operational lifecycle effect.
- T0 contains ten retained Calendar candidates: eight ranking candidates and
  two `EXCLUDED_BUT_RETAINED` candidates, CMT-T0-07 and CMT-T0-08.
- Calendar candidate IDs and operational Commitment IDs are different identity
  domains. Explicit lineage is required; title similarity is never identity
  evidence.
- CMT-05 aggregates two Calendar evidence candidates without duplicating
  attention.
- CMT-01 and CMT-02 enter only after the trigger, remain separate, and preserve
  `BUILD_FIRST`: CMT-01 ranks above CMT-02 and CMT-02 `depends_on` CMT-01.
- CMT-03 remains visible. CMT-04 (`Pending bounded validation`) is the only
  conditional displacement and is never marked executed by this fixture.
  CMT-05 remains confirmation-required under abstract JOINT authority.
- Protected work is never marked displaced. Exclusion is never deletion, and
  Calendar absence never implies available capacity.

## Oracle boundary

The expected rankings and expected GraphDelta are human-authored test oracles.
They contain ordinal expectations, evidence, uncertainty, protection,
conditionality, and approval requirements. They contain no numeric production
score, score component, calculated tie-break result, computed digest, model
output, or execution claim.

Phase 1 deterministic tests may compare computed output with these approved
ordinal invariants. They must not rewrite the human oracle or make a human rank
serve as a production score.

## Time and UNKNOWN policy

All public fixture timestamps use independently synthesized coarse windows on
whole-hour boundaries. Each Calendar interval is synthesized independently;
there is no common offset from the private chronology, and exact private gaps,
minute values, and durations are not retained. Duration classes preserve only
the ordering, crossing-T0, coarse overlap or conflict, and urgency semantics
required by the oracle.

Public D-0 is a synthetic fixture deadline anchor. It is not the official
deadline and cannot be joined to the compliance documents as a shared temporal
anchor. The concrete values are designed to prevent direct recovery of the
private chronology rather than asserting safety for a constant date shift.

`UNKNOWN` and null values are deliberate. In particular, do not infer:

- `occurred_at` from `received_at`;
- capacity from Calendar absence;
- CMT-04 execution, repair slot, or reactivation condition;
- CMT-05 joint-authority outcome;
- production scores or tie-break results;
- follow-up outcomes, submission completion, demo availability, or final
  compliance.

Unknown values must never silently become zero, false, complete, approved,
executed, available, or absent.

## Provenance vocabulary

Only these public-safe evidence categories are used:

- `EVENT_TRIGGER_EMAIL`
- `CALENDAR_T0_PUBLIC_CANDIDATE`
- `GOAL_MODEL_PUBLIC_COMPRESSION`
- `FOUNDER_GOAL_APPROVAL`
- `FOUNDER_COMMITMENT_APPROVAL`
- `HUMAN_EXPECTATION`

Follow-up categories remain permitted by the ontology but are not instantiated
in this T1 fixture. Evidence records contain short synthetic summaries and
stable repository-safe references only. No raw text, external ID, source URL,
filesystem path, account link, private filename, or reversible provenance is
included.

Communication evidence has `COMMUNICATION_EVIDENCE_ONLY` authority. It cannot
establish official rules, entrant eligibility, submission completion, Goal
completion, or compliance. Official hackathon sources remain controlling.

## Privacy transformations and publication

The package applies `REMOVE`, `GENERALIZE`, `PSEUDONYMIZE`, `SYNTHESIZE`, and
explicitly safe `KEEP` transformations. Public timestamps use
`INDEPENDENT_SYNTHETIC_COARSE_TIME`; the rejected constant-offset `SHIFT_DATE`
method is not used. Private names, emails, phone numbers, locations, external
IDs, sensitive transaction details, accounts, raw metadata, and private
narrative context are prohibited.

The founder approved the exact concrete fixture package for commit to the
current private repository. This authorization is not public release.
Publication approval is tracked separately for `PUBLIC_FIXTURE`,
`REPOSITORY_DOCS`, `DEMO_UI`, `DEMO_VIDEO`, and `DEVPOST_SUBMISSION`; approval
for one surface never implies approval for another. All five publication
surfaces remain `PENDING`; staging or committing the fixture in the current
private repository is not public-surface approval.

Artifact or file existence is not completion. Separate human approval for a
specific public surface is required before that publication status may advance.
