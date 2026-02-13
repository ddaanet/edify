# Cycle 4.1

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Cycle 4.1: Click command setup

**Prerequisite:** Read `src/claudeutils/cli.py:1-30` — understand existing Click group and subcommand registration pattern

**RED Phase:**

**Test:** `test_when_command_exists`
**Assertions:**
- `from claudeutils.when.cli import when_cmd` succeeds (importable)
- `when_cmd` is a Click command (has `click.Command` type or callable with click decorators)
- Invoking CLI with `claudeutils when --help` shows help text (Click runner test)

**Expected failure:** ImportError — `cli` module doesn't exist in `when/`

**Why it fails:** Module `src/claudeutils/when/cli.py` not yet created

**Verify RED:** `pytest tests/test_when_cli.py::test_when_command_exists -v`

**GREEN Phase:**

**Implementation:** Create `cli.py` with Click command and register in main CLI.

**Behavior:**
- Create `when_cmd` Click command
- Register in `src/claudeutils/cli.py` main group via `cli.add_command(when_cmd, "when")`
- Command accepts operator and query arguments

**Approach:** Follow existing pattern from `recall`, `validate`, `statusline` command registration.

**Changes:**
- File: `src/claudeutils/when/cli.py`
  Action: Create with Click command definition
- File: `src/claudeutils/cli.py`
  Action: Add `from claudeutils.when.cli import when_cmd` and `cli.add_command(when_cmd, "when")`
  Location hint: Near other add_command calls

**Verify GREEN:** `pytest tests/test_when_cli.py::test_when_command_exists -v`
**Verify no regression:** `pytest tests/ -q`

---
