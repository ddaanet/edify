# Item 2.11 — plugin/README.md: sandbox-lies, verified commits, triage's list

Target: `plugin/README.md`. Requirements: C1, M1, m9, m13. Depends on: Item
1.1 (landed).

## Edits

All three sit in §Scripts, in the list of `skills/build/scripts/`.

### `verify-step.sh` bullet — call sites (m13)

Was: "a slice's GREEN and its code-review commit, a delegated general item, …".

Now: "a slice's GREEN, its code-review commit, its refactor commit and its
list-revision commit, a delegated general item, …". This matches `SKILL.md`
§4.4 ("a slice's GREEN, its code review, its refactor and its list revision")
and `tdd-slice.md` §After the slice steps 2 and 3, which each end at §4.4. The
"Never after a RED or a test review" sentence stays.

### `verify-step.sh` bullet — `sandbox-lies` as an optional dependency (m9)

Added, after the call sites:

> A `DIRTY:` listing annotated as sandbox masks is re-run once rather than
> remediated; the annotation comes from the `phantom-untracked` detector of the
> optional `sandbox-lies` plugin's Bash hook. Without that plugin no listing is
> annotated, so the re-run never fires, and a masked listing reads as dirt.

Named as `escalation.md` §Post-item remediation's exit-1 bullet names it:
`phantom-untracked` is a detector run by the plugin's Bash hook, not a hook of
its own. The consequence is Item 2.3's, in the same words. Placed in the
`verify-step.sh` bullet rather than a new "Optional dependencies" section: the
README lists no other optional plugin (`plugin-dev`, `craft`), so a section
holding `sandbox-lies` alone would read as the complete list.

### `changed-files.sh` bullet — triage reads the list (C1, M1)

Was: "The phase-boundary and review-gate scopes and the triage base come from
it."

Now:

> The phase-boundary and review-gate scopes come from it, and
> `triage-feedback.sh <job>` runs it itself and measures that list, the set the
> review gate reviewed: its file count, and behavioural code in those paths'
> diff only. The report count alone looks past the list, at the reports the
> `<base> HEAD` range adds under `plans/<job>/reports/`, which the list drops
> with the job's record.

Checked against `plugin/bin/triage-feedback.sh` as landed by Item 1.1: it calls
`../skills/build/scripts/changed-files.sh "$job_dir"`, counts the list's lines
for Files changed, limits the behavioural-code diff to the list's paths, and
counts reports over `"$baseline_commit" HEAD -- ":(glob)$reports_dir/*"`. It
agrees with `finishing.md` §2 ("It takes no base: it runs `changed-files.sh
<job>` itself and measures that list, the set §1 reviewed"). No outline
decision label is cited.

## Verification

- `just precommit`: `Precommit OK` (version consistency, tests cached, line
  limits, design links). No reflow beyond the edit; the file is 102 lines. The
  three `oversized-file` lines it prints (`corrector.md`,
  `outline-corrector.md`, `design-corrector.md`) are files this item does not
  touch.

## Surfaces outside scope

- `docs/references/build-run-state.md` D-90 still says triage "takes the
  script's `BASE:` as its argument", and D-91 names "the `sandbox-lies` hook"
  without saying it is optional; both are Item 3.1's.
- The README names neither `plugin-dev` nor `craft`, which
  `review-dispatch-template.md` treats as optional too. Not in this item's
  scope; reported, not changed.
