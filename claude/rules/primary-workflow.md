# Primary Workflow

**IMPORTANT:** Analyze the skills catalog and activate the skills that are needed for the task during the process.
**IMPORTANT**: Ensure token efficiency while maintaining high quality.

## Delegation Gate

The steps below name an agent for each phase. That naming says *which* agent owns a
phase, not that every task must route through all of them.

Spawn a subagent only when the work is genuinely independent and parallelizable, or
needs its own context budget. Work finishable in a handful of tool calls stays inline —
writing the prompt, paying for the subagent's context, and reading its report back
costs more than doing it. Full criteria: `./.claude/rules/opus-5-calibration.md` §2.

The gate scales with the task, not with the phase. A one-line fix runs inline
end-to-end. A multi-file feature or anything touching unfamiliar code still routes
through `planner`, `tester`, and `code-reviewer` — skipping review there is how
regressions ship. When unsure, delegate: the cost of an unnecessary review is one
subagent, the cost of a skipped one is a bug in main.

#### 1. Code Implementation
- Before you start, create an implementation plan with TODO tasks in `./plans` directory (delegate to `planner` when the delegation gate applies; otherwise plan inline).
- When in planning phase, research the relevant technical topics (use multiple `researcher` agents in parallel when the topics are genuinely independent and the gate applies; otherwise research inline). Research feeds the plan either way.
- Write clean, readable, and maintainable code
- Follow established architectural patterns
- Implement features according to specifications
- Handle edge cases and error scenarios
- **DO NOT** create new enhanced files, update to the existing files directly.
- **[IMPORTANT]** After creating or modifying code file, run compile command/script to check for any compile errors.

#### 2. Testing
- Run tests on the **simplified code** (delegate to `tester` when the delegation gate applies; otherwise run them inline)
  - Write comprehensive unit tests
  - Ensure high code coverage
  - Test error scenarios
  - Validate performance requirements
- Tests verify the FINAL code that will be reviewed and merged
- **DO NOT** ignore failing tests just to pass the build.
- **IMPORTANT:** make sure you don't use fake data, mocks, cheats, tricks, temporary solutions, just to pass the build or github actions.
- **IMPORTANT:** Always fix failing tests follow the recommendations and run the tests again (delegate to `tester` when the delegation gate applies; otherwise re-run them inline), only finish your session when all tests pass.

#### 3. Code Quality
- After testing passes, review the clean, tested code (delegate to `code-reviewer` when the delegation gate applies; otherwise review inline).
- Follow coding standards and conventions
- Write self-documenting code
- Add meaningful comments for complex logic
- Optimize for performance and maintainability

#### 4. Integration
- Always follow the plan from step 1, whether `planner` produced it or you wrote it inline
- Ensure seamless integration with existing code
- Follow API contracts precisely
- Maintain backward compatibility
- Document breaking changes
- Update docs in `./docs` directory if any (delegate to `docs-manager` when the delegation gate applies; otherwise update them inline).

#### 5. Debugging
- When a user report bugs or issues on the server or a CI/CD pipeline, run the tests and analyze the failure (delegate to `debugger` when the delegation gate applies; otherwise investigate inline).
- Implement the fix from that analysis.
- Run the tests again and analyze the result (delegate to `tester` when the delegation gate applies; otherwise run them inline).
- If tests still fail, fix them follow the recommendations and repeat from the **Step 3**.

#### 6. Visual Explanations
When explaining complex code, protocols, or architecture:
- **When to use:** User asks "explain", "how does X work", "visualize", or topic has 3+ interacting components
- Use `/ck:preview --explain <topic>` to generate visual explanation with ASCII + Mermaid
- Use `/ck:preview --diagram <topic>` for architecture and data flow diagrams
- Use `/ck:preview --slides <topic>` for step-by-step walkthroughs
- Use `/ck:preview --ascii <topic>` for terminal-friendly output only
- **HTML mode** (add `--html` for self-contained HTML pages, opens directly in browser):
  - `/ck:preview --html --explain <topic>` — publication-quality HTML explanation
  - `/ck:preview --html --diagram <topic>` — interactive HTML diagram with zoom controls
  - `/ck:preview --html --slides <topic>` — magazine-quality slide deck
  - `/ck:preview --html --diff [ref]` — visual diff review
  - `/ck:preview --html --plan-review` — plan vs codebase comparison
  - `/ck:preview --html --recap [timeframe]` — project context snapshot
- **Plan context:** Visuals save to plan folder from `## Plan Context` hook injection; if none, uses `plans/visuals/`
- **Markdown mode:** Renders Markdown with Mermaid diagrams
- **HTML mode:** Opens directly in browser — self-contained, no server needed
- See `development-rules.md` → "Visual Aids" section for additional guidance
