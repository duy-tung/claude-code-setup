# Prevention Gate

Add the narrowest durable protection that is valuable for the diagnosed bug class.
Prevention is proportional; do not add ceremony or unrelated defensive layers.

## Choose the Useful Protection

| Root cause | Useful protection |
|------------|-------------------|
| Behavior regression | Focused test that fails before and passes after the fix |
| Type or lint defect | The relevant compiler/linter check; add a runtime test only if behavior also matters |
| Invalid external input | Boundary validation and a focused invalid-input test |
| Wrong internal state/contract | Type/contract guard at the earliest correct boundary |
| Environment-sensitive operation | Explicit environment guard or startup validation |
| Hard-to-observe incident | Targeted diagnostic context without noisy permanent logging |
| External dependency failure | Timeout, bounded retry, fallback, or explicit error as the contract requires |

A regression test is strongly preferred when it can distinguish the defect and
has lasting value. When no suitable harness exists, use the closest executable
check and report that limitation as `unknown` or residual risk; do not create an
arbitrary assertion merely to satisfy a checkbox.

## Proportional Evidence Bundle

Before completion, collect one coherent bundle:

- the exact pre-fix repro or closest executable equivalent rerun fresh;
- a before/after result;
- focused regression coverage or the relevant deterministic type/lint check;
- checks for the demonstrated blast radius and direct contracts;
- applicable lint/type/build checks at the narrowest meaningful scope;
- final-diff inspection for unrelated changes and side effects.

Broaden checks for shared contracts, cross-module behavior, or high-risk changes.
Parallelize only long independent checks. Generate `verification.json` or review
artifacts only when a selected workflow/CI gate consumes them.

## Evidence Summary

```markdown
Root cause protection: [test/guard/check and why]
Verified: [fresh commands and results]
Inferred: [supported conclusions without a direct executable check]
Unknown: [unverified surface or residual risk]
```

If verification reveals a clear in-scope reversible regression, repair it and
rerun the bundle. Ask the user only for a material scope, contract, authority, or
regression-acceptance choice.
