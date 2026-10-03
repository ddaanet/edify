# Review: Item 1.4 slice 2 — `--phase` base is the latest boundary commit

**Scope**: `plugin/skills/build/scripts/changed-files.sh`, the `--phase`
base query and its header comment as landed in HEAD (2a2bbafb). The tests are
out of scope and were not edited.
**Date**: 2026-10-03
**Mode**: review + fix

## Summary

The slice adds one `git log -1 --format=%H --no-renames --no-show-signature
"${base_sha}..HEAD" -- <pathspec>` query, run only under `--phase`. It
replaces the run base when the query finds a commit. The query matches KD-2's
literal form, its exit status is propagated, and the path with no flag is
byte-for-byte unchanged. One genuine defect: git's default pathspec `*`
matches `/`, so a file in a subdirectory of `reports/` counted as a phase
boundary. Fixed with `:(glob)` magic.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The pathspec `*` crossed `/`, so a non-boundary file could move the base
   forward**
   - Location: `plugin/skills/build/scripts/changed-files.sh:98` (query),
     header comment lines 28–35
   - Problem: without magic, git matches pathspecs with wildmatch and no
     `WM_PATHNAME`, so `*` also matches `/`. Probed on git 2.47.3 with a
     throwaway repo: `plans/j/reports/phase-*-corrector.md` matched
     `plans/j/reports/phase-1/old-corrector.md`. It did not match
     `plans/j/reports/sub/phase-1-corrector.md` (the literal
     `reports/phase-` prefix rules that out) or `phase-1-corrector.md.bak`
     (the pattern is anchored at its end). KD-2's rule names
     `plans/<job>/reports/phase-<P>-corrector.md`, which has no `/` after
     `phase-`, so a file under `reports/phase-1/` is not a boundary. A false
     match moves the base *forward*, and that is the unsafe direction:
     everything before the decoy drops out of the list the phase corrector
     reviews.
   - Fix: prefix the pathspec with `:(glob)`, which keeps `*` inside one path
     component, and state that reason once in the header comment.
     `:(glob)` also disables `log.follow` for this query (git allows only
     FROMTOP/LITERAL magic with follow), which removes one more config
     dependency.
   - **Status**: FIXED. Checked against the script on a probe repo
     (boundary → `a.txt` → `reports/phase-1/old-corrector.md` →
     `phase-1-corrector.md.bak` → `b.txt`). It prints the real boundary as
     `BASE:` and lists `a.txt`, `b.txt`. Shellcheck `-x` is clean, the 6
     `changed-files` tests pass, and `just precommit` passes.

### Minor Issues

None.

## Answers to the scope questions

- **Does pathspec `*` cross `/`?** Yes, without `:(glob)`. Fixed above.
- **`reports/sub/phase-1-corrector.md`**: matched neither before nor after
  the fix. It should not match: it is not the boundary report's path.
- **`phase-1-corrector.md.bak`**: matched neither before nor after the fix,
  which is correct.
- **`phase-2-design-corrector.md`**: matches both before and after the fix,
  because the spec's own glob `phase-*-corrector.md` admits it. No pipeline
  surface writes such a name today: `phase-boundary.md` and `escalation.md`
  name only `phase-<P>-corrector.md`, and the dispatch name is
  `phase-P-corrector`. Past plans did use the `phase-N-<role>-review.md`
  family (`phase-1-implementation-review.md`), though. A pathspec cannot
  express "digits only" (`phase-[0-9]*` still admits `-design`), so
  tightening this would mean enumerating widths or adding a regex filter.
  Left as the spec's glob; see Recommendations.
- **Range**: `"${base_sha}..HEAD"` excludes the run base. That is correct:
  the run base is the parent of the first item-report commit, so it belongs
  to an earlier run. `test_phase_without_boundary_gives_run_base` pins the
  range. Mutating it to `HEAD` (below) turns that test red.
- **Merges in the range**: the query is KD-2's literal form, and on linear
  history (what `/build` produces) it is exact. Two residual bounds, probed:
  (a) a branch forked *before* the run base and merged during the run brings
  its commits into `<run base>..HEAD`. A same-job `phase-*-corrector.md` on
  that branch becomes the base, and the list then over-reports (pre-run files
  appear). That is the safe direction. `--ancestry-path` does not cure it: on
  the same probe it named the merge commit instead, which is also not a
  boundary. (b) With merges, `-1` takes the newest by commit date, and that
  is not always the topologically latest. Neither bound is a defect against
  the spec. Both would be a change to KD-2.
