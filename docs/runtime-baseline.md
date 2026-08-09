# Runtime Baseline

What this kit expects from its runtime, and the constraints that produce errors if
violated. Behavior guidance lives in `claude/rules/model-calibration.md`; this file is
configuration and platform facts only.

Verified against Anthropic documentation on **2026-08-09**.

## Shipped defaults

| Setting | Value | Where it lives | Note |
|---|---|---|---|
| Model | `claude-opus-5` | `claude/settings.json` | Fixed ID for reproducible runs; `opus` is a moving alias |
| Effort | `high` | `claude/settings.json` | Pinned explicitly because a prior session's choice can carry over |
| Claude Code | `2.1.219+` | prerequisite | Below this, the `opus` alias resolves to an older model |
| Thinking | adaptive, on by default | model default | No `thinking` field is sent |
| Context | 1M tokens | model default | Both the default and the maximum; no beta header |
| Max output | 128K tokens | model default | Thinking tokens count against `max_tokens` |
| Base API price | $5 in / $25 out per 1M | — | Re-baseline cost with real workload traces |

Confirm the resolved model and effort with `/status`. Custom gateways and Microsoft
Foundry can require deployment-specific model names — see
[Claude Code model configuration](https://code.claude.com/docs/en/model-config).

## Hard constraints

These return errors or produce malformed output. They are not style preferences.

- **Disabled thinking is capped at `high` effort.** `thinking: {"type": "disabled"}`
  combined with `xhigh` or `max` returns a 400. Prefer thinking enabled at a lower effort
  over disabling it.
- **With thinking disabled**, tool calls can leak into visible text and internal XML tags
  can appear in output. Never instruct the model not to think or reason; that increases
  tag leakage.
- **No fixed thinking budgets.** `budget_tokens` and `thinking.type = "enabled"` are
  removed. Effort is the control.
- **No non-default `temperature`, `top_p`, or `top_k`**, and no assistant prefill.
- **Classifier refusals arrive as HTTP 200** with `stop_reason: "refusal"`. Discard
  partial output for that response rather than parsing it.
- **Same-model continuations must replay `thinking` and `redacted_thinking` blocks
  unchanged.** When switching models, strip them instead.
- **Not available:** Messages API server-side Web Fetch, and Priority Tier. This does not
  affect Claude Code's own `WebFetch` tool.

## Operational notes

- The 1M context window is a ceiling, not a target. Keep only task-relevant context and
  use runtime-reported utilization rather than filling the window.
- `max_tokens` covers thinking plus visible output. Revisit it for workloads tuned when
  thinking was off.
- Record `modelUsage` in every live eval run, so a silent fallback cannot be mistaken for
  a result from the pinned model. `eval/run.py` fails a run when a model was requested and
  `modelUsage` is missing or reports another one.
- Effort is worth sweeping on this repo's own evals before changing the baseline:
  `npm run eval:effort-sweep`. `low` and `medium` are the primary cost and latency
  controls wherever quality holds.

## Sources

- [Models overview and migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide)
- [Effort](https://platform.claude.com/docs/en/build-with-claude/effort)
- [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)
- [Claude Code model configuration](https://code.claude.com/docs/en/model-config)
- [Claude Code settings](https://code.claude.com/docs/en/settings)
