# Submission Checklist

This is an operational control derived from the official evidence in
`RULES_BASELINE.md` and the controls in `REQUIREMENTS_MATRIX.md`. It does not
replace the Official Rules.

## Deadline controls

- **Official deadline:** Tuesday, 2026-07-21 17:00 PDT
  (`America/Los_Angeles`, `UTC-07:00`).
- **Internal submission target:** Tuesday, 2026-07-21 14:00 PDT
  (`America/Los_Angeles`, `UTC-07:00`), exactly three hours before the official
  deadline.
- The internal target is an **internal operational control, not an official
  rule**.
- **Conservative availability control:** keep demo, repository access, sample
  data, and judge test path available through at least `2026-08-12 23:59 PDT`
  (`America/Los_Angeles`). This is internal and does not extend the Official
  Rules judging period ending `2026-08-05 17:00 PDT`.
- A checked final-verification box requires human review. Automation and source
  capture alone cannot check it.

## 1. Eligibility

| Requirement ID | Action | Evidence location | Current status | Owner | Due time | Final verification |
|---|---|---|---|---|---|---|
| `REQ-ELIG-001` | Confirm entrant type, age/guardian condition if relevant, and eligibility. | Private human attestation; Devpost entrant record | `NOT_STARTED` | Entrant / representative | `2026-07-21 14:00 PDT` internal target | [ ] |
| `REQ-ELIG-002` | Recheck the dynamic OpenAI supported-country source, then obtain human confirmation of country of legal residence, age-of-majority eligibility, and absence of applicable exclusions. Do not infer these facts from technical signals. | `HUMAN_ELIGIBILITY_ATTESTATION_REQUIRED`; no private address in Git | `NOT_STARTED` | Entrant / representative | `2026-07-21 14:00 PDT` internal target | [ ] |
| `REQ-ELIG-003` | If entering as a team/organization, appoint the eligible representative and confirm invitations are accepted. | Devpost team and representative evidence | `NOT_STARTED` | Entrant / representative | `2026-07-21 14:00 PDT` internal target | [ ] |
| `REQ-ELIG-004` | Review every relevant exclusion in Official Rules section 3. | Private eligibility attestation | `NOT_STARTED` | Entrant / representative | `2026-07-21 14:00 PDT` internal target | [ ] |

## 2. Product functionality

| Requirement ID | Action | Evidence location | Current status | Owner | Due time | Final verification |
|---|---|---|---|---|---|---|
| `REQ-PROJ-003` | Confirm the product and submission fit Work & Productivity and select only that track. | README, demo narrative, Devpost track field | `NOT_STARTED` | Product / submission owner | `2026-07-21 14:00 PDT` internal target | [ ] |
| `REQ-PROJ-004` | Run the complete install/start/test path and prove consistent behavior. | README test instructions, test logs, release evidence | `NOT_STARTED` | Primary engineering thread | `2026-07-21 12:00 PDT` internal control | [ ] |
| `REQ-PROJ-005` | Identify the post-2026-07-13 qualifying implementation delta. | Commit history, build log, baseline comparison | `NOT_STARTED` | Primary engineering thread | `2026-07-21 12:00 PDT` internal control | [ ] |
| `REQ-JUDGE-001` | Perform a Stage One readiness review for viability, theme fit, and required-tool use. | Review record linked from README or build log | `NOT_STARTED` | Product + engineering owners | `2026-07-21 12:30 PDT` internal control | [ ] |

## 3. Codex evidence

| Requirement ID | Action | Evidence location | Current status | Owner | Due time | Final verification |
|---|---|---|---|---|---|---|
| `REQ-PROJ-001` | Preserve evidence of meaningful Codex contribution to core construction. | Primary Codex thread, dated commits, `BUILD_LOG.md`, README | `NOT_STARTED` | Primary engineering thread | `2026-07-21 12:00 PDT` internal control | [ ] |
| `REQ-PROJ-006` | Distinguish pre-existing concept/work from new Build Week implementation. | `BUILD_WEEK_BASELINE.md`, commit history, README disclosure | `NOT_STARTED` | Primary engineering thread | `2026-07-21 12:00 PDT` internal control | [ ] |
| `REQ-SUB-005` | Add concrete Codex workflow and decision evidence to README and video. | README Codex section; video timestamps | `NOT_STARTED` | Primary engineering thread + video owner | `2026-07-21 13:00 PDT` internal control | [ ] |
| `REQ-SUB-012` | Run `/feedback` in the representative primary thread and copy the Session ID to Devpost. | Devpost Session ID field; private submission evidence record | `NOT_STARTED` | Primary engineering thread | `2026-07-21 13:30 PDT` internal control | [ ] |

## 4. GPT-5.6 evidence

