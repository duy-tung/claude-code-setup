# Diagnosis Protocol

Diagnose from executable evidence and fix the cause rather than the visible
symptom. Scale the record to the failure: a lint error needs a command and line;
a production incident needs a durable evidence chain.

## 1. Capture the Baseline

Capture the smallest useful pre-fix state:

- exact error, failed assertion, or observed behavior;
- command/input/environment needed to reproduce it;
- expected versus actual behavior;
- relevant stack or log context;
- recent changes only when timing or regression history matters.

The baseline becomes the first item in the final evidence bundle.

## 2. Observe and Hypothesize

Read the failing path before editing. Identify where the symptom appears, its
direct callers and inputs, and the nearest relevant tests or contracts.

For each plausible cause, state:

1. the hypothesis;
2. evidence that would confirm or refute it;
3. the cheapest discriminating check.

Common categories include a recent regression, invalid state or data shape,
environment mismatch, missing boundary validation, race/timing behavior, and an
incorrect contract assumption.

## 3. Test and Trace

Test hypotheses in the cheapest useful order. Delegate independent hypotheses only
when they touch separate surfaces and can run without duplicating context.

Classify each result as:

- `verified`: direct code or executable evidence confirms it;
- `inferred`: evidence supports it but a direct check is unavailable;
- `unknown`: more evidence is required.

Trace backward until the change point is the original defect:

```text
symptom <- immediate trigger <- invalid state/contract <- root cause
```

Do not stop at a downstream guard if the invalid state should instead be prevented
at its source.

## 4. Escalate Deliberately

When two hypotheses fail, revisit assumptions, broaden the inspected surface, and
consider environment, scale, timing, or concurrency. Structured reasoning tools
can help here, but are not mandatory for an obvious local failure.

After three failed fix attempts, stop changing code and discuss whether the
architecture, reproduction, or intended contract is wrong.

Ask the user only when missing information changes a material scope, contract, or
authority decision and cannot be learned locally.

## Diagnosis Summary

For moderate/deep work, record:

```markdown
Root cause: [specific defect and location]
Evidence: [verified / inferred / unknown observations]
Reproduction: [command or steps]
Blast radius: [demonstrated callers, contracts, and tests]
Fix direction: [smallest change addressing the cause]
Prevention: [valuable regression check or guard]
```

For quick work, the same content may be one concise paragraph; no separate report
artifact is required.
