# Review: Phase 1 Checkpoint — Git Extraction + Package Structure

**Scope**: Phase 1 — Extract git utilities (`_git`, `_is_submodule_dirty`, `_is_dirty`) to `claudeutils/git.py`, add `_git changes` command, create session package stubs, update imports in worktree modules.
**Date**: 2026-03-14
**Mode**: review + fix

## Summary

Phase 1 delivers the foundational shared infrastructure: `claudeutils/git.py` with extracted git helpers, `claudeutils/git_cli.py` with the `_git changes` command, and session package stubs registered in the main CLI. Worktree modules updated to import from the new shared location. All tests pass (`just precommit` green). One minor issue fixed; no critical or major issues found.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`_init_repo` helper duplicated across test files**
   - Location: `tests/test_git_helpers.py:14`, `tests/test_git_cli.py:14`
   - Note: Identical `_init_repo` function defined in both files. Extracted to `tests/pytest_helpers.py` (existing non-fixture shared helper module). `fixtures_worktree.py` was not used as it is at the 400-line limit.
   - **Status**: FIXED

## Fixes Applied

- `tests/pytest_helpers.py` — added `init_repo_at(path: Path)` as a module-level helper (matches existing `_init_repo` behavior: git init + user config + README commit via `-C` flags)
- `tests/test_git_helpers.py` — removed local `_init_repo` definition; imports `init_repo_at as _init_repo` from `tests.pytest_helpers`
- `tests/test_git_cli.py` — removed local `_init_repo` definition and redundant inline init in `_add_submodule_gitlink`; imports `init_repo_at as _init_repo` from `tests.pytest_helpers`

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| S-1: Package structure — `_handoff`, `_commit`, `_status` registered via `cli.add_command()` | Satisfied | `cli.py:155-158` |
| S-2: `_git()` extraction to `claudeutils/git.py` with submodule discovery | Satisfied | `git.py:10-65` |
| S-2: Update worktree imports | Satisfied | `worktree/cli.py:13`, `merge.py:9`, `merge_state.py:7`, `remerge.py:8`, `resolve.py:9` |
| S-5: `_git changes` unified parent + submodule output | Satisfied | `git_cli.py:40-76` |
| S-5: Discovers submodules via git (no hardcoded names in changes command) | Satisfied | `git_cli.py:58` uses `discover_submodules()` |
| S-3: All output to stdout, exit code carries signal | Satisfied | `_fail()` in `git.py:33-39`, no stderr usage |
| Tests — CliRunner + real git repos via tmp_path | Satisfied | `test_git_helpers.py`, `test_git_cli.py` |

---

## Positive Observations

- `_fail()` carries `Never` return type — enables exhaustiveness checking in callers without special cases
- `_git_ok()` boolean pattern aligns with recall entry: "when checking expected program state — `_git_ok()` boolean pattern, not exception-based"
- `git_ops.py` re-exports `_git`, `_is_dirty`, `_is_submodule_dirty` with `# noqa: F401` — preserves backward compatibility for any callers importing from the old location without silently breaking them
- `discover_submodules()` handles the status character prefix correctly (strips leading `[+-U ]` + hash before extracting path)
- `_is_submodule_dirty` generalized from hardcoded `agent-core` to path parameter — correct for shared infrastructure
- `_check_not_dirty` in `worktree/cli.py` updated to pass `"agent-core"` explicitly — correct transition: worktree-specific knowledge stays at the call site
- Test for `_add_submodule_gitlink` uses git plumbing (`update-index --cacheinfo 160000`) to register the gitlink without requiring a real clone — robust test isolation
- `changes_cmd` emits `"Tree is clean."` when nothing dirty — informational output for LLM callers consistent with S-3 design
- Session stub commands registered as hidden, raise `NotImplementedError` — clean placeholder that fails loudly if accidentally invoked before implementation

## Notes

- `except FileNotFoundError, subprocess.CalledProcessError:` style in `worktree/cli.py` lines 110 and 182 — valid Python 3.14 syntax. AST confirms these parse as `Tuple` exception types (not Python 2 name-binding). Equivalent to `except (FileNotFoundError, subprocess.CalledProcessError):`.
- `clean-tree` command (`worktree/cli.py:195`) still hardcodes `agent-core` for its submodule check — this is pre-existing code unchanged by Phase 1. The design's submodule discovery generalization applies to the new `_git changes` command; `clean-tree` is exempt.
- Task prompt listed `tests/test_worktree_rm_dirty.md` — the actual file is `tests/test_worktree_rm_dirty.py`. The `.py` file exists and has been updated to import from `claudeutils.git`.
