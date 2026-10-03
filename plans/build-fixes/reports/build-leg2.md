# build-fixes — leg 2 report

Leg 2 picks up from `build-leg1.md`, which stopped on the Item 2.3 question. It
ended at a clean tree at HEAD `88ef264e`. The delegate's context was recycled
while Item 1.4 slice 4 was still open: its GREEN is committed and its code
review has not run.

## Resume point

**Item 1.4, slice 4, dispatch (d): code review.** RED, test review and GREEN are
committed. The next steps, in order:

1. Dispatch `edify:corrector` (opus) for the code review. Scope IN:
   `plugin/skills/build/scripts/verify-step.sh`, which the slice did not change.
   The question is whether the `core.quotePath` fix and the test that now pins
   it agree. Write the report to
   `plans/build-fixes/reports/item-1-4-s4-code-review.md`.
2. Commit that report together with any fixes it made:
   `fix: Item 1.4/4 — code-review fixes`, using `git commit -- <paths>`. Then
   run `verify-step.sh`.
3. Item 1.4 is then complete. Go to Item 2.3 (see below), then 2.4 to 2.15, then
   §5 Finish.

## Governing rules

- The skill text that governs is `plugin/skills/build/` at `d415f22d`. Read it
  with `git show d415f22d:plugin/skills/build/<file>`. A frozen copy also sits
  at `/tmp/claude-1000/build-rules/`, but it is session-scoped and may be gone.
  The Skill tool loads a stale `dist/` copy, so do not use it (leg 1 deviation
  1). Do not re-read the live `plugin/skills/build/`: this job is rewriting it.
- `tmp/build-baseline` holds `d415f22daf94eb5ae5424a927e126f4010ff7a21`.
- Dispatches are unnamed, per the coordinator, so resume them by agent id.
- **`.claude/handoff-todo.md` is staged by the main session.** It is not part of
  this job. Every commit uses `git commit -m … -- <paths>`, which keeps it out.
  Never unstage it, reset it or commit it. `verify-step.sh` exempts it.
- The pre-existing untracked
  `inbox/brief-corrector-reads-surfaces-against-each-other.md` and the zero-byte
  `.claude/*` sandbox masks stay untouched.

## Answers from my human partner this leg

1. **Item 2.3's question: a variant of option 1.** A new Item 1.4 (tdd),
   `changed-files.sh <job> --phase`. Its base is the latest commit in
   `<run base>..HEAD` touching `plans/<job>/reports/phase-*-corrector.md`. That
   is KD-2's path rule, never the commit subject, per KD-8. When nothing
   matches, the base is the run base. Without `--phase` nothing changes. It has
   four slices: (a) no boundary landed; (b) one boundary landed; (c) the filters
   under `--phase`; (d) the `core.quotePath` regression test, a mutation red as
   in Item 1.1. The outline amendment rode slice (a)'s code-review commit. Item
   2.3's base resolution becomes "`changed-files.sh <job> --phase` at every
   boundary; its `BASE:` is the phase base", and KD-2's rule stays as the
   definition.
2. **Item 2.15 (general): make `just lint` agree with `precommit`** on
   `tests/line_limits_helpers.py:32`. The correction stands: remove `PLR0913`
   from `ruff_ignores` in `plugin/portable.just`, around line 45. Leave the rest
   of that list as it is. **Never ignore RUF100.** If removing it surfaces new
   PLR0913 hits under `just lint` that `precommit` does not already flag, stop
   and report them; do not add suppressions. Add the item to the outline in its
   own commit.
3. After Item 1.4, resume the 2.3/2.4 artisan against the amended text, then
   carry on as planned.

## Completed this leg

| Slice | Commits |
|---|---|
| 1.4/1 | `✨ Item 1.4/1 — phase without boundary gives run base`; `🐛 Item 1.4/1 — code-review fixes; outline gains Item 1.4 and --phase base` |
| 1.4/2 | `✨ Item 1.4/2 — phase base is latest boundary commit`; `🐛 Item 1.4/2 — code-review fixes` |
| 1.4/3 | `✅ Item 1.4/3 — phase list keeps the filters`; `🐛 Item 1.4/3 — code-review fixes` |
| 1.4/4 | `✅ Item 1.4/4 — quotePath false does not hide dirt` (code review pending) |

