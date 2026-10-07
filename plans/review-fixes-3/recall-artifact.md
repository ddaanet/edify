# Recall Artifact: review-fixes-3

Read each file listed below — do not rely on inline summaries.

## Entries

- memory/line-caps.md — Items 1.1 and 1.2 split `test_changed_files.py` (391
  lines) and `test_triage_feedback.py` (366) on a seam before new tests land;
  never shave docstrings
- memory/ddaanet/audit-a-contract-across-its-surfaces.md — m12, m14 and m16
  are seams between a script, the prose that calls it and the decision that
  records it
- memory/ddaanet/no-stderr-suppression.md — m2 and m5 are diagnostics
  misordered or lost on stdout
- memory/macos-gate-target.md — every script edit stays portable to macOS
- memory/ddaanet/cc-grep-shell-function.md — Item 2.3's `grep` shim: a hand
  probe in the Bash tool measures ugrep, not the `grep` the script resolves
- memory/edify-docformatter-d205.md — Items 1.1 and 1.2 rewrite module
  docstrings
- memory/ddaanet/reflow-joins-field-lines.md — a field list in prose
  (`Requirements:`, `Files:`) stays a nested list, or the formatter re-fills it
- memory/feedback-build-delegate-legs.md — for the orchestrator, when `/build`
  runs in delegated legs

## Skills to load before executing

- shell-scripting:shell-gotchas — Items 2.1 and 2.2 (`changed-files.sh`,
  `triage-feedback.sh`) and Item 2.3's shims
- craft:test-discipline — the tdd items' reds, including Item 2.3's mutation
  reds
- craft:design-doc-writing — Item 4.1's decision amendments
- craft:directive-writing — Items 3.2 and 3.5, agent-facing instruction text
