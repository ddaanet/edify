# Item 3.5 — `classification.md` opens with one bare job-level label

- Target: `plugin/skills/design/references/triage.md` §Classification Gate,
  its block template and its persistence paragraph (KD-3, finding m15)
- Type: general
- Outcome: done; `just precommit` green

## Before

```markdown
Produce this classification block before routing (visible output, not internal
reasoning — **per-item if composite**):
- **Classification:** [Simple / Moderate / Complex / Defect]
...
**Classification persistence (C-2):** Write the filled-in classification block
to `plans/<job>/classification.md`. This file is consumed by
`triage-feedback.sh` for post-execution comparison.
```

## After

```markdown
Produce this classification block before routing (visible output, not internal
reasoning — **per-item if composite**). A single-item job's block is the whole
file, and its first line is the job-level line. A composite job opens with one
job-level `- **Classification:** <label>` line, then one block per item:
- **Classification:** <label> — exactly one of `Simple`, `Moderate`, `Complex`
  or `Defect`, with nothing after it
...
**Classification persistence (C-2):** Write the filled-in block or blocks to
`plans/<job>/classification.md`. Open the file with one job-level
`- **Classification:** <label>` line, at the start of its line, before any
per-item block. Write `<label>` as exactly `Simple`, `Moderate`, `Complex` or
`Defect`, with nothing after it: `triage-feedback.sh` reads the file's first
`Classification:` line, and any other value gives `no-classification`, so the
job's row is lost to calibration. A composite job's label is its most demanding
item's class, in the order Simple < Moderate < Complex, because triage measures
the whole run's evidence against that one label. `Defect` is the job-level label
only when every item is a Defect. No calibration data backs this ordering yet;
the triage log is where it will come from, once composite jobs have logged rows.
```

The other template bullets and every other section are unchanged. The file
goes from 121 to 131 lines.

## Contract bullets

1. **Template and paragraph require the file to open with one job-level line,
   before any per-item block.** The template's framing sentence: "A composite
   job opens with one job-level `- **Classification:** <label>` line, then one
   block per item", and for a single-item job "its first line is the job-level
   line", so no duplicate line is needed there. The paragraph: "Open the file
   with one job-level `- **Classification:** <label>` line, at the start of
   its line, before any per-item block."
2. **The value is exactly one of the four labels, nothing after it, with the
   reason.** The template's first bullet replaces the slash-separated
   placeholder `[Simple / Moderate / Complex / Defect]`, the form m15 names
   as producing composite labels, with `<label>` and "exactly one of
   `Simple`, `Moderate`, `Complex` or `Defect`, with nothing after it". The
   paragraph repeats the rule and gives the reason the contract states:
   "`triage-feedback.sh` reads the file's first `Classification:` line, and
   any other value gives `no-classification`, so the job's row is lost to
   calibration." That sentence replaces the old "consumed by
   `triage-feedback.sh` for post-execution comparison" line rather than
   standing beside it.
3. **The composite rule of KD-3.** Stated in KD-3's terms: most demanding
   item's class, Simple < Moderate < Complex, with KD-3's reason (triage
   measures the whole run's evidence against that one label); `Defect` only
   when every item is a Defect. The no-confabulation constraint is met by
   "No calibration data backs this ordering yet; the triage log is where it
   will come from, once composite jobs have logged rows." No threshold or
   criterion beyond KD-3 is added.
4. **`craft:directive-writing`; the template stays instruction.** Each added
   sentence is an act (open the file with, write `<label>` as, the label is).
   The one reason kept is the one the contract requires. The bad composite
   form is not named anywhere in the new text (withhold, don't forbid), and
   the text states the form to write, `- **Classification:** <label>`.

**Gap left as stated, not filled.** KD-3 does not say what a composite job
whose items mix a Defect with other classes takes as its label. Its ordering
covers Simple, Moderate and Complex only, and `Defect` applies only when every
item is a Defect. The prose states KD-3 literally and adds no rule for the
mixed case; settling it is a decision for the outline, not for this item.

## Code evidence for the parsing claim

`plugin/bin/triage-feedback.sh`, read at HEAD:

- `:173` — `label_prefix_re='^-?[[:space:]]*(\*\*Classification:\*\*|Classification:)'`.
  Accepted forms: `- **Classification:** X`, `**Classification:** X` and
  `Classification: X`, each from column 0 (an optional `-`, then
  whitespace). A line indented before its `-` does not match, which is why
  the paragraph says "at the start of its line".
- `:176` greps every matching line and `:179` keeps the first
  (`${label_lines%%$'\n'*}`); `:180`'s `sed` strips the prefix and trailing
  whitespace.
- `:192–193` — no matching line (grep exit 1) leaves the value empty:
  verdict `no-classification`, no extra output line.
- `:194–197` — any value other than exactly `Simple`, `Moderate`, `Complex`
  or `Defect`: `unrecognised_label` is set and the verdict is
  `no-classification`; `:245–248` prints
  `unrecognised classification: <value>`.
- `:261` — the log row is appended only when the verdict is not
  `no-classification`, so either case loses the row.

Pinned by `tests/test_triage_feedback.py::test_unrecognised_label_is_no_classification`
(first line `- **Classification:** Simple / Moderate agentic-prose (one route)`,
then an exact `Simple`: `no-classification`, one `unrecognised classification:`
line, no log) and `test_odd_names_and_labels_do_not_derail_triage`
(`colon-label`, `no-label-line` cases). The contract's claim matches the code.

**Probe of the new template.** A scratch composite file (heading, then
`- **Classification:** Moderate`, then two item blocks with `Simple` and
`Moderate`) run through the script's own `:173` regex and `:179–180`
pipeline, using `command grep`, yields exactly `Moderate\n`.

## Precommit

`PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit` was run in the
foreground. The first run failed at `# rumdl`: the reflow wanted two of the
new lines re-filled. `just format` applied the reflow to `triage.md` only. The
second run was green:

- version consistency: `Version consistent: 0.3.0`
- tests: `Tests cached (inputs unchanged)`
- rumdl: clean
- line limits: passed. It lists `plugin/agents/corrector.md` 682,
  `outline-corrector.md` 450 and `design-corrector.md` 460, each at its
  allowlisted ceiling in `scripts/check_line_limits.allow`, none of them
  touched here
- design links: `94 decisions indexed, defined once, conclusions match, 9 nodes present`
- `✓ Precommit OK`