Reports are under `plans/build-fixes/reports/item-1-4-s*-*.md`. After every
committed slice, `verify-step.sh` returned exit 0.

## State of Item 1.4's outline amendment

Done in `2f84d013`. The amendment made four changes:

- KD-6's script paragraph gained the `--phase` sentence.
- Item 1.2's interface became `changed-files.sh <job> [--phase]`.
- Item 2.3's base resolution was replaced.
- Item 1.4 was added after Item 1.3, with its four slices.

Two side effects:

- `rumdl fmt` reflowed the whole outline to 80 columns in the same commit, so
  the diff runs to 348 lines. The content changes are only the four above; the
  rest is reflow only.
- KD-2's sentence "An empty result during a live run means the boundary commit
  was skipped → STOP" now sits awkwardly beside `--phase`. With `--phase`, an
  empty match falls back to the run base, so `--phase` alone cannot tell that a
  boundary commit was skipped. The ruling keeps KD-2 unchanged. Item 2.3's
  executor should decide where, if anywhere, that STOP still applies, and say
  so.

## Item 2.15

Not started. It is not in the outline yet.

## Items 2.3 and 2.4: the artisan was not resumed

The leg-1 artisan committed 2.1 and 2.2 and stopped before 2.3. Neither 2.3 nor
2.4 has been touched (`phase-boundary.md` and `finishing.md` are unchanged since
`d415f22d`). A fresh delegate cannot resume that artisan. Dispatch a new
`edify:artisan` (opus) for 2.3 and 2.4. Compose it from the outline's current
Item 2.3 and 2.4 text and point it at:

- `plans/build-fixes/reports/item-2-1.md` and `item-2-2.md`, for what 2.1/2.2
  left. `escalation.md` points to `phase-boundary.md` for the landed-boundary
  query, and that query must exist after 2.3.
- The KD-2 STOP note above.
- The script's final interface. `changed-files.sh <job> [--phase]` takes
  `:(glob)` pathspecs. Exit 1 means `NO-BASE:` and exit 2 means `ERROR:`.

## Notes for later items and the review gate

- **Item 2.14:** the script's KD-1 and KD-2 queries use `:(glob)` pathspec
  magic, but the outline's KD-1 and KD-2 text does not. Record the queries with
  the magic, or the decision record and the script will disagree
  (`item-1-4-s3-code-review.md`).
- **The `:(glob)` on the KD-1 `item-*` query is unpinned.** Slice 3 pins the
  phase query's glob; the KD-1 query's glob has no test. The 1.4/3 reviewer
  suggested one: an earlier commit adding `plans/j/reports/item-x/notes.md`
  together with a non-plans file, with the asserted `BASE:` and list unchanged.
  This needs a decision: add it as a slice, or leave it to the review gate.
- **The test modules were split to stay under the 400-line cap.**
  - `tests/changed_files_helpers.py`, `tests/test_changed_files.py` and
    `tests/test_changed_files_phase.py` (in 1.4/2).
  - `tests/verify_step_helpers.py`, `tests/test_verify_step.py` and
    `tests/test_verify_step_exemption.py` (in 1.4/4).
  - Item 1.1's RED reports cite `tests.test_verify_step.SCRIPT`. `SCRIPT` now
    lives in `tests/verify_step_helpers.py`; `item-1-4-s4-test-review.md`
    records where.
- **The quotePath test pins `LC_ALL=C.UTF-8`.** Under `C`/`POSIX` the hazard it
  pins does not occur (`item-1-4-s4-test-review.md`).
- **Some executors' full-suite runs report 16 skips.** They come from
  `test_full_pipeline_remark`, which depends on PATH. The gate's own runs report
  1 xfail and no skips.
- Leg 1's open notes still stand: deviations 1 to 8, which include the
  orchestrator's D205 docstring fix and code-review fixes beyond the slice text.

## Open questions

None blocks the resume point. The unpinned KD-1 `:(glob)` test is a decision for
the review gate or for my human partner.
