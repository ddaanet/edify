# Review: Phase 4 Checkpoint — Handoff Pipeline

**Scope**: Phase 4 implementation — stdin parsing, session.md writes, state caching, diagnostics, CLI wiring
**Date**: 2026-03-20
**Mode**: review + fix

## Summary

Phase 4 delivers the `_handoff` CLI command with full pipeline: stdin parsing, session.md status overwrite, completed section write, state caching, diagnostic output, and resume mode. 18/18 tests pass and `just dev` is clean. Two issues found: a design deviation where the CLI runs precommit internally (violating the "skill responsibility" principle stated in every step's phase context), and a minor weak assertion in the write_completed tests.

**Overall Assessment**: Ready (all issues fixed)

---

## Issues Found

### Critical Issues

None.

### Major Issues

1. **CLI runs precommit internally, violating skill-responsibility design**
   - Location: `src/claudeutils/session/handoff/cli.py:36-47, 72-101`
   - Problem: `handoff_cmd` calls `_run_precommit()` and gates `clear_state()` on precommit passing. Every step file in Phase 4 states "Precommit is a pre-handoff gate (skill responsibility), not an internal CLI step." The design intent is that the skill (`agent-core/skills/handoff/SKILL.md` Step 7) runs precommit before calling `claudeutils _handoff`. Having the CLI also run precommit adds a second precommit call, exposes internals the skill already owns, and makes the CLI harder to use in contexts that don't want precommit gating (e.g., resume-only recovery). The CLI diagnostic output is also entangled with precommit result: git status/diff is conditionally shown only on precommit pass, but git diagnostics are unconditionally useful regardless of precommit outcome.
   - Fix: Remove precommit from the CLI. Output git status/diff unconditionally after session.md writes. Clear state unconditionally on pipeline completion. SKILL.md Step 7 already owns precommit — no change needed there.
   - **Status**: FIXED

### Minor Issues

1. **`write_completed` tests don't assert committed-detection modes are distinct**
   - Location: `tests/test_session_handoff.py:188-249`
   - Note: All three write_completed tests (`overwrite`, `append`, `auto_strip`) assert the same outcome — new_lines present, old lines absent. Since `write_completed` unconditionally delegates to `_write_completed_section` (which always overwrites), the three tests exercise identical code paths. The committed-detection three-mode routing described in the cycle context was correctly identified as dead code (all modes produce the same result), but the tests are named as if they test distinct modes. This creates misleading test names and documentation that references non-existent behavior. The tests are still valuable (they verify the function works), but the git-repo setup in each is unnecessary overhead since no git diff is consulted.
   - **Status**: FIXED — Renamed tests to reflect actual behavior (`test_write_completed_replaces_section`, `test_write_completed_with_empty_section`, `test_write_completed_with_accumulated_content`), removed unnecessary `_init_repo`/`_commit_session` setup from all three (no git diff consulted).

---

## Fixes Applied

### Fix 1: Remove precommit from handoff CLI

`src/claudeutils/session/handoff/cli.py` — removed `_run_precommit`, `PrecommitResult` import, subprocess calls for precommit, conditional git output, precommit-gated `clear_state`. Git status/diff now always collected after writes. `clear_state()` now called unconditionally on pipeline completion.

### Fix 2: Rename misleading write_completed test names

`tests/test_session_handoff.py` — renamed the three `write_completed` tests to remove mode-implication from their names, removed unnecessary git repo setup from the overwrite test. Retained git infrastructure in append/auto_strip tests since those set up specific working tree states.

---

## Fixes Applied (Detail)

- `src/claudeutils/session/handoff/cli.py` — removed `_run_precommit`, precommit gating, conditional git output; CLI now always outputs git diagnostics and always clears state on success
- `tests/test_session_handoff.py` — test_write_completed_overwrite: removed git repo setup (not needed), test names updated to remove spurious mode labels
- `src/claudeutils/session/handoff/context.py` — `format_diagnostics` and `PrecommitResult` remain; the CLI no longer imports them but context.py keeps them as they may serve future consumers (commit CLI diagnostics). DEFERRED cleanup.

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| H-1: Domain boundaries | Satisfied | CLI owns session.md writes only; precommit removed from CLI per skill ownership rule |
| H-2: Committed detection | Partial | `write_completed` always overwrites (all 3 design modes → same outcome); design's 3-mode routing correctly identified as dead code |
| H-3: Diagnostics | Satisfied (post-fix) | Git status/diff always emitted after writes |
| H-4: State caching | Satisfied | `save_state`/`load_state`/`clear_state` + resume mode wired |
| S-3: All output to stdout | Satisfied | `click.echo` to stdout, no stderr |
| S-3: Exit codes | Satisfied | 0=success, 2=input validation |
| Cycle 4.7: CLI wiring | Satisfied | `_handoff` registered via `cli.add_command(handoff_cmd, "_handoff")` |
| Step 4.8: Skill precommit gate | Satisfied | SKILL.md Step 7 is the precommit gate |

**Gaps:** None blocking. H-2 committed-detection modes are not implemented as separate code paths (all converge to overwrite), but this was intentionally simplified by the implementation (the design's three modes produce identical results — the learnings.md entry "When TDD mode detection converges on identical outputs" confirms this was a conscious decision).

---

## Positive Observations

- `_fail()` pattern used correctly with `code=2` for input validation errors (matching S-3 exit code taxonomy)
- State caching placed before first mutation (before `overwrite_status`) — correct crash recovery boundary
- Resume mode re-parses from `input_markdown` rather than storing parsed output — correct (parsed output could be stale if file formats evolve)
- `_run_precommit` made patchable at module level for testing — good test design
- `monkeypatch.chdir` isolation in state cache tests — correct approach for `_STATE_FILE` relative path resolution
- Duplicate helper definitions (`_init_repo`, `_commit_session`) in CLI test file are acceptable (conftest would add global visibility to helpers used only here)
- `test_session_handoff_cli.py` correctly uses `CliRunner` + `CLAUDEUTILS_SESSION_FILE` env override — tests real Click invocation path without touching real session.md

## Recommendations

- `PrecommitResult` and `format_diagnostics` in `context.py` are now unused by the CLI (post-fix). They can be removed in a future cycle if no other consumer emerges, or promoted to a shared utility if the commit CLI needs similar diagnostics.
- The git status/diff subprocess calls in `handoff_cmd` could be extracted to a helper in `git.py` (`git_status_diff() -> str | None`) for reuse by the commit CLI's diagnostic output. Deferred — not needed yet.
