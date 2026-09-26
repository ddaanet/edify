# Review: Item 2.5 agent-definition half — pathspec commits in test-driver and refactor

**Scope**: `git diff f44ddbbf89c4bea2ffa49a0fdfdd961cbe167474` over
`plugin/agents/test-driver.md` (GREEN step 6) and `plugin/agents/refactor.md`
(Step 6), committed in `cc99d225`
**Date**: 2026-09-26
**Mode**: review + fix (no fixes were needed; resumed after the refused call
to apply the loaded agent-development criteria)

## Refused tool call — review stopped here

One tool call was refused, and under the dispatch constraint the review stopped
there.

- **Call:** a Bash probe in a throwaway `mktemp -d` repository, not the edify
  tree. It was meant to confirm empirically that `git commit -m x -- <paths>`
  handles a rename, a deletion and a new file and leaves pre-staged dirt out of
  the commit. The probe seeded the scratch repo with `git add .`.
- **Refusal:** the project `PreToolUse:Bash` hook refused it because it
  contained `git add .`. The hook's message was "Stage the paths you mean
  (`git add <path>...`), or `git add -u` for already-tracked files only". The
  hook blocked the command before it ran, so nothing executed.
- **Consequence:** I made no retry in any form. The review stopped before I
  loaded the `plugin-dev:agent-development` skill or ran the recall step.
- **Resumption:** the orchestrator (`build-leg6`) confirmed the stop was correct
  and told me not to re-run the probe in any form. It asked me to load
  `plugin-dev:agent-development` and apply its criteria, which I did. The
  results are under §Agent-development criteria below. Nothing failed, so I
  applied no fixes and the constraint did not call for `just precommit`.
- **What the probe would have added:** empirical confirmation of the
  rename/delete case (Minor 1 below). The finding rests on git's documented
  `--only` semantics, not on an observed run.

## Summary

Both commit instructions now stage by name and commit with
`git commit -- <paths>`, naming the paths they staged. That is the form in
`dispatch-composition.md` §Prompt contents item 4. The two agents agree with
each other and with the rule. Each gives its reason next to the command:
test-driver says "nothing staged before this dispatch rides along", and refactor
says staged exempt dirt survives a clean verdict. I found no issues.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Pathspec commit over a rename or deletion (checked, not a defect)**
   - Location: `refactor.md` Step 6 code block
   - Note: a refactoring can move or delete files, and then
     `<the files you changed>` includes paths that are gone from the worktree.
     `git commit -- <paths>` runs in `--only` mode. That mode matches the
     pathspec against the index with HEAD overlaid, so a path that was deleted
     or renamed away still matches. Staging by name first handles the new side
     of a rename, which a pathspec commit would otherwise refuse as unknown to
     git. So the instruction as written covers moves and deletes.
   - **Status**: OUT-OF-SCOPE — informational only; nothing to change. The
     empirical probe that would have confirmed it was the refused call.

## Surfaces read against each other

- **Rule:** `dispatch-composition.md` item 4 says a committing dispatch stages
  the paths it names, its own report among them, never `git add -A`, and then
  commits with `git commit -- <paths>`, naming the paths it staged.
- **Enforcers:**
  - `test-driver.md` GREEN step 6 stages by name the tests, the implementation,
    and the RED, test-review and GREEN reports, then runs
    `git commit -m "<subject>" -- <the same paths>`. That matches item 4.
  - `refactor.md` Step 6 runs `git add` and `git commit … --` over the same two
    path groups, its report among them. That matches item 4.
- **Consumer:** `verify-step.sh` KD-7 treats staged exempt dirt as clean. That
  dirt stays staged after a pathspec commit, so the post-commit verdict is
  unchanged. Nothing the consumer relies on goes unchecked on the enforcer side.
- **Each other:** both agents give `-m` before `--`, name the staged paths, and
  forbid or leave out `git add -A` / `git add .`. Neither names a commit hash in
  its report, which is consistent with item 5.
- The Item 2.5 per-item review settled the missing reason in `refactor.md`.
  That text is present and accurate: `.claude/handoff-*.md` matches the KD-7
  exemptions, and "such as" covers the `memory` gitlink and `inbox/*.md`.

## Agent-development criteria

I loaded the `plugin-dev:agent-development` skill and applied its criteria to
`test-driver.md` GREEN step 6 and `refactor.md` Step 6. Frontmatter criteria
(name, description and triggers, model, color, tools) cover lines that this
change does not touch, and those lines are OUT.

| Criterion (skill §System Prompt Design) | test-driver GREEN step 6 | refactor Step 6 |
|---|---|---|
| Second person, addressing the agent | Pass — imperatives ("Stage by name…", "Commit with…") | Pass — "You start from a clean tree…", then imperatives |
| Specific, not vague | Pass — names each path group and the exact command form | Pass — a literal command block with the full path list after `--` |
| Step-by-step process | Pass — stage, commit, return, in order, within the numbered GREEN list | Pass — write report, stage, commit, as sequenced prose plus a code block |
| Edge cases addressed | Pass — says why pre-staged files stay out ("nothing staged before this dispatch rides along") | Pass — says staged exempt dirt survives a clean verdict; renames and deletes are covered by the `--only` semantics (Minor 1) |
| Output format defined | Pass — "Return the report path." | Pass — defined in the unchanged §Return Protocol |
| Quality standards / boundaries | Pass — forbids `git add -A` / `git add .`, and says the commit never leaves the suite red | Pass — a separate commit, and the slice commit is never amended (the unchanged Goal line) |
| Under 10,000 characters | Not applicable — the edit adds a few lines to a body whose size is OUT | Same |

Neither section fails a criterion.

## Fixes Applied

None. Neither the reading review nor the loaded agent-development criteria
turned up anything to fix.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| orch m5 / KD-7 — test-driver GREEN step 6 stages by name, commits `git commit -- <paths>` | Satisfied | `test-driver.md`:99–104 |
| orch m5 / KD-7 — refactor Step 6 stages by name, commits `git commit -- <paths>` | Satisfied | `refactor.md`:175–186 |
| Never `git add -A` / `git add .` | Satisfied | `test-driver.md`:101–102 forbids both; `refactor.md` code block uses named paths only |
| Matches `dispatch-composition.md` §Prompt contents item 4 | Satisfied | Both name the paths they staged, with the report among them |
| `plugin-dev:agent-development` criteria on the changed sections | Satisfied | Skill loaded after resumption; every applicable criterion passes (§Agent-development criteria). Frontmatter, tools and triggers are unchanged and OUT |

**Gaps:** none.

## Positive Observations

- Each command carries its reason, so an executor that reads "clean tree" has no
  grounds to drop the pathspec.
- `refactor.md` repeats the full path list after `--` rather than a
  placeholder like "the same paths". An agent can copy that command block
  directly.
