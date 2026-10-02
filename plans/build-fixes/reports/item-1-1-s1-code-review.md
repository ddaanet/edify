# Review: build-fixes Item 1.1, slice 1 (code review)

**Scope**: `plugin/skills/build/scripts/verify-step.sh` as of HEAD `b0e71862`.
The slice changed no implementation. The script is reviewed for whether its
exemption holds for the four porcelain states the slice pins, and the
committed test is checked for whether it runs the script the way production
does.
**Date**: 2026-10-02
**Mode**: review + fix

## Summary

The exemption regex `^[^RC][^RC] "?(memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)"?$`
filters all four pinned lines (`A `, ` D`, `UU`, `D `). It also filters every
other non-rename state probed outside the suite (`AA`, `DU`, `UD`, ` A`, `T `).
The test runs the script the way production runs it. No defect was found in
this slice's behaviour, and no edits were made.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Evidence

**Exemption against the slice's states.** Each pinned line matches the
pattern:

- `A  .claude/handoff-new.md`: X=`A`, Y=space, both `[^RC]`, then the handoff
  alternative.
- ` D .claude/handoff-task.md`: same, with X=space and Y=`D`.
- `UU inbox/conflict.md`: `U`/`U`, then the `inbox/[^/]+\.md` alternative.
- `D  inbox/old.md`: same, with `D`/space.

On the real script, `pytest tests/test_verify_step.py` gives 7/7 passed.

**Probe beyond the slice** (scratch repo, `/tmp/claude/build-fixes/probe.sh`,
real tracked script, stub `just`): a real conflicting merge, plus a typechange
and an intent-to-add, produced this porcelain:

```
AA inbox/aa2.md
DU inbox/au.md
DU inbox/du.md
 A inbox/ita.md
T  inbox/t.md
UD inbox/ua.md
UD inbox/ud.md
```

Result: `CLEAN: tree clean, just precommit passed`, exit 0. The `[^RC]` class
admits every porcelain v1 status letter except rename and copy, which matches
KD-7 and the KD-7 addendum.

**Invocation parity.** Production calls the script as
`plugin/skills/build/scripts/verify-step.sh` from the repo root (`SKILL.md`
§2 and §After each item, `finishing.md` §1). `_run_script` runs it by absolute
path with `cwd=repo` and the stub `just` first on `PATH`. Three things make
these equivalent:

- The script never resolves its own location: no `$0` or `BASH_SOURCE`.
- `git status --porcelain` reports paths relative to the repo root no matter
  where the CWD is inside the repo.
- Both paths run the file directly, so both depend on the exec bit and the
  `#!/usr/bin/env bash` shebang.

The test also checks the stub marker equals `precommit\n`, which proves the
`command -v just` check and the `just precommit` call both ran.

**Mutated-SUT run (one).** The scratch copy is
`/tmp/claude/build-fixes/verify-step-mutant-s1-code.sh`. `SCRIPT` was rebound
by `/tmp/claude/build-fixes/rebind_script_plugin_code.py`, a copy of the RED
report's plugin with `MUTANT` repointed. The mutant replaces the complement
class with an explicit whitelist of the letters the module's fixtures use:

- Before: `exempt='^[^RC][^RC] "?(...)"?$'`
- After: `exempt='^[ MADU?][ MADU?] "?(...)"?$'`

Result: **7/7 passed. No test went red.** This is the expected outcome:

- The slice names four states, and the whitelist covers them.
- The two earlier mutants, `[ M?]` (RED) and `[^RCU]` (test review), already
  showed that each pinned letter is load-bearing.

The run shows where the module stops: no test in it would notice a whitelist
that drops `T` (typechange) or any other letter outside `{space, M, A, D, U, ?}`.
That is about test coverage, which is out of scope here, so it is recorded
under Recommendations rather than raised as a finding.

An earlier attempt at this mutant also deleted the space after the XY columns.
It gave 3/7 and was thrown away because it was not the intended mutant. The
copy was rebuilt and the one-line diff against the tracked file confirmed
before the run above.

`git diff --quiet plugin/skills/build/scripts/verify-step.sh` reported the
tracked script untouched after both runs.

## Fixes Applied

None. No defect was found in this slice's behaviour.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Major 6 / F-4: exemption holds in any non-rename porcelain state (slice-1 share: `A `, ` D`, `UU`, `D `) | Satisfied | regex `verify-step.sh:19`; real-script 7/7; probe above |
| KD-7 addendum: `R`/`C` lines fail closed | Satisfied (unchanged) | `[^RC]` in both columns; comment `verify-step.sh:11-13` |
| Item 1.1: tracked script never reverted; mutant is a rebound copy | Satisfied | `git diff --quiet` after each mutant run |

---

## Positive Observations

- The complement class `[^RC]` puts KD-7's rule directly into the pattern
  ("anything but a rename or copy"). It does not list allowed letters, so new
  porcelain letters are exempted without a code change.
- The exit-code handling separates grep's exit 1 ("every line filtered") from
  a real failure (exit 2). The pipe-not-here-string comment explains a failure
  mode that is easy to miss.

## Recommendations

- **Coverage bound for the orchestrator (not a defect):** the whitelist mutant
  above passes every test in the module. If Major 6 / F-4's "any porcelain
  state" should be pinned against a whitelist regression, the fixture needs a
  state outside `{space, M, A, D, U, ?}`. `T ` (typechange: `rm f && ln -s
  README.md f && git add f`) is the cheapest. Whether that belongs in Item 1.1
  is the orchestrator's call. The outline names only the four states.
- **Seam between UU and the commit form (observation):** the slice pins
  `UU inbox/...` as CLEAN, as KD-7 requires. The gate therefore passes while a
  merge is still in progress. Every committing dispatch uses
  `git commit -- <paths>` (KD-4), and git refuses that during a merge. The
  probe got `fatal: cannot do a partial commit during a merge.`, exit 128.
  That failure is loud, not silent, so the gate's verdict does not hide
  anything. It does mean CLEAN does not guarantee that the next commit can
  run. This is recorded for the design's KD-7 record, not raised as a script
  defect.
- No `REFACTOR-NEEDED`. Item 1.2 owns the planned extraction of the alternation
  into `exempt-paths.sh`, which is out of scope here and was not done.
