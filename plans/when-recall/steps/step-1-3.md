# Cycle 1.3

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.3: Split primary trigger and extra triggers

**RED Phase:**

**Test:** `test_trigger_splitting`
**Assertions:**
- `/when auth fails | auth error, login failure` → trigger `"auth fails"`, extras `["auth error", "login failure"]`
- `/when auth fails` (no pipe) → trigger `"auth fails"`, extras `[]` (empty list)
- `/when auth | ` (trailing pipe, empty extras) → trigger `"auth"`, extras `[]` (empty segments filtered)
- `/when auth fails | single` → trigger `"auth fails"`, extras `["single"]`
- Extra triggers trimmed of whitespace: ` mock patch ` → `"mock patch"`

**Expected failure:** AssertionError — edge cases with missing extras or whitespace not handled

**Why it fails:** Pipe splitting and whitespace handling not yet robust

**Verify RED:** `pytest tests/test_when_index_parser.py::test_trigger_splitting -v`

**GREEN Phase:**

**Implementation:** Robust trigger/extras splitting.

**Behavior:**
- Split line on first `|` character
- Left side (after operator prefix): primary trigger, stripped
- Right side (if present): comma-separated extra triggers, each stripped
- Empty segments filtered out
- No pipe = empty extras list

**Approach:** `text.split("|", 1)` then `extras.split(",")` with strip and filter.

**Changes:**
- File: `src/claudeutils/when/index_parser.py`
  Action: Implement trigger/extras splitting with edge case handling
  Location hint: Within entry parsing logic

**Verify GREEN:** `pytest tests/test_when_index_parser.py::test_trigger_splitting -v`
**Verify no regression:** `pytest tests/ -q`

---
