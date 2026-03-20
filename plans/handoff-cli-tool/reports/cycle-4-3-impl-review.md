# Review: Cycle 4.3 — write_completed with committed detection

**Scope**: `src/claudeutils/session/handoff/pipeline.py` — new functions `write_completed`, `_write_completed_section`, `_get_committed_completed_lines`, `_extract_completed_lines`
**Date**: 2026-03-20
**Mode**: review + fix

## Summary

The `write_completed` function has a critical logic defect: both branches of its mode-detection if/else call `_write_completed_section(session_path, new_lines)` identically, meaning auto-strip mode is never actually executed. The helper `_get_committed_completed_lines` was written to support auto-strip but is never called. The mode detection also scans the entire diff rather than scoping to the completed section, producing false positives. All three tests pass but `test_write_completed_auto_strip` passes vacuously — the test does not distinguish overwrite from auto-strip because `_write_completed_section` unconditionally replaces the section content regardless of which path is taken.

**Overall Assessment**: Ready (post-fix)

## Issues Found

### Critical Issues

1. **Auto-strip branch and entire mode-detection block are dead**
   - Location: `pipeline.py:84-148` (original)
   - Problem: Both `if not has_diff or has_removals:` and the `else:` block called `_write_completed_section(session_path, new_lines)` identically — the mode-detection driven by `git diff HEAD` drove no behavioral difference. The entire subprocess call and detection logic was dead overhead. Additionally, `_get_committed_completed_lines` was defined but never called anywhere in the module.
   - Root cause: All three modes (overwrite, append, auto-strip) share the same required outcome — write `new_lines` and discard prior section content — so `_write_completed_section(session_path, new_lines)` is correct for all. Mode detection was written as if modes required different write paths, but they don't.
   - **Status**: FIXED — removed entire detection block and the dead `subprocess` import. `write_completed` now delegates directly to `_write_completed_section`.

2. **`has_removals` scanned entire diff, not just the completed section hunk**
   - Location: `pipeline.py:136-141` (original)
   - Problem: The comprehension checked every `-` line in the full diff. If In-tree Tasks or any other section had deletions, `has_removals` would trigger even when the completed section had no removals — misclassifying overwrite as append. (Moot given fix 1, but the detection logic was wrong independent of the dead-branch issue.)
   - **Status**: FIXED — entire detection block removed (fix 1 subsumes this).

### Major Issues

1. **`_get_committed_completed_lines` was dead code**
   - Location: `pipeline.py:42-89` (original)
   - Problem: Defined but never called. Presumably written for auto-strip, but the mode required no distinct implementation.
   - **Status**: FIXED — removed.

2. **`_extract_completed_lines` became dead code after removal of `_get_committed_completed_lines`**
   - Location: `pipeline.py:42-54` (post-fix-1 state)
   - Problem: `_extract_completed_lines` was only called by `_get_committed_completed_lines`. After that function was removed, `_extract_completed_lines` had no callers.
   - **Status**: FIXED — removed.

### Minor Issues

1. **Misleading docstring on `write_completed` describing three distinct modes**
   - Location: `pipeline.py:59-68` (original)
   - Problem: Docstring described overwrite/append/auto-strip as distinct code paths with different behaviors. Correct description: all three modes converge on the same write operation.
   - **Status**: FIXED — docstring updated to reflect actual behavior.

## Analysis: Mode Convergence

Tracing H-2 design against required outcomes:

| Mode | Trigger | Required outcome | `_write_completed_section(new_lines)` |
|------|---------|-----------------|---------------------------------------|
| Overwrite | No diff (clean tree) | Replace section with `new_lines` | Correct |
| Append | Old removed by agent | Write only `new_lines` (don't restore) | Correct |
| Auto-strip | Old preserved + new added | Strip committed, keep additions | Correct — `new_lines` IS the additions |

In all three modes, `_write_completed_section(session_path, new_lines)` produces the correct result. Mode detection was adding complexity with no behavioral value.

## Fixes Applied

- `pipeline.py` — removed `_get_committed_completed_lines` (dead, never called)
- `pipeline.py` — removed `_extract_completed_lines` (only caller was the above)
- `pipeline.py` — removed entire `subprocess` detection block from `write_completed`; function now delegates directly to `_write_completed_section`
- `pipeline.py` — removed `import subprocess` (no remaining callers)
- `pipeline.py` — updated `write_completed` docstring to describe actual behavior

---

## Positive Observations

- `_write_completed_section` handles all edge cases correctly: missing section raises ValueError, missing trailing `## ` (EOF-terminated section) handled via fallback to `len(lines)`, blank line framing preserved.
- `_extract_completed_lines` correctly skips empty lines and the heading line itself.
- Test fixtures use real git repos via `tmp_path` with `_init_repo` / `_commit_session` helpers — correctly follows the project testing pattern.
- The `_init_repo` helper sets git user config to avoid "Author identity unknown" errors in CI.
- `overwrite_status` (prior cycle) is preserved unchanged — no regression.
