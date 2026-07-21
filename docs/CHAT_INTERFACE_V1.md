# Memoria Viva — Chat-first interface v1

## Product decision

The judge-facing surface becomes a conversation with the current deterministic
memory state. The existing replay engine, attention ranking, GraphDelta, oracle
checks, execution states, evidence references, and digests remain authoritative.

The interface should feel as simple as a general chat product while remaining
more constrained and auditable:

```text
Memoria Viva
What deserves your attention now?

[ Ask anything about the current memory state... ]
```

## V1 scope

The first interface increment supports five deterministic intents:

1. explain what changed after the trigger;
2. show the current attention priorities;
3. explain why CMT-04 remains conditional;
4. summarize what the bounded replay remembers;
5. rerun and verify the same decision receipt.

Unknown questions receive a transparent bounded-scope response rather than an
invented answer.

## Architecture

```text
chat input
  → deterministic intent router
  → current public-safe DemoViewModel
  → grounded answer + evidence refs + replay digest
```

The chat adapter reads the computed view. It does not calculate or mutate scores,
ranks, GraphDelta, claims, approvals, execution state, or uncertainty.

The existing four-tab experience remains available under **Inspect deterministic
system** for judges who want to inspect the shift, evidence, uncertainty, and
technical proof.

## Guardrails

- No automatic OpenAI API request on import or initial render.
- No raw private evidence or provider identifiers enter the conversation.
- `UNKNOWN` never becomes complete, false, zero, approved, or executed.
- CMT-04 remains conditional with execution `UNKNOWN`.
- A replay question runs the same canonical fixture and exposes the resulting
  digest and oracle status.
- Suggested prompts are convenience controls, not hidden policy inputs.

## Next interface increments

After this shell is validated, the next useful increments are:

1. richer intent coverage over the same deterministic state;
2. a compact answer card showing ranking movement and evidence lineage;
3. optional GPT explanation for open-ended language, still grounded in the
   deterministic response contract;
4. a production input boundary for user-specific memory rather than the single
   canonical fixture.
