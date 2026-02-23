# Deliverable Review: remember-skill-update

**Date:** 2026-02-23
**Methodology:** agents/decisions/deliverable-review.md
**Merge base:** `37f2ab32`

## Inventory

| Type | File | + | - |
|------|------|---|---|
| Code | src/claudeutils/validation/learnings.py | +17 | -1 |
| Code | src/claudeutils/when/cli.py | +44 | -13 |
| Code | agent-core/bin/when-resolve.py | +2 | -3 |
| Test | tests/test_validation_learnings.py | +153 | -13 |
| Test | tests/test_when_cli.py | +124 | -43 |
| Agentic prose | agent-core/skills/codify/SKILL.md | +36 | -13 |
| Agentic prose | agent-core/skills/codify/references/consolidation-patterns.md | +26 | -9 |
| Agentic prose | agent-core/skills/handoff/SKILL.md | +8 | -2 |
| Agentic prose | agent-core/skills/handoff/references/consolidation-flow.md | +7 | -8 |
| Agentic prose | agent-core/skills/when/SKILL.md | +3 | -3 |
| Agentic prose | agent-core/skills/how/SKILL.md | +3 | -3 |
| Agentic prose | agent-core/skills/memory-index/SKILL.md | +9 | -6 |
| Agentic prose | agents/decisions/project-config.md | +2 | -2 |
| Human docs | CLAUDE.md | +0 | -4 |

Rename propagation (FR-10, all `/remember` → `/codify`):

| Type | File | + | - |
|------|------|---|---|
| Agentic prose | agents/SYSPROMPT_GENERATION_GUIDE.md | +3 | -3 |
| Agentic prose | agents/decisions/workflow-advanced.md | +1 | -1 |
| Agentic prose | agents/decisions/workflow-core.md | +1 | -1 |
| Agentic prose | agent-core/skills/reflect/SKILL.md | +4 | -4 |
| Agentic prose | agent-core/skills/review/SKILL.md | +1 | -1 |
| Agentic prose | agent-core/skills/handoff/references/learnings.md | +2 | -2 |
| Human docs | agent-core/README.md | +2 | -4 |
| Human docs | agent-core/docs/general-workflow.md | +2 | -2 |
| Human docs | agent-core/docs/migration-guide.md | +1 | -1 |
| Human docs | agent-core/docs/shortcuts.md | +1 | -1 |
| Human docs | agent-core/migrations/001-separate-learnings.md | +2 | -2 |
| Code | agent-core/hooks/userpromptsubmit-shortcuts.py | +1 | -1 |
| Configuration | agent-core/skills/codify/examples/codify-patterns.md | rename |
| Configuration | .claude/skills/codify | symlink |

Non-production artifacts (excluded from review): `.claude/agents/remember-skill-update-task.md` (plan-specific agent, ephemeral)

**Totals:** 31 files, +643/-146, net +497

**Design conformance summary:** All 12 active functional requirements (FR-1 through FR-13, excluding struck FR-7) have corresponding deliverables. No missing deliverables. Excess files are rename propagation (FR-10 scope) — justified.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

### Naming consistency

1. **tests/test_validation_learnings.py:15** — Test fixture preamble references `/remember` (`use '/remember' to consolidate`) while production `agents/learnings.md:5` uses `/codify`. The validator skips preamble (first 10 lines), so behavior is unaffected, but the fixture content diverges from the file it simulates.
   - Axis: Consistency
   - Fix: Change `/remember` → `/codify` in fixture string

### Vestigial reference

2. **agent-core/skills/handoff/references/consolidation-flow.md:24** — Error handling section reads "On error during script execution or agent delegation:" but FR-8 eliminated agent delegation from the consolidation flow. Should read "On error during consolidation:" or similar.
   - Axis: Accuracy
   - Fix: Remove "or agent delegation" from the phrase

## Gap Analysis

| Requirement | Status | Reference |
|-------------|--------|-----------|
| FR-1: When/How prefix | Covered | learnings.py:64-68, SKILL.md:100, handoff SKILL.md:106 |
| FR-2: Min 2 content words | Covered | learnings.py:71-77, SKILL.md:101 |
| FR-3: Precommit enforcement | Covered | cli.py:52 imports validate_learnings (pre-existing wiring) |
| FR-4: Mechanical consolidation | Covered | SKILL.md:68-71, consolidation-patterns.md:90-93 |
| FR-5: Semantic guidance | Covered | SKILL.md:96-113, handoff SKILL.md:105-111 |
| FR-6: Frozen-domain analysis | Covered | reports/frozen-domain-analysis.md |
| FR-7: Migration | Struck | All 54 titles already prefixed |
| FR-8: Inline execution | Covered | SKILL.md:18, consolidation-flow.md:3-4, stale symlinks cleaned |
| FR-9: Inline splitting | Covered | SKILL.md:61, consolidation-flow.md:14-19 |
| FR-10: Rename to /codify | Covered | Directory renamed, 17 files updated, symlinks synced |
| FR-11: Agent routing | Covered | SKILL.md:34, consolidation-patterns.md:34-50 |
| FR-12: CLI simplification | Covered | cli.py rewritten, 8 tests, when/how/memory-index docs updated |
| FR-13: Remove memory-index | Covered | CLAUDE.md -4 lines |

## Summary

- **Critical:** 0
- **Major:** 0
- **Minor:** 2

All functional requirements satisfied. Code is tested (21/21 pass). Agentic prose follows platform conventions (third-person descriptions, imperative body, progressive disclosure). Rename propagation is thorough — `grep -r "/remember" agent-core/ agents/ .claude/ --include="*.md"` returns only plan-file historical references and session.md context.
