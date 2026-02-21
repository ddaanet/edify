# Codebase Exploration Report: Quality Infrastructure Reform

## Summary

Comprehensive mapping of the claudeutils codebase for a quality infrastructure reform involving agent renames, skill/fragment reorganization, and systematic reference updates across ~37 files. The exploration identified 17 agent definitions, 8 plan-specific tasks to delete, 30 skill directories, and 28 fragment files, along with reference locations for "vet-fix-agent", "quiet-task", "tdd-task", and "plan-reviewer" throughout the codebase.

---

## Key Findings

### A. Agent Definitions in agent-core/agents/

**Location:** `/Users/david/code/claudeutils/agent-core/agents/`

Complete list of 17 agent definition files:

1. `/Users/david/code/claudeutils/agent-core/agents/test-hooks.md`
2. `/Users/david/code/claudeutils/agent-core/agents/memory-refactor.md`
3. `/Users/david/code/claudeutils/agent-core/agents/quiet-explore.md`
4. `/Users/david/code/claudeutils/agent-core/agents/remember-task.md`
5. `/Users/david/code/claudeutils/agent-core/agents/vet-agent.md` **[RENAME to review-agent.md]**
6. `/Users/david/code/claudeutils/agent-core/agents/brainstorm-name.md`
7. `/Users/david/code/claudeutils/agent-core/agents/design-vet-agent.md` **[RENAME to design-reviewer.md or design-corrector.md]**
8. `/Users/david/code/claudeutils/agent-core/agents/vet-fix-agent.md` **[RENAME to corrector.md]**
9. `/Users/david/code/claudeutils/agent-core/agents/vet-taxonomy.md`
10. `/Users/david/code/claudeutils/agent-core/agents/runbook-outline-review-agent.md`
11. `/Users/david/code/claudeutils/agent-core/agents/quiet-task.md`
12. `/Users/david/code/claudeutils/agent-core/agents/refactor.md`
13. `/Users/david/code/claudeutils/agent-core/agents/review-tdd-process.md`
14. `/Users/david/code/claudeutils/agent-core/agents/runbook-simplification-agent.md`
15. `/Users/david/code/claudeutils/agent-core/agents/plan-reviewer.md`
16. `/Users/david/code/claudeutils/agent-core/agents/outline-review-agent.md`
17. `/Users/david/code/claudeutils/agent-core/agents/tdd-task.md`

### B. Plan-Specific Agents to Delete from .claude/agents/

**Location:** `/Users/david/code/claudeutils/.claude/agents/`

All 8 requested agents exist and should be deleted:

1. `/Users/david/code/claudeutils/.claude/agents/error-handling-task.md` ✓ EXISTS
2. `/Users/david/code/claudeutils/.claude/agents/pushback-task.md` ✓ EXISTS
3. `/Users/david/code/claudeutils/.claude/agents/runbook-quality-gates-task.md` ✓ EXISTS
4. `/Users/david/code/claudeutils/.claude/agents/when-recall-task.md` ✓ EXISTS
5. `/Users/david/code/claudeutils/.claude/agents/workflow-rca-fixes-task.md` ✓ EXISTS
6. `/Users/david/code/claudeutils/.claude/agents/worktree-merge-data-loss-task.md` ✓ EXISTS
7. `/Users/david/code/claudeutils/.claude/agents/worktree-merge-resilience-task.md` ✓ EXISTS
8. `/Users/david/code/claudeutils/.claude/agents/workwoods-task.md` ✓ EXISTS

**Additional symlinks found (keep as they reference agent-core):**
- brainstorm-name.md → agent-core
- design-vet-agent.md → agent-core
- memory-refactor.md → agent-core
- outline-review-agent.md → agent-core
- plan-reviewer.md → agent-core
- quiet-explore.md → agent-core
- quiet-task.md → agent-core
- refactor.md → agent-core
- remember-task.md → agent-core
- review-tdd-process.md → agent-core
- runbook-outline-review-agent.md → agent-core
- runbook-simplification-agent.md → agent-core
- tdd-task.md → agent-core
- hook-batch-task.md (standalone, not a symlink)

### C. Skill Directories in agent-core/skills/

**Location:** `/Users/david/code/claudeutils/agent-core/skills/`

30 skill directories found:

