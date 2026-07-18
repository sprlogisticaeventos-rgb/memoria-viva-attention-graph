# Repository Instructions

## Purpose

Memoria Viva converts verifiable events into versioned state changes,
explainable attention rankings, and auditable execution records.

## Canonical source hierarchy

1. `docs/CONSTRUCTION_BLUEPRINT.md`
2. `docs/ontology.md`
3. `schemas/*`
4. Deterministic code and invariants
5. The current milestone instruction

Read the blueprint before changing a canonical contract. Use
`config/attention-policy.v1.json` for scoring policy and `docs/privacy.md` for
data boundaries. Reference these sources; do not duplicate their ontology or
policy definitions.

## Repository map

- `docs/`: semantic, privacy, and evidence contracts
- `schemas/`: canonical machine-readable contracts
- `config/`: versioned policy instances
- `fixtures/`: ignored private inputs and sanitized public fixtures
- `runs/`: ignored generated run outputs

## Privacy and epistemic rules

Never read, stage, or expose `.env.local`, `fixtures/private/**`, or local run
content. Keep facts separate from inference. Preserve provenance and use only
the epistemic states defined in `docs/ontology.md`. Never silently overwrite
historical state.

## Phase 0 Definition of Done

Phase 0 is complete when canonical documents, schemas, policy, fixture
boundaries, and compliance scaffolds are internally consistent and validated.
It does not include executable application behavior.

## Git safety

Work on a dedicated branch. Stage explicit approved paths only. Do not commit
secrets, private data, or generated local runs. Do not commit or push without
the requested review gate.

Canonical files must not be edited concurrently. Sequence changes to the
blueprint, ontology, schemas, policy, privacy contract, and decision ledger
through one owner and reconcile each change before the next begins.
