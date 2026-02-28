# Classification: Task Pattern Statuses

- **Classification:** Moderate
- **Implementation certainty:** High — extend character class in 3 regex locations, known technique
- **Requirement stability:** High — statuses `[!]`, `[✗]`, `[–]` defined in execute-rule.md
- **Behavioral code check:** Yes — task extraction logic gains visibility of 3 new status types
- **Work type:** Production
- **Artifact destination:** production (`src/`)
- **Evidence:** "When Triaging Behavioral Code Changes As Simple" — behavioral code = Moderate minimum. Three identical regex edits with existing test infrastructure.

## Scope

**Files affected:**
- `src/claudeutils/validation/session_structure.py:12` — `TASK_PATTERN`
- `src/claudeutils/validation/tasks.py:16` — `TASK_PATTERN`
- `src/claudeutils/worktree/session.py:30` — `task_pattern`

**Change:** Extend `[ x>]` to `[ x>!✗–]` in all three locations.

**Downstream impact:** None behavioral — callers extract task names, don't branch on status character. Tasks in blocked/failed/canceled states become visible to extraction, validation, and merge (previously invisible).
