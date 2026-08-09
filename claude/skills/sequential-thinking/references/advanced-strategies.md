# Advanced Decision Strategies

## Decisions under uncertainty

Separate facts from assumptions and look for a robust choice:

| State | Evidence | Action |
|---|---|---|
| Verified | Requirement A is contractual | Reject options that violate A |
| Inferred | Traffic may double this year | Prefer reversible capacity choices |
| Unknown | Provider failure behavior | Run one failure-mode probe before committing |

If one missing fact changes the decision, ask for or measure that fact. Otherwise
make the safest reversible choice and label the inference.

## Cascading revision

When a foundational assumption changes:

1. state the new evidence;
2. list only downstream conclusions whose validity changed;
3. retain conclusions still supported independently;
4. recompute the decision from the corrected foundation;
5. summarize the resulting scope or risk change.

## Recover from a stalled analysis

If repeated inspection produces no new evidence, do not add more narrative.
Identify the missing discriminator, run the smallest relevant experiment, consult
an authoritative source, or report the concrete blocker.

## Multiple constraints

Build a constraint table and eliminate infeasible options:

| Option | Security | Latency | Operations | Viable |
|---|---:|---:|---:|---:|
| X | pass | fail | pass | no |
| Y | pass | pass | unknown | pending probe |
| Z | pass | pass | pass | yes |

Verify feasibility once at the relevant boundary. Revisit a constraint only when
new evidence or the requested scope changes it.
