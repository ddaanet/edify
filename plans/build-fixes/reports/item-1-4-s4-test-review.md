# Review: Item 1.4 / slice 4, test review (`core.quotePath` regression)

**Scope**: uncommitted test changes: the split of `tests/test_verify_step.py`
into `tests/verify_step_helpers.py`, `tests/test_verify_step_exemption.py` and
the remaining `tests/test_verify_step.py`, plus the new
`test_quotepath_false_does_not_hide_dirt`. Also the RED report
`plans/build-fixes/reports/item-1-4-s4-red.md`. `verify-step.sh` and
`exempt-paths.sh` are OUT.
**Date**: 2026-10-03
**Mode**: review + fix

## Summary

The split is faithful: every function from `HEAD:tests/test_verify_step.py` is
AST-identical in its new home, and nothing is lost. The new test passes on the
real script and redded on an assertion under both the RED mutant and a second,
independent mutant. One wrong-reason defect was found: the test inherited the
runner's locale, so under `C`/`POSIX` the hazard it pins does not occur. The
RED mutant then raised `UnicodeDecodeError` inside `subprocess.run` instead of
failing the assertion. Fixed by pinning `LC_ALL=C.UTF-8`. The test also moved
to the fail-closed module, which is where the split's own docstrings put it.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Red depends on the runner's locale: under `C` it is an ERROR from the
   wrong cause**
   - Location: `tests/test_verify_step_exemption.py::test_quotepath_false_does_not_hide_dirt`
     (pre-fix), at the `_run_script(repo, bin_dir)` call
   - Problem: the fail-open exists only when grep runs in a UTF-8 locale. In
     that locale GNU grep calls the raw `0xFF` byte binary and drops the line.
     `_run_script` copies `os.environ`, so a runner with `LANG` unset or
     `LC_ALL=C` (common in CI and containers) runs grep in `C`. There, grep
     passes the raw line through. Measured with the RED report's own mutant
     (`/tmp/claude/build-fixes/mutant-s4`, `-c core.quotePath=true` dropped):
     under `LC_ALL=C` and under `LC_ALL=POSIX`, the test failed with
     `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 37`
     inside `subprocess.run`'s `text=True` decode. It never reached
     `_assert_dirty`. That red does not show the stated reason (the dropped
     line). It shows only that raw bytes reached stdout. The test was
     discriminating only because this box sets `LANG=C.UTF-8`.
   - Fix: pass `extra_env={"LC_ALL": "C.UTF-8"}` to the script run, and add a
     docstring sentence saying why. Post-fix, the RED mutant run with an outer
     `LC_ALL=C` reds on `assert result.returncode == 1` with
     `grep: (standard input): binary file matches` / `CLEAN: …`. The real
     script stays green under an outer `LC_ALL=C` too.
   - Residual bound: on a Linux libc without a `C.UTF-8` locale, `setlocale`
     falls back to `C`. The real-script pass is unaffected, since its output
     is quoted ASCII. Only the mutant's discrimination is lost there. glibc ≥
     2.35 and musl both provide it.
   - **Status**: FIXED

### Minor Issues

