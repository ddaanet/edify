# Review: handoff-cli-tool Moderate batch (M-pre-1, M-pre-2, m-pre-3)

**Scope**: Changes since 8f6c5581 — blocker wiring, vet stale detail, blank line preservation
**Date**: 2026-03-23
**Mode**: review + fix

## Summary

Three findings addressed: blocker extraction wired to `detect_parallel`, stale vet output with per-file detail, and blank line preservation in both completed-section parsers. Core logic is correct across all three. Two issues found: stale output uses `.name` (filename only) where spec requires relative path, and `handoff/parse.py` strips trailing blanks but not leading blanks.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Stale vet output uses filename only, spec requires relative path**
   - Location: `src/claudeutils/session/commit_gate.py:174-175`
   - Problem: `newest_source_path.name` returns `foo.py`; spec (outline.md:205-206) shows `src/auth.py` and `plans/foo/reports/vet-review.md` — relative paths, not bare filenames. Both the source and report paths use `.name`.
   - Fix: Replace `.name` with relative path string (cast via `str(newest_source_path)` / `str(newest_report_path)`).
   - **Status**: FIXED

### Minor Issues

1. **`handoff/parse.py` strips trailing blanks but not leading blanks**
   - Location: `src/claudeutils/session/handoff/parse.py:48-55`
   - Note: The scope requirement states both parsers should handle leading/trailing stripping. `session/parse.py` (the other parser) strips both. `handoff/parse.py` only strips trailing — leading blank after the heading is preserved in `completed_lines`. The test passes because it only checks that `""` exists (not that it's internal). This creates a leading blank in the written completed section.
   - Fix: Add leading-blank strip loop mirroring `session/parse.py`.
   - **Status**: FIXED

2. **Test for stale detail only checks filenames, not paths**
   - Location: `tests/test_session_commit_validation.py:255-256`
   - Note: Test asserts `"foo.py" in result.stale_info` and `"vet-review.md" in result.stale_info`. After fixing to use relative paths, the test still passes (filename is a substring of relative path). No behavioral gap — correct by containment — but the assertion could be tightened to verify the path prefix is present.
   - Fix: Tighten assertions to verify relative path presence.
   - **Status**: FIXED

## Fixes Applied

- `src/claudeutils/session/commit_gate.py:174-175` — Changed `.name` to `str(path)` for both source and report paths to match spec format
- `src/claudeutils/session/handoff/parse.py:48-55` — Added leading-blank strip loop after the trailing-blank strip
- `tests/test_session_commit_validation.py:255-256` — Tightened assertions to check `src/foo.py` and `plans/review-2026-01/reports/vet-review.md`

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| M-pre-1: Parallel detection uses blockers from session.md (ST-1) | Satisfied | `parse.py:156` extracts blockers; `status/cli.py:99` passes `data.blockers` to `detect_parallel` |
| M-pre-2: Stale vet output includes per-file detail with timestamps | Satisfied (after fix) | `commit_gate.py:173-175` — filenames+timestamps; paths fixed to match spec |
| m-pre-3: Completed section parser preserves blank lines between groups | Satisfied | `parse.py:85-88` strips leading/trailing only; `handoff/parse.py:54-55` strips trailing (leading fixed) |

**Gaps:** None after fixes.

---

## Positive Observations

- `extract_blockers` reuse from `worktree/session.py` — zero reimplementation, consistent behavior.
- `_newest_file` helper returns both mtime and path in one call, eliminating the prior double-stat anti-pattern.
- Both blank-line strip implementations follow the same loop pattern (`while list and not list[-1].strip(): list.pop()`), making the approach visually consistent across files.
- Test for blocker wiring (`test_status_parallel_uses_blockers`) uses real `CliRunner` + filesystem setup — correctly follows e2e-over-mocked pattern.
- `SessionData.blockers` default factory correctly uses `field(default_factory=list)`.
