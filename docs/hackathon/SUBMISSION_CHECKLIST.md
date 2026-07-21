# Submission Checklist

This is the current operational checklist derived from the historical official
source capture in [RULES_BASELINE.md](RULES_BASELINE.md). Final evidence and
status rationale are maintained in
[REQUIREMENTS_MATRIX.md](REQUIREMENTS_MATRIX.md) and
[FINAL_COMPLIANCE_REVIEW.md](FINAL_COMPLIANCE_REVIEW.md). This checklist does
not replace the Official Rules, decide eligibility, or predict judging results.

Review timestamp: `2026-07-21T22:08:58Z`.

## Status semantics

- `VERIFIED`: the objective control and cited evidence were checked.
- `EVIDENCED`: relevant evidence exists, but a judge, host, or human retains
  final authority.
- `IN_PROGRESS`: the operational obligation continues during judging.
- `NOT_APPLICABLE`: the conditional requirement does not apply.
- `HUMAN_REVIEW_REQUIRED`: evidence exists, but a bounded human review remains.
- `BLOCKED`: an essential human fact or attestation is not recorded.

No private eligibility facts or literal Codex Session ID belong in this file.

## Deadline and continuing controls

- The submission was completed and received before the official deadline of
  `2026-07-21 17:00 PDT` (`2026-07-22T00:00:00Z`).
- `CODE_FREEZE` is `FINAL`. No Devpost modification is authorized.
- Keep the public demo, public repository, sample fixture, and judge test path
  free and usable through the Rules-defined judging end of
  `2026-08-05 17:00 PDT` and, as a conservative internal control, through
  `2026-08-12 23:59 PDT`.
- Continuing availability and post-deadline freeze monitoring remain
  `IN_PROGRESS`.

## 1. Eligibility

| Requirement ID | Final control | Evidence | Current status | Final verification |
|---|---|---|---|---|
| `REQ-ELIG-001` | Privately confirm the applicable individual, guardian, team, or organization eligibility path. | Privacy-preserving human attestation only; no identity details in Git. | `BLOCKED` | `HUMAN_ELIGIBILITY_ATTESTATION_NOT_RECORDED` |
| `REQ-ELIG-002` | Recheck the dynamic supported-country source and privately confirm legal-residence, age, and exclusion facts. | Official source rechecked; technical signals were not used as personal evidence. | `BLOCKED` | `HUMAN_ELIGIBILITY_ATTESTATION_NOT_RECORDED` |
| `REQ-ELIG-003` | Privately confirm entrant structure and, if applicable, representative authority. | Devpost entrant/team evidence outside Git. | `BLOCKED` | `HUMAN_ENTRANT_STRUCTURE_ATTESTATION_NOT_RECORDED` |
| `REQ-ELIG-004` | Review all exclusions in Official Rules section 3. | Privacy-preserving human attestation only. | `BLOCKED` | `HUMAN_EXCLUSIONS_ATTESTATION_NOT_RECORDED` |

## 2. Product and Build Week evidence

