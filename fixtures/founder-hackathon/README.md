# Founder Hackathon Fixture

## Fixture record

| Field | Value |
|---|---|
| Fixture ID | `founder_hackathon_v1` |
| Status | `scaffold_only` |
| Intended replay | OpenAI event changes founder attention |
| Public approval | `NOT_APPROVED` |

This directory is the future public, sanitized replay boundary. It currently
contains only a superseded Goal scaffold and privacy manifest scaffold. It does
not contain Calendar data, an OpenAI event, expected outputs, personal data, or
executable test material.

`goal-hackathon.json` is a superseded Phase 0 scaffold and remains untouched in
Phase 0D2. A separately authorized Phase 0C2 migration will preserve Git history
while renaming it to `public-goals.json` and replacing it with the approved
three-Goal controlled model.

## Phase 0C2 contract

The future approved fixture must:

- define `T0` immediately before one canonical normalized trigger and `T1`
  immediately after applying only that trigger;
- retain follow-up communications as related evidence while excluding them
  from the `T1` transition;
- use relative time or one consistent date shift and keep `received_at`,
  `occurred_at`, and `deadline_at` semantically distinct;
- contain exactly the three approved public Goals and represent `G5` neutrally
  as `OMITTED_FROM_CONTROLLED_DEMO`, separate from operational lifecycle;
- keep active Calendar candidates separate from excluded-but-retained
  candidates, with explicit exclusion reasons rather than deletion;
- keep Calendar candidate identity separate from operational commitment
  identity and connect them only through approved, evidence-backed lineage;
- preserve `UNKNOWN` values, uncertainty, conditionality, mobility,
  eligibility, authority, and execution state without collapsing them;
- express the human-authored expectation through the ordinal oracle schema,
  with no fabricated numeric production scores;
- represent all approved GraphDelta categories where the fixture oracle calls
  for them: `ADDED`, `UPDATED`, `CONFLICTED`, `DISPLACED`, `PROTECTED`,
  `REQUIRES_CONFIRMATION`, and `UNCHANGED`;
- prevent communication evidence from claiming official-rule authority;
- never treat artifact existence as Goal completion;
- contain no raw locator, reversible provenance, secret, or private identifier;
  and
- record fixture-level privacy review and publication approval per surface.

## Planned inputs

- `calendar-t0.json` — not created in Phase 0
- `openai-event.json` — not created in Phase 0

## Planned expected outputs

Phase 0C2 may create only the separately authorized human oracle fixtures.
Generated snapshots, GraphDelta, RunRecord, and computed rankings remain Phase
1 outputs under the appropriate ignored or versioned-output boundary.

## Publication rule

No file becomes public-ready because it exists in this directory. The privacy
manifest must record PII review and explicit human approval before publication.
