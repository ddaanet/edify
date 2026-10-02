# Review: Item 1.1 / Slice 2 — test review

**Scope**: uncommitted diff to `tests/test_verify_step.py` (new
`test_nested_path_under_exempt_dir_is_dirty`, the `_status(repo)` refactor)
and the RED report `plans/build-fixes/reports/item-1-1-s2-red.md`. OUT:
`plugin/skills/build/scripts/verify-step.sh` (not edited or reverted, and
`git diff --quiet` on it passes), Item 1.2 onward.
**Date**: 2026-10-02
**Mode**: review + fix

## Summary

The new test discriminated on the nested-path globs, but it was a bare
negative. A pattern exempting neither `inbox/` nor `.claude/handoff-*` at all
passed it, so only other tests caught the loss of the exemption. Fixed by
adding single-level exempt siblings to the same tree. The `_status` refactor
keeps every existing pre-assertion as it was. Adding the siblings pushed the
module over the line cap. Two module-wide duplication seams fixed that, and
the module went from 399 to 380 lines.

**Overall Assessment**: Ready

## Mechanical check

- Real script: `8/8 passed` (`pytest tests/test_verify_step.py`, after all
  fixes).
- `git diff --quiet plugin/skills/build/scripts/verify-step.sh` → untouched.
- `scripts/check_line_limits.sh`: exit 0; `tests/test_verify_step.py` is not
  listed (380 lines).

### Reviewer's own mutation (differs from the RED's `.+`)

The two copies are at `/tmp/claude/build-fixes/`. Each has its own rebind
plugin, `rebind_script_plugin_s2_review_<v>.py`, which has the same shape as
the RED's: it sets `sys.modules["tests.test_verify_step"].SCRIPT` after
collection and asserts it had not already been set. To check that each
mutation landed, line 19 of each copy was grepped against the tracked
script's line 19. The `diff` against the tracked script showed only line 19
changing.

- **`space`**: both `[^/]+` → `[^ ]+`, a plausible confusion of slash with
  space:
  `exempt='^[^RC][^RC] "?(memory|\.claude/handoff-[^ ]+\.md|inbox/[^ ]+\.md)"?$'`
  Run:
  `PYTHONPATH=/tmp/claude/build-fixes pytest -p rebind_script_plugin_s2_review_space tests/test_verify_step.py`
  → `6/8 passed, 2 failed`:
  - `test_nested_path_under_exempt_dir_is_dirty` failed on the assertion
    `assert result.returncode == 1` (in `_assert_dirty`), with output
    `CLEAN: tree clean, just precommit passed`.
  - `test_quoted_exempt_path_is_clean` also failed: `inbox/my brief.md`
    contains a space.
- **`noexempt`**: the alternation is cut to `memory` only, which is the
  bare-negative probe:
  `exempt='^[^RC][^RC] "?(memory)"?$'`
  → `4/8 passed, 4 failed`. The new test failed on the listing assertion,
  because all four `??` lines were listed. With the fixture as the RED wrote
  it, the listing would have been exactly the two nested lines and the test
  would have **passed** (finding 1).

The RED's three mutants were re-run against the revised test, and all three
still fail on assertions:
- `s2` fails on `returncode` (`CLEAN:`).
- `s2_inbox` fails on the listing (the inbox line is missing).
- `s2_handoff` fails on the listing (the handoff line is missing).

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The nested-path test was a bare negative**
   - Location: `tests/test_verify_step.py`,
     `test_nested_path_under_exempt_dir_is_dirty`
   - Problem: the fixture held only the two nested paths. Any pattern
     lacking an `inbox/` or `handoff-` exemption left both lines dirty, so
     the test passed both before the exemption existed and after it was
     deleted. The `noexempt` mutant above shows this. Its meaning depended
     on `test_conventional_dirt_...` failing alongside it, which is path
     staleness in `non-vacuous-negatives` terms. This matters before
     Item 1.2, which moves the alternation into a sourced file. A broken
     extraction of either alternative would leave this test green.
   - Fix: added untracked `inbox/x.md` and `.claude/handoff-x.md` to the
     same tree. Each is its nested partner one level up, so the only
     difference is the guard's trigger. The pre-status assertion now pins
     all four `??` lines. The DIRTY listing still asserts only the two
     nested lines, so the exempt siblings must be filtered out. The
     docstring gained a paragraph saying so.
   - **Status**: FIXED