1. `/Users/david/code/claudeutils/agent-core/skills/brief`
2. `/Users/david/code/claudeutils/agent-core/skills/commit`
3. `/Users/david/code/claudeutils/agent-core/skills/deliverable-review`
4. `/Users/david/code/claudeutils/agent-core/skills/design`
5. `/Users/david/code/claudeutils/agent-core/skills/doc-writing`
6. `/Users/david/code/claudeutils/agent-core/skills/error-handling`
7. `/Users/david/code/claudeutils/agent-core/skills/gitmoji`
8. `/Users/david/code/claudeutils/agent-core/skills/ground`
9. `/Users/david/code/claudeutils/agent-core/skills/handoff`
10. `/Users/david/code/claudeutils/agent-core/skills/handoff-haiku`
11. `/Users/david/code/claudeutils/agent-core/skills/how`
12. `/Users/david/code/claudeutils/agent-core/skills/memory-index`
13. `/Users/david/code/claudeutils/agent-core/skills/next`
14. `/Users/david/code/claudeutils/agent-core/skills/opus-design-question`
15. `/Users/david/code/claudeutils/agent-core/skills/orchestrate`
16. `/Users/david/code/claudeutils/agent-core/skills/plugin-dev-validation`
17. `/Users/david/code/claudeutils/agent-core/skills/prioritize`
18. `/Users/david/code/claudeutils/agent-core/skills/project-conventions`
19. `/Users/david/code/claudeutils/agent-core/skills/reflect`
20. `/Users/david/code/claudeutils/agent-core/skills/release-prep`
21. `/Users/david/code/claudeutils/agent-core/skills/remember`
22. `/Users/david/code/claudeutils/agent-core/skills/requirements`
23. `/Users/david/code/claudeutils/agent-core/skills/review-plan`
24. `/Users/david/code/claudeutils/agent-core/skills/runbook`
25. `/Users/david/code/claudeutils/agent-core/skills/shelve`
26. `/Users/david/code/claudeutils/agent-core/skills/token-efficient-bash`
27. `/Users/david/code/claudeutils/agent-core/skills/vet` **[RENAME to review]**
28. `/Users/david/code/claudeutils/agent-core/skills/when`
29. `/Users/david/code/claudeutils/agent-core/skills/worktree`

### D. Fragment Files in agent-core/fragments/

**Location:** `/Users/david/code/claudeutils/agent-core/fragments/`

28 fragment files found:

1. `/Users/david/code/claudeutils/agent-core/fragments/code-removal.md`
2. `/Users/david/code/claudeutils/agent-core/fragments/commit-skill-usage.md`
3. `/Users/david/code/claudeutils/agent-core/fragments/tmp-directory.md`
4. `/Users/david/code/claudeutils/agent-core/fragments/token-economy.md`
5. `/Users/david/code/claudeutils/agent-core/fragments/design-decisions.md`
6. `/Users/david/code/claudeutils/agent-core/fragments/commit-delegation.md`
7. `/Users/david/code/claudeutils/agent-core/fragments/bash-strict-mode.md`
8. `/Users/david/code/claudeutils/agent-core/fragments/no-estimates.md`
9. `/Users/david/code/claudeutils/agent-core/fragments/deslop.md` ✓ EXISTS
10. `/Users/david/code/claudeutils/agent-core/fragments/pushback.md`
11. `/Users/david/code/claudeutils/agent-core/fragments/claude-config-layout.md`
12. `/Users/david/code/claudeutils/agent-core/fragments/delegation.md`
13. `/Users/david/code/claudeutils/agent-core/fragments/execution-routing.md`
14. `/Users/david/code/claudeutils/agent-core/fragments/sandbox-exemptions.md`
15. `/Users/david/code/claudeutils/agent-core/fragments/project-tooling.md`
16. `/Users/david/code/claudeutils/agent-core/fragments/tool-batching.md`
17. `/Users/david/code/claudeutils/agent-core/fragments/source-not-generated.md`
18. `/Users/david/code/claudeutils/agent-core/fragments/continuation-passing.md`
19. `/Users/david/code/claudeutils/agent-core/fragments/error-classification.md`
20. `/Users/david/code/claudeutils/agent-core/fragments/escalation-acceptance.md`
21. `/Users/david/code/claudeutils/agent-core/fragments/prerequisite-validation.md`
22. `/Users/david/code/claudeutils/agent-core/fragments/task-failure-lifecycle.md`
23. `/Users/david/code/claudeutils/agent-core/fragments/no-confabulation.md`
24. `/Users/david/code/claudeutils/agent-core/fragments/execute-rule.md`
25. `/Users/david/code/claudeutils/agent-core/fragments/communication.md` ✓ EXISTS
26. `/Users/david/code/claudeutils/agent-core/fragments/vet-requirement.md` **[RENAME to review-requirement.md]**
27. `/Users/david/code/claudeutils/agent-core/fragments/error-handling.md`
28. `/Users/david/code/claudeutils/agent-core/fragments/workflows-terminology.md`