| Requirement ID | Action | Evidence location | Current status | Owner | Due time | Final verification |
|---|---|---|---|---|---|---|
| `REQ-PROJ-002` | Implement and identify a substantive GPT-5.6-backed capability. | Code/config, runtime evidence, README | `NOT_STARTED` | Primary engineering thread | `2026-07-21 12:00 PDT` internal control | [ ] |
| `REQ-SUB-006` | Explain exactly what GPT-5.6 does and show the result in the demo. | README GPT-5.6 section; video timestamps; Devpost description | `NOT_STARTED` | Primary engineering thread + video owner | `2026-07-21 13:00 PDT` internal control | [ ] |

## 5. Repository and README

| Requirement ID | Action | Evidence location | Current status | Owner | Due time | Final verification |
|---|---|---|---|---|---|---|
| `REQ-SUB-008` | Confirm the judge-facing repository URL points to the final runnable project. | Devpost repository field; logged-out access check | `NOT_STARTED` | Repository owner | `2026-07-21 13:00 PDT` internal control | [ ] |
| `REQ-SUB-009` | If public, select and attach relevant licensing. | Repository license file and visibility evidence | `NOT_STARTED` | Repository owner + licensing reviewer | `2026-07-21 13:00 PDT` internal control | [ ] |
| `REQ-SUB-010` | If private, grant both required judging addresses access. | Private collaborator/access confirmation | `NOT_STARTED` | Repository owner | `2026-07-21 13:00 PDT` internal control | [ ] |
| `REQ-SUB-011` | Complete README setup, sample-data-if-needed, testing, Codex, decisions, and GPT-5.6 sections. | `README.md` | `NOT_STARTED` | Primary engineering thread | `2026-07-21 12:30 PDT` internal control | [ ] |
| `REQ-SUB-013` | Rehearse README instructions from a clean judge perspective. | Test log and README cross-check | `NOT_STARTED` | Primary engineering thread | `2026-07-21 13:00 PDT` internal control | [ ] |

## 6. Demo access

| Requirement ID | Action | Evidence location | Current status | Owner | Due time | Final verification |
|---|---|---|---|---|---|---|
| `REQ-SUB-014` | Provide a working public demo, test build, or secure test account and verify access outside the owner session. | Devpost testing instructions; logged-out test record | `NOT_STARTED` | Demo owner | `2026-07-21 13:00 PDT` internal control | [ ] |
| `REQ-SUB-015` | Ensure demo, repository access, sample data, and judge test path remain free and usable through the Rules-defined judging end; conservatively maintain them through the end of August 12. | Access plan and monitoring record | `NOT_STARTED` | Demo owner | **Official Rules:** `2026-08-05 17:00 PDT`; **internal control:** at least `2026-08-12 23:59 PDT` | [ ] |
| `REQ-JUDGE-008` | Ask a reviewer unfamiliar with the project to evaluate only the description, images, and video. | Media-only review record | `NOT_STARTED` | Video + submission owners | `2026-07-21 13:15 PDT` internal control | [ ] |

## 7. Video

| Requirement ID | Action | Evidence location | Current status | Owner | Due time | Final verification |
|---|---|---|---|---|---|---|
| `REQ-SUB-002` | Export the final video strictly below `00:03:00` and record its measured duration. | Final media metadata and review record | `NOT_STARTED` | Video owner | `2026-07-21 12:30 PDT` internal control | [ ] |
| `REQ-SUB-003` | Upload to YouTube as Public and verify the link while logged out. | YouTube URL, visibility evidence, incognito check | `NOT_STARTED` | Video owner | `2026-07-21 13:00 PDT` internal control | [ ] |
| `REQ-SUB-004` | Confirm the video audibly narrates a clear working-project demo. | Final playback review and video timestamps | `NOT_STARTED` | Video owner | `2026-07-21 13:00 PDT` internal control | [ ] |
| `REQ-SUB-005` | Confirm narration explains concrete Codex workflow and decisions. | Script and final video timestamps | `NOT_STARTED` | Video owner + primary engineering thread | `2026-07-21 13:00 PDT` internal control | [ ] |
| `REQ-SUB-006` | Confirm narration explains the integrated GPT-5.6 capability. | Script and final video timestamps | `NOT_STARTED` | Video owner + primary engineering thread | `2026-07-21 13:00 PDT` internal control | [ ] |
| `REQ-SUB-007` | Remove or license protected music, marks, and third-party media. | Final asset/rights inventory | `NOT_STARTED` | Video owner + licensing reviewer | `2026-07-21 12:30 PDT` internal control | [ ] |

## 8. Devpost form

