# Deliverable Review — code

**Scope.** Layer 1, code partition, round 3. Range
`d444630c01bd98851cddbedde3fbc9b85c18345d..HEAD`, final state at HEAD. Files:
`plugin/bin/triage-feedback.sh`,
`plugin/skills/build/scripts/changed-files.sh`,
`plugin/skills/build/scripts/exempt-paths.sh` and
`plugin/skills/build/scripts/verify-step.sh`, each read whole. The baseline is
`plans/review-fixes-2/outline.md` (KD-1, KD-2, Items 1.1, 1.2, 1.5) and
`docs/references/build-run-state.md` D-88 to D-94 as now written. I loaded the
recall artifact, its five memory files and `shell-scripting:shell-gotchas`.

**Method.** Probes ran on throwaway repos under `$TMPDIR/dr3-code` with
`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null`, against the in-repo
scripts. Failure arms were reached with `PATH` shims for `git`, `grep` and
`sed`, and with unreadable files. Each finding says whether it was probed or
reasoned. The targeted suite (`just test` over the seven triage, changed-files
and verify-step modules) ran in the foreground: 50/50 passed. With shellcheck
0.10.0, the default run is clean. `--enable=all` reports only SC2250 (style),
SC2249 (info) and SC2312 on the `review_artifact` `find | wc -l`. Those lines
did not change in the range, so that report is not counted as a finding.

**Portability.** The macOS / bash 3.2 checks were reasoned, not run. No bash
3.2 binary was available.

- Constructs the scripts use that bash 3.2 supports: `$'\n'` inside
  double-quoted `${…%%…}` (`extquote` is on by default since bash 3.0, per bash
  CHANGES), array `+=`, `read -r -d ''`, `PIPESTATUS`, `compgen -G` and
  `[[ =~ ]]` with the regex in a variable.
- Under `set -u`, `"${list_pathspecs[@]}"` is expanded only when the array is
  non-empty.
- The external tools stay portable to BSD: `wc` padding is stripped,
  `find -maxdepth` and `sed -E` are BSD-safe, and `date -u +%Y-%m-%d` is
  portable.
- I found no GNU-only form.

## Round-2 findings status

- **C1 — resolved (probed).** A Simple run committed `item-1-1.md`, a
  non-report file and the gate reports `review-code.md` and `tdd-audit.md`. It
  read `- Reports: 0`, `- Behavioral code: no` and verdict `match`. With the
  label `Complex`, the verdict was `overclassified`, so that branch is
  reachable again. A slice report (`item-1-1-s1-red.md`) counted
  `- Reports: 1`.
- **M1 — resolved (probed).** The run commit held `item-1-1.md`, `notes.txt`,
  `inbox/x.md`, `.claude/handoff-task.md` and a file named `HEAD`. It read
  `- Files changed: 2`: `notes.txt` and `HEAD`. Behavioural code reads only the
  list's paths, as `:(literal)` pathspecs.
- **m1 — resolved (probed).** `changed-files.sh` no longer has
  `exec 2>&1`. In an unborn repo, stdout is exactly
  `ERROR: git log failed` and stderr carries git's `fatal:`. A late diff
  failure is a separate edge, covered under Minor 2.
- **m2 — resolved as a documented limitation.** D-90's **Limitation**
  paragraph states the linear-history assumption and the merge-only-report
  `NO-BASE:` case.
- **m3 — resolved (probed, and documented in D-90).** An unborn `HEAD` exits
  2 with `ERROR:`, never `NO-BASE:`.
- **m4 — resolved (probed).** Every git call in `triage-feedback.sh` puts
  `--` before its pathspecs. A tracked file named `HEAD` is counted and the
  script exits 0.
- **m5 — resolved (form checked; behaviour probed).** The script uses no
  here-string. The behavioural match is a pipe that reads grep's status from
  `PIPESTATUS[1]`. A `grep` shim exiting 2 on `-qE` gave
  `ERROR: grep failed` and exit 2.
- **m6 — resolved (probed).** The script has no `xargs` and no `|| true`.
  `- **Classification:** Moderate (my human partner's call)` gives
  `no-classification` and the label verbatim, apostrophe included. Nothing
  goes to stderr.
- **m7 / KD-2 — resolved (probed).** Two runs on the same evidence left one
  row. A run after a closing commit that landed the log also left one row: the
  log is dropped from the list, and `tdd-audit.md` is excluded from Reports.
- **m8 — resolved (checked).** `rg 'KD-'` finds nothing in the four scripts.
  Their comments cite D-88, D-89, D-90, D-91 and D-94.
- **N-1 — resolved (probed).** These labels give `no-classification`, the
  line `unrecognised classification: <label>`, exit 0 and no log row:
  `Simple / Moderate agentic-prose (one route)`, `simple` and `**Simple**`.
  `Simple` with trailing spaces and `Defect` with CRLF read as their classes.
  A file with no `Classification:` line gives `no-classification` and no
  unrecognised-label line.
- **Gate decisions in D-90 — the code matches (checked and probed).**
  - `tdd-audit.md` sits in the Reports exclusion `case` arm, beside
    `review.md`, `review-*.md` and `final-review.md`.
  - `changed-files.sh` drops `plans/reports/triage-feedback-log.md` by exact
    name.
  - `plans/reports/explore-x.md` and `plans/jj/x.md`, a sibling job sharing
    the prefix, stay listed.
