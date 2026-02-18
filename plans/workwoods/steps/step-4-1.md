# Cycle 4.1

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Cycle 4.1: Add --porcelain flag to ls command

**Prerequisite:** Read current cli.py ls implementation (lines 145-151) to understand existing structure.

**RED Phase:**

**Test:** `test_porcelain_flag_exists`
**Assertions:**
- `claudeutils _worktree ls --porcelain` runs without error
- `claudeutils _worktree ls --help` shows --porcelain flag in help text
- Flag is boolean (no argument required)

**Expected failure:** Unrecognized option --porcelain (flag not added)

**Why it fails:** ls command doesn't accept --porcelain flag yet

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_porcelain_flag_exists -v`

**GREEN Phase:**

**Implementation:** Add @click.option for --porcelain flag to ls command

**Behavior:**
- Add `@click.option("--porcelain", is_flag=True, help="Machine-readable output")`
- Accept porcelain parameter in ls function signature
- When porcelain=True: use existing logic
- When porcelain=False: use new rich output (stub for now)

**Approach:** Click boolean flag, default False (rich output is new default)

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add @click.option("--porcelain") decorator above ls command
  Location hint: Above @worktree.command() decorator for ls (around line 145)

- File: `src/claudeutils/worktree/cli.py`
  Action: Update ls() function signature to accept porcelain: bool parameter
  Location hint: ls function definition (line 146)

- File: `tests/test_worktree_ls_upgrade.py`
  Action: Create test invoking CLI with --porcelain flag via CliRunner
  Location hint: New file, use click.testing.CliRunner

**Verify GREEN:** `pytest tests/test_worktree_ls_upgrade.py::test_porcelain_flag_exists -v`
**Verify no regression:** `pytest tests/test_worktree_ls_upgrade.py -v`

---
