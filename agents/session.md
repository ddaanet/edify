# Session: Worktree — Worktree merge data loss

**Status:** Focused worktree for parallel execution.

## Completed This Session

- Design document generated and vetted (`plans/worktree-merge-data-loss/design.md`)
  - Three tracks: removal safety guard (cli.py rm), merge correctness (merge.py Phase 4), skill update (SKILL.md Mode C)
  - Design review: Ready, 1 major + 2 minor issues fixed by vet, no UNFIXABLE
  - Report: `plans/worktree-merge-data-loss/reports/design-review.md`
  - Checkpoint commit: 9f7c51e

- Runbook outline generated and reviewed (`plans/worktree-merge-data-loss/runbook-outline.md`)
  - Tier 3 assessment: Full runbook (13 TDD cycles, 2 independent tracks)
  - Automated review: 4 major + 4 minor issues fixed, all FIXED (no UNFIXABLE)
  - Checkpoint commit: 1d03b8b

- Interactive opus outline review completed (was pending task)
  - Found 1 major (Cycle 1.7 probe ordering vs design flow diagram) + 2 minor (branch deletion flags, branch-not-found case)
  - All 3 fixes applied to outline: bbbc9df
  - Opus sub-agent review report: `plans/worktree-merge-data-loss/reports/runbook-outline-review-opus.md`

- Review agent quality diagnostic and fix
  - RCA: sonnet review agent produces ungrounded corrections during fix-all (confabulated operation list, removed design features, fabricated file sizes)
  - 2×2 controlled experiment: test worktrees `runbook-opus-test` (opus gen+review) and `runbook-sonnet-test` (opus gen+sonnet review) at commit e7b4164
  - Session transcript scraped to compare delegation prompts (equivalent — eliminated as variable)
  - Primary cause: model tier (sonnet lacks grounding discipline). Contributing: agent instructions lack design-reference constraint
  - Fix: outline review agent `model: sonnet` → `model: opus`, grounding constraint added to fix-all policy
  - Decision record: `agents/decisions/pipeline-contracts.md` (section: "When Outline Review Produces Ungrounded Corrections")
  - Diagnostic procedure documented: `agents/decisions/operational-practices.md` (section: "When Diagnosing Review Agent Quality Gaps")
  - Test branches merged with revert (history preserved), worktrees cleaned up: 03a058b

## Pending Tasks

- [ ] **Expand runbook** — `/runbook plans/worktree-merge-data-loss/design.md` | sonnet
  - Outline reviewed and fixed, ready for full phase expansion
  - Phase 1: 13 TDD cycles (Track 1 removal guard + Track 2 merge correctness), haiku execution
  - Phase 2: 1 general step (SKILL.md Mode C), haiku execution
  - Opus review findings to incorporate during expansion: `plans/worktree-merge-data-loss/reports/runbook-outline-review-opus.md`
- [ ] **Design-to-deliverable** — Design session for tmux-like session clear/model switch/restart automation | opus | restart
- [ ] **Worktree skill adhoc mode** — Add mode for creating worktree from specific commit without task tracking | sonnet

## Blockers / Gotchas

- Diagnostic procedure (`agents/decisions/operational-practices.md`) may be needed again during full runbook expansion — if expansion quality is suspect, run 2×2 experiment on the expansion agent
- cli.py at 382 lines, projected 417 after guard implementation — monitor growth, extract `_create_session_commit` if exceeding 420

## Next Steps

Expand runbook: `/runbook plans/worktree-merge-data-loss/design.md`