- **Leg-4 open items 1–2 (ruled unchanged).** Nothing is worse than stated.
- **Leg-4 open items 3–4 — confirmed and refined.** See Minor 3.

## Critical

None.

## Major

None.

## Minor

**1. `plugin/bin/triage-feedback.sh`, top level (the evidence and
classification sections): run from a subdirectory, the script prints wrong
evidence and exits 0.**

- Axis: robustness, error signaling. Probed.
- `changed-files.sh` changes to the repository root, because "the pathspecs
  are root-relative; from a subdirectory they would match nothing". Triage
  consumes that root-relative list but never changes directory. Its pathspecs
  and file paths resolve against the CWD:
  - the reports pathspec `:(glob)plans/<job>/reports/*`;
  - the `:(literal)<path>` list pathspecs;
  - `plans/<job>/classification.md`;
  - `reports_dir`.
- The probe was a Simple run with `def foo():` in `a.py` and one slice report:

  ```text
  from root:          Files changed: 1, Reports: 1, Behavioral code: yes, underclassified
  from subdirectory:  Files changed: 1, Reports: 0, Behavioral code: no,  no-classification, exit=0
  ```

- No row was logged, because the classification file was also missed. The
  printed evidence still contradicts the gate's list without any error.
  `finishing.md` §2 runs the script from the root, so `/build` does not hit
  this path.

**2. `plugin/skills/build/scripts/changed-files.sh`, the final
`git diff … | while read` pipeline: a late diff failure puts `ERROR:` after
`BASE:` and the paths it already printed.**

- Axis: conformance (Item 1.5 m1: "an exit 2 prints `ERROR:` first"), error
  signaling. Probed with a `git` shim that runs the real diff, then exits 128:

  ```text
  BASE: b9cfaf49…
  a.txt
  b.txt
  ERROR: git diff failed
  exit=2
  ```

- The exit code is right. Triage and `finishing.md` key on it, so no verdict
  or log row results. A consumer that reads stdout before the exit code would
  see a list that looks complete above the `ERROR:` line. D-90 says only
  "exits 2 with `ERROR:`". The order differs from the Item 1.5 wording alone.

**3. `plugin/bin/triage-feedback.sh`: four failure arms behave correctly but
no test pins them (leg-4 item 4, refined).**

- Axis: testability. Behaviour probed. Test coverage checked with `rg` over
  `tests/test_triage_feedback*.py`.
- **Behavioural-code grep, exit ≥ 2 (the `case $grep_status` `*)` arm).** A
  `grep` shim exiting 2 on `-qE` gave `ERROR: grep failed`, exit 2. The
  outline (m5) exempts this arm from a test, so it is not a gap against the
  design. The exemption's premise, "no input provokes it without fault
  injection", holds. The suite already injects faults with a `PATH` shim,
  though: `test_failing_reports_diff_is_an_error_not_none` does it for `git`.
  A test here would cost the same.
- **Classification grep, exit ≥ 2.** No shim is needed:
  `chmod 000 plans/j/classification.md` gave
  `grep: … Permission denied`, `ERROR: grep failed`, exit 2 and no row. The
  arm can be pinned exactly as `test_unreadable_log_is_an_error_and_appends_nothing`
  pins the log read, with the same root skip. KD-1 and m6 specify this clause.
  By the rubric's "test gap for a specified scenario" it could read Major. It
  is listed here because the caller designated items 3–4 known open.
- **Classification `sed` failure.** A `sed` shim exiting 4 gave
  `ERROR: sed failed`, exit 2 and no row. Only a shim reaches it.
- **Not in leg-4 item 4: `mkdir -p "$log_dir"` failure.** With `plans/`
  mode 555 and no `plans/reports/`, the script printed the evidence, then
  `ERROR: cannot write plans/reports/triage-feedback-log.md`, exit 2.
  `test_unwritable_log_is_an_error_not_a_usage_exit` covers the `header` and
  `row` cases only, and both create `plans/reports/` first. Removing the
  `mkdir` guard would exit 1, the usage code, and no test would fail.
  Reasoned: that last claim was not mutated.

**4. `agents/learnings.md` §"When calling triage-feedback.sh": a live
consumer still gives the two-argument call as the correct pattern.**

- Axis: conformance across surfaces (D-90 / KD-1: `triage-feedback.sh <job>`
  takes no base). This file is outside the code partition, but it consumes
  this script's interface.
- Its "Correct pattern" reads ``triage-feedback.sh outline-proofing baseline``.
  The file is live: `/ground`'s `grounding-criteria.md` reads it as the
  antipattern store, and `/proof` appends to it.
- Probed: `triage-feedback.sh j baseline` prints
  `Usage: triage-feedback.sh <job>` and exits 1. Its anti-pattern line,
  `plans/<job>` as `$1`, is now rejected by `changed-files.sh` with exit 2,
  not double-prefixed as it says.

**5. `plugin/skills/build/scripts/changed-files.sh`, header comment: one line
of the D-90 paragraph was not reflowed.**

- Axis: style. Checked.
- "on whitespace or newlines. `--no-renames` on the diff makes a rename a
  deletion plus an" runs to 89 columns. The lines around it wrap near 76, and
  the next line is short.