1. **The new test sat in the exemption-pattern module**
   - Location: `tests/test_verify_step_exemption.py` (pre-fix, last test)
   - Note: the split's module docstrings define the seam. The exemption file
     holds "Exemption-pattern tests" (KD-7's three paths), and
     `test_verify_step.py` holds "Fail-closed tests". The new test pins the
     `git status` call's forced quoting against a fail-open. The nested
     `inbox/x\377/y.md` is dirt under the pattern either way, and the pattern
     is not what the test exercises. Moved, together with its `os`, `sys` and
     `pytest` imports. Line counts after the move: 94 / 240 / 109, where
     before they were 54 / 273 / 109.
   - **Status**: FIXED

2. **Bytes-path construction was more roundabout than needed**
   - Location: same test, `Path(os.fsdecode(os.fsencode(repo) + b"/inbox/x\xff"))`
   - Note: it re-encoded the whole repo path just to append a component.
     `repo / os.fsdecode(b"inbox/x\xff")` is equal (checked: `a == b`, and
     `os.fsencode` gives `…/inbox/x\xff`). It keeps the surrogateescape round
     trip that writes the raw byte, and it avoids ruff's PTH rules as the
     original did.
   - **Status**: FIXED

## Check results

**1. Mechanical, mutation red.**

- Real script: `pytest tests/test_verify_step.py tests/test_verify_step_exemption.py`
  gives **9/9 passed**. Under an outer `LC_ALL=C` it also gives **9/9 passed**.
- RED report's mutant (copy with `-c core.quotePath=true` dropped, `SCRIPT`
  rebound by `rebind_s4`): **8/9 passed, 1 failed**. The failure is
  `test_quotepath_false_does_not_hide_dirt` on `assert result.returncode == 1`,
  with stdout `grep: (standard input): binary file matches` /
  `CLEAN: tree clean, just precommit passed`. The result is the same with no
  outer `LC_ALL` and with outer `LC_ALL=C` (post-fix).
- **Independent mutant** under `/tmp/claude/build-fixes/review-s4/`: copies of
  `verify-step.sh` and `exempt-paths.sh`. A Python replacement, with its count
  asserted to be 1, turned `git -c core.quotePath=true status` into
  `git -c core.quotePath=false status`. This forces the hazard regardless of
  repo config. `diff` shows only line 40 changed, and
  `grep -c "quotePath=false status"` gives 1. The plugin
  `rebind_review_s4.py` asserts `tests.verify_step_helpers` is imported and
  `SCRIPT != MUTANT`, then rebinds it. Result: **8/9 passed, 1 failed**, the
  same test, the same assertion, the same `binary file matches` / `CLEAN:`
  output. This holds with no outer `LC_ALL` and with outer `LC_ALL=C`.
- `git diff --quiet plugin/skills/build/scripts/` exits 0, so the tracked
  scripts are untouched.

**2. Split integrity.**

- An AST comparison against `git show HEAD:tests/test_verify_step.py` was run
  after all fixes.
  - All six helpers (`_run_git`, `_status`, `_init_repo`, `_stub_just`,
    `_run_script`, `_assert_dirty`) are identical in `verify_step_helpers.py`.
  - The six exemption tests are identical in `test_verify_step_exemption.py`.
  - `test_git_status_failure_exits_2` and `test_missing_just_exits_2` are
    identical in `test_verify_step.py`.
  - Nothing is missing.
- `REPO_ROOT` and `SCRIPT` keep their definitions. The `*_helpers.py` name
  follows the existing `tests/changed_files_helpers.py`,
  `tests/review_range_helpers.py` and others. No other module imported from
  `tests.test_verify_step`.
- **`SCRIPT` now lives in `tests.verify_step_helpers`.** `_run_script` reads
  the module global at call time, and no test module imports `SCRIPT` by name.
  A rebind there therefore reaches every test in both files.
- Item 1.1's recorded recipe does not work against the new layout. Its
  plugins rebind `sys.modules["tests.test_verify_step"].SCRIPT`, and its
  commands name `tests/test_verify_step.py::test_exempt_paths_clean_in_any_porcelain_state`.
  The recipe fails closed, not silently:
  `/tmp/claude/build-fixes/rebind_script_plugin.py` raises `AttributeError` on
  `mod.SCRIPT != MUTANT` (confirmed: `hasattr(tests.test_verify_step, "SCRIPT")`
  is `False`). pytest exits 3 with 0 tests run. To re-run Item 1.1's mutants,
  rebind `tests.verify_step_helpers.SCRIPT` and target
  `tests/test_verify_step_exemption.py`. The RED-s4 plugin and this review's
  plugin do exactly that.
- Full suite: `pytest tests/` gives **364/380 passed, 16 skipped**, and no
  collection errors.

**3. Wrong-reason hunting on the new test.**

