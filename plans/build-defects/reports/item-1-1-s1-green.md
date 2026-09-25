# Item 1.1 / Slice 1 — GREEN

**Status: done.**

## Implementation

`plugin/bin/triage-feedback.sh`'s `reports_count` `find` now also excludes
`review.md`, `review-*.md`, `final-review.md` (KD-3), alongside the existing
`design-review*`/`outline-review*`/`recall-*` exclusions. The comment above
the exclusion explains why: `review_artifact` already reports review-gate
presence separately, so counting these here double-counted the same signal
and misclassified a reviewed Simple run as `underclassified`.

```diff
--- a/plugin/bin/triage-feedback.sh
+++ b/plugin/bin/triage-feedback.sh
@@ -15,10 +15,17 @@ files_changed=$(git diff --name-only "$baseline_commit" | wc -l | tr -d ' ')

 # Count report files in plans/$job_dir/reports/
 # Exclude pre-execution artifacts: design-review*, outline-review*, recall-*
+# Exclude review-gate and closing-review reports too: review.md, review-*.md,
+# final-review.md (KD-3). review_artifact below already reports their
+# presence separately, so counting them here double-counts the same signal
+# and misclassifies a reviewed Simple run as underclassified.
 reports_count=0
 reports_dir="plans/$job_dir/reports"
 if [[ -d "$reports_dir" ]]; then
-    reports_count=$(find "$reports_dir" -maxdepth 1 -type f ! -name "design-review*" ! -name "outline-review*" ! -name "recall-*" | wc -l | tr -d ' ')
+    reports_count=$(find "$reports_dir" -maxdepth 1 -type f \
+        ! -name "design-review*" ! -name "outline-review*" ! -name "recall-*" \
+        ! -name "review.md" ! -name "review-*.md" ! -name "final-review.md" \
+        | wc -l | tr -d ' ')
 fi
```

Only one test in the batch, made to pass in one pass (no iteration needed):

| Order | Test | Result |
|---|---|---|
| 1 | `test_simple_with_review_reports_matches` | PASS |

```
PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_triage_feedback.py -v
```
→ 1/1 passed.

`shellcheck plugin/bin/triage-feedback.sh` → exit 0, no findings.

## Gate run

```
PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit
```

```
# version consistency
Version consistent: 0.3.0
Test Report: 361/362 passed, 1 xfail
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
```

`run-checks`'s `ruff check`, `ruff format --check`, `docformatter -c` and
`mypy` all passed silently (the `report` helper, `plugin/portable.just:28`,
only prints a header when a check produces output — none did here). The
three `oversized-file` line-limit warnings are pre-existing files untouched
by this dispatch (`plugin/agents/*-corrector.md`), out of Item 1.1's scope —
recorded per the mode's rule that precommit warnings go into the report, not
into refactoring. `tmp/.test-sentinel` hash after this run: `1942824792
551041`.

## History note — earlier block, now resolved

The first `just precommit` run in this dispatch failed on `docformatter -c`,
which flagged `tests/test_triage_feedback.py:75`'s docstring summary line (83
columns, over `pyproject.toml`'s `wrap-summaries = 80`). Fixing it needed a
test-file edit, which GREEN mode's absolute test-file prohibition forbids, so
the slice was reported `blocked` and no commit was made at that point. The
test review then shortened the docstring summary (`Addendum — docstring fix`
in `plans/build-defects/reports/item-1-1-s1-test-review.md`), touching only
the docstring — no fixture, assertion, or code change — and reconfirmed
`docformatter -c`, `ruff check`, `ruff format --check`, `mypy` and `pytest -v`
all pass. `plugin/bin/triage-feedback.sh` was not touched between the block
and this resolution — the diff above is the same one from the original GREEN
pass.

## Also observed, not part of the gate

`just lint` (not `just precommit`) separately reports
`tests/line_limits_helpers.py:32:30: RUF100 Unused noqa directive
(non-enabled: PLR0913)`. That file is untouched by this dispatch
(`git status --porcelain tests/line_limits_helpers.py` shows nothing). The
finding only fires under `run-lint-checks`'s extra `--ignore=$ruff_ignores`
(which disables `PLR0913`, making its `# noqa: PLR0913` read as unused);
`just precommit`'s `run-checks` invokes `ruff check -q` with no such
override, so this does not affect `just precommit`'s green result. Noted for
visibility, out of Item 1.1's scope.

## Tree state at end of dispatch

- `plugin/bin/triage-feedback.sh`: modified (diff above), in scope.
- `tests/test_triage_feedback.py`: modified by the test review only (the
  docstring fix described above) — never edited by GREEN.
- `plans/build-defects/reports/item-1-1-s1-red.md`,
  `plans/build-defects/reports/item-1-1-s1-test-review.md`: uncommitted
  reports from earlier dispatches, carried into this commit.
- Untracked `.claude/launch.json`, `.claude/loop.md`, `.claude/output-styles`,
  `.claude/routines`, `.claude/workflows` are sandbox masks — left alone, not
  staged.
- No `plans/reports/triage-feedback-log.md` or other stray file was produced
  by these runs.
</content>
