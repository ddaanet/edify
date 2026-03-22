# Cycle 2.2

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.2: Handoff uses shared git changes

**Finding:** M#11

**Prerequisite:** Read `src/claudeutils/session/handoff/cli.py:57-72` and `src/claudeutils/git_cli.py:41-76`

---

**RED Phase:**

**Test:** `test_handoff_shows_submodule_changes`
**Assertions:**
- In a repo with dirty submodule, handoff output includes submodule path-prefixed file status
- Output contains `## Submodule:` section header (matching `_git changes` format)
- Parent-only changes still work correctly

**Expected failure:** `AssertionError` — inline subprocess calls `git status --porcelain` and `git diff HEAD` on parent only, ignoring submodules

**Why it fails:** Handoff CLI uses raw subprocess without submodule discovery (lines 57-72).

**Verify RED:** `pytest tests/test_session_handoff.py::test_handoff_shows_submodule_changes -v`

---
