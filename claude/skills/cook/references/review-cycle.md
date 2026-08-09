# Risk-Calibrated Review Cycle

Review is an evidence activity, not a mandatory subagent or human-approval phase.
Small, clear work is reviewed inline through the proportional verification bundle.
Use the structured cycle below only when breadth, difficulty, risk, an explicit
workflow flag, or a ship-like action justifies durable review evidence.

Shared artifact contract: `../../_shared/references/workflow-artifacts.md`.

## When Review Artifacts Apply

Create/update the artifact bundle when an `--auto` structured workflow, a
large/high-risk change, or a finalize/commit/ship/push/PR/deploy workflow relies
on the artifact gate:

- `context-snippets.json`
- `risk-gate.json`
- `verification.json`
- `review-decision.json`
- `adversarial-validation.json` for auto, high-risk, large-diff, or ship-like work

Artifact directory:

- Plan workflow: `plans/<plan-dir>/reports/harness/`
- No-plan structured workflow: `plans/reports/harness/<timestamp-slug>/`
- Active pointer: `.claude/workflow-artifacts.json`

Do not create this bundle for a small inline change merely to satisfy ceremony.
When the bundle applies, validate it with:

```bash
node claude/hooks/workflow-artifact-gate.cjs --stage finalize --artifact-dir <artifact-dir>
```

## Risk Triggers

| Trigger | Additional evidence |
|---|---|
| `--auto` structured workflow | Adversarial validation before artifact-gated finalize |
| Auth, secrets, payments | Domain-risk review |
| DB schema or migration | Domain-risk review and rollback evidence |
| Public API or exported contract | Compatibility review |
| CI, deploy, release, production config | Operational-risk review |
| Destructive filesystem operation | Target and recovery validation |
| Large diff or ship/push/PR/deploy | Adversarial validation when it adds independent evidence |

No vote or numeric score overrides an evidenced critical issue. Findings must be
tied to observable behavior, file/line evidence, or a missing verification step.

## Structured Interactive Cycle (maximum 3 fix cycles)

```text
cycle = 0
LOOP:
  1. Review inline, or delegate one independent reviewer when risk/breadth warrants it.
  2. If a risk trigger exists, obtain the matching adversarial/domain evidence.
  3. If this workflow uses artifacts, update them and run the validator.
  4. Fix clear, in-scope, reversible blockers and re-run the affected checks.
  5. Continue autonomously when evidence passes and no material choice remains.
  6. Ask the user only when:
     - a blocking fix changes scope or a public contract,
     - authority is needed for an external/high-risk effect,
     - alternatives materially change behavior, risk, or cost, or
     - three fix cycles leave an unresolved blocker.
```

Do not stop after research, planning, implementation, testing, or review solely
because a phase ended. `--interactive` may add a checkpoint the user explicitly
requested, but routine phase approvals remain unnecessary.

## Auto-Handling Cycle

```text
cycle = 0
LOOP:
  1. Produce verification and risk evidence.
  2. Add independent/adversarial review only when triggered.
  3. Update artifacts and run the validator.

  4. IF risk-gate.autoStopRequired == true AND humanApproved != true:
       STOP before the high-risk finalize/commit/ship effect and ask for approval.

  5. IF review-decision.decision == PASS
       AND validator passes
       AND risk-gate.autoStopRequired == false:
       PROCEED.

  6. ELSE IF a clear in-scope blocker exists AND cycle < 3:
       fix it, re-run the affected evidence, increment cycle, and repeat.

  7. ELSE:
       ask the user for the material decision or additional authority required.
```

## Adversarial Validator Prompt

```text
Disprove implementation claims for <phase>.
Scope: correctness, acceptance coverage, regression reachability, contracts.
Forbidden: style polish, broad rewrites, preference-only feedback.
Return JSON-ready fields:
- decision: PASS | PASS_WITH_RISK | BLOCKED
- disprovenClaims[]
- unverifiedClaims[]
- missingProof[]
- reachableRegressions[]
```

## Output Formats

- Inline: `Step 5: Inline review complete - relevant evidence passed`
- Fixed: `Step 5: Fixed [N] blockers - affected checks passed`
- Auto: `Step 5: Review PASS - artifact validator passed - continuing`
- High risk: `Step 5: High-risk effect requires approval before finalize`

Report verified facts, reasoned inferences, and remaining unknowns directly.
Do not convert them into a numeric confidence score.
