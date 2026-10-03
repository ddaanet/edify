# Review: build-fixes review gate, `review-agent` group

**Scope**: `plugin/agents/tdd-auditor.md`, `plugin/agents/test-driver.md`,
`plugin/agents/refactor.md`. The diff reviewed is
`git diff d415f22daf94eb5ae5424a927e126f4010ff7a21 HEAD`. It was read against
outline Items 2.10 and 2.13 and KD-8, and against `/build`'s current text in
`SKILL.md`, `tdd-slice.md`, `dispatch-composition.md`, `finishing.md`,
`phase-boundary.md` and `escalation.md`.
**Date**: 2026-10-03
**Mode**: review + fix

## Summary

The diff changes three things:

- It renames "Phase checkpoints" to "Phase boundaries" in the auditor's
  §Inputs.
- It gives every commit-subject prescription and subject match in the three
  agents KD-8's `<job> Item N.M/k` form.
- It widens the auditor's check on marker-bearing commits. The refactor commit
  and the `runbook.md`-only list-revision commit no longer count as violations.

All three agents now agree with `/build` on subjects, reports and the slice's
commits. No remaining old-form subject prescription exists in `plugin/`.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Fixes Applied

None. No file changed.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Item 2.10, m15: "Phase checkpoints" becomes "Phase boundaries" | Satisfied | `tdd-auditor.md:51`. It matches `SKILL.md` §4.5 "Phase boundary" and `dispatch-composition.md:108` (`phase-P-corrector` for phase boundaries). |
| Item 2.10: any subject match the auditor prescribes takes KD-8's form | Satisfied | `tdd-auditor.md:86` and `:96-97` read `<job> Item N.M/k`. Check 4 (`:132-133`) and §Inputs (`:53-55`) resolve commits by report path, not by subject, so they need no change. |
| Item 2.13: every file prescribing a `/build` commit subject takes KD-8's form | Satisfied | `test-driver.md:95` uses `<type>: <job> Item N.M/k — <title>`, the same string as `tdd-slice.md` (c). `refactor.md:184` uses `refactor: <job> Item N.M/k — <what changed>`. See the grep below for the rest of `plugin/`. |
| KD-8: subjects are labels only, and nothing mechanical keys on them | Satisfied | The auditor resolves slice, refactor and code-review commits from the commits that add their reports (`:80-82`, `:132-133`). The marker is used only by the agent reading labels to spot an unaccounted commit. `test-driver.md:97-99` and `refactor.md:188-190` still say that nothing keys on the type. |

**Gaps:** none.

### Scope completeness grep

I ran
`rg -n 'Item N\.M|<type>:|Phase P boundary|Review gate|commit -m' plugin/` and
dropped the lines already carrying `<job>`. Then I ran
`rg -n 'N\.M/k|N\.M\[/k\]|subject' plugin/`.

- The only commit-subject prescriptions outside `plugin/skills/build/` are
  `test-driver.md:95` and `refactor.md:184`. Both now carry `<job>`.
- Every subject in `plugin/skills/build/` carries `<job>`:
  - `dispatch-composition.md:28-29`
  - `tdd-slice.md` (c) and §After the slice, steps 1 and 3
  - `phase-boundary.md:75`
  - `finishing.md:78` and `:126`
  - `SKILL.md:119`
- The remaining `Item N.M:` hits are runbook item syntax used as content
  markers, not commit subjects:
  - `item-review.md:17`
  - `runbook-format.md:16`
  - `design-corrector.md:68` and `:77`
  - `corrector.md:153`
- `runbook-format.md:38-39` describes `N.M/k` as the id used in slice commit
  subjects. That is still true, and it prescribes no subject form.
- For information only: `docs/` and `CLAUDE.md` have no old-form `Item N.M`
  subjects left. Both are outside this group's scope.

No prescription outside the three files needs reporting.

### Integration: agents against `/build`

I read the contract as three surfaces. The rule is KD-8 and
`dispatch-composition.md` item 4. The producers are `test-driver`, `refactor`,
and the orchestrator's code-review and list-revision commits in `tdd-slice.md`.
The consumer is `tdd-auditor`.

- **Every marker-bearing commit a slice can produce is accounted for by the
  auditor.** There are four:
  - The GREEN commit, which adds `-green.md`.
  - The code-review commit, which adds `-code-review.md` (`tdd-slice.md` step
    1).
  - The refactor commit, which adds `-refactor.md` (`refactor.md` Step 6,
    auditor check 4).
  - The list revision, `git commit -- plans/<job>/runbook.md` (`tdd-slice.md`
    step 3).

  The new "touches `runbook.md` alone" condition matches step 3's single-path
  commit. Without the widening, the auditor would flag every list revision,
  because KD-8 now puts the marker on that commit too. The refactor commit had
  the marker before this change as well. Item 2.10's judgement call holds.
- **The escalated refactor run makes no commit.** The sonnet run that returns
  `escalated:` stops before Step 6, and the opus re-dispatch reuses the
  `-refactor` name. That gives one report and one refactor commit, which is
  what check 4 expects.
- **The producers write the same label the consumer reads.** `test-driver`
  takes the job and title from the prompt, which carries the subject per
  `dispatch-composition.md` item 4. `refactor`'s `<job>` is bound by the report
  path in the same code block. Both produce exactly the `<job> Item N.M/k`
  label the auditor matches.
- **Reports name no commit hash in any of the three agents.** This agrees with
  `dispatch-composition.md` item 5 and `finishing.md` §3.2.

### `plugin-dev:agent-development` criteria, changed parts

- **Frontmatter:** no hunk touches it, and `validate-agent.sh` passes `name`,
  delimiters and structure on all three files. The validator also warns on the
  description in all three files: no `<example>` blocks in two of them, and it
  misreads `tdd-auditor`'s `|` block scalar as one character. The descriptions
  predate the baseline, so these warnings are not findings here.
- **Tools:** unchanged.
- **System prompt:** the edits stay inside the existing numbered steps and keep
  second-person imperatives. Each new sentence gives an act and its reason.

## Positive Observations

- The widened auditor check names each extra commit together with how it is
  accounted for: the refactor commit by its report, the list revision by
  touching `runbook.md` alone. That avoids a blanket exemption.
- `refactor.md` keeps the type advisory and changes only the label. Its
  "nothing keys on the type" paragraph is still accurate without edits.
- Item 2.13 did not repeat KD-8's "nothing mechanical keys on the subject" in
  each agent. KD-8 is stated once, in `dispatch-composition.md` item 4.

## Recommendations

None within scope.

## Verification

`just precommit` ran green in the foreground with nothing changed in the tree.
It reported:

- version consistency
- cached tests
- line limits, where only the three allowlisted correctors reported
- design links: 94 decisions indexed, 9 nodes

## Files changed

- `plans/build-fixes/reports/review-agent.md`, this report. It is the only file
  written.
