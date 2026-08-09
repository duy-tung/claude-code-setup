# Claude Code Boilerplate

A boilerplate for building software projects with **Claude Code**. It ships a set of skills, agents, hooks, and rules that scale planning, delegation, and verification to the size of the task — inline work stays inline, and specialists appear only when the work genuinely warrants them.

The shipped profile pins a fixed model and effort level so runs are reproducible; see [Runtime Baseline](./docs/runtime-baseline.md).

## What is Claude Code?

**Claude Code** is Anthropic's official CLI tool that brings AI-powered development assistance directly to your terminal. It enables natural language interaction with your codebase and provides intelligent automation for common development tasks.

- [Claude Code](https://claude.com/product/claude-code)
- [Docs](https://code.claude.com/docs/en/overview)

Additional provider support, including OpenCode, is handled by ClaudeKit CLI migration rather than bundled engineer-kit artifacts.

## Related Projects & Directories

- `claudekit` - Website of ClaudeKit
  - Directory: `../claudekit`
  - Repo: https://github.com/claudekit/claudekit
- `claudekit-marketing` - Marketing Kit repository
  - Directory: `../claudekit-marketing`
  - Repo: https://github.com/claudekit/claudekit-marketing
- `claudekit-cli` - CLI tool for quick project setup
  - Directory: `../claudekit-cli`
  - Repo: https://github.com/mrgoonie/claudekit-cli
- `claudekit-docs` - Public documentation repository: https://docs.claudekit.cc
  - Directory: `../claudekit-docs`
  - Repo: https://github.com/claudekit/claudekit-docs

## Key Benefits

### 🚀 Accelerated Development
- **Proportional Planning**: Inline plans for small changes; durable plans for complex work
- **Intelligent Code Generation**: Context-aware code creation and modification
- **Automated Testing**: Comprehensive test generation and execution
- **Smart Documentation**: Synchronized docs that evolve with your code

### 🎯 Enhanced Quality
- **Risk-Based Review**: Specialized reviewers for broad, difficult, or high-risk changes
- **Evidence-Based Quality**: One coherent verification bundle scaled to the change
- **Best Practices Enforcement**: Built-in adherence to coding standards
- **Security-First Development**: Proactive security analysis and recommendations

### 🏗️ Structured Workflow
- **Bounded Orchestration**: Independent specialists only when parallel work pays for the coordination cost
- **Task Management**: Automated project tracking and progress monitoring
- **Documentation Sync**: Always up-to-date technical documentation
- **Clean Git Workflow**: Professional commit messages and branch management

## Documentation

### 📚 Core Documentation
- **[Project Overview & PDR](./docs/project-overview-pdr.md)** - Comprehensive project overview, goals, features, and product development requirements
- **[Codebase Summary](./docs/codebase-summary.md)** - High-level overview of project structure, technologies, and components
- **[Code Standards](./docs/code-standards.md)** - Coding standards, naming conventions, and best practices
- **[System Architecture](./docs/system-architecture.md)** - Detailed architecture documentation, component interactions, and data flow
- **[Runtime Baseline](./docs/runtime-baseline.md)** - Required versions, shipped defaults, and the API constraints that error
- **[Skills Reference](./guide/SKILLS.md)** - Auto-generated catalog of all available skills

### 📖 Additional Resources
- **[AI-facing Rules](./claude/rules/CLAUDE.md)** - Development instructions and workflows installed by the CK CLI
- **[Verification Workflow](./.github/workflows/verify.yml)** - PR gate for prompt policy, harness integrity, hooks, statusline, and worktree tests

## Quick Start

### Prerequisites
- [Claude Code](https://code.claude.com/docs/en/setup) **2.1.219+** installed and configured (older versions resolve the `opus` alias to a previous model)
- Git for version control
- Node.js 18+ (or your preferred runtime)
- Operating Systems: macOS 10.15+, Ubuntu 20.04+/Debian 10+, or Windows 10+ (with WSL 1, WSL 2, or Git for Windows)
- Hardware: 4GB+ RAM

```bash
claude --version
claude update  # run when the version is older than 2.1.219
```

### Setup your new project with ClaudeKit

1. **Install ClaudeKit CLI**:
   ```bash
   npm install -g claudekit-cli
   ```

2. **Create your new project with ClaudeKit framework**:
   ```bash
   mkdir my-project
   ck new --dir my-project --kit engineer
   ```

   **Note:** If you want to use the kit with your existing project:
   ```bash
   cd /path/to/project
   ck init --kit engineer
   ```

   To target another provider later, run ClaudeKit CLI migration from the project root, for example:
   ```bash
   ck migrate -a opencode
   ```

3. **Start development**:
   ```bash
   # claude/settings.json pins the model and effort for new sessions
   claude
   # One-session equivalent:
   claude --model claude-opus-5 --effort high
   # [YOLO mode - not recommended]
   # claude --dangerously-skip-permissions

   # now you can use these specific commands
   /ck:plan "implement user authentication"
   /ck:plan --deep "refactor the notification pipeline"
   /ck:plan --tdd "refactor auth middleware safely"
   /ck:cook "add database integration"
   /ck:cook "refactor auth middleware" --tdd
   ```

   Confirm the active model and effort in `/status`. `high` is the reproducible
   baseline; test `low`/`medium` for cost-sensitive work and reserve `xhigh`/`max` for
   workloads where this repo's evals show a real gain. The context window is 1M tokens by
   default; Claude Code plan access can still depend on account/provider.

   On Microsoft Foundry or a custom gateway, replace the model setting with the
   deployment-specific model name described in the
   [Claude Code model configuration](https://code.claude.com/docs/en/model-config).

   The kit intentionally omits `fallbackModel` so runs do not silently switch away
   from the pinned baseline. Claude Code fallback chains cover model overload,
   unavailability, and some server errors, but not authentication, billing,
   rate-limit, request-size, or transport errors. If your account or provider does
   not expose the pinned model, choose a supported one explicitly for the session:

   ```bash
   claude --model sonnet --effort high
   ```

   For a persistent personal override, set `"model": "sonnet"` in
   `.claude/settings.local.json` instead of changing the shared profile. Either
   override intentionally stops representing the pinned eval baseline.

   Agent Teams are experimental and disabled by default. Opt in for one Claude
   session from a POSIX shell (macOS, Linux, WSL, or Git Bash) with:

   ```bash
   CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude
   ```

   Current limitations include no restoration of in-process teammates after
   `/resume` or `/rewind`, task status that can lag, and shutdown that can wait for
   an in-flight request or tool call. See the
   [Agent Teams guide](./docs/agent-teams-guide.md) before enabling it persistently.

📖 **Learn more from our docs:** [https://docs.claudekit.cc](https://docs.claudekit.cc)

## Project Structure

```
├── .claude/                 # Claude Code configuration
│   ├── agents/             # Claude Code agents
│   ├── hooks/              # Claude Code hooks
│   │   └── .logs/          # Structured hook diagnostics (hook-log.jsonl)
│   ├── skills/             # Claude Code skills
│   └── rules/              # AI-facing rules installed by the CK CLI
│       └── CLAUDE.md       # Top-level ClaudeKit Engineer guidance
├── docs/                   # Project documentation
│   ├── codebase-summary.md # Auto-generated codebase overview
│   ├── code-standards.md   # Development standards
│   ├── project-overview-pdr.md # Product requirements
│   └── project-roadmap.md      # Project roadmap
├── plans/                  # Implementation plans and reports
│   ├── templates/          # Plan templates
│   └── reports/            # Agent-to-agent communication
└── README.md              # This file
```

## The AI Agent Team

This boilerplate includes 11 optional specialists. Small, clear tasks are handled inline; reach for an agent when a sizeable task has independent workstreams or needs domain-specific review. Agent Teams share one checkout, so assign non-overlapping files and nominate one integrator for shared files.

### 🎯 Core Development Agents

#### **Planner Agent**
- Researches technical approaches and best practices
- Creates comprehensive implementation plans
- Analyzes architectural trade-offs
- Spawns multiple researcher agents for parallel investigation

#### **Researcher Agent**
- Investigates specific technologies and frameworks
- Analyzes existing solutions and patterns
- Provides technical recommendations
- Supports the planner with detailed findings

#### **Tester Agent**
- Generates comprehensive test suites
- Validates functionality and performance
- Ensures cross-platform compatibility
- Reports on test coverage and quality metrics

### 🔍 Quality Assurance Agents

#### **Code Reviewer Agent**
- Performs automated code quality analysis
- Enforces coding standards and conventions
- Identifies security vulnerabilities
- Provides improvement recommendations

#### **Debugger Agent**
- Analyzes application logs and error reports
- Diagnoses performance bottlenecks
- Investigates CI/CD pipeline issues
- Provides root cause analysis

#### **Code Simplifier Agent**
- Refactors for clarity, consistency, and maintainability
- Removes duplication and dead code
- Preserves behavior while reducing complexity
- Aligns code with surrounding conventions

### 📚 Documentation & Management Agents

#### **Docs Manager Agent**
- Maintains synchronized technical documentation
- Updates API documentation automatically
- Ensures documentation accuracy
- Manages codebase summaries with repomix

#### **Git Manager Agent**
- Creates clean, conventional commit messages
- Manages branching and merge strategies
- Handles version control workflows
- Ensures professional git history

#### **Project Manager Agent**
- Tracks development progress and milestones
- Updates project roadmaps and timelines
- Manages task completion verification
- Maintains project health metrics

### 🔎 Specialized Agents

#### **Brainstormer Agent**
- Generates and pressure-tests solution ideas
- Weighs trade-offs and feasibility with brutal honesty
- Explores alternative architectures before implementation
- Surfaces risks early in the design phase

#### **Journal Writer Agent**
- Documents development decisions
- Tracks technical explorations
- Records lessons learned
- Maintains decision history

## Agent Orchestration Patterns

### Sequential Chaining
Use when a substantial task has real phase dependencies:
```bash
# Planning → Implementation → Testing → Review
/ck:plan "implement user dashboard"
# For large refactors:
/ck:plan --deep "untangle the dashboard data flow"
/ck:plan --tdd "refactor dashboard state safely"
# After planning, use the exact absolute-path handoff command emitted by plan:
/ck:cook /absolute/path/to/plans/YYMMDD-HHMM-dashboard/plan.md
# If planning used --tdd, preserve it on handoff:
/ck:cook /absolute/path/to/plans/YYMMDD-HHMM-dashboard/plan.md --tdd
# Cook selects proportional testing and review for the task risk.

# Alternative: Use /ck:cook for standalone implementation (plans internally)
/ck:cook "implement user dashboard"
/ck:cook "refactor dashboard state" --tdd
```

### Parallel Execution
Use for independent, non-overlapping tasks that justify coordination overhead:
```bash
# Multiple researchers exploring different approaches
planner agent spawns:
- researcher (database options)
- researcher (authentication methods)
- researcher (UI frameworks)
# Each returns source paths or command evidence for synthesis
```

### Context Management
- Agents communicate through file system reports
- Context is preserved between agent handoffs
- Fresh context prevents conversation degradation
- Essential information is documented in markdown

## Development Workflow

### 1. Feature Development
```bash
# Start with planning
/ck:plan "add real-time notifications"
/ck:plan --deep "refactor the notifications delivery pipeline"

# Research is conditional on novelty, ambiguity, or version-sensitive facts

# Implementation
/ck:cook "implement notification system"
/ck:cook "refactor notification retries" --tdd

# Cook verifies proportionally; independent review is risk-triggered.

# Documentation update
/ck:docs

# Project tracking
/ck:project-management  # Check project status
```

### 2. Bug Fixing
```bash
# Analyze the issue
/ck:debug "investigate login failures"

# Create fix plan
/ck:plan "resolve authentication bug"

# Implement solution
/ck:fix "authentication issue"

# Validate fix
/ck:test
```

### 3. Documentation Management
```bash
# Update documentation
/ck:docs

# Pack the codebase for LLM consumption
repomix  # Creates ./repomix-output.xml

# Review project status
/ck:project-management
```

## Configuration Files

### .claude/rules/CLAUDE.md
Installed ClaudeKit Engineer instructions for Claude Code. Customize a project-level `CLAUDE.md` only when your project needs local overrides; keep kit guidance in the rules bundle.
- Project architecture guidelines
- Development standards and conventions
- Agent coordination protocols
- Specific workflows for your project

### plans/templates/*.md
Reusable templates for:
- Feature implementation plans
- Bug fix procedures
- Refactoring strategies
- Architecture decisions

## Model Context Protocol (MCP)

✍️ Please read [my technical blog article about MCP here](https://faafospecialist.substack.com/p/claude-code-solution-to-use-mcp-servers).

### Pre-requisites

In ClaudeKit, you need to setup the MCP servers in `.claude/.mcp.json` file.

Copy the example file:
```bash
mv .claude/.mcp.json.example .claude/.mcp.json
```

Then add your MCP servers, below are some examples:

### [Context7](https://github.com/upstash/context7)
```json
{
   "mcpServers": {
      "context7": {
         "command": "npx",
         "args": ["-y", "@upstash/context7-mcp", "--api-key", "YOUR_API_KEY"],
      }
   }
}
```

### [Human MCP](https://github.com/mrgoonie/human-mcp/)

```json
{
   "mcpServers": {
      "human": {
         "command": "npx",
         "args": ["@goonnguyen/human-mcp@latest"],
         "env": { "GOOGLE_GEMINI_API_KEY": "YOUR_API_KEY" }
      }
   }
}
```

### [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)
```json
{
   "mcpServers": {
      "chrome-devtools": {
         "command": "npx",
         "args": ["-y", "chrome-devtools-mcp@latest"]
      }
   }
}
```

## Best Practices

### Development Principles
- **YAGNI**: You Aren't Gonna Need It - avoid over-engineering
- **KISS**: Keep It Simple, Stupid - prefer simple solutions
- **DRY**: Don't Repeat Yourself - eliminate code duplication

### Code Quality
- Small changes get a targeted check; broad changes get wider tests and review
- Verification is based on fresh tool/test evidence, without duplicate self-check loops
- Security considerations are built-in
- Performance work is driven by measurements and requirements

### Documentation
- Documentation evolves with code changes
- API docs are automatically updated
- Architecture decisions are recorded
- Codebase summaries are regularly refreshed

### Git Workflow
- Clean, conventional commit messages
- Professional git history
- No AI attribution in commits
- Focused, atomic commits

## Usage Examples

### Starting a New Feature
```bash
# Small, clear feature: inspect, implement, and run a targeted check inline
claude "Add the existing OAuth provider's logout callback"

# Cross-cutting feature: create a durable plan when coordination helps
/ck:plan "implement OAuth2 across the API, web app, and migration layer"
/ck:cook /absolute/path/to/plans/YYMMDD-HHMM-oauth2/plan.md

# High-risk boundary: request an independent security-focused review
/ck:code-review "review the OAuth2 trust boundaries"
```

### Debugging Issues
```bash
# Investigate problem
claude "Debug the slow database queries"
# Debugger agent analyzes logs and performance

# Diagnose, fix, and verify with measured query evidence
/ck:fix "optimize the confirmed query bottleneck"
```

### Project Maintenance
```bash
# Check project health
claude "What's the current project status?"
# Project manager reports the tracked state without expanding scope

# Update documentation
claude "Sync documentation with recent changes"
# Only affected public/setup documentation is updated

# Plan next sprint
claude "Plan the next development phase"
# Planner creates detailed roadmap for upcoming work
```

## Advanced Features

### Multi-Project Support
- Manage multiple repositories simultaneously
- Shared agent configurations across projects
- Consistent development patterns

### Custom Agent Creation
- Define project-specific agents
- Extend existing agent capabilities
- Create domain-specific expertise

## Customization Guide

### 1. Project Setup
- Add or update a project-level `CLAUDE.md` only for project-specific overrides
- Customize plan templates in `plans/templates/`

### 2. Agent Specialization
- Add domain-specific knowledge to agents
- Create custom agents for unique requirements
- Configure agent interaction patterns

### 3. Workflow Optimization
- Define project-specific commands
- Create shortcuts for common tasks
- Establish team coding standards

## Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the agent orchestration workflow
4. Ensure all tests pass and documentation is updated
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Learn More

### Claude Code Resources
- [Claude Code Documentation](https://code.claude.com/docs/en/overview)

### Community
- [ClaudeKit Community](https://claudekit.cc/discord)
- [Discussion Forum](https://github.com/anthropic/claude-code/discussions)
- [Example Projects](https://github.com/topics/claude-code)

### Support
- [Issue Tracker](https://github.com/anthropic/claude-code/issues)
- [Feature Requests](https://github.com/anthropic/claude-code/discussions/categories/ideas)
- [Documentation](https://code.claude.com/docs/en/overview)

---

**Start building with AI-powered development today!** This boilerplate provides everything you need to create professional software with intelligent agent assistance.
