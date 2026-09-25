# Review: Item 1.2 / Slice 1 — test review

**Scope**: `tests/test_verify_step.py`,
`plans/build-defects/reports/item-1-2-s1-red.md`. SUT
`plugin/skills/build/scripts/verify-step.sh` read only (unchanged; `git diff`
empty).
**Date**: 2026-09-25
**Mode**: review + fix (TDD test review, dispatch 2 of 4)

## Summary

The RED run is genuine: the single test fails on its first assertion
(`returncode == 0`) against the unchanged script, which prints
`DIRTY: … ?? inbox/` plus the handoff line. The as-authored test still passed
six of the eight plausible wrong GREENs, though: exempting all of `.claude/`,
all of `inbox/`, the collapsed `?? inbox/` line under a bare status, a
single-porcelain-column handoff exemption, `.claude/handoff-*` of any
extension, and `.claude/*.md`. I made the fixture carry those distinctions
inside the one named test. After the fixes the test reds on the same first
assertion, every wrong candidate fails it, and the correct candidate passes.

**Overall Assessment**: Ready

## Mechanical first check

`PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_verify_step.py -v`

- Before fixes: 1 failed, 0 passed, 0 errors. FAILED at the assertion
  `result.returncode == 0`. The stdout was `DIRTY: uncommitted changes` /
  `M  .claude/handoff-task.md` / `?? inbox/`.
- After fixes: 1 failed, 0 passed, 0 errors. FAILED at the same assertion
  (now line 121). The stdout was `DIRTY: uncommitted changes` /
  `MM .claude/handoff-task.md` / `?? inbox/`. This is a real behaviour red, not
  an ImportError or setup error.

## Candidate-GREEN probe (measured)

I wrote each candidate as a standalone script in a scratch dir under `$TMPDIR`
and removed the dir afterwards. The SUT was never touched. For each run, the
test module's `SCRIPT` global pointed at the candidate. The script resolves
nothing from its own path, since it runs `git status` in CWD, so pointing at a
copy does not rebind any path. Each candidate filters
`git status --porcelain[ --untracked-files=all]` with `grep -vxE` and follows
the current script's DIRTY/CLEAN shape.

| Candidate | As authored (RED report) | After review |
|---|---|---|
| A correct: `-uall`; `.. .claude/handoff-[^/]*\.md`, `.. inbox/[^/]*\.md` | PASS | PASS |
| B exempts all of `.claude/` | PASS | FAIL (dirty listing) |
| C exempts all of `inbox/`, any file, any depth | PASS | FAIL (inbox phase: CLEAN) |
| D no `-uall`; exempts `?? inbox/` dir line | PASS | FAIL (inbox phase: CLEAN) |
| E exempts only untracked (`??`) state | FAIL | FAIL (clean phase) |
| F handoff exempt only as `M ` (index column) | PASS | FAIL (clean phase) |
| G skips `just precommit` | FAIL | FAIL (precommit record) |
| H `.claude/handoff-*` of any extension | PASS | FAIL (dirty listing) |
| I `.claude/*.md` (any md under `.claude/`) | PASS | FAIL (dirty listing) |

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Over-broad `.claude/` exemption undetected**
   - Location: `tests/test_verify_step.py`, the DIRTY phase
   - Problem: `.claude/handoff-task.md` was the only path under `.claude/`, and
     the DIRTY phase checked only `?? stray.txt` membership. So exempting all of
     `.claude/`, `.claude/*.md` or `.claude/handoff-*` passed (B, H, I).
   - Fix: added untracked decoys `.claude/notes.md` and
     `.claude/handoff-notes.txt` to the DIRTY phase. Each matches one
     over-broad pattern and not `.claude/handoff-*.md`.
   - **Status**: FIXED

2. **Over-broad `inbox/` exemption and the collapsed-directory shortcut
   undetected**
   - Location: `tests/test_verify_step.py`, the whole test
   - Problem: the only `inbox/` content was an exempt `.md` file. Exempting all
     of `inbox/` passed (C). So did keeping the bare `git status --porcelain`
     and exempting its `?? inbox/` line (D), which is the exact shortcut KD-7's
     `--untracked-files=all` rule rules out. A non-`.md` `inbox/` decoy could
     not go in the DIRTY phase, because the slice requires that output to name
     no `inbox/` path.
   - Fix: added an inbox phase at the end of the same test. It removes
     `stray.txt` and the `.claude/` decoys, adds untracked `inbox/notes.txt`,
     and asserts exit 1 with the exact listing
     `DIRTY: uncommitted changes` / `?? inbox/notes.txt`. Under C or D this
     phase gives exit 0 `CLEAN:`. A bare status that did not exempt `?? inbox/`
     would print `?? inbox/` and fail the exact listing.
   - **Status**: FIXED

3. **Handoff exemption pinned in only one porcelain column**
   - Location: `tests/test_verify_step.py`, clean-phase fixture
   - Problem: the handoff file was staged only (`M `), so an exemption keyed to
     the index column passed (F). KD-7 says "in any porcelain state".
   - Fix: stage the edit, then modify the worktree again, which gives `MM`. The
     slice wording "staged, modified" covers this. A fixture guard now asserts
     that `git status --porcelain --untracked-files=all` is exactly
     `MM .claude/handoff-task.md` / `?? inbox/brief.md` before the script runs.
     The fixture therefore demonstrably reaches the states the docstring
     claims.
   - **Status**: FIXED

