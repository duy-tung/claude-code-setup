# Complexity Assessment

Classify issue complexity before routing to workflow. Assessment happens AFTER Step 1 (Scout) and Step 2 (Diagnose).

## Classification Criteria

### Simple (→ workflow-quick.md) — No Tasks

**Indicators:**
- Single file affected
- Clear error message (type error, syntax, lint)
- Keywords: `type`, `typescript`, `tsc`, `lint`, `eslint`, `syntax`
- Obvious fix location
- Root cause confirmed by diagnosis (not assumed)

**Task usage:** Skip. < 3 steps, overhead exceeds benefit.

**Examples:**
- "Fix type error in auth.ts"
- "ESLint errors after upgrade"
- "Syntax error in config file"

### Moderate (→ workflow-standard.md) — Tasks When Useful

**Indicators:**
- 2-5 files affected
- Root cause identified but fix spans multiple files
- Needs investigation to confirm diagnosis
- Keywords: `bug`, `broken`, `not working`, `fails sometimes`
- Test failures with root cause traced

**Task usage:** Use a small task list when the work spans meaningful phases,
owners, or handoffs. Keep a straightforward multi-file fix inline when tracking
would add no value. See `references/task-orchestration.md`.

**Examples:**
- "Login sometimes fails"
- "API returns wrong data"
- "Component not rendering correctly"

### Complex (→ workflow-deep.md) — Durable Coordination

**Indicators:**
- System-wide impact (5+ files)
- Architecture decision needed
- Research required for solution
- Keywords: `architecture`, `refactor`, `system-wide`, `design issue`
- Performance/security vulnerabilities
- Multiple interacting components
- Root cause spans multiple layers/modules

**Task usage:** Create a dependency graph for the phases and owners the incident
actually needs. Parallelize bounded investigation only when work is independent.
See `references/task-orchestration.md`.

**Examples:**
- "Memory leak in production"
- "Database deadlocks under load"
- "Security vulnerability in auth flow"

### Parallel (→ multiple general-purpose agents) — Use Task Trees

**Triggers:**
- `--parallel` flag explicitly passed (activate parallel routing regardless of auto-classification)

**Indicators:**
- 2+ independent issues mentioned
- Issues in different areas (frontend + backend, auth + payments)
- No dependencies between issues
- Keywords: list of issues, "and", "also", multiple error types

**Task usage:** Create separate issue owners or task trees only for independent
surfaces, plus one integration check. See `references/task-orchestration.md`.

**Examples:**
- "Fix type errors AND update UI styling"
- "Auth bug + payment integration issue"
- "3 different test failures in unrelated modules"
