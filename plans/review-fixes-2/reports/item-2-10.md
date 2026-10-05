# Item 2.10 — review-dispatch-template.md: the example asks for a full UNFIXABLE

Target: `plugin/skills/build/references/review-dispatch-template.md`.
Requirements: m18.

## Edits

### §Example: Skill Creation Task — the prompt's return line

Was:

> Return the report path on success, or `blocked: <reason>`. Mark an issue you
> cannot fix "UNFIXABLE: [description]" inside the report.

Now:

> Return the report path on success, or `blocked: <reason>`. Inside the report,
> mark an issue that has no fix path "UNFIXABLE" with its subcategory code:
> U-REQ (requirements ambiguous or in conflict), U-ARCH (the fix would break an
> architectural invariant or a documented design decision) or U-DESIGN (several
> valid approaches with non-trivial downstream consequences). Follow it with an
> investigation summary of the three gates you checked — Scope OUT, design
> deferral, codebase patterns — and your conclusion. An issue in Scope OUT or
> deferred by the design is DEFERRED, not UNFIXABLE.

The UNFIXABLE sentences are §Report-only variant's, word for word. The return
contract itself is unchanged and still matches `dispatch-composition.md`
§Prompt contents: the report path or `blocked: <reason>`, with UNFIXABLE inside
the report, never a return. An UNFIXABLE marked as the example now asks carries
what `review-requirement.md` §UNFIXABLE Detection Protocol validates: a
subcategory code and an investigation summary of all three gates.

## Verification

- `just precommit`: `Precommit OK` (version consistency, tests cached, line
  limits, design links). No reflow beyond the edit; the file is 179 lines. The
  three `oversized-file` lines it prints (`corrector.md`,
  `outline-corrector.md`, `design-corrector.md`) are files this item does not
  touch.

## Surfaces outside scope

None found: a search of `plugin/` for "UNFIXABLE: [description]" finds no
other copy of the old return line.
