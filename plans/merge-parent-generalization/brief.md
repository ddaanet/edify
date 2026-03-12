# Brief: Merge Parent Generalization

## Problem

`_worktree merge` is hardcoded to two directions: branch→main (default) and main→branch (`--from-main`). No `--parent <branch>` parameter exists. This forces a "merge everything back to main and recreate trees" workflow when work branches off other work branches.

The post-design-split convention (sub-problems become separate tasks post-design) creates worktree-from-worktree workflows where a child task's worktree branches from a parent task's worktree, not from main. Design changes in the parent need to propagate to children via merge.

## Scope

Generalize `merge.py` to accept an arbitrary parent branch:
- Add `--parent <branch>` parameter to CLI
- Replace `from_main: bool` with `parent: str` internally
- Preserve backward compatibility (`--from-main` → `--parent main`)
- Update validation (Phase 1), merge (Phase 3), and commit (Phase 4) to use parent branch
- Tests for non-main parent merges

## Success Criteria

- `claudeutils _worktree merge --parent <branch> <slug>` works for any named branch
- `--from-main` remains as shorthand for `--parent main`
- Existing merge behavior unchanged when no `--parent` specified

## References

- `src/claudeutils/worktree/merge.py` — current implementation
- `tests/test_worktree_merge_from_main.py`, `tests/test_worktree_merge_parent.py` — existing tests
