# Fix report: agent-definitions group

**Date:** 2026-09-02
**Source:** `plans/pipeline-simplification/reports/deliverable-review.md`
**Scope:** `plugin/agents/{test-driver,tdd-auditor,refactor,runbook-simplifier,corrector,artisan}.md`
**Line numbers below are post-edit.**

## Findings applied

| Finding | Site | Change |
|---|---|---|
| Critical 2 | `test-driver.md:60-66` | Slice commit subject is `<type>: Item N.M/k — <title>` with the type the executor's free choice (`feat`/`fix`/`docs`/`perf`/`test`/`build`/`chore`); states that the `commit-msg` hook rewrites the prefix so nothing downstream keys on it, and that `Item N.M/k` identifies the commit. GREEN report now carries the commit hash, the tests run, and the one-at-a-time pass order, named as the audit's source instead of commit history. |
| Critical 2 | `tdd-auditor.md:64-72` (check 2) | No longer greps `feat:`. The GREEN report names the single slice commit; identification is by report, and `Item N.M/k` is the only thing matchable in a subject. Red-suite spot-check now reads the GREEN report's suite result. |
| Critical 2 | `tdd-auditor.md:85-88` (check 4) | Refactor commit identified from the refactor report, not a `refactor:` prefix. |
| Critical 2 | `tdd-auditor.md:41-51` (Inputs) | Inputs are the four per-slice reports in order (RED → test review → GREEN → code review), the reviews being the paths the orchestrator assigned and named by `Item N.M/k`; each names its commit. Fallback is the dispatch transcript under the session's `subagents/` directory. Git history is restricted to confirming a named commit exists and diffing it. |
| Critical 2 | `tdd-auditor.md:119` | Report table column `One feat: commit` → `One slice commit`. |
| Critical 1 | `corrector.md` | No change, as directed: the orchestrator commits code-review fixes; the corrector stays non-committing. |
| Major 1 | `corrector.md:364-370` | The dispatch prompt's report path governs, whatever default the definition carries, with the collision rationale stated. Fallbacks kept in order: `plans/<plan>/reports/review.md` when a plan is named, else `tmp/review-<ts>.md`. |
| Major 1 | `tdd-auditor.md:43-47` | Per-slice reviews described as the orchestrator-assigned paths named by `Item N.M/k` rather than a fixed filename. |
| Major 2 | `corrector.md:184` | Untouched, as directed (tracked under pilfer defect 21). |
| Major 3 | `refactor.md:160-164` | Added `git add <the files you changed>` before the commit. |
| Major 4 | `refactor.md:131-152` | Step 5's `plans/` sweep deleted; the sweep and its verification now cover `docs/` and `CLAUDE.md` only. Added the prohibition on writing into `plans/` with the two-writers-on-`runbook.md` reason, and the instruction to record renames in the report for the orchestrator to carry. Steps 1 and 2 renumbered within Step 5; no top-level renumbering needed. |
| Major 5 | `refactor.md:29-38, 57-62, 92-99, 178-179` | `escalated:` kept and given its consumer. Escalation table row now reads "the opus re-dispatch"; added that the model is not visible to the agent and that a run the prompt names as the opus escalation performs the refactoring rather than escalating again. Return protocol notes `escalated:` never comes from that run. |
| Major 6 | `runbook-simplifier.md:50-52` | Context input accepts `design.md` or `outline.md`, whichever the plan has. |
| Major 8 | `test-driver.md:54-59` | GREEN runs the full suite, `just lint`, then `just precommit`, before the commit; item 4 now reports that run's warnings rather than a command never invoked. |
| Minor (auditor) | `tdd-auditor.md:64-72` | "or CI evidence" removed with the check-2 rewrite; no CI exists. |
| Minor (auditor) | `tdd-auditor.md:164-165` | "ask the caller for the range" → `blocked: <what is missing>`, with the reason (a one-shot dispatch has no caller). |
| Minor (auditor) | `tdd-auditor.md:33` | "planned-vs-executed cycle count" → "planned-vs-executed slice count". |
| Minor (auditor) | `tdd-auditor.md:80-83` | Added the D14 note: under one commit per slice, FR-5's "test-at-a-time from the commit sequence" is unauditable from git and is audited from the GREEN report's recorded sequence plus the tests-unmodified diff check. |
| Minor (thresholds) | `runbook-simplifier.md:88, 156` | "≤8 assertions" and "≤10 items" labelled *(ungrounded — needs calibration)*, matching `runbook-corrector.md:78`. |
| Minor (vocabulary) | `corrector.md:156, 301` | "this step/phase" → "this item/phase"; "Flag any step containing" → "Flag any item containing". `corrector.md:293-304`'s runbook criteria left untouched, as directed. |
| Minor (housekeeping) | `refactor.md` end | "Created: 2026-01-30 / Purpose:" footer deleted. |
| Minor (housekeeping) | `artisan.md:65` | "Use **Bash `rg`** instead of `grep` or `rg` commands" → "instead of `grep`". |

