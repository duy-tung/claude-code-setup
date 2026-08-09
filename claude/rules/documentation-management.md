---
paths:
  - "docs/**"
  - "**/*.md"
  - "CHANGELOG*"
---

# Project Documentation Management

Loads when you touch documentation rather than every session. The rule that governs
*whether* to write docs at all lives in `./.claude/rules/model-calibration.md` §2 — update
only what changed, and do not produce artifacts the task did not ask for.


### Roadmap & Changelog Maintenance
- **Project Roadmap** (`./docs/project-roadmap.md`): Living document tracking project phases, milestones, and progress
- **Project Changelog** (`./docs/project-changelog.md`): Detailed record of all significant changes, features, and fixes
- **System Architecture** (`./docs/system-architecture.md`): Living document describing system design, components, and data flow
- **Code Standards** (`./docs/code-standards.md`): Living document defining coding conventions, patterns, and best practices

### Scale Documentation to the Change

- **Small internal change:** Do not update roadmap, changelog, architecture, or status
  documents merely because code changed.
- **User-visible setup or behavior:** Update the specific guide or changelog entry that
  users rely on.
- **Public contract or durable architecture:** Update the owning API/schema or
  architecture documentation in the same change.
- **Release, milestone, scope, or timeline change:** Update roadmap/changelog state when
  the repository actually maintains those artifacts.
- **Security update:** Document public remediation or durable operational guidance
  without exposing sensitive details.

### Documentation Triggers
Update only the affected document when:

- user-visible setup, behavior, or migration guidance changes
- a public API, schema, CLI, configuration contract, or dependency requirement changes
- a durable architecture or security decision changes
- a release, milestone, committed scope, or timeline changes

A `project-manager` or `docs-manager` subagent is optional. Use one only for a broad,
independently owned documentation pass; make small, targeted updates inline.

### Update Protocol
1. **Before Updates**: Read only the target document and the source evidence it describes
2. **During Updates**: Maintain version consistency and proper formatting
3. **After Updates**: Verify links, dates, and cross-references are accurate
4. **Quality Check**: Ensure updates align with actual implementation progress

### Plans

### Plan Location
Save plans in `./plans` directory with timestamp and descriptive name.

**Format:** Use naming pattern from `## Naming` section injected by hooks.

**Example:** `plans/251101-1505-authentication-and-profile-implementation/`

#### File Organization

```
plans/
├── 20251101-1505-authentication-and-profile-implementation/
    ├── research/
    │   ├── researcher-XX-report.md
    │   └── ...
│   ├── reports/
│   │   ├── scout-report.md
│   │   ├── researcher-report.md
│   │   └── ...
│   ├── plan.md                                # Overview access point
│   ├── phase-01-setup-environment.md          # Setup environment
│   ├── phase-02-implement-database.md         # Database models
│   ├── phase-03-implement-api-endpoints.md    # API endpoints
│   ├── phase-04-implement-ui-components.md    # UI components
│   ├── phase-05-implement-authentication.md   # Auth & authorization
│   ├── phase-06-implement-profile.md          # Profile page
│   └── phase-07-write-tests.md                # Tests
└── ...
```

#### File Structure

##### Overview Plan (plan.md)
- Keep generic and under 80 lines
- List each phase with status/progress
- Link to detailed phase files
- Key dependencies

##### Phase Files (phase-XX-name.md)
Fully respect the `.claude/rules/development-rules.md` file.
Each phase file should contain:

**Context Links**
- Links to related reports, files, documentation

**Overview**
- Priority
- Current status
- Brief description

**Key Insights**
- Important findings from research
- Critical considerations

**Requirements**
- Functional requirements
- Non-functional requirements

**Architecture**
- System design
- Component interactions
- Data flow

**Related Code Files**
- List of files to modify
- List of files to create
- List of files to delete

**Implementation Steps**
- Detailed, numbered steps
- Specific instructions

**Todo List**
- Checkbox list for tracking

**Success Criteria**
- Definition of done
- Validation methods

**Risk Assessment**
- Potential issues
- Mitigation strategies

**Security Considerations**
- Auth/authorization
- Data protection

**Next Steps**
- Dependencies
- Follow-up tasks
