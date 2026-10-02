# Item 2.2 — `plugin/skills/build/references/escalation.md`

Requirements: Majors 1, 2, 5; (a); m5, m6, m7.

## Changes per bullet

- **Exit-1 bullet (m5).** The lead-in now covers both arrivals ("after a step
  whose work is committed, or at the entry gate for its mask re-run"). The mask
  re-run stays first; "at the entry gate as after an item" is gone. At the entry
  gate the re-run's verdict goes back to `SKILL.md` §2, whose STOP governs it;
  "After an item, any other exit 1 → remediate" scopes remediation to a verdict
  after an item.
- **§Post-item remediation, KD-3's live-run chain.** Split out of the bullet as
  "Remediation after an item", opening with KD-3's premise (the gate held the
  tree clean before the item). Three numbered steps:
  1. Resume the named agent once with "Your dispatch left uncommitted work:
     finish it and commit it by name." The three skip cases (no named agent, a
     review dispatch, no edit tools) are kept.
  2. No owner, or no progress → a fresh dispatch composed from the item by
     `references/dispatch-composition.md`, carrying the dirt as a prior
     attempt's work. The context-free "recovery is mechanical" `edify:artisan`
     (sonnet) is gone.
  3. That fails → escalate with the listing and the dispatch's findings.
- **Closing paragraph.** "The agent that owns the dirt commits or reverts its
  own work … `git checkout -- . && git clean -fd` runs only where no agent owns
  the dirt" is replaced by KD-3: nothing reverts by default, the orchestrator
  never cleans up "on its own judgement" (narrowed from "in its own session"),
  the user decides escalated dirt path by path, and a decided revert is the
  one-call `git restore --source=HEAD --staged --worktree -- … && rm -- …`, with
  KD-3's `git status -z` and drop-the-empty-half rules and its probe note.
- **"Agent never returns" (m7).** The report written or the commit landed →
  treat the agent as returned and proceed. Neither → resume once; a resume that
  produces the report → proceed. Otherwise escalate.
- **§Resuming.**
  - The "invocation says so, or … reports/ already holds this run's reports"
    sentence is replaced by a pointer to `SKILL.md` §1's `item-*` test, plus
    KD-1's note that a finished job re-invoked reads as resumed and goes to §5.
  - The `tmp/build-baseline` paragraph is replaced: the base is the parent of
    the earliest commit adding an `item-*` report, printed by
    `scripts/changed-files.sh <job>` as `BASE:`; `NO-BASE:` means no item has
    landed yet, matching the script's exit 1.
  - Step 1 is the inventory from report history (`git log --format=%H --
    <report>`), never from subjects, plus KD-2's three boundary cases (absent,
    present-uncommitted-complete, partial) and the completeness rule against
    `edify:corrector`'s §4 template through `## Fixes Applied`. The phase
    boundary's own landed query is pointed at in `phase-boundary.md` rather than
    restated.
  - Step 2 is KD-3's examine-and-adopt with the tdd limit (no `-red.md` and
    `-test-review.md` on disk → implementation-side dirt escalates).
  - The old steps 3 and 4 (inventory; "§2 without the baseline capture and
    §3") collapse into step 1 and a step 3 that runs §3 and starts §4.

## Judgement calls for review

- **Resume step 2 stands in for `SKILL.md` §2's gate.** KD-3 adopts relevant
  dirt into the first remaining item's dispatch, but §2's gate STOPs on any
  dirt, so running §2 unchanged after adoption would refuse the run. Step 2
  therefore runs `verify-step.sh` as §2's gate with one change, dirt examined
  rather than refused; the mask re-run and every other verdict are §2's.
- **`PRECOMMIT:` in the live-run chain.** KD-3's resume message names
  uncommitted work only; the old message also covered precommit failures. Step
  1 adds that on a `PRECOMMIT:` verdict over a clean tree the message carries
  the failing output and asks for the fix, committed by name.
- "the user", not "my human partner", is the file's existing voice and is kept.

## Cross-references left for later items

- `phase-boundary.md` states the boundary's landed query and the base
  resolution: Item 2.3, next in this run.
- `../../fragments/escalation-acceptance.md` §Dirty tree recovery still
  restates the old procedure and §Rollback still prescribes
  `git checkout -- .`: Item 2.8.
- `dispatch-composition.md` §Naming and resumption does not yet name
  `item-N-M` as §4.1's self-review report, which the inventory relies on: Item
  2.6.
- `plugin/README.md` and `docs/` mention of the removed artisan fallback, if
  any: Items 2.11, 2.14.

## Verification

`just precommit` green after `rumdl fmt`. 79 lines before, 131 after.
