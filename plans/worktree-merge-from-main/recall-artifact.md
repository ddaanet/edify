# Recall Artifact: worktree-merge-from-main

## Planning-relevant

- when merge fails on main — rollback pattern, branch self-updates, `--from-main` prerequisite
- when no-op merge orphans branch — always create merge commit
- when failed merge leaves debris — abort + untracked cleanup
- when validating worktree merges — `remerge_session_md` runs phase 4 all paths
- when resolving session.md conflicts during merge — never discard branch-side tasks
- when merging completed tasks from branch — filter `[x]` and `[-]` from additive merge
- when merging worktree with consolidated learnings — delta only post-consolidation
- when adding a new variant to an enumerated system — grep downstream enumeration sites

## Testing-relevant

- when tests simulate merge workflows — branch as merged parent, amend preserves
- when preferring e2e over mocked subprocess — real git repos via tmp_path
- when testing CLI tools — Click CliRunner in-process
- when extracting git helper functions — `_git()` pattern

## Implementation-relevant

- when removing worktrees with submodules — core.worktree restore
- when recovering broken submodule worktree refs — repair links