2. **Line cap: the module was at 399/400 and the fix pushed it to 405**
   - Location: `tests/test_verify_step.py` (whole module)
   - Problem: at 399 lines the module was one line below the gate. The
     pairing fix needed 11 lines, which put it over the hard cap.
   - Fix: three module-wide seams, each removing duplication repeated
     across tests. No docstring was trimmed and no line was crammed.
     - `_stub_just(tmp_path) -> (bin_dir, marker)` now owns the
       `bin_dir = tmp_path / "bin"` / `marker = tmp_path / "just-invocations"`
       / `_stub_just(bin_dir, marker)` triple. That triple appeared at 6
       sites. The docstring now states that `marker` exists only once `just`
       has been invoked, which is what `not marker.exists()` relies on.
     - `_init_repo(tmp_path) -> Path` now owns the
       `repo = tmp_path / "repo"` / `_init_repo(repo)` pair. That pair
       appeared at 7 sites. It follows the same "helper owns its path under
       `tmp_path`" shape as `_stub_just`.
     - `_assert_dirty(result, *lines)` replaces the 6 repeated
       `returncode == 1` plus exact
       `["DIRTY: uncommitted changes", ...]` listing blocks. The assertions
       and their messages are the same as before: exact list equality, in
       order, with `result.stdout` attached.
   - Result: 380 lines, and the real script still passes `8/8`. Ruff's fix
     pass renamed the now-unused `marker` in
     `test_rename_out_of_exempt_path_is_dirty` to `_marker`.
   - **Status**: FIXED

### Minor Issues

None.

## Wrong-reason hunting

- **Can the test pass other than because the globs reject nested paths?**
  - Before the fix, yes: a pattern with no inbox or handoff exemption passed
    it (finding 1).
  - After the fix, `CLEAN` requires both nested lines to be exempted, and a
    listing of anything other than exactly the two nested lines fails. That
    excludes widened globs (`.+` and `[^ ]+`, either glob alone or both) and
    a pattern exempting neither directory.
  - `--untracked-files=all` drift, where directories collapse to
    `?? inbox/sub/`, is caught by the four-line pre-status assertion.
  - The `not marker.exists()` assertion is a real discriminator: `marker`
    is written only on the path that reaches `just precommit`.
- **Does the `_status` refactor preserve the existing tests?** Yes.
  - `_status` runs the same command,
    `_run_git(repo, "status", "--porcelain", "--untracked-files=all")`.
  - Each of the six refactored pre-assertions compares against the same
    literal it had before. I checked each one in `git diff`:
    - `MM .claude/handoff-task.md\n?? inbox/brief.md\n`
    - `MM memory\n`
    - `R  inbox/a.md -> notes.md\n`
    - `'?? "inbox/my brief.md"\n'`
    - the two-line quoted listing
    - the four-line XY listing
  - The whole module passes `8/8` on the real script.
  - Under the `noexempt` mutant, the three clean-phase tests fail on their
    own `returncode == 0` assertions. Their pre-assertions still hold, so the
    fixtures did not drift.

## Line cap — standing position

The module is at 380/400. Item 1.1 ends with this slice, and Item 1.2 puts
its tests in a new `tests/test_changed_files.py`. If this module needs to
grow past its headroom later, split it along this seam:
- the exemption-pattern tests: `conventional_dirt`, `memory_gitlink`,
  `rename`, `quoted`, `any_porcelain_state`, `nested_path`
- the fail-closed environment tests: `git_status_failure_exits_2`,
  `missing_just_exits_2`

The shared helpers would move to `tests/verify_step_helpers.py`, following
the existing `tests/*_helpers.py` pattern. `SCRIPT` would then live in the
helpers module, so a mutation plugin would rebind
`tests.verify_step_helpers.SCRIPT` instead.

## Fixes Applied

- `tests/test_verify_step.py` `test_nested_path_under_exempt_dir_is_dirty`:
  - added the `inbox/x.md` and `.claude/handoff-x.md` siblings
  - the pre-status assertion now pins four lines
  - the docstring has a paragraph on the pairing
  - the listing is asserted through `_assert_dirty` (finding 1)
- `tests/test_verify_step.py` `_stub_just`: now takes `tmp_path` and returns
  `(bin_dir, marker)`. Applied at 6 sites (finding 2).
- `tests/test_verify_step.py` `_init_repo`: now takes `tmp_path` and returns
  `repo`. Applied at 7 sites (finding 2).
- `tests/test_verify_step.py`: new `_assert_dirty(result, *lines)`. Applied
  at 6 DIRTY sites (finding 2).
- Scratch files, untracked and outside the repo:
  - `/tmp/claude/build-fixes/verify-step-mutant-s2-review-{space,noexempt}.sh`
  - `/tmp/claude/build-fixes/rebind_script_plugin_s2_review_{space,noexempt}.py`

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Major 6 / F-4: pin the single-level globs | Satisfied | Nested test fails under the `.+` mutant (both globs and each one alone) and under `[^ ]+`; passes on the real script |
| Slice 2: untracked `inbox/sub/x.md` and `.claude/handoff-dir/x.md` give exit 1 and the DIRTY listing carries both `??` lines | Satisfied | `_assert_dirty(result, "?? .claude/handoff-dir/x.md", "?? inbox/sub/x.md")` |
| Fixtures are `_init_repo` and `_stub_just`; the tracked script is never reverted | Satisfied | Both helpers are used (their signatures changed to own their paths); `verify-step.sh` has no diff |

## Positive Observations

- The RED proved each glob load-bearing on its own with single-glob mutants.
  That is the reason the DIRTY listing is asserted exactly, and not just the
  return code.
- Asserting the pre-status catches directory-collapse drift before the
  script runs.
- The mutants were kept out of the tracked path, and `SCRIPT` was rebound by
  a plugin instead of by editing the module.
