# Intent and Scale Detection

Classify scale before selecting a workflow mode. The scale gate in
`../SKILL.md` takes precedence over keyword routing.

## Detection Algorithm

```text
FUNCTION detectWorkflow(input, scoutSignals):
  flags = parseExplicitFlags(input)
  IF flags conflict: resolve by explicit user priority or ask only if the
                     difference materially changes behavior or risk

  IF input points to plan.md or phase-*.md:
    mode = "code"
  ELSE IF flags contains --interactive: mode = "interactive"
  ELSE IF flags contains --fast:        mode = "fast"
  ELSE IF flags contains --parallel:    mode = "parallel"
  ELSE IF flags contains --auto:        mode = "auto"
  ELSE IF flags contains --no-test:     mode = "no-test"
  ELSE:
    mode = inferModeFromIntent(input)

  scale = classifyScale(input, scoutSignals)
  IF scale == "small-clear":
    RETURN {mode: "proportional", path: "inline", composableFlags: flags}

  IF mode == "parallel":
    workstreams = identifyIndependentWorkstreams(input, scoutSignals)
    IF count(workstreams) < 2: mode = "proportional"
    ELSE: fanout = min(count(workstreams), 3)

  RETURN {mode, path: "structured", composableFlags: flags}
```

`--tdd` composes with any mode and does not select a mode. `--no-test` records an
evidence gap; it does not waive type/build checks needed to establish that the
changed code is usable.

## Scale Signals

| Scale | Typical signals | Workflow consequence |
|---|---|---|
| Small and clear | Localized change, known contract, routine reversible choices | Targeted inspect, inline intent, implementation, one proportional evidence bundle |
| Standard | Multiple touchpoints, non-obvious contract, useful resumability | Short plan, targeted research/testing, conditional delegation |
| Large/high-risk | Public API/schema, auth/secrets/payments, destructive action, deploy/release, broad migration | Durable plan and evidence, risk-specific review, material human gates |

Feature count is only a routing signal. Three closely related edits can remain
one inline or sequential change; three genuinely independent workstreams may use
parallel mode. Never exceed three ordinary concurrent workers.

## Intent Signals

After scale classification, use these signals:

1. Explicit flags (`--interactive`, `--fast`, `--parallel`, `--auto`,
   `--no-test`) override inferred mode.
2. A current plan path selects `code` mode.
3. “fast”, “quick”, or “rapidly” suggests `fast`.
4. “trust me”, “auto”, “yolo”, or “just do it” suggests `auto`, but never
   bypasses a high-risk external-effect gate.
5. “no test”, “skip test”, or “without test” selects `no-test`.
6. “parallel”, or three or more independent deliverables, suggests `parallel`.
7. Otherwise select `proportional`.

## Mode Behaviors

| Mode | Research | Testing | Human checkpoint | Parallel execution |
|---|---|---|---|---|
| proportional | When uncertainty warrants it | Proportional | Material decisions only | No by default |
| interactive | Conditional | Proportional | Material decisions plus checkpoints explicitly requested by the user | No by default |
| auto | Conditional | Proportional | High-risk external effects, contract choices, or a blocking evidence gap | Up to 3 independent workers |
| fast | Skip broad research | Targeted | Material decisions only | No by default |
| parallel | Conditional | Proportional | Material decisions only | Up to 3 independent workers |
| no-test | Conditional | Skipped as requested; report gap | Material decisions only | Only if independently useful |
| code | Use current plan evidence | Per plan and risk | Material deviations only | Per plan, capped at 3 workers |

A completed phase is not itself a reason to ask for approval. Routine,
reversible decisions should be inferred from the request, nearby code, and
existing conventions.

## Examples

```text
"/ck:cook rename the local helper and update its unit test"
-> Scale: small-clear; inline proportional flow

"/ck:cook implement user auth --interactive"
-> Structured interactive flow; checkpoints only for material choices

"/ck:cook plans/260120-auth/phase-02-api.md"
-> Code mode; execute the current plan without re-planning ceremony

"/ck:cook implement auth, payments, notifications, shipping --parallel"
-> Parallel mode if scout confirms independent streams; maximum fanout 3

"/ck:cook implement everything --auto"
-> Auto mode; low-risk artifact-validated steps continue, high-risk effects stop

"/ck:cook refactor auth middleware --tdd"
-> Proportional mode with tests-first behavior
```

## Conflict Resolution

Use this priority:

1. Explicit user instruction and compatible flags
2. Safety and authorization boundaries
3. Current plan path
4. Scale classification
5. Intent keywords
6. Proportional default

Ask the user only when resolving a conflict would materially change observable
behavior, public contracts, risk, cost, or external side effects.
