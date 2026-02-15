# Session: Worktree — Worktree fixes

**Status:** Focused worktree for parallel execution.

## Completed This Session

**Runbook planning:**
- Tier 3 assessment: 4 phases, 25 TDD cycles + 4 general steps
- Runbook outline created at `plans/worktree-fixes/runbook-outline.md`
- Outline reviewed twice: round 1 (4 minor fixed), round 2 (5 minor fixed — cycle consolidation, test reference, duplicate sections)
- RCA on review defects: 3 systemic patterns written to `workflow-improvements/plans/reports/rca-runbook-outline-review.md`
- Outline ready for expansion, blocked on workflow-improvements process fixes

## Pending Tasks

- [ ] **Worktree fixes** — `/runbook plans/worktree-fixes/design.md` | sonnet
  - Plan: worktree-fixes | Status: outlined | **Blocked:** workflow-improvements
  - 5 FRs: task name constraints (FR-1), precommit validation (FR-2), session merge blocks (FR-4), merge commit fix (FR-5), session automation (FR-6)
  - 4 phases: P0 TDD (FR-1,2), P1 TDD (FR-4,5), P2 TDD (FR-6), P3 general (SKILL.md update)
  - Outline reviewed (25 cycles + 4 steps), blocked on runbook generation process fixes

- [ ] **Build pushback into conversation process** → `wt/pushback` — `/design plans/pushback/requirements.md` | opus
- [ ] **Codebase quality sweep** — Tests, deslop, factorization, dead code | sonnet
- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
- [ ] **Design workwoods** — `/design plans/workwoods/requirements.md` | opus
- [ ] **Error handling framework design** → `wt/error-handling` — Resume `/design` Phase B | opus
- [ ] **Execute plugin migration** — Refresh outline then orchestrate | sonnet
- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
- [ ] **Handoff skill memory consolidation worktree awareness** — Only consolidate in main repo or dedicated worktree | sonnet
- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet
- [ ] **Learning ages computation after consolidation** — Verify age calculation correct when learnings consolidated/rewritten | sonnet
- [ ] **Model tier awareness hook** — Hook injecting "Response by Opus/Sonnet/Haiku" into context | sonnet | restart
- [ ] **Precommit validation improvements** — Expand precommit checks | sonnet
- [ ] **Protocolize RED pass recovery** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
- [ ] **Upstream plugin-dev: document skills frontmatter** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` field | sonnet
- [ ] **Workflow improvements** → `workflow-improvements` — Process fixes from RCA + skill/fragment/orchestration cleanup | sonnet
- [ ] **Worktree fixes** → `worktree-fixes` — `/design plans/worktree-fixes/` | opus
## Blockers / Gotchas

- Session merge loses continuation lines (single-line set diff) → worktree-fixes FR-4
- No-op merge skips commit → orphan branch → worktree-fixes FR-5
- Phase 1 is largest phase (9 cycles: session.py + merge.py + cli.py focus_session + phase4 MERGE_HEAD)
- **Runbook generation blocked on workflow-improvements:** 3 process defects (behavioral vacuity detection, review integration, cross-reference verification) must land before `/runbook` expansion
  - RCA: `workflow-improvements/plans/reports/rca-runbook-outline-review.md`
  - Fixes needed in: `agents/decisions/runbook-review.md`, review-fix workflow, cross-reference verification

**All tasks with documentation must have in-tree file references.**

## Reference Files

- `plans/worktree-fixes/requirements.md` — 5 FRs (FR-3 dropped, FR-6 added)
- `plans/worktree-fixes/design.md` — Design document (vetted, ready for runbook)
- `plans/worktree-fixes/runbook-outline.md` — Runbook outline (reviewed, ready for expansion)
- `plans/worktree-fixes/reports/explore-worktree-code.md` — Codebase exploration (function signatures, test patterns)
- `plans/worktree-fixes/reports/design-review.md` — Design vet report (all issues fixed)
- `plans/worktree-fixes/reports/runbook-outline-review.md` — Outline review round 1 (4 minor fixed)
- `plans/worktree-fixes/reports/runbook-outline-review-2.md` — Outline review round 2 (5 minor fixed, 4 recommendations)
- `workflow-improvements/plans/reports/rca-runbook-outline-review.md` — RCA: 3 systemic patterns in outline generation/review

## Next Steps

Unblock by landing workflow-improvements process fixes, then `/runbook plans/worktree-fixes/design.md`.