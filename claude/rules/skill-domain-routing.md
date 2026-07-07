# Skill Domain Routing

When a user's task involves a specific domain, use these decision trees to pick the RIGHT skill based on user intent.

## Codebase Understanding

```
User wants to...
├── Quick file search, locate specific code     → /ck:scout
└── Onboard a new repo / dump codebase for LLM  → /ck:repomix
```

## Agent Harness (project agent-readiness)

```
User wants to...
├── Scaffold harness files for a repo (AGENTS.md, feature-list, init.sh) → /ck:harness
└── Audit / score a repo's agent-readiness and fix the weakest subsystem → /ck:harness
```

## Security

```
User wants to...
└── STRIDE/OWASP security audit with auto-fix    → /ck:security
```

## AI / LLM

```
User wants to...
├── Optimize context, agent architecture, memory → /ck:context-engineering
└── Learn the autoresearch pattern / find the right family member → /ck:autoresearch
```

## Testing

```
User wants to...
└── Run test suites, coverage reports, TDD       → /ck:test
```

## Version Control

```
User wants to...
├── Stage / commit (conventional, auto-split) / push / open a PR → /ck:git
└── Full branch → merge → test → review → PR release pipeline    → /ck:ship
```

## Project Tracking

```
User wants to...
└── Open the plans dashboard / kanban view of plan progress → /ck:plans-kanban
```

## Documentation

```
User wants to...
├── Update project docs (codebase-summary, PDR)   → /ck:docs
├── Discover skills by capability / "is there a skill" → /ck:find-skills
├── Publish-grade SVG/PNG diagrams (architecture) → /ck:tech-graph
└── Sprint retrospective from git history         → /ck:retro
```

## Documents / Office Files

```
User wants to...
├── Create / edit / extract from .docx (Word)         → /ck:docx
├── Create / edit / extract from .pdf (forms, tables) → /ck:pdf
├── Create / edit / extract from .pptx (PowerPoint)   → /ck:pptx
└── Create / edit / extract from .xlsx (spreadsheets) → /ck:xlsx
```

## Output Style

```
User wants to...
└── Match explanation depth / code complexity to their experience (0-5) → /ck:coding-level
```

## Usage Notes

- Pick ONE skill per distinct user intent
- Domain skills combine with core workflow: `/ck:plan` → domain skill → `/ck:cook`
- Skills not listed here are either core workflow skills (see `skill-workflow-routing.md`) or utility skills activated on demand (e.g. `/ck:ask`, `/ck:preview`, `/ck:sequential-thinking`)
