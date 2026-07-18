# Hackathon Rule Changelog

## Contract

This append-only log records changes to rule evidence. It does not contain
rule content independently of `RULES_BASELINE.md`.

| Field | Meaning |
|---|---|
| `change_id` | Stable change identifier |
| `observed_at` | When the change was detected |
| `authority` | Authority value from the baseline hierarchy |
| `new_rule_id` | Current rule record |
| `superseded_rule_id` | Previous rule record, or `null` |
| `change_type` | `ADDED`, `CHANGED`, `REMOVED`, or `CLARIFIED` |
| `evidence_ref` | Source supporting the change |
| `impact` | Requirements or artifacts affected |
| `status` | `UNVERIFIED`, `EVIDENCED`, or `VERIFIED` |

## Entries

No entries exist yet.
