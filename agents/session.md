# Session: Worktree — Worktree CLI default

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Worktree CLI default** — Positional = task name, `--branch` = bare slug | `/runbook plans/worktree-cli-default/outline.md` | sonnet
  - Plan: worktree-cli-default | Status: designed
  - `--branch` creates worktree from existing branch (no session.md handling)
  - Scope expansion: Eliminate Worktree Tasks section, remove `_update_session_and_amend` ceremony, co-design with session.md validator
  - Absorbs: pre-merge untracked file fix (`new` leaves session.md untracked), worktree skill adhoc mode (covered by `--branch`), `--slug` override for `--task` mode (25-char slug limit vs prose task names)
  - `rm --confirm` gate: replace with merge-status check (is branch ancestor of HEAD?). Current gate provides no safety, gives wrong error message ("use wt merge" when user already merged), agent retries immediately with `--confirm`

## Blockers / Gotchas

- Fix: worktree-cli-default adds `--branch` flag
**Merge resolution produces orphaned lines in append-only files:**

## Reference Files

- `plans/worktree-cli-default/outline.md` — CLI change design (positional=task, --branch=slug)