| Requirement ID | Final control | Evidence | Current status | Final verification |
|---|---|---|---|---|
| `REQ-PROJ-001` | Demonstrate meaningful Codex contribution to core construction. | [README Codex collaboration](../../README.md#13-codex-collaboration), [BUILD_LOG.md](../../BUILD_LOG.md), dated commits, implementation, and tests. | `VERIFIED` | Complete |
| `REQ-PROJ-002` | Demonstrate a substantive GPT-5.6-backed capability. | [GPT-5.6 configuration](../../README.md#7-gpt-56-configuration), strict output contracts, tests, and recorded live smoke. | `VERIFIED` | Complete |
| `REQ-PROJ-003` | Select Work & Productivity and align the submitted product with it. | README, final Devpost selection receipt, and public project description. | `VERIFIED` | Complete |
| `REQ-PROJ-004` | Prove a functional, consistently runnable project matching the submission. | Public demo, reproducible setup, `260 PASS`, and `3/3` oracle checks. | `VERIFIED` | Complete |
| `REQ-PROJ-005` | Identify qualifying implementation created during the submission period. | [Build Week baseline](../../BUILD_WEEK_BASELINE.md), dated commit history, and build log. | `VERIFIED` | Complete |
| `REQ-PROJ-006` | Separate the pre-existing concept from new Build Week implementation. | Baseline, README disclosure, append-only build log, and commit history. | `VERIFIED` | Complete |
| `REQ-JUDGE-001` | Provide viability, theme-fit, and required-tool evidence without self-awarding Stage One. | Demo, repository, tests, README, and submitted narrative. | `EVIDENCED` | `JUDGE_DETERMINED` |

## 3. Repository, README, and demo access

| Requirement ID | Final control | Evidence | Current status | Final verification |
|---|---|---|---|---|
| `REQ-SUB-008` | Provide and test the final judge-facing repository URL. | [Public repository](https://github.com/sprlogisticaeventos-rgb/memoria-viva-attention-graph) and public Devpost link. | `VERIFIED` | Complete |
| `REQ-SUB-009` | Attach relevant licensing to the public repository. | Public visibility and [MIT License](../../LICENSE). | `VERIFIED` | Complete |
| `REQ-SUB-010` | Share a private repository with both official judging addresses. | Repository is public. | `NOT_APPLICABLE` | Conditional requirement resolved |
| `REQ-SUB-011` | Provide README setup, sample-data, testing, Codex, decision, and GPT-5.6 evidence. | [README.md](../../README.md). | `VERIFIED` | Complete |
| `REQ-SUB-012` | Provide the representative primary-thread `/feedback` Session ID privately in Devpost. | Recorded as captured and privately provided; literal value excluded from Git. | `VERIFIED` | Complete |
| `REQ-SUB-013` | Provide and rehearse setup, sample fixture, and test instructions. | README quick start, CLI, Streamlit, test suite, and fixture documentation. | `VERIFIED` | Complete |
| `REQ-SUB-014` | Provide a no-login working-project link and test it outside the owner session. | [Public demo](https://memoria-viva-attention-graph-kmhfgbtexurbgcqvhaht8v.streamlit.app/) and logged-out browser review. | `VERIFIED` | Complete |
| `REQ-SUB-015` | Maintain free demo, repository, sample-data, and judge-path access through judging. | Current public access passes; ongoing availability control above. | `IN_PROGRESS` | Continue monitoring |
| `REQ-SUB-020` | Provide physical access if the project depends on proprietary or uncommon third-party hardware. | Memoria Viva is a browser-accessible software project and requires no such hardware. | `NOT_APPLICABLE` | Conditional requirement resolved |

## 4. Video

| Requirement ID | Final control | Evidence | Current status | Final verification |
|---|---|---|---|---|
| `REQ-SUB-002` | Keep the final encode strictly below `00:03:00`. | [Public video](https://youtu.be/a7Ri_qCfxc0); accessible player metadata reports less than 180 seconds. | `VERIFIED` | Complete |
| `REQ-SUB-003` | Publish the YouTube link and verify public, logged-out access. | Public player metadata reports playable, non-private, and non-unlisted. | `VERIFIED` | Complete |
| `REQ-SUB-004` | Confirm audible narration and clear working-project footage. | Public video exists and is linked in Devpost. | `HUMAN_REVIEW_REQUIRED` | `HUMAN_WORKING_DEMO_AND_NARRATION_REVIEW_NOT_RECORDED` |
| `REQ-SUB-005` | Confirm narration explains concrete Codex workflow and decisions. | Repository and Devpost contain Codex evidence. | `HUMAN_REVIEW_REQUIRED` | `HUMAN_VIDEO_CODEX_COVERAGE_REVIEW_NOT_RECORDED` |
| `REQ-SUB-006` | Confirm narration explains the integrated GPT-5.6 capability. | Repository and Devpost contain GPT-5.6 evidence. | `HUMAN_REVIEW_REQUIRED` | `HUMAN_VIDEO_GPT_5_6_COVERAGE_REVIEW_NOT_RECORDED` |
| `REQ-SUB-007` | Confirm ownership or permission for protected music, marks, and other media. | Public video exists; no rights conclusion is inferred from availability. | `HUMAN_REVIEW_REQUIRED` | `HUMAN_MEDIA_RIGHTS_REVIEW_NOT_RECORDED` |

## 5. Devpost and submission closure

| Requirement ID | Final control | Evidence | Current status | Final verification |
|---|---|---|---|---|
| `REQ-SUB-001` | Provide an accurate English project description matching the product. | [Published Devpost project](https://devpost.com/software/memoria-viva), README, and demo. | `VERIFIED` | Complete |
| `REQ-SUB-016` | Confirm every submitted surface is English or has a complete English translation. | README and public Devpost description are English. | `HUMAN_REVIEW_REQUIRED` | `HUMAN_ALL_SUBMITTED_SURFACES_LANGUAGE_REVIEW_NOT_RECORDED` |
| `REQ-SUB-017` | Complete and enter the final submission before the deadline. | `SUBMITTED`, `PUBLISHED`, and `RECEIVED` receipts in README and build log. | `VERIFIED` | Complete |
| `REQ-SUB-018` | Preserve the final freeze and obey post-deadline modification limits. | `CODE_FREEZE: FINAL`; submission receipts and final hashes recorded. | `IN_PROGRESS` | No post-deadline Devpost changes |
| `REQ-DATE-003` | Confirm submission before the official deadline. | Final closure receipt and pre-deadline repository record. | `VERIFIED` | Complete |
| `REQ-SUB-019` | Privately confirm whether the entrant made another submission; if so, verify it is unique and substantially different. | Privacy-preserving human attestation only. | `BLOCKED` | `HUMAN_MULTIPLE_SUBMISSIONS_ATTESTATION_NOT_RECORDED` |

## 6. Licensing, rights, privacy, and security

| Requirement ID | Final control | Evidence | Current status | Final verification |
|---|---|---|---|---|
| `REQ-PROJ-007` | Verify authorization for every third-party SDK, API, and dataset. | Dependencies are enumerated; authorization is not inferred. | `BLOCKED` | `HUMAN_THIRD_PARTY_AUTHORIZATION_ATTESTATION_NOT_RECORDED` |
| `REQ-RIGHTS-001` | Confirm original work, ownership, contributor rights, and authority to submit. | Repository provenance is evidence, not a legal conclusion. | `BLOCKED` | `HUMAN_ORIGINAL_WORK_OWNERSHIP_ATTESTATION_NOT_RECORDED` |
| `REQ-RIGHTS-002` | Verify open-source licenses and meaningful enhancement. | Dependency list and project MIT license exist; no third-party license conclusion is inferred. | `BLOCKED` | `HUMAN_OPEN_SOURCE_LICENSE_ATTESTATION_NOT_RECORDED` |
| `REQ-RIGHTS-003` | Review third-party code, data, media, trademark, privacy, and publicity rights. | Repository privacy controls and dependency inventory provide partial evidence. | `BLOCKED` | `HUMAN_THIRD_PARTY_RIGHTS_ATTESTATION_NOT_RECORDED` |
| `REQ-RIGHTS-004` | Privately confirm that the project was not developed or derived with disqualifying Sponsor or Administrator financial or preferential support. | Privacy-preserving human attestation only. | `BLOCKED` | `HUMAN_SPONSOR_SUPPORT_ATTESTATION_NOT_RECORDED` |
| `REQ-PRIV-001` | Review secret/PII handling across repository, demo, video, and Devpost. | [Privacy policy](../privacy.md), fixture manifest, sanitization controls, and repository scans. | `HUMAN_REVIEW_REQUIRED` | `HUMAN_EXTERNAL_SURFACE_PRIVACY_REVIEW_NOT_RECORDED` |
| `REQ-SEC-001` | Review submitted code and dependencies for harmful or malicious behavior. | Tests, compilation, and source review provide evidence. | `HUMAN_REVIEW_REQUIRED` | `DEDICATED_SECURITY_ATTESTATION_NOT_RECORDED` |

## 7. Judging and source responsibility

| Requirement ID | Final control | Evidence | Current status | Final verification |
|---|---|---|---|---|
| `REQ-JUDGE-006` | Provide balanced evidence for all four equally weighted criteria without assigning scores. | Public description, README, video, demo, code, and tests. | `EVIDENCED` | `JUDGE_DETERMINED` |
| `REQ-JUDGE-008` | Ensure submitted media can communicate the project even if judges do not run it. | Public video, description, README, and demo. | `EVIDENCED` | `JUDGE_DETERMINED` |
| `REQ-PLUGIN-002` | Use official sources, never plugin output, as compliance authority. | Rules, FAQ, Updates, Dates, and supported-country source were rechecked directly. | `VERIFIED` | Complete |
| `REQ-PLUGIN-003` | Preserve entrant responsibility for compliance and human-only attestations. | Matrix and final compliance review identify unresolved human facts. | `EVIDENCED` | Human attestations remain unresolved |

## Current status summary

| Status | Count |
|---|---:|
| `VERIFIED` | 18 |
| `EVIDENCED` | 4 |
| `IN_PROGRESS` | 2 |
| `NOT_APPLICABLE` | 2 |
| `HUMAN_REVIEW_REQUIRED` | 7 |
| `BLOCKED` | 10 |

The checklist covers 43 distinct controls. Objective product, repository,
license, demo, video metadata, private Session-ID delivery, and submission
closure controls are no longer pending. Continuing access/freeze controls and
human-only legal, eligibility, rights, privacy, media, language, and security
reviews remain explicit.
