---
name: ck:research
description: "Research bounded technical questions with citations. Use for technology evaluation, external behavior, architecture decisions, and implementation constraints."
user-invocable: true
when_to_use: "Invoke when current or external technical evidence is needed before a decision or implementation."
category: utilities
keywords: [research, evaluation, analysis, solutions]
license: MIT
argument-hint: "[topic]"
metadata:
  author: claudekit
  version: "1.1.0"
---

# Research

Answer the assigned technical question with current, cited evidence. Stay within
the requested scope; do not turn a narrow lookup into a general technology survey.

## 1. Define the Decision

Extract:

- the question or decision the research must support;
- project/user constraints and options already in scope;
- recency and source-authority requirements;
- the smallest set of claims that would change the outcome.

Ask one focused question only when missing information would materially change the
research direction. Otherwise make a conservative assumption and state it.

## 2. Gather Proportional Evidence

Prefer primary sources: official documentation, specifications, release notes,
maintainer repositories, and first-party advisories. A primary source can support
a direct stable fact; triangulate recommendations, disputed claims, and material
benchmarks with independent evidence.

Use no more than five research tool calls, and fewer when the answer is already
supported. Search independent queries in parallel only when it saves time without
duplicating the same question.

### Optional Gemini CLI

Read `.claude/.ck.json` or `~/.claude/.ck.json`:

- `skills.research.useGemini` defaults to `false`;
- `gemini.model` defaults to `gemini-3-flash-preview`.

When enabled, validate the CLI first:

```bash
command -v gemini >/dev/null 2>&1 && cd /tmp && timeout 15 gemini -y -m <gemini.model> --prompt "ping" >/dev/null 2>&1
```

Run successful research from a temporary directory to avoid project-local
instruction interception:

```bash
cd /tmp && timeout 180 gemini -y -m <gemini.model> --prompt "<bounded question>" 2>&1
```

Fall back to WebSearch when validation fails, the command exits non-zero, or output
contains `GaxiosError`, `RESOURCE_EXHAUSTED`, `MODEL_CAPACITY_EXHAUSTED`,
`PERMISSION_DENIED`, or `UNAUTHENTICATED`. State the fallback briefly.

## 3. Evaluate

For each material claim:

- assess source authority and publication/version date;
- distinguish documented facts from inference;
- note conflicts, deprecations, compatibility constraints, and adoption risk only
  when they affect the requested decision;
- compare only the options and dimensions in scope;
- avoid unsupported benchmark or popularity conclusions.

Use these evidence labels:

- `verified`: directly supported by cited primary or executable evidence;
- `inferred`: a reasoned conclusion from the cited evidence;
- `unknown`: evidence is unavailable, conflicting, or outside the research budget.

Provide a concise reasoning summary, not private chain-of-thought or confidence
scores.

## 4. Output

Return a concise cited answer inline by default. Create a markdown report only when
the user requests an artifact or a multi-session/multi-owner handoff will consume
one. If required, use the `Report:` path from the injected `## Naming` section;
otherwise do not ask for a path.

Use only applicable sections:

```markdown
# Research: [Question]

## Recommendation or Answer
[Direct conclusion]

## Material Evidence
- [Verified/inferred claim with citation]

## Trade-offs
[Only decision-relevant comparisons]

## Unknowns and Limits
[Residual uncertainty]

## Sources
- [Descriptive link]
```

Include the research date when freshness matters. Add code, diagrams, security
advisories, compatibility matrices, or implementation steps only when requested or
necessary to support the decision.

Write concise, clear, grammatical output. Do not implement code or expand the
requested deliverable into adjacent research.
