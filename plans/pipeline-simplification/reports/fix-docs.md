# Fix report — docs group (deliverable-review, pipeline-simplification)

Scope: `docs/design.md`, `plugin/README.md`, `outline.md` (D5, D14),
`reports/measurements.md`, `memory/workflow-pipeline-revival.md`.

## Findings applied

- **Critical 2 (commit convention)** → `docs/design.md` §5.3 (new paragraph at
  `docs/design.md:169-181`): slice commits are `<type>: Item N.M/k — <title>`,
  type is the executor's choice, nothing keys on it because the gitmoji
  `commit-msg` hook rewrites the prefix, `Item N.M/k` is the only subject
  content `tdd-auditor` may match, a reviewed slice carries two commits with
  that marker so subject matching alone cannot pick the slice out, the auditor
  keys on the hash the GREEN report names with the session's `subagents/`
  transcripts as fallback, and git only confirms and diffs.
- **Critical 2** → `plans/pipeline-simplification/outline.md:123-133` (D5c):
  same convention, the "nothing keys on the type" reason, and the two-commit
  note.
- **Critical 2** → `plans/pipeline-simplification/outline.md:352-368` (D14):
  "exactly one green `feat:` commit" → "exactly one GREEN commit … plus the
  orchestrator's review-fix commit where the code review changed anything";
  the auditor keys on the hash the GREEN report names, and never on the type.
- **Critical 1 (commit owner for review fixes)** → `docs/design.md:163-167`
  (§5.3, adjacent to the D5/D6 gate-placement text): the orchestrator owns
  every commit a review produces, the corrector never commits, the orchestrator
  commits after the per-slice code review as it does at a phase boundary, and
  `verify-step.sh` runs after that commit.
- **Critical 1** → `plans/pipeline-simplification/outline.md:132-140` (D5d and
  the gate sentence): corrector applies fix-all and never commits; the gate now
  fires after (c), after the orchestrator's commit of (d)'s fixes, and after
  any general item.
- **Critical 3 (continuation hook)** → no change needed. `rg -ni continuation
  docs/design.md` returns no hits, so the design record makes no continuation
  claim to correct.
- **Major 5 (`escalated:` consumer)** → `docs/design.md:499-502` (D-30, where
  the refactor agent's place in the slice loop is described): on `escalated:`
  the orchestrator re-dispatches `edify:refactor` once with model opus; the
  escalation is a dispatch, not a run-summary line.
- **Major 9 (README gate condition)** → `plugin/README.md:72-75`: the gate runs
  after each committing dispatch (GREEN, code review, general items), never
  after a RED or a test review.
- **Minor (stale verified-against)** → `docs/design.md:7`: `06a431ec`
  (2026-09-01) → `f50ed025` (2026-09-02), the current HEAD.
- **Minor (one verification script)** → `docs/design.md:135-136` and
  `docs/design.md:157-161`: "one verification script" → two, and the script
  paragraph now names `plugin/bin/triage-feedback.sh` alongside
  `verify-step.sh` with its D-26 T5 role.
- **Minor (D-26 missing row)** → `docs/design.md:430`: added
  `| T6 | Requirements → Design outline | requirements.md or inline |
  outline.md | outline-corrector (opus), then /proof |`. Appended as T6 rather
  than inserted before T1, because T1, T2 and T5 are cited by ID elsewhere and
  renumbering would break those citations.
- **Minor (`(Python 3)` heading)** → `plugin/README.md:63`: "Utility scripts in
  `bin/` (Python 3)" → "(POSIX shell and Python 3)"; two of the four listed
  scripts are shell.
- **Minor (corrector growth attribution)** →
  `plans/pipeline-simplification/reports/measurements.md:99`: "D12 added the
  TDD slice-review protocols" → "D5 added …".
- **Minor (memory pointer)** → `memory/workflow-pipeline-revival.md:28-32`: the
  2026-09 retirements now point at the `docs/changelog.md` entry of 2026-09-01
  only. The `docs/design.md` §7 pointer is dropped — §7 names
  `validate-runbook.py` but none of `runbook-outline.md`, `/review-plan`,
  `runbook-outline-corrector` or the tiers.
- **Minor (README slice-loop consistency, decision 10)** → re-read
  `plugin/README.md` end to end. No sentence contradicts the settled commit
  convention, commit ownership or the refactor escalation. The agent table
  entries for `test-driver`, `corrector`, `refactor` and `tdd-auditor` are
  role-level and stay accurate. Only the gate sentence and the scripts heading
  needed changing.

## Follow-up from the orchestrate group

- **Per-dispatch report paths** — no change made. Neither `docs/design.md` nor
  `plugin/README.md` names a per-dispatch report file. The only report-file
  mentions are `plans/reports/triage-feedback-log.md` (`docs/design.md:1005`,
  a different artifact) and "writes findings to a report file" in the `scout`
  row of `plugin/README.md:49`, which names no path. Per the instruction not to
  add detail where none exists, both stay as they are.
- **Two commits per reviewed slice** — applied in `docs/design.md` §5.3 and in
  outline D5c and D14, as listed above.

## Not done

- **Major 10 (`docs/design.md` L-5 "~28.9 KB")** — left as instructed; it
  belongs to the index-consolidation pass.
- **Outline D3** — not touched. The opus escalation was stated in
  `docs/design.md` D-30 per the settled decision; D3 already reads "the opus
  escalation" and was outside the D5/D14 edit scope.
- `plugin/README.md:22` "each stage hands to the next via continuation" — left
  alone. It claims no hook, and the continuation fragment is being rewritten by
  the fragments group.

## Validation

`PATH=.venv/bin:$PATH just precommit` — green. Full output:

```
# version consistency
<frozen site>:101: RuntimeWarning: Unexpected value in sys.prefix, expected /Users/david/code/edify/.venv, got .venv
<frozen site>:101: RuntimeWarning: Unexpected value in sys.exec_prefix, expected /Users/david/code/edify/.venv, got .venv
Version consistent: 0.1.1
Tests cached (inputs unchanged)
✓ Precommit OK
```

The test sentinel reports cached because this group's edits are all
documentation; no file under `src/`, `tests/`, `plugin/hooks/` or `plugin/bin/`
changed. Nothing committed.