## Second pass — report naming and the two-commit slice

Applied after the orchestrate group finalized dispatch-name report paths.

| Change | Site | Detail |
|---|---|---|
| Literal report names | `tdd-auditor.md:43-52` | Inputs now name the four per-slice files: `item-N-M-s<k>-red.md`, `-test-review.md`, `-green.md`, `-code-review.md`, all under `plans/<job>/reports/`, with the rule that a report path is mechanically its dispatch name. Added `phase-P-corrector.md` and `final-review.md`. |
| Auditor's own report | `tdd-auditor.md:116` | `plans/<job>/reports/tdd-process-review.md` → `tdd-audit.md`. Matches the rename `fix-orchestrate.md:19` records. No other live reference to the old name remains. |
| Literal report names | `test-driver.md:39-41, 68-69` | RED writes `plans/<job>/reports/item-N-M-s<k>-red.md`, GREEN writes `item-N-M-s<k>-green.md`, both still stated as the path the prompt assigns. |
| Two-commit slice | `tdd-auditor.md:71-84` (check 2) | The slice commit is keyed on the hash the GREEN report names. Added: a reviewed slice carries two commits bearing the `Item N.M/k` marker — the GREEN commit and the orchestrator's code-review-fix commit — and the second is expected wherever the code-review report accounts for it, not a slice split across commits. A marker-bearing commit no report accounts for is the violation. |
| Slice-commit identity | `test-driver.md:64-65` | "`Item N.M/k` is what identifies the slice commit" → the hash recorded in the report identifies it, since the marker is no longer unique. |

**Open point for the orchestrate group.** Check 4 (refactoring separation)
cites "the refactor report" with no filename. The finalized naming list
covers slice, checkpoint, closing and audit dispatches but not the `refactor`
dispatch, so no literal name was invented here. If refactor dispatches are
named `item-N-M-s<k>-refactor`, that name should land in
`tdd-auditor.md:96-99`. The same gap applies to `refactor.md:166-169`, which
tells the agent to name its commit hash in "your report" without a filename.

## Left undone

- Nothing from the assigned list. Every finding routed to this group was
  applied.
- Sites for Critical 2 outside this group (`dispatch-composition.md`,
  `outline.md` D5/D14, `docs/design.md` §5.3/D-26) belong to the sibling
  agents; `dispatch-composition.md:19-35` was read and its wording agrees
  with what landed here.
- `refactor.md` now says to record renames "in your report". `refactor` has
  no report path in its own definition, but every dispatch receives one
  (`dispatch-composition.md:29-35`), so the reference resolves. No report
  contract was added to the agent, to avoid widening scope.

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

The test suite was served from the sentinel cache, not re-run: these edits
touch only `plugin/agents/*.md`, which is not a test input. Nothing committed.
