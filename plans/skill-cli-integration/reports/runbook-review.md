# Runbook Review: Skill-CLI Integration

**Artifact**: `plans/skill-cli-integration/runbook.md`
**Date**: 2026-03-29T00:00:00Z
**Mode**: review + fix-all
**Phase types**: Mixed (1 TDD, 3 inline)

## Summary

Runbook covers SP-H (Stop hook Python module) via TDD (Phase 1) and SP-1/SP-2/SP-H registration via inline phases (2-4). Structure and design alignment are sound. Three minor issues found and fixed: specific pytest path selectors in Verify RED lines, and a Post-Commit removal target string mismatch in Phase 4.

**Overall Assessment**: Ready

**Warning**: No outline review report found at `plans/skill-cli-integration/reports/runbook-outline-review.md`. Outline review may have been skipped.

## Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Specific pytest path selectors in Verify RED (Cycle 1.1)**
   - Location: Cycle 1.1, RED Phase, Verify RED lines
   - Problem: `pytest tests/test_stop_hook_status.py::test_should_trigger -v` and `pytest tests/test_stop_hook_status.py::test_process_hook_loop_guard -v` — specific file paths and `::` selectors accumulate staleness risk (test renames, file moves).
   - Fix: Replaced both with `just green`
   - **Status**: FIXED

2. **Specific pytest path selector in Verify RED (Cycle 1.2)**
   - Location: Cycle 1.2, RED Phase, Verify RED line
   - Problem: `pytest tests/test_stop_hook_status.py::test_format_ansi -v` — only covers one of three RED tests in the cycle (`test_format_ansi`, `test_process_hook_uses_status_fn`, `test_process_hook_status_failure`). Specific selector was both stale-prone and incomplete.
   - Fix: Replaced with `just green`
   - **Status**: FIXED

3. **Post-Commit removal target text mismatch in Phase 4**
   - Location: Phase 4, Replace Post-Commit section
   - Problem: Runbook said `Remove "Display STATUS per execute-rule.md MODE 1."` but actual text in `plugin/skills/commit/SKILL.md` (line 178) is `"Then display STATUS per execute-rule.md MODE 1."` — the leading "Then" was absent. Executor using the runbook's text as an exact match target would fail to locate the line.
   - Fix: Updated removal target to `"Then display STATUS per execute-rule.md MODE 1."`
   - **Status**: FIXED

## Fixes Applied

- Cycle 1.1 RED Phase, first Verify RED — `pytest tests/...::test_should_trigger -v` → `just green`
- Cycle 1.1 RED Phase, second Verify RED — `pytest tests/...::test_process_hook_loop_guard -v` → `just green`
- Cycle 1.2 RED Phase, Verify RED — `pytest tests/...::test_format_ansi -v` → `just green`
- Phase 4, Replace Post-Commit section — removal target prefixed with "Then" to match actual SKILL.md text

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
