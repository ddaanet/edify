# Item 2.1 — `/build` hub: Item 1.1, refactor and list-revision verification, landed gate

Target: `plugin/skills/build/SKILL.md`. Requirements: M4, m7, m13.

## Edits

- **§1 (M4).** The resume paragraph ("Resumed or fresh") gains one sentence:
  work with no `Item N.M`, meaning option 3 or a design or outline without
  items, is one item, Item 1.1. Its report is `item-1-1.md` and its subject
  `<type>: <job> Item 1.1 — <title>`, so every run commits an item report
  (D-88). It sits at the end of the resume paragraph rather than under the
  option list at line 39. It ties to the resume test the paragraph states,
  and appending it there used that paragraph's short last line instead of a
  new paragraph and blank line. That placement is what brings the hub under
  200.
- **§2 DIRTY bullet (room).** The enumeration of the three exempt paths
  (`memory`, `.claude/handoff-*.md`, `inbox/*.md`) is replaced by a pointer:
  "except the paths dirty by convention that `scripts/exempt-paths.sh`
  defines (D-91)". Net −1 line.
- **§4.4 (m13).** The step list now covers a slice's refactor and its list
  revision. The repeated "once its commit lands" is factored to the head of
  the sentence, which now reads: "After every step whose work is committed,
  once its commit lands — a slice's GREEN, its code review, its refactor and
  its list revision, a review item, §4.1's one commit, a phase-boundary
  corrector, and any general item." No item lost its condition. This matches
  Item 2.4's "steps 2 and 3 each end at `SKILL.md` §4.4 once their commit
  lands".
- **§5 (m7).** One clause added to the "Not skippable" sentence: "a review
  gate `finishing.md` §1 finds already landed is not re-run". This matches
  Item 2.2's "§1 opens with the landed check; a landed gate goes to §2". The
  living design has no D-number for the landed-gate rule, so the text cites
  none.

No text cites an outline KD.

## Line count

`wc -l plugin/skills/build/SKILL.md` after `just format` gives **199**. It
was 196 before the edits. A second `just format` pass reformatted nothing.
The first placement of the §1 sentence, as its own paragraph after the
option list, measured 201. The sentence was then moved into the resume
paragraph as described above. No unrelated prose was shortened, and no line
runs past 80 columns.

## Verification

`just precommit` in the foreground: `✓ Precommit OK`. Version consistent
0.3.0, tests cached (inputs unchanged), design-links 94 decisions indexed.
The line-limits step printed three `oversized-file` lines for files this
item did not touch: `plugin/agents/corrector.md` 682,
`outline-corrector.md` 450, `design-corrector.md` 460. The gate still
passed.
