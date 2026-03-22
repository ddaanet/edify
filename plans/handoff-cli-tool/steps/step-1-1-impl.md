# Cycle 1.1

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 1

---

**GREEN Phase:**

**Implementation:** Add returncode propagation to commit helpers

**Behavior:**
- `_git_commit` returns `tuple[bool, str]` — `(returncode == 0, stdout or stderr)`
- `_commit_submodule` returns `tuple[bool, str]` with same pattern
- `commit_pipeline` checks boolean, returns `CommitResult(success=False)` on failure
- `_stage_files` and `_commit_submodule` git-add `CalledProcessError` caught in pipeline, returned as `CommitResult(success=False, output="**Error:** staging failed: {stderr}")`

**Changes:**
- File: `commit_pipeline.py`
  Action: Change `_git_commit` to return `(result.returncode == 0, result.stdout.strip() if ok else result.stderr.strip())`
  Location: `_git_commit` function (lines 62-84)

- File: `commit_pipeline.py`
  Action: Same pattern for `_commit_submodule` return value
  Location: `_commit_submodule` function (lines 110-148)

- File: `commit_pipeline.py`
  Action: Wrap staging calls in try/except CalledProcessError, check commit return tuples
  Location: `commit_pipeline` function (lines 254-290)

**Verify GREEN:** `just green`
