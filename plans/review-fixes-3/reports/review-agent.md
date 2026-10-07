# Review: review-fixes-3 — review-agent group (agent definitions)

**Scope**: `plugin/agents/refactor.md` (Item 3.4, m13) and
`plugin/agents/tdd-auditor.md` (Item 2.4, m14, KD-7), diffed against baseline
`daad4769e5eb694f151b9972ed51555033d0e1ca`
**Date**: 2026-10-08
**Mode**: review + fix

## Summary

Two one-site prose changes. `refactor.md` §Step 5's plan-sources paragraph now
gives a reason covering all four files the prohibition names: the hosting file
takes the orchestrator's list-revision commits, and the rest are the plan the
run executes against. `tdd-auditor.md` check 2's GREEN-commit query gains
`--no-show-signature` and nothing else. Both match the outline's contracts
word for word. Read against the `/build` surfaces that dispatch these agents,
they agree.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Fixes Applied

None. No edits were made.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Item 3.4 (m13): the reason covers every file the prohibition names | Satisfied | `refactor.md:162-166`. The hosting file is one of `runbook.md`, `outline.md` or `design.md`, and "the rest" covers the other two and `requirements.md` |
| Item 3.4: hosting file takes list-revision commits, the rest are the plan, a second writer collides with either | Satisfied | Same lines. Wording follows the outline contract clause by clause |
| Item 3.4: prohibition unchanged | Satisfied | The list `runbook.md`, `design.md`, `outline.md`, `requirements.md` and the report-path exception are byte-identical to the baseline |
| Item 2.4 (m14, KD-7): check 2's `--format=%H` query passes `--no-show-signature` | Satisfied | `tdd-auditor.md:87` |
| Item 2.4: no other wording changed | Satisfied | The baseline diff for `tdd-auditor.md` is the one flag insertion |
| KD-7: §Inputs' `git log` forms are out | Satisfied | `tdd-auditor.md:60-61` unchanged. Neither form carries `--format=%H` |

**Gaps:** none.

**Verification run:**

- `just precommit` passed (`Tests cached`). The line-limits check printed the
  three oversized corrector files and still passed. They are in Scope OUT
  (defect 21).
- `.venv/bin/pytest -p no:markdown_report tests/test_build_prose_git_log.py`:
  10 passed, 0 skipped, including `tdd-auditor.md:1`. `ssh-keygen` and git
  SSH signing are present here, so the signed-history fixture actually ran.

---

## Cross-surface reading

The surfaces are: the rule (the outline's KD-7 and Item 3.4), the dispatcher
(`tdd-slice.md`, `dispatch-composition.md`, `finishing.md` §3) and the agent
consuming it (`refactor.md`, `tdd-auditor.md`).

- **tdd-auditor check 2 ↔ `tdd-slice.md` (c).** The two now hold the same
  command, flags and all: `git log --diff-filter=A --no-show-signature
  --format=%H -- plans/<job>/reports/item-N-M-s<k>-green.md`. The auditor's
  "resolve it from the RED report the same way" reuses that flagged form.
- **tdd-auditor ↔ `finishing.md` §3 step 2.** The inputs match: the slice
  reports, plus the hosting file "which the prompt names". git is used for
  report→commit resolution, commit diffs and list-revision commits. The
  auditor's Edge Cases citation of `finishing.md` §3 resolves to
  `## 3. Completion`, which holds the TDD-audit step.
- **refactor ↔ `tdd-slice.md` §After the slice.** The refactor is dispatched
  only in step 2, so "You run inside a slice" holds. Step 3's list revision is
  made in the hosting file and committed with
  `git commit -- plans/<job>/<hosting file>`. That is the collision the new
  reason names: a refactor edit to the hosting file would ride that commit.
  Both files use the same hosting-file phrase: "`runbook.md`, or the
  `outline.md` or `design.md` routed to `/build`".
- **refactor ↔ `dispatch-composition.md` item 5.** The report-path exception
  ("your report under `plans/<job>/reports/` … is required") agrees with
  item 5. That item names `edify:refactor` as writing its report at the
  assigned path while returning its own status protocol.

## Agent-development criteria (changed passages only)

- Frontmatter is not touched by either change. Name, model, color and tools
  are unchanged and valid.
- Tool access is unchanged. The flag needs no new tool: tdd-auditor already
  holds Bash for `git log`.
- System-prompt structure: both edits sit inside existing sections (refactor
  §Step 5, tdd-auditor §Per-Slice Checks item 2), with no new headings and no
  restructuring.
- The changes do not touch `refactor.md`'s description, which lacks the
  `Use this agent when …` / examples shape. Per the dispatch it is not
  flagged.

## Positive Observations

- The refactor paragraph keeps the prohibition unchanged and adds only the
  reason. It splits the files into two roles, so the reason covers every
  file the prohibition names, not just `runbook.md`.
- The hosting-file phrase is reused verbatim from `tdd-slice.md` step 3 and
  `tdd-auditor.md` §Inputs, so the three surfaces cannot drift on which file
  takes list revisions.
- The tdd-auditor edit is the minimal one KD-7 requires, and the scanning test
  pins it.

## Recommendations

None within scope.
