# Documentation Triggers

## When to Update Docs

Update the affected project documentation in `./docs` when the change modifies a
user-visible setup/behavior contract, public interface, durable architecture decision,
or release/milestone state. Do not create documentation work for a small internal edit
that leaves those surfaces unchanged.

| Trigger | Which Docs | Action |
|---------|-----------|--------|
| Committed phase or milestone status changes | project-roadmap.md | Update progress or milestone status |
| User-visible feature or release completes | changelog or owning guide | Document behavior and migration/setup impact |
| User-visible significant bug fix | changelog or owning guide | Document impact when users need to act or know |
| Security patch changes public guidance | changelog or system-architecture.md | Record safe remediation guidance |
| API contract changes | system-architecture.md, code-standards.md | Update endpoints, schemas |
| Architecture decision | system-architecture.md | Document decision + rationale |
| Scope/timeline change | project-roadmap.md | Adjust phases, dates |
| Dependency requirement changes setup/compatibility | owning setup or architecture guide | Record requirement and impact |
| Breaking changes | owning guide, code-standards.md | Document migration path |

## Documentation Files

```
./docs/
├── project-overview-pdr.md     # Product requirements
├── code-standards.md           # Coding conventions
├── codebase-summary.md         # Architecture overview
├── design-guidelines.md        # UI/UX standards
├── deployment-guide.md         # Deploy procedures
├── system-architecture.md      # System design
└── project-roadmap.md          # Milestones & progress
```

## Update Protocol

1. **Read current state:** Always read target doc before editing
2. **Gather evidence:** Use implementation output or active-plan reports when they exist
3. **Update content:** Modify progress %, statuses, dates, descriptions
4. **Cross-reference:** Ensure consistency across docs
5. **Validate:** Verify dates, versions, references accurate

## Quality Standards

- **Consistency:** Same formatting, versioning across all docs
- **Accuracy:** Progress %, dates, statuses reflect reality
- **Completeness:** Sufficient detail for stakeholder communication
- **Timeliness:** Update within same session as significant changes
- **Traceability:** Clear links between roadmap items and implementation

## Delegation Pattern

Use `docs-manager` only for a broad, independently owned documentation pass. Make a
small, tightly scoped update inline.

```
Agent(
  subagent_type: "docs-manager",
  prompt: "Update ./docs for [changes]. Work context: [path]",
  description: "Update docs"
)
```

Project manager coordinates WHEN to update; docs-manager handles HOW.
