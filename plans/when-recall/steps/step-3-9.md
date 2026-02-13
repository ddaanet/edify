# Cycle 3.9

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.9: Error handling — file not found

**RED Phase:**

**Test:** `test_file_not_found_lists_files`
**Assertions:**
- `resolve("when", "..nonexistent.md", index_path, decisions_dir)` raises `ResolveError`
- Error message contains `"File 'nonexistent.md' not found in agents/decisions/."`
- Error message contains `"Available:"` followed by list of actual `.md` files
- Available files formatted as `..filename.md` (one per line)

**Expected failure:** ResolveError raised but without available files list

**Why it fails:** File-not-found error doesn't list alternatives

**Verify RED:** `pytest tests/test_when_resolver.py::test_file_not_found_lists_files -v`

**GREEN Phase:**

**Implementation:** Add file-not-found error with available files list.

**Behavior:**
- When file doesn't exist: raise ResolveError
- List all `.md` files in decisions_dir
- Format: `"File '<name>' not found in agents/decisions/. Available:\n  ..cli.md\n  ..testing.md"`
- Files sorted alphabetically

**Approach:** `sorted(decisions_dir.glob("*.md"))` for file listing.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Add file-not-found error formatting
  Location hint: File mode error branch

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_file_not_found_lists_files -v`
**Verify no regression:** `pytest tests/ -q`

# Phase 4: CLI Integration

**Type:** TDD
**Model:** haiku
**Dependencies:** Phase 3 (resolver)
**Files:** `src/claudeutils/when/cli.py`, `tests/test_when_cli.py`, `src/claudeutils/cli.py` (registration)

**Design reference:** cli.py module, Click CLI entry point

**Prior state:** Phase 3 provides `resolve(operator, query, index_path, decisions_dir)` that returns formatted content string or raises `ResolveError`.

**Weak Orchestrator Metadata:** Total Cycles: 5

---
