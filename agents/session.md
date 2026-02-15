# Session: Worktree — Worktree fixes

**Status:** Focused worktree for parallel execution.

## Completed This Session

**Phase 0: Task name constraints (FR-1, FR-2) — DONE**
- 6 TDD cycles executed via haiku tdd-task agent
- `validate_task_name_format()` added to `validation/tasks.py` (char set, length, empty checks)
- `derive_slug()` updated: calls validation, removes `max_length` param (lossless)
- Precommit integration: `validate()` calls format check on all task names
- 5 existing task names renamed to comply with 25-char limit
- Tests extracted to `tests/test_validation_task_format.py` (line limit)
- Vet: all issues fixed, no UNFIXABLE

**Phase 1: Merge fixes (FR-4, FR-5) — DONE (vet pending)**
- 9 TDD cycles: 4 via sonnet, 4 via sonnet, 1 via haiku
- New module `src/claudeutils/worktree/session.py`: `TaskBlock`, `extract_task_blocks()`, `find_section_bounds()`
- `_resolve_session_md_conflict()` rewritten: block-based comparison, uses `find_section_bounds()` for insertion
- `_phase4_merge_commit_and_precommit()` rewritten: MERGE_HEAD detection, `--allow-empty` for empty-diff merges
- `focus_session()` refactored to use `extract_task_blocks()`
- Test file compression: `test_worktree_merge_conflicts.py` 678→260 lines (helper functions, shared setup)
- `test_focus_session_multiline` moved to `test_worktree_session.py`
- New `tests/test_worktree_merge_merge_head.py` for MERGE_HEAD tests
- `just dev` passes (869/870 + 1 xfail)

**SKILL.md attempted then reverted:**
- Phase 3 prose edits applied inline, skill-reviewer found critical: automation claims reference unimplemented code
- Reverted all 4 SKILL.md edits — must follow Phase 2

## Pending Tasks

- [>] **Worktree fixes** — Phase 1 vet + Phase 2 + Phase 3 remaining | sonnet
  - Plan: worktree-fixes | Status: executing
  - Phase 0: complete (6 cycles, vetted)
  - Phase 1: complete (9 cycles, vet pending)
  - Phase 2: not started (10 cycles: session automation FR-6)
  - Phase 3: not started (4 SKILL.md edits, inline after Phase 2)

- [ ] **Build pushback** → `wt/pushback` — `/design plans/pushback/requirements.md` | opus
- [ ] **Codebase quality sweep** — Tests, deslop, factorization, dead code | sonnet
- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
- [ ] **Design workwoods** — `/design plans/workwoods/requirements.md` | opus
- [ ] **Error handling design** → `wt/error-handling` — Resume `/design` Phase B | opus
- [ ] **Execute plugin migration** — Refresh outline then orchestrate | sonnet
- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
- [ ] **Handoff consol scope** — Only consolidate in main repo or dedicated worktree | sonnet
- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet
- [ ] **Learning ages consol** — Verify age calculation correct when learnings consolidated/rewritten | sonnet
- [ ] **Model tier awareness hook** — Hook injecting "Response by Opus/Sonnet/Haiku" into context | sonnet | restart
- [ ] **Precommit improvements** — Expand precommit checks | sonnet
- [ ] **RED pass recovery** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
- [ ] **Upstream skills field** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` field | sonnet
- [ ] **Workflow improvements** → `workflow-improvements` — Process fixes from RCA + skill/fragment/orchestration cleanup | sonnet

## Blockers / Gotchas

- Phase 1 vet still needed before Phase 2 can start
- Phase 3 SKILL.md edits must follow Phase 2 (automation code must exist before skill claims it)
- **Do NOT use `/runbook` or `/orchestrate`** — pipeline is blocked on workflow-improvements. Execute directly:
  - TDD phases: delegate to `tdd-task` agent with outline + design context (no expanded runbook needed)
  - Skill edits: apply inline, then run `skill-reviewer` agent
  - Phase 1 was executed from `runbook-outline.md` + `design.md` without expansion — same approach for Phase 2

## Reference Files

- `plans/worktree-fixes/requirements.md` — 5 FRs (FR-3 dropped, FR-6 added)
- `plans/worktree-fixes/design.md` — Design document
- `plans/worktree-fixes/runbook-outline.md` — Runbook outline
- `plans/worktree-fixes/runbook-phase-0.md` — Phase 0 expanded runbook
- `plans/worktree-fixes/reports/phase-0-execution.md` — Phase 0 execution report
- `plans/worktree-fixes/reports/phase-0-vet.md` — Phase 0 vet report
- `plans/worktree-fixes/reports/phase-1-execution.md` — Phase 1 execution report
- `plans/worktree-fixes/reports/explore-worktree-code.md` — Codebase exploration

## Next Steps

1. Vet Phase 1 (vet-fix-agent with scope: session.py, merge.py, cli.py focus_session, _phase4)
2. Execute Phase 2: 10 TDD cycles (move_task_to_worktree, remove_worktree_task, CLI wiring)
3. Phase 2 checkpoint (fix + vet + functional)
4. Phase 3: SKILL.md prose edits inline + skill-reviewer
