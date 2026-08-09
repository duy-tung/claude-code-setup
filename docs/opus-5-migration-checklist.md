# Claude Opus 5 Migration Checklist

Validated against Anthropic's official documentation on **2026-08-08**. This
document separates the two Opus 4.8 → 5 breaking changes from older API cleanup,
so migrations do not attribute pre-existing restrictions to Opus 5.

## Shipped baseline

| Setting | Kit default | Operational note |
|---|---|---|
| Model | `claude-opus-5` | Fixed ID for reproducible runs; `opus` is a moving alias |
| Claude Code | `2.1.219+` | Minimum version with Opus 5 support |
| Effort | `high` | Explicitly pinned because a prior user selection can carry over |
| Thinking | Adaptive, on by default | Prefer lower effort to disabling thinking |
| Context | 1M tokens, default and maximum | Account/provider access can still vary in Claude Code |
| Max output | 128K tokens | Thinking tokens count against `max_tokens` |
| Base API price | $5 input / $25 output per 1M tokens | Re-baseline cost with real workload traces |

The installable profile in `claude/settings.json` pins the model and persistent
effort. Confirm the resolved values in `/status`; custom gateways and Microsoft
Foundry can require deployment-specific model names.

## Runtime and rollout

- [ ] Run `claude --version`; update with `claude update` when older than
      `2.1.219`.
- [ ] Use the fixed `claude-opus-5` ID in production settings and evals. Use
      `opus` only when following the latest family release is intentional.
- [ ] Confirm the actual model and effort after launch, especially after changing
      models or reusing an existing session.
- [ ] Remove the retired 1M beta header. Opus 5 exposes 1M as its normal context
      window; there is no smaller Opus 5 context variant.
- [ ] Revisit context warnings, chunk sizes, compaction thresholds, and retrieval
      assumptions that were calibrated for 128K or 200K.
- [ ] Decide whether Claude Code's security-flag model fallback is acceptable for
      the workload. Record `modelUsage` in evals so a fallback cannot look like an
      Opus 5 result.

## Messages API: Opus 4.8 → 5

Anthropic identifies two breaking changes for this direct upgrade:

- [ ] If `thinking` is omitted, adaptive thinking is now **on**. Re-sweep
      `max_tokens`, because it covers both internal thinking and visible output.
- [ ] Do not combine `thinking: {"type": "disabled"}` with `xhigh` or `max`
      effort; the API rejects the request. Prefer thinking-on with lower effort.

Also validate model-specific behavior:

- [ ] Treat a classifier refusal as an HTTP 200 response with
      `stop_reason: "refusal"`; discard partial streamed output for that response.
- [ ] Do not request Messages API server-side Web Fetch or Priority Tier with
      Opus 5. This restriction does **not** remove Claude Code's own `WebFetch`
      tool or Managed Agents web fetch.
- [ ] When continuing on the same model, pass every `thinking` and
      `redacted_thinking` block back unchanged. When switching models, do not pass
      incompatible thinking blocks into the new request.

## Cumulative cleanup for kits coming from 4.6 or earlier

These are not new Opus 5 removals relative to Opus 4.8, but legacy integrations
still need to clean them up:

- [ ] Replace manual thinking budgets (`budget_tokens` / fixed
      `thinking.type = enabled`) with adaptive thinking and effort.
- [ ] Remove non-default `temperature`, `top_p`, and `top_k` parameters.
- [ ] Remove assistant prefills.
- [ ] Remove legacy context, effort, interleaved-thinking, and fine-grained
      streaming beta headers.
- [ ] Migrate deprecated `output_format` request fields to
      `output_config.format` where applicable.

## Prompt and workflow calibration

- [ ] State visible length and format explicitly. Lower effort does not reliably
      make answers shorter.
- [ ] Put a narrow scope boundary in review, refactor, and research prompts.
- [ ] Let small, clear changes use an inline plan and one proportional evidence
      bundle. Do not require plan files, journals, duplicate review passes, or
      verifier agents by default.
- [ ] Cap ordinary delegation. Give every worker an independent deliverable and
      require source paths, diffs, or command output in its report.
- [ ] Narrate only material corrections; silently fix harmless slips.
- [ ] Ask the user only when materially different interpretations would change
      the result, contract, risk, or external side effect.
- [ ] Never instruct the model not to think or reason. Disabled thinking can make
      tool syntax or internal XML appear as visible text.

## Agent Teams

- [ ] Use the current `Agent(...)` invocation and allowlist syntax. Keep legacy
      `Task(...)` handling only in compatibility parsers for older transcripts.
- [ ] Do not call retired `TeamCreate` or `TeamDelete`; current Claude Code creates
      a team on the first teammate spawn and cleans it up automatically.
- [ ] Send one direct message per recipient; there is no broadcast message type.
- [ ] Treat Agent Teams as a shared checkout, not implicit worktree isolation.
      Partition file ownership or use an explicit worktree process.
- [ ] Do not force every teammate onto Opus. Teammates can use different models;
      they inherit the lead's effort but not necessarily its model.
- [ ] Keep Agent Teams for parallel work with genuinely independent streams;
      use inline work or ordinary subagents for smaller tasks.

## Evaluation gate

- [ ] Record the requested model and effort plus `modelUsage`, turns, input/output
      tokens, cost, and latency for every live run.
- [ ] Fail a run when a fixed model was requested but `modelUsage` is missing or
      reports another model.
- [ ] Sweep `low`, `medium`, and `high` first. Add `xhigh` and session-only `max`
      for capability-critical tasks; do not assume one effort wins globally.
- [ ] Re-baseline token counts only where needed. Opus 4.8 and 5 use the same
      tokenizer; migrations from 4.6 or earlier can change tokenization.
- [ ] Include small-change, narrow-review, concise-final, and no-op/oracle harness
      tests so legacy over-planning and broken graders cannot pass silently.
- [ ] Protect visible grader tests from agent edits and count unrequested plan,
      report, journal, or summary artifacts against the task budget.

## Sources

- [Migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide)
- [What's new in Claude Opus 5](https://platform.claude.com/docs/en/about-claude/models/whats-new-opus-5)
- [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)
- [Claude Code model configuration](https://code.claude.com/docs/en/model-config)
- [Claude Code Agent Teams](https://code.claude.com/docs/en/agent-teams)
- [Claude Opus 5 System Card](https://www-cdn.anthropic.com/c5fbac3f0b1280a933ebd26d3cb8bb9f5bdeaf48/Claude%20Opus%205%20System%20Card.pdf)
