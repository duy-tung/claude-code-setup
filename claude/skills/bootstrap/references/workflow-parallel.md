# Parallel Workflow (`--parallel`)

**User gates:** Design approval, then normal parallel cook review gates. Implementation uses multi-agent parallel execution after user-approved cook continuation.

## Step 1: Research

Spawn max 2 `researcher` agents in parallel:
- Explore requirements, validation, challenges, solutions
- Keep reports ≤150 lines

No user gate — proceed automatically.

## Step 2: Tech Stack

Use `planner` + multiple `researcher` agents in parallel for best-fit stack.
Write to `./docs` directory (≤150 lines).

No user gate — proceed automatically.

## Step 3: Wireframe & Design

1. Use `general-purpose` + `researcher` agents in parallel:
   - Research style, trends, fonts, colors, spacing, positions
   - Predict Google Fonts name (NOT just Inter/Poppins)
   - Describe assets for image-generation
2. `general-purpose` creates:
   - Design guidelines at `./docs/design-guidelines.md`
   - Wireframes in HTML at `./docs/wireframe/`
3. If no logo: generate with an image-generation tool
4. Screenshot with Chrome MCP → save to `./docs/wireframes/`

**Gate:** Ask user to approve design. Repeat if rejected.

**Image tools:** an image-generation/vision tool for generation/analysis, `imagemagick` for crop/resize, background removal tool as needed.

## Step 4: Parallel Planning

Activate **ck:plan** skill: `/ck:plan --parallel <requirements>`
- Creates phases with **exclusive file ownership** per phase (no overlap)
- **Dependency matrix**: which phases run concurrently vs sequentially
- `plan.md` includes dependency graph, execution strategy, file ownership matrix
- Task hydration with `addBlockedBy` for sequential deps, no blockers for parallel groups

After planning, hand off to cook with normal review gates. Add `--auto` only if the user explicitly asked for autonomous bootstrap.

## Step 5: Parallel Implementation → Final Report

Load `references/shared-phases.md` for remaining phases.

Activate **ck:cook** skill: `/ck:cook --parallel <plan-path>`
- Read `plan.md` for dependency graph and execution strategy
- Launch multiple `general-purpose` agents in PARALLEL for concurrent phases
  - Pass: phase file path, environment info
- Use `general-purpose` for frontend (generate/analyze assets with an image-generation/vision tool, edit with `imagemagick`)
- Respect file ownership boundaries
- Run type checking after implementation
- Keep cook review gates; `--parallel` controls execution shape, not approval bypass

Cook handles testing, review, docs, onboarding, final report per `shared-phases.md`.
