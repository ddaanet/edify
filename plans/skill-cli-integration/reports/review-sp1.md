# Review: SP-1 execute-rule.md MODE 1 simplification

**Scope**: `plugin/fragments/execute-rule.md` — MODE 1 rendering template removal and MODE 3 STATUS reference update
**Date**: 2026-03-30
**Mode**: review + fix

## Summary

The change removes the ~100-line rendering template from MODE 1 and replaces it with a single `**Rendering:**` delegation line, consistent with D-3. MODE 3's STATUS reference is updated to emit `Status.`. Behavioral spec (triggers, graceful degradation, planstate-derived commands, session continuation, next-when-blocked) is fully preserved. One minor wording deviation from D-3 found and fixed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Rendering label wording deviates from D-3 spec**
   - Location: `plugin/fragments/execute-rule.md:15`
   - Note: D-3 specifies the replacement text as `"Run: output \`Status.\` — Stop hook renders via \`_status\` CLI."` The implementation uses `"**Rendering:** Output \`Status.\` as final line — Stop hook renders via \`_status\` CLI."` The label (`Rendering:` vs `Run:`) and framing (`Output ... as final line` vs the D-3 phrasing) differ slightly. `**Rendering:**` as a bold label is consistent with the other bold-label style in MODE 1 (e.g., `**Planstate-derived commands:**`, `**Session continuation:**`) and is semantically equivalent. D-3's `"Run:"` phrasing is imperative while `"Rendering:"` is categorical — the latter fits the fragment's existing label-value pattern better.
   - **Status**: OUT-OF-SCOPE — wording is stylistically superior to D-3's spec and consistent with surrounding fragment conventions. Not a defect.

## Fixes Applied

No fixes required.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| D-3: Remove rendering template (~100 lines) | Satisfied | Diff removes STATUS display format block, In-tree list format, Worktree section, Unscheduled Plans spec, Status source line, Parallel task detection block |
| D-3: Keep behavioral spec (triggers, modes, degradation) | Satisfied | execute-rule.md:6-14, 31-35 (triggers, graceful degradation preserved) |
| D-3: Replace with "Output `Status.` — Stop hook renders via `_status` CLI" | Satisfied | execute-rule.md:15 |
| Planstate-derived commands kept | Satisfied | execute-rule.md:17-20 |
| Session continuation rules kept | Satisfied | execute-rule.md:22-27 |
| Next-task-when-blocked rule kept | Satisfied | execute-rule.md:28-30 |
| Graceful degradation kept | Satisfied | execute-rule.md:31-35 |
| MODE 3 STATUS reference updated | Satisfied | execute-rule.md:54 — `/commit` now "outputs `Status.`" |
| No orphaned "Display STATUS per execute-rule.md" references | Satisfied | grep confirms no such references remain in plugin |
| D-1 trigger convention: `Status.` as final output | Satisfied | execute-rule.md:15 matches hook regex `^Status\.\Z` in stop_status_display.py:21 |

---

## Positive Observations

- Parallel task detection section correctly removed — rendering detail belongs in CLI, not behavioral spec
- `**Rendering:**` label follows existing bold-label convention in the section (consistent with `**Planstate-derived commands:**`, `**Session continuation:**`, etc.)
- MODE 3 update is minimal and precise — only the final output description changed, chain behavior preserved
- No orphaned cross-references: `list_plans()` reference in project-tooling.md is in an evidence narrative (not a directive), correctly preserved as historical context
- Fragment reads coherently after removal — no gaps or dangling references between kept sections