- **Exit-status honesty**: `phase_commit=$(git log …) || { ERROR; exit 2; }`
  carries git's status through the assignment, there is no pipe, and
  `-1` makes git stop without SIGPIPE. An empty result with exit 0 is the
  specified fallback to the run base. `base_sha` is already verified by
  `rev-parse --verify`, so the range cannot be malformed. Git's own message
  reaches stdout through `exec 2>&1` ahead of `ERROR:`, as for every other
  query in the script.
- **No-flag path**: the new block is guarded by `[[ ${2:-} == --phase ]]`.
  The argument guard already makes `$2` either absent or exactly `--phase`.
  The bare call's output is unchanged, and both tests assert it in the same
  repo.
- **Comments**: the KD-2 paragraph is accurate (path not subject, no
  `--diff-filter`, `-1`, run-base fallback) and is stated once. It sits in
  the header with the KD-1/KD-6 paragraphs, not repeated at the query. The
  only addition is the `:(glob)` reason.

## Mutated-SUT run

Mutation (exact-string Edit): `--no-show-signature "${base_sha}..HEAD" --` →
`--no-show-signature HEAD --`. This is the whole-history search that KD-2's
range exists to rule out.

- `test_phase_without_boundary_gives_run_base`: **red** (BASE named the
  pre-run report commit).
- `test_phase_base_is_latest_boundary_commit`: green. This is expected and
  documented in its docstring: an in-run boundary is always later than any
  pre-run commit there.
- `test_phase_flag_only_as_exact_second_argument`: green, as expected (it
  does not exercise the query).

Restored by the inverse exact-string Edit. The restore is proven by `grep -F`
of the full fixed query line (line 98) and a green run of
`tests/test_changed_files.py` and `tests/test_changed_files_phase.py` (6/6).

## Fixes Applied

- `plugin/skills/build/scripts/changed-files.sh:98`: pathspec
  `"plans/$job/reports/phase-*-corrector.md"` →
  `":(glob)plans/$job/reports/phase-*-corrector.md"`.
- `plugin/skills/build/scripts/changed-files.sh:32-35`: header comment gains
  the reason for `:(glob)` (git's default `*` matches `/`), with the concrete
  decoy path.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Item 1.4: base = latest commit in `<run base>..HEAD` touching `phase-*-corrector.md`, by path not subject (KD-2, KD-8) | Satisfied | `changed-files.sh:97-104`; subject decoy in `test_phase_base_is_latest_boundary_commit` |
| No match → run base (KD-1) | Satisfied | `-n $phase_commit` guard; `test_phase_without_boundary_gives_run_base` |
| Prints `BASE: <sha>` and the same filtered list since that base | Satisfied | the shared `printf`/diff path after the block |
| Without `--phase` nothing changes | Satisfied | the `${2:-} == --phase` guard; bare-call assertions in both tests |
| Slice 2: one boundary landed → base is that commit, only later files listed | Satisfied | `test_phase_base_is_latest_boundary_commit` |

**Gaps:** none.

## Positive Observations

- The query is the KD-2 query nearly verbatim, with the script's established
  `--no-renames`/`--no-show-signature` hardening applied consistently.
- The error branch keeps the script's exit-code contract: exit 2 `ERROR:`,
  never exit 1, which means `NO-BASE:`.
- The phase base is put in `base_sha` and flows through the unchanged
  print/diff/filter path, so slice 3's filters need no new code.

## Recommendations

- `phase-2-design-corrector.md`-style names match the spec's glob. If a
  future phase role ever writes `phase-<P>-<role>-corrector.md`, it will be
  taken as a boundary. Whether to pin the boundary name to digits is a KD-2
  question, not a slice fix.
- The KD-1 `item-*` pathspec has the same `*`-crosses-`/` behaviour. It
  predates this slice and is not changed here. Note that the two queries now
  differ in magic, so a later reader does not "harmonise" the `:(glob)` away.
- Merged pre-run branches and commit-date ordering under `-1` (above) are
  residual bounds of KD-2's query on non-linear history. If `/build` ever
  supports merging work into a run, KD-2 needs a rule for it.

REFACTOR-NEEDED: none.
