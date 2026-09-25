# Item 1.1 / Slice 1 — RED

`test_simple_with_review_reports_matches` in `tests/test_triage_feedback.py`.

## Mode

No stub written. Item 1.1 is slice 1 of the item and the SUT
(`plugin/bin/triage-feedback.sh`) already exists with the pre-fix behaviour
the slice targets (KD-3: `reports_count` does not yet exclude
`review-*.md`/`final-review.md`). The RED procedure step 1 applies only when
the SUT does not exist; here it does, so the test reds against the unchanged
script with no mutation needed — the slice text itself predicts this
("the script should red on its assertion without any stub").

## Test run

```
PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_triage_feedback.py -v
```

1 failed, 0 passed.

### `test_simple_with_review_reports_matches`

Failed on its own assertion (not ImportError/AttributeError):

```
tests/test_triage_feedback.py:108: in test_simple_with_review_reports_matches
    assert "- Reports: 0" in lines, result.stdout
AssertionError: ## Evidence
  - Files changed: 1
  - Reports: 3
  - Behavioral code: no
  - Review artifact: review

  ## Verdict
  underclassified

  Triage: predicted Simple, evidence suggests underclassified (files=1, reports=3, code=no)

assert '- Reports: 0' in ['## Evidence', '- Files changed: 1', '- Reports: 3', '- Behavioral code: no', '- Review artifact: review', '', ...]
```

The script currently counts all three fixture reports (`review-skill.md`,
`review-skip.md`, `final-review.md`) toward `reports_count`, yielding
`Reports: 3` and verdict `underclassified` instead of the `Reports: 0` /
`match` the slice asserts. This is exactly the KD-3 defect the item exists to
fix, so the red is on the named assertion, for the named reason.

## Mutation proof

Not needed. The behaviour the test pins (the KD-3 exclusion) is *absent* from
the current SUT — the slice text says so explicitly ("the script currently
prints `- Reports: 3`... the test should red on its assertion without any
stub") — so ordering alone supplies the red per `genuine-red.md`'s
stub-then-assert rule; no mutation is required to manufacture an absence that
already exists. No mutation was performed and none restored.

## Fixtures tried and rejected

- **Staging the added plain-text file instead of committing it.** `git diff
  <baseline>` only shows staged/tracked changes relative to the working tree;
  an uncommitted-but-staged file would still appear in the diff, so this would
  have worked too, but committing it keeps the fixture's git history
  unambiguous (two real commits, `baseline` resolvable as the first) and
  matches the house pattern in `tests/review_range_helpers.py::_init_repo`
  (two commits, base sha is not `HEAD`). Rejected in favor of committing.
- **Passing only one or two of the three excluded report names.** Rejected
  per the slice's explicit instruction: "One fixture covers every excluded
  name: a GREEN excluding only some still fails." Using all three
  (`review-skill.md`, `review-*.md` via `review-skip.md`, and
  `final-review.md`) makes a partial GREEN fix (e.g. excluding only
  `final-review.md` literal, or only `review-*.md`) still fail this test,
  since any one of the three left uncounted keeps `reports_count` above zero
  and the verdict at `underclassified`.
- **Asserting the raw `verdict` line by fixed-offset index (`lines[7]`) instead
  of locating `## Verdict` first.** Rejected: a substring/fixed-offset
  assertion is exactly the "substring another line satisfies" and
  "satisfied by birth state" vacuous-green shapes `vacuous-green.md`
  catalogues if the `## Evidence` block ever grows or shrinks a line; anchoring
  on the literal `## Verdict` heading and reading the next line is robust to
  that and still fails for the right reason here (the line after `## Verdict`
  is `underclassified`, not `match`).
- **Asserting only `result.returncode == 0`.** Rejected per D-18
  (`docs/references/testing.md`): the script always `exit 0`, including on the
  underclassified path, so a bare exit-code check would be satisfied by the
  unfixed script and prove nothing about the KD-3 defect — the same red the
  item's own bug would produce, i.e. no red at all.
