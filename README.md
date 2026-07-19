# Memoria Viva — Attention Graph

Memoria Viva is an Attention Graph for founder decisions. It turns a new,
verifiable event into an immutable state transition, an explainable attention
ranking, and an auditable replay receipt.

> Memory stores the past. Attention chooses the next move.

Built during OpenAI Build Week 2026 for the **Work & Productivity** track.

## Live Demo

**[Run the public Memoria Viva demo](https://memoria-viva-attention-graph-kmhfgbtexurbgcqvhaht8v.streamlit.app/)**

The deployed app is a public-safe synthetic replay of the reviewed canonical
fixture. It requires no login and exposes no raw private evidence, secret,
private path, or external source material.

| Current validation | Status |
|---|---|
| Unit tests | `200 PASSING` |
| CLI smoke | `PASS` |
| Streamlit local smoke | `PASS` |
| Deployed smoke | `PASS` |
| Public app access | `PASS` |
| Live GPT-5.6 smoke | `PASS` |
| Ranking-before oracle | `PASS` |
| Ranking-after oracle | `PASS` |
| GraphDelta oracle | `PASS` |

## 1. Product statement

Memoria Viva answers four practical questions:

1. What changed?
2. What now deserves attention?
3. What must remain protected?
4. What still requires evidence or human approval?

The deterministic engine—not a language model—constructs state transitions,
scores, rankings, GraphDelta, and claims. GPT-5.6 explains those completed
results; it does not determine or modify them.

## 2. The founder problem

Calendar entries, messages, opportunities, and obligations live in separate
tools. A new event usually becomes one more task, while its effects on existing
commitments stay implicit. Memoria Viva reconstructs the before/after system,
keeps displaced and protected work visible, and preserves uncertainty instead
of inventing certainty.

## 3. What the demo proves

One sanitized founder scenario executes end to end:

```text
BEFORE → NEW EXTERNAL EVENT → AFTER → WHY ATTENTION CHANGED
```

The replay:

- validates committed inputs against canonical JSON Schemas;
- builds immutable Snapshot T0 and Snapshot T1;
- applies one canonical trigger without follow-up leakage;
- computes versioned six-component attention scores;
- preserves protection, dependency, confirmation, and conditionality rules;
- emits a 21-change GraphDelta across all seven approved categories;
- compares before, after, and GraphDelta outputs with human-authored oracles;
- produces an immutable RunRecord and ReplayResult digest;
- passes all three oracle comparisons.

The same replay is deployed through Streamlit Community Cloud from `main`. Its
public access, deterministic replay, optional GPT-5.6 brief, four-tab render,
and sanitized JSON download have passed human smoke review.

## 4. Quick start

Requires Python 3.12.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
PYTHONPATH=src python -m unittest discover -s tests -v
```

The dependency file installs the local package with its pinned `demo` extras.

## 5. Run the CLI

Judge-readable replay, with no file writes:

```bash
python -m memoria_viva.cli replay
```

Deterministic public-safe JSON:

```bash
python -m memoria_viva.cli replay --format json
```

Optional explicit local export under the ignored `runs/` boundary:

```bash
python -m memoria_viva.cli replay --output-dir runs/demo
```

Existing exports are never replaced unless `--force` is supplied. Paths outside
`runs/` are rejected.

## 6. Run Streamlit locally

```bash
streamlit run streamlit_app.py
```

The app computes the deterministic replay locally without a network call. Use
**Run deterministic replay** to repeat the same transition and digest.

## 7. GPT-5.6 configuration

GPT-5.6 runs only after the user presses **Generate GPT-5.6 Decision Brief**.
It is not called on import or initial page render.

For local development, keep credentials in ignored `.env.local`:

```dotenv
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.6
```

An existing environment variable takes precedence; dotenv never overwrites it.
Streamlit Community Cloud can use server-side secrets named
`OPENAI_API_KEY` and, optionally, `OPENAI_MODEL`. Secret values are never sent
to the browser, printed, persisted, or committed.

The app remains fully usable without an API key. It always shows the
**Deterministic Engine Brief** and returns a concise safe diagnostic if the
optional model call fails.

## 8. Deterministic architecture

```text
sanitized runtime bundle
  → schema validation
  → Snapshot T0
  → canonical trigger
  → Snapshot T1
  → production rankings
  → GraphDelta
  → isolated oracle comparisons
  → RunRecord
  → public-safe DemoViewModel
```

Canonical serialization is `MV_CANONICAL_JSON_V1`. Stable IDs and SHA-256
digests make repeated replays byte-identical. Runtime and Oracle bundles remain
separate; human expected ranks never enter scoring or production generation.

## 9. GPT-5.6 versus deterministic-engine responsibility

| Deterministic engine | GPT-5.6 explanation layer |
|---|---|
| Creates Snapshots and transition state | Explains supplied sanitized output |
| Extracts components and computes scores | Cannot change a component or score |
| Builds rankings and GraphDelta | Cannot change rank or execution state |
| Preserves claims, uncertainty, and approvals | Must retain uncertainty and approval boundaries |
| Produces replay and RunRecord digests | Produces a strict `DecisionBrief` only |

The Responses API uses strict Structured Output validated against
[`schemas/decision-brief.schema.json`](schemas/decision-brief.schema.json).
Invalid output is discarded safely; it never replaces deterministic results.

## 10. Canonical demo scenario

The only MVP scenario is the reviewed sanitized founder fixture in
[`fixtures/founder-hackathon/`](fixtures/founder-hackathon/README.md). A bounded
OpenAI Build Week opportunity serves `GC-01 — PRODUCT_VALIDATION`; it is not a
fourth Goal. The replay keeps three public Goals, ten Calendar candidates,
excluded-but-retained evidence, five operational commitments, and explicit
lineage.

The synthetic event creates two protected commitments. A protected continuity
item remains top-three, one item is only conditionally displaceable with
execution `UNKNOWN`, and two items still require confirmation. Communication
evidence is not official-rule authority.

## 11. Privacy and sanitization

- The fixture uses independently synthesized coarse chronology.
- No real Gmail or Calendar connection exists in the MVP.
- No raw provider IDs, private paths, URLs, accounts, or reversible mappings
  enter the demo.
- Residual aggregation risk remains `LOW_MEDIUM`.
- `PUBLIC_FIXTURE` is `APPROVED` only for the committed sanitized canonical
  fixture and sanitized replay projection reviewed through the deployed UI and
  downloadable JSON. This does not authorize raw private evidence or external
  source material.
- `DEMO_UI` is `APPROVED`; `PUBLIC_APP_ACCESS` and `DEPLOYED_SMOKE` are `PASS`.
- `REPOSITORY_DOCS` is `PENDING_FINAL_REVIEW`.
- `DEMO_VIDEO` and `DEVPOST_SUBMISSION` remain `PENDING`.
- `FINAL_COMPLIANCE` remains `UNVERIFIED`.

Approval is surface-specific and does not extend beyond the statuses above.
See [`docs/privacy.md`](docs/privacy.md) and the fixture privacy manifest.

## 12. Test suite

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src tests streamlit_app.py
```

The suite covers closed-schema registration, fixture boundaries, immutable
Snapshots, transition semantics, scoring, oracle isolation, GraphDelta,
RunRecord, replay determinism, CLI export controls, public-safe presentation,
mocked strict GPT output, safe fallback behavior, and Streamlit rendering. No
automated test makes a paid API request. The Phase 2 validation baseline is
**200 passing tests**.

## 13. Codex collaboration

Codex was the primary engineering collaborator. This primary thread implemented
contracts, loaders, canonical serialization, Snapshots, transition, scoring,
oracle isolation, GraphDelta, RunRecord, replay, tests, CLI, and demo.

The founder retained authority over ontology, policy, privacy, Goals,
trade-offs, approval boundaries, and public wording. Git history,
[`DECISIONS.md`](DECISIONS.md), and [`BUILD_LOG.md`](BUILD_LOG.md) preserve that
evolution. The final primary `/feedback` Session ID remains pending until this
thread is complete.

## 14. Repository structure

```text
config/                       versioned attention policies
docs/                         blueprint, ontology, privacy, compliance evidence
fixtures/founder-hackathon/   sanitized canonical scenario and human oracles
schemas/                      canonical Draft 2020-12 contracts
src/memoria_viva/             deterministic core and demo adapters
tests/                        unittest contract, replay, CLI, UI, and explainer tests
runs/                         ignored explicit local exports only
streamlit_app.py              one-page judge demo
```

## 15. Known limits

- One sanitized fixture scenario only.
- The feature policy remains approved only for bounded Replay Mode; it is not a
  production-active policy claim. The base policy remains `draft` with
  `effective_at: null`.
- GPT-5.6 explains completed deterministic output but is not required for replay.
- No real Gmail, Calendar, database, authentication, agents, scheduler, or
  external writes.
- Compliance, submission completion, Goal completion, executed displacement,
  and publication approval remain unclaimed.

## 16. Deployment instructions

The public demo is deployed on Streamlit Community Cloud from `main`:

<https://memoria-viva-attention-graph-kmhfgbtexurbgcqvhaht8v.streamlit.app/>

Current deployment validation:

- `DEMO_UI: APPROVED`
- `PUBLIC_APP_ACCESS: PASS`
- `DEPLOYED_SMOKE: PASS`
- `LIVE_GPT_5_6_SMOKE: PASS`

For a future deployment update:

1. Select this repository and the approved deployment branch.
2. Use `streamlit_app.py` as the entrypoint.
3. Use Python 3.12.
4. Let `requirements.txt` install the local package and pinned demo dependencies.
5. Add `OPENAI_API_KEY` and optional `OPENAI_MODEL` as server-side secrets.
6. Verify the deterministic initial render before testing the optional GPT
   button.
7. Preserve the existing surface-specific privacy and publication gates.

Paths are repository-relative and Linux-compatible. No Mac-specific behavior or
local absolute path is required.

## 17. Hackathon status

The executable replay core and all three oracle comparisons pass. The public
Streamlit deployment, no-login access, deterministic replay, GPT-5.6 brief, and
sanitized JSON download have passed human smoke review. `PUBLIC_FIXTURE` and
`DEMO_UI` are approved within their bounded sanitized scopes.

`REPOSITORY_DOCS` remains `PENDING_FINAL_REVIEW`; `DEMO_VIDEO` and
`DEVPOST_SUBMISSION` remain `PENDING`; and `FINAL_COMPLIANCE` remains
`UNVERIFIED`.

Official hackathon sources have been captured as evidence. Compliance remains
unverified pending final implementation artifacts, current-source recheck, and
human review. See [`docs/hackathon/`](docs/hackathon/RULES_BASELINE.md).

## 18. Canonical sources

1. [`docs/CONSTRUCTION_BLUEPRINT.md`](docs/CONSTRUCTION_BLUEPRINT.md)
2. [`docs/ontology.md`](docs/ontology.md)
3. [`schemas/`](schemas/)
4. Deterministic code and invariants
5. Current milestone instruction

Attention policy authority is in [`config/`](config/). Contract and product
decisions are recorded in [`DECISIONS.md`](DECISIONS.md).
