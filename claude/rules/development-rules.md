# Development Rules

Engineering standards for this codebase. Model behavior — scope, delegation, verification,
output length, evidence — lives in `./.claude/rules/model-calibration.md` and is not
repeated here.

**IMPORTANT:** You ALWAYS follow these principles: **YAGNI (You Aren't Gonna Need It) - KISS (Keep It Simple, Stupid) - DRY (Don't Repeat Yourself)**

## General
- **File Naming**: Use kebab-case for file names with a meaningful name that describes the purpose of the file, doesn't matter if the file name is long, just make sure when LLMs read the file names while using Grep or other tools, they can understand the purpose of the file right away without reading the file content.
- **File Size Management**: Treat 200 lines as a prompt to inspect cohesion, not a hard target
  - Split large files only at real responsibility or reuse boundaries
  - Use composition over inheritance for complex widgets
  - Extract utility functions into separate modules
  - Create dedicated service classes for business logic
  - Do not split a cohesive file solely to satisfy a line count
- When looking for docs, use the `research` skill or web search for exploring latest docs.
- Use `gh` bash command to interact with Github features if needed
- **[IMPORTANT]** Follow the codebase structure and code standards in `./docs` during implementation.
- **[IMPORTANT]** Do not just simulate the implementation or mocking them, always implement the real code.

## Code Quality Guidelines
- Read and follow codebase structure and code standards in `./docs`
- Don't be too harsh on code linting, but **make sure there are no syntax errors and code are compilable**
- Prioritize functionality and readability over strict style enforcement and code formatting
- Use reasonable code quality standards that enhance developer productivity
- Use try catch error handling & cover security standards

## Code Implementation
- Write clean, readable, and maintainable code
- Follow established architectural patterns
- Implement features according to specifications
- Handle edge cases and error scenarios
- **DO NOT** create new enhanced files, update to the existing files directly.

## Code Comments and Artifact Naming — No Plan References

Code comments and file names (including SQL migrations) **must not reference plan
artifacts**: phase numbers, finding codes (F1, F13, Y1, CU2…), audit labels, red-team
labels, brainstorm sections (§5.4), or plan taxonomy.

**Why:** plan headers get renumbered or disappear, so the reference becomes unresolvable
noise. The *reason* for code (invariant, race, trade-off) must be stable and
self-contained.

- **Explain the why, not the origin.** Write "org-scoped advisory lock serializes concurrent reassigns" — NOT "per F13 advisory-lock fix".
- **Migration filenames:** domain slug only — `000003_polymorphic_permission_groups.up.sql` (NOT `000003_phase_0a_...`).
- **Test names:** describe the scenario — `TestReassignPrimaryDept_Concurrent` (NOT `_F13`).
- **Commit messages:** describe the change, not the finding code.
- Plan refs belong in `plans/…/phase-XX-*.md` and PR descriptions, not in code.
- Allowed in code: symbol names from the same codebase, and stable external IDs (RFC numbers, PostgreSQL SQLSTATE, CVE IDs, durable issue numbers).

## Pre-commit/Push Rules
- Run linting before commit
- Run tests before push (DO NOT ignore failed tests just to pass the build or github actions)
- Keep commits focused on the actual code changes
- **DO NOT** commit and push any confidential information (such as dotenv files, API keys, database credentials, etc.) to git repository!
- Create clean, professional commit messages without AI references. Use conventional commit format.

## Cross-Service Conventions (Polyrepo Fleet)

Apply these when this project is one service among several repos sharing a business (microservice fleet). Skip for standalone projects.

- **Contract-first**: Any change to an inter-service API starts in the contracts repo (OpenAPI/proto); implement in the service only after the contract is updated. Never invent or drift from a contract inside a service.
- **Structured logging**: JSON logs with a propagated correlation id (`X-Request-Id` or the fleet's equivalent) on every inter-service call; include it in error reports and diagnostics.
- **Consistent error envelope**: All services return errors in the same shape (code, message, details). Reuse the fleet's existing envelope — do not invent a new one per service.
- **Resilience defaults**: Every outbound inter-service call sets an explicit timeout and bounded retry with backoff; no unbounded retries.
- **Health endpoints**: Each service exposes liveness/readiness endpoints consistent with the rest of the fleet.
- **Mirror the golden service**: When in doubt about structure, middleware, or conventions, copy the fleet's reference ("golden") service instead of introducing a new pattern.

## Visual Aids

Use a visual only when it materially clarifies a multi-component relationship, flow, or state change.

- `/ck:preview --explain <topic>` for a visual explanation
- `/ck:preview --diagram <topic>` for architecture or data flow
- `/ck:preview --slides <topic>` for a step-by-step walkthrough
- `/ck:preview --ascii <topic>` for terminal-only output
- Add `--html` for a self-contained HTML artifact
- Visuals save to `{plan_dir}/visuals/` when a plan is active (see `## Plan Context` in the hook injection), otherwise `plans/visuals/`
