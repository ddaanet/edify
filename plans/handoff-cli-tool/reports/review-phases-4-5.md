# Runbook Review: Phases 4 and 5

**Artifact**: `plans/handoff-cli-tool/runbook-phase-4.md`, `plans/handoff-cli-tool/runbook-phase-5.md`
**Date**: 2026-03-07T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (both phases)

## Summary

Both phases are structurally sound with correct RED/GREEN sequencing, no prescriptive code blocks in GREEN phases, and appropriate use of real git repos (aligned with recall `when preferring e2e over mocked subprocess`). Two behavioral assertion gaps were found: Phase 4 Cycle 4.3 append-mode outcome was ambiguous, and Phase 5 Cycle 5.2 `CleanFileError` string format lacked the exact error message required by `when cli error messages are llm-consumed`. Both fixed.

**Overall Assessment**: Ready

## Findings

### Major Issues

1. **Cycle 4.3 RED: Append-mode assertion too vague**
   - Location: Phase 4, Cycle 4.3, RED Phase assertions
   - Problem: "appends new lines to section (does not restore old content)" doesn't specify the precise resulting section content. An executor could write tests where prior committed lines appear alongside new lines and still satisfy the prose. This violates the "could different executors write different tests" heuristic.
   - Fix: Strengthened to specify that the resulting section contains exactly `new_lines`, and that prior committed lines are NOT restored.
   - Also added git fixture requirement: committed `agents/session.md` with an existing completed section is required for diff modes to function.
   - **Status**: FIXED

2. **Cycle 5.2 RED: `CleanFileError` string representation format unspecified**
   - Location: Phase 5, Cycle 5.2, RED Phase assertions
   - Problem: "String representation containing `STOP:` directive" is too vague — multiple string formats could satisfy this. Recall entry `when cli error messages are llm-consumed` (facts only, STOP directive for data-loss) requires the exact message format so LLM callers can parse it deterministically. The design outline (outline.md C-3 + output examples) specifies the exact format.
   - Fix: Replaced with exact format string: `**Error:** Listed files have no uncommitted changes\n- <path>\n\nSTOP: Do not remove files and retry.`
   - **Status**: FIXED

### Minor Issues

None.

## Fixes Applied

- `runbook-phase-4.md`, Cycle 4.3 RED — Strengthened append-mode assertion: exact section content specified, prior-committed-lines-not-restored made explicit; added git fixture requirement for committed session.md with completed section
- `runbook-phase-5.md`, Cycle 5.2 RED — Replaced vague `STOP:` directive assertion with exact error message format from design outline output examples

## Notes: Items Inspected and Cleared

**Phase 4:**
- Cycle 4.5 GREEN: `subprocess.run(["just", "precommit"], capture_output=True, text=True, check=False)` appears inline in a Behavior prose bullet, not a code block. Per review criteria, prescriptive code blocks are violations; inline prose hints are acceptable. Cleared.
- Cycle 4.7 GREEN: `_fail("**Error:** No input on stdin and no state file", code=2)` with exact string — the exact error message is behavioral specification required by `when cli error messages are llm-consumed`. Appropriate. Cleared.
- Cycle 4.3 GREEN: `_git("diff", "HEAD", "--", str(session_path))` in Approach field — hint-level guidance, not a code block. Cleared.
- Checkpoint spacing: Mid-phase checkpoint after 4.4, phase checkpoint after 4.7. Two checkpoints for 7 cycles, ≤5 items between checkpoints. Cleared.
- RED/GREEN sequencing: All 7 cycles progress from non-existent function → minimal implementation. Cleared.

**Phase 5:**
- Cycle 5.1 RED: Input fixture is markdown in a code block, not test code. Parametrized test names with exact expected values. Cleared.
- Cycle 5.2 GREEN: `_git("status", "--porcelain")` and `_git("diff-tree", ...)` in Behavior bullets — hint-level prose guidance aligned with established `_git()` pattern from Phase 1. Cleared.
- Cycle 5.3 GREEN: `fnmatch` or `pathlib.PurePath.match` — hints, not prescription. Cleared.
- File references: All target files are creation targets (none exist yet). `src/claudeutils/session/cli.py` referenced in 4.7 is a Phase 1 creation target — cross-phase dependency correctly ordered. Cleared.
- Density: 3 cycles in Phase 5, each covering distinct behavioral boundary (parsing, input validation, vet check). Cleared.
- Model assignment: `sonnet` for both phases — implementation/TDD work. Appropriate.

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