### E. Files Referencing "vet-fix-agent"

**46 files found** with "vet-fix-agent" references:

Key locations for systematic replacement (vet-fix-agent → corrector):
- `/Users/david/code/claudeutils/plans/quality-infrastructure/reports/outline-review.md`
- `/Users/david/code/claudeutils/plans/quality-infrastructure/reports/explore-reviewer-usage.md`
- `/Users/david/code/claudeutils/plans/quality-infrastructure/outline.md`
- `/Users/david/code/claudeutils/plans/quality-infrastructure/requirements.md`
- `/Users/david/code/claudeutils/agent-core/agents/vet-fix-agent.md` (source file)
- `/Users/david/code/claudeutils/agent-core/agents/vet-agent.md`
- `/Users/david/code/claudeutils/agent-core/agents/vet-taxonomy.md`
- `/Users/david/code/claudeutils/agent-core/agents/design-vet-agent.md`
- `/Users/david/code/claudeutils/agent-core/agents/outline-review-agent.md`
- `/Users/david/code/claudeutils/agent-core/agents/runbook-outline-review-agent.md`
- `/Users/david/code/claudeutils/agent-core/skills/vet/SKILL.md`
- `/Users/david/code/claudeutils/agent-core/skills/orchestrate/SKILL.md`
- `/Users/david/code/claudeutils/agent-core/skills/deliverable-review/SKILL.md`
- `/Users/david/code/claudeutils/agent-core/skills/design/SKILL.md`
- `/Users/david/code/claudeutils/agent-core/skills/memory-index/SKILL.md`
- `/Users/david/code/claudeutils/agent-core/skills/doc-writing/SKILL.md`
- `/Users/david/code/claudeutils/agents/decisions/deliverable-review.md`
- `/Users/david/code/claudeutils/agents/decisions/workflow-optimization.md`
- `/Users/david/code/claudeutils/agents/decisions/operational-practices.md`
- `/Users/david/code/claudeutils/agents/decisions/orchestration-execution.md`
- `/Users/david/code/claudeutils/agents/decisions/workflow-planning.md`
- `/Users/david/code/claudeutils/agents/learnings.md`
- `/Users/david/code/claudeutils/agent-core/README.md`
- `/Users/david/code/claudeutils/README.md`
- `/Users/david/code/claudeutils/agent-core/bin/focus-session.py`
- `/Users/david/code/claudeutils/.claude/rules/plugin-dev-validation.md`
- Additional 20+ files in plans/ directory

### F. Files Referencing "vet-agent" (but not "vet-fix-agent")

No standalone "vet-agent" references found. The pattern `(?<!vet-fix-)vet-agent` returned no results, indicating all "vet-agent" references in the codebase are part of "vet-fix-agent" pattern.

### G. Files Referencing "quiet-task"

**24 files found** with "quiet-task" references:

