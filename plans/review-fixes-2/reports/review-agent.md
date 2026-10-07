# Review: review-fixes-2 Item 2.5 — `tdd-auditor.md` hosting file

**Scope**: `plugin/agents/tdd-auditor.md`,
`git diff 888eda7a312e962a28ba59c2695eecd5f34c6e14 HEAD`, read against
`plugin/skills/build/references/finishing.md` §3 step 2,
`dispatch-composition.md` §Prompt contents item 2 (both as on disk, uncommitted),
`tdd-slice.md` §After the slice step 3, `SKILL.md` §1, and outline KD-7 /
Item 2.5.
**Date**: 2026-10-06
**Mode**: review + fix

## Summary

The commit puts the hosting file in place of `runbook.md` at every place the
outline's Item 2.5 enumerates, plus the opening paragraph, description and Tool
Usage. Two seams with the `/build` side were open. §Inputs said the dispatch
does not name the hosting file, while `finishing.md` and
`dispatch-composition.md` now say the prompt names it. And §Inputs' git bullet
limited git to "only" report resolution and diffing, which shuts out the
list-revision history that the agent's own first bullet, check 2 and §List
revisions recorded all depend on. Both are fixed. `just precommit` is green.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **§Inputs contradicts the dispatch contract on who names the hosting file**
   - Location: `plugin/agents/tdd-auditor.md:44-46` (pre-fix)
   - Problem: the agent said "The dispatch does not name it" and derived the
     file itself. `finishing.md` §3 step 2 says "the hosting file, which the
     prompt names", and `dispatch-composition.md` §Prompt contents item 2 says
     the `tdd-audit` prompt names "the hosting file and its history". The
     agent's derivation also attributed a design-before-outline precedence to
     `/build` §1. §1 lists "`design.md` or `outline.md`" and sets no order
     between them.
   - Fix: "The dispatch names it." The fallback for a prompt that omits it is
     kept, as the review-skill gate suggested, and follows §1 as written:
     `runbook.md` where it exists, otherwise the plan's `design.md` or
     `outline.md`. Where both of those exist and there is no runbook, the agent
     returns `blocked: hosting file not named` and does not guess. This matches
     the agent's existing §Edge Cases, which also returns `blocked:` when an
     input is missing.
   - **Status**: FIXED

2. **§Inputs' git bullet excludes list-revision history**
   - Location: `plugin/agents/tdd-auditor.md:57-59` (pre-fix)
   - Problem: "Git history, used only to resolve a report to its adding commit
     and to diff that commit". Check 2 must account for list-revision commits
     that touch the hosting file alone, and §List revisions recorded reads them
     from the hosting file's history. "Only" forbids both. `finishing.md` §3
     step 2 lists three uses: report resolution, diffing, and "to read the
     hosting file's list-revision commits".
   - Fix: the third use is added with its command,
     `git log -- plans/<job>/<hosting file>`. The ban on discovering slice
     commits by subject search stays.
   - **Status**: FIXED

### Minor Issues

None.

## Fixes Applied

- `plugin/agents/tdd-auditor.md` §Inputs, first bullet: the dispatch names the
  hosting file. The fallback follows `/build` §1's actual order and returns
  `blocked: hosting file not named` when `design.md` and `outline.md` both exist
  with no runbook.
- `plugin/agents/tdd-auditor.md` §Inputs, git bullet: reading the hosting file's
  list-revision commits is added as a permitted use, with its `git log`
  pathspec form.
- `just precommit`: green, run in the foreground. The first run failed on a
  rumdl reflow of my own edit, which I fixed with Edit (not `just format`, so
  other groups' uncommitted files were not touched). The three
  `oversized-file:` lines (`corrector.md`, `outline-corrector.md`,
  `design-corrector.md`) are allowlisted and print on every green run. They are
  not in this file. `tdd-auditor.md` is at 229 lines, under the 400-line cap.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| M5 / KD-7: list revision lives in the hosting file (`runbook.md`, or routed `outline.md`/`design.md`) | Satisfied | §Inputs first bullet (wording matches `tdd-slice.md` §After the slice step 3) |
| KD-7: the list-revision commit takes the hosting file alone; auditor accounts for it | Satisfied | check 2, list-revision paragraph |
| KD-7: auditor reads list revisions from that file's history | Satisfied | §Inputs git bullet (post-fix), §List revisions recorded, report template `## List Revisions` hint |
| Item 2.5 enumerated places: §Inputs, check 2, §List revisions recorded, `Runbook:` line, `## List Revisions` hint | Satisfied | all five changed; also the opening paragraph, description, example context and Tool Usage |
| Agreement with `finishing.md` §3 step 2 / `dispatch-composition.md` item 2 | Satisfied (post-fix) | Major 1 and 2 |

**Gaps:** none.

## Agent-definition criteria (`plugin-dev:agent-development`, installed)

- Frontmatter: `name`, `description`, `model`, `color` and `tools` are all
  present and valid. The identifier is lowercase-hyphenated.
- Description: it states the trigger (after a plan's tdd items complete) and has
  two `<example>` blocks with commentary. The change from "runbook" to "plan" is
  correct, because tdd items can come from a routed design or outline.
- Tools: `Read`, `Write` and `Bash`. This is the minimum set: Read for the
  hosting file and reports, Bash for git and `rg`, Write for the report. The
  change needs no new tool.
- System prompt: written in second person and structured as Inputs, checks,
  Report, Edge Cases and Tool Usage. The body is 9345 characters, under the
  skill's 10,000-character ceiling.

## Positive Observations

- The hosting-file wording quotes `tdd-slice.md` §After the slice step 3
  word for word ("`runbook.md`, or the `outline.md` or `design.md` routed to
  `/build`"), so the rule and the enforcer agree on terms.
- In check 2, a marker-bearing commit accounts for itself only as a list
  revision "touching the hosting file alone". That is the enforcer checking
  exactly what KD-7's commit form produces (`git commit -- plans/<job>/<hosting
  file>`).
- The report template's `**Hosting file:**` line lists the three possible
  hosts and does not presume a runbook.

## Recommendations

None.