4. **Exempt lines echoed in DIRTY output not fully pinned**
   - Location: `tests/test_verify_step.py`, DIRTY-phase assertions
   - Problem: `"?? stray.txt" in lines` plus "no line names `inbox/`" still let
     the handoff line, or any other extra line, through. A GREEN that exempts
     only in an "all lines exempt, so CLEAN" check but still echoes exempt lines
     when something else is dirty would pass.
   - Fix: replaced both checks with an exact-block equality on
     `stdout.splitlines()`: header plus the three non-exempt lines, in git's
     path order. This subsumes the slice's `DIRTY:`, `?? stray.txt` and
     no-`inbox/` assertions.
   - **Status**: FIXED

### Minor Issues

1. **Stub `just` proved invocation, not `just precommit`**
   - Location: `_stub_just`, clean-phase marker assertion
   - Problem: `touch "$marker"` showed only that `just` ran, with any arguments.
   - Fix: the stub appends `$*` to the marker, and the test asserts the content
     is exactly `precommit\n`: one call, correct recipe.
   - **Status**: FIXED

2. **Docstrings out of step with the strengthened test**
   - Location: `_stub_just` and test docstrings
   - Fix: rewrote them to describe the three phases and the pattern each decoy
     rules out. Summary lines stay on one physical line of 80 columns or fewer.
     A format pass had wrapped an earlier over-long draft, which ruff D205
     flagged; both summaries are now shortened.
   - **Status**: FIXED

## Checks confirmed without change

- **Stub shadows the real `just`**: `/usr/local/bin/just` exists. `bin_dir` is
  prepended to `PATH` in the script's env only. The marker content proves the
  stub ran; a real `just` in the tmp repo has no justfile and would exit
  non-zero.
- **Git insulation**: `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` point to
  `os.devnull` for both the setup git calls and the script run. This also
  neutralises a user `status.showUntrackedFiles` or `core.excludesFile`. The
  env still inherits `GIT_CONFIG_COUNT`/`GIT_CONFIG_PARAMETERS`, which today
  carry only `safe.directory` and the proxy. `GIT_DIR`/`GIT_INDEX_FILE` would
  leak if pytest ran under a git hook. `tests/test_triage_feedback.py` uses the
  same pattern, so I did not raise this as a finding.
- **Invocation as `/build` invokes it**: absolute script path, CWD at the tmp
  repo root, no args. `SKILL.md` runs
  `plugin/skills/build/scripts/verify-step.sh` bare.
- **Fixture reachability**: every state comes from real git operations
  (commit, add, edit, untracked write), with no hand-authored porcelain.

## Residual (not pinned, by choice)

- **Nested inbox depth** (`inbox/sub/x.md`): whether KD-7's `inbox/*.md`
  covers subdirectories is not settled by the outline. `*` crosses `/` in
  shell `case` and in git pathspec. Pinning either answer would decide it for
  GREEN, so I left it open.
- **` M memory`**: already implemented in the pre-fix script and not the
  slice's target.
- **DIRTY short-circuits before precommit**: existing behaviour, outside this
  slice.

## Fixes Applied

- `tests/test_verify_step.py` `_stub_just`: the stub now appends its args to
  the marker instead of touching it.
- `tests/test_verify_step.py` clean phase: handoff set to `MM` (stage, then
  edit again); added the exact-porcelain fixture guard; added the
  `marker == "precommit\n"` assertion.
- `tests/test_verify_step.py` DIRTY phase: added the `.claude/notes.md` and
  `.claude/handoff-notes.txt` decoys; the assertions are now one exact-block
  equality.
- `tests/test_verify_step.py` inbox phase (new, same test): an untracked
  `inbox/notes.txt` must be listed exactly, with exit 1.
- `tests/test_verify_step.py` docstrings: rewritten to match; summaries of 80
  columns or fewer.
- Lint: `docformatter -c` exit 0, `ruff check` clean, `ruff format --check`
  clean, `mypy` exit 0.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| orch m5 / KD-7: exemptions in any porcelain state | Pinned | clean phase `MM` handoff, untracked inbox md |
| KD-7: only `.claude/handoff-*.md`, `inbox/*.md` | Pinned | DIRTY decoys; inbox phase `inbox/notes.txt` |
| KD-7: status under `--untracked-files=all` | Pinned | inbox phase exact `?? inbox/notes.txt`; candidate D fails |
| Slice text: exit 0 + `CLEAN:`; then exit 1, `DIRTY:`, `?? stray.txt`, no `inbox/` | Pinned | clean-phase assertions; exact DIRTY block |
| Item 1.2 harness: real git, one commit, abs path, CWD root, stub `just` first on PATH | Satisfied | `_init_repo`, `_run_script`, `_stub_just` |

## Positive Observations

- The RED report's reasoning is accurate: no stub is needed because the SUT
  exists without the behaviour, and the red is a real assertion failure.
- The stub `PATH` and the git config insulation are scoped to per-call
  `env=` dicts, with no process-wide mutation.
- The setup helpers assert with stderr attached (D-21).
