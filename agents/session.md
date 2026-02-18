# Session: Worktree — Worktree merge resilience

**Status:** Fix plan ready for execution. 4 Major deliverable review findings batched into diamond TDD plan.

## Completed This Session

**Fix plan design (diamond TDD for 4 Majors):**
- Batched all 4 deliverable review Majors into single execution plan
- Diamond structure: 4 RED integration tests → 4 fixes → all GREEN + regression
- Plan: `plans/worktree-merge-resilience/fix-plan.md`
- Key decisions: integration-test-first (not per-fix TDD), exit 3 for orphaned submodule MERGE_HEAD, helper extraction for auto-resolution dedup

**Deliverable review (3 parallel opus agents + Layer 2 interactive):**
- 4 Major, 12 Minor findings across 11 files (3007 lines)
- Report: `plans/worktree-merge-resilience/reports/deliverable-review.md`

**Vet invariant scope design:** `plans/vet-invariant-scope/design.md` — packaged for import to main.

**Orchestration (23 commits, b69ff220..3c063383):**
- Phase 1-5 complete, 5 vet checkpoints, TDD process reviewed

**Prior sessions (committed):**
- Designed, created runbook (13 steps, 5 phases), all phases reviewed, prepare-runbook.py generated artifacts

## Pending Tasks

- [ ] **Execute fix plan (4 Majors)** — Diamond TDD: write 4 RED integration tests, apply fixes (#4→#2→#1→#3), verify GREEN + regression
  - Plan: `plans/worktree-merge-resilience/fix-plan.md`
  - Fixes: parent_conflicts auto-resolution, precommit stdout, submodule MERGE_HEAD lifecycle, resolve.py err=True
  - Fix #1 edge case: if ALL conflicts auto-resolvable, fall through to Phase 4 (not exit 3 with empty report)
  - After fixes: tighten `test_merge_continues_to_phase3_when_submodule_conflicts` from `in (0, 3)` to exact exit code
- [ ] **Fix prepare-runbook.py model override** — Script defaults all step metadata to baseline `haiku`, ignoring per-step `**Execution Model:**` in phase file content. Parse and propagate.
- [ ] **Design model directive pipeline** — Model guidance flows design → runbook → execution. Add review/refactor model fields to runbook format, design stage outputs model recommendations per phase, runbook refines. Directional constraint: runbook can upgrade but not downgrade design recommendations without justification. | opus
  - Touches: design skill, outline format, runbook skill, prepare-runbook.py, orchestrate skill, plan-reviewer
  - Prerequisite: fix prepare-runbook.py model override (execution model propagation is foundation)
- [ ] **Fix plan-reviewer model adequacy gap** — Reviewer doesn't assess per-cycle model adequacy when no explicit model tagged. Add criterion: flag cycles where complexity exceeds default model capability. Currently only checks explicitly tagged steps. | opus

## Blockers / Gotchas

- **Never run `git merge` without sandbox bypass** — partial checkout + sandbox failure leaves orphaned files
- **Learnings at 199 lines** — well over 80-line soft limit, but no entries old enough (≥7 active days) for consolidation batch. Will resolve as entries age.
- **Fix plan blocks worktree merge** — execute fix plan before `wt merge`

## Reference Files

- `plans/worktree-merge-resilience/fix-plan.md` — diamond TDD fix plan (4 Majors batched)
- `plans/worktree-merge-resilience/outline.md` — design (8 decisions, D-1 through D-8)
- `plans/worktree-merge-resilience/reports/deliverable-review.md` — consolidated review (4 Major, 12 Minor)
- `plans/vet-invariant-scope/design.md` — process improvement design (for import to main)
- `src/claudeutils/worktree/merge.py` — main merge logic (341 lines)
- `src/claudeutils/worktree/merge_state.py` — state detection + untracked file recovery
- `src/claudeutils/worktree/resolve.py` — conflict resolution (err=True fix targets)

## Next Steps

Execute `plans/worktree-merge-resilience/fix-plan.md` — diamond TDD for 4 deliverable review Majors, then merge worktree.