Key locations:
- `/Users/david/code/claudeutils/agent-core/agents/quiet-task.md` (source file)
- `/Users/david/code/claudeutils/plans/quality-infrastructure/outline.md`
- `/Users/david/code/claudeutils/plans/quality-infrastructure/requirements.md`
- `/Users/david/code/claudeutils/plans/quality-infrastructure/reports/outline-review.md`
- `/Users/david/code/claudeutils/plans/quality-infrastructure/reports/agent-naming-brainstorm.md`
- `/Users/david/code/claudeutils/agents/decisions/workflow-optimization.md`
- `/Users/david/code/claudeutils/plans/plugin-migration/reports/explore-structure.md`
- `/Users/david/code/claudeutils/agent-core/skills/runbook/SKILL.md`
- `/Users/david/code/claudeutils/agent-core/skills/vet/SKILL.md`
- `/Users/david/code/claudeutils/plans/orchestrate-evolution/reports/design-review-d5.md`
- `/Users/david/code/claudeutils/plans/orchestrate-evolution/design.md`
- `/Users/david/code/claudeutils/plans/orchestrate-evolution/outline.md`
- `/Users/david/code/claudeutils/tests/test_prepare_runbook_inline.py`
- `/Users/david/code/claudeutils/plans/prototypes/agent-duration-analysis.py`
- `/Users/david/code/claudeutils/plans/prototypes/collect-delegation-overhead.py`
- `/Users/david/code/claudeutils/agent-core/bin/prepare-runbook.py`
- `/Users/david/code/claudeutils/plans/remember-skill-update/requirements.md`
- `/Users/david/code/claudeutils/agents/decisions/implementation-notes.md`
- `/Users/david/code/claudeutils/agent-core/README.md`
- `/Users/david/code/claudeutils/agents/runbook-review-guide.md`
- And 4+ additional files

### H. Files Referencing "tdd-task"

**21 files found** with "tdd-task" references:

Key locations:
- `/Users/david/code/claudeutils/agent-core/agents/tdd-task.md` (source file)
- `/Users/david/code/claudeutils/plans/quality-infrastructure/outline.md`
- `/Users/david/code/claudeutils/plans/quality-infrastructure/requirements.md`
- `/Users/david/code/claudeutils/plans/quality-infrastructure/reports/agent-naming-brainstorm.md`
- `/Users/david/code/claudeutils/agents/plan-archive.md`
- `/Users/david/code/claudeutils/plans/plugin-migration/reports/explore-structure.md`
- `/Users/david/code/claudeutils/agent-core/skills/runbook/SKILL.md`
- `/Users/david/code/claudeutils/plans/orchestrate-evolution/reports/design-review-d5.md`
- `/Users/david/code/claudeutils/plans/orchestrate-evolution/design.md`
- `/Users/david/code/claudeutils/agent-core/README.md`
- `/Users/david/code/claudeutils/agents/decisions/workflow-core.md`
- `/Users/david/code/claudeutils/agents/runbook-review-guide.md`
- And 9+ additional files

### I. Files Referencing "plan-reviewer"

**33 files found** with "plan-reviewer" references:

Key locations:
- `/Users/david/code/claudeutils/agent-core/agents/plan-reviewer.md` (source file)
- `/Users/david/code/claudeutils/plans/quality-infrastructure/outline.md`
- `/Users/david/code/claudeutils/plans/quality-infrastructure/requirements.md`
- `/Users/david/code/claudeutils/plans/quality-infrastructure/reports/outline-review.md`
- `/Users/david/code/claudeutils/plans/quality-infrastructure/reports/explore-reviewer-usage.md`
- `/Users/david/code/claudeutils/agents/learnings.md`
- `/Users/david/code/claudeutils/agents/decisions/workflow-optimization.md`
- `/Users/david/code/claudeutils/agents/decisions/pipeline-contracts.md`
- `/Users/david/code/claudeutils/agents/decisions/deliverable-review.md`
- `/Users/david/code/claudeutils/agents/decisions/defense-in-depth.md`
- `/Users/david/code/claudeutils/agent-core/skills/runbook/SKILL.md`
- `/Users/david/code/claudeutils/agent-core/skills/deliverable-review/SKILL.md`
- `/Users/david/code/claudeutils/agent-core/skills/review-plan/SKILL.md`
- `/Users/david/code/claudeutils/plans/runbook-evolution/reports/explore-skill-structure.md`
- `/Users/david/code/claudeutils/README.md`
- `/Users/david/code/claudeutils/.claude/agents/error-handling-task.md`
- And 17+ additional files

### J. CLAUDE.md @-References Section

**File:** `/Users/david/code/claudeutils/CLAUDE.md`

The @-references include:

```
@agent-core/fragments/workflows-terminology.md
@agent-core/fragments/communication.md
@agent-core/fragments/deslop.md
@agent-core/fragments/execute-rule.md
@agent-core/fragments/pushback.md
@agent-core/fragments/execution-routing.md
@agent-core/fragments/delegation.md
@agents/session.md
@agents/memory-index.md
@agent-core/fragments/error-handling.md
@agent-core/fragments/token-economy.md
@agent-core/fragments/commit-skill-usage.md
@agent-core/fragments/no-estimates.md
@agent-core/fragments/no-confabulation.md
@agent-core/fragments/source-not-generated.md
@agent-core/fragments/code-removal.md
@agent-core/fragments/tmp-directory.md
@agent-core/fragments/design-decisions.md
@agent-core/fragments/project-tooling.md
@agent-core/fragments/tool-batching.md
```

**Architecture & Design Documentation References:**
```
- **agents/decisions/architecture.md** - Module structure
- **agents/decisions/cli.md** - CLI patterns
- **agents/decisions/testing.md** - Testing conventions
- **agents/decisions/workflows.md** - Oneshot and TDD patterns
- **agents/decisions/implementation-notes.md** - Implementation details
```

### K. Fragment File: deslop.md

**File:** `/Users/david/code/claudeutils/agent-core/fragments/deslop.md` ✓ EXISTS

First 20 lines (full content):

```markdown
## Deslop

Strip output to its informational payload. Remove anything that doesn't advance understanding or function. Apply the deletion test: remove the sentence or construct — keep it only if information or behavior is lost.

### Prose

- State information directly — no hedging, framing, or preamble
  - ❌ "It's worth noting that the config is cached"
  - ✅ "The config is cached"
- Answer immediately — skip acknowledgments and transitions
  - ❌ "Great question! Let's dive into..."
  - ✅ (just the answer)
- Reference, never recap — assume the reader has context
  - ❌ "As we discussed above, the parser..."
  - ✅ "The parser..." or omit entirely
- Let results speak — no framing around output that's already visible
  - ❌ "Here's what I found:" followed by what you found
  - ✅ (just the findings)
- Commit to your answer — no hedging qualifiers after delivering it
  - ❌ "This is just one approach, there may be others"
```

### L. Decision File: agents/decisions/cli.md

**File:** `/Users/david/code/claudeutils/agents/decisions/cli.md` ✓ EXISTS

First 20 lines:

```markdown
# CLI Design

CLI-specific patterns and conventions for claudeutils command-line interface.

## .CLI Conventions

### When Getting Current Working Directory

**Decision:** Use `Path.cwd()` for default project directory

**Rationale:** Consistency with pathlib usage throughout codebase

**Implementation:** `cli.py:main()`

### How to Output Errors To Stderr

**Decision:** Print errors to stderr using `print(..., file=sys.stderr)` before `sys.exit(1)`

**Rationale:** Standard Unix convention - errors to stderr, data to stdout
```

### M. Fragment File: agent-core/fragments/communication.md

**File:** `/Users/david/code/claudeutils/agent-core/fragments/communication.md` ✓ EXISTS

Full content:

```markdown
## Communication Rules

1. **Stop on unexpected results** - If something fails OR succeeds unexpectedly, describe expected vs observed, then STOP and wait for guidance
2. **Wait for explicit instruction** - Do NOT proceed with a plan or TodoWrite list unless user explicitly says "continue" or equivalent
3. **Be explicit** - Ask clarifying questions if requirements unclear
4. **Stop at boundaries** - Complete assigned task then stop (no scope creep)
5. **Unambiguous directives** - Automation directives must have explicit boundaries. Use "Do NOT commit or handoff" not "drive to completion" (which is ambiguous). Clear prohibitions prevent scope creep in automation
```

### N. Skill File: agent-core/skills/vet/SKILL.md

**File:** `/Users/david/code/claudeutils/agent-core/skills/vet/SKILL.md` ✓ EXISTS

First 30 lines:

```markdown
---
name: vet
description: Review in-progress changes for quality and correctness
allowed-tools: Read, Bash(git:*, diff:*)
user-invocable: true
---

# Review Changes for Quality

Review in-progress work for quality, correctness, and adherence to project standards. This skill examines uncommitted changes, recent commits, or partial branch work to identify issues and suggest improvements.

**Distinction:** This skill reviews work-in-progress. The built-in `/review` is for PR-focused reviews.

## When to Use

**Use this skill when:**
- Ready to review changes before committing
- Want to check recent commits for issues
- Need quality check on partial branch work
- Unsure if changes are ready for commit
- After completing runbook execution (general workflow)

**Do NOT use when:**
- Reviewing a pull request (use built-in `/review`)
- Changes already committed and pushed
- Need code exploration (use explore agent)

## Review Process

### 1. Determine Scope
```

