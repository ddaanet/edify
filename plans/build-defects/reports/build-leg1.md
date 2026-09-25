# build-defects — leg 1 (Items 1.1, 1.2)

**Status: both slices executed and committed. Stopped on a routed decision.**
Slice 1.2/1's code review found one UNFIXABLE (U-DESIGN), and `tdd-slice.md`
says UNFIXABLE means STOP. The same review has fix text for
`verify-step.sh` that has not been applied. The auto-mode classifier refuses
`Edit` on that file, so the text is routed to my human partner.

Entry state: baseline `f44ddbbf89c4bea2ffa49a0fdfdd961cbe167474` in
`tmp/build-baseline`, left untouched. This job has no `recall-artifact.md`.
The recall pass selected `sandbox-effects`, `edify-commit-hook-gotchas`,
`macos-gate-target`, `no-stderr-suppression` and `cc-subagent-approval`.

Dispatch notes:
- **Unnamed dispatches.** The harness refuses `name` from a teammate ("roster
  is flat"), so every dispatch ran unnamed and was resumed by agentId.
- **Handback failures.** Every dispatch ended "without delivering a report
  through SubagentHandback". The report file was always on disk. Some replies
  went to team-lead instead of this leg.

## Slice 1.1/1 — `test_simple_with_review_reports_matches`: done

**Commits**
- `2152b28b` 🐛 Item 1.1/1 — exclude review-gate reports from triage
  reports_count. This is GREEN: the test, the script, and the RED,
  test-review and GREEN reports.
- `a2b4ac2c` 📝 Item 1.1/1 — code-review fixes. The report only.
- `7cc0e5c2` 🐛 Item 1.1/1 — code-review fixes applied. My human partner
  applied the review's three minor fixes after the classifier refused them:
  - the newline-safe count, `-exec printf x \; | wc -c`;
  - the comment corrected, since `review_artifact` does not report
    `final-review.md`;
  - `\s` → `[[:space:]]` at line 51.

**RED evidence.** `assert "- Reports: 0" in lines` failed against the
unchanged script, which printed `- Reports: 3` and `underclassified`.

**Test review.** All FIXED:
- Added `review.md` to the fixture, which catches a partial GREEN.
- Added a positive control: `item-1-1-s1-code-review.md` must count as 1.
  This catches `*review*` or a zeroed count.
- Asserted `Behavioral code: no`.
- The reviewer probed 7 candidate GREENs against copies. Only the intended
  one passes.

**GREEN, blocked once.** `docformatter -c` flagged the test docstring's
summary line at 83 columns, and wrapping it fails ruff D205. The resumed
test reviewer shortened the summary, which is recorded in that report's
Addendum. GREEN then committed.

**Code review.** No critical or major findings, three minor fixes (now
`7cc0e5c2`). Its mutated-SUT run did not happen, because the classifier
refused the in-place mutation. The test review had already covered the
partial-GREEN mutant on a copy. One observation, not pinned by a test: on the
Complex branch, a run whose only reports are review-gate ones now reads
`overclassified`. That is consistent with KD-3.

**Post-item verification.** After `2152b28b` and after `a2b4ac2c`:
`CLEAN: tree clean, just precommit passed`.

**Refactor and list revision.** No refactor was flagged. List revision:
none. There is no runbook.

## Slice 1.2/1 — `test_conventional_dirt_is_clean_and_other_dirt_is_not`: done, review open

**Commits**
- `31fe4a16` 🐛 Item 1.2/1 — exempt conventional dirt in verify-step.sh.
  This is GREEN: `verify-step.sh`, `justfile`, the test, and the three
  reports.
- `c2cec494` 📝 Item 1.2/1 — code-review fixes. The report only.

**RED evidence.** `assert result.returncode == 0` failed. The script printed
`DIRTY: uncommitted changes` / `M  .claude/handoff-task.md` / `?? inbox/`.

**Test review.** All FIXED. It probed 9 candidate GREENs; as the RED left the
test, 6 wrong ones passed, and after the fixes all 8 wrong ones fail and only
the intended one passes. The fixes:
- the handoff file set to `MM`, with a fixture guard asserting the exact
  porcelain;
- `.claude/notes.md` and `.claude/handoff-notes.txt` decoys, with an exact
  DIRTY listing;
- a third phase with an untracked `inbox/notes.txt`;
- the stub `just` records its args, and the test asserts `precommit\n`.

Left open: whether nested `inbox/sub/x.md` is exempt. The implementation
reads `*` as not crossing `/`, and a nested file is DIRTY.

**GREEN, blocked once.**
1. The classifier refused the `Edit` of `verify-step.sh` ("no verdict").
2. My human partner applied the intended edit and the `justfile` line.
3. The resumed GREEN confirmed the test passes, then committed.

**Orchestrator addition beyond the outline: `justfile`.** The `run-pytest`
test sentinel now hashes `plugin/skills/build/scripts/`. Without that, an
edit to `verify-step.sh` alone returns a cached green (memory
`gate-cache-must-cover-every-check`). The code review found this line
correct.

**Dogfood.** On the real repo after `31fe4a16`, `verify-step.sh` printed
`CLEAN` with an untracked `inbox/brief-…md` present. For that run this
report was parked in gitignored `tmp/`, because it is untracked and would
otherwise read as dirt.

**Code review** (`item-1-2-s1-code-review.md`). No fixes were applied: its
one `Edit` was refused. The findings:
- **UNFIXABLE (U-DESIGN): KD-7's "exempt dirt never enters a commit" fails
  for *staged* exempt dirt.**
  - Every committing dispatch commits with a bare `git commit` after staging
    by name. That records the whole index, so a staged
    `.claude/handoff-task.md` (or `M  memory`, or `A  inbox/x.md`) rides the
    next dispatch's commit. The reviewer reproduced this.
  - Option (a): committing dispatches use `git commit -- <paths>`. This
    touches `dispatch-composition.md`, `test-driver.md` and `refactor.md`,
    and keeps KD-7.
  - Option (b): exempt only the unstaged and untracked states. This
    contradicts KD-7's "any porcelain state" and the slice test's `MM`
    fixture, and `/build` would stop after a `/precompact` that stages the
    handoff.
  - The reviewer recommends settling this before Item 2.1 writes the §2
    DIRTY bullet.
- **Major 1: a rename out of an exempt path passes.**
  `R  inbox/a.md -> notes.md` reads CLEAN. Fix F-1 rejects `R`/`C` lines.
- **Major 2: a `git status` failure exits 128, outside the 0/1/2 contract.**
  F-1 maps it to exit 2 with an `ERROR:` line.
- **Minor 1: quoted exempt paths read as DIRTY.** These are paths with a
  space or a non-ASCII byte. F-1 allows the quotes.
- **Minor 2 (pre-existing): a missing `just` reads as a PRECOMMIT failure,
  exit 1.** Optional F-2 maps it to exit 2.
- **Fix text.** F-1 and F-2 are written out exactly as old → new in the
  review's §Fixes Routed. The reviewer checked F-1 on a copy: the slice test
  stays green, shellcheck is clean, and every probe row gets the intended
  verdict.
- **Mutated-SUT runs.** These ran on a copy with `SCRIPT` rebound, not in
  place, because a refused restore would have stranded a mutated SUT. Every
  forbidden mutant went red.
- **Recommendation.** After F-1, add a slice pinning three cases: a rename
  out of `inbox/` is DIRTY, a quoted inbox brief is CLEAN, and a non-repo
  CWD exits 2.

**Post-item verification.** After `31fe4a16`:
`CLEAN: tree clean, just precommit passed`. After `c2cec494`: see below.

**Refactor and list revision.** No refactor was flagged. List revision:
none.

## Deferred and routed

- **Routed to my human partner:** the 1.2/1 UNFIXABLE decision (option a or
  b), and applying F-1 (and F-2 if wanted) to
  `plugin/skills/build/scripts/verify-step.sh`.
- **1.1/1 code-review DEFERRED item:** `xargs` plus `|| true` at
  `triage-feedback.sh` line 51 turns an unterminated-quote failure into
  `no-classification`. It is pre-existing and outside KD-3.
- **Pre-existing, out of scope:** `just lint` reports
  `tests/line_limits_helpers.py:32:30 RUF100` (unused `noqa: PLR0913`) under
  `run-lint-checks`' extra ignores. `just precommit` does not hit it.

## Final `verify-step.sh` output

This run was after `c2cec494` and before this report was committed, so the
report was parked in `tmp/` for it. The sandbox was disabled:

```
# version consistency
Version consistent: 0.3.0
Tests cached (inputs unchanged)
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
CLEAN: tree clean, just precommit passed
exit=0
```

## Resume block

- **Where the next leg starts.** Item 2.1, once the 1.2/1 UNFIXABLE is
  decided. If the decision is option (a), the commit-scoping change lands in
  `dispatch-composition.md` and the agent definitions, and Item 2.5 already
  touches `dispatch-composition.md`. If it is option (b), `verify-step.sh`
  and `tests/test_verify_step.py` change as a new slice. Either way,
  Item 2.1's §2 DIRTY bullet must not repeat the "never enters a commit"
  premise until the decision is made.
- **If F-1 is applied.** Add the pinning slice the reviewer recommends:
  RED, test review, GREEN and code review, as slice 1.2/2.
- **Tree state at stop.** Clean except for the untracked
  `inbox/brief-corrector-reads-surfaces-against-each-other.md`. That file is
  not this leg's, is KD-7-exempt, and must never be staged.
- **Baseline.** `tmp/build-baseline` holds `f44ddbbf…`, unchanged. §5 Finish
  uses it.
