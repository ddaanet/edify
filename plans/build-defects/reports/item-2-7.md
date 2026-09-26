# Item 2.7 — `plugin/fragments/review-requirement.md`

Status: **applied.**

Requirements: orch C1.

## Per bullet

- **§Execution Context, Changed files (orch C1, KD-1).** The field read
  "Explicit file list (from `git diff --name-only` or known from
  implementation)". It now reads: an explicit file list, from
  `git diff --name-only <base>` against the base commit of the run or phase
  under review, never a bare `git diff --name-only`, which compares the working
  tree to the index and is empty once the work is committed. "Must not be
  empty" is kept. This is the inherited copy of the bare command the finding
  cites; `/build`'s own sites (`phase-boundary.md`, `finishing.md` §1) already
  diff against a base.

## Judgement calls

- **"recorded base" not used.** The outline item and the finding's fix text
  both say "the run's or phase's recorded base commit". KD-1 says a phase's base
  is "resolved from its predecessor's corrector report, not stored", so
  "recorded" is true of the run's base (`tmp/build-baseline`) and false of a
  phase's. Per the KD-wins rule the text says "the base commit of the run or
  phase under review", which covers both without implying a stored phase base.
- **"or known from implementation" dropped.** The finding's fix text drops it,
  and it was the escape that let a list be assembled without a base at all.
- **No pointer to `/build`.** The fragment is generic; naming
  `phase-boundary.md` would add a repo-relative path to a file that is not
  `/build`-specific. The reason clause (index comparison, empty after commit)
  carries why the bare form fails.

## Noticed, not changed

- §Proportionality's self-review process still says "Run `git diff HEAD`",
  which is empty once the item is committed, the same failure in another field.
  Outside the named section.
