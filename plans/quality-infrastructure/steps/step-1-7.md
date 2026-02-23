# Step 1.7

**Plan**: `plans/quality-infrastructure/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.7: Symlink sync, stale removal, and verification

**Objective**: Clean up dangling symlinks, regenerate correct ones, verify no stragglers across entire codebase.
**Script Evaluation**: Direct
**Execution Model**: Haiku
**Depends on**: Steps 1.1-1.6

**Implementation**:
- Find and remove dangling symlinks in .claude/agents/ and .claude/skills/ (old-name targets gone after git mv)
- Run `just sync-to-parent` to regenerate correct symlinks
- Grep entire codebase for ALL old names: vet-fix-agent, quiet-task, tdd-task, plan-reviewer, design-vet-agent, outline-review-agent, runbook-outline-review-agent, review-tdd-process, quiet-explore, runbook-simplification-agent, test-hooks, vet-agent, vet-taxonomy, vet-requirement, /vet
- Fix any stragglers found
- Commit if changes made

**Expected Outcome**: All symlinks valid. Zero grep hits for old names across codebase.
**Error Conditions**: `just sync-to-parent` fails -> STOP, report. Stragglers found -> fix if mechanical, STOP if ambiguous.
**Validation**: `just precommit` passes; grep for old names -> zero hits; no dangling symlinks

---


- Merge 5 prose deslop rules into agent-core/fragments/communication.md as new subsection after existing rules. Rules only, strip examples. Discard principle line.
- Update agent-core/skills/project-conventions/SKILL.md: remove "Prose" subsection under Deslop section (now ambient). Add missing code rule: "Expose fields directly until access control needed." Restructure heading to "Code Quality."
- Add `skills: ["project-conventions"]` to YAML frontmatter of agent-core/agents/artisan.md and agent-core/agents/test-driver.md.
- Remove "Code Quality" section (8 bullets) from agent-core/agents/artisan.md — redundant with project-conventions skill injection.
- Remove `@agent-core/fragments/deslop.md` line from CLAUDE.md. Delete agent-core/fragments/deslop.md. Update remaining "deslop" references:
  - agent-core/README.md — update inventory description
  - agent-core/skills/memory-index/SKILL.md — update if references deslop fragment
  - agents/memory-index.md — update deslop-related /when triggers
  - agents/decisions/operational-practices.md — update term to "code quality"/"prose quality"
  - agents/session.md — update task descriptions

---


- Add 5 entries to agents/decisions/cli.md. Each states general principle first, project instance second. Source content from plans/reports/code-density-grounding.md:
  1. Expected state checks return booleans — normal states checked with boolean returns, not exceptions. Project: `_git_ok(*args) -> bool`
  2. Consolidate display and exit — error termination as single call. Project: `_fail(msg, code=1) -> Never`
  3. Formatter expansion signals abstraction need — 5+ lines after formatting = extract helper. Project: default kwargs pattern
  4. Exceptions for exceptional events only — custom exception classes, not ValueError. Project: lint satisfaction via proper design
  5. Error handling layers don't overlap — context at failure site, display at top level. Project: never both
- Add 5 /when triggers to agents/memory-index.md under `## agents/decisions/cli.md` section.
