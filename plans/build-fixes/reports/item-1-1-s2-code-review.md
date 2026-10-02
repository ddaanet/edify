# Review: build-fixes Item 1.1, slice 2 (code review)

**Scope**: `plugin/skills/build/scripts/verify-step.sh` as of HEAD `0aab33f3`.
The slice changed no implementation. Reviewed: whether the single-level globs
`\.claude/handoff-[^/]+\.md` and `inbox/[^/]+\.md` classify nested paths
correctly — quoted paths, a nested path whose last segment ends `.md`, and
directories exploded by `--untracked-files=all` — and whether the test runs
the script the way production does.
**Date**: 2026-10-02
**Mode**: review + fix

## Summary

The globs handle every nested shape probed. One gap came out of the quoting
question: the script assumes git quotes non-ASCII bytes, and a user's
`core.quotePath=false` breaks that assumption. Then a path holding an invalid
UTF-8 byte, nested under an exempt directory or anywhere else, makes GNU grep
treat its input as binary and drop that line. The gate read CLEAN with that
dirt in the tree. Fixed with one line: the status call now forces
`core.quotePath=true`.

**Overall Assessment**: Ready (one major fixed; it has no pinning test yet, see
Recommendations)

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Fail-open under `core.quotePath=false`: dirt containing an invalid UTF-8
   byte reads CLEAN**
   - Location: `plugin/skills/build/scripts/verify-step.sh:20` pre-fix (the
     `git status` call), `:22` post-fix
   - Problem: the comment at lines 13-14 says "Git quotes a path holding a
     space or a non-ASCII byte". That holds only while `core.quotePath` is
     true. With `false`, which non-English users set routinely, git prints
     bytes ≥ 0x80 raw. If a byte is not valid UTF-8 and the locale is UTF-8
     (`C.UTF-8` here), GNU grep 3.11 calls stdin binary, prints
     `grep: (standard input): binary file matches` to stderr, drops the
     offending line from stdout, and still exits 0. The script's exit-code
     branch takes exit 0 to mean "lines survived", reads the empty `status`
     as clean, and runs precommit. Probe (`/tmp/claude/build-fixes/probe-s2-code-binary.sh`,
     real script, `git config core.quotePath false`, untracked
     `inbox/x\377/y.md` and `evil\377.sh`):

     ```
     grep: (standard input): binary file matches
     CLEAN: tree clean, just precommit passed
     exit=0
     ```

     This touches the slice directly: the nested `inbox/x\377/y.md` is
     exactly the dirt the slice pins, and here it reads clean. It is a
     general fail-open, not one specific to nested paths. The test suite
     cannot see it because `_run_git` and `_run_script` set
     `GIT_CONFIG_GLOBAL=/dev/null`. Production runs under the user's config,
     so the defect sits in exactly that gap.
   - Fix: `git -c core.quotePath=true status --porcelain --untracked-files=all`.
     This makes the comment's claim true whatever the user's config. Porcelain
     output is then pure ASCII (control characters, `"` and `\` are always
     escaped; bytes ≥ 0x80 become octal), so grep's locale and binary
     heuristics no longer matter, and that includes macOS BSD grep. The
     comment gains two sentences naming the reason. I preferred this over
     `LC_ALL=C grep` or `grep -a`: those keep raw bytes and would echo them
     in the DIRTY listing, and they leave the quote allowance in the pattern
     depending on config.
   - **Status**: FIXED

### Minor Issues

None.

## Evidence

**Nested-path probe** (`/tmp/claude/build-fixes/probe-s2-code.sh`, scratch
repos, stub `just`, insulated config). The probe ran against both the original
and the fixed script, with the same verdicts:

| Fixture (porcelain line) | Verdict |
|---|---|
| `?? "inbox/sub dir/x.md"`, `?? ".claude/handoff-a b/x y.md"`: quoted nested | DIRTY, both listed |
| `?? inbox/a.md/b.md`, `?? .claude/handoff-x.md/y.md`: directory named `*.md` holding a `.md` | DIRTY, both listed (`[^/]+` stops at `/`, and `\.md"?$` cannot sit mid-path) |
| `?? inbox/n.md/`: nested repo, which `--untracked-files=all` does not explode | DIRTY (trailing `/` fails `\.md"?$`) |
| `?? inbox/a/b/c/d.md`: three levels deep | DIRTY |
| `?? "inbox/caf\303\251/x.md"`: non-ASCII nested, default quoting | DIRTY |
| `inbox/café/x.md` under `core.quotePath=false` (valid UTF-8) | DIRTY |
| `inbox/x\377/y.md` + `stray.txt` under `core.quotePath=false` | pre-fix: DIRTY listing only `stray.txt` (nested line dropped); post-fix: both listed, quoted |
| `inbox/.md`, `.claude/handoff-.md`: empty stem | DIRTY (`[^/]+` needs one character); errs toward dirt, not a defect |

After the fix, under `core.quotePath=false`, single-level `inbox/café.md` and
`inbox/x\377.md` still read CLEAN (forced to `"inbox/caf\303\251.md"` and
`"inbox/x\377.md"`, both matched through the quote allowance).

**Exploding.** `--untracked-files=all` turns `inbox/sub/` into
`inbox/sub/x.md`. The only untracked directory it leaves collapsed is a nested
repository. That line ends in `/`, so the `$` anchor marks it dirty whatever
the directory is named.

**Invocation parity.** Same as slice 1's review: production calls
`plugin/skills/build/scripts/verify-step.sh` from the repo root (`SKILL.md:53`,
`:150`; `finishing.md:62`). The test runs it by absolute path with
`cwd=repo`. The script never reads `$0`, and porcelain paths are always
relative to the repo root. One difference matters: the test's config
insulation. That insulation hid Major 1, and it is the right place for a
pinning test to inject `core.quotePath=false` (repo-local config survives
`GIT_CONFIG_GLOBAL=/dev/null`).

**Mutated-SUT run (one).** Copy `/tmp/claude/build-fixes/verify-step-mutant-s2-code.sh`
was rebound by `rebind_script_plugin_s2_code.py`, the RED plugin with
`MUTANT` repointed. The mutant drops the trailing `$` from the exempt pattern
and nothing else (confirmed by a one-line `diff`). Full module: **7/8 passed**.
`test_nested_path_under_exempt_dir_is_dirty` **stayed green**, and only
`test_memory_gitlink_is_clean_and_a_sibling_name_is_not` redded, because
`memory.md` matched the bare `memory` prefix. So the slice test detects
`[^/]+` widened to `.+` (RED's three mutants) but not a missing end anchor.
In this pattern the anchor is shared by all three alternatives, so the memory
decoy covers it.

`git diff --quiet` confirmed the tracked script untouched after the mutant
run. The fix was applied afterwards.

**Post-fix checks.** `shellcheck` clean, and
`pytest tests/test_verify_step.py` gave 8/8 passed. `just precommit` was not
run, because this dispatch commits nothing.

## Fixes Applied

- `plugin/skills/build/scripts/verify-step.sh:22`: `git status` became
  `git -c core.quotePath=true status`, so porcelain is always quoted ASCII
  and grep cannot drop a line as binary.
- `plugin/skills/build/scripts/verify-step.sh:14-16`: two sentences added to
  the header comment giving the reason for forcing `core.quotePath`.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Major 6 / F-4: exempt globs are single-level (slice-2 share: nested `inbox/sub/x.md`, `.claude/handoff-dir/x.md` are dirt) | Satisfied | `verify-step.sh:21` `[^/]+`; probe table; real-script 8/8 |
| KD-7: any change is dirt except the three conventional paths | Satisfied after fix | pre-fix fail-open under `core.quotePath=false` (Major 1) |
| Item 1.1: tracked script never reverted; mutant is a rebound copy | Satisfied | `git diff --quiet` after the mutant run |

---

## Positive Observations

- The `$` anchor after the optional closing quote also closes the
  directory-named-`*.md` and collapsed-nested-repo cases, with no extra
  alternative needed.
- The grep exit-code split (0 / 1 / other) is sound. Major 1 was a case
  where grep exits 0 with lines silently withheld, which no exit-code
  handling can see. Fixing the input was the only correct remedy.

## Recommendations

- **Pin Major 1 with a test (orchestrator's call where it lands).** Suggested
  fixture: `git config core.quotePath false` in the test repo, plus an
  untracked `inbox/x\377/y.md` (bytes path, Linux). Expected result: exit 1
  and `?? "inbox/x\377/y.md"` listed. Mutant: drop `-c core.quotePath=true`.
  macOS APFS rejects invalid UTF-8 names, so the test needs a skip there.
  This is untested by the suite: the fix went in through code review, which
  never edits tests. `tests/test_verify_step.py` is at 380 lines, so a
  ~25-line test fits under the 400 gate.
- **Carry the same forcing into Item 1.2.** `changed-files.sh` will parse git
  path output against the same alternation (KD-6). Any `git status`/`git diff
  --name-only` it runs needs `-c core.quotePath=true` too, or the same binary
  drop can hide a changed path. Recorded here for Item 1.2's dispatch; not
  done.
- **Guard for Item 1.2's extraction.** The slice test does not pin the end
  anchor (mutant run above). If the extraction puts anchors on each
  alternative separately, only `memory`'s anchor stays pinned. A
  `inbox/a.md/b.md` fixture would cover the other two.
- No `REFACTOR-NEEDED`.
