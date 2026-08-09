# Core Structured-Analysis Patterns

## Revise an assumption

Record only the decision-relevant change:

```markdown
Previous inference: Query X is the bottleneck.
New evidence: Profile shows X at 4 ms and Y at 280 ms.
Revision: Investigate Y; no optimization of X is justified.
Impact: The implementation scope moves from the query layer to serialization.
```

Do not replay the full analysis that preceded the revision.

## Compare alternatives

Use a small matrix containing only criteria that could change the choice:

| Option | Verified advantages | Material costs | Blocking unknown |
|---|---|---|---|
| A | Reuses current deployment | Higher steady-state latency | None |
| B | Meets latency target | Adds an operated cache | Failure-mode behavior |

Choose after resolving a blocking unknown or state the next decisive check.

## Test competing hypotheses

```markdown
Symptom: Requests stall after authentication.
Hypothesis A: Database lock.
Decisive check: Inspect lock wait metrics during one reproduction.
Result: Refuted — no waits recorded.
Hypothesis B: Downstream timeout.
Decisive check: Trace outbound call duration.
Result: Verified — 30 s timeout matches the stall.
```

Test the cheapest discriminating evidence first. Do not create branches that
cannot change the next action.

## Control scope

- Expand only when evidence shows a wider blast radius or missing dependency.
- Contract when one verified cause explains the observed behavior.
- Keep independent questions separate until their results must be combined.
- Stop when acceptance criteria are supported; do not target an arbitrary amount
  of analysis.

## Anti-patterns

- subjective confidence scores without evidence;
- repeated verification of a fresh passing check;
- alternatives added only to make the analysis look comprehensive;
- status narration that does not change the decision;
- exposing a transcript of private reasoning instead of a concise rationale.
