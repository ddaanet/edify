# Cycle 6.2

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

**GREEN Phase:**

**Implementation:** Add submodule coordination to `commit_pipeline()`

**Behavior:**
- Partition `input.files` by submodule path prefix (using `discover_submodules()`)
- For each submodule with files:
  - Check `input.submodules` has message for this path → error if missing
  - Stage submodule files: `_git("-C", path, "add", *submod_files)`
  - Commit submodule: `_git("-C", path, "commit", "-m", submod_message)`
  - Stage pointer: `_git("add", path)`
- For orphaned submodule messages (path in `input.submodules` but no files): emit warning
- Commit parent with remaining files + staged pointers
- Output: submodule output prefixed with `<path>:`, parent output unlabeled

**Changes:**
- File: `src/claudeutils/session/commit.py`
  Action: Add submodule partitioning and coordination to `commit_pipeline()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---
