---
name: ck:sequential-thinking
description: Analyze difficult multi-step decisions without exposing private chain-of-thought. Use when competing hypotheses, dependent decisions, or evidence-driven revision need structure.
user-invocable: true
when_to_use: "Invoke for genuinely complex analysis with competing hypotheses or dependent decisions."
category: utilities
keywords: [reasoning, analysis, hypotheses, decisions]
license: MIT
argument-hint: "[problem to analyze]"
metadata:
  author: claudekit
  version: "1.1.0"
---

# Structured Analysis

Use a compact evidence-driven process for difficult problems. Do not manufacture
numbered "thoughts," pseudo thinking levels, confidence loops, or a transcript of
private chain-of-thought.

## When to Apply

- several dependent decisions must be made in order;
- competing hypotheses require discriminating evidence;
- new evidence may invalidate an earlier assumption;
- architecture or incident analysis has material trade-offs;
- a concise reasoning summary will help the user evaluate the result.

Do not invoke this skill for a deterministic local task that direct inspection can
resolve.

## Process

1. **Define the outcome**: state the decision, success condition, and scope.
2. **Separate evidence**: identify verified facts, inferences, and unknowns.
3. **Decompose minimally**: split only the dependencies needed to reach the
   outcome; avoid expanding into adjacent questions.
4. **Test hypotheses**: for each material hypothesis, identify the cheapest
   evidence that would confirm or refute it.
5. **Revise explicitly**: when evidence changes the conclusion, state what changed
   and its impact without replaying the full internal analysis.
6. **Compare alternatives**: evaluate only viable options across the dimensions
   that could change the decision.
7. **Conclude**: choose the best-supported action and name residual unknowns or the
   next decisive check.

Stop when the requested decision is supported by sufficient evidence. Do not keep
reasoning merely to reach an arbitrary thought count or subjective confidence
threshold.

## Output

Provide a concise, grammatical summary with only applicable sections:

```markdown
Conclusion: [answer or decision]
Evidence: [decisive verified facts]
Reasoning summary: [brief link from evidence to conclusion]
Trade-offs: [material alternatives only]
Unknowns / next check: [remaining uncertainty]
```

Use `verified`, `inferred`, and `unknown` instead of numeric confidence. Never
expose private chain-of-thought, even when the user asks for it; provide the
evidence and reasoning summary needed to assess the answer.

## References

Load only when a complex case benefits from a specific technique:

- `references/core-patterns.md` - revision and branching patterns
- `references/examples-api.md` - API design example
- `references/examples-debug.md` - debugging example
- `references/examples-architecture.md` - architecture decision example
- `references/advanced-techniques.md` - hypothesis testing and convergence
- `references/advanced-strategies.md` - uncertainty and revision handling
