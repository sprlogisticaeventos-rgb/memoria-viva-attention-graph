# Final Compliance Review

## Review identity

| Field | Value |
|---|---|
| Review timestamp | `2026-07-21T23:21:01Z` |
| Project | Memoria Viva — Attention Graph for Founder Decisions |
| Branch | `build-week/final-repo-metadata-closure` |
| Reviewed base commit | `794aaa1712a4d23b4d739550970616cb18571e2d` |
| Track | Work & Productivity |
| Record type | Internal final implementation/submission compliance review |

This review applies the official-source hierarchy recorded in
[RULES_BASELINE.md](RULES_BASELINE.md): Official Rules control, followed by
Official FAQ, Official Updates, written clarification, and internal
interpretation. The Official Schedule and current OpenAI supported-country
documentation are supplemental sources; the Rules control any conflict.

## Current-source recheck

Official Rules, FAQ, Updates, Dates, and the supported-country source were
accessed read-only again at `2026-07-21T22:54:41Z`. No material source change
or rule was found that contradicts the submitted browser project. The
previously recorded Rules-versus-Schedule judging-window discrepancy remains
unresolved, so the more conservative access window remains an internal control.

The recheck identified three obligations that were not indexed in the original
repository baseline. The available historical capture cannot establish whether
the official wording was added later or was present and omitted locally. They
are now recorded without rewriting the 2026-07-18 capture:

- `BW-RULE-057` — Multiple Submissions: human confirmation remains required.
- `BW-RULE-058` — proprietary or third-party hardware access: not applicable
  because the project runs in a normal browser.
- `BW-RULE-059` — Financial or Preferential Support: privacy-safe human
  attestation remains required.

See append-only [RULE_CHANGELOG.md](RULE_CHANGELOG.md).

## Repository-integrity reconciliation

The first reconciliation was validated locally at commit
`a59862228dd9b4c65c6b543328ada73e69e536a7` and merged remotely through pull
request 6 at `c2039595e9d33b875141c810c0c5b99ee4b13632`. A byte-level comparison found
that nine of the ten intended files matched exactly, while `BUILD_LOG.md` had
been truncated during authenticated remote reconstruction. This second review
restored `BUILD_LOG.md` byte-for-byte from the validated local commit before
appending the next sequential entry. No earlier `MV-BUILD` record was edited.

The incident affected repository documentation only. Application behavior,
deterministic semantics, schemas, fixtures, policies, scores, rankings,
GraphDelta, RunRecord, ReplayResult, oracle expectations, GPT behavior, and
deployment behavior were unchanged.

## Final public surfaces

