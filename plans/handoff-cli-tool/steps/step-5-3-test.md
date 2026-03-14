# Cycle 5.3

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 5

---

## Phase Context

Markdown stdin parser (commit-specific format) and scripted vet check.

---

---

## Cycle 5.3: Scripted vet check (C-1)

**RED Phase:**

**Test:** `test_vet_check_no_config`, `test_vet_check_pass`, `test_vet_check_unreviewed`, `test_vet_check_stale`
**File:** `tests/test_session_commit.py`

Tests use `tmp_path` with pyproject.toml and plan report directories.

**Assertions:**
- `vet_check(files)` with no `[tool.claudeutils.commit]` section in pyproject.toml → passes (opt-in, returns `VetResult(passed=True)`)
- `vet_check(files)` with `require-review = ["src/**/*.py"]` and file `src/foo.py` in files, with report `plans/bar/reports/vet-review.md` newer than `src/foo.py` → passes
- `vet_check(files)` with matching pattern but no report file → fails with `VetResult(passed=False, reason="unreviewed", unreviewed_files=["src/foo.py"])`
- `vet_check(files)` with report older than newest matching file → fails with `VetResult(passed=False, reason="stale", stale_info=...)`
- Files not matching any pattern are not checked (non-production files pass freely)

**Expected failure:** `ImportError`

**Why it fails:** No vet check function

**Verify RED:** `pytest tests/test_session_commit.py::test_vet_check_no_config -v`

---
