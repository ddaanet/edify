# Item 1.6 — test hygiene

## Edits

- tests/test_verify_step.py: module docstring says the exemption tests were
  split out to tests/test_verify_step_exemption.py to keep each module under
  its line cap (m20).
- tests/test_verify_step_exemption.py: module docstring states D-91's
  exemption (`memory`, `.claude/handoff-*.md`, `inbox/*.md`, each `*` one path
  component, any porcelain state but a rename or copy, which fails closed as
  dirt), checked against exempt-paths.sh and verify-step.sh (`^[^RC][^RC]`);
  and says it is split from test_verify_step.py for the line cap (m20, m21).
- tests/test_changed_files.py: `test_no_item_report_exits_1` split (m22).
- tests/test_line_limits_wc_padding.py: docstring no longer cites
  `triage-feedback.sh:14`, `:21`.

## Split

- `test_git_failure_is_error_not_no_base` (new, first): the unborn-repo
  assertions (exit 2, `ERROR: git log failed` line, no `NO-BASE:`) and the
  root-commit-report assertions (exit 2, stdout starts `ERROR:`). Docstring
  keeps the reason: exit 1 is NO-BASE's code, not every failure's.
- `test_no_item_report_exits_1`: keeps only the outline scenario (jj's
  committed report, j's planning reports, uncommitted j item-1-1.md ->
  exit 1, `NO-BASE:`, no `BASE:` line). Docstring trimmed of the failure-case
  paragraph that moved. No assertion changed or added.
- tests/test_changed_files.py is 318-ish lines, under the 400 cap.

## `wc` sites in plugin/bin/triage-feedback.sh as found

- :39 `printf ... | wc -l | tr -d ' '` — counts changed-file lines
  (files_changed); guarded.
- :69 `done | wc -c | tr -d ' '` — counts committed reports (one `x` each);
  guarded.
- :198 `$(find ... -name 'review-*.md' | wc -l) -eq 1` — counts review-*.md
  files; unguarded but only a numeric `-eq` test, so padding is harmless.
Docstring now describes these by what they count.

## Verification

`just precommit` foreground: ruff, version, tests (403/404 passed, 1 xfail),
line limits, design links; "Precommit OK". Line-limits lines printed for
plugin/agents/{corrector,outline-corrector,design-corrector}.md are
pre-existing and not a failure.
