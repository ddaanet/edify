# Outline — review-fixes-4

Fifth pass on the `/build` run-state work: the 7 minors F1–F7 of
`review-fixes-3`'s round-4 deliverable review
(`plans/review-fixes-3/reports/deliverable-review.md` §Minor Findings; its
sub-reports beside it carry the probes). Each finding's contract is that
report's text plus the edit stated here. Classification: `classification.md`.

## Provenance

- **Derived from:** `plans/review-fixes-3/reports/deliverable-review.md`
- **Base:** `8eb1c9629fea5e12361e906b1135b70fbc60b345` -- HEAD when this
  outline was written; this job is reviewed on its own, as round 4 reviewed
  `review-fixes-3` alone

## Model routing (my human partner's ruling)

`/build` orchestrator: sonnet. Executors — RED, GREEN and the prose item:
haiku. Test review, code review and the review gate's correctors: sonnet.
Follow-up `/deliverable-review`: opus, dispatched by the main session.

## Item 1.1 — tdd: pin triage's repository-root `cd` failure (F3)

Files: `tests/test_triage_feedback_failures.py`,
`plugin/bin/triage-feedback.sh`.

**Slice 1.** Test `test_root_cd_failure_is_one_error_line` in
`tests/test_triage_feedback_failures.py`:

- A `git` shim via `_write_shim` (`tests/changed_files_helpers.py`) answers
  `rev-parse --show-toplevel` with a nonexistent absolute path under
  `tmp_path` and exits 0, passing every other call to the real `git`.
- Run triage from a fixture repo with the shim directory prepended to `PATH`.
- Assert exit 2, and stdout exactly `ERROR: cannot change to <that path>`.

RED is a mutation red: the guard exists, so the test passes on HEAD. Replace
the `if ! cd "$repo_root"; then … fi` block (`triage-feedback.sh:43-46`) with
a bare `cd "$repo_root"`, show the test fails on its assertion (the round-4
probe saw exit 1, empty stdout), then restore the block.

GREEN: narrow the residual-bound comment above the guard
(`triage-feedback.sh:40-42`) to the script-directory `cd` only: it is a
builtin fed by `BASH_SOURCE`, and reaching it would need new,
bash-version-dependent fault injection. Drop the claim that no input
provokes the root `cd`.

## Item 1.2 — general: prose fixes (F1, F2, F4–F7)

Every edit is stated verbatim; apply it as written, keep the surrounding text,
hard-wrap at 80 columns.

- **F2, `plugin/skills/build/references/finishing.md:76`:** "Planning
  artifacts do not route through this gate. They route by artifact" →
  "Planning artifacts do not route through the four group rows. They route by
  artifact".
- **F2, `docs/references/build-run-state.md` D-93 (line 183-185):** "The
  `/build` review gate routes implementation files only; planning artifacts
  route by artifact (D-26)." → "The `/build` review gate's four group rows take
  implementation files only; a planning artifact on its list routes by
  artifact (D-26)."
- **F1, same D-93 paragraph,** after the sentence ending "read its report as a
  review report.", insert: "The gate's reports, `review-plan-*` ones included,
  land under the running job's `reports/` in one commit, together with any
  planning corrector's edits to the source job's plan file: a `review-plan-*`
  report committed on its own, ahead of the group reports, would read to
  D-89's landed check as the gate landed." If `docs/decisions.md`'s D-93
  conclusion line paraphrases the routing sentence just changed, update it to
  match; `just precommit`'s design-links check confirms.
- **F4, `plugin/README.md` §Optional plugins, `plugin-dev` entry:** append
  after "…already in `agents/` instead.": "The `/requirements`, `/design` and
  `/build` steps that load a `plugin-dev:*` skill for hook, agent, skill or
  plugin work go without that guidance."
- **F5, `plugin/skills/design/references/triage.md:122-125`:** "Open the file
  with one job-level `- **Classification:** <label>` line, at the start of its
  line, before any per-item block, so that no other `Classification:` line,
  bulleted or bare, can precede it." → "Write one job-level
  `- **Classification:** <label>` line, at the start of its line, before any
  per-item block, so that no other `Classification:` line, bulleted or bare,
  can precede it; a heading or prose may come before it."
- **F6, same paragraph, lines 130-132:** "`Defect` is the job-level label only
  when every item is a Defect. No calibration data backs this ordering yet;
  the triage log is where it will come from, once composite jobs have logged
  rows." → "`Defect` is the job-level label only when every item is a Defect;
  in a mixed job a Defect item does not raise the label, which is the most
  demanding non-Defect item's class. This ordering is ungrounded: no
  calibration data backs it."
- **F7, `agents/learnings.md:64`,** replace the whole Anti-pattern bullet
  with: "- Anti-pattern: Calling `triage-feedback.sh plans/outline-proofing` —
  `$1` is a job name, not a path. `changed-files.sh` refuses any `$1` holding
  `/`, so triage exits 2 with no evidence and no log row. A second argument,
  such as the retired base argument, is a usage error (exit 1)." Keep it one
  physical line, as the file's other bullets are.

## Traceability

| Finding | Item |
|---|---|
| F1 | 1.2 |
| F2 | 1.2 |
| F3 | 1.1 |
| F4 | 1.2 |
| F5 | 1.2 |
| F6 | 1.2 |
| F7 | 1.2 |

## Out of scope

Ruled out, not to reopen: the bash 3.2 `source` defect in `changed-files.sh`
when `exempt-paths.sh` is absent, and the absent bash-3.2 suite run; test D's
output-side `printf '%b'` gap; final-review fixes landing after triage. The
round-4 "observed, not raised" `triage_feedback_helpers.py` docstring note is
not a finding.
