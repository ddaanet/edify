# Review: Item 1.2 slice 1 — code review of `changed-files.sh`

**Scope**: `plugin/skills/build/scripts/changed-files.sh` as committed in HEAD
(22998e19): the base derivation, the `BASE:` line, the NUL-delimited committed
diff with `plans/<job>/` dropped, and usage/git-failure exit 2. The test file
was not edited.
**Date**: 2026-10-02
**Mode**: review + fix

## Summary

The committed script does what slice 1's test asks. The committed-range diff,
the NUL read, the quoted `case` prefix and the `||` checks on the substitutions
are all sound. Probes against scratch repos found two silent wrong answers and
three false failures. Silent wrong answers: a glob-metacharacter job name
picked up a sibling job's report as the base, and `..` read `reports/item-*`
at the root. False failures: invocation from a subdirectory, a path named
`HEAD`, and a user's `log.showSignature`. All five are fixed. The root-commit
edge was already an error, and it now prints a specific message.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **A job name containing pathspec glob syntax silently yields a wrong base
   and leaks a sibling job's files**
   - Location: `changed-files.sh:20` pre-fix (the `git log` pathspec)
   - Problem: `plans/$job/reports/item-*` is a git pathspec, where `*`, `?`,
     `[` and `\` are glob syntax. The comment claimed that a glob job name
     "still matches literally". That holds for the `case` exclusion, but not
     for the pathspec. Probe: sibling job `jx` has an earlier item report,
     and job `j*` is run. The script printed exit 0, `BASE:` set to the
     parent of `jx`'s commit (wrong), and `plans/jx/reports/item-1.md` in the
     list. Empty, `.`, `..` and `/`-holding names have the same flaw: `..`
     returned a base derived from the root's `reports/item-*`, with exit 0.
   - Fix: reject `''`, `.`, `..`, `*/*` and any name holding `*?[\` with
     `ERROR: usage: … not a job name: <job>`, exit 2. This is the interface's
     usage error. The filter is a blocklist of exactly the hazards, so no
     charset is imposed on legitimate names: `j-x`, `j.x`, `j x`, `-j` and
     `:j` are accepted (a leading `:` cannot trigger pathspec magic, since
     the pathspec starts with `plans/`). The stale comment was replaced.
   - **Status**: FIXED

2. **Invocation from a subdirectory derives no base**
   - Location: `changed-files.sh:20` pre-fix
   - Problem: git resolves pathspecs relative to CWD. From `sub/`,
     `plans/j/reports/item-*` matches nothing and `first_commit` is empty.
     Today that falls through to `ERROR: git rev-parse failed` (probe F).
     Once slice 3 maps an empty `first_commit` to `NO-BASE:`, the same
     invocation would claim the run has no item report, which is a wrong
     verdict rather than an error.
   - Fix: `cd "$(git rev-parse --show-toplevel)"`, with each step checked
     for exit 2. This also neutralises a user's `diff.relative`. Probe F
     after the fix: correct `BASE:`, `sub/a.txt` listed.
   - **Status**: FIXED

### Minor Issues

1. **A path named `HEAD` makes the diff revision ambiguous**
   - Location: `changed-files.sh:37` pre-fix
   - Note: `git diff --name-only -z "$base_sha" HEAD` without `--` fails
     with `fatal: ambiguous argument 'HEAD': both revision and filename`
     when the worktree has a path named `HEAD`. Probe A: exit 2 on a valid
     run. Fixed by adding a trailing `--`. After the fix, probe A gives the
     correct base and lists `HEAD`.
   - **Status**: FIXED

2. **`log.showSignature=true` breaks base derivation for signing users**
   - Location: `changed-files.sh:20` pre-fix
   - Note: verified with an ssh-signed commit and `log.showSignature=true`.
     `git log --format=%H` prints `No signature` on stdout ahead of the sha,
     so the first line is not a sha and `rev-parse` fails (fail-closed, exit
     2). Fixed with `--no-show-signature` (git ≥ 2.10). Re-probe: correct
     `BASE:`, exit 0.
   - **Status**: FIXED

3. **The root-commit error message misled**
   - Location: `changed-files.sh:26` pre-fix
   - Note: when the first item commit is the root, the script already exited
     2 rather than inventing a base. The scope required that and it held. The
     output, though, was git's `ambiguous argument '<sha>^': unknown revision
     or path` followed by `ERROR: git rev-parse failed`. Now
     `git rev-parse --verify --quiet` prints nothing on failure, and the
     script says `ERROR: cannot resolve the parent of first item report
     commit "<sha>"`. A comment states that a root commit is an error, never
     a fallback base.
   - **Status**: FIXED

4. **The output line format cannot carry a newline in a path, and the
   comment implied full coverage**
   - Location: `changed-files.sh:11-12` pre-fix
   - Note: the read side is NUL-safe (probe D: leading space, leading `-`,
     a file named `--`, a backslash and a raw `\377` byte under
     `core.quotePath=false` all survive verbatim). The interface prints one
     path per line, though, so `new\nline.txt` comes out as two lines. That
     is inherent to the interface's line format. The header comment now
     states it as a residual bound.
   - **Status**: FIXED

## Fixes Applied

- `changed-files.sh` header comment: added the reason for
  `--no-show-signature` and the newline residual bound.
- `changed-files.sh` after the argument-count check: a `case` that rejects
  pathspec-unsafe or `plans/`-escaping job names with a usage `ERROR:`, exit 2
  (Major 1). The stale "glob metacharacter still matches literally" comment
  was removed.
- `changed-files.sh`: `git rev-parse --show-toplevel` and `cd`, each with an
  exit-2 check (Major 2).
- `changed-files.sh` `git log`: added `--no-show-signature` (Minor 2).
- `changed-files.sh` parent lookup: `git rev-parse --verify --quiet`, with a
  specific error naming the commit (Minor 3).
- `changed-files.sh` `git diff`: trailing `--` (Minor 1).

## Evidence

**Probes** were run in scratch repos with insulated config, against the real
script before and after the fixes:

| Probe | Pre-fix | Post-fix |
|---|---|---|
| A: path named `HEAD` | exit 2, git ambiguity error | correct BASE, `HEAD` listed |
| B: first item commit is root | exit 2, git's error + generic ERROR | exit 2, specific ERROR |
| C: job `j*`, sibling `jx` has an earlier report | exit 0, wrong BASE, `plans/jx/…` listed | exit 2, usage ERROR |
| D: sibling `plans/j-x/a.md`, spaces, `-lead`, `--`, `\`, `\377`, newline | all correct; `plans/j-x/a.md` kept; newline splits | unchanged |
| F: run from `sub/` | exit 2 | correct BASE, `sub/a.txt` |
| G: `color.ui=always` | no escape bytes (`od -c`) | unchanged |
| H: job `''` / `..` | exit 2 / exit 0 with wrong base | exit 2 usage ERROR, both |
| signed commit + `log.showSignature=true` | (fail-closed, shown on raw `git log`) | correct BASE |

On `core.quotePath`, following Item 1.1/2's recommendation: `-z` emits paths
verbatim, so quoting does not apply, and no grep touches the paths. The
binary-drop failure mode is absent from this slice.

**Exit-status honesty**: both substitutions use `v=$(cmd) || {…}`, and the
assignment takes the substitution's status, so failures surface. The diff
pipeline is guarded by `pipefail` plus `|| {…}`. The `while` loop drains
fully, so there is no SIGPIPE. A git failure after partial output still exits
2.

**bash 3.2 / BSD**: the script uses `[[ ]]`, `$'\n'`, `${v%%pat}`,
`read -r -d ''` and POSIX `case` brackets, all present in 3.2. It invokes no
BSD-divergent utility. Not run on macOS (no host here).

**Mutated-SUT run (one)**: exact-string replacement of
`-- "plans/$job/reports/item-*")` with `-- "plans/*/reports/item-*")`, the
unscoped-glob derivation the other-job decoy exists for. The test **redded on
its assertion**: `BASE: fc0d55…` against the expected `ab5d00…`, plus
`plans/other/reports/item-1-1.md` in the list. Restored by the inverse
replacement. Proof of restore: `grep -c 'plans/\*/'` gave 0,
`git diff --quiet` passed (identical to HEAD), and the slice test passed 1/1.
The review fixes were applied after that.

