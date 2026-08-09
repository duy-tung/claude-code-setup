# Quick Workflow

Use an inline scout → diagnose → fix → verify cycle for a deterministic,
low-risk issue. No plan artifact, task tree, or mode question is needed.

## 1. Targeted Scout and Diagnosis

In one short pass:

1. Capture the smallest reproducible failure, including the exact command or
   observable symptom.
2. Locate the failing line, its local convention, and the nearest relevant check.
3. Trace far enough to confirm the cause rather than patching the displayed
   symptom.
4. Note direct dependents only when the changed contract or behavior reaches them.

Use direct reads and searches by default. Activate `ck:debug` or delegate only if
the failure stops being quick or competing hypotheses emerge.

## 2. Fix

- Make the smallest coherent change that addresses the confirmed root cause.
- Preserve public contracts unless the request explicitly changes one.
- Follow the local pattern and avoid opportunistic cleanup.
- If evidence reveals a broader or riskier surface, reclassify to Standard or Deep.

## 3. Proportional Evidence Bundle

Run one coherent set of checks inline:

1. Re-run the original repro or the closest executable equivalent.
2. Run the narrowest relevant regression test, typecheck, lint, or build check.
3. Inspect the final diff and direct dependents for unintended contract changes.
4. Add a regression test or guard when it has lasting value; a deterministic
   compiler/linter check can itself be the regression proof.

Do not launch separate Bash or reviewer agents for routine quick fixes. Use an
independent reviewer only if the change becomes broad, difficult to reason about,
or high risk.

## 4. Report

Report the root cause, changed files, fresh checks, and remaining risk. Label
claims `verified`, `inferred`, or `unknown`; do not provide a confidence score.

Sync an existing plan only if one already owns the fix. Update documentation only
for changed public behavior or operating instructions. Journal only a noteworthy
technical decision. Ask before commit/push/deploy unless authority was already
granted.