| Surface | Final evidence |
|---|---|
| Repository | [Public GitHub repository](https://github.com/sprlogisticaeventos-rgb/memoria-viva-attention-graph) |
| License | [MIT](../../LICENSE) |
| Demo | [Public no-login Streamlit app](https://memoria-viva-attention-graph-kmhfgbtexurbgcqvhaht8v.streamlit.app/) |
| Video | [Public YouTube demo](https://youtu.be/a7Ri_qCfxc0) |
| Devpost | [Published project](https://devpost.com/software/memoria-viva) |
| Devpost state | `SUBMITTED`, `PUBLISHED`, confirmation `RECEIVED` |
| Code freeze | `FINAL` |

The primary Codex `/feedback` Session ID was captured and provided privately
in Devpost. Its literal value is not stored here.

A logged-out browser recheck loaded the repository, demo, video, and Devpost
URLs. At `2026-07-21T23:21:01Z`, the repository page metadata reported the
public description `Attention Graph for founder decisions.` The previously
flagged unprofessional description was corrected by the repository owner; no
tracked product or deterministic artifact changed as part of that settings
correction.

## Technical receipts

| Receipt | Result |
|---|---|
| Complete test suite | `260 PASS` |
| Python compilation | `PASS` |
| CLI replay | `PASS` |
| Ranking-before oracle | `PASS` |
| Ranking-after oracle | `PASS` |
| GraphDelta oracle | `PASS` |
| ReplayResult digest | `sha256:3ae0d566fef04029972e1875f2026e11cd9a60d39208241f030330e6237c6f15` |
| Public replay JSON hash | `18be9783b470b0fb738b2c8be82a76b76d302d88346c22443f19346b3cbaeb37` |
| Strict tracked JSON parsing | `32/32 PASS` |
| Schema registration/local resolution | `19/19 PASS` |

Codex evidence is preserved in the dated commit history,
[BUILD_LOG.md](../../BUILD_LOG.md), [DECISIONS.md](../../DECISIONS.md), and the
[README collaboration section](../../README.md#13-codex-collaboration). Codex
was the primary implementation collaborator across contracts, deterministic
runtime, replay, tests, CLI, and demo.

GPT-5.6 evidence is preserved in the
[configuration](../../README.md#7-gpt-56-configuration),
[responsibility boundary](../../README.md#9-gpt-56-versus-deterministic-engine-responsibility),
strict structured-output adapters, tests, and live-smoke receipt. GPT-5.6 may
explain or recommend over a completed sanitized deterministic result; it cannot
change state, scores, rankings, GraphDelta, execution, or approvals.

## Requirements disposition

The controlling row-by-row evidence is in
[REQUIREMENTS_MATRIX.md](REQUIREMENTS_MATRIX.md).

| Status | Count |
|---|---:|
| `VERIFIED` | 20 |
| `EVIDENCED` | 18 |
| `IN_PROGRESS` | 3 |
| `NOT_APPLICABLE` | 4 |
| `BLOCKED` | 9 |
| **Total** | **54** |

### VERIFIED

`REQ-DATE-001`–`003`; `REQ-PROJ-001`–`006`; `REQ-SUB-001`–`003`;
`REQ-SUB-008`; `REQ-SUB-009`; `REQ-SUB-011`–`014`; `REQ-SUB-017`;
`REQ-PLUGIN-002`.

These are objective timing, implementation, track, functionality, description,
repository, license, README, private Session-ID delivery, setup/test path,
public-demo, video-metadata, source-authority, and final-submission controls.

### EVIDENCED

`REQ-PROJ-007`; `REQ-SUB-004`–`006`; `REQ-SUB-016`;
`REQ-JUDGE-001`–`009`; `REQ-RIGHTS-002`; `REQ-PRIV-001`; `REQ-SEC-001`;
`REQ-PLUGIN-003`.

Evidence exists, but judges or human/legal reviewers retain authority over
judging quality, complete video-content review, language coverage,
third-party-license conclusions, privacy rights, security, and final
compliance.

### IN_PROGRESS

- `REQ-DATE-004` — keep judge access available during the governing window.
- `REQ-SUB-015` — keep demo, repository, sample fixture, and judge test path
  free and usable through at least the conservative `2026-08-12 23:59 PDT`
  control.
- `REQ-SUB-018` — maintain the post-deadline freeze and availability
  monitoring; do not modify Devpost.

### NOT_APPLICABLE

- `REQ-DATE-005` — winner announcement is not a project compliance outcome.
- `REQ-SUB-010` — private-repository sharing does not apply to a public repo.
- `REQ-SUB-020` — no proprietary or uncommon physical hardware is required.
- `REQ-PLUGIN-001` — the optional plugin is not a product dependency.

### BLOCKED / human-only attestations

- `REQ-ELIG-001`–`004` — eligibility, residence/age condition, entrant
  structure, representative authority, and exclusions.
- `REQ-SUB-007` — media-rights attestation.
- `REQ-SUB-019` — entrant-wide submission count and, if applicable,
  substantial differentiation.
- `REQ-RIGHTS-001` — original-work ownership and authority to grant rights.
- `REQ-RIGHTS-003` — third-party rights conclusion.
- `REQ-RIGHTS-004` — financial or preferential support attestation.

No blocked human-only fact has been inferred from code, IP address, timezone,
Git metadata, public URLs, or machine state.

## Privacy and limits

This repository records no literal Session ID, identity data, address, age,
financial details, secret, private filesystem path, email message identifier,
or raw private evidence. Canonical fixture and replay publication states remain
unchanged; external submission does not broaden their deterministic semantics
or surface-specific privacy authority.

This is an internal compliance record, not legal advice, an eligibility
determination, a rights opinion, or a guarantee of any judging outcome.
