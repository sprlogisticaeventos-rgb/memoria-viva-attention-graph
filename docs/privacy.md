# Privacy and Data Boundaries

## Policy metadata

| Field | Value |
|---|---|
| Policy ID | `mv_privacy_phase_0` |
| Version | `1.0.0` |
| Status | `active_repository_boundary` |
| Effective date | 2026-07-18 |

This policy controls where evidence, fixtures, generated outputs, and secrets
may exist. It does not claim that any future public fixture has been approved.

## Data classes

| Data class | Allowed location | Git state | Publication state |
|---|---|---|---|
| Raw private inputs | `fixtures/private/**` | Ignored except `.gitkeep` | Prohibited |
| Sanitized public fixtures | `fixtures/founder-hackathon/**` | Tracked after review | Eligible only after approval |
| Generated local runs | `runs/**` | Ignored except `.gitkeep` | Prohibited by default |
| Versioned expected outputs | `fixtures/founder-hackathon/expected/**` | Tracked later | Eligible only after review |
| Secrets | `.env.local` and other ignored `.env.*` files | Ignored | Prohibited |
| Configuration names | `.env.example` | Tracked | Public, with empty placeholders only |

## Raw private inputs

Raw Calendar exports, messages, names, contact details, private repository
material, account identifiers, and source documents remain under
`fixtures/private/**` or outside the repository. They must never be staged,
logged, pasted into documents, or copied into `runs/` for publication.

Private identifiers must not appear in public Graph references. A public
fixture receives new stable identifiers that cannot be resolved back to a
private person without separately held information.

Public evidence and lineage use repository-safe synthetic references only.
They must not retain filesystem paths, URLs, email or Calendar IDs, account or
submission identifiers, raw locators, or any reversible mapping to a private
source. Artifact-level provenance records classification, authority, capture
method, review state, and sanitization—not the private address of the source.

## Sanitized public fixtures

A fixture is eligible for tracking only when:

1. it contains the minimum fields required for the replay;
2. real names, email addresses, phone numbers, account IDs, private URLs,
   message bodies, credentials, tokens, and unnecessary timestamps are absent;
3. source-derived and synthetic fields are labeled in its privacy manifest;
4. PII review has a recorded status;
5. approval status is explicit and never inferred from file presence.

`NOT_APPROVED` and `NOT_REVIEWED` are valid states. Missing approval is not
equivalent to approval.

Publication approval is surface-specific. Approval for a repository fixture
does not automatically authorize a demo screen, narrated video, Devpost form,
public documentation, or API response. Each field transformation records its
original class, action, sanitized class, source-derived or synthetic status,
reversibility, approved publication surfaces, reviewer state, and approval
artifact.

The canonical machine-readable manifest contract is
[`../schemas/privacy-manifest.schema.json`](../schemas/privacy-manifest.schema.json).
It preserves residual aggregation risk, including `LOW_MEDIUM`, because a set
of individually safe fields may reveal more when combined. Residual risk and
`UNKNOWN` values remain visible until human review resolves them.

## Generated runs and expected outputs

Local runs may inherit sensitive information from inputs and are therefore
ignored. A local run must never be promoted by copying it wholesale into a
tracked path.

Expected outputs are separate sanitized golden artifacts. Promotion requires
deterministic replay, field-by-field privacy review, an updated manifest, and
explicit approval. Expected outputs retain sanitized evidence references but
not private locators.

## Secrets

Secrets belong only in ignored environment files or an external secret store.
They must not appear in fixtures, schemas, policies, documentation, logs,
RunRecords, Git history, or screenshots. `.env.example` contains variable names
and empty placeholders only.

## Review and retention

- Raw private inputs: local retention only, for the minimum period needed.
- Sanitized fixtures: versioned with their privacy manifest.
- Local runs: disposable and ignored.
- Expected outputs: versioned only after privacy review.
- Evidence of approval: reference an approval record; do not invent a reviewer.
- Publication approval: grant per surface and never infer from another surface.

Before staging, review the staged path list, verify ignore rules, run a
filename-only redacted secret/PII scan, and confirm that public fixtures match
their manifest. Any uncertainty blocks publication.
