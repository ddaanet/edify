# Session Handoff: 2026-03-06

**Status:** All 8 prose quick wins completed. Branch ready for deliverable review and merge.

## Completed This Session

**Prose quick wins (7/8 — prior session):**
- Agentic prose terminology: 3 files — category labels in `complexity-routing-grounding.md` (2), `complexity-routing-internal-codebase.md`. Descriptive "LLM-consumed" uses preserved.
- Memory-index loading docs: 2 files — `migration-guide.md` (removed stale @-ref suggestion), `workflow-advanced.md` (corrected always-loaded claim). Skill/agent "skip if already in context" refs correct (within-session reads).
- Wt merge-rm shorthand: Mode D added to `worktree/SKILL.md` — chains merge + rm. Usage note updated.
- Corrector removal audit: Decision entry in `workflow-planning.md` — corrector must verify removal covers all callers/purposes. Memory-index entry added. Evidence: task-classification D-4 incident.
- Runbook outline review: User review gate added to `tier3-planning-process.md` Phase 0.75 step 5. Iterative fix cycle until user approves.
- Review auto-commit: Continuation frontmatter + section added to `deliverable-review/SKILL.md`. Default-exit chains `/handoff` → `/commit`.
- Task notation migration: `[✗]` → `[†]` in 3 active behavioral files: `task-failure-lifecycle.md`, `error-classification.md`, `handoff/SKILL.md`. Test fixture preserved (parser test data).

**Command lint gate (8/8):**
- FR-1: `check_command_presence()` — pending/in-progress tasks must have backtick commands. Checkbox-aware exemptions for completed/blocked/failed/canceled.
- FR-2: `check_skill_allowlist()` — 7-entry workflow skill allowlist (`requirements`, `design`, `runbook`, `orchestrate`, `deliverable-review`, `inline`, `ground`). Hardcoded per C-2 — filesystem discovery rejected (would auto-accept non-task skills).
- FR-3: Wired into `session_structure.py` precommit pipeline alongside existing `check_command_semantics()`.
- FR-4: `_validate_task_command()` in `worktree/cli.py` — validates before `_setup_worktree_safe()`, fails early on missing/invalid commands.
- Discussion: restricted scope from all-skills to workflow allowlist after empirical analysis of 18 historical skill commands in task entries (7 active after filtering retired/in-session/deprecated).
- 6 files changed, 324 insertions, 40 deletions. All 1614 tests pass.

## In-tree Tasks

- [x] **Command lint gate** — `/requirements` then `/design` | sonnet
  - Precommit lint: scan backtick commands in task entries for executability
  - Existing framework: `src/claudeutils/validation/tasks.py`

## Next Steps

Branch work complete.
