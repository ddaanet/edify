# Review: Item 2.5 — dispatch-composition naming, return contract, pathspec commit

**Scope**: uncommitted changes to `plugin/skills/build/references/dispatch-composition.md`
(§Naming and resumption, §Prompt contents items 4 and 5),
`plugin/agents/test-driver.md` (GREEN step 6), `plugin/agents/refactor.md` (Step 6)
**Date**: 2026-09-26
**Mode**: review + fix

## Summary

The three applied edits match the prepared text in `item-2-5.md`, reflowed. The
contract was read across its surfaces: rule (`dispatch-composition.md` items 4
and 5), enforcers (`test-driver.md`, `refactor.md`), consumers
(`review-dispatch-template.md` §Report-only variant and §Field Rules,
`finishing.md` §1, `verify-step.sh`, `triage-feedback.sh`). Three seams found
and fixed; none blocks.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The report-only return has no consumer-side check for the end marker**
   - Location: `dispatch-composition.md` §Prompt contents item 5
   - Problem: item 5 says the report-only reviewer "returns its findings as text
     in parts" and the dispatching session writes them. The part protocol
     (`CONTINUED` / `END OF REPORT`) is defined only in the prompt the reviewer
     receives (`review-dispatch-template.md` §Report-only variant). The session
     that consumes the return, `finishing.md` §1, just "reads the findings it
     returns". Nothing on the consumer side tells the orchestrator to resume the
     reviewer for the next part, or to hold the write until the end marker. The
     template itself says a truncated report without the marker reads as a
     complete one, so the gate would file part 1 as the whole report.
   - Fix: item 5 now says the dispatching session resumes the reviewer by name
     for the next part while a part ends `CONTINUED`, and writes the parts to
     the assigned path only once one ends `END OF REPORT`. Item 5 is the one
     rule that `review-dispatch-template.md` and `finishing.md` defer to.
   - **Status**: FIXED

### Minor Issues

1. **`<group>` is not given a slug form, and the groups have none of their own**
   - Location: `dispatch-composition.md` §Naming and resumption
   - Problem: `<group>` was defined as "the artifact group `finishing.md` §1
     routed". The group labels there are "code/tests/plans", "skill
     definitions" and so on, and in `review-requirement.md` they are "Code,
     tests, plans". Taken literally they give a name with slashes or spaces, so
     `reports/review-code/tests/plans.md` would be nested. `triage-feedback.sh`
     only finds `review-*.md` at `-maxdepth 1`, so it would report no review
     artifact. The appositive inside the comma-separated name list also made
     the list hard to parse.
   - Fix: the definition is now in parentheses: "`<group>` a lowercase one-word
     slug for the artifact group `finishing.md` §1 routed, as in
     `review-skill`". `review-skill` is the example that
     `review-dispatch-template.md` §Example already uses.
   - **Status**: FIXED

2. **`refactor.md` states the pathspec form without its reason, next to "You start from a clean tree"**
   - Location: `plugin/agents/refactor.md` Step 6
   - Problem: `test-driver.md` gives the reason for `-- <paths>` ("so nothing
     staged before this dispatch rides along"), but `refactor.md` does not. Its
     paragraph opens with "You start from a clean tree", which makes repeating
     the paths look redundant, and an agent could drop them. A `CLEAN:` verdict
     from `verify-step.sh` still allows exempt dirt in any porcelain state,
     staged `.claude/handoff-*.md` included. Checked against the script's
     `exempt` pattern. This fails the agent-development criterion that the
     agent should get clear, specific instructions.
   - Fix: added "— a clean tree can still hold staged exempt dirt such as
     `.claude/handoff-*.md`, which a pathspec-less `git commit` would carry".
   - **Status**: FIXED

3. **`review-dispatch-template.md` §Field Rules restates the `<group>` definition instead of deferring to it**
   - Location: `review-dispatch-template.md` line 95–96
   - Note: it repeats "`<group>` being the artifact group `finishing.md` §1
     routed". It is not wrong, but it now lacks the slug clause that §Naming
     carries. Pointing only at `dispatch-composition.md` §Naming would keep one
     copy.
   - **Status**: OUT-OF-SCOPE — the file was committed under Item 2.4 and is not
     among the three files this review may edit. Flagged for the orchestrator.

## Surfaces read against each other

- **Commit form:** the rule is `dispatch-composition.md` item 4. The enforcers
  are `test-driver.md` GREEN step 6 and `refactor.md` Step 6. The consumer is
  `verify-step.sh`, whose KD-7 exemption comment relies on the pathspec commit.
  The orchestrator's own commits are `finishing.md` §1, `SKILL.md`:134 and
  `phase-boundary.md`:38. All of them state `git commit -- <paths>` and stage
  by name first. Staging first is still needed under pathspec semantics,
  because a pathspec commit refuses a path git does not know, so new files must
  be added. `artisan.md` has no commit text and takes the form from item 4.
  `tdd-slice.md` is OUT.
- **Return contract:** item 5 sets report path or `blocked:`, with UNFIXABLE
  inside the report. `corrector.md` §Edge Cases ("All issues unfixable … Return
  filename") agrees. `finishing.md` §1 greps UNFIXABLE in the report.
  `review-dispatch-template.md` §Example's closing line matches item 5. The
  report-only variant has the reviewer mark "UNFIXABLE:" in its findings, and
  those become the written report, so the grep reaches them. The
  `edify:refactor` exception matches `refactor.md` §Return Protocol.
- **Report path:** `review-<group>.md` matches `triage-feedback.sh`'s
  `review-*.md` exclusion and its review-artifact detection, now that `<group>`
  is a single slug. The structural proof in `finishing.md` §1 reads the path
  actually dispatched.

## Fixes Applied

- `dispatch-composition.md` §Naming and resumption: `<group>` is defined as a
  lowercase one-word slug, with `review-skill` as the example, in parentheses.
- `dispatch-composition.md` §Prompt contents item 5: the dispatching session
  resumes by name while a part ends `CONTINUED`, and writes the report only once
  a part ends `END OF REPORT`.
- `refactor.md` Step 6: added the reason for naming the paths, which is staged
  exempt dirt under a clean verdict.
- `just format` reflowed `dispatch-composition.md`. `just precommit` then
  passed: version consistency, tests (cached), rumdl, line limits, design
  links. It printed the `corrector.md` / `outline-corrector.md` /
  `design-corrector.md` oversized-file lines, which are OUT.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| inline M1 / KD-2 — `review-<group>` in §Naming | Satisfied | `dispatch-composition.md` §Naming and resumption |
| inline m15 / KD-2 — report path or `blocked:`; UNFIXABLE inside the report; report-only reviewer as second exception, returning in parts | Satisfied | `dispatch-composition.md` item 5 |
| orch m5 / KD-7 — `git commit -- <paths>` for committing dispatches and the orchestrator's review commit | Satisfied | item 4 ("in the same form" for the review commit); `test-driver.md` step 6; `refactor.md` Step 6 |
| Agent definitions against `plugin-dev:agent-development` | Satisfied for changed lines | Commit instructions are specific, second-person and carry their reason. Frontmatter is unchanged; the missing "When to invoke" sections predate this change and are not flagged |

**Gaps:** none.

## Positive Observations

- Item 4 covers the orchestrator's review commit with "in the same form"
  instead of a second statement, and `finishing.md` §1 matches it.
- `test-driver.md` states the reason for the pathspec next to the command, not
  just the command.
- The prepared text applied exactly as specified: every old string was
  replaced, and the only drift from the prepared text is `just format`'s reflow.
