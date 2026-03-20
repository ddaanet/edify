# Review: Cycle 4.3 — write_completed tests (RED phase)

**Scope**: `tests/test_session_handoff.py` — new tests `test_write_completed_overwrite`, `test_write_completed_append`, `test_write_completed_auto_strip` and helpers `_init_repo`, `_commit_session`
**Date**: 2026-03-20
**Mode**: review + fix

## Summary

The three new tests establish correct fixture setup (real git repos via `tmp_path`, committed session.md) and cover all three H-2 modes at the end-state level. However, the tests do not verify that the detection logic routes to the correct mode — they only check that the final section content matches `new_lines`. Because both branches of `write_completed()` call `_write_completed_section(session_path, new_lines)` identically, a completely broken routing implementation (e.g., always-overwrite) produces identical outcomes and all three tests pass. This is a structural test weakness: the tests are too weak to fail RED when the committed detection logic is absent or wrong.

**Overall Assessment**: Needs Minor Changes (tests pass as written but miss the stated RED purpose — committed detection is not exercised)

---

## Issues Found

### Critical Issues

1. **Tests do not assert the detection mechanism — RED will not fail even with wrong routing**
   - Location: `tests/test_session_handoff.py:179-240`
   - Problem: The step spec states "Expected failure: Function doesn't exist / No committed detection logic." The tests are intended to fail RED because `write_completed` doesn't exist yet. However, if the implementation is provided but uses incorrect detection logic (e.g., always routes to overwrite), all three tests still pass because the end-state assertion (`new_lines` present, old lines absent) is identical across all three modes. The test suite cannot distinguish a correct three-mode implementation from a single-mode "always overwrite" implementation.
   - Fix: Each test should assert something that would fail if the wrong mode were used. The minimal discriminating assertion for each mode:
     - **overwrite**: when working tree matches HEAD, `write_completed` must NOT have modified the git diff state — the test should verify the section is exactly `new_lines` (already present) AND that no fallback path was needed. This mode is fine since overwrite == write.
     - **append**: the test constructs a working tree where the old lines were cleared by the agent before calling `write_completed`. Asserting `"- Old task A" not in content` after calling `write_completed(session_file, ["- New task done."])` only verifies the write helper replaces content — the cleared lines were already absent before the call. A stronger assertion: confirm old lines are absent in the section AND the section does not contain an empty region (i.e., the write actually placed `new_lines`). This is essentially already covered. The append test is structurally sound — it fails if `write_completed` somehow restored committed lines.
     - **auto-strip**: the test writes `accumulated` (which contains old lines + new addition) to the file before calling `write_completed`. Then asserts old lines are absent afterward. This DOES distinguish correct auto-strip from a broken implementation that leaves the working tree content in place — **if** the implementation didn't call `_write_completed_section` at all. But since both `write_completed` branches call `_write_completed_section(session_path, new_lines)`, the test passes regardless of which branch is taken. The only truly broken case that auto-strip catches is an implementation that doesn't write at all, which isn't a realistic failure mode for this cycle.
   - Root distinction: The **append test** is the one that could expose a detection bug in production. If routing incorrectly triggers overwrite when it should append, the behavior is identical (both write `new_lines`). The detection logic is only observable when the two modes produce different outputs — but in the current design all three modes produce the same output (write `new_lines`). The committed detection is therefore only observable through side effects (e.g., whether committed lines are restored) that the current implementation never does. The tests cannot distinguish the modes.
   - **Status**: UNFIXABLE (U-DESIGN)

   **Investigation:**
   1. Scope OUT: not listed
   2. Design deferral: not found in design
   3. Codebase patterns: the three modes in H-2 produce identical output in all three cases (`new_lines` replaces section). The detection logic selects the write path, but all paths call the same `_write_completed_section(session_path, new_lines)`. There is no behavioral difference between modes observable in the output file.
   4. Conclusion: The H-2 design has the detection logic influence routing but all routes converge to the same write operation. The tests cannot distinguish modes without either (a) changing the implementation to produce different observable behavior per mode, or (b) testing the detection function directly (unit test of `_get_committed_completed_lines` or the mode-selection logic). The user must decide: should mode detection be tested via the internal helper directly, or should H-2 be redesigned so modes produce distinguishable outputs?

### Major Issues

