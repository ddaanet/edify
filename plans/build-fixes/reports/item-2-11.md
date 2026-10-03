# Item 2.11 — `plugin/README.md` §Scripts

Requirements: m17.

## Changes per bullet

- **`verify-step.sh` call sites (m17).** The one-sentence paragraph listing
  "GREEN, code review and general items" became the first of three bullets
  under "Plus three in `skills/build/scripts/`, used by `/build`". The call
  sites now listed are:
  - the entry gate;
  - a slice's GREEN and its code-review commit;
  - a delegated general item;
  - a review item;
  - an item done in session (`/build` §4.1);
  - the phase-boundary commit;
  - the review gate;
  - the run's closing commit (`skills/build/references/finishing.md` §3).

  "Never after a RED or a test review" is kept.
- **`changed-files.sh` and `exempt-paths.sh` added.**
  - `changed-files.sh`: prints the run's base as `BASE:`, then the committed
    diff from that base to `HEAD`, minus the exempt paths and `plans/<job>/`.
    `--phase` takes the phase base. The phase-boundary and review-gate scopes
    and the triage base come from it. This is checked against the script's
    header comment and `phase-boundary.md`, `finishing.md` §1 and §2.
  - `exempt-paths.sh`: sourced by the other two, never run. It is the one
    definition of the three paths dirty by convention, which the gate tolerates
    and the list drops. This is checked against its header comment.

## Judgement calls for review

- **Two call sites beyond the item's list.**
  - The entry gate: `SKILL.md` §2 runs the script, and so does
    `escalation.md` §Resuming step 2 on resume.
  - The delegated general item: `SKILL.md` §4.4's "any general item", which
    the old README named as "general items".

  The item lists "every committing dispatch". These two are call sites
  `SKILL.md` names, and leaving them out would make the list incomplete in a new
  way. The list-revision commit is not listed: `SKILL.md` §4.4 does not run the
  gate after it (`item-2-7.md` noted this).
- **"Committing step", not "committing dispatch".** §4.1's commit, the
  phase-boundary commit, the review gate and the closing commit are made by the
  orchestrator, not by a dispatch. `SKILL.md` §4.4 says "every step whose work
  is committed".
- **No claim that every review scope comes from `changed-files.sh`.** `/build`
  §4.1's corrector reviews uncommitted work with the working-tree form
  (`review-requirement.md` §Execution Context, as Item 2.9 left it). So the
  bullet names the phase-boundary and review-gate scopes only.
- **Path form.** `skills/build/...`, plugin-relative, as the README already
  writes it.

## Cross-references left for later items

- None for `plugin/`. `docs/references/pipeline-contracts.md`'s D-86 sentence
  ("which tolerates nothing but ` M memory`") is Item 2.12's.

## Verification

- `just format`, then `just precommit` green: version consistency, cached
  tests, line limits (only the three allowlisted correctors reported), design
  links.
- Self-review of the uncommitted diff against Item 2.11's two bullets. Call
  sites were read against `SKILL.md` §2 and §4.4, `phase-boundary.md` §Commit,
  `finishing.md` §1 and §3, `tdd-slice.md` §After the slice and `escalation.md`
  §Resuming. Script descriptions were read against the three scripts' header
  comments.
- 81 lines before, 93 after (`wc -l`, after `rumdl fmt`).
