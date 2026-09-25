# Item 2.3 — `plugin/skills/build/references/finishing.md`

Status: **applied.**

Requirements: inline m10, m11, m12, M3 (second half), m6. Plus the authorized
carry-forward to `plugin/skills/build/SKILL.md` §2.

## Per bullet

- **§1 scope (m10).** "the uncommitted changes for that artifact group" became
  "that artifact group's share of step 1's list". Step 1 is the
  `git diff --name-only "$(cat tmp/build-baseline)"` line, so the scope is the
  KD-1 review-gate base rather than an empty working-tree diff.
- **Structural proof (m11, KD-2).**
  - UNFIXABLE is now validated by `../../fragments/review-requirement.md`
    §UNFIXABLE Detection Protocol before the stop, and only the ones that hold
    stop the run. The protocol's own checks are not restated; the pointer lands
    on the section that lists them and says what to do when one fails.
  - A new **Report-only re-dispatch** paragraph, placed before the structural
    proof so the Read covers the report after the second pass: a group whose
    fixes this session applied is re-dispatched once to its reviewer, citing
    `/build` §4.1 as the reason.
- **After the report commit (m12, KD-1).** The commit paragraph now covers
  fixes applied by the reviewer or by this session, and commits with
  `git commit -- <paths>` (KD-7). It is followed by a `verify-step.sh` block;
  exit 0 goes to §2, anything else to `references/escalation.md` §Post-item
  remediation, and §2 waits for exit 0.
- **§2 (M3 second half, KD-3).** `WARNING: No corrector report` is surfaced
  inline and investigated before §3. Checked against `plugin/bin/triage-feedback.sh`:
  the warning fires when `review_artifact` is `none`, i.e. no `review.md` and no
  `review-*.md`, which includes `review-skip.md`; the text says so. "match or
  no-classification" now proceeds silently only with no warning.
- **Planning-artifact paragraph (m6).** Kept unchanged; it is the one copy.
  Item 2.4 replaces the template's duplicate with a pointer here.

## Carry-forward — `SKILL.md` §2

"Section 4 and `references/phase-boundary.md` call the same one" became "Section
4 and `references/finishing.md` §1 call the same one". Checked by `rg`:
`verify-step.sh` is now run at SKILL.md §2, §4.4 and `finishing.md` §1;
`phase-boundary.md` no longer runs it (Item 2.2), and `escalation.md` names it
without running it. Nothing else in SKILL.md was touched.

## Judgements

- **What happens to the re-dispatch's findings.** KD-2 says "re-dispatched
  once" and does not say what the second pass's findings become. Settled as:
  add them to the same `review-<group>.md` (the structural proof reads one path
  per group) and apply them, with no further pass — "once" is the cap. The
  second pass's own fixes are therefore not reviewed by another agent; that is
  what "once" accepts.
- **The re-dispatch's name.** Not given. `dispatch-composition.md` §Naming gets
  `review-<group>` in Item 2.5; whether a second dispatch of the same group
  reuses that name was left unsaid rather than invented.
- **Non-zero verify exit.** KD-1 says only that exit 0 is required before §2.
  Routing any other exit to `escalation.md` §Post-item remediation is the one
  remediation `/build` has; the sandbox instruction is not repeated here,
  because SKILL.md §2 already states it for every call site.

## Left undone

Nothing within the item.
