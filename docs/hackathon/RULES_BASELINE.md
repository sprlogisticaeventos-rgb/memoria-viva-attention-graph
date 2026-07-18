# Hackathon Rules Baseline

## Status

`NOT_STARTED` — no official hackathon source was fetched or recorded in
Phase 0B. This file defines the evidence structure only.

## Authority hierarchy

| Priority | Authority value | Meaning |
|---:|---|---|
| 1 | `official_rules` | Published Official Rules |
| 2 | `official_faq` | Published official FAQ |
| 3 | `official_update` | Published official update or announcement |
| 4 | `written_clarification` | Direct written clarification from OpenAI or Devpost |
| 5 | `internal_interpretation` | Internal reading that has no external authority |

Higher-priority evidence overrides lower-priority interpretation. Conflicts are
recorded; previous records are superseded, not deleted.

## Future rule record contract

Every future record must support:

| Field | Contract |
|---|---|
| `rule_id` | Stable local identifier |
| `authority` | One value from the hierarchy above |
| `source_url` | Exact source URL, or `null` only for internal interpretation |
| `source_excerpt` | Minimal relevant excerpt; never an unsupported paraphrase |
| `observed_at` | When the source was accessed |
| `verified_at` | When a second verification occurred, or `null` |
| `status` | `CURRENT`, `SUPERSEDED`, `DISPUTED`, or `UNVERIFIED` |
| `supersedes` | Prior `rule_id`, or `null` |
| `notes` | Bounded interpretation, uncertainty, and follow-up |

## Rule records

No rule records exist yet.
