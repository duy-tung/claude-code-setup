# Development Rules

**IMPORTANT:** Activate a skill only when its workflow materially helps the task;
small scoped work can proceed directly.
**IMPORTANT:** You ALWAYS follow these principles: **YAGNI (You Aren't Gonna Need It) - KISS (Keep It Simple, Stupid) - DRY (Don't Repeat Yourself)**

## Working With the Model

- **Act when ready.** Once you have enough information to act, act — don't keep re-planning or produce a plan-only response when implementation was requested.
- **Match the requested action.** Diagnose/explain/status requests are read-only. Fix/change/build requests include implementation after the minimum diagnosis needed to act; do not stop for redundant approval.
- **Grounded progress.** Before claiming something works or is complete, verify against actual tool output (tests run, files changed). Report partial completion as partial.
- **Small decisions don't need permission.** For minor ambiguous choices, pick the reasonable option and note it; ask only when the decision changes scope or is hard to reverse.

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
- Use `sequential-thinking` and `debug` skills for sequential thinking, analyzing code, debugging, etc. if needed
- **[IMPORTANT]** Follow the codebase structure and code standards in `./docs` during implementation.
- **[IMPORTANT]** Do not just simulate the implementation or mocking them, always implement the real code.

## Code Quality Guidelines
- Read and follow codebase structure and code standards in `./docs`
- Don't be too harsh on code linting, but **make sure there are no syntax errors and code are compilable**
- Prioritize functionality and readability over strict style enforcement and code formatting
- Use reasonable code quality standards that enhance developer productivity
- Use try catch error handling & cover security standards
- Inspect the final diff inline. Delegate an independent review only when size, risk, or unfamiliarity meets the gate in `./.claude/rules/primary-workflow.md`.

## Pre-commit/Push Rules
- Run linting before commit
- Run tests before push (DO NOT ignore failed tests just to pass the build or github actions)
- Keep commits focused on the actual code changes
- **DO NOT** commit and push any confidential information (such as dotenv files, API keys, database credentials, etc.) to git repository!
- Create clean, professional commit messages without AI references. Use conventional commit format.

## Code Implementation
- Write clean, readable, and maintainable code
- Follow established architectural patterns
- Implement features according to specifications
- Handle edge cases and error scenarios
- **DO NOT** create new enhanced files, update to the existing files directly.

## Cross-Service Conventions (Polyrepo Fleet)

Apply these when this project is one service among several repos sharing a business (microservice fleet). Skip for standalone projects.

- **Contract-first**: Any change to an inter-service API starts in the contracts repo (OpenAPI/proto); implement in the service only after the contract is updated. Never invent or drift from a contract inside a service.
- **Structured logging**: JSON logs with a propagated correlation id (`X-Request-Id` or the fleet's equivalent) on every inter-service call; include it in error reports and diagnostics.
- **Consistent error envelope**: All services return errors in the same shape (code, message, details). Reuse the fleet's existing envelope — do not invent a new one per service.
- **Resilience defaults**: Every outbound inter-service call sets an explicit timeout and bounded retry with backoff; no unbounded retries.
- **Health endpoints**: Each service exposes liveness/readiness endpoints consistent with the rest of the fleet.
- **Mirror the golden service**: When in doubt about structure, middleware, or conventions, copy the fleet's reference ("golden") service instead of introducing a new pattern.

## Visual Aids
- Use `/ck:preview --explain` when explaining unfamiliar code patterns or complex logic
- Use `/ck:preview --diagram` for architecture diagrams and data flow visualization
- Use `/ck:preview --slides` for step-by-step walkthroughs and presentations
- Use `/ck:preview --ascii` for terminal-friendly diagrams (no browser needed to understand)
- Add `--html` to any generation flag for self-contained HTML output (opens in browser, no server needed)
- **Plan context:** Active plan determined from `## Plan Context` in hook injection; visuals save to `{plan_dir}/visuals/`
- If no active plan, fallback to `plans/visuals/` directory
- See `primary-workflow.md` → Step 6 for workflow integration
