# Session: Worktree — Worktree merge resilience

**Status:** Runbook ready for orchestration. Restart required.

## Completed This Session

- Designed worktree merge resilience (outline as design artifact, 8 key decisions D-1 through D-8)
- Created runbook: 5 TDD phases (12 cycles) + 1 general phase (3 steps), 13 total steps
  - Phase 1: state machine + idempotent resume (5 cycles, `_detect_merge_state`)
  - Phase 2: submodule conflict pass-through, `check=False` (2 cycles)
  - Phase 3: remove abort block, untracked `git add` + retry (2 cycles)
  - Phase 4: `_format_conflict_report` with file list, diff stats, divergence, hint (1 cycle)
  - Phase 5: exit code audit, stdout migration, SKILL.md Mode C (3 general steps)
- All 5 phases reviewed (background plan-reviewer agents), holistic cross-phase review done — no UNFIXABLE
- Key fixes from review: Cycle 1.1 GREEN scoped to merged/clean only (incremental state machine); Cycle 2.1 exit code corrected (0 or 3, not 3 — submodule pointer auto-resolves via Phase 3); Cycle 3.2 mock_precommit required for same-content success path
- prepare-runbook.py generated 14 artifacts (13 steps + orchestrator-plan.md + task agent)
- Orchestrate command on clipboard: `/orchestrate worktree-merge-resilience`

## Pending Tasks

- [ ] **Orchestrate worktree merge resilience** — `/orchestrate worktree-merge-resilience` | sonnet | restart
  - Plan: worktree-merge-resilience | Status: planned
  - State machine (Phase 1) is the foundation — all later phases depend on it
  - Holistic review catch: Phase 2 Cycle 2.1 expects exit 0 or 3 (not 3 alone), since agent-core pointer auto-resolves via Phase 3's existing checkout --ours logic

## Blockers / Gotchas

- **Never run `git merge` without sandbox bypass** — partial checkout + sandbox failure leaves orphaned files
- **Existing tests assert abort behavior** — Cycles 3.1 and 3.2 update `test_merge_conflict_surfaces_git_error` and `test_merge_aborts_cleanly_when_untracked_file_blocks` in RED phase (assert new behavior, fail with old code)
- **merge.py growth**: projected ~387 lines after Phase 4. If >350 after Phase 3 GREEN, extract `_format_conflict_report` + state detection into `merge_state.py` before Phase 4.
- **Cycle 1.5 sabotage protocol**: RED requires sabotaging `_detect_merge_state` to return `"merged"` always, confirm failure, then revert before GREEN.
- **validate-runbook.py absent** — Phase 3.5 skipped (graceful degradation per skill spec)

## Reference Files

- `plans/worktree-merge-resilience/outline.md` — design (8 decisions)
- `plans/worktree-merge-resilience/runbook-outline.md` — reviewed outline (12 items)
- `plans/worktree-merge-resilience/orchestrator-plan.md` — orchestration plan
- `plans/worktree-merge-resilience/steps/` — 13 step/cycle files
- `plans/worktree-merge-resilience/reports/` — all review reports (phases 1-5, holistic)

## Next Steps

Restart session. Paste `/orchestrate worktree-merge-resilience` from clipboard.
