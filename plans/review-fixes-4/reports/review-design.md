# Review: review-fixes-4 Item 1.2 — D-93 paragraph (review-design group)

**Scope**: `docs/references/build-run-state.md` D-93 paragraph, diff
`35d470b1..HEAD`; agreement with `docs/decisions.md`, D-89, D-26,
`plugin/skills/build/references/finishing.md` §1 and
`plugin/skills/build/references/dispatch-composition.md` §Naming and
resumption.
**Date**: 2026-10-09
**Mode**: review + fix
**Criteria source**: `craft:design-doc-writing` (craft 0.2.1, installed and
loaded): living-doc present tense, hub/node agreement, no stale statements.

## Summary

Both outline edits are present and the wording is identical to the outline text
after the re-wrap. `docs/decisions.md` D-93 carries a conclusion line that does
not paraphrase the routing sentence, so it needs no change. The F1 claim is
true of the D-89 landed check as `finishing.md` §1 states it. One stale
same-claim sentence exists in `dispatch-composition.md` (outside Scope IN).

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Stale same-claim sentence in `dispatch-composition.md`**
   - Location: `plugin/skills/build/references/dispatch-composition.md:130-131`
     ("The gate routes implementation files only; planning artifacts route by
     artifact (`finishing.md` §1).")
   - Problem: same sentence F2 corrected in the node and in `finishing.md:76`.
     The gate does route planning artifacts (as `review-plan-*`, which this
     file's next bullet names), so "the gate routes implementation files only"
     contradicts its own next bullet. The node, `finishing.md` and this file now
     disagree on the sentence.
   - Opinion: reword to the F2 form ("The four group rows take implementation
     files only; planning artifacts route by artifact (`finishing.md` §1)."),
     as a follow-up edit to that file. The outline's Item 1.2 does not list it,
     and the F2 edit of the node and `finishing.md` already made the wording
     stale there.
   - **Status**: OUT-OF-SCOPE — file is outside Scope IN; reported with
     opinion, not edited.

## Fixes Applied

None. No in-scope issue found.

## Verification

- **Verbatim check.** F2 sentence in the node reads "The `/build` review gate's
  four group rows take implementation files only; a planning artifact on its
  list routes by artifact (D-26)." F1 sentence reads "The gate's reports,
  `review-plan-*` ones included, land under the running job's `reports/` in one
  commit, together with any planning corrector's edits to the source job's plan
  file: a `review-plan-*` report committed on its own, ahead of the group
  reports, would read to D-89's landed check as the gate landed." Both match the
  outline; F1 sits right after "read its report as a review report." as
  specified. Remainder of the paragraph is unchanged apart from the re-wrap.
- **decisions.md.** D-93 line is "Review-gate groups are four fixed rows, with
  fixed slugs." It paraphrases neither the routing sentence nor the F1
  sentence. No other occurrence of the old sentence in `docs/`.
- **design-links.** `just precommit` (foreground, full output): exit 0,
  "94 decisions indexed, defined once, conclusions match, 9 nodes present". The
  three `oversized-file` lines (corrector, outline-corrector, design-corrector)
  are allowlisted files this change does not touch. The node is 278 lines.
- **F1 truth vs the D-89 landed check.** `finishing.md` §1 queries
  `git log -1 <L>..HEAD -- ':(glob)plans/<job>/reports/review-*.md'` where
  `<L>` is the last item-report commit. `review-plan-<source job>-<stem>.md`
  matches `review-*.md`, so a lone earlier `review-plan-*` commit prints a hash
  and reads as the gate landed. D-89 in the node states the same key ("the
  review gate on a `review-*.md` report, `review-skip.md` included"), and
  `finishing.md:116-118` states the identical hazard. `dispatch-composition.md`
  :136 ("matches `review-*.md`, so the gate's landed check reads its report as a
  review report") agrees. "Land under the running job's `reports/`" matches
  `finishing.md:88` and "a planning corrector's edits to the source job's plan
  file included" matches `finishing.md:113-115`. Three surfaces (node D-93/D-89,
  `finishing.md` §1, `dispatch-composition.md`) agree on the rule, the enforcer
  and the consumer; the one disagreement is the stale sentence above.
- **Living-doc style.** The inserted text states a present rule with its
  mechanism, no dates or status. The antecedent of "Its groups" (previously a
  report) is now "the gate", which reads correctly. No stale statement about
  routing remains in the node.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| F2 (D-93 routing sentence) | Satisfied | node lines 183-185 |
| F1 (insert after "report as a review report.") | Satisfied | node lines 189-194 |
| decisions.md conclusion matches | Satisfied | line unchanged, precommit design-links green |

**Gaps:** none.

## Positive Observations

- F1 names the exact failure (a lone `review-plan-*` report read as the gate
  landed) and its enforcing key (D-89), so a reader can verify it against
  `finishing.md` §1.
- The re-wrap left no mid-paragraph artifacts and kept the 80-column shape.

## Deferred Items

None.
