# Project Overview & Product Development Requirements (PDR)

**Project Name**: ClaudeKit Engineer
**Version**: 2.19.1
**Last Updated**: 2026-08-09
**Status**: Active Development
**Repository**: https://github.com/duy-tung/claude-code-setup

## Executive Summary

ClaudeKit Engineer is a scale-aware Claude Code setup kit. Small, clear work stays in
the main session; specialized agents and durable artifacts are activated only when
planning, research, testing, review, documentation, or project coordination has a
meaningful independent deliverable.

## Project Purpose

### Vision
Enable developers to build professional software projects faster and with higher quality by leveraging AI agent orchestration, automated workflows, and intelligent project management.

### Mission
Provide a production-ready template that:
- Accelerates development velocity through AI-powered agent collaboration
- Applies project standards with workflows proportional to task size and risk
- Keeps affected user-facing and architectural documentation aligned with code
- Uses targeted verification by default and independent review when risk warrants it
- Streamlines git workflows with professional commit standards

### Value Proposition
- **Fast Small Changes**: Inspect, edit, run a targeted check, and report without orchestration overhead
- **Risk-Calibrated Quality**: Broaden tests and independent review only when the blast radius warrants it
- **Focused Documentation**: Update user-visible setup, public contracts, durable architecture, and release guidance when affected
- **Professional Git History**: Clean, conventional commits without AI attribution
- **Reduced Context Switching**: Specialized agents handle specific concerns

## Target Users

### Primary Users
1. **Solo Developers**: Building projects faster with AI assistance
2. **Small Development Teams**: Standardizing workflows and practices
3. **Open Source Maintainers**: Managing contributions and documentation
4. **Startups**: Rapid prototyping and MVP development
5. **Enterprise Teams**: Enforcing architectural standards

### User Personas

**Persona 1: Solo Full-Stack Developer**
- **Needs**: Fast iteration, quality code, minimal documentation overhead
- **Pain Points**: Context switching, documentation maintenance, testing gaps
- **Solution**: AI agents handle planning, testing, docs while dev focuses on features

**Persona 2: Technical Lead**
- **Needs**: Enforce standards, review code, maintain architecture docs
- **Pain Points**: Code review bottleneck, inconsistent patterns, outdated docs
- **Solution**: Automated reviews, standardized workflows, living documentation

**Persona 3: Open Source Maintainer**
- **Needs**: Scale contributions, maintain quality, clear documentation
- **Pain Points**: Limited time, varying contribution quality, doc rot
- **Solution**: Consistent review process, automated standards enforcement

## Key Features & Capabilities

### 1. Multi-Agent Orchestration System

**Agent Types**:
- **Planning Agents**: Research, architecture, technical decisions
- **Implementation Agents**: Code generation, feature development
- **Quality Agents**: Testing, code review, security analysis
- **Documentation Agents**: Broad, independently owned docs and API-reference updates
- **Management Agents**: Project tracking, progress monitoring, git operations

**Orchestration Patterns**:
- **Scale First**: Small clear work stays inline with one targeted evidence bundle
- **Sequential Chaining**: Substantial dependent stages only
- **Parallel Execution**: Multiple researchers exploring different approaches
- **Query Fan-Out**: Simultaneous investigation of technical solutions

**Performance Optimization**:
- **Scout Block Hook**: Cross-platform hook system blocking heavy directories
  - Automatic platform detection (Windows/Unix/WSL)
  - Zero-configuration setup
  - Blocks: node_modules, __pycache__, .git/, dist/, build/
  - Improves AI agent response time and token efficiency

### 2. Skill-Routed Entry Points (post-v2.17 migration)

`/ck:*` entry points are now backed by user-invocable **skills** under `claude/skills/`, not by a separate command parser. Each skill ships frontmatter (`name:`, `description:`, `user-invocable: true`) and is validated by `claude/scripts/validate-skill-frontmatter.py` and `claude/scripts/validate-skill-crossrefs.py`; `.github/workflows/verify.yml` runs the combined gate on pull requests and pushes to `main`.

