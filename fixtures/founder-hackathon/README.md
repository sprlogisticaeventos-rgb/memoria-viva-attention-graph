# Founder Hackathon Fixture

## Fixture record

| Field | Value |
|---|---|
| Fixture ID | `founder_hackathon_v1` |
| Status | `scaffold_only` |
| Intended replay | OpenAI event changes founder attention |
| Public approval | `NOT_APPROVED` |

This directory is the future public, sanitized replay boundary. It currently
contains only the Goal Contract and privacy manifest. It does not contain
Calendar data, an OpenAI event, expected outputs, personal data, or executable
test material.

## Planned inputs

- `calendar-t0.json` — not created in Phase 0
- `openai-event.json` — not created in Phase 0

## Planned expected outputs

Future sanitized golden outputs will live under `expected/`, separate from
ignored local `runs/` data.

## Publication rule

No file becomes public-ready because it exists in this directory. The privacy
manifest must record PII review and explicit human approval before publication.
