# Quality Gate Rules

Rules for contributors and AI agents working on the claudekit-engineer repo. These are NOT shipped to end users.

> **Local and CI contract.** Run `npm run verify` before committing. The same
> verification bundle is enforced by `.github/workflows/verify.yml` on every
> pull request and every push to `main`, using Node.js 18 and 20 with Python
> 3.11. The workflow covers the static validators, eval-harness integrity, hook
> and statusline tests, prompt-policy checks, and clean-worktree assertions.
> Passing CI does not waive the metadata-deletion contract below.

## Prompt Policy (tree-wide, enforced by tests)

`claude/hooks/__tests__/prompt-policy-contract.test.cjs` is the prompt-behavior contract. It no longer works from a hardcoded file list — it scans **every** shipped skill, agent, rule, and doc, so a newly added file is covered the moment it lands. It checks for:

- pre-Opus-5 scaffolding in **hook sources** as well as Markdown (the injected text is what the model actually reads)
- unconditional delegation openers, unconditional `/ck:` skill chaining, multi-persona role theater
- over-verification and self-scoring: self-recheck instructions, "subagent to verify", restrictive review filters, numeric confidence scores

**Prohibitions do not trip the guard.** `claude/hooks/__tests__/lib/prompt-policy.cjs` reports a phrase only when it reads as an *instruction*: it ignores clause-level negation ("do not double-check"), Markdown soft wrapping that separates a negation from its phrase, and whole sections under an `## Anti-patterns`-style heading. This matters — a guard that fires on the rule banning the behavior gets silenced by deleting the correct rule.

When a check fires, **fix the prose**. Only add to `PROMPT_POLICY_EXEMPTIONS` when the phrase is genuinely domain logic (re-running a test after a fix, re-measuring a noisy metric, re-reading stale third-party output), and state why in a comment. A companion test fails when an exemption stops matching, so stale entries cannot accumulate. A growing exemption list means the pattern is wrong, not that the exceptions are.

**Affected files:** `claude/hooks/__tests__/prompt-policy-contract.test.cjs`, `claude/hooks/__tests__/lib/prompt-policy.cjs`

## Metadata Deletions (MANDATORY)

When renaming or deleting ANY file under `claude/` directory (skills, hooks, agents, scripts), you MUST add the old relative path to `claude/metadata.json` `deletions[]` array. This tells the CLI installer to remove stale files from user machines during upgrade. Forgetting this leaves orphaned files that cause conflicts.

**Affected files:** `claude/metadata.json`

## Skill Registry Contract

Canonical skill names live in each `claude/skills/*/SKILL.md` frontmatter `name:` field. All cross-references in markdown files MUST use exact registered names with `/ck:` prefix. Before adding a new skill name, check for collisions with Claude Code built-in commands (`/help`, `/clear`, `/debug`, `/plan`, `/compact`, `/review`, `/search`). When renaming a skill, update ALL cross-references in the same PR.

## Skill Cross-Reference Integrity (run before committing)

`claude/scripts/validate-skill-crossrefs.py` builds a registry from all `claude/skills/**/SKILL.md` frontmatter `name:` fields (nested skills like `document-skills/pdf` included) and audits every `/ck:` reference in the skill bodies — reporting broken refs, graph orphans, hubs, and workflow-chain gaps.

**Critical rule: use REGISTERED names, not directory names.**

The registry normalizes names by stripping the `ck:` prefix from frontmatter. So `name: ck:debug` registers as `debug`. The reference `/ck:debug` captures `debug` → match. But `/ck:ck-debug` captures `ck-debug` → **no match, validator flags it**.

| Directory Name | Frontmatter `name:` | Registered As | Correct Reference |
|----------------|---------------------|---------------|-------------------|
| `ck-debug` | `ck:debug` | `debug` | `/ck:debug` |
| `ck-plan` | `ck:plan` | `plan` | `/ck:plan` |
| `ck-security` | `ck:security` | `security` | `/ck:security` |
| `cook` | `ck:cook` | `cook` | `/ck:cook` |
| `brainstorm` | `ck:brainstorm` | `brainstorm` | `/ck:brainstorm` |

**Before committing any `/ck:` reference**, verify the name resolves:
```bash
python3 claude/scripts/validate-skill-crossrefs.py claude/skills/
```

**When modifying `claude/rules/skill-routing.md`:**
- It IS shipped to end users — it guides Claude's skill suggestions
- Keep every `/ck:` reference resolvable (the validator above flags dangling ones)
- When adding a new skill to a chain, update BOTH the routing rule AND the skill's `## Workflow Position` section

**Affected files:** `claude/rules/skill-routing.md`, `claude/skills/*/SKILL.md`, `claude/scripts/validate-skill-crossrefs.py`

## Skill Discoverability (run before committing)

`validate-skill-crossrefs.py` reports **orphaned skills** — skills with no inbound or outbound `/ck:` reference in the skill-to-skill graph. A graph orphan is not necessarily undiscoverable.