**Core Development Entry Points**:
- `/ck:plan` - Research and create implementation plans (`--deep` for major refactors, `--tdd` for tests-first plans)
- `/ck:cook` - Implement features with full workflow (`--tdd` for tests-first refactors, `--parallel` for multi-agent execution)
- `/ck:test` - Run comprehensive test suites
- `/ck:ask` - Expert technical consultation
- `/ck:bootstrap` - Initialize new projects end-to-end
- `/ck:brainstorm` - Solution ideation and evaluation
- `/ck:debug` - Deep issue analysis

**Skill Organization** (`.claude/skills/`):
Command behavior is implemented via skill directories:
- `bootstrap/` - Project initialization workflows
- `docs/` - Documentation generation and updates
- `ck-plan/` - Planning workflows and validators
- `ck-code-review/` - Code review workflows
- `test/` - Testing and validation workflows

### 3. Extensive Skills Library (40 Skills)

**Organized by Domain** (`.claude/skills/`):

**Code Quality & Debugging**: ck-code-review, ck-debug, fix, coding-level, sequential-thinking
**Content & Ideation**: brainstorm, ask
**DevOps & Infrastructure**: git, worktree, ship
**Documentation**: docs, repomix, document-skills, journal
**Graph & Visualization**: tech-graph
**Planning & Prediction**: ck-plan, plans-kanban, ck-predict, ck-scenario
**Project Management**: project-management, project-organization, team, retro
**Research & Discovery**: research, ck-autoresearch, scout, find-skills, context-engineering
**Security**: ck-security
**Skill Development**: skill-creator, ck-harness
**Testing & QA**: test
**Workflow Tools**: cook, ck-loop, preview, xia, bootstrap

### 4. Release Management (manual, post-lean-refactor)

**Features**:
- Semantic versioning (MAJOR.MINOR.PATCH) maintained by hand in `package.json` and `claude/metadata.json`
- Conventional commits as a convention (the `/ck:git` skill writes them; nothing enforces them)
- `metadata.json` `deletions[]` contract so the CLI installer removes retired files on user upgrade
- CI verifies pull requests and `main`; changelog generation, releases, version
  bumps, and NPM publishing remain manual

**Commit Types** (convention for choosing the manual version bump):
- `feat:` → Minor version bump
- `fix:` → Patch version bump
- `BREAKING CHANGE:` → Major version bump
- `docs:`, `refactor:`, `test:` → Patch bump

### 5. Local Quality Gates

Contributors run these locally before committing, and the GitHub Actions verify
workflow reruns the repository gate on pull requests and pushes to `main` (see
`init.sh`):
- `python3 claude/scripts/validate-skill-frontmatter.py`
- `python3 claude/scripts/validate-skill-crossrefs.py claude/skills/`
- `npm test` and `python3 eval/tier0_static.py`

## Technical Requirements

### Functional Requirements

**FR1: Agent Orchestration**
- Support sequential and parallel agent execution
- Enable agent-to-agent communication via file system
- Maintain context across agent handoffs
- Track agent task completion

**FR2: Skill Routing System**
- Parse `/ck:` skill invocations with arguments
- Route to appropriate agent workflows via the domain/workflow routing rules
- Namespaced flat skill names (e.g., `/ck:fix` — nested command paths were retired in the v2.17 migration)
- Provide skill discovery via `/ck:find-skills` and the routing rules

**FR3: Documentation Management**
- Generate codebase summaries with repomix when a broad documentation pass needs one
- Update docs when user-visible setup/behavior or a public contract changes
- Maintain roadmap and changelog for actual release, milestone, scope, or timeline changes
- Record durable architecture and API changes in their owning documents

**FR4: Quality Assurance**
- Run tests before commits
- Run targeted checks for small changes and broaden them for shared or high-risk surfaces
- Perform independent code review when size, unfamiliarity, or risk warrants it
- Check type safety and compilation
- Validate security best practices

