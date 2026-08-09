# Log Analysis Fix Workflow

Use logs as evidence for a root-cause trace, not as a substitute for reproducing or
reading the affected path.

## Workflow

1. Read the most recent relevant error window first, then expand around timestamps,
   request IDs, stack traces, or repeated signatures.
2. Identify the earliest causal event rather than fixing the final downstream
   exception.
3. Map the logged frames to code, inputs, environment, and direct dependents.
4. Reproduce the smallest failure locally or in a safe diagnostic environment when
   possible.
5. Implement the root-cause fix and collect one proportional evidence bundle:
   original repro/log signature, focused regression check, affected module checks,
   and final-diff inspection.

Work inline for a localized failure. Use tasks, a debugger, parallel exploration,
or an independent reviewer only when the incident is broad, uncertain, or high
risk. Add durable logging or update operating docs only when observability or
public runbook behavior genuinely changed.

If logs are missing, ask for them only when they cannot be obtained from the
authorized environment. Do not silently add permanent log piping to project
configuration.
