# Build leg 1 — review-fixes-4

`/build plans/review-fixes-4`, run fresh (no `item-*` report at start). The
entry gate was `CLEAN`. Recall read the artifact's eight memory files and
`craft:test-discipline`. The run finished: every item, the review gate, triage,
the TDD audit and the closing commit landed in this leg.

## Commits (subjects)

| Commit subject | Carries |
|---|---|
| `Item 1.1/1 — pin triage's repository-root cd failure` | the test, the narrowed comment, RED, test-review and GREEN reports |
| `Item 1.1/1 — code-review fixes` | the code-review report alone (no fixes needed) |
| `Item 1.2 — prose fixes F1, F2, F4–F7` | six prose edits, `item-1-2.md` |
| `Review gate` | `review-code`, `review-skill`, `review-design` reports; one reword in `triage.md` |
| `Finish` | triage log row, `tdd-audit.md` |

`verify-step.sh` ran `CLEAN` after every committed step. This leg report is
committed after `Finish`.

## Review gate and triage

- `review-code` (corrector): 0 issues in F3, F4, F7. Three mutations of the
  script each reded the new test on an assertion.
- `review-skill` (`plugin-dev:skill-reviewer`, report-only, sonnet): Pass, one
  minor. `triage.md` still said the file's "first line" is the job-level line,
  which F5 had just loosened. The session reworded it, the reviewer's one second
  pass asked for one further rewording, and the session applied that too. That
  last rewording went unreviewed by design.
- `review-design` (corrector): 0 in-scope issues. One OUT-OF-SCOPE stale
  sentence, see the first open question.
- Triage: `match`, 7 files, 4 reports, behavioural code yes, review artifact
  yes. Classification `Moderate`. No final-review dispatch, since the gate
  covered all four groups.

## TDD audit

Verdict: PASS WITH RECOMMENDATIONS, no violation. Item 1.1 slice 1 is a genuine
mutation red. Recommendations, all about pipeline text and none a defect here:

1. `tdd-slice.md` (c) does not describe a GREEN with no implementation to
   write, as in a mutation-red slice whose GREEN is a comment edit.
2. A test review of a mutation-red slice that changes the fixture should re-run
   the RED's own mutation after its last fix.
3. Require a mutation per asserted contract, not per test. RED's mutation
   reded only the stdout assertion; the test review's `exit 3` mutation proved
   the exit-code one.
4. (Minor) A figure in a docstring, here "exits 1 with empty stdout", is either
   measured by the dispatch or attributed to its source. The auditor measured
   it independently and it holds.
5. (Minor) `plugin/agents/corrector.md` code-review step says "save the SUT,
   mutate, restore", against `tdd-slice.md` "never restore from a copy". The
   `review-code` gate reviewer restored from a saved copy; the tree was clean
   afterwards. The untracked `inbox/brief-slice-code-review-mutation-runs.md`
   raises the same conflict.

## Dispatches by model

| Dispatch | Agent | Model |
|---|---|---|
| `item-1-1-s1-red`, `item-1-1-s1-green` | `edify:test-driver` | haiku |
| `item-1-2` | `edify:artisan` | haiku |
| `item-1-1-s1-test-review`, `item-1-1-s1-code-review` | `edify:corrector` | sonnet |
| `review-code`, `review-design` | `edify:corrector` | sonnet |
| `review-skill` | `plugin-dev:skill-reviewer` | sonnet |
| `tdd-audit` | `edify:tdd-auditor` | sonnet |

No haiku dispatch failed its contract, so there was no escalation. No dispatch
was named, none stopped, and none was left running. Every executor ran its suite
in the foreground. `/deliverable-review` was not run; the main session
dispatches it.

## Open questions for my human partner

1. **Stale sentence in `dispatch-composition.md`** (§Naming and resumption,
   near line 130): "The gate routes implementation files only; planning
   artifacts route by artifact (`finishing.md` §1)." It is the sentence F2 fixed
   at its two other sites, and the `review-design` reviewer called it stale,
   since the gate does route planning artifacts as `review-plan-*`. The
   `review-skill` reviewer judged it consistent. It is outside the outline's
   verbatim list. **Default:** a one-line follow-up edit to the F2 form, "The
   four group rows take implementation files only; ...", landed with the next
   job or after the deliverable review. Not edited here.
2. **The pipeline recommendations above (1 to 3, and 5).** **Default:** treat
   them as inputs for the next pipeline-text job, with no change in this one.
   Recommendation 3 and the code-review restore conflict overlap the three
   untracked `inbox/brief-*.md` files, which this leg left alone.
3. **Reviewer model.** `tdd-slice.md` says test review and code review run opus
   (D-32 reviewer one rung above the implementer); this job's ruling put them
   on sonnet over haiku implementers, which keeps the one-rung gap. No action
   needed unless the ruling should change the skill text.

## State

`main` is clean apart from the three untracked `inbox/brief-*.md` files, which
belong to another session. `just precommit` is green.

## Next leg resumes at

Nothing is left in this job. Follow-up: `/deliverable-review plans/review-fixes-4`
(opus, fresh session, dispatched by the main session).