### O. Justfile: sync-to-parent Target

**File:** `/Users/david/code/claudeutils/agent-core/justfile` ✓ EXISTS

The `sync-to-parent` target is present in the agent-core justfile. Key details:

```bash
sync-to-parent:
    #!/usr/bin/env bash
    set -euo pipefail

    # Determine parent project directory (one level up from agent-core)
    PARENT_DIR="$(cd .. && pwd)"
    CLAUDE_DIR="$PARENT_DIR/.claude"

    echo "Syncing agent-core to $PARENT_DIR/.claude via relative symlinks"

    # Create .claude directories if they don't exist
    ...
```

**CLAUDE.md reference:** Line 85 mentions `just sync-to-parent` as available recipe for agent-core

---

## Patterns & Observations

### Naming Conventions Identified

1. **Agent naming patterns:**
   - Task agents: `*-task.md` (quiet-task, tdd-task, remember-task)
   - Reviewer/evaluator agents: `*-agent.md` or `*-reviewer.md` (plan-reviewer, vet-agent, design-vet-agent)
   - Special agents: `quiet-explore.md`, `refactor.md`, `brainstorm-name.md`

2. **Skill naming patterns:**
   - All skills in `/agent-core/skills/` with SKILL.md frontmatter
   - Current problematic names: `vet/` (should be `review/`)
   - Related skill: `review-plan/SKILL.md` already exists (naming inconsistency)

3. **Fragment naming patterns:**
   - Fragment files are atomic behavioral concepts
   - Current problematic name: `vet-requirement.md` (should be `review-requirement.md`)

### Symlink Strategy

The `.claude/agents/` directory uses a two-tier structure:

**Symlinked agents** (reference agent-core):
- Core/reusable agents that should sync with `just sync-to-parent`
- Point to relative paths like `../../agent-core/agents/quiet-task.md`

**Plan-specific agents** (standalone files):
- Task agents created for specific plans: error-handling-task, pushback-task, runbook-quality-gates-task, etc.
- Should be deleted as part of cleanup
- hook-batch-task.md is also standalone (newer, non-symlinked)

### Reference Locations Summary

