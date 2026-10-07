# Item 4.1 — design record for the round-3 minors

Requirements: m3, m12, m14, m16, m17. Type: general. Loaded
`craft:design-doc-writing` (body plus `maintaining-entries.md` and
`writing-style.md`): mechanism text updated in place, present tense, no
supersession narrative, rejected alternatives kept as decisions.

Files: `docs/references/build-run-state.md`, `docs/decisions.md`. No changelog
entry. `just format` reflowed the edited paragraphs of `build-run-state.md` at
80 columns; `decisions.md` needed no reflow. `build-run-state.md` is 272 lines,
under its 400 cap, and is not on the allowlist.

## Contract

- **D-88 (m14).** One sentence after the `--no-renames` sentence: every
  `git log` whose output `/build` reads passes `--no-show-signature`, because a
  user's `log.showSignature` prints verification lines ahead of the shas, and
  `tests/test_build_prose_git_log.py`
  (`test_read_git_log_commands_print_hashes_only_on_signed_history`) runs each
  such command from the prose against a signed history. The sentence does not
  spell the hash-format flag, so the test's per-file flag count is unchanged:
  `command grep -c -- '--format=%H'` on the node still gives 2, the two query
  blocks.
- **D-89 (m16, KD-2).** Conclusion, in both files: "A phase boundary or a
  finishing stage has landed when the run holds a commit touching its report."
  The body ends with the finishing stages, each keyed on its report path in
  the range after the run's last item-report commit, as `finishing.md` §1 and
  §3 query it: the review gate on a `review-*.md` report, `review-skip.md`
  included; the final review on `final-review.md`; the TDD audit on
  `tdd-audit.md`. A re-invoked or resumed run re-runs none that has landed.
  Code evidence: `finishing.md` §1 runs `git log -1 … <L>..HEAD --
  ':(glob)plans/<job>/reports/review-*.md'` with `<L>` the last item-report
  commit and says `review-skip.md` counts. §3.1 runs the same `<L>..HEAD` query
  over `final-review.md`, and §3.2 runs "the same query" over `tdd-audit.md`.
  No rationale for the `<L>` start was added, because neither `finishing.md`
  nor the outline states one.
- **D-90 (m3).** After the re-run sentence, the bound: reports committed under
  `plans/<job>/reports/` after Finish still count, such as the
  `deliverable-review*.md` that `/deliverable-review plans/<job>` writes. A
  re-run after one can therefore log a second row, and for a Simple job its
  verdict can flip from `match` to `underclassified`. The final-review fixes
  clause was not added. Code evidence: `triage-feedback.sh` counts
  `--diff-filter=A` paths over `<base> HEAD` directly under `reports/`, and
  excludes only `item-<N>-<M>.md` and
  `review.md | review-*.md | final-review.md | tdd-audit.md`.
  `deliverable-review*.md` matches none of these. Under `Simple`, a
  `reports_count -gt 0` gives `underclassified`. The re-run sentence now uses
  the conditional ("would differ", "would not fire", "would be logged"), and
  "the log's skip of a row equal past its date" points back to the new row
  sentence as "the skip".
- **D-90 (m16, KD-2's row sentence).** A sentence of its own, before "Both
  drops": "Triage commits no report, so it has no landed check, and its log
  appends at most one row per evidence: a row equal to the new one past the
  date column skips the append." Code evidence: the log loop strips the date
  column (`log_rest=${log_row#"| "}`, then `${log_rest#* | }`) and compares
  the rest whole with `new_undated`. On a match it sets `row_seen=yes` and
  skips the `printf … >>` append. Triage's only commit-side trace is the log
  line, which the closing commit carries (`finishing.md` §3.3).
- **D-90 (m2).** It now reads "A usage error or a git failure exits 2 with
  `ERROR:` alone on stdout, with no `BASE:` line and no path: the list is built
  in full before `BASE:` prints, so a diff failing part-way leaves nothing
  ahead of it (`test_late_diff_failure_prints_error_alone`)." The unborn-`HEAD`
  clause follows as its own sentence. Code evidence: in `changed-files.sh` the
  list is captured whole in `paths=$(git diff … | while … done && printf x) ||
  { echo "ERROR: git diff failed"; exit 2; }`, and only then
  `printf 'BASE: %s\n'` and the paths are printed. Every other exit-2 arm
  (usage, job name, exempt-paths load, rev-parse, cd, log, parent, phase log)
  echoes its `ERROR:` line before anything else reaches stdout. "On stdout"
  scopes the claim, since git's own stderr passes through.
- **D-93 (m12, KD-1).** One sentence after "planning artifacts route by
  artifact (D-26)": a planning artifact on the gate's list is dispatched as
  `review-plan-<source job>-<stem>`, a name and not a group, `<source job>`
  being the `plans/` directory it sits in and `<stem>` `design`, `outline` or
  `runbook`; the name matches `review-*.md`, so the gate's landed check
  (D-89), triage's report exclusion and its `Review artifact` probe all read
  its report as a review report. The wording follows
  `dispatch-composition.md` §Naming and resumption ("a name and not a group",
  "the `plans/` directory the artifact sits in") and `finishing.md` §1. Code
  evidence for the three readers: `finishing.md` §1's landed check pathspec
  `review-*.md`, triage's `case` exclusion `review-*.md`, and triage's
  `compgen -G "$reports_dir/review-*.md"` probe.
- **Rejected (m17).** The entry is now "**Triage filtering its own log path
  out of the list on its side** — the list already drops it, and a filter in
  triage is a second copy of the list's filters, as above (D-90)."
- **`decisions.md`.** D-89's index line takes the new conclusion. In the
  build-run-state *Rejected:* line, "triage dropping its own log path from the
  list" becomes "triage filtering its own log path out of the list on its
  side". The D-88, D-90 and D-93 conclusion lines are unchanged, in both files.
- **No changelog entry.** `docs/changelog*` is untouched.

## Scope checks

- Query blocks: `git diff --word-diff` shows no change inside either fenced
  block of D-88 or D-89. Only prose changed.
- Untouched: `docs/references/pipeline-contracts.md`, `docs/design.md`,
  `docs/changelog*`, every `plugin/` file, tests and scripts, and the two
  untracked `inbox/brief-*.md` files.
- The bolded D-89 lead contains no literal `*`. That is the residual bound
  `check_design_links.sh` states, so `review-*.md` is kept in the body.

## Verification

`PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit`, foreground,
full output:

```text
# version consistency
Version consistent: 0.3.0
# Test Report

**Summary:** 431/432 passed, 1 xfail
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 94 decisions indexed, defined once, conclusions match, 9 nodes present
✓ Precommit OK
```

The three `oversized-file` lines name allowlisted corrector-family agents
that this item does not touch. The gate still passes.

Passed: version consistency, test suite (431 passed, 1 xfail), line limits,
design links (94 decisions, conclusions match, 9 nodes).

`.venv/bin/pytest -p no:markdown_report tests/test_build_prose_git_log.py`:
10 passed.