**FR5: Git Workflow**
- Enforce conventional commits
- Scan for secrets before commits
- Generate professional commit messages
- Create clean PR descriptions

**FR6: Project Bootstrapping**
- Initialize git repository
- Gather requirements through questions
- Research tech stacks
- Generate project structure
- Create initial documentation
- Set up CI/CD

### Non-Functional Requirements

**NFR1: Performance**
- Command execution < 5 seconds for simple operations
- Parallel agent spawning for independent tasks
- Efficient file system operations
- Optimized context loading

**NFR2: Reliability**
- Handle agent failures gracefully
- Provide rollback mechanisms
- Validate agent outputs
- Error recovery and retry logic

**NFR3: Usability**
- Clear command syntax and documentation
- Helpful error messages
- Progress indicators for long operations
- Comprehensive command help

**NFR4: Maintainability**
- Modular agent definitions
- Reusable workflow templates
- Clear separation of concerns
- Self-documenting code and configs

**NFR5: Security**
- Secret detection before commits
- No AI attribution in public commits
- Secure handling of credentials
- Security best practice enforcement

**NFR6: Scalability**
- Support projects of any size
- Handle large codebases efficiently
- Scale agent parallelization
- Manage complex dependency graphs

## Success Metrics

### Adoption Metrics
- GitHub stars and forks
- NPM package downloads
- Active users and installations
- Community engagement (issues, discussions, PRs)

### Performance Metrics
- Average time to bootstrap new project: < 10 minutes
- Planning to implementation cycle time: 50% reduction
- Documentation coverage: > 90%
- Test coverage: > 80%
- Code review time: 75% reduction

### Quality Metrics
- Conventional commit compliance: 100%
- Zero secrets in commits: 100%
- Automated test pass rate: > 95%
- Documentation freshness: < 24 hours lag

### Developer Experience Metrics
- Time to first commit: < 5 minutes
- Developer onboarding time: 50% reduction
- Context switching overhead: 60% reduction
- Satisfaction score: > 4.5/5.0

## Technical Architecture

### Core Components

**1. Agent Framework**
- Agent definition files (Markdown with frontmatter)
- Agent orchestration engine
- Context management system
- Communication protocol (file-based reports)

**2. Skill Routing System** (replaces the original Command System as of v2.17)
- Frontmatter-driven skill registry (`name:`, `description:`, `user-invocable: true`)
- Skill routing rules (`claude/rules/skill-routing.md`)
- Cross-reference, description, frontmatter, Opus policy, eval-harness, statusline,
  and worktree checks run through `npm run verify` locally and in GitHub Actions
- `metadata.deletions[]` to retire stale commands/skills on user upgrade

**3. Workflow Engine**
- Sequential execution support
- Parallel task scheduling
- Dependency resolution
- Error handling and recovery

**4. Documentation System**
- Repomix integration for codebase compaction
- Template-based doc generation
- Auto-update triggers
- Version tracking

**5. Quality System**
- Test runner integration
- Code review automation
- Type checking and linting
- Security scanning

**6. Release/Upgrade System**
- Manual semantic versioning (`package.json` + `claude/metadata.json`)
- `metadata.deletions[]` upgrade contract consumed by the CLI installer
- Catalog regeneration via `claude/scripts/scan_skills.py`

### Technology Stack

**Runtime**:
- Node.js >= 18.0.0
- All hooks are cross-platform Node.js (`.cjs`) — no Bash/PowerShell hook scripts
- Python 3 for skill/validation scripts (`claude/scripts/`, document skills)

**AI Platforms**:
- Anthropic Claude (Opus / Sonnet / Haiku) — all subagents
- Google Gemini via Gemini-CLI — optional external path in the research/scout skills
- Grok Code via opencode — optional external scouting model (see `skills/scout/references/external-scouting.md`)

**Development Tools**:
- Repomix (codebase compaction)
- Scout Block Hook (performance optimization)
- Node.js test runner (`node --test`) for hook tests

### Integration Points

