# Mode Selection

Infer the lightest safe mode from the request and the initial evidence. Do not ask
the user to choose a workflow merely because several modes exist.

## Routing

| Evidence | Mode | Behavior |
|----------|------|----------|
| Deterministic local failure, small blast radius | Quick | Scout, diagnose, edit, and check inline |
| Multi-file or uncertain root cause | Autonomous/Standard | Track the work when useful; broaden checks across the demonstrated blast radius |
| Production-critical, security-sensitive, destructive, or architectural | Human-in-the-loop/Deep | Use explicit checkpoints, durable evidence, and independent review |
| Two or more truly independent issues | Parallel | Split by issue only when workers will not duplicate context or edit the same surface |

An explicit `--quick`, `--review`, `--auto`, or `--parallel` request overrides the
inferred mode unless doing so would be unsafe.

## When to Ask

Ask one focused question only when the answer changes a material choice that
cannot be discovered locally, such as:

- whether a public contract may change;
- which of two mutually exclusive scopes is intended;
- whether destructive, external, commit, push, or deploy authority is granted;
- whether a known regression may be accepted.

State the evidence and concrete consequences of each option. Otherwise choose the
conservative, reversible path and continue.

When a material choice is required, keep the question focused:

```text
Evidence: [what was verified and what remains unknown]
Decision: [the single scope/contract/authority choice]
Options:
- [conservative option] — [consequence]
- [alternative option] — [consequence]
```

## Evidence State

Describe conclusions as `verified`, `inferred`, or `unknown`. Do not use numeric
confidence scores as approval gates.
