# Conditional Subagent Patterns

Subagents are optional specialists with independent deliverables. Do the work
inline when delegation would add coordination overhead without new evidence.
Small, clear work normally uses no subagents. Across ordinary cook workflows,
run no more than three workers concurrently.

## Delegation Gate

Delegate only when at least one condition holds:

- independent workstreams can proceed without overlapping ownership;
- a novel or version-sensitive question needs separate research;
- a broad/high-risk change benefits from independent domain evidence;
- a difficult test or diagnosis can run independently while implementation continues;
- the user explicitly requests parallel execution.

Do not create a planner → implementer → tester → reviewer → docs chain by
default. A worker should own a concrete artifact, file set, experiment, or review
lens. The lead remains responsible for integrating evidence and resolving conflicts.

## Agent Tool Pattern

```text
Agent(subagent_type="[type]", prompt="[bounded deliverable, scope, evidence]", description="[brief]")
```

Include file ownership and acceptance criteria in the prompt. In shared
checkouts, assume every worker can see live edits; assign disjoint files and tell
workers not to overwrite unrelated changes.

## Research

```text
Agent(
  subagent_type="researcher",
  prompt="Research [version-sensitive question] from primary sources. Return the decision-relevant facts and citations only.",
  description="Research [topic]")
```

- Use when local code and governing docs cannot answer the question.
- Parallelize only distinct questions; keep total concurrent fanout at three or less.
- Skip a separate status report unless findings change the approach or require a decision.

## Scout

```text
Agent(
  subagent_type="Explore",
  prompt="Locate [feature] touchpoints, tests, conventions, and contracts. Do not edit files.",
  description="Scout [feature]")
```

- Prefer targeted inline inspection for localized work.
- Use `/ck:scout ext` or an Explore worker only for broad discovery that can be
  usefully isolated.

## Planning

```text
Agent(
  subagent_type="planner",
  prompt="Create a durable implementation plan for [large/complex task] from [evidence]. Save it to [path].",
  description="Plan [feature]")
```

- Use only when a durable plan improves coordination, risk control, or resumability.
- Do not create plan artifacts for a small, clear change.

## Implementation

```text
Agent(
  subagent_type="general-purpose",
  prompt="Implement [bounded stream]. Own only [files]. Meet [acceptance criteria] and report checks run.",
  description="Implement [stream]")
```

- Use for independent sizeable streams, not every frontend task.
- Assign disjoint ownership; serialize work that shares files or contracts.
- Launch at most three ordinary workers at once.

## Testing and Debugging

```text
Agent(
  subagent_type="tester",
  prompt="Verify [behavior/risk surface] with [targeted commands]. Return failures with reproducible evidence.",
  description="Verify [surface]")
```

```text
Agent(
  subagent_type="debugger",
  prompt="Diagnose [specific failure] without broad edits. Return root cause and the smallest supported fix.",
  description="Diagnose [failure]")
```

- Run ordinary targeted checks inline.
- Delegate when verification is long-running, independent, difficult, or needs a
  distinct environment/domain lens.
- Require relevant tests to pass; do not claim a universal pass percentage when
  unrelated or unavailable suites remain.

## Review and Risk Validation

```text
Agent(
  subagent_type="code-reviewer",
  prompt="Review [bounded diff] against [acceptance criteria]. Check reachable regressions and public contracts. Report only evidenced blockers/warnings with file locations.",
  description="Review [risk surface]")
```

Delegate review for broad, difficult, high-risk, or ship-like changes. Otherwise
review the diff inline. Do not add another worker merely to verify the reviewer.
When the artifact workflow applies, write the result to `review-decision.json`
using `../../_shared/references/workflow-artifacts.md`.

### Adversarial Validation

```text
Agent(
  subagent_type="code-reviewer",
  prompt="Disprove the implementation claims for [phase]. Check acceptance coverage, regression reachability, contracts, and verification proof. Return JSON-ready decision, disprovenClaims[], unverifiedClaims[], missingProof[], reachableRegressions[].",
  description="Adversarially validate [phase]")
```

Trigger for a structured `--auto` workflow, high-risk surface, large diff, or
ship/push/PR/deploy action when it adds independent evidence. Do not average
reviewers; any evidenced critical issue blocks.

### Domain-Risk Review

```text
Agent(
  subagent_type="code-reviewer",
  prompt="Review [auth|secrets|payments|db|api|deploy|filesystem|production-config] risk in [scope]. Return evidence for risk-gate.json and blocking findings only.",
  description="Review domain risk")
```

Use only when touched files affect the named domain.

## Conditional Simplify

```text
Agent(
  subagent_type="code-simplifier",
  prompt="Simplify only [modified files] while preserving behavior and public contracts exactly.",
  description="Simplify recent edits")
```

Trigger only when the live diff breaches a configured simplify threshold. Compare
the scoped diff before and after; do not rely on the worker's prose summary.

## Finalization Specialists

- Activate `/ck:project-management` only when a plan/task artifact was actually
  used and needs reconciliation.
- Use `docs-manager` only when public behavior, setup, or operating instructions
  changed enough to require documentation.
- Use `git-manager` only when commit/publish is in the requested workflow and
  delegation has a bounded benefit; routine git operations can remain inline.
- Journal only noteworthy decisions that will help future work.

These activities are conditional deliverables, not a mandatory finalize fanout.

## Parallel Execution

```text
Agent(
  subagent_type="general-purpose",
  prompt="Implement [stream] with exclusive ownership of [files]. Do not alter other live changes.",
  description="Implement [stream]")
```

- Prove streams are independent before launching them.
- Declare file ownership and integration boundaries.
- Use at most three concurrent ordinary workers.
- Integrate and run one coherent verification bundle after the group returns.