- *State that fails it:* the status call not forcing `core.quotePath=true`,
  run under a UTF-8 grep. That condition is now pinned (Major 1).
- *What else could produce exit 1 plus the quoted listing:* nothing.
  - The listing is the exact quoted line, and only git with quoting on emits
    it.
  - The nested path is non-exempt in either form, so the exemption pattern
    can neither cause the CLEAN under the mutant nor hide the line under the
    real script.
  - `just` not being invoked confirms that the DIRTY branch fired.
- *Bytes-path fixture:* sound. The surrogateescape `Path` writes the raw
  `0xFF` byte, as both mutants prove by tripping grep's binary detection. The
  config is repo-local, which survives `GIT_CONFIG_GLOBAL=/dev/null`.
- *Exact-listing assertion:* it would also red on an alternative fail-closed
  fix that emits the raw byte, such as `grep -a` without forced quoting. That
  red would be a decode ERROR, not an assertion. This was accepted: the
  suite's convention is the exact listing (`_assert_dirty`), and the slice
  pins the existing fix.
- *macOS skip:* correctly scoped. APFS (and HFS+) refuse a filename that is
  not valid UTF-8, so the fixture cannot be created on `darwin`. The reason
  string states that. Linux is where the fail-open was measured.

**4. Lint and size.**

- `ruff check`: all checks passed. `ruff format --check`: 3 files already
  formatted. `docformatter -c`: exit 0. This covers all three test files.
- Sizes are 94 / 240 / 109 lines, all well under 400.
  `scripts/check_line_limits.sh` reports no test file. Its three
  `oversized-file` lines are `plugin/agents/*corrector.md` files and fall
  outside this scope.

## Fixes Applied

- `tests/test_verify_step.py`: added `test_quotepath_false_does_not_hide_dirt`,
  moved from the exemption module. The script run now passes
  `extra_env={"LC_ALL": "C.UTF-8"}`, and the docstring gives the reason. The
  nested path is built as `repo / os.fsdecode(b"inbox/x\xff")`. Imports gained
  `os`, `sys`, `pytest`, `_assert_dirty`, `_run_git` and `_stub_just`
  (ruff-formatted).
- `tests/test_verify_step_exemption.py`: removed the test and its now-unused
  `os`, `sys` and `pytest` imports. The six exemption tests are unchanged.
- `plans/build-fixes/reports/item-1-4-s4-red.md`: added a note that the test
  moved and pins `LC_ALL`, with the reproduction target and the expected count
  (`8/9 passed, 1 failed`). The RED run's original figures are kept as
  recorded.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Item 1.4/4: repo-local `core.quotePath false` + untracked `inbox/x\377/y.md` → `verify-step.sh` exit 1 | Satisfied | `tests/test_verify_step.py::test_quotepath_false_does_not_hide_dirt`; real 9/9 |
| Skipped on macOS | Satisfied | `skipif(sys.platform == "darwin")` |
| Mutation red, as in Item 1.1 (tracked script never edited) | Satisfied | two mutants each 8/9 with the named test failing on its assertion; `git diff --quiet plugin/skills/build/scripts/` exit 0 |
| Pins 1.1/2 code review Major 1 | Satisfied | red output reproduces that Major's probe (`binary file matches` / `CLEAN:`) |

## Files to stage

- `tests/test_verify_step.py`
- `tests/test_verify_step_exemption.py`
- `tests/verify_step_helpers.py`
- `plans/build-fixes/reports/item-1-4-s4-red.md`
- `plans/build-fixes/reports/item-1-4-s4-test-review.md`

## Positive Observations

- The split was done mechanically: it is AST-identical, it takes the seam the
  helpers already formed, and it follows the existing `*_helpers.py`
  convention.
- The RED plugin asserts both that the module exists and that `SCRIPT !=
  MUTANT` before it rebinds, so a stale module name fails loudly. This review
  confirmed that against Item 1.1's old plugin.
- The fixture rejections are recorded with reasons (`_status` text decode,
  global config nulled), which made the fixture quick to audit.
