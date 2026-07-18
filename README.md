# Memoria Viva — Attention Graph

A temporal layer of memory, attention, and execution for founders.

Memoria Viva transforms verifiable events into explainable state changes,
attention rankings, Goal progress, and auditable decisions.

Built during OpenAI Build Week 2026.

## Current phase

Phase 0 establishes contracts only. There is no executable transition,
application, integration, or demo runtime yet.

The first planned replay is:

```text
calendar-t0.json + openai-event.json
-> snapshot-t1.json
-> graph-delta.json
-> attention-ranking-before.json
-> attention-ranking-after.json
-> run-record.json
```

## Canonical sources

1. [Construction blueprint](docs/CONSTRUCTION_BLUEPRINT.md)
2. [Phase 0 ontology](docs/ontology.md)
3. [Machine-readable schemas](schemas/)
4. Deterministic code and invariants, when implemented
5. The current milestone instruction

The active scoring contract is
[attention-policy.v1.json](config/attention-policy.v1.json). Privacy boundaries
are defined in [docs/privacy.md](docs/privacy.md).

## Build Week records

- [Baseline](BUILD_WEEK_BASELINE.md)
- [Decision ledger](DECISIONS.md)
- [Build log](BUILD_LOG.md)
- [Hackathon evidence scaffold](docs/hackathon/RULES_BASELINE.md)

Official hackathon sources have been captured as evidence in the
[hackathon rules baseline](docs/hackathon/RULES_BASELINE.md) and mapped in the
[requirements matrix](docs/hackathon/REQUIREMENTS_MATRIX.md). Compliance remains
unverified until the required implementation, submission artifacts, final
source recheck, and human review are complete; see the
[build log](BUILD_LOG.md) for the latest recorded construction status.
