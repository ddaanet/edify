# Session: Worktree — Worktree rm amend

**Status:** Complete — ready to merge back to main.

## Completed This Session

- [x] **Worktree rm amend** — Implemented Option B: `rm` detects merge commit via parent count, stages+amends session.md
  - `_is_merge_commit()` helper in cli.py — `git rev-list --parents -n 1 HEAD`, checks `len(parts) >= 3`
  - Amend logic in `rm()`: after `remove_worktree_task()`, checks merge commit + session.md dirty, stages + amends
  - Conditional output: "Removed worktree {slug} Merge commit amended." vs "Removed worktree {slug}"
  - SKILL.md Mode C step 3 updated — removed manual `git add && git commit --amend` instruction
  - 4 new tests: merge detection, amend positive, amend negative (normal commit), output message
  - Caught critical off-by-one bug from haiku: `>= 2` → `>= 3` (rev-list output includes commit hash)
  - Lint cleanup: ruff format across 3 files, line-length fix in scrape-validation.py
  - Vet review passed, all fixes applied, `just precommit` green

## Pending Tasks

(none — worktree task complete)

## Reference Files

- `src/claudeutils/worktree/cli.py` — `_is_merge_commit()` + amend logic in `rm()`
- `tests/test_worktree_rm.py` — 7 tests covering rm behavior
- `agent-core/skills/worktree/SKILL.md` — Mode C step 3 (automatic amend)

## Next Steps

Merge worktree back to main: `wt merge worktree-rm-amend`
