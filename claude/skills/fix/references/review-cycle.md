# Review Cycle

Review depth follows change risk. Executable evidence and concrete findings—not a
numeric score—determine whether a fix is ready.

## Quick and Routine Standard Fixes

Review the final diff inline as part of the proportional evidence bundle:

- does it address the confirmed root cause and acceptance criteria;
- are public contracts preserved or intentionally changed;
- do direct dependents remain compatible;
- is unrelated scope excluded;
- do the fresh repro and targeted checks support the conclusion.

No reviewer subagent or workflow artifact is required for a small, low-risk diff.

## Broad or High-Risk Fixes

Use one independent reviewer when the change is broad, difficult to reason about,
security-sensitive, data-risking, migration-heavy, or production-critical. Add a
domain/adversarial reviewer only for a separate material risk.

Produce artifacts from `../../_shared/references/workflow-artifacts.md` only when a
CI/release gate, requested audit trail, or high-risk approval consumes them. In
that case, run:

```bash
node claude/hooks/workflow-artifact-gate.cjs --stage finalize --artifact-dir <artifact-dir>
```

The artifact bundle may include context, risk, verification, review, and
adversarial-validation records as required by that gate. Do not manufacture all
artifacts for routine local fixes.

## Handling Findings

1. Repair a verified, in-scope, reversible defect.
2. Re-run the original repro and affected checks after a repair.
3. Ask the user only when the finding creates a material scope/contract choice,
   needs new authority, or requires accepting a known regression.
4. Stop and report after three failed repair cycles rather than looping.

Always block unresolved data-loss risk, exploitable security defects, unauthorized
breaking changes, or missing proof that the original symptom is fixed. Label
review conclusions `verified`, `inferred`, or `unknown`.
