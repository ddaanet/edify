# Item 1.2 — prose fixes F1, F2, F4–F7

## Edits

- F2, `plugin/skills/build/references/finishing.md` (Planning artifacts
  paragraph): "through this gate" changed to "through the four group rows".
- F2, `docs/references/build-run-state.md` D-93 paragraph: routing sentence
  changed to "The `/build` review gate's four group rows take implementation
  files only; a planning artifact on its list routes by artifact (D-26)."
- F1, `docs/references/build-run-state.md` D-93 paragraph: inserted the
  `review-plan-*` landing sentence after "read its report as a review report."
- F4, `plugin/README.md` §Optional plugins, `plugin-dev` entry: appended the
  sentence on `/requirements`, `/design` and `/build` steps going without the
  `plugin-dev:*` guidance.
- F5, `plugin/skills/design/references/triage.md` Classification persistence:
  "Open the file with" changed to "Write"; added "a heading or prose may come
  before it."
- F6, `plugin/skills/design/references/triage.md`: the Defect/ordering sentences
  replaced with the mixed-job rule and "This ordering is ungrounded: no
  calibration data backs it."
- F7, `agents/learnings.md:64`: Anti-pattern bullet replaced with the verbatim
  text, one physical line.

## decisions.md

Unchanged. The D-93 conclusion line (`docs/decisions.md:104`) reads "Review-gate
groups are four fixed rows, with fixed slugs." and does not paraphrase the
routing sentence.

## Formatting

The first `just precommit` run failed in rumdl: it wanted to reflow the D-93,
finishing.md and triage.md paragraphs my edits lengthened. `just format` then
reflowed those three files (only those). No other file was touched by it.

## Line counts (after edits and format)

- `plugin/skills/build/references/finishing.md`: 189
- `docs/references/build-run-state.md`: 278
- `plugin/README.md`: 120
- `plugin/skills/design/references/triage.md`: 134
- `agents/learnings.md`: 195

None of these files is on `scripts/check_line_limits.allow`. No ceiling was
changed.

## Precommit

`PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit` — Precommit OK.
Checks that passed: version consistency (0.3.0), test report (432/433 passed,
1 xfail), rumdl, design links (94 decisions indexed, defined once, conclusions
match, 9 nodes present). The line-limits step printed three `oversized-file`
lines for `plugin/agents/corrector.md` (682), `plugin/agents/outline-corrector.md`
(450) and `plugin/agents/design-corrector.md` (460); all three are on the
allowlist with ceilings equal to those counts, and this item did not touch them.
