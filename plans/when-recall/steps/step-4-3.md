# Cycle 4.3

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 4

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
