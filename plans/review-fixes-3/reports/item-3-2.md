# Item 3.2 — name the planning-artifact dispatch (KD-1)

Requirement: m12. Type: general.

## What changed

- `plugin/skills/build/references/dispatch-composition.md` §Naming and
  resumption: a new top-level entry, after the `review-<group>` entry and
  before `final-review`:
  `review-plan-<source job>-<stem>` for a planning artifact on the gate's
  list, a name and not a group. It defines `<source job>` (the `plans/`
  directory the artifact sits in) and `<stem>` (`design`, `outline` or
  `runbook`), gives KD-1's example (`plans/build-fixes/outline.md` →
  `review-plan-build-fixes-outline`), and states the reason in one clause:
  it matches `review-*.md`, so the gate's landed check reads its report as a
  review report.
- `plugin/skills/build/references/finishing.md` §1, the planning-artifact
  paragraph: the three artifact routes are now a list, each carrying its
  dispatch name (`review-plan-<source job>-design`, `-outline`, `-runbook`),
  with `<source job>` defined and a pointer to `dispatch-composition.md`
  §Naming and resumption. One sentence says the prompt assigns the report
  path from that name, as `dispatch-composition.md` §Prompt contents item 5
  does for every dispatch. The D-26 pointer and the `runbook-corrector`
  rejection sentence are kept.

## Contract

- §Naming lists `review-plan-<source job>-<stem>` beside the four group slugs,
  as a name and not a group, with KD-1's reason in one clause. Met: it is a
  sibling top-level entry of `review-<group>`, not a fifth nested slug. Its
  text says "a name and not a group", and the reason clause is "It matches
  `review-*.md`, so the gate's landed check reads its report as a review
  report." KD-1's other three constraints (slug collision, the agent's
  default, uniqueness) are left to the design record. The corrector's default
  report filename is withheld from both files, per `craft:directive-writing`
  §Withhold, don't forbid.
- `finishing.md` §1's paragraph gives that name for each planning artifact it
  routes. Met: `design.md`, `outline.md` and `runbook.md` each carry
  `review-plan-<source job>-<stem>` with the stem filled in.
- The prompt assigns the report path by §Prompt contents item 5, and no
  corrector definition changes. Met: `finishing.md` routes the report path
  through item 5. Nothing under `plugin/agents/` was touched.

## Consistency

The wording agrees with KD-1 as Item 4.1's D-93 sentence will give it. The
name is `review-plan-<source job>-<stem>`, `<source job>` is the directory the
artifact sits in, and it matches `review-*.md`. D-26's routing table is
unchanged and still cited.

## Observed seam, not fixed (out of scope)

The report-commit paragraph in `finishing.md` §1 ("every group's report, with
the fixes applied …") names group reports only. A `review-plan-*` report is
not a group's report, so that paragraph does not explicitly put it in the
review-gate commit. The item scopes the edit to the planning-artifact
paragraph, so this is recorded here and not changed.

## Verification

- `command grep -n 'review-plan-'` over both files returns the §Naming entry
  and the three names in `finishing.md`.
- `git diff` touches only the two targeted regions. The `git log …
  --format=%H` commands in `finishing.md` are byte-identical.
- `just precommit` on the first run: rumdl reflowed two lines of the new
  paragraph that were hand-wrapped past 80 columns. Those lines were rewrapped
  and the gate was rerun.
- `just precommit`, final run: green. Recap: version consistency (0.3.0),
  tests (cached, inputs unchanged), line limits (only the three corrector
  agents reported over 400, each within its allowlist ceiling: 682, 450 and
  460), design links (94 decisions indexed, defined once, conclusions match, 9
  nodes present). `Precommit OK`.
- Tests were cached, so
  `.venv/bin/pytest -p no:markdown_report tests/test_build_prose_git_log.py`
  was run directly: 10 passed.
