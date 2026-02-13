# Phase 4: CLI Integration

**Type:** TDD
**Model:** haiku
**Dependencies:** Phase 3 (resolver)
**Files:** `src/claudeutils/when/cli.py`, `tests/test_when_cli.py`, `src/claudeutils/cli.py` (registration)

**Design reference:** cli.py module, Click CLI entry point

**Prior state:** Phase 3 provides `resolve(operator, query, index_path, decisions_dir)` that returns formatted content string or raises `ResolveError`.

**Weak Orchestrator Metadata:** Total Cycles: 5

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

## Cycle 4.2: Operator argument (when/how)

**RED Phase:**

**Test:** `test_operator_argument_validation`
**Assertions:**
- CLI invoked with `claudeutils when when "writing mock tests"` → accepted (operator=when)
- CLI invoked with `claudeutils when how "encode paths"` → accepted (operator=how)
- CLI invoked with `claudeutils when what "some topic"` → rejected by Click (invalid choice)
- Error output contains "Invalid value" for invalid operator

**Expected failure:** AssertionError — operator not validated or all values accepted

**Why it fails:** Operator argument not yet constrained to when/how choices

**Verify RED:** `pytest tests/test_when_cli.py::test_operator_argument_validation -v`

**GREEN Phase:**

**Implementation:** Add operator as Click Choice argument.

**Behavior:**
- First positional argument: `operator` with `click.Choice(["when", "how"])`
- Invalid operators rejected by Click automatically with error message

**Approach:** `@click.argument("operator", type=click.Choice(["when", "how"]))`

**Changes:**
- File: `src/claudeutils/when/cli.py`
  Action: Add operator argument with Choice constraint
  Location hint: Command decorator arguments

**Verify GREEN:** `pytest tests/test_when_cli.py::test_operator_argument_validation -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 4.3: Query argument (nargs=-1, variadic)

**RED Phase:**

**Test:** `test_query_variadic_argument`
**Assertions:**
- `claudeutils when when writing mock tests` → query joined as `"writing mock tests"`
- `claudeutils when when .Section` → query is `".Section"` (dot prefix preserved)
- `claudeutils when when ..file.md` → query is `"..file.md"` (double dot preserved)
- `claudeutils when when` (no query args) → error "Missing argument"

**Expected failure:** AssertionError — query not properly joined or not required

**Why it fails:** Query argument not yet implemented as variadic

**Verify RED:** `pytest tests/test_when_cli.py::test_query_variadic_argument -v`

**GREEN Phase:**

**Implementation:** Add variadic query argument.

**Behavior:**
- Remaining positional arguments joined with spaces to form query string
- At least one query word required
- Dot prefixes preserved (no stripping)

**Approach:** `@click.argument("query", nargs=-1, required=True)` then `" ".join(query)` in handler.

**Changes:**
- File: `src/claudeutils/when/cli.py`
  Action: Add query argument with nargs=-1
  Location hint: Command decorator arguments

**Verify GREEN:** `pytest tests/test_when_cli.py::test_query_variadic_argument -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 4.4: Invoke resolver with joined query

**RED Phase:**

**Test:** `test_cli_invokes_resolver`
**Assertions:**
- CLI `claudeutils when when writing mock tests` with valid test index:
  - Output to stdout contains resolved content (heading + section content)
  - Exit code 0
- Output includes navigation links (Broader/Related sections)

**Expected failure:** AssertionError — CLI doesn't call resolver or output is empty

**Why it fails:** CLI command body not yet connected to resolver

**Verify RED:** `pytest tests/test_when_cli.py::test_cli_invokes_resolver -v`

**GREEN Phase:**

**Implementation:** Connect CLI to resolver.

**Behavior:**
- Join query tuple into space-separated string
- Determine index_path and decisions_dir from project root
- Call `resolve(operator, query_str, index_path, decisions_dir)`
- Print result to stdout

**Approach:** Use project root detection (Path.cwd() or CLAUDE_PROJECT_DIR env), call resolve, click.echo().

**Changes:**
- File: `src/claudeutils/when/cli.py`
  Action: Implement command body — root detection, resolve call, output
  Location hint: Command function body

**Verify GREEN:** `pytest tests/test_when_cli.py::test_cli_invokes_resolver -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 4.5: Error handling (print to stderr, exit 1)

**RED Phase:**

**Test:** `test_cli_error_handling`
**Assertions:**
- CLI with nonexistent trigger: exit code 1 (not 0)
- Error message printed to stderr (not stdout)
- Error message contains suggestion text ("Did you mean:" for trigger mode)
- CLI with nonexistent section: exit code 1, stderr contains "not found"
- CLI with nonexistent file: exit code 1, stderr contains "not found"

**Expected failure:** AssertionError — errors printed to stdout or exit code 0

**Why it fails:** Error handling not routing to stderr with correct exit code

**Verify RED:** `pytest tests/test_when_cli.py::test_cli_error_handling -v`

**GREEN Phase:**

**Implementation:** Add error handling with stderr output.

**Behavior:**
- Catch `ResolveError` from resolver
- Print error message to stderr via `click.echo(str(e), err=True)`
- Exit with code 1 via `sys.exit(1)` or `raise SystemExit(1)`

**Approach:** try/except around resolve call. Click's err=True for stderr.

**Changes:**
- File: `src/claudeutils/when/cli.py`
  Action: Add try/except for ResolveError, stderr output, exit code 1
  Location hint: Command function body, around resolve call

**Verify GREEN:** `pytest tests/test_when_cli.py::test_cli_error_handling -v`
**Verify no regression:** `pytest tests/ -q`
