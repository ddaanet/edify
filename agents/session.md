# Session: Worktree — Worktree merge resilience

**Status:** Deliverable review complete. 4 Major findings to fix before merge. Vet invariant scope design created for import to main.

## Completed This Session

**Deliverable review (3 parallel opus agents + Layer 2 interactive):**
- 4 Major, 12 Minor findings across 11 files (3007 lines)
- Report: `plans/worktree-merge-resilience/reports/deliverable-review.md`
- Layer 1 reports: `deliverable-review-code.md`, `deliverable-review-tests.md`, `deliverable-review-prose.md`

**Process analysis — 0/4 Majors belonged at deliverable review layer:**
- Major #1 (parent_conflicts auto-resolution): outline review gap — D-5 didn't specify resume behavior
- Major #2 (precommit stdout dropped): Phase 5 vet verified delta not invariant
- Major #3 (submodule MERGE_HEAD lifecycle): final checkpoint missed cross-cutting lifecycle audit — same class as exit code audit already performed
- Major #4 (resolve.py err=True): Phase 5 vet scope narrower than invariant domain

**Vet invariant scope design:** `plans/vet-invariant-scope/design.md` — three changes: verification scope field in vet execution context, lifecycle audit at final checkpoint, resume completeness in outline review. Packaged for import to main via `git show worktree-merge-resilience:plans/vet-invariant-scope/design.md`.

**Orchestration (23 commits, b69ff220..3c063383):**
- Phase 1-5 complete, 5 vet checkpoints, TDD process reviewed
- Key escalations: Cycle 1.2 haiku regression (sonnet fixed), Cycle 3.2 haiku stuck (sonnet restart)

**Prior sessions (committed):**
- Designed, created runbook (13 steps, 5 phases), all phases reviewed, prepare-runbook.py generated artifacts
- Reviewed all 13 steps, fixed model metadata issues, added Model Directives to orchestrator-plan.md

## Pending Tasks

- [ ] **Fix parent_conflicts auto-resolution** — `merge()` parent_conflicts route (merge.py:327-333) skips `resolve_session_md`, `resolve_learnings_md`, and agent-core --ours. Agent gets stuck on auto-resolvable files after partial conflict resolution. FR-5 gap.
- [ ] **Fix precommit output forwarding** — merge.py:313 echoes `precommit_result.stderr` but drops `.stdout`. Lint tools write diagnostics to stdout. SKILL.md step 5 assumes complete output.
- [ ] **Fix submodule MERGE_HEAD lifecycle** — Phase 2 submodule conflict leaves MERGE_HEAD in agent-core. If parent merge succeeds (exit 0, no source conflicts), MERGE_HEAD persists indefinitely. Re-run can't clean it up. D-2 gap: exit 0 gives no signal that submodule resolution needed.
- [ ] **Fix resolve.py err=True in merge path** — Two `click.echo(..., err=True)` calls at resolve.py:100,105 execute during Phase 3 merge. D-8 violation. Change to `click.echo()`.
- [ ] **Fix prepare-runbook.py model override** — Script defaults all step metadata to baseline `haiku`, ignoring per-step `**Execution Model:**` in phase file content. Parse and propagate.
- [ ] **Design model directive pipeline** — Model guidance flows design → runbook → execution. Add review/refactor model fields to runbook format, design stage outputs model recommendations per phase, runbook refines. Directional constraint: runbook can upgrade but not downgrade design recommendations without justification. | opus
  - Touches: design skill, outline format, runbook skill, prepare-runbook.py, orchestrate skill, plan-reviewer
  - Prerequisite: fix prepare-runbook.py model override (execution model propagation is foundation)
- [ ] **Fix plan-reviewer model adequacy gap** — Reviewer doesn't assess per-cycle model adequacy when no explicit model tagged. Add criterion: flag cycles where complexity exceeds default model capability. Currently only checks explicitly tagged steps. | opus

## Blockers / Gotchas

- **Never run `git merge` without sandbox bypass** — partial checkout + sandbox failure leaves orphaned files
- **Learnings at 191 lines** — well over 80-line soft limit, but no entries old enough (≥7 active days) for consolidation batch. Will resolve as entries age.
- **First 4 pending tasks block worktree merge** — fix deliverable review Majors before `wt merge`

## Reference Files

- `plans/worktree-merge-resilience/outline.md` — design (8 decisions, D-1 through D-8)
- `plans/worktree-merge-resilience/reports/deliverable-review.md` — consolidated review (4 Major, 12 Minor)
- `plans/vet-invariant-scope/design.md` — process improvement design (for import to main)
- `src/claudeutils/worktree/merge.py` — main merge logic (341 lines)
- `src/claudeutils/worktree/merge_state.py` — state detection + untracked file recovery
- `agent-core/skills/worktree/SKILL.md` — Mode C updated with exit code 3

## Next Steps

Fix the 4 deliverable review Majors (parent_conflicts, precommit output, MERGE_HEAD lifecycle, resolve.py err=True), then merge worktree.
