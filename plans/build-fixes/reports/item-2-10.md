# Item 2.10 — `plugin/agents/tdd-auditor.md` §Inputs

Requirements: m15.

## Changes per bullet

- **§Inputs, the term (m15).** "Phase checkpoints: `phase-P-corrector.md`"
  became "Phase boundaries: `phase-P-corrector.md`", the term `SKILL.md` §4.5
  and `phase-boundary.md` use.
- **Subject matching, KD-8's form.** The auditor's two subject-matching rules
  are in §Per-Slice Checks check 2, not in §Inputs. Both now take KD-8's
  `<job> Item N.M/k`:
  - "so `Item N.M/k` is the only thing you may match in a subject" became
    `<job> Item N.M/k`.
  - "two commits bearing the `Item N.M/k` marker" became `<job> Item N.M/k`.
  This is the site `item-2-6.md` handed to Item 2.10 or 2.13
  (`tdd-auditor.md:96`).

## Judgement calls for review

- **The marker-bearing commit count.** Check 2 said a reviewed slice carries
  two marker-bearing commits (GREEN and the code-review commit), and that any
  marker-bearing commit no report accounts for is a violation. KD-8 and Item
  2.7 now put the marker on the list-revision commit too
  (`<type>: <job> Item N.M/k — list revision`, `tdd-slice.md` §After the slice
  step 3). That commit carries `runbook.md` alone and no report. Read as
  written, the auditor would flag every list revision as a violation. The
  refactor commit already bore the marker under `refactor.md`'s old subject; it
  has its own report and its own check 4. The paragraph now says two more
  commits may follow, and neither is a split: the refactor commit (check 4) and
  the `runbook.md`-only list revision. The violation is now a marker-bearing
  commit that neither a report nor such a list revision accounts for. I count
  this under "any subject matching it prescribes takes KD-8's form", because
  the match is only correct if it knows every commit KD-8 labels. It goes
  beyond a word swap, so it is flagged here.
- "Nothing mechanical keys on the subject" (KD-8) stays true: the auditor is an
  agent reading labels, and it resolves every slice commit from its report's
  adding commit, never from a subject (§Inputs, check 2).

## Cross-references left for later items

- `plugin/agents/refactor.md` Step 6's subject `refactor: Item N.M/k — …`:
  Item 2.13 gives it `<job>`. The refactor commit this file now names as
  marker-bearing assumes that form.
- `docs/design.md:232-240` still records `<type>: Item N.M/k — <title>` and says
  the marker "is the only thing `tdd-auditor` may match in a subject"
  (`item-2-6.md` flagged it). Item 2.14 records KD-8; the hub line needs the
  `<job>` form too.

## Verification

- `just format`, then `just precommit` green: version consistency, cached
  tests, line limits (only the three allowlisted correctors reported), design
  links.
- Self-review of the uncommitted diff against Item 2.10's bullet and KD-8, and
  against `tdd-slice.md` (GREEN subject, §After the slice steps 1–3),
  `dispatch-composition.md` §Prompt contents item 4 and §Naming and resumption,
  and `finishing.md` §3.2.
- 219 lines before, 222 after (`wc -l`, after `rumdl fmt`).
