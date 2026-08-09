# Advanced Evidence Techniques

## Spiral refinement

Start with the smallest decision model that can work. Add a constraint only when
source evidence, a failing check, or a contract requires it. Re-evaluate the
affected conclusion, not the entire problem by default.

## Hypothesis testing

For each plausible cause, specify:

- predicted observation if true;
- cheapest check that distinguishes it from alternatives;
- observed result and evidence location;
- disposition: verified, refuted, or still unknown.

Stop testing a refuted hypothesis unless later evidence invalidates the check.

## Alternative convergence

Compare independent options first, then consider a hybrid only when it preserves
verified advantages without combining their major costs. A hybrid is not
automatically safer or more complete.

## System decomposition

Decompose by contracts or independently testable boundaries. Track only
interactions that affect the requested outcome. When an interaction changes a
local conclusion, revise that conclusion and its consumers rather than expanding
to unrelated components.

## Evidence sufficiency

A decision is ready when:

- the success condition is explicit;
- material claims are verified or clearly labeled as inferred;
- no unresolved unknown can reverse the choice without a stated next check;
- the chosen action fits the requested scope and authority.
