# Cycle 4.4

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 4

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
