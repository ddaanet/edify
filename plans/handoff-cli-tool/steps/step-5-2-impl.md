# Cycle 5.2

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 5

---

## Phase Context

Markdown stdin parser (commit-specific format) and scripted vet check.

---

---

**GREEN Phase:**

**Implementation:** Add `validate_files()` to `src/claudeutils/session/commit_gate.py`

**Behavior:**
- `CleanFileError` exception with `clean_files: list[str]` attribute
- `validate_files(files: list[str], amend: bool = False) -> None`
- Get dirty files: `_git("status", "--porcelain")` → parse paths (column 3+)
- If amend: also get HEAD files: `_git("diff-tree", "--no-commit-id", "--name-only", "HEAD")`
- For each file in `files`: check presence in dirty set (or HEAD set if amend)
- Collect clean files → raise `CleanFileError` with STOP directive

**Changes:**
- File: `src/claudeutils/session/commit_gate.py`
  Action: Create with `CleanFileError`, `validate_files()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit.py -v`
**Verify no regression:** `just precommit`

---
