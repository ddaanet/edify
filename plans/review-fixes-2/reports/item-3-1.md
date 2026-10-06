# Item 3.1 — build-run-state: triage measures the review gate's list

Targets: `docs/references/build-run-state.md`, `docs/decisions.md`.
Requirements: C1, M1, M2, m2, m3, m9, m11, m19. Depends on: Item 1.1 (landed).
`craft:design-doc-writing` loaded (SKILL.md, `maintaining-entries.md`,
`writing-style.md`).

## Edits — `docs/references/build-run-state.md`

### D-90 — conclusion and body (C1, M1, m3)

- Conclusion now ends "… and one script produces it, for the phase boundary,
  the review gate and triage alike", matching the index line.
- Exit codes: `NO-BASE:` (exit 1) is stated for "a repo with commits and no
  committed item report"; usage error or git failure exits 2 with `ERROR:`,
  and an unborn `HEAD` is a git failure, exit 2, never `NO-BASE:` (m3).
  Checked against `changed-files.sh`: `git log` on an unborn repo fails and
  takes the `ERROR: git log failed` exit 2 branch; pinned by
  `tests/test_changed_files.py::test_git_failure_is_error_not_no_base`.
- Removed: triage "takes the script's `BASE:` as its argument and whose two
  diffs take the same `<base> HEAD` form".
- Added: triage, `plugin/bin/triage-feedback.sh <job>`, takes no base, runs
  the script itself and counts its list (the set the review gate reviewed).
  Files changed is the length of the list; behavioural code is read from the
  `<base> HEAD` diff of those paths only, as literal pathspecs. The report
  count looks past the list: reports `<base> HEAD` adds directly under
  `plans/<job>/reports/`, excluding the `item-<N>-<M>.md` report every item
  leaves and the review reports (`review.md`, `review-*.md`,
  `final-review.md`); slice, refactor and phase-boundary reports count;
  planning reports before the base fall outside the range. A `NO-BASE:` or
  `ERROR:` from the script stops triage with exit 2 and no log row. Each
  clause checked against `plugin/bin/triage-feedback.sh` lines 18–133 and
  `finishing.md` §2.

### D-90 — Limitation paragraph (m2)

New paragraph after D-90: the base query and `<base> HEAD` range read the job
branch as linear; a merge of `main` into the job branch, or another session
committing on the branch, puts non-run commits into the range and their paths
into the list; a report added only in a merge commit is invisible to the base
query, which gives `NO-BASE:`; frequency unmeasured.

The merge-commit claim was probed before recording (git 2.47.3, scratch repo
under `$TMPDIR`): an `item-1-1.md` added only in a `--no-ff` merge commit,
then the D-88 query
`git log --no-renames --diff-filter=A --reverse --format=%H -- ':(glob)plans/j/reports/item-*'`
printed nothing. The paragraph cites "probed on git 2.47.3".

### D-91 — `sandbox-lies` is optional (m9)

"A listing the `sandbox-lies` hook annotates" became "A listing annotated as
sandbox masks", followed by: the annotation comes from the `phantom-untracked`
detector of the optional `sandbox-lies` plugin's Bash hook; without that plugin
no listing is annotated, so the re-run never fires, and a masked listing reads
as dirt. Wording as `escalation.md`'s exit-1 bullet and `plugin/README.md`.

### D-92 — committed case and revert operand (M2, m19)

- Revert operand: `-- <paths>` became `-- <tracked or indexed paths>`, as
  `escalation.md` §Post-item remediation writes it.
- Added the committed case per `escalation-acceptance.md` §Rollback protocol:
  a failed fix already committed is not reverted by default; it escalates with
  the commits since the last clean commit before the failed item and what the
  attempt found; only the commits my human partner decides to revert are
  reverted, newest first, `git revert --no-commit <sha>`, then the reverted
  paths committed by name with subject
  `<type>: <job> Item N.M[/k] — revert failed fix`; never `git reset`.
- Conclusion unchanged ("nothing reverts by default" already covers both).

### D-93 — skill-row wording (m11)

The `review-skill` parenthetical now carries `dispatch-composition.md`
§Naming and resumption's words verbatim: "skill definitions and the
agent-instruction prose they load, meaning their `references/` nodes and the
shared instruction files a skill loads from outside itself. An instruction
file no skill loads, such as `CLAUDE.md` or `.claude/rules/*.md`, matches no
row and takes the `review-code` default".

### Rejected alternatives

Added, after the prose-copy entry: "**Triage keeping a base argument and
filtering the raw diff itself** — a second copy of the list's filters, which
drifts from the script's as a prose copy does (D-90)."

## Edits — `docs/decisions.md` §Build run state

- D-90 index line: "… and one script produces it, for the phase boundary, the
  review gate and triage alike."
- *Rejected* line: added "triage keeping a base argument and filtering the raw
  diff itself" after the prose-copy alternative.

No outline KD label is cited in either file.

## Verification

- `just format` reflowed both files; measured after: `build-run-state.md` 220
  lines, `decisions.md` 213 lines (both under 400).
- `just precommit`: Precommit OK — version consistency, 403/404 passed with 1
  xfail, line limits, design links (94 decisions indexed, defined once,
  conclusions match, 9 nodes present). The three `oversized-file` lines
  (`corrector.md`, `outline-corrector.md`, `design-corrector.md`) are files
  this item does not touch.
