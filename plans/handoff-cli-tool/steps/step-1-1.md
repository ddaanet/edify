# Step 1.1

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Extract git utilities and establish package structure. Foundation for all subcommands.

---

---

## Step 1.1: Extract git helpers to `claudeutils/git.py`

**Objective:** Move `_git()` and `_is_submodule_dirty()` from `worktree/git_ops.py` to new `claudeutils/git.py`, add `discover_submodules()`, `_git_ok()`, and `_fail()`. Update all import sites.

**Script Evaluation:** Medium (~60 lines new code + import updates across 5 files)

**Execution Model:** Sonnet

**Prerequisite:** Read `src/claudeutils/worktree/git_ops.py:9-23` (current `_git()` implementation) and `src/claudeutils/worktree/git_ops.py:78-112` (current `_is_parent_dirty()` at lines 78-97 and `_is_submodule_dirty()` at lines 100-112 — submodule check hardcodes `"agent-core"`)

**Implementation:**

Create `src/claudeutils/git.py` containing:

1. **`_git(*args, check=True, env=None, input_data=None) -> str`** — moved verbatim from `worktree/git_ops.py:9-23`

2. **`_git_ok(*args) -> bool`** — uses `subprocess.run(["git", *args], check=False, capture_output=True)` and returns `True` if returncode == 0. Must use `subprocess.run` directly (not `_git()`) because `_git()` returns stdout string, not returncode.

3. **`_fail(msg: str, code: int = 1) -> Never`** — `click.echo(msg)` (stdout, not stderr — S-3 convention) then `raise SystemExit(code)`. Return type `Never` informs type checkers.

4. **`discover_submodules() -> list[str]`** — parse `git submodule status` output. Each line starts with space/+/- then commit hash then space then path. Extract path field. Return empty list if no submodules.

5. **`_is_submodule_dirty(path: str) -> bool`** — generalized from `_is_submodule_dirty()`. Accepts submodule path instead of hardcoded `"agent-core"`. Checks `Path(path).exists()` before querying.

6. **`_is_dirty(exclude_path: str | None = None) -> bool`** — moved from `worktree/git_ops.py:78-97` (`_is_parent_dirty`). Renamed to `_is_dirty` in the new module (no callers outside git_ops.py so no import update needed).

**Import updates** (verify scope with `grep -r "from claudeutils.worktree.git_ops import" src/`):
- `worktree/git_ops.py`: Remove `_git`, `_is_submodule_dirty`, `_is_parent_dirty` definitions. Import from `claudeutils.git` instead. Keep worktree-specific functions (`wt_path`, `_classify_branch`, etc.)
- `worktree/cli.py`: Update `from claudeutils.worktree.git_ops import _git, _is_submodule_dirty` → `from claudeutils.git import _git, _is_submodule_dirty`
- `worktree/merge.py`: Same import update pattern
- `worktree/merge_state.py`: Same import update pattern
- `worktree/resolve.py`: Same import update pattern
- `worktree/remerge.py`: Update `from claudeutils.worktree.git_ops import _git` → `from claudeutils.git import _git`

**Tests:** `tests/test_git_helpers.py`
- `test_git_ok_success`: `_git_ok("status")` returns True in a valid git repo
- `test_git_ok_failure`: `_git_ok("log", "--invalidflag")` returns False
- `test_fail_exits`: `_fail("error msg", code=2)` raises SystemExit(2), output contains "error msg"
- `test_discover_submodules_none`: In repo without submodules, returns `[]`
- `test_discover_submodules_present`: In repo with submodule, returns `["submod-name"]`
- `test_is_submodule_dirty_parametrized`: Tests with clean/dirty submodule, nonexistent path

**Expected Outcome:** `just precommit` passes. All existing tests pass (no broken imports). New tests pass.

**Error Conditions:**
- Import site missed → existing tests fail (caught by precommit)
- Function signature change → grep for all call sites before modifying

**Validation:** `just precommit` (runs full test suite + lint)

---