| Requirement ID | Action | Evidence location | Current status | Owner | Due time | Final verification |
|---|---|---|---|---|---|---|
| `REQ-SUB-001` | Enter an accurate English project description matching the product and video. | Devpost description field and final screenshot | `NOT_STARTED` | Submission owner | `2026-07-21 13:00 PDT` internal control | [ ] |
| `REQ-PROJ-003` | Select Work & Productivity. | Devpost track field | `NOT_STARTED` | Submission owner | `2026-07-21 13:00 PDT` internal control | [ ] |
| `REQ-SUB-008` | Enter and test the repository URL. | Devpost repository field | `NOT_STARTED` | Submission owner | `2026-07-21 13:00 PDT` internal control | [ ] |
| `REQ-SUB-003` | Enter and test the public YouTube URL. | Devpost video field | `NOT_STARTED` | Submission owner | `2026-07-21 13:00 PDT` internal control | [ ] |
| `REQ-SUB-012` | Enter the primary `/feedback` Session ID. | Devpost Session ID field | `NOT_STARTED` | Submission owner | `2026-07-21 13:30 PDT` internal control | [ ] |
| `REQ-SUB-014` | Enter test path and securely provide any required private credentials. | Devpost testing instructions | `NOT_STARTED` | Submission owner + demo owner | `2026-07-21 13:30 PDT` internal control | [ ] |

## 9. Licensing and privacy

| Requirement ID | Action | Evidence location | Current status | Owner | Due time | Final verification |
|---|---|---|---|---|---|---|
| `REQ-PROJ-007` | Verify authorization for every SDK, API, and dataset. | Dependency/data authorization inventory | `NOT_STARTED` | Engineering + licensing reviewer | `2026-07-21 12:00 PDT` internal control | [ ] |
| `REQ-RIGHTS-001` | Confirm original work, ownership, contributor rights, and authority to submit. | Private attestation and repository provenance | `NOT_STARTED` | Entrant + licensing reviewer | `2026-07-21 12:30 PDT` internal control | [ ] |
| `REQ-RIGHTS-002` | Verify open-source licenses and document meaningful extensions. | License inventory, attributions, baseline/delta | `NOT_STARTED` | Engineering + licensing reviewer | `2026-07-21 12:30 PDT` internal control | [ ] |
| `REQ-RIGHTS-003` | Review third-party code, data, media, trademarks, privacy, and publicity rights. | Rights/permissions inventory | `NOT_STARTED` | Licensing + privacy reviewers | `2026-07-21 12:30 PDT` internal control | [ ] |
| `REQ-PRIV-001` | Run secret/PII review across staged repository, demo, video, sample data, and Devpost fields. | Scan results plus human privacy approval | `NOT_STARTED` | Privacy reviewer | `2026-07-21 13:15 PDT` internal control | [ ] |
| `REQ-SEC-001` | Run security and dependency checks; confirm no harmful code. | Security review record | `NOT_STARTED` | Engineering + security reviewer | `2026-07-21 13:15 PDT` internal control | [ ] |

## 10. Final pre-submission verification

| Requirement ID | Action | Evidence location | Current status | Owner | Due time | Final verification |
|---|---|---|---|---|---|---|
| `REQ-SUB-016` | Confirm every submitted material is English or has a complete English translation. | Final language review | `NOT_STARTED` | Submission owner | `2026-07-21 13:15 PDT` internal control | [ ] |
| `REQ-PLUGIN-002`, `REQ-PLUGIN-003` | Recheck Rules, FAQ, and Updates directly; do not rely on plugin output. | `RULE_CHANGELOG.md` recheck entry | `NOT_STARTED` | Compliance owner + human reviewer | `2026-07-21 13:00 PDT` internal control | [ ] |
| `REQ-JUDGE-006` | Verify balanced evidence for all four equally weighted judging criteria. | Final evidence-coverage review | `NOT_STARTED` | Submission owner | `2026-07-21 13:15 PDT` internal control | [ ] |
| `REQ-SUB-018` | Freeze final commit, media, and submission evidence with hashes before deadline. | Final release/submission evidence record | `NOT_STARTED` | Submission owner | `2026-07-21 13:30 PDT` internal control | [ ] |
| `REQ-SUB-017` | Confirm Devpost shows the entry in final Submitted state, not draft. | Timestamped confirmation page/screenshot | `NOT_STARTED` | Entrant / representative | **`2026-07-21 14:00 PDT` internal target** | [ ] |
| `REQ-DATE-003` | Retain three-hour safety margin; escalate any unresolved blocker before the internal target. | Final readiness record | `NOT_STARTED` | Submission owner | **`2026-07-21 14:00 PDT` internal target** | [ ] |

The official submission deadline remains `2026-07-21 17:00 PDT`; nothing in
this checklist changes that official rule.
