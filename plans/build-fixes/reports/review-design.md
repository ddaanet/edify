# Review: build-fixes review gate, `review-design` group

**Scope**: `git diff d415f22daf94eb5ae5424a927e126f4010ff7a21 HEAD` over
`docs/references/build-run-state.md` (new), `docs/references/pipeline-contracts.md`,
`docs/decisions.md`, `docs/design.md`, `docs/changelog.md`,
`docs/changelog/2026-10-03-build-reads-run-state-from-report-history.md` (new).
I read these against `plans/build-fixes/outline.md` (KD-1 to KD-8, Items 2.12
and 2.14), `plans/build-defects/outline.md` KD-7, and the shipped `/build`
text: `SKILL.md`, `references/{phase-boundary,escalation,finishing,dispatch-composition,tdd-slice}.md`,
the headers of `changed-files.sh`, `verify-step.sh` and `exempt-paths.sh`,
`plugin/bin/triage-feedback.sh`, `plugin/fragments/review-requirement.md` and
`plugin/agents/tdd-auditor.md`.
**Date**: 2026-10-03
**Mode**: review + fix
**Criteria source**: `craft:design-doc-writing`, loaded (no fallback needed).

## Summary

Item 2.12 is done: D-86's defect clause is now in the past tense. Item 2.14 is
done in the venue my human partner chose: one new node holds D-88 to D-94 and
cites D-86. A new group in the index has seven conclusion lines that match the
node's leads word for word, and a *Rejected* line naming all twelve of the
node's rejected alternatives. The `docs/design.md` §5.3 hub paragraphs were
rewired to match, and a changelog entry was added. Each decision agrees with
the shipped `/build` text, with three exceptions. One rationale clause
contradicted `changed-files.sh`'s own header, and a probe confirmed the header
is right. Two clauses were imprecise against the shipped text. All three are
fixed, along with one hub phrasing.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **D-88 gave `--no-renames` a role it does not have**
   - Location: `docs/references/build-run-state.md` D-88, after the base query
   - Problem: the node said "`--no-renames` counts a report renamed into place
     as added". `changed-files.sh`'s header says the opposite: the flag is
     there "for uniformity only: a path-limited log pairs no rename source from
     outside its pathspec, so a report renamed into place reads as added either
     way". I probed this in a scratch repo on git 2.47.3: `tmp/r.md` moved to
     `plans/j/reports/item-1-1.md`. `git log --diff-filter=A` returns the move
     commit both with `diff.renames=true` and with `--no-renames`. A future
     reader would take the flag as load-bearing for the resume test, and it is
     not.
   - Fix: say the flag is there for uniformity with the script's diff only,
     with the header's reason.
   - **Status**: FIXED

### Minor Issues

1. **D-90 said triage "calls the script"**
   - Location: `docs/references/build-run-state.md` D-90, "Every site that
     needs the list or the base calls the script"
   - Note: `triage-feedback.sh` never calls `changed-files.sh`. It takes
     `<baseline-commit>` as an argument, and `finishing.md` §2 fills that in
     from the script's `BASE:`. Its two diffs are unfiltered `<base> HEAD`
     diffs, which the node already describes correctly as "the same form".
   - Fix: "triage, which takes the script's `BASE:` as its argument and whose
     two diffs take the same `<base> HEAD` form".
   - **Status**: FIXED

2. **D-92's revert command, taken literally, errors when one half has no paths**
   - Location: `docs/references/build-run-state.md` D-92, the one-call revert
   - Note: `escalation.md` §Post-item remediation and the outline's KD-3 both
     say to drop the half with no paths, because `git restore` and `rm` both
     error on an empty operand list. The record left that out.
   - Fix: added "dropping either half that has no paths, since both commands
     error on an empty operand list".
   - **Status**: FIXED

3. **Hub Scripts parenthetical read as a list of fragments**
   - Location: `docs/design.md` §5.3, "(clean tree, D-91, + precommit, …"
   - Note: the comma-separated citation and `+` made it hard to tell that D-91
     defines the clean tree.
   - Fix: "(the clean tree of D-91 plus precommit, …".
   - **Status**: FIXED

## Fixes Applied

- `docs/references/build-run-state.md` D-88: corrected the `--no-renames`
  rationale to match the `changed-files.sh` header and the probe.
- `docs/references/build-run-state.md` D-90: triage takes the script's `BASE:`
  as its argument; it does not call the script.
- `docs/references/build-run-state.md` D-92: added the empty-operand clause to
  the revert call.
- `docs/design.md` §5.3: reworded the `verify-step.sh` parenthetical.
- `just format`: `rumdl` reflowed the edited `build-run-state.md` paragraphs,
  whitespace only.

**Files changed:** `docs/references/build-run-state.md`, `docs/design.md`.
Node: 184 → 190 lines. Hub: 339 lines, unchanged. Both are under the 400 cap.
Nothing was staged or committed.

