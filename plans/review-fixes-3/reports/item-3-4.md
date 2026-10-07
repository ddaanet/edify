# Item 3.4 — refactor's plan-sources reason covers every named file

- Requirements: m13
- Target: `plugin/agents/refactor.md` §Step 5, the plan-sources paragraph
- Finding (round-3 deliverable review, prose m3): the prohibition names four
  plan sources, but the reason named `runbook.md` alone as "the orchestrator's
  artifact". Under review-fixes-2 KD-7 the list-revision commit writes
  whichever of `runbook.md`, `outline.md` or `design.md` hosts the item
  (`plugin/skills/build/references/tdd-slice.md` §After the slice step 3).

## Before

```markdown
Never write into a plan's own sources — `runbook.md`, `design.md`, `outline.md`,
`requirements.md`. You run inside a slice, where `runbook.md` is the
orchestrator's artifact and a second writer collides with it. Your report under
`plans/<job>/reports/` is the one exception, and it is required (Step 6). Record
every rename in your report; the orchestrator carries the reference update into
the remaining items.
```

## After

```markdown
Never write into a plan's own sources — `runbook.md`, `design.md`, `outline.md`,
`requirements.md`. You run inside a slice. The file hosting the item —
`runbook.md`, or the `outline.md` or `design.md` routed to `/build` — takes the
orchestrator's list-revision commits, and the rest are the plan the run executes
against. A second writer collides with either. Your report under
`plans/<job>/reports/` is the one exception, and it is required (Step 6). Record
every rename in your report; the orchestrator carries the reference update into
the remaining items.
```

## Contract

- **Every named file is covered.** The hosting-file clause uses
  `tdd-slice.md` step 3's own wording ("`runbook.md`, or the `outline.md` or
  `design.md` routed to `/build`"), so whichever of the three hosts the item
  is covered as the list-revision target. "The rest" is unscoped: it covers the
  two non-hosting files of those three and `requirements.md`, which never
  hosts an item, as the plan the run executes against.
- **A second writer collides with either** is stated once, after both clauses.
- **The prohibition is unchanged.** The sentence "Never write into a plan's own
  sources — `runbook.md`, `design.md`, `outline.md`, `requirements.md`." and the
  report-exception and rename sentences after the reason are word-for-word as
  before. Only the reason sentence was replaced.
- No mechanism beyond the collision was added (`craft:directive-writing`).
- `refactor.md` has no entry in `scripts/check_line_limits.allow`; it went from
  226 to 228 lines.

## Precommit

`PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit`, run in the
foreground from the repo root, ended `✓ Precommit OK`. Checks that ran:

- version consistency: `Version consistent: 0.3.0`
- tests: `Tests cached (inputs unchanged)`
- line limits: passed; it listed the three allowlisted corrector-family files
  (`corrector.md` 682, `outline-corrector.md` 450, `design-corrector.md` 460),
  which this item does not touch
- design links: 94 decisions indexed, defined once, conclusions match, 9 nodes
  present

The formatter changed nothing in `refactor.md`: after the run, its diff showed
only the reason sentence.
