# Classification — review-fixes-3

Job-level line first, because `triage-feedback.sh` reads the first
`Classification:` it finds and takes it as a class only when it is one bare
label.

- **Classification:** Moderate

**Requirements source:** `plans/review-fixes-2/reports/deliverable-review.md`
(round 3), its three sub-reports, and my human partner's rulings in the
dispatch brief: m15 in scope; m3 resolved by a bound stated in D-90, no code
change; test D's output-side `printf '%b'` gap and final-review fixes landing
after triage ruled unchanged. **Completeness:** every finding names its file,
section and mechanism: Y. **Routing:** proceed to triage.

**Multi-item decomposition:** implicit bundling. The report holds 0 critical,
0 major and 18 minors. Each was checked against HEAD before classifying. Only
`5775ac00` landed after the review, and it touches none of the eighteen sites,
so every finding reproduces as written. They are classified per cluster below.

## Script behaviour: m1, m2, m18

- **Classification:** Moderate
- **Implementation certainty:** High. m1 copies the root-change idiom
  `changed-files.sh` already uses. m2 buffers the list before printing.
- **Requirement stability:** High
- **Behavioral code check:** Yes. m1 adds a directory change and a failure
  arm to `plugin/bin/triage-feedback.sh`. m2 changes when
  `changed-files.sh` prints its `BASE:` line. m18 is a comment reflow.
- **Work type:** Production
- **Artifact destination:** production (`plugin/bin/`,
  `plugin/skills/build/scripts/`, `tests/`)
- **Evidence:** `triage-feedback.sh` has no `cd`, and its pathspecs,
  `classification.md` and `reports_dir` are all CWD-relative.
  `changed-files.sh` prints `BASE:` at line 119 and streams paths from the
  `git diff | while read` loop at line 123, ahead of the error arm.

## Test pins: m4, m5, m6

- **Classification:** Moderate
- **Implementation certainty:** High. Each arm exists and behaves as the
  reviewers probed, so each red is a mutation red.
- **Requirement stability:** High
- **Behavioral code check:** Yes. These add test functions. The script does
  not change.
- **Work type:** Production
- **Artifact destination:** production (`tests/`)
- **Evidence:** `test_no_base_is_an_error_with_no_log_row` drives only the
  exit-1 `NO-BASE:` arm. No triage test passes zero or two arguments. No test
  reaches `:129`, `:152`, `:158` or the `mkdir -p` guard.

## Test hygiene: m7, m8, m9, m10

- **Classification:** Simple
- **Implementation certainty:** High
- **Requirement stability:** High
- **Behavioral code check:** No. Docstrings, citations, and tests moved
  between modules unchanged.
- **Work type:** Production
- **Artifact destination:** production (`tests/`)
- **Evidence:** `tests/test_changed_files.py` is at 391 lines and
  `tests/test_triage_feedback.py` at 366. The new tests of m1, m2, m4–m6 need
  room in both, so the splits come first. Recall entry `line-caps` applies.

## Cross-surface prose: m11, m12, m13, m14, m15, C-1, C-2

C-1 (a fresh remediation dispatch's name) and C-2 (`plugin/README.md` naming
`plugin-dev` and `craft` as optional) are leg-4 candidates that my human
partner ruled into scope at the outline gate.

- **Classification:** Moderate
- **Implementation certainty:** High. m12's name is stated as KD-1 in the
  outline, and m15's job-level rule as KD-3. The KD-3 ordering is ungrounded,
  with no calibration data, and was accepted as stated.
- **Requirement stability:** High
- **Behavioral code check:** Yes for m14, by ruling. A new test runs the
  prose's `git log` commands on a signed history and reds on today's prose.
  No for the rest, which are prose instructions.
- **Work type:** Production
- **Artifact destination:** agentic-prose
- **Evidence:** every site was read at HEAD. `build/SKILL.md` is at 199 lines
  of its 200 cap and no item touches it. No file this job touches is on
  `scripts/check_line_limits.allow`.

## Design record: m3, m16, m17, and the D-88, D-89 and D-93 amendments

- **Classification:** Moderate
- **Implementation certainty:** High
- **Requirement stability:** High
- **Behavioral code check:** No
- **Work type:** Production
- **Artifact destination:** investigation (`docs/references/`,
  `docs/decisions.md`)
- **Evidence:** D-90's re-run sentence, the Rejected entry "Triage dropping
  its own log path from the list", and the absence of any positive decision
  for the finishing stages' landed checks, all read at HEAD.

## Not in this job

- Test D's output-side `printf '%b'` gap, and final-review fixes landing after
  triage. Both were ruled unchanged.
- The four leg-4 candidates that stay deferred (outline §Deferred
  candidates).