**Verification:** `just precommit` green with the fixes in the tree. Checks
that passed:

- version consistency (0.3.0);
- tests 383/384 passed, 1 xfail;
- line limits: only the three allowlisted correctors reported;
- design links: "94 decisions indexed, defined once, conclusions match, 9
  nodes present".

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| Item 2.12 (m17), D-86 clause in the past tense | Satisfied | `pipeline-contracts.md` D-86, "which then tolerated nothing but ` M memory`". The rest of the paragraph is a rumdl reflow with no word changed. |
| Item 2.14, KD-1 recorded | Satisfied | D-88. Rejected: the baseline file, commit subjects as the key, the start marker. |
| Item 2.14, KD-2 recorded | Satisfied | D-89. The three query choices, the STOP, the never-empty base and the resume inventory are all there. |
| Item 2.14, KD-3 recorded | Satisfied | D-92. The live-run chain, the after-kill examination, the tdd limit and the per-path decision with a one-call revert are there. Its four rejections are in the node and the index. |
| Item 2.14, KD-5 recorded | Satisfied | D-93. Four rows and slugs, the class rule, the `craft` criteria and fallback. Rejected: a group per file kind, and `design-corrector`. |
| Item 2.14, KD-6 recorded | Satisfied | D-90. Rejected: prose copies at each site. |
| Item 2.14, KD-8 recorded | Satisfied | D-94, plus the rewired `docs/design.md` §5.3 paragraph. |
| Item 2.14, build-defects KD-7 (+ addendum) recorded | Satisfied | D-91. The three exemptions, untracked counted, `--untracked-files=all`, the rename/copy fail-closed rule and the safety argument are there. Rejected: filtering or gitignoring the mask names. |
| Index conclusion lines match the node | Satisfied | Seven lines, word for word; the `design-links` check agrees. |
| Hub changes together with its node (orchestrator's extension) | Satisfied | §5.3 Scripts and the commit-subjects paragraph. |
| Changelog entry | Satisfied | It leads with the motivating defect, states the positive design, and is indexed in `docs/changelog.md`. |

**Where the record follows shipped text over the outline**, as `item-2-14.md`
declares, I checked each case against the shipped text:

- `:(glob)` in D-88 and in `--phase`'s pathspec, and `--no-renames` in D-88:
  they match `changed-files.sh` once the rationale fix above is applied.
- D-89's two-condition STOP matches `phase-boundary.md` §Base and changed
  files.
- D-90's working-tree form, covering `/review` and the §4.1 corrector, matches
  `review-requirement.md` §Execution Context.
- D-91's `memory` exemption in any state but a rename or copy matches
  `exempt-paths.sh` and `verify-step.sh`. The outline's Scope OUT accepts it as
  F-2.

**Integration grep.** `tmp/build-baseline`, `git checkout -- .`, `clean -fd`,
`Item N.M`, "two verification scripts", `review-fragments` and `review-agents`
over `docs/` (excluding `docs/superpowers/` and the dated changelog files)
return only the new records' own rejected-alternative and grounding text. No
other node, and nothing in the hub, still states a conclusion these decisions
changed. D-80's Provenance `Base:` covers the deliverable-review range, not
`/build`'s run base, so it does not conflict with D-88. D-49's
`verify-step.sh` description in `quality-gates.md` is still accurate.

**Style.** The records are present-tense and carry no draft archaeology or
supersession bookkeeping. The superseded build-defects KD-1 and KD-5 were never
in the graph, so no superseding pointer is owed. The records hold no commit ids
and no "as of" claims. D-86's existing commit-id grounding predates this diff
and is out of review.

## Noted, not raised (outside this group's scope)

- **`plugin/agents/corrector.md` §0 versus D-93.** This is the known open
  finding under discussion with my human partner. I did not re-litigate it. This
  dispatch ran because its scope was a multi-file git diff, not a single
  `design.md`.
- **`.claude/rules/workflow-work.md`** routes workflow work only to
  `pipeline-contracts.md` and `execution-routing.md`, so it does not route to
  `build-run-state.md`. `.claude/rules/` is in Scope OUT. `item-2-14.md` already
  flags this for the orchestrator.
- **`CLAUDE.md` routing bullet** for the new node: pending with my human
  partner. Not flagged as a finding.

## Positive Observations

- Every decision gives its rationale beside its conclusion. D-93 cites the
  observed run as its grounding (`review-agents`, `review-fragments`) instead
  of inventing a rationale.
- The rejected alternatives that the superseded build-defects KD-1 made, and
  that still hold (`tmp/build-phase-base`, `HEAD~N`), were carried into D-89
  rather than lost.
- The changelog entry leads with the incident: a fresh session recaptured the
  baseline, and the no-owner cleanup deleted legitimate `inbox/` dirt.
