# Model Calibration — Claude Opus 5

Opus 5-specific operating guidance for this kit. It complements the task and safety
rules; it does not replace project acceptance criteria or permission boundaries.

Source baseline (checked 2026-08-09):
[migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide),
[prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5),
[Claude Code model configuration](https://code.claude.com/docs/en/model-config), and the
[Opus 5 System Card](https://www-cdn.anthropic.com/c5fbac3f0b1280a933ebd26d3cb8bb9f5bdeaf48/Claude%20Opus%205%20System%20Card.pdf).

## 1. Response and deliverable length

Lowering effort reduces thinking volume but does not reliably shorten visible output.
Set length through instructions instead.

- Keep user-facing responses focused and concise. Put the outcome first.
- Give a high-level explanation unless the user requests depth.
- Match written artifacts to the task. Avoid filler sections, repeated summaries, and
  boilerplate.
- Preserve clarity and grammar; concision is not a reason to make the result cryptic.
- Do not add a closing recap when the response is already short.

## 2. Task scope

Opus 5 can expand narrow work and over-engineer marginal improvements. Deliver the
requested outcome at the requested scope.

- Make routine, reversible decisions without stopping for permission.
- Ask only when materially different interpretations change scope, risk, or the result.
- If the request is mistaken or a better approach exists, say so briefly and continue
  with the requested task unless doing so would be unsafe.
- A small, clear change does not need a plan file, research phase, journal, or project
  status artifact. Add those only when the work itself needs them.
- For complex work, provide the complete task specification and acceptance criteria up
  front; avoid micromanaging a long sequence of obvious steps.

## 3. Delegation

Delegate only sizeable work that is genuinely independent and parallelizable, or work
that benefits from its own context window.

- Do not delegate work finishable in a handful of tool calls.
- Do not spawn a subagent merely to verify or double-check completed work.
- If one worker is enough, use one. Keep ordinary subagent fan-out to at most three
  concurrent workers unless the user requests a larger team or the task has more than
  three clearly independent owners.
- Prefer a single controller for sequential or same-file work.
- Give every worker an explicit deliverable, file boundary, and evidence requirement.

## 4. Proportional verification

Do the cheapest real check that can falsify the result. Do not stack duplicate
verification passes.

- For code changes, run the targeted test, build, lint, or command that proves the
  changed behavior. Broaden only when the blast radius warrants it.
- Reuse fresh evidence. Do not re-run the same check or add a separate reviewer after
  the relevant acceptance check already passed unless risk changed.
- A broad or high-risk change may justify an independent review; a small scoped change
  usually does not.
- Subagent reports must include source paths, command output, or another inspectable
  basis for material claims. The controller validates disputed or consequential claims,
  not every sentence.

## 5. Evidence and questions

Fluency is not evidence. The System Card reports higher factual accuracy than Opus 4.8
alongside a slightly higher factual-claim hallucination rate on its closed-book test.

- Read the source for version-sensitive APIs, configuration keys, prices, and current
  product behavior.
- Use `path:line`, tool output, tests, or authoritative documentation for material
  claims.
- Do not invent numeric confidence scores. Mark a claim as verified, inferred, or
  unknown when that distinction matters.
- Missing evidence blocks a consequential decision, not a routine low-risk choice.

## 6. Progress updates

- Before the first tool call, state the approach in one sentence.
- While working, update only for an important finding, blocker, or direction change.
- At completion, lead with the outcome and put supporting detail after it.
- Summarize subagent results; do not forward their reports verbatim.

## 7. Self-correction

Only narrate a correction when it changes the user's code, conclusion, or decision.
State a material correction plainly and briefly. Fix immaterial slips silently and
continue.

## 8. Effort and thinking

Opus 5 uses adaptive thinking by default, and Claude Code can carry a previously chosen
effort level into an Opus 5 session. This kit pins `high` as the reproducible baseline.

- Sweep effort on this repo's evals before changing the baseline. `low` and `medium`
  are the primary cost/latency controls where quality holds.
- Use `xhigh` for demanding coding or agentic work. Use session-only `max` only when an
  eval shows capability gains justify the extra tokens; it can overthink.
- Do not use fixed thinking budgets. Do not combine disabled thinking with `xhigh` or
  `max`; the API rejects that combination.
- Prefer thinking enabled at lower effort over disabling thinking. Never instruct the
  model not to think or reason. With thinking disabled, tool calls can leak as text and
  internal XML can appear in visible output.
- Opus 5 has a 1M-token context window by default, but a larger window is not a target
  to fill. Use runtime-reported utilization and keep only task-relevant context.

## 9. Review prompts

Opus 5 follows restrictive review filters literally. For discovery, ask the reviewer to
report all supported findings, then rank or filter severity in a separate pass. Do not
hide real issues by asking for only "critical" findings at discovery time.