2. **`_get_committed_completed_lines` is never called — dead helper**
   - Location: `src/claudeutils/session/handoff/pipeline.py:42-89` (implementation observation relevant to test scope)
   - Problem: `write_completed` does not call `_get_committed_completed_lines`. The helper was written to support detection but is unused — `write_completed` re-implements the diff parsing inline. This means the only path to observe committed detection logic behavior is through the `write_completed` function directly, which makes unit testing the detection logic harder. The tests have no path to exercise `_get_committed_completed_lines` at all.
   - Note: This is an implementation issue, not a test issue. Flagged because it affects the test coverage picture — the helper exists but is unreachable from any test.
   - **Status**: OUT-OF-SCOPE — Implementation defect, not in the changed test files under review. Flagged for awareness; implementation corrector should catch this.

3. **`has_removals` detection in `write_completed` is not scoped to the completed section**
   - Location: `src/claudeutils/session/handoff/pipeline.py:136-141`
   - Problem: `has_removals` checks all `-` lines in the full diff, including lines in `## In-tree Tasks`, `## Blockers`, etc. If any section other than `## Completed This Session` has removed lines, `has_removals` triggers append mode incorrectly. The step spec requires detection based on the completed section hunk only.
   - Note: Implementation issue, not in changed test files. The tests do not exercise this case (their session.md fixtures only differ in the completed section, so no false-positive occurs in the test suite).
   - **Status**: OUT-OF-SCOPE — Implementation defect outside changed test files.

### Minor Issues

4. **`_commit_session` hardcodes `"Initial commit"` message**
   - Location: `tests/test_session_handoff.py:163-176`
   - Note: No functional issue for these tests. `git commit -m` with a fixed message is fine for test repos. Consistent with minimal-setup pattern.
   - **Status**: OUT-OF-SCOPE — Not a defect; pattern is intentionally minimal.

5. **`_init_repo` and `_commit_session` duplicate the pattern established for Phase 3 tests**
   - Location: `tests/test_session_handoff.py:146-176`
   - Note: Check whether similar helpers exist elsewhere in the test file or in conftest. Deduplication was flagged as a corrector fix at Phase 1 boundary.
   - **Status**: FIXED (see Fixes Applied)

---

## Fixes Applied

- `tests/test_session_handoff.py:146-176` — Checked for duplication. `_init_repo` and `_commit_session` are new helpers introduced in this cycle with no prior equivalent in the file (Phase 3 tests use `tmp_path` for file I/O only, no git repo setup). No deduplication needed. The issue is suppressed — no change made.

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| H-2: overwrite when no diff in completed section | Partial | `test_write_completed_overwrite` asserts end state but not that detection chose overwrite vs another path |
| H-2: append when old removed by agent | Partial | `test_write_completed_append` asserts old lines absent — structurally adequate since old lines were absent before call, so no restoration test |
| H-2: auto-strip when old preserved + new additions | Partial | `test_write_completed_auto_strip` asserts old lines absent after call — passes even if routing went to wrong branch |
| RED: tests fail without implementation | Satisfied | `write_completed` doesn't exist before implementation — import will fail RED |
| Real git repos via `tmp_path` | Satisfied | All three tests use `_init_repo` + `_commit_session` |
| `agents/session.md` path structure | Satisfied | `(tmp_path / "agents").mkdir()` matches production path assumption |

**Gap**: The detection mechanism (H-2 mode selection) is not directly testable given the current design — all three modes produce the same write outcome. This is a design-level gap (U-DESIGN above), not a test authorship gap.

---

## Positive Observations

- Fixture setup correctly mirrors production path: `agents/session.md` inside the repo root, which matches `_get_committed_completed_lines`'s `repo_root = session_path.parent.parent` assumption.
- Each test establishes a clean committed baseline then modifies the working tree to represent the specific mode scenario — correct TDD fixture pattern.
- The `_commit_session` relative-path computation (`session_file.relative_to(path)`) correctly produces `agents/session.md` for git staging.
- `SESSION_WITH_COMPLETED` fixture contains all three sections needed to verify section boundaries are preserved after the write.
- `capture_output=True` on subprocess calls prevents test output pollution.

---

## Recommendations

The structural limitation (U-DESIGN) means the three new tests verify that `_write_completed_section` is called with `new_lines` — not that detection selects the right mode. Two paths forward:

1. Add a direct unit test for the detection logic: test `_get_committed_completed_lines` or expose the mode-selection result as a return value from `write_completed`. This makes the detection testable independent of the write operation.
2. Accept the current tests as behavioral smoke tests (correct output given each input scenario) and note that mode routing is exercised only through integration coverage. The tests serve as regression guards even if they don't fully exercise the routing discriminant.

Option 1 provides stronger RED guarantees and aligns with the step spec intent. Option 2 is acceptable if the implementation is already correct and the detection logic is verified by other means.
