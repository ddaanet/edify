# Step 1.2

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.2: Fix _filter_section continuation lines and plan_dir regex

**Objective**: Fix two bugs in `cli.py` — continuation lines leaking into filtered output (M1), and case-sensitive plan_dir regex (M2).

**Findings**: M1 (`cli.py:55-60` non-bullet continuation lines leak) and M2 (`cli.py:73` regex `plan:\s*(\S+)` won't match title case `Plan:`).

**Implementation**:

1. **Read _filter_section function** at `src/claudeutils/worktree/cli.py:55-60`:
   - Understand current filtering logic
   - Identify where continuation lines are processed

2. **Add continuation line tracking**:
   - Track state: whether current section is relevant (should include) or filtered out (should skip)
   - When a bullet line matches filter: set state to "including"
   - When a bullet line doesn't match: set state to "skipping"
   - Only append lines (bullets + continuation) when state is "including"

3. **Handle edge cases**:
   - Empty lines between sections (preserve structure)
   - Nested bullets (indented with spaces)
   - Headers (always include)

4. **Fix plan_dir regex** at `src/claudeutils/worktree/cli.py:73`:
   - Change `plan:\s*(\S+)` to `[Pp]lan:\s*(\S+)` (explicit both cases)
   - Check if other metadata fields (Model:, Restart:) have similar case issues — fix if found

**Expected Outcome**: Focused sessions exclude continuation lines from irrelevant tasks. `focus_session` extracts plan directory from both `plan:` and `Plan:` formats.

**Error Conditions**:
- If filtering too aggressive → verify bullet detection regex
- If continuation lines still leak → check state tracking logic
- If regex matches incorrectly → verify \S+ captures plan directory without whitespace

**Validation**:
```bash
pytest tests/test_worktree_commands.py -k "filter_section or focus_session" -v 2>/dev/null || echo "Manual verification needed"
```

---
