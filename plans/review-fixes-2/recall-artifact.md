# Recall Artifact: review-fixes-2

Read each file listed below — do not rely on inline summaries.

## Entries

- memory/line-caps.md — `build/SKILL.md` sits at 196 of its 200 lines, and
  `tests/test_triage_feedback.py` grows past 400 with the Item 1.1/1.2 slices
- memory/ddaanet/audit-a-contract-across-its-surfaces.md — triage, the review
  gate and D-90 are three surfaces of one changed-files contract
- memory/ddaanet/no-stderr-suppression.md — m1, m5 and m6 are masked or
  misrouted diagnostics
- memory/macos-gate-target.md — every script edit stays portable to macOS
- memory/ddaanet/sandbox-effects.md — the mask branch m9 names as dependent on
  the `sandbox-lies` hook

## Skills to load before executing

- shell-scripting:shell-gotchas — any edit to `triage-feedback.sh`,
  `changed-files.sh`, `verify-step.sh` or `exempt-paths.sh`
- craft:test-discipline — the tdd items' reds, including the mutation reds of
  Items 1.3 and 1.4
- craft:design-doc-writing — Item 2.12's decision amendments and the changelog
  entry