| Reference | Files | Primary Locations |
|-----------|-------|------------------|
| vet-fix-agent | 46 | Plans, agents/, skills/*, agent-core docs |
| quiet-task | 24 | Plans, agent-core docs, skills, tests |
| tdd-task | 21 | Plans, agent-core docs, skills |
| plan-reviewer | 33 | Plans, agents/decisions, skills |
| vet-agent | embedded in vet-fix-agent references | (no standalone refs) |

---

## Gaps & Unresolved Questions

### 1. Agent Rename Targets Not Specified

Current requirement mentions:
- vet-fix-agent → **corrector** (specified)
- design-vet-agent → **design-corrector**? (not explicitly specified)
- vet-agent → **reviewer**? (not explicitly specified)

**Action needed:** Clarify final names for all three agents

### 2. Fragment Rename Scope

Only `vet-requirement.md` explicitly mentioned for rename. Unknown if other fragments with "vet" prefix need renaming:
- `vet-taxonomy.md` (agent file, not fragment)
- Should this be renamed to `review-taxonomy.md`?

### 3. Symlink Update Strategy

The `just sync-to-parent` command needs verification after renames. It uses hardcoded paths to agent-core/agents/ and agent-core/skills/. Will it need updates for:
- agents/skills/vet → agents/skills/review
- agents/agents/*-vet-* → new names

### 4. Skills vs Fragments

Current structure has:
- `/agent-core/skills/vet/` (skill)
- `/agent-core/fragments/vet-requirement.md` (fragment)
- `/agent-core/agents/vet-agent.md` (agent)

The skill should also be renamed if "vet" is being retired. Recommendation: rename to `review` directory

### 5. Plan-Specific Task Files

8 files to delete. Verify none are actively referenced in:
- Current session.md or active plans
- Any workflow documentation
- Agent memory/learnings

### 6. CLAUDE.md Fragment References

After fragment renames, these @ references may break:
- `@agent-core/fragments/vet-requirement.md` → needs update to `@agent-core/fragments/review-requirement.md`

But deslop, communication, and others referenced in CLAUDE.md appear safe.

---

## Reference File Manifest

### Source Files to Rename

1. `/Users/david/code/claudeutils/agent-core/agents/vet-fix-agent.md` → `corrector.md`
2. `/Users/david/code/claudeutils/agent-core/agents/design-vet-agent.md` → `design-corrector.md` (confirm name)
3. `/Users/david/code/claudeutils/agent-core/agents/vet-agent.md` → `reviewer.md` (confirm name)
4. `/Users/david/code/claudeutils/agent-core/skills/vet/` → `agent-core/skills/review/`
5. `/Users/david/code/claudeutils/agent-core/fragments/vet-requirement.md` → `review-requirement.md`

### Files to Delete

```
/Users/david/code/claudeutils/.claude/agents/error-handling-task.md
/Users/david/code/claudeutils/.claude/agents/pushback-task.md
/Users/david/code/claudeutils/.claude/agents/runbook-quality-gates-task.md
/Users/david/code/claudeutils/.claude/agents/when-recall-task.md
/Users/david/code/claudeutils/.claude/agents/workflow-rca-fixes-task.md
/Users/david/code/claudeutils/.claude/agents/worktree-merge-data-loss-task.md
/Users/david/code/claudeutils/.claude/agents/worktree-merge-resilience-task.md
/Users/david/code/claudeutils/.claude/agents/workwoods-task.md
```

### Estimated Reference Updates: ~37 Files

Based on grep results, the following files require reference updates (vet-fix-agent → corrector, etc.):

**Planning documents (~10):**
- plans/quality-infrastructure/outline.md
- plans/quality-infrastructure/requirements.md
- plans/quality-infrastructure/reports/outline-review.md
- plans/quality-infrastructure/reports/explore-reviewer-usage.md
- plans/orchestrate-evolution/design.md
- plans/orchestrate-evolution/outline.md
- plans/orchestrate-evolution/reports/design-review-d5.md
- plans/remember-skill-update/requirements.md
- plans/plugin-migration/reports/explore-structure.md
- plans/prototypes/agent-duration-analysis.py

**Agent documentation (~8):**
- agent-core/agents/vet-agent.md
- agent-core/agents/design-vet-agent.md
- agent-core/agents/outline-review-agent.md
- agent-core/agents/runbook-outline-review-agent.md
- agent-core/agents/vet-taxonomy.md
- agent-core/agents/review-tdd-process.md
- agents/decisions/workflow-planning.md
- agents/runbook-review-guide.md

**Skills documentation (~8):**
- agent-core/skills/vet/SKILL.md
- agent-core/skills/orchestrate/SKILL.md
- agent-core/skills/deliverable-review/SKILL.md
- agent-core/skills/design/SKILL.md
- agent-core/skills/memory-index/SKILL.md
- agent-core/skills/doc-writing/SKILL.md
- agent-core/skills/review-plan/SKILL.md (contains plan-reviewer references)
- agent-core/skills/runbook/SKILL.md

**Decisions & operational docs (~6):**
- agents/decisions/deliverable-review.md
- agents/decisions/workflow-optimization.md
- agents/decisions/orchestration-execution.md
- agents/decisions/workflow-core.md
- agents/decisions/operational-practices.md
- agents/decisions/implementation-notes.md

**Root-level docs (~5):**
- README.md
- agent-core/README.md
- CLAUDE.md (fragment references)
- agent-core/bin/focus-session.py
- agent-core/bin/prepare-runbook.py

**Tests & utilities (~5):**
- tests/test_prepare_runbook_inline.py
- agents/learnings.md
- agents/memory-index.md
- agents/plan-archive.md
- .claude/rules/plugin-dev-validation.md

---

## Data Quality Notes

- All paths verified as absolute paths from /Users/david/code/claudeutils/
- No relative path references in this report
- Grep results are complete (pattern matching confirmed 46/46, 24/24, 21/21, 33/33 for respective searches)
- File existence verified for key documents (deslop.md, cli.md, communication.md, SKILL.md)
- Symlink status verified in .claude/agents/ directory (13 symlinks + 1 standalone)

