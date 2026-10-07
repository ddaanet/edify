# Item 3.1 — `agents/learnings.md` §"When calling triage-feedback.sh"

Requirement: m11. Type: general.

## What changed

`agents/learnings.md`, the section's two bullets only (lines 64–65). The
heading, the blank line above it and the absence of one below it are
unchanged. Each bullet stays one long unwrapped line, as the file's style is.
`git diff --stat` after precommit: `agents/learnings.md | 4 ++--`, 2
insertions, 2 deletions, nothing else.

- Anti-pattern: `triage-feedback.sh plans/outline-proofing`. `$1` is a job
  name, not a path. `changed-files.sh` refuses it as not a job name and exits
  2. Triage prints that line, then `ERROR: changed-files.sh exited 2`, and
  exits 2 itself, with no evidence and no log row. It never reaches the old
  double prefix. A two-argument call (the retired base argument, the old
  section's `outline-proofing baseline`) exits 1 with
  `Usage: triage-feedback.sh <job>` on stderr.
- Correct pattern: `triage-feedback.sh outline-proofing`, the job name alone.
  The base is derived from report history: `changed-files.sh` takes the parent
  of the earliest commit adding a `plans/<job>/reports/item-*` report (D-88).

The old section's "prepends `plans/`" mechanism and its two-argument correct
pattern are gone.

## Evidence per contract claim

1. **Job name alone, base from report history.**
   `plugin/bin/triage-feedback.sh` lines 7–10 accept exactly one argument and
   pass it to `changed-files.sh` (line 49). `changed-files.sh` lines 93–108
   derive the base as the parent of the first commit adding
   `plans/$job/reports/item-*`, per its D-88 header comment.
2. **`plans/<job>` as `$1` is refused, exit 2, not a double prefix.**
   `changed-files.sh` lines 58–63: the `*/*` case pattern prints
   `ERROR: usage: changed-files.sh <job> [--phase]; not a job name: …` and
   exits 2. Triage lines 50–53 print that output, then
   `ERROR: changed-files.sh exited <status>`, and exit 2, before any evidence
   or log write. Tests:
   - `tests/test_changed_files_errors.py::test_unsafe_job_name_is_a_usage_error`
     pins the `/` arm with the job `jj/sub` (exit 2, stdout `ERROR:`), so any
     `$1` holding `/` is covered, not a literal `plans/<job>`;
   - `tests/test_triage_feedback_failures.py::test_changed_files_error_is_printed_then_exit_2`
     pins triage's side: `changed-files.sh`'s line, then its own, exit 2, no
     row.

   Live run from the repo root:

   ```text
   $ plugin/bin/triage-feedback.sh plans/review-fixes-3
   ERROR: usage: changed-files.sh <job> [--phase]; not a job name: plans/review-fixes-3
   ERROR: changed-files.sh exited 2
   exit=2
   ```

3. **Two arguments exit 1 with `Usage:`.** Triage lines 7–9: `$# -gt 1`
   prints `Usage: triage-feedback.sh <job>` to stderr and exits 1.
   `tests/test_triage_feedback_failures.py::test_usage_error_exits_1`, case
   `stale-base` (`j HEAD`), pins exit 1, that stderr, empty stdout and no
   row. Any second argument takes the same arm. Live run:

   ```text
   $ plugin/bin/triage-feedback.sh review-fixes-3 HEAD
   Usage: triage-feedback.sh <job>
   exit=1
   ```

4. **Line style kept.** Two bullets, each one physical line, no reflow. No
   formatter was run over the file, and precommit changed nothing in it.

No contract claim disagreed with the code.

## Precommit

`PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit`, foreground,
exit 0:

- version consistency: `Version consistent: 0.3.0`
- tests: `Tests cached (inputs unchanged)`
- line limits: three allowlisted `oversized-file` lines
  (`plugin/agents/corrector.md` 682, `outline-corrector.md` 450,
  `design-corrector.md` 460), not failures
- design links: `94 decisions indexed, defined once, conclusions match, 9
  nodes present`
- `✓ Precommit OK`