**MCP Tools** (none wired by default; optional examples in `claude/.mcp.json.example`):
- **context7**: Read latest documentation
- **human-mcp**: Vision/multimodal analysis via Gemini
- **chrome-devtools**: Browser debugging integration

**External Services**:
- GitHub (Issues and PRs)

## Use Cases

### UC1: Bootstrap New Project
**Actor**: Developer
**Goal**: Create new project from scratch
**Flow**:
1. Run `/bootstrap` command
2. Answer requirement questions
3. AI researches tech stacks
4. Review and approve recommendations
5. AI generates project structure
6. AI implements initial features
7. AI creates tests and documentation
8. Project ready for development

**Outcome**: Fully functional project with tests, docs, CI/CD in < 10 minutes

### UC2: Implement New Feature
**Actor**: Developer
**Goal**: Add a feature with a workflow proportional to its complexity and risk
**Flow**:
1. Assess scope, uncertainty, and blast radius.
2. For a small clear feature, inspect relevant files, implement inline, run a targeted
   check, and inspect the diff.
3. For a multi-component or risky feature, use `/ck:plan` or `/ck:cook` and add bounded
   research only when an external decision must be resolved.
4. Broaden tests or add an independent review when contracts, security, data,
   concurrency, or broad fan-out make it worthwhile.
5. Update affected user-facing, public-contract, architecture, or release docs.
6. Commit or publish only through an explicitly requested git/ship workflow.

**Outcome**: Feature complete with proportional evidence and no unrelated artifacts

### UC3: Debug Production Issue
**Actor**: Developer
**Goal**: Identify and fix production bug
**Flow**:
1. Run `/ck:debug "API timeout errors"`
2. Debugger agent analyzes logs and system
3. Root cause identified
4. AI implements the narrowest complete solution
5. The original reproduction or targeted regression test validates the fix
6. Add a plan, independent review, documentation, or publish step only when risk or the
   requested workflow requires it

**Outcome**: Bug fixed with evidence matched to its blast radius

### UC4: Manage Commits and Deployments
**Actor**: Developer
**Goal**: Maintain professional git history
**Flow**:
1. Developer completes feature implementation
2. Run tests via `/ck:test` command
3. Code review via `/ck:cook` workflow
4. Conventional commit via git-manager agent
5. Push to feature branch
6. Create PR via GitHub interface

**Outcome**: Professional commit history and clean PR ready for review

### UC5: Update Documentation
**Actor**: Project Manager
**Goal**: Ensure docs are current
**Flow**:
1. Run `/ck:docs update`
2. Resolve the exact target and the source evidence it documents
3. Update a small target inline, or delegate a broad independent pass to docs-manager
4. Use repomix only when the broad pass needs a new codebase summary
5. Update only affected guides, contracts, architecture, or release state
6. Validate affected links, names, and examples once

**Outcome**: Affected documentation synchronized without unrelated regeneration

## Constraints & Limitations

### Technical Constraints
- Requires Node.js >= 18.0.0
- Depends on Claude Code CLI
- File-based communication has I/O overhead
- Token limits on AI model context windows

### Operational Constraints
- Requires API keys for AI platforms
- Internet connection for MCP tools
- Storage for repomix output files

### Design Constraints
- Agent definitions must be Markdown with frontmatter
- Commands follow slash syntax
- Reports use specific naming conventions
- Conventional commits required

## Risks & Mitigation

### Risk 1: AI Model API Failures
**Impact**: High
**Likelihood**: Medium
**Mitigation**: Retry logic, fallback models, graceful degradation

### Risk 2: Context Window Limits
**Impact**: Medium
**Likelihood**: High
**Mitigation**: Repomix for code compaction, selective context loading, chunking

### Risk 3: Agent Coordination Failures
**Impact**: High
**Likelihood**: Low
**Mitigation**: Validation checks, error recovery, rollback mechanisms

### Risk 4: Secret Exposure
**Impact**: Critical
**Likelihood**: Low
**Mitigation**: Pre-commit scanning, .gitignore enforcement, security reviews

