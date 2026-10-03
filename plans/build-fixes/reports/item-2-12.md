# Item 2.12 — `docs/references/pipeline-contracts.md`, the D-86 argument

Requirements: m17.

## Changes

- **D-86, "The defect this settles".** "`verify-step.sh`, which tolerates
  nothing but ` M memory`" became "`verify-step.sh`, which then tolerated
  nothing but ` M memory`". The clause describes the script at the time of the
  defect. Today the script tolerates three exempt paths in any porcelain state
  except a rename or copy (`exempt-paths.sh`, `verify-step.sh` header). rumdl
  reflowed the rest of the paragraph. No words changed there.

## Judgement calls for review

- **"then tolerated", not a statement of today's exemptions.** D-86's
  paragraph is the dated rationale of a past defect. Under
  `craft:design-doc-writing`'s write-time-record rule its rationale is
  preserved, so the fix moves the clause into the past tense. It does not
  restate what the script tolerates now. That current truth is recorded as a
  decision by Item 2.14 (build-defects KD-7).

## Cross-references left for later items

- The current exemption set, recorded as a decision in this node and in
  `docs/decisions.md`: Item 2.14.

## Verification

- `just format` (rumdl reflowed the D-86 paragraph), then `just precommit`
  green: version consistency, tests 379/380 passed with 1 xfail, line limits
  (only the three allowlisted correctors reported), and design links (87
  decisions indexed, defined once, conclusions match, 8 nodes present).
- Self-review of the uncommitted diff against Item 2.12: one clause changed,
  and the reflow is whitespace only.
- `docs/references/pipeline-contracts.md`: 314 lines before, 314 after
  (`wc -l`, after `rumdl fmt`).
