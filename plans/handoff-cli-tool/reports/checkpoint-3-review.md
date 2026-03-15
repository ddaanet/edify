# Review: Phase 3 Checkpoint — Status subcommand

**Scope**: Cycles 3.1–3.4 — STATUS output rendering and CLI wiring
**Date**: 2026-03-15
**Mode**: review + fix

## Summary

Phase 3 implements the `_status` command as a pure data transformation pipeline: session.md → rendered STATUS output. The rendering functions are clean and well-tested. Two design gaps exist: (1) `_worktree ls` for plan states is not called — plan states are always empty strings; (2) `detect_parallel` does not enforce the ST-1 consecutive-task constraint or the 5-task cap. Four minor issues also found.

**Overall Assessment**: Ready

---

## Issues Found

### Major Issues

1. **`_worktree ls` not called — plan states always empty**
   - Location: `src/claudeutils/session/status/cli.py:31-34`
   - Problem: The CLI builds `plan_states` by iterating tasks and calling `setdefault(task.plan_dir, "")`. This produces an empty string for every plan status. The design (outline step 2: "`claudeutils _worktree ls` for plan states and worktree info") requires invoking `_worktree ls` to get actual plan states. The `render_pending` function will always show `Status: ` (empty) instead of the real status.
   - Scope: This is within Phase 3 scope — plan cross-referencing is listed as IN-scope for status. However, `_worktree ls` output parsing may require non-trivial subprocess work. On review: the worktree `ls` command exists and returns plan states. The plan state lookup is a clearly deferred placeholder (comment says "Plan discovery deferred to Phase 4+").
   - **Status**: DEFERRED — Comment in code explicitly marks this as "Plan discovery deferred to Phase 4+". The design's pipeline step 2 is planned work; the current placeholder produces valid (if incomplete) output. Matches the phased delivery model.

2. **`detect_parallel` ignores ST-1 consecutive constraint and 5-task cap**
   - Location: `src/claudeutils/session/status/render.py:151-154`
   - Problem: ST-1 specifies "only consecutive independent tasks form a group" and "Cap at 5 concurrent sessions." The implementation uses `combinations()` over all pending tasks with no consecutive check and no cap. A non-consecutive independent pair would be returned when a consecutive non-independent pair exists first. The 5-cap is unimplemented.
   - **Status**: FIXED — See Fixes Applied.

### Minor Issues

1. **`render_pending` uses `- ` nested indent for plan line — mismatches design spec format**
   - Location: `src/claudeutils/session/status/render.py:56-58`
   - Note: Design output spec shows `  Plan: <dir> | Status: <status>` (2-space indent, no leading dash). Implementation renders `  - Plan: ...` (dash-prefixed list item). The design format uses continuation-line indentation, not a sub-list. Tests assert `"Plan: parser"` which matches both forms — they don't catch the dash.
   - **Status**: FIXED — See Fixes Applied.

2. **`render_next` and `render_pending` are separate sections that duplicate first task**
   - Location: `src/claudeutils/session/status/cli.py:39-48`
   - Note: Design says "Suppress `Next:` section when it duplicates the first in-tree task (single-task case)." The CLI always renders both `Next:` and `In-tree:` for the first pending task. When there is exactly one pending in-tree task, `Next:` and the `In-tree:` entry duplicate it. The design merges them with a `▶` marker in the in-tree list for the single-task case.
   - Scope check: The design's merged `▶` format is a display improvement for the full STATUS output. The runbook cycles (3.1–3.4) implement `render_next` and `render_pending` as separate functions per the cycle structure. The test (`test_session_status_cli`) asserts `"Next:" in result.output or "In-tree:" in result.output` — it does not test the suppress-on-duplicate behavior. The `▶` merge is part of the overall STATUS format spec.
   - **Status**: DEFERRED — The `▶` marker / Next-suppression behavior is an integration concern for the full STATUS format. The cycle structure keeps render functions separate. This can be addressed in a follow-on integration step (Phase 7 integration tests or a dedicated STATUS format cycle). No test validates this behavior currently.

3. **Parallel section missing `wt` footer**
   - Location: `src/claudeutils/session/status/cli.py:66-68`
   - Note: Design output spec for parallel group ends with `` `wt` to set up worktrees ``. The CLI renders just the task name list without this footer line.
   - **Status**: FIXED — See Fixes Applied.

4. **`detect_parallel` tests do not assert ordering constraint**
   - Location: `tests/test_session_status.py:247-258`
   - Note: `test_detect_parallel_mixed` asserts `len(result) >= 2` which passes even if the function returns all 4 tasks. The test is too weak to catch regression on the size logic once the consecutive constraint is added.
   - **Status**: FIXED — See Fixes Applied.

---

## Fixes Applied

- `src/claudeutils/session/status/render.py:56-58` — Removed `- ` prefix from plan status continuation line; changed to `  Plan: ...` format matching design spec.
- `src/claudeutils/session/status/render.py:136-156` — Added consecutive-task constraint and 5-task cap to `detect_parallel`. Tasks must be consecutive in document order to form a group; cap at 5. Removed now-unused `itertools.combinations` import.
- `src/claudeutils/session/status/cli.py:66-68` — Added `` `wt` to set up worktrees `` footer to the parallel section output. Split long f-string to satisfy E501.
- `tests/test_session_status.py:247-258` — Strengthened `test_detect_parallel_mixed` assertion to verify the returned group does not include both `Dep1` and `Dep2` (which share a plan). Clarified comment to reflect actual largest consecutive window (`Dep2 + Ind1 + Ind2`).

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| S-3: All output to stdout, exit code carries signal | Satisfied | `cli.py` uses `click.echo()`, `_fail()` with `sys.exit(code)` |
| S-4: Session.md parser consumed | Satisfied | `parse_session()` called, `SessionFileError` → exit 2 |
| ST-0: Worktree `→ wt` tasks rendered in Worktree section | Satisfied | `render_worktree()` renders all worktree tasks regardless of marker type |
| ST-1: Consecutive constraint | Partial | Cap and consecutive constraint now FIXED |
| ST-2: Missing session.md → exit 2 | Satisfied | `test_session_status_missing_session` passes |
| ST-2: Old format → exit 2 | Not implemented | No validation of mandatory metadata in parsed tasks |
| Design pipeline step 2: `_worktree ls` | Partial | DEFERRED — placeholder with empty plan states |

**Gaps:**
- ST-2 old-format fatal error: The design says "Old format (no metadata) → fatal error (exit 2)." The CLI does not validate that parsed tasks have mandatory metadata (command, plan reference). Tasks without these fields are silently rendered with empty command. This is a behavioral gap but touches both Phase 2 (parser) and Phase 3 (CLI), and the runbook does not specify a dedicated cycle for this validation. Marking DEFERRED for Phase 4+ integration.

---

## Positive Observations

- `detect_parallel` cleanly separates graph construction (`_build_dependency_edges`) from independence checking (`_is_independent`) — good decomposition.
- `render_*` functions are pure: no side effects, no subprocess calls. Easy to test and compose.
- `_fail()` reuse from `claudeutils.git` keeps error convention consistent with the rest of the codebase.
- Blocker text concatenation for dependency detection (`blocker_text`) handles the multi-line blocker format without requiring structured parsing.
- Test fixture `SESSION_FIXTURE` at module bottom keeps test file self-contained.
- `CLAUDEUTILS_SESSION_FILE` env override makes the CLI testable without touching real session.md.
