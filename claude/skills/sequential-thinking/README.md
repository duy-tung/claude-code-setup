# Structured Analysis Skill

This skill provides an evidence-driven method for difficult decisions without
requesting or displaying private chain-of-thought.

## What it does

- separates verified facts, inferences, and unknowns;
- compares viable alternatives against decision-relevant criteria;
- tests competing hypotheses with the cheapest discriminating evidence;
- records material revisions when new evidence changes a conclusion;
- returns a concise conclusion and any decisive next check.

Use it only when complexity, uncertainty, or dependent decisions justify more
structure than direct inspection. Small deterministic tasks stay inline.

## Files

- `SKILL.md` — activation criteria, process, and output contract
- `references/core-patterns.md` — revision and alternative-comparison patterns
- `references/advanced-techniques.md` — hypothesis and convergence techniques
- `references/advanced-strategies.md` — uncertainty and constraint handling
- `references/examples-*.md` — concise worked evidence summaries
- `scripts/` and `tests/` — legacy deterministic formatting utilities retained
  for consumers that store user-authored analysis records

The skill does not invoke the legacy scripts to expose model reasoning. If a
consumer uses them, pass only user-authored labels, evidence, or decision notes;
never use them to persist or display hidden reasoning.

## Output contract

```markdown
Conclusion: [decision]
Evidence: [decisive verified facts]
Reasoning summary: [brief link from evidence to conclusion]
Trade-offs: [material alternatives]
Unknowns / next check: [only what could change the decision]
```

Stop when the requested decision has sufficient evidence. Do not add artificial
depth, repeated self-checks, or numeric confidence scores.
