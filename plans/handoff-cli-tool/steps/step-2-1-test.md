# Cycle 2.1

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.1: git_status strip bug

**Finding:** M#10

**Prerequisite:** Read `src/claudeutils/git.py:84-98`

---

**RED Phase:**

**Test:** `test_git_status_preserves_porcelain_format`
**Assertions:**
- In a repo with a modified (unstaged) file, `git_status()` output line starts with ` M ` (space-M-space), not `M ` (M-space)
- Full XY status code preserved for every line, not just first
- Empty repo returns empty string (backward compat)

**Expected failure:** `AssertionError` — `.strip()` removes leading space from first line, ` M file` becomes `M file`

**Why it fails:** `result.stdout.strip()` strips all leading/trailing whitespace from entire output. First line's leading space (part of XY code) is removed.

**Verify RED:** `pytest tests/test_git_cli.py::test_git_status_preserves_porcelain_format -v`

---
