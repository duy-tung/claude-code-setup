# Quality Gate Rules

Rules for contributors and AI agents working on the claudekit-engineer repo. These are NOT shipped to end users.

> **Local and CI contract.** Run `npm run verify` before committing. The same
> verification bundle is enforced by `.github/workflows/verify.yml` on every
> pull request and every push to `main`, using Node.js 18 and 20 with Python
> 3.11. The workflow covers the static validators, eval-harness integrity, hook
> and statusline tests, Opus 5 policy checks, and clean-worktree assertions.
> Passing CI does not waive the metadata-deletion contract below.

## Opus 5 Prompt Policy (tree-wide, enforced by tests)

`claude/hooks/__tests__/opus-5-alignment-policy.test.cjs` is the prompt-behavior contract. It no longer works from a hardcoded file list — it scans **every** shipped skill, agent, rule, and doc, so a newly added file is covered the moment it lands. It checks for:

- pre-Opus-5 scaffolding in **hook sources** as well as Markdown (the injected text is what the model actually reads)
- unconditional delegation openers, unconditional `/ck:` skill chaining, multi-persona role theater
- over-verification and self-scoring: self-recheck instructions, "subagent to verify", restrictive review filters, numeric confidence scores

**Prohibitions do not trip the guard.** `claude/hooks/__tests__/lib/prompt-policy.cjs` reports a phrase only when it reads as an *instruction*: it ignores clause-level negation ("do not double-check"), Markdown soft wrapping that separates a negation from its phrase, and whole sections under an `## Anti-patterns`-style heading. This matters — a guard that fires on the rule banning the behavior gets silenced by deleting the correct rule.

When a check fires, **fix the prose**. Only add to `PROMPT_POLICY_EXEMPTIONS` when the phrase is genuinely domain logic (re-running a test after a fix, re-measuring a noisy metric, re-reading stale third-party output), and state why in a comment. A companion test fails when an exemption stops matching, so stale entries cannot accumulate. A growing exemption list means the pattern is wrong, not that the exceptions are.

**Affected files:** `claude/hooks/__tests__/opus-5-alignment-policy.test.cjs`, `claude/hooks/__tests__/lib/prompt-policy.cjs`

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

**When modifying workflow routing rules** (`claude/rules/skill-workflow-routing.md`, `claude/rules/skill-domain-routing.md`):
- These rules ARE shipped to end users — they guide Claude's skill suggestions
- Keep every `/ck:` reference resolvable (the validator above flags dangling ones)
- When adding a new skill to a workflow chain, update BOTH the routing rule AND the skill's `## Workflow Position` section

**Affected files:** `claude/rules/skill-*.md`, `claude/skills/*/SKILL.md`, `claude/scripts/validate-skill-crossrefs.py`

## Skill Routing Coverage (run before committing)

`validate-skill-crossrefs.py` also reports **orphaned skills** — skills with no inbound or outbound `/ck:` reference in the skill-to-skill graph. Note the validator does NOT read the routing files: a graph orphan can still be perfectly discoverable via `skill-domain-routing.md` / `skill-workflow-routing.md`. There is no routing-coverage script or allowlist file anymore; for each orphan the validator prints, grep the two routing files yourself and judge reachability from there.

**The principle (audit-route-reframe):** discoverability is part of the contract. Shipping a skill that no routing file mentions means users (and Claude) will not find it. **Telemetry zero ≠ zero value** — most dormant skills audited under epic #711 flipped to KEEP after routing or description fixes. When tempted to delete a "dormant" skill:

1. **Audit:** Does the skill have unique capability (scripts, references, agents)? If yes, deletion likely loses real value.
2. **Route:** Is it reachable from a routing file? If no, dormancy is a discoverability problem — fix the routing.
3. **Reframe:** Does the SKILL.md `description` read like a maintainer-only utility? Rewrite with user-phrasing keywords.

Delete only when: (a) audit confirms zero unique capability, AND (b) routing fix wouldn't change adoption, AND (c) use case is genuinely covered by another skill. Catalog size is an output, not a target.

**When adding a new skill:**
1. Add the skill to the appropriate domain block in `skill-domain-routing.md` (preferred — user-facing)
2. OR add it to a workflow chain in `skill-workflow-routing.md`
3. Genuine meta / orchestrator / maintainer skills may stay orphaned by design — document why in the skill's own SKILL.md body (the allowlist files that used to record this were removed with CI).

**When deleting a skill:**
- Re-run the validator and remove every now-dangling `/ck:` reference in the same change.

**Affected files:** `claude/rules/skill-domain-routing.md`, `claude/rules/skill-workflow-routing.md`, `claude/skills/*/SKILL.md`

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
