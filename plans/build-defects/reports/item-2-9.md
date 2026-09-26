# Item 2.9 — `plugin/fragments/delegation.md`

Status: **applied.**

Requirements: inline m2.

## Per bullet

- **§Multi-Step Verification, Correct pattern (inline m2).** The section
  prescribed `git status --porcelain && just lint` as the correct pattern, on
  the claim that compound commands "can't be partially executed — both run or
  neither". It now says one script owns the whole verdict, `/build`'s
  `verify-step.sh`, which checks the tree, then runs `just precommit`, and names
  which check failed (its `DIRTY:` and `PRECOMMIT:` outputs, checked against
  the script). It says why the compound fails, as the item requires:
  `git status --porcelain` exits 0 on a dirty tree too, so `&&` guards nothing;
  the lint runs either way and a dirty tree reads as a pass. The false
  "both run or neither" claim is gone.
- **Named by skill, no new repo-relative path.** The script is "`/build`'s
  `verify-step.sh`", not `plugin/skills/build/scripts/verify-step.sh` as the
  finding's fix text had it; the item's own constraint overrides the fix text.

## Judgement calls

- **The Anti-pattern paragraph is kept as is.** It describes splitting the
  checks across tool calls, which the one-script pattern also answers, and it
  names `just lint` rather than `just precommit`. The item names only the
  correct pattern; the anti-pattern's `just lint` is left, and the new
  sentence quotes the compound in that same form so the two paragraphs read as
  one argument.