**Post-fix checks**: `shellcheck` clean. `pytest tests/test_changed_files.py`
1/1. `just precommit` gave `✓ Precommit OK` (370/371 passed, 1 xfail; three
allowlisted `oversized-file:` lines; design links 87 indexed). Nothing
committed.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| KD-1: base = parent of earliest `item-*` add | Satisfied | slice test; mutant run; probes C/F now correct or refused |
| KD-6 (slice-1 share): `<base> HEAD` diff minus `plans/<job>/` | Satisfied | slice test; probe D keeps sibling `plans/j-x/` |
| Interface: exit 0 `BASE:` + one path per line; exit 2 `ERROR:` on usage/git failure; NUL-read | Satisfied | probes A–H; newline bound documented |
| Major 1, m1, m2, m18 (slice-1 share) | Satisfied | as above; exempt paths and `NO-BASE:` are slices 2–3 (OUT) |

---

## Positive Observations

- Taking the first line with `${v%%$'\n'*}` instead of `| head -1` avoids the
  pipefail-plus-SIGPIPE trap.
- Streaming `git diff -z` straight into `read -d ''`, rather than capturing it
  in a variable that would drop the NULs, is the right shape.
- The quoted `"$exclude_prefix"*` with a trailing slash keeps sibling
  `plans/<job>-x/` (probe D).

## Recommendations

- **Pin the fixed edges with tests (the orchestrator decides where).** The
  slice test covers none of them: job-name rejection (`j*`, `..`),
  subdirectory invocation, a path named `HEAD`, and a sibling
  `plans/<job>-x/` path kept. The last one matters for slice 2. By
  reasoning, not by running it: a mutant that drops the trailing `/` from
  `exclude_prefix` would stay green, because the fixture has no sibling job
  path in the range.
- **Slice 3 must test for an empty `first_commit` before the parent lookup.**
  Otherwise the new `cannot resolve the parent … ""` error fires where
  `NO-BASE:` belongs.
- **Slice 2: filter the NUL-read paths in shell (`case`), not by piping raw
  paths into grep.** `-z` paths carry raw bytes, and a grep filter would
  bring back Item 1.1/2's binary-drop fail-open under `core.quotePath=false`.
- **Renames (observation, not a finding):** `--name-only` with git's default
  rename detection lists only a rename's destination. A file moved from
  `src/` into `plans/<job>/` therefore drops out of the list entirely. KD-6
  does not address renames, so this is noted for whoever owns that decision.
- No `REFACTOR-NEEDED`.