### Risk 5: Documentation Drift
**Impact**: Medium
**Likelihood**: Medium
**Mitigation**: Automated triggers, freshness checks, validation workflows

## Future Roadmap

### Phase 1: Foundation (Complete - v1.0–v1.8)
- ✅ Core agent framework
- ✅ Slash command system (later replaced by skills in Phase 2)
- ✅ Automated releases in the original framework (release/versioning is now manual;
  current CI is verification-only)
- ✅ Skills library (initial)
- ✅ Documentation system

### Phase 2: Enhancement + Commands→Skills Migration (Complete - v2.x through v2.18)
- ✅ Skills expansion, later slimmed to a focused 40-skill catalog
- ✅ Commands→Skills migration (v2.17)
- ✅ Skill validation gates: cross-ref, description, frontmatter (v2.18;
  available locally and in verification CI)
- ✅ Windows parity + hook safety (v2.18.x)
- ✅ Preview Dashboard
- ✅ Cross-platform performance optimization

### Phase 3: Advanced Features (Planned, no firm date)
- 📋 Visual workflow builder
- 📋 Custom agent creator UI
- 📋 Team collaboration features
- 📋 Analytics and insights dashboard
- 📋 Multi-language support

### Phase 4: Enterprise (Future)
- 📋 Self-hosted deployment
- 📋 Advanced security features
- 📋 Compliance automation
- 📋 Custom integrations
- 📋 Enterprise support

## Dependencies & Integration

### Required Dependencies
- Node.js runtime environment
- Git version control
- Claude Code CLI
- API keys for AI platforms

### Integrations
- Repomix
- Various MCP servers

## Compliance & Standards

### Coding Standards
- YAGNI (You Aren't Gonna Need It)
- KISS (Keep It Simple, Stupid)
- DRY (Don't Repeat Yourself)
- Files < 500 lines
- Comprehensive error handling
- Security-first development

### Git Standards
- Conventional Commits
- Clean commit history
- No AI attribution
- No secrets in commits
- Professional PR descriptions

### Documentation Standards
- Markdown format
- Up-to-date (< 24 hours)
- Comprehensive coverage
- Clear examples
- Proper versioning

### Testing Standards
- Unit test coverage > 80%
- Integration tests for workflows
- Error scenario coverage
- Performance validation
- Security testing

## Glossary

- **Agent**: Specialized AI assistant with specific expertise and responsibilities
- **Slash Command**: Shortcut that triggers agent workflows (e.g., `/ck:plan`)
- **Skill**: Reusable knowledge module for specific technologies or patterns
- **MCP**: Model Context Protocol for AI tool integration
- **Repomix**: Tool for compacting codebases into AI-friendly format
- **Sequential Chaining**: Running agents one after another with dependencies
- **Parallel Execution**: Running multiple agents simultaneously
- **Query Fan-Out**: Spawning multiple researchers to explore different approaches
- **Conventional Commits**: Structured commit message format (type(scope): description)

## Appendix

### Related Documentation
- [Codebase Summary](./codebase-summary.md)
- [Code Standards](./code-standards.md)
- [System Architecture](./system-architecture.md)
- [Skills Reference](../guide/SKILLS.md)

### External Resources
- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code/overview)
- [Conventional Commits](https://conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

### Support & Community
- GitHub Issues: https://github.com/duy-tung/claude-code-setup/issues
- Discussions: https://github.com/duy-tung/claude-code-setup/discussions
- Repository: https://github.com/duy-tung/claude-code-setup

## Unresolved Questions

1. **Performance Benchmarks**: Need to establish baseline metrics for agent execution times
2. **Multi-Repository Support**: How to handle projects spanning multiple repositories?
3. **Custom AI Model Support**: Should we support AI platforms beyond Claude (and the optional Gemini/Grok external-scouting paths)?
4. **Agent Marketplace**: Community-contributed agents and skills distribution mechanism?
5. **Real-Time Collaboration**: How to handle multiple developers using agents simultaneously?
