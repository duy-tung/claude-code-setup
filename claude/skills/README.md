# Skills

Skills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. This directory contains the 40 skills shipped with **claudekit-engineer** — a lean kit for core software-engineering workflows with Claude Code. The CK CLI installs it as `.claude/skills/` in your project.

Background reading on the skills system itself:
- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Equipping agents for the real world with Agent Skills](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

## Anatomy and Naming

Each skill is a self-contained directory with a `SKILL.md` (YAML frontmatter + instructions), and optionally `references/` (detail docs loaded on demand), `scripts/` (executables), and `agents/` (subagent prompts).

Naming convention: the directory may carry a `ck-` prefix, but the invocation name comes from the frontmatter `name:` field with its `ck:` prefix — so directory `ck-debug` has `name: ck:debug` and is invoked as `/ck:debug`.

## Skill Catalog

Invoke any skill as a slash command, or just describe the task — the routing rules in `.claude/rules/skill-domain-routing.md` and `skill-workflow-routing.md` guide Claude to the right one. `/ck:find-skills` searches the catalog by capability.

| Category | Skills |
|----------|--------|
| Core workflow | `/ck:plan`, `/ck:cook`, `/ck:fix`, `/ck:test`, `/ck:code-review`, `/ck:ship`, `/ck:git`, `/ck:debug`, `/ck:scout`, `/ck:worktree` |
| Ideation & analysis | `/ck:brainstorm`, `/ck:ask`, `/ck:predict`, `/ck:scenario`, `/ck:security`, `/ck:research`, `/ck:autoresearch`, `/ck:sequential-thinking` |
| Project & process | `/ck:bootstrap`, `/ck:project-management`, `/ck:project-organization`, `/ck:plans-kanban`, `/ck:journal`, `/ck:retro`, `/ck:harness`, `/ck:loop`, `/ck:team`, `/ck:coding-level` |
| Docs, context & visuals | `/ck:docs`, `/ck:preview`, `/ck:tech-graph`, `/ck:repomix`, `/ck:context-engineering`, `/ck:xia`, `/ck:find-skills`, `/ck:skill-creator` |
| Office documents | `/ck:docx`, `/ck:pdf`, `/ck:pptx`, `/ck:xlsx` |

## Installation

Most skills are pure instructions and need no setup. A few require external dependencies (librsvg for tech-graph, Poppler for pdf, Python packages for document-skills, the repomix CLI). Use the automated installation scripts to set up all dependencies:

**Linux/macOS:**
```bash
cd .claude/skills
./install.sh
```

**Windows (PowerShell as Administrator):**
```powershell
cd .claude\skills
.\install.ps1
```

The installation scripts will:
- Install system tools (librsvg/rsvg-convert, Poppler/pdftoppm)
- Install Node.js packages (pnpm, repomix)
- Create a Python virtual environment
- Install Python packages (pypdf, Pillow, openpyxl, python-pptx, etc.)
- Verify all installations

For manual installation or troubleshooting, see [INSTALLATION.md](INSTALLATION.md) for the complete dependency list and platform-specific instructions.

When running a skill's Python scripts, use the venv interpreter (`.claude/skills/.venv/bin/python3` on Linux/macOS, `.claude\skills\.venv\Scripts\python.exe` on Windows) so those packages are available.

## Document Skills

The `document-skills/` subdirectory contains the docx / pdf / pptx / xlsx skills Anthropic developed for Claude's document capabilities, included here as point-in-time snapshots (source-available, not open source — see their license headers). They demonstrate advanced patterns for binary file formats and are the reason for most of the Python dependencies above.

## Creating a Skill

A skill is just a folder with a `SKILL.md`. Use `/ck:skill-creator` to scaffold one, or copy a small existing skill (e.g. `retro/`) as a starting point:

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name

[Instructions Claude follows when this skill is active]
```

Keep the `description` a tight routing signal (lead with a capability verb). If you add a skill to this kit, register it in a routing rule and run the validators before committing — see the repo's quality-gates rules for the contract (cross-reference integrity, frontmatter schema, catalog regeneration).
