# Review: review-fixes-2 design graph (Items 3.1–3.3)

**Scope**: `git diff 888eda7a HEAD` over `docs/changelog.md`,
`docs/changelog/2026-10-06-triage-measures-the-review-gates-set.md`,
`docs/decisions.md`, `docs/design.md`, `docs/references/build-run-state.md`;
plus the routed seam in `docs/references/pipeline-contracts.md`. Read against
the on-disk surfaces: `triage-feedback.sh`, `changed-files.sh`,
`exempt-paths.sh`, `finishing.md`, `escalation.md`, `dispatch-composition.md`,
`tdd-slice.md`, `escalation-acceptance.md`, `review-requirement.md`,
`plugin/README.md`, `build/SKILL.md` §1.
**Date**: 2026-10-06
**Mode**: review + fix
**Criteria source**: `craft:design-doc-writing` is installed (0.2.1) and was
loaded. Recall: `line-caps`, `audit-a-contract-across-its-surfaces`,
`sandbox-effects`.

## Summary

Items 3.1–3.3 deliver what the outline asks for. D-90, D-91, D-92 and D-93
now match their surfaces, the hub conclusion matches the node heading, and the
Rejected line names the new alternative. Reading the graph against the
surfaces turned up six defects: two places that still named `runbook.md` as
the only host of list revisions (the routed seam), an L-2 that implied the
older log rows compare with the new ones, an incomplete failure clause in
D-90, a D-88 that did not make the claim `/build` §1 and `finishing.md` cite it
for, and a changelog sentence that described something counterfactual as
having happened. All six are fixed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **L-2 implied the older triage-log rows compare with the new ones**
   - Location: `docs/design.md` §8 L-2
   - Problem: L-2 said only the reports column changed meaning. The script
     that wrote every earlier row (`git show 79d0b687:plugin/bin/triage-feedback.sh`,
     and `10f7f711`'s first version) counted Files Changed over the whole diff
     since the base, `plans/<job>/` and the exempt paths included. It also
     grepped behavioural code over that whole diff. All three evidence columns
     changed meaning, not only Reports. Anyone calibrating from the log would
     compare old and new Files Changed values as like for like.
   - Fix: say that the columns keep their headers but the earlier rows do not
     compare with later ones, because they were not measured over the set. The
     on-disk report count stays as the specific case. Also added "and the
     review reports" to the reports field, since the script excludes those too.
   - **Status**: FIXED

2. **D-88 did not make the claim `/build` §1 and `finishing.md` cite it for**
   - Location: `docs/references/build-run-state.md` D-88
   - Problem: `SKILL.md` §1 and `finishing.md` §1 step 1 both cite D-88 for
     "work with no `Item N.M` is Item 1.1, so every run commits an item
     report". Under KD-3 that is what turns `NO-BASE:` at finishing into a
     fault. D-88 only said "every item leaves a report". It did not say that
     item-less work is an item, and did not give KD-3's rationale.
   - Fix: added one sentence to D-88. Work with no `Item N.M` (the invocation's
     task, or a design or outline without items) is one item, Item 1.1. A
     design without items carries general work only (D-83), and the cost is
     resume granularity.
   - **Status**: FIXED

### Minor Issues

1. **List revisions named `runbook.md` as their only host (routed from
   review-agent)**
   - Location: `docs/references/build-run-state.md` D-90 (was line 76);
     `docs/references/pipeline-contracts.md` D-24 context (line 26)
   - Problem: KD-7 and `tdd-slice.md` step 3 put a list revision in the file
     hosting the item: `runbook.md`, or the `outline.md` or `design.md` routed
     to `/build`. Both nodes still said `runbook.md`. A grep for list revisions
     across `docs/` (changelog entries excluded, since those are write-time
     records) finds only these two claims. `pipeline-contracts.md` records the
     same contract, so it is the one seam, and I fixed it as the routing note
     allowed.
   - Fix: both now name the hosting file in `tdd-slice.md`'s words.
   - **Status**: FIXED

2. **D-90's failure clause left out triage's own failures**
   - Location: `docs/references/build-run-state.md` D-90
   - Problem: D-90 said only that a `NO-BASE:` or `ERROR:` from the script
     stops triage. KD-1 also sends triage's own git or grep failure to exit 2
     with no verdict and no row. `triage-feedback.sh` lines 69–72, 111–113 and
     128–131 do this, and `finishing.md` §2 says so.
   - Fix: "…or a git or grep failure of triage's own, stops triage with exit
     2, no verdict and no log row."
   - **Status**: FIXED

3. **D-93's skill-row parenthetical held a full sentence in the middle of the
   list**
   - Location: `docs/references/build-run-state.md` D-93
   - Problem: the parenthetical opened by `` `review-skill` ( `` contained a
     full stop followed by a second sentence, so the four-row list read
     broken. The wording itself matches `dispatch-composition.md` §Naming and
     `review-requirement.md` word for word (KD-8 holds).
   - Fix: moved the "An instruction file no skill loads…" sentence, unchanged,
     to after the list. That is where `review-requirement.md` puts it, after
     its table.
   - **Status**: FIXED

4. **The changelog stated as fact something that never happened**
   - Location: `docs/changelog/2026-10-06-…md`, paragraph 1
   - Problem: "every Simple run was logged `underclassified`". The log holds no
     `Simple` row. The deliverable review's claim is general and comes from a
     probe ("is logged").
   - Fix: "every Simple run would log `underclassified`".
   - **Status**: FIXED

5. **The changelog left out KD-3, which changes D-88**
   - Location: same entry, paragraph 3
   - Problem: once fix Major 2 added KD-3 to D-88, this job's dated record
     needed to name it.
   - Fix: one clause. Work with no `Item N.M` is Item 1.1, so every run leaves
     an item report and `NO-BASE:` at finishing is a fault (D-88).
   - **Status**: FIXED

## Fixes Applied

- `docs/design.md` §8 L-2: the reports field names the review-report
  exclusion. Earlier rows are stated as not comparable on any column, with the
  on-disk report count kept as the example.
- `docs/references/build-run-state.md` D-88: added KD-3 (item-less work is
  Item 1.1), with its D-83 grounding and its resume-granularity cost.
- `docs/references/build-run-state.md` D-90: list revisions live in the
  hosting file. The failure clause covers triage's own git and grep failures.
- `docs/references/build-run-state.md` D-93: the "no skill loads" sentence
  moved out of the parenthetical, words unchanged.
- `docs/references/pipeline-contracts.md` D-24 context: list revisions live in
  the hosting file.
- `docs/changelog/2026-10-06-triage-measures-the-review-gates-set.md`: changed
  "was logged" to "would log", and added the KD-3 clause.
- Reflowed with `rumdl fmt` on the touched files only, since `just format`
  would have rewritten other groups' files. `just precommit` ran in the
  foreground: Precommit OK (version consistency, 407/408 passed with 1 xfail,
  rumdl, line limits, design links: 94 decisions indexed, defined once,
  conclusions match, 9 nodes present). The three `oversized-file` lines name
  corrector agent files I did not touch. `build-run-state.md` is now 226
  lines.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| C1, M1 (D-90 triage counts the list) | Satisfied | D-90 body; matches `triage-feedback.sh` lines 18–40, 85–113 and `finishing.md` §2 |
| D-90 report count excludes per-item and review reports | Satisfied | D-90 body; matches script lines 42–72 |
| m3 (`NO-BASE:` with commits; unborn `HEAD` is exit 2) | Satisfied | D-90; `changed-files.sh` lines 86–95 |
| m2 (merge-shaped history Limitation, frequency unmeasured) | Satisfied | D-90 Limitation paragraph, with the probe recorded in `item-3-1.md` |
| m9 (D-91 `sandbox-lies` optional, with its consequence) | Satisfied | D-91; same words as `escalation.md` exit-1 bullet and `plugin/README.md` |
| M2 (D-92 committed failed fix escalates) | Satisfied | D-92; matches `escalation-acceptance.md` §Rollback protocol |
| m19 (revert operand `<tracked or indexed paths>`) | Satisfied | D-92; matches `escalation.md` |
| m11 (D-93 wording = KD-8, same words) | Satisfied | D-93 against `dispatch-composition.md` lines 114–118 and `review-requirement.md` lines 52, 56 |
| KD-1 rejected alternative | Satisfied | node Rejected alternatives; `decisions.md` *Rejected* line |
| `decisions.md` D-90 conclusion | Satisfied | matches node heading (checked by design-links) |
| L-2 (Item 3.2) | Satisfied after fix | Major 1 |
| Changelog entry and index line (Item 3.3) | Satisfied | entry plus first index line, same format as earlier entries |

**Gaps:** none remaining.

## Positive Observations

- Every D-90 clause can be traced to a line in `triage-feedback.sh`, and the
  Limitation's merge claim was probed before it was written down.
- `item-3-2.md` and `item-3-3.md` caught that the outline's "counted every
  report" was not literally true, and worded around it rather than copying
  it.
- The changelog entry leads with the motivating fact and the false rationale,
  and does not list deletions, as `design-doc-writing` asks.

## Recommendations

- **On the question already escalated (review-code Major 1). This is a view
  only and changes nothing.** A re-invoked finished job reaches §2 with two
  additions to the evidence. One is the triage log, committed by the closing
  commit outside `plans/<job>/`, which now sits in D-90's list. The other is
  `tdd-audit.md`, which counts as a report. KD-2's equal-row check therefore
  cannot catch the re-run. I would fix the evidence, not add a landed check.
  `plans/reports/triage-feedback-log.md` is the pipeline's record in the same
  sense as `plans/<job>/`, which D-90 drops for exactly that reason, so the
  list should drop it as well. `tdd-audit.md`, like `final-review.md`, is a
  review of the run and not the run's work, so it belongs with the review-report
  exclusions. With both changes the re-run's evidence equals the first run's,
  and KD-2's dedupe applies as designed. The other option is a §2 landed check
  keyed on a `Finish` commit, but that has no report path of its own to key on
  (D-89's principle), so it would key on the shared log. The decision belongs
  to my human partner.
- KD-4's landed checks for the finishing stages (`finishing.md` §1 and §3) are
  in no design node. D-88's "a finished job re-invoked … goes to finishing"
  stops before them. I have not added them: they were not among this group's
  requirements, and how §2 is worded depends on the escalated question above.
  Once that is settled, D-88 or D-89 could take one sentence on it.
