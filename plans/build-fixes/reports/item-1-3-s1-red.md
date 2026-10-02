# Item 1.3 / slice 1 — RED report

## Scope

`tests/test_triage_feedback.py` carrying
`test_files_changed_counts_committed_changes_only`. No edit to
`plugin/bin/triage-feedback.sh`: this item is a later slice on a pre-existing
SUT, so no stub is written and the SUT is untouched except for the mutation
proof (not needed here — see below).

## Test run

```
PATH=/Users/david/code/edify/.venv/bin:$PATH python -m pytest tests/test_triage_feedback.py -v
```

### `test_files_changed_counts_committed_changes_only` — FAILED

Failure line:

```
tests/test_triage_feedback.py:159: in test_files_changed_counts_committed_changes_only
    assert "- Files changed: 1" in lines, "\n".join(lines)
E   AssertionError: ## Evidence
E     - Files changed: 3
E     - Reports: 0
E     - Behavioral code: no
E     - Review artifact: none
E
E     ## Verdict
E     no-classification
E
E     WARNING: No corrector report — review gate may have been bypassed
E   assert '- Files changed: 1' in ['## Evidence', '- Files changed: 3', '- Reports: 0', '- Behavioral code: no', '- Review artifact: none', '', ...]
```

`result.returncode == 0` passed inside `_triage_lines` first (the script
always exits 0 on this path), so the red lands on the content assertion — a
wrong value (`3` against the current single-ref `git diff
"$baseline_commit"`, which diffs baseline against the working tree and so
counts the committed change to `a.txt` plus the uncommitted unstaged change to
`b.txt` plus the uncommitted staged change to `c.txt`) versus the expected `1`
(only the committed change, once the diff takes `"$baseline_commit" HEAD`).
This is a genuine red produced by the existing bug the item targets, not by a
missing symbol or a setup crash.

### `test_simple_with_review_reports_matches` — PASSED (pre-existing, unaffected)

## Fixtures tried and rejected

- **Leaving `b.txt` untracked instead of tracked-at-baseline.** Rejected per
  the dispatch's own warning: `git diff` does not report an untracked path at
  all (it shows up only as `??` in `git status`), so an untracked `b.txt`
  would make `files_changed` read `1` today — matching the test's expected
  value for the wrong reason, and the red would vanish without proving
  anything about committed-vs-working-tree scope. `b.txt` is added and
  committed alongside `a.txt` and `c.txt` in the setup commit that becomes
  the baseline, so its later edit is a tracked working-tree diff.
- **Two files instead of three (`a.txt` committed-changed, `b.txt`
  uncommitted-unstaged only, no staged file).** This also reds today (count
  `2` vs. expected `1`), but it leaves the staged-uncommitted form
  unexercised. Added `c.txt`, modified and `git add`-ed but not committed,
  to also pull in the staged case: `git diff "$baseline_commit"` (no second
  ref) reads from the working tree regardless of index state, so a staged
  file counts too under the current bug, but a staged-only file is still
  absent from `git diff "$baseline_commit" HEAD` once fixed (staging alone
  never lands in `HEAD`). This keeps the final assertion unchanged at
  `- Files changed: 1` while discriminating both uncommitted forms, so a
  future fix that handles only the unstaged case would still fail this test.
- **Using `_init_repo`'s baseline directly as the test's baseline.**
  Rejected: `_init_repo` only seeds `README.md`, and `a.txt`/`b.txt`/`c.txt`
  must already be tracked *before* the baseline so their later edits are
  diffs rather than additions. The test instead commits the three tracked
  files in a second commit and uses that commit's sha as the baseline passed
  to the script, calling `_init_repo` only for its config-insulated `git
  init` setup.
- **Asserting the full `## Evidence` block via `lines.index` arithmetic**
  (mirroring the Reports-count assertions in the existing test). Rejected as
  unnecessary for this slice: the item's stated assertion is the one
  `- Files changed: 1` line, and `reports_count`/`behavioral_code` are
  untouched by this item (slice 2 covers `Behavioral code`), so asserting
  them here would couple this test to behaviour it does not claim to pin.

## Mutation proof

None. The test fails on its own assertion against the unchanged SUT (an
`AssertionError` on a wrong value, `3` vs. `1`), which is itself the evidence
the behaviour targeted by this item (diffing against the working tree instead
of `HEAD`) is present in the SUT today — the slice text states the defect
(KD-6: "both diffs take `"$baseline_commit" HEAD`") and the code shows it
(`git diff --name-only "$baseline_commit"` with no second ref). Step 4 of the
RED protocol's mutation requirement applies only to a test that has passed
against unchanged code; this one did not pass, so no mutation was performed
and the SUT was not touched.

## Scope confirmation

Only the one named test was added, to the existing `tests/test_triage_feedback.py`.
`plugin/bin/triage-feedback.sh` is untouched. Slice 2
(`test_uncommitted_definition_is_not_behavioral`) and every other item are
untouched.

## Lint

- `ruff check tests/test_triage_feedback.py` — all checks passed.
- `docformatter -c tests/test_triage_feedback.py` — no changes needed.

## Files

- `tests/test_triage_feedback.py` (one test added)
