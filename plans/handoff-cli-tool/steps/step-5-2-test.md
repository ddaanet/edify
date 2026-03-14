# Cycle 5.2

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 5

---

## Phase Context

Markdown stdin parser (commit-specific format) and scripted vet check.

---

---

## Cycle 5.2: Input validation — clean files check (C-3)

**RED Phase:**

**Test:** `test_validate_files_dirty`, `test_validate_files_clean_error`, `test_validate_files_amend`
**File:** `tests/test_session_commit.py`

Tests use real git repos via `tmp_path`.

**Assertions:**
- `validate_files(files, amend=False)` with all files appearing in `git status --porcelain` → returns normally (no error)
- `validate_files(files, amend=False)` with a clean file (not in `git status --porcelain`) → raises `CleanFileError` with:
  - `clean_files` attribute listing the clean file paths
  - String representation matching exact format: `**Error:** Listed files have no uncommitted changes\n- <path>\n\nSTOP: Do not remove files and retry.`
- `validate_files(files, amend=True)` with a file that's clean in working tree but present in HEAD commit (via `git diff-tree`) → returns normally (amend allows HEAD-committed files)
- `validate_files(files, amend=True)` with a file in neither working tree changes nor HEAD commit → raises `CleanFileError`

**Expected failure:** `ImportError`

**Why it fails:** No validation function

**Verify RED:** `pytest tests/test_session_commit.py::test_validate_files_dirty -v`

---
