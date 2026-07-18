# Hackathon Rule Changelog

This append-only log records source captures and later rule changes. Canonical
rule records live in `RULES_BASELINE.md`; this file never replaces them.

## Entry contract

| Field | Meaning |
|---|---|
| `change_id` | Stable change identifier |
| `capture_timestamp` | UTC source-capture time |
| `source_urls` | Official sources checked |
| `source_access` | Whether each source was accessible |
| `authority` | Highest authority applicable to the entry |
| `new_rule_ids` | Added or current rule records |
| `amended_rule_ids` | Existing records clarified by the capture, or `null` |
| `superseded_rule_ids` | Prior local records, or `null` |
| `change_type` | `ADDED`, `CHANGED`, `REMOVED`, or `CLARIFIED` |
| `material_inconsistencies` | Conflicting or corrected official material |
| `unresolved_ambiguities` | Questions that still require clarification or human judgment |
| `impact` | Requirements or artifacts affected |
| `status` | `UNVERIFIED`, `EVIDENCED`, or `VERIFIED` |
| `next_scheduled_recheck` | Internal recheck time; never a guarantee against future changes |

## Entries

### MV-RULE-CHANGE-001 — First sourced compliance capture

| Field | Value |
|---|---|
| `change_id` | `MV-RULE-CHANGE-001` |
| `capture_timestamp` | `2026-07-18T18:39:47Z` |
| `source_urls` | https://openai.devpost.com/rules; https://openai.devpost.com/details/faqs; https://openai.devpost.com/updates |
| `source_access` | Official Rules: accessible; Official FAQ: accessible; Official Updates: accessible |
| `authority` | `official_rules` |
| `new_rule_ids` | `BW-RULE-001` through `BW-RULE-054`; `BW-FAQ-001` through `BW-FAQ-003`; `BW-UPDATE-001` through `BW-UPDATE-002` |
| `superseded_rule_ids` | `null` — no earlier sourced local records existed |
| `change_type` | `ADDED` and `CLARIFIED` |
| `impact` | Established the compliance baseline, matrix, and operational checklist; no product contract or implementation changed |
| `status` | `EVIDENCED` — source capture only; no compliance requirement is verified |
| `next_scheduled_recheck` | `2026-07-20T16:00:00Z` (`2026-07-20 09:00 PDT`, `America/Los_Angeles`) |

#### Observed material inconsistencies

1. The current Official Update says a previous update named Monday as the
   deadline and explicitly corrects it to Tuesday, 2026-07-21 at 17:00 PT.
   Official Rules and FAQ agree with Tuesday. `BW-RULE-003` is controlling;
   `BW-UPDATE-001` preserves the correction.
2. Official Rules say the video should be **less than** three minutes, while
   FAQ says three minutes or under. The internal control follows the stricter
   Rules wording: final duration must be below `00:03:00`.
3. Official Rules require a publicly visible YouTube video and FAQ says public
   video, while the current Official Update says Unlisted is acceptable. The
   internal control uses YouTube Public visibility unless a higher-authority
   written clarification resolves the difference.
4. FAQ says a submitted entry can still be edited, while Official Rules bar
   entrant changes after the Submission Period. These are reconciled as edits
   allowed only before the official deadline; Rules control afterward.

#### Unresolved ambiguities

- The entrant's eligibility and current supported-territory status are not
  verified. The Rules link to a separate territory list, but Phase 0C1 allowed
  only the three named official source pages, so that linked page was not used.
- “Meaningful” Codex and GPT-5.6 use is qualitative; the official sources give
  evidence surfaces but no numeric threshold.
- Official sources do not identify a specific “relevant” license for a public
  repository.
- The Public-versus-Unlisted YouTube wording differs across official sources;
  the stricter Public control is conservative, not a new official rule.
- The Rules require completing and entering all required fields but do not
  name the exact Devpost UI label for the final state. `Submitted` is the
  internal operational control.
- Actual entrant, ownership, privacy, licensing, and submission-form facts
  require human review and remain unverified.

#### Recheck policy

The scheduled recheck does not imply that no rule can change earlier or later.
Recheck all three official sources again before the internal submission target
and append any additions, corrections, or supersessions; never rewrite this
entry.

### MV-RULE-CHANGE-002 — Eligibility source and schedule conflict amendment

| Field | Value |
|---|---|
| `change_id` | `MV-RULE-CHANGE-002` |
| `capture_timestamp` | `2026-07-18T19:01:58Z` |
| `source_urls` | https://openai.devpost.com/details/dates; https://developers.openai.com/api/docs/supported-countries |
| `source_access` | Official Devpost Schedule: accessible; OpenAI `Supported countries and territories`: accessible through the Official Rules link |
| `authority` | `official_rules` remains controlling; supplemental sources are `official_schedule` and `official_openai_documentation` |
| `new_rule_ids` | `BW-RULE-055`; `BW-RULE-056` |
| `amended_rule_ids` | `BW-RULE-004`; `BW-RULE-007`; `BW-RULE-032` |
| `superseded_rule_ids` | `null` |
| `change_type` | `ADDED` and `CLARIFIED` |
| `impact` | Added a privacy-preserving eligibility attestation control and a conservative judge-access window; no product, fixture, schema, ontology, policy, or privacy architecture changed |
| `status` | Country source `EVIDENCED`; schedule conflict `DISPUTED`; all compliance requirements remain `NOT_STARTED` |
| `next_scheduled_recheck` | `2026-07-20T16:00:00Z` (`2026-07-20 09:00 PDT`, `America/Los_Angeles`), plus a final source recheck before submission |

#### Observed material inconsistency

- Official Rules define judging as `2026-07-22 10:00 PDT` through
  `2026-08-05 17:00 PDT`.
- Official Schedule defines judging as `2026-07-22 09:00 PDT` through
  `2026-08-09 17:00 PDT`.
- Official Rules remain controlling. The one-hour start difference and four-day
  end difference remain explicit and are not silently reconciled.
- The conservative availability control keeps the demo, repository access,
  sample data, and judge test path available through at least the end of
  `2026-08-12` in `America/Los_Angeles`. This is an internal control, not an
  official extension of the judging period.

#### Eligibility evidence state

- The current OpenAI source title is `Supported countries and territories`.
- The list is dynamic; only its source and eligibility meaning were captured.
  The complete list was not copied into the repository.
- Eligibility remains `HUMAN_ELIGIBILITY_ATTESTATION_REQUIRED` and
  `NOT_STARTED` until the user confirms country of legal residence,
  age-of-majority eligibility, and absence of applicable exclusions.
- No residence, age, or private address was inferred or recorded from IP,
  machine settings, timezone, Git identity, or another technical signal.
- Recheck the OpenAI source immediately before final submission.