**The primary discovery surface is the skill's own `description`.** Claude Code lists every shipped skill with its description in context, so a well-written description is what makes a skill findable. `claude/rules/skill-routing.md` is the *secondary* surface: it carries only what a description cannot — escalation chains and disambiguation between skills that sound alike. Do not re-describe a skill there; that duplication is what the always-loaded budget below exists to prevent.

**The principle (audit-route-reframe):** discoverability is part of the contract. **Telemetry zero ≠ zero value** — most dormant skills audited under epic #711 flipped to KEEP after routing or description fixes. When tempted to delete a "dormant" skill:

1. **Audit:** Does the skill have unique capability (scripts, references, agents)? If yes, deletion likely loses real value.
2. **Reframe the description:** Does it read like a maintainer-only utility, or does it use the words a user would type? This is the highest-leverage fix.
3. **Route:** Only if the skill is confusable with another, or belongs in a chain, add it to `skill-routing.md`.

Delete only when: (a) audit confirms zero unique capability, AND (b) a description fix wouldn't change adoption, AND (c) the use case is genuinely covered by another skill. Catalog size is an output, not a target.

**When deleting a skill:**
- Re-run the validator and remove every now-dangling `/ck:` reference in the same change.

**Affected files:** `claude/rules/skill-routing.md`, `claude/skills/*/SKILL.md`

## Always-Loaded Rules Budget (enforced by tests)

Unscoped `.md` files under `.claude/rules/` load into **every session** at the same priority as `.claude/CLAUDE.md`. Anthropic's guidance is under 200 lines per file, and warns that longer files reduce adherence and that contradictory rules get resolved arbitrarily.

`claude/rules/model-calibration.md` is the **single normative source for model behavior**. Other rules reference it by section; they do not restate it. Two tests in `prompt-policy-contract.test.cjs` enforce this: a budget test that prints the per-file breakdown and fails over the ceiling, and a canon test that fails when another always-loaded rule states a canonical phrasing.

When a rule grows, move task-specific content to a `paths:`-scoped rule (loads only for matching files, like `documentation-management.md`) or into a skill's `references/` directory (loads with the skill). **Do not raise the ceiling** — it ratcheted 946 → 426 and is meant to keep going down.

**Affected files:** `claude/rules/*.md`, `claude/hooks/__tests__/prompt-policy-contract.test.cjs`

### Hooks carry runtime facts, rules carry behavior

The per-turn injection built by `claude/hooks/lib/context-builder.cjs` must contain only what is resolved at runtime: absolute plans/docs/reports paths, the active plan and branch, the naming pattern, the skills venv path, machine stats. Behavior rules belong in `.claude/rules/`, which already loads every session — restating them per turn spends tokens on a second copy that can drift from the first, and the drifting copy is the one the model reads most often.

`advisory-boundary-policy.test.cjs` asserts both directions: the invariants exist in the rules, and the hook does **not** restate them.

**Affected files:** `claude/hooks/lib/context-builder.cjs`, `claude/hooks/__tests__/advisory-boundary-policy.test.cjs`


## Skill Description and Listing Policy

`python3 claude/scripts/validate-skill-frontmatter.py` is the frontmatter contract. It validates every `SKILL.md` against `claude/schemas/skill-schema.json`, requires `user-invocable: true`, and rejects `disable-model-invocation: true` for shipped skills. Run it standalone:

```bash
python3 claude/scripts/validate-skill-frontmatter.py
```

`claude/scripts/score-skill-description.py` (invoked by `scan_skills.py`) scores each description on structural format criteria and flags confusable skill pairs (Jaccard similarity) and dependency cycles. It measures FORMAT COMPLIANCE (structure), not semantic effectiveness.

Description guidance — keep frontmatter as a tight routing signal:

- Lead with a capability / action verb, not "Use this when…" (instructional phrasing reads worse for routing)
- Keep descriptions roughly between 50 and 512 characters
- No TODO / FIXME / WIP or maintainer-only markers (`[KAI]`, `maintainer-only`) in a shipped description
- After changing any description, regenerate the catalog: `python3 claude/scripts/scan_skills.py` (rewrites `guide/SKILLS.md` and `guide/SKILLS.yaml`)

Listing pressure is managed through project settings, not a lint:

- `skillListingBudgetFraction` (currently `0.04`) and `skillListingMaxDescChars` (currently `512`) in `claude/settings.json` keep the shipped-skill listing within budget. Keep both set; tighten descriptions rather than hiding skills — do not add `skillOverrides`.

**Affected files:** `claude/scripts/validate-skill-frontmatter.py`, `claude/scripts/score-skill-description.py`, `claude/scripts/scan_skills.py`, `claude/settings.json`

## Statusline Changes

Changes to `statusline*.cjs` or `statusline-*.cjs` MUST update snapshot tests. Run test suite with all config variants: minimal config, full config, custom lines, no quota, 1M context window. ANSI escape sequences and special characters (NBSP) must be explicitly tested.
