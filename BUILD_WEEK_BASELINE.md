# Build Week Baseline

## Record

| Field | Value |
|---|---|
| Record ID | `mv_build_week_baseline_2026` |
| Project | Memoria Viva — Attention Graph for Founders |
| Event | OpenAI Build Week 2026 |
| Track | Work & Productivity |
| Repository | `sprlogisticaeventos-rgb/memoria-viva-attention-graph` |
| Primary thread | `BUILD WEEK — MEMORIA VIVA PRIMARY CORE` |
| Phase | Phase 0 — Contracts |
| Baseline date | 2026-07-18 |
| Evidence status | `NOT_STARTED` for hackathon compliance |

## Provenance boundary

Memoria Viva and the Attention Graph concept predated this repository. The
executable implementation, schemas, tests, UI, and runtime are being built
during OpenAI Build Week 2026.

No pre-existing executable code may be imported into this repository without
explicit disclosure of its source, license, original creation time, and the
specific changes made during Build Week.

## Authority

Official hackathon Rules override the official FAQ, which overrides official
Updates, which override written clarification from OpenAI or Devpost, which
override internal interpretation. Local records are evidence indexes; they do
not replace their official sources.

## Phase 0 contract

Phase 0 creates contracts only: canonical documentation, machine-readable
schemas, the versioned attention policy, fixture/privacy boundaries, and an
empty compliance evidence scaffold.

Phase 0 does not implement the replay transition, application code, UI, API
calls, integrations, databases, agents, Skills, caching, reasoning continuity,
Programmatic Tool Calling, notifications, or autonomous actions.

## Planned transition

```text
calendar-t0.json + openai-event.json
-> snapshot-t1.json
-> graph-delta.json
-> attention-ranking-before.json
-> attention-ranking-after.json
-> run-record.json
```

The inputs and outputs above are not created in Phase 0 except for the
sanitized Goal Contract and the contracts that will validate future artifacts.

## Open dependencies and questions

- Official hackathon sources have not been captured.
- Public sample inputs have not been created or approved.
- Scoring component normalization accepts bounded inputs in Phase 0; the
  source-specific normalization rules remain a Phase 1 decision.
- Score thresholds are intentionally unset until a human product decision is
  recorded.
