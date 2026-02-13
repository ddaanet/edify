# Cycle 3.1

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.1: Mode detection (trigger vs .section vs ..file)

**Design note:** Mode detection tests routing logic first (not simplest happy path). This is foundation for all three resolution modes — without mode detection, no mode can execute. Testing meta-behavior first is acceptable when it's minimal infrastructure.

**RED Phase:**

**Test:** `test_mode_detection`
**Assertions:**
- Query `"writing mock tests"` → trigger mode
- Query `".Mock Patching"` → section mode
- Query `"..testing.md"` → file mode
- Query `"."` → section mode (single dot prefix)
- Query `".."` → file mode (double dot with empty name — should error, tested in 3.9)

**Expected failure:** ImportError — `resolver` module doesn't exist

**Why it fails:** Module `src/claudeutils/when/resolver.py` not yet created

**Verify RED:** `pytest tests/test_when_resolver.py::test_mode_detection -v`

**GREEN Phase:**

**Implementation:** Create `resolver.py` with mode detection logic.

**Behavior:**
- `..` prefix → file mode (strip `..`)
- `.` prefix (single) → section mode (strip `.`)
- Anything else → trigger mode
- Check `..` before `.` (longer prefix first)

**Approach:** Simple string prefix check. Return enum or string indicating mode.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Create module with `resolve(operator, query, index_path, decisions_dir)` function and internal mode detection
  Location hint: New module

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_mode_detection -v`
**Verify no regression:** `pytest tests/ -q`

---
