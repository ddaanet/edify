# Session: Worktree — Worktree merge data loss

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Worktree merge data loss** — Resume `/design` Phase C (generate design) | sonnet
  - Outline: `plans/worktree-merge-data-loss/outline.md` (Phase B complete)
  - Two root causes: (1) merge doesn't include parent repo changes, (2) `rm` CLI suggests `git branch -D` which agents follow
  - Three tracks: removal safety guard, skill update, merge correctness investigation
  - Key decisions: D-1 focused-session detection via marker text, D-2 `rm` exit codes, D-3 no destructive instructions in CLI output
  - Reports: `plans/worktree-merge-data-loss/reports/` (explore-merge-logic, explore-git-history, outline-review)
