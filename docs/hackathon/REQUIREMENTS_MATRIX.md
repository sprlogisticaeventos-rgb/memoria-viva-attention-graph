# Hackathon Requirements Matrix

Official-source capture and historical rule observations are preserved in
[RULES_BASELINE.md](RULES_BASELINE.md). This matrix records final
implementation and submission evidence for **Memoria Viva — Attention Graph
for Founder Decisions**.

`VERIFIED` means objective evidence was checked against the corresponding
official requirement. `EVIDENCED` means the project supplies relevant evidence,
but the final conclusion belongs to a judge, host, or human authority.
`IN_PROGRESS` identifies an operational obligation that continues during
judging. `NOT_APPLICABLE` identifies a conditional requirement that does not
apply. `BLOCKED` identifies a missing essential human fact or attestation.

Allowed statuses: `NOT_STARTED`, `IN_PROGRESS`, `EVIDENCED`, `VERIFIED`,
`NOT_APPLICABLE`, `BLOCKED`.

Review timestamp: `2026-07-21T22:16:34Z`.

## Final evidence index

- Repository: [public GitHub repository](https://github.com/sprlogisticaeventos-rgb/memoria-viva-attention-graph), [MIT License](../../LICENSE)
- Demo: [public no-login Streamlit app](https://memoria-viva-attention-graph-kmhfgbtexurbgcqvhaht8v.streamlit.app/)
- Video: [public YouTube demo](https://youtu.be/a7Ri_qCfxc0)
- Submission: [published Devpost project](https://devpost.com/software/memoria-viva)
- Implementation: [README](../../README.md), [Build Week baseline](../../BUILD_WEEK_BASELINE.md), [append-only build log](../../BUILD_LOG.md), and dated [commit history](https://github.com/sprlogisticaeventos-rgb/memoria-viva-attention-graph/commits/main/)
- Validation: `260 PASS`; ranking-before, ranking-after, and GraphDelta `3/3 PASS`
- ReplayResult: `sha256:3ae0d566fef04029972e1875f2026e11cd9a60d39208241f030330e6237c6f15`
- Public replay JSON: `18be9783b470b0fb738b2c8be82a76b76d302d88346c22443f19346b3cbaeb37`
- Primary Codex Session ID: captured and provided privately in Devpost; the
  literal value is intentionally absent from Git.

## Dates

| Requirement ID | Rule source | Authoritative requirement | Final evidence | Status | Verified at | Blocker / notes |
|---|---|---|---|---|---|---|
| `REQ-DATE-001` | `BW-RULE-001` | Register during the official Registration Period. | Accepted [Devpost submission](https://devpost.com/software/memoria-viva) and pre-deadline closure in [BUILD_LOG.md](../../BUILD_LOG.md). | `VERIFIED` | `2026-07-21T22:16:34Z` | Accepted submission establishes completed registration before the deadline. |
| `REQ-DATE-002` | `BW-RULE-002` | Submit during the official Submission Period. | Dated commits, `SUBMITTED`, `PUBLISHED`, and `RECEIVED` receipts in [README](../../README.md#submission-status) and build log. | `VERIFIED` | `2026-07-21T22:16:34Z` | Submission closure was recorded before `2026-07-22T00:00:00Z`. |
| `REQ-DATE-003` | `BW-RULE-003`, `BW-UPDATE-001` | Official deadline is Tuesday, 2026-07-21 17:00 PDT. | Official deadline rechecked; final submission receipt predates it. | `VERIFIED` | `2026-07-21T22:16:34Z` | The earlier internal target was operational, not an official rule. |
| `REQ-DATE-004` | `BW-RULE-004`, `BW-RULE-056` | Maintain judge access during the governing judging period. | Repository and demo currently public; conservative access window is documented below. | `IN_PROGRESS` | `2026-07-21T22:16:34Z` | Continue access through at least `2026-08-12 23:59 PDT`; the Rules/Schedule discrepancy remains recorded. |
| `REQ-DATE-005` | `BW-RULE-005` | Winners are announced on or around 2026-08-12 14:00 PDT. | External future event; no project action determines it. | `NOT_APPLICABLE` | `2026-07-21T22:16:34Z` | Not a project compliance outcome. |

## Eligibility

| Requirement ID | Rule source | Authoritative requirement | Final evidence | Status | Verified at | Blocker / notes |
|---|---|---|---|---|---|---|
| `REQ-ELIG-001` | `BW-RULE-006` | Meet the applicable individual, guardian, team, or organization eligibility rules. | No private eligibility facts are stored in Git. | `BLOCKED` | `2026-07-21T22:16:34Z` | `HUMAN_ELIGIBILITY_ATTESTATION_NOT_RECORDED`. |
| `REQ-ELIG-002` | `BW-RULE-007`, `BW-RULE-055` | Meet legal-residence, age-of-majority, and exclusion conditions. | Current supported-country source rechecked; no personal fact inferred from technical signals. | `BLOCKED` | `2026-07-21T22:16:34Z` | `HUMAN_ELIGIBILITY_ATTESTATION_NOT_RECORDED`. |
| `REQ-ELIG-003` | `BW-RULE-008`, `BW-RULE-009` | Teams/organizations require an eligible authorized representative. | Final entrant structure is not recorded in this public repository. | `BLOCKED` | `2026-07-21T22:16:34Z` | `HUMAN_ENTRANT_STRUCTURE_ATTESTATION_NOT_RECORDED`; individual status was not inferred. |
| `REQ-ELIG-004` | `BW-RULE-010` | Entrant must not fall within the Rules' exclusions. | No private exclusions conclusion is recorded. | `BLOCKED` | `2026-07-21T22:16:34Z` | `HUMAN_EXCLUSIONS_ATTESTATION_NOT_RECORDED`. |

## Project

| Requirement ID | Rule source | Authoritative requirement | Final evidence | Status | Verified at | Blocker / notes |
|---|---|---|---|---|---|---|
| `REQ-PROJ-001` | `BW-RULE-011`, `BW-FAQ-001` | Build the Project with meaningful Codex use. | [Codex collaboration](../../README.md#13-codex-collaboration), build log, decisions, dated implementation, and tests. | `VERIFIED` | `2026-07-21T22:16:34Z` | Core implementation is traceable to the primary Codex workflow. |
| `REQ-PROJ-002` | `BW-RULE-012`, `BW-FAQ-001` | Use GPT-5.6 meaningfully in the Project. | [GPT-5.6 configuration](../../README.md#7-gpt-56-configuration), [responsibility split](../../README.md#9-gpt-56-versus-deterministic-engine-responsibility), strict adapters, tests, and recorded live smoke. | `VERIFIED` | `2026-07-21T22:16:34Z` | GPT-5.6 explains/recommends over completed deterministic output and cannot change it. |
| `REQ-PROJ-003` | `BW-RULE-013` | Select the Work & Productivity track. | README positioning and final Devpost selection receipt. | `VERIFIED` | `2026-07-21T22:16:34Z` | Track: Work & Productivity. |
| `REQ-PROJ-004` | `BW-RULE-014`, `BW-RULE-035` | Provide a functional, consistently runnable Project matching the submission. | Public demo, clean setup path, `260 PASS`, CLI replay, and `3/3` oracle checks. | `VERIFIED` | `2026-07-21T22:16:34Z` | Independent no-login browser access passed. |
| `REQ-PROJ-005` | `BW-RULE-015` | Create or meaningfully extend the Project during the Submission Period. | [Baseline](../../BUILD_WEEK_BASELINE.md), dated commit history, and append-only build log delimit the executable implementation. | `VERIFIED` | `2026-07-21T22:16:34Z` | Qualifying delta is documented. |
| `REQ-PROJ-006` | `BW-RULE-016` | Clearly separate pre-existing and new work. | Baseline, README disclosure, build log, and commits. | `VERIFIED` | `2026-07-21T22:16:34Z` | Concept history is preserved without claiming it as new implementation. |
| `REQ-PROJ-007` | `BW-RULE-017` | Be authorized to use third-party SDKs, APIs, and datasets. | Dependencies are enumerated in [pyproject.toml](../../pyproject.toml); fixture data is synthetic and sanitized. | `EVIDENCED` | `2026-07-21T22:16:34Z` | Final authorization/license conclusion remains human/legal review. |

## Submission

| Requirement ID | Rule source | Authoritative requirement | Final evidence | Status | Verified at | Blocker / notes |
|---|---|---|---|---|---|---|
| `REQ-SUB-001` | `BW-RULE-018` | Include an English description explaining features and functionality. | Accessible English [Devpost description](https://devpost.com/software/memoria-viva), README, and matching demo. | `VERIFIED` | `2026-07-21T22:16:34Z` | Description matches the submitted product. |
| `REQ-SUB-002` | `BW-RULE-019`, `BW-FAQ-003` | Provide a video strictly under three minutes under the Rules-first control. | Unauthenticated YouTube player metadata reported a maximum duration of 179 seconds. | `VERIFIED` | `2026-07-21T21:54:09Z` | Below `00:03:00`. |
| `REQ-SUB-003` | `BW-RULE-020`, `BW-UPDATE-002` | Provide a publicly visible YouTube link. | Public player metadata reported playable, non-private, and non-unlisted; URL returned HTTP 200. | `VERIFIED` | `2026-07-21T21:54:09Z` | Stricter Rules-first public control satisfied. |
| `REQ-SUB-004` | `BW-RULE-021`, `BW-FAQ-003` | Clearly show the working Project with narration/audio. | Public video and caption track exist and are linked from Devpost. | `EVIDENCED` | `2026-07-21T22:16:34Z` | `HUMAN_WORKING_DEMO_AND_NARRATION_REVIEW_NOT_RECORDED`. |
| `REQ-SUB-005` | `BW-RULE-022` | Explain how Codex was used. | Strong repository and submission Codex evidence exists. | `EVIDENCED` | `2026-07-21T22:16:34Z` | `HUMAN_VIDEO_CODEX_COVERAGE_REVIEW_NOT_RECORDED`. |
| `REQ-SUB-006` | `BW-RULE-023` | Explain how GPT-5.6 was used. | Strong repository and submission GPT-5.6 evidence exists. | `EVIDENCED` | `2026-07-21T22:16:34Z` | `HUMAN_VIDEO_GPT_5_6_COVERAGE_REVIEW_NOT_RECORDED`. |
| `REQ-SUB-007` | `BW-RULE-024`, `BW-RULE-048` | Use protected music, marks, or third-party media only with permission. | Video exists; accessibility does not establish rights. | `BLOCKED` | `2026-07-21T22:16:34Z` | `HUMAN_MEDIA_RIGHTS_ATTESTATION_NOT_RECORDED`. |
| `REQ-SUB-008` | `BW-RULE-025` | Provide the code repository URL. | Devpost links the tested [public repository](https://github.com/sprlogisticaeventos-rgb/memoria-viva-attention-graph). | `VERIFIED` | `2026-07-21T22:16:34Z` | Judge-facing URL resolves. |
| `REQ-SUB-009` | `BW-RULE-026` | If public, attach relevant licensing. | Public repository metadata and [MIT License](../../LICENSE). | `VERIFIED` | `2026-07-21T22:16:34Z` | Repository is PUBLIC with SPDX MIT. |
| `REQ-SUB-010` | `BW-RULE-027` | If private, share with official judging accounts. | Repository is public. | `NOT_APPLICABLE` | `2026-07-21T22:16:34Z` | Private-repository condition does not apply. |
| `REQ-SUB-011` | `BW-RULE-028`, `BW-FAQ-002` | README must cover setup/testing, sample data, Codex decisions, and GPT-5.6 integration. | [README](../../README.md) contains all required sections and links. | `VERIFIED` | `2026-07-21T22:16:34Z` | Final repository documentation checked. |
| `REQ-SUB-012` | `BW-RULE-029` | Provide the primary `/feedback` Codex Session ID. | Captured and provided privately in Devpost. | `VERIFIED` | `2026-07-21T22:16:34Z` | Literal value intentionally excluded from Git. |
| `REQ-SUB-013` | `BW-RULE-030`, `BW-FAQ-002` | Provide setup, sample data if needed, and testing instructions. | README quick start, CLI, Streamlit, tests, and [fixture documentation](../../fixtures/founder-hackathon/README.md). | `VERIFIED` | `2026-07-21T22:16:34Z` | Reproducible judge path present. |
| `REQ-SUB-014` | `BW-RULE-031` | Provide an accessible working-project link or build. | Logged-out browser loaded the complete [public demo](https://memoria-viva-attention-graph-kmhfgbtexurbgcqvhaht8v.streamlit.app/) without login. | `VERIFIED` | `2026-07-21T21:54:00Z` | No credentials required. |
| `REQ-SUB-015` | `BW-RULE-032`, `BW-RULE-004`, `BW-RULE-056` | Maintain free, unrestricted access through judging. | Current demo/repository access passes. | `IN_PROGRESS` | `2026-07-21T22:16:34Z` | Continue monitoring through the conservative August 12 window. |
| `REQ-SUB-016` | `BW-RULE-033` | Submit materials in English or with English translations. | README and Devpost description are English. | `EVIDENCED` | `2026-07-21T22:16:34Z` | `HUMAN_ALL_SUBMITTED_SURFACES_LANGUAGE_REVIEW_NOT_RECORDED`. |
| `REQ-SUB-017` | `BW-RULE-034`, `BW-RULE-051` | Complete and enter the submission before deadline. | `SUBMITTED`, `PUBLISHED`, and `RECEIVED` receipts in README/build log. | `VERIFIED` | `2026-07-21T22:16:34Z` | Final Devpost state established. |
| `REQ-SUB-018` | `BW-RULE-051` | Respect post-deadline modification limits. | `CODE_FREEZE: FINAL`; hashes and submission receipts recorded. | `IN_PROGRESS` | `2026-07-21T22:16:34Z` | Continue freeze and availability monitoring; no Devpost modification authorized. |
| `REQ-SUB-019` | `BW-RULE-057` | Multiple submissions by one Entrant must be unique and substantially different. | Public project evidence does not establish the Entrant's complete submission count. | `BLOCKED` | `2026-07-21T22:16:34Z` | `HUMAN_MULTIPLE_SUBMISSIONS_ATTESTATION_NOT_RECORDED`. |
| `REQ-SUB-020` | `BW-RULE-058` | Provide physical access if uncommon proprietary or third-party hardware is required. | Memoria Viva runs in a normal browser and requires no uncommon physical hardware. | `NOT_APPLICABLE` | `2026-07-21T22:16:34Z` | Conditional hardware-access requirement does not apply. |

## Judging readiness

The repository may provide evidence, but only judges determine viability,
design, impact, technological quality, novelty, scores, and tie outcomes.

| Requirement ID | Rule source | Authoritative requirement | Final evidence | Status | Verified at | Blocker / notes |
|---|---|---|---|---|---|---|
| `REQ-JUDGE-001` | `BW-RULE-035`, `BW-RULE-036` | Stage One viability, theme fit, and required-tool application. | Runnable project, track fit, Codex/GPT evidence, README, and video. | `EVIDENCED` | `2026-07-21T22:16:34Z` | `JUDGE_DETERMINED`. |
| `REQ-JUDGE-002` | `BW-RULE-037` | Demonstrate technological implementation. | Deterministic core, tests, schemas, replay, UI, and Codex evidence. | `EVIDENCED` | `2026-07-21T22:16:34Z` | `JUDGE_DETERMINED`. |
| `REQ-JUDGE-003` | `BW-RULE-038` | Demonstrate coherent product design. | Guided decision workspace, responsive review, and public demo. | `EVIDENCED` | `2026-07-21T22:16:34Z` | `JUDGE_DETERMINED`. |
| `REQ-JUDGE-004` | `BW-RULE-039` | Make a credible impact case. | Founder attention problem, protected commitments, and auditable next-action flow. | `EVIDENCED` | `2026-07-21T22:16:34Z` | `JUDGE_DETERMINED`. |
| `REQ-JUDGE-005` | `BW-RULE-040` | Demonstrate creativity, novelty, and differentiation. | Attention Graph, deterministic replay, GraphDelta, and bounded GPT layer. | `EVIDENCED` | `2026-07-21T22:16:34Z` | `JUDGE_DETERMINED`. |
| `REQ-JUDGE-006` | `BW-RULE-041` | Treat all four Stage Two criteria as equally weighted. | README, description, video, demo, and implementation provide balanced evidence. | `EVIDENCED` | `2026-07-21T22:16:34Z` | No self-assigned score. |
| `REQ-JUDGE-007` | `BW-RULE-042` | Tie-break follows the listed order and judge vote. | Evidence is organized in official criterion order. | `EVIDENCED` | `2026-07-21T22:16:34Z` | Tie outcome remains judge-controlled. |
| `REQ-JUDGE-008` | `BW-RULE-043` | Judges may evaluate without running the Project. | Standalone public video, description, README, and demo. | `EVIDENCED` | `2026-07-21T22:16:34Z` | `JUDGE_DETERMINED`. |
| `REQ-JUDGE-009` | `BW-RULE-044` | Evaluation may use automated AI-driven analysis. | Claims, hashes, schemas, and evidence links are internally consistent and machine-readable. | `EVIDENCED` | `2026-07-21T22:16:34Z` | No attempt to predict or game evaluation. |

## Intellectual property, privacy, security, and source responsibility

| Requirement ID | Rule source | Authoritative requirement | Final evidence | Status | Verified at | Blocker / notes |
|---|---|---|---|---|---|---|
| `REQ-RIGHTS-001` | `BW-RULE-045`, `BW-RULE-046` | Submit original work owned by the Entrant with authority to grant required rights. | Repository provenance and Build Week history exist. | `BLOCKED` | `2026-07-21T22:16:34Z` | `HUMAN_ORIGINAL_WORK_OWNERSHIP_ATTESTATION_NOT_RECORDED`. |
| `REQ-RIGHTS-002` | `BW-RULE-047` | Comply with open-source licenses and add meaningful enhancement. | Dependency inventory, project MIT License, baseline, and implementation delta provide evidence. | `EVIDENCED` | `2026-07-21T22:16:34Z` | Final third-party license conclusion remains human/legal review. |
| `REQ-RIGHTS-003` | `BW-RULE-017`, `BW-RULE-048` | Respect third-party code, data, IP, privacy, and publicity rights. | Synthetic fixture, privacy boundaries, and dependency inventory provide partial evidence. | `BLOCKED` | `2026-07-21T22:16:34Z` | `HUMAN_THIRD_PARTY_RIGHTS_ATTESTATION_NOT_RECORDED`. |
| `REQ-RIGHTS-004` | `BW-RULE-059` | Project must not have disqualifying Sponsor/Administrator financial or preferential support. | Code and public records cannot establish this human-only fact. | `BLOCKED` | `2026-07-21T22:16:34Z` | `HUMAN_SPONSOR_SUPPORT_ATTESTATION_NOT_RECORDED`; no financial details belong in Git. |
| `REQ-PRIV-001` | `BW-RULE-049` | Do not violate privacy rights or disclose PII. | [Privacy contract](../privacy.md), sanitized fixture manifest, secret/PII scans, and public-safe demo. | `EVIDENCED` | `2026-07-21T22:16:34Z` | External-surface privacy-rights conclusion remains human-reviewed. |
| `REQ-SEC-001` | `BW-RULE-050` | Include no malicious or harmful code. | `260 PASS`, compilation, source review, strict schemas, and bounded no-write runtime. | `EVIDENCED` | `2026-07-21T22:16:34Z` | Dedicated security attestation is not recorded. |
| `REQ-PLUGIN-001` | `BW-RULE-052` | Devpost plugin use is optional. | Plugin is not a project dependency or compliance premise. | `NOT_APPLICABLE` | `2026-07-21T22:16:34Z` | Optional tool; no product control required. |
| `REQ-PLUGIN-002` | `BW-RULE-053` | Plugin output is not official source-of-truth evidence. | Rules, FAQ, Updates, Dates, and supported-country source were rechecked directly and indexed in [RULES_BASELINE.md](RULES_BASELINE.md). | `VERIFIED` | `2026-07-21T22:08:15Z` | No requirement relies solely on plugin output. |
| `REQ-PLUGIN-003` | `BW-RULE-054` | Entrant remains responsible for verification and compliance. | Current-source review, matrix, checklist, and explicit human-only blockers. | `EVIDENCED` | `2026-07-21T22:16:34Z` | Eligibility and legal attestations remain unresolved. |

## Status summary

| Status | Count |
|---|---:|
| `NOT_STARTED` | 0 |
| `IN_PROGRESS` | 3 |
| `EVIDENCED` | 18 |
| `VERIFIED` | 20 |
| `NOT_APPLICABLE` | 4 |
| `BLOCKED` | 9 |

Total requirements: **54**.

No subjective judging outcome, eligibility conclusion, ownership conclusion,
rights conclusion, multiple-submission fact, or financial-support fact is
self-awarded or inferred. Continuing availability and freeze obligations remain
open throughout the governing review window.
