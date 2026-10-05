# Classification — review-fixes-2

Job-level line first, because `triage-feedback.sh` reads the first
`Classification:` it finds.

- **Classification:** Moderate

**Requirements source:** `plans/build-fixes/reports/deliverable-review.md`
(round 2), its three sub-reports, and my human partner's rulings in the
dispatch brief. **Completeness:** every finding names its file, section and
mechanism, and every finding with an open fork (C1/M1's evidence model, M2,
M4, m7, m9, m10, m13) has a ruling: Y. **Routing:** proceed to triage.

**Multi-item decomposition:** implicit bundling. The report holds 1 critical,
6 majors and 23 minors. M3 is out, owned by defect 21. The other 29 were each
verified against HEAD (`79d0b687`) before classifying, and every one
reproduces. They are classified per cluster below. Each finding had its own
behavioural-code check. Within a cluster the findings came out on the same
axes, so one block covers them.

## Triage evidence: C1, M1, m4, m5, m6, N-1, and m7's log half

N-1 is not the review's finding. It surfaced while verifying C1, and my human
partner put it in scope at the outline gate: an unrecognised
`Classification:` value falls through to `match`. It is the same parse line
as m6.

- **Classification:** Moderate
- **Implementation certainty:** High. `changed-files.sh` already produces the
  set the review gate reviews, and triage calls it rather than restating it
  (D-90's one-script rule).
- **Requirement stability:** High. My human partner ruled the evidence model
  and the D-90 amendment.
- **Behavioral code check:** Yes. It changes the evidence computation, the
  report count, the classification parse and the log append in
  `plugin/bin/triage-feedback.sh`.
- **Work type:** Production
- **Artifact destination:** production (`plugin/bin/`, `tests/`), plus
  investigation (D-90 in `docs/references/build-run-state.md`,
  `docs/decisions.md`)
- **Evidence:** probe-free reading at HEAD. `reports_count` counts
  `item-*.md`, so a Simple run reads `underclassified`. `files_changed` and
  `committed_diff` take a raw `<base> HEAD` diff. Lines 15 and 46 have no
  `--`, line 48 has a here-string inside `if`, and line 56 has
  `xargs || true`. Recall entries: `audit-a-contract-across-its-surfaces`
  (triage, the review gate and D-90 are three surfaces of one contract),
  `no-stderr-suppression`, `macos-gate-target`.

## Test pins: M6, m23, and test hygiene m20–m22

- **Classification:** Moderate
- **Implementation certainty:** High. The behaviour exists, so each red is a
  mutation red, and the review names the mutants.
- **Requirement stability:** High
- **Behavioral code check:** Yes for M6 and m23, which add test functions.
  No for m20–m22, which are docstrings and a test split.
- **Work type:** Production
- **Artifact destination:** production (`tests/`)
- **Evidence:** no fixture path in `test_changed_files*.py` holds a space or a
  non-ASCII byte. No test greps `cannot load`. `test_no_item_report_exits_1`
  runs both exit-2 repos first.

## Script hygiene: m1, m8

- **Classification:** Moderate
- **Implementation certainty:** High
- **Requirement stability:** High
- **Behavioral code check:** Yes for m1. Dropping `exec 2>&1` changes which
  stream git's diagnostics reach. No for m8, which is comments only.
- **Work type:** Production
- **Artifact destination:** production (`plugin/skills/build/scripts/`)
- **Evidence:** `changed-files.sh:2` `exec 2>&1`. `KD-N` citations sit in all
  four scripts' comments, and the durable IDs are D-88 to D-94.

## `/build` run-state prose: M2, M4, M5, m7's gate half, m9–m18

- **Classification:** Moderate
- **Implementation certainty:** High. M2, M4, m7, m9, m10 and m13 are ruled.
  The remaining decisions are stated in the outline.
- **Requirement stability:** High
- **Behavioral code check:** No. The changes are prose instructions only.
- **Work type:** Production
- **Artifact destination:** agentic-prose
- **Evidence:** every site was quoted at HEAD in the outline's findings
  table. Recall entry `line-caps` applies: `build/SKILL.md` is at 196 lines
  against its 200 cap.

## Design record: m2, m3, m19, the D-90/D-91/D-92/D-93 amendments, changelog

- **Classification:** Moderate
- **Implementation certainty:** High
- **Requirement stability:** High
- **Behavioral code check:** No
- **Work type:** Production
- **Artifact destination:** investigation (`docs/references/`,
  `docs/decisions.md`, `docs/design.md`, `docs/changelog/`,
  `plans/build-fixes/outline.md`)
- **Evidence:** D-90 says triage's "two diffs take the same `<base> HEAD`
  form", which is what M1 measures as wrong. D-92 has `<paths>` where
  `escalation.md` has `<tracked or indexed paths>`.

## Not in this job

M3. `corrector.md` §0 refuses the `review-design` row, and defect 21 owns
that file.
