# Item 1.3 / slice 2 — RED report

## Scope

`tests/test_triage_feedback.py` carrying
`test_uncommitted_definition_is_not_behavioral`. No edit to
`plugin/bin/triage-feedback.sh`: this item is a later slice on a pre-existing
SUT, so no stub is written and the SUT is untouched except for the mutation
proof (not needed here — see below).

## Test run

```
PATH=/Users/david/code/edify/.venv/bin:$PATH python -m pytest tests/test_triage_feedback.py -v
```

### `test_uncommitted_definition_is_not_behavioral` — FAILED

Failure line:

```
tests/test_triage_feedback.py:204: in test_uncommitted_definition_is_not_behavioral
    assert "- Behavioral code: no" in lines, "\n".join(lines)
E   AssertionError: ## Evidence
E     - Files changed: 2
E     - Reports: 0
E     - Behavioral code: yes
E     - Review artifact: none
E
E     ## Verdict
E     no-classification
E
E     WARNING: No corrector report — review gate may have been bypassed
E   assert '- Behavioral code: no' in ['## Evidence', '- Files changed: 2', '- Reports: 0', '- Behavioral code: yes', '- Review artifact: none', '', ...]
```

The positive pairing (`- Behavioral code: yes` after a committed `def` in a
separate throwaway repo) ran first and held, with no `AssertionError`:
`result.returncode == 0` inside `_triage_lines` also held there, so the only
thing exercised is the content assertion. The negative then reds on a wrong
value (`yes` against the current `git diff "$baseline_commit"` with no second
ref, which diffs baseline against the working tree and so picks up both the
unstaged `def foo():` edit to `module.py` and the staged-but-uncommitted
`def bar():` edit to `other.py`) versus the expected `no` (neither def is
committed, so once the diff takes `"$baseline_commit" HEAD` only the plain-text
commit remains in range). This is a genuine red produced by the existing bug
the item targets, not by a missing symbol or a setup crash.

### `test_simple_with_review_reports_matches` — PASSED (pre-existing, unaffected)

### `test_files_changed_counts_committed_changes_only` — PASSED (pre-existing, unaffected)

## Fixtures tried and rejected

- **No positive pairing, negative fixture alone.** Rejected per the dispatch's
  own instruction: a test asserting only `Behavioral code: no` cannot
  discriminate an implementation that always prints `no`, or whose regex
  never matches anything, from one that correctly scopes the diff to
  `HEAD`. The positive check — a committed `def` after the baseline reading
  `yes` — runs first in a separate throwaway repo and would fail against
  either degenerate implementation, so its presence is what makes the
  negative's `no` meaningful.
- **Positive and negative sharing one repo and one baseline.** Rejected: if
  the `def` that proves the positive case were committed in the same repo
  used for the negative assertion, that commit would stay in the committed
  range (`baseline..HEAD`) for every later check in the test, so the
  negative's `Behavioral code: no` could never be reached even after the
  fix — the fixture would assert something impossible rather than pinning
  the uncommitted-only behaviour. Two throwaway repos under `tmp_path` keep
  the committed history each assertion depends on disjoint.
- **Only an unstaged `def` edit, no staged one.** This reds today for the
  same reason (an unstaged edit still shows in `git diff "$baseline_commit"`
  with no second ref), but it leaves the staged-uncommitted form unexercised.
  Added a second tracked `.py` file (`other.py`) that is modified with a
  `def` line and `git add`-ed but not committed, so the fixture also covers a
  future fix that only special-cases the unstaged case (e.g. reading the
  index instead of comparing against `HEAD`) and would still leave a staged
  def counted.
- **A single tracked `.py` file carrying both the unstaged and staged
  changes.** Rejected: a file cannot be simultaneously staged and
  further modified in a way that isolates which state the diff command
  picked up without added bookkeeping; two files (`module.py` for the
  unstaged edit, `other.py` for the staged one) keep each case
  independently attributable in the failure output.
- **Asserting the full `## Evidence` block via `lines.index` arithmetic**
  (mirroring the Reports-count assertions in the existing
  `test_simple_with_review_reports_matches`). Rejected as unnecessary for
  this slice: the item's stated assertion is the one `- Behavioral code: no`
  line (and, for the pairing, `- Behavioral code: yes`); `files_changed` and
  `reports_count` are untouched by this item's negative claim, so asserting
  them here would couple the test to behaviour it does not claim to pin.

## Mutation proof

None. The test fails on its own assertion against the unchanged SUT (an
`AssertionError` on a wrong value, `yes` vs. `no`), which is itself the
evidence the behaviour targeted by this item (diffing against the working
tree instead of `HEAD` for the behavioral-code check) is present in the SUT
today — the slice text states the defect (KD-6: "both diffs take
`"$baseline_commit" HEAD`") and the code shows it (`git diff
"$baseline_commit"` with no second ref on the line feeding `definition_re`
and `shell_fn_re`). Step 4 of the RED protocol's mutation requirement applies
only to a test that has passed against unchanged code; this one did not
pass, so no mutation was performed and the SUT was not touched.

## Scope confirmation

Only the one named test was added, to the existing
`tests/test_triage_feedback.py`. `plugin/bin/triage-feedback.sh` is
untouched. Every other item and slice 1 (already landed) are untouched.

## Lint

- `ruff check tests/test_triage_feedback.py` — all checks passed.
- `docformatter -c tests/test_triage_feedback.py` — no changes needed.

## Files

- `tests/test_triage_feedback.py` (one test added)
