# Apply batch 2 — proof, runbook, requirements

All `open-mechanical` findings from `verify-proof.md`, `verify-runbook.md` and
`verify-requirements.md` applied, in that order, per the dispatch. One finding
(requirements m10) skipped on the line budget as the report itself allowed;
everything else quoted-old-text-matched the working tree and applied cleanly.

## Findings applied

| Finding | File | Status |
|---|---|---|
| proof C2 (×2 sites) | `plugin/skills/proof/SKILL.md` | applied |
| proof M1 | `plugin/skills/design/SKILL.md` (2 sites), `plugin/skills/design/references/write-outline.md`, `plugin/skills/design/references/write-design.md`, `plugin/skills/runbook/SKILL.md` | applied |
| proof M1 (requirements site) | `plugin/skills/requirements/SKILL.md` | applied as part of requirements C1's rewrite (same target text) — see note below |
| proof M2 | `plugin/skills/proof/SKILL.md` | applied |
| proof M3 | `plugin/skills/proof/SKILL.md` | applied |
| proof M4 | `plugin/skills/proof/SKILL.md` | applied |
| proof M5 | `plugin/skills/proof/SKILL.md` | applied |
| proof M6 | `plugin/skills/proof/SKILL.md` | applied |
| proof m1 | `plugin/skills/proof/SKILL.md` | applied |
| proof m2 | `plugin/skills/proof/SKILL.md` | applied |
| proof m3 | `plugin/skills/proof/SKILL.md` | applied |
| proof m4 | `plugin/skills/proof/SKILL.md` | applied |
| proof m5 | `plugin/skills/proof/references/item-review.md` | applied |
| proof m6 | `plugin/skills/proof/SKILL.md` + `plugin/skills/proof/references/item-review.md` | applied — report offered two homes for the detail; kept detail in the reference (matching its own §3-5 framing) and cut SKILL.md's revisit bullet to a pointer |
| runbook M3 | `plugin/skills/runbook/SKILL.md` | applied |
| runbook M5 (×2 files) | `plugin/skills/runbook/SKILL.md`, `plugin/agents/runbook-corrector.md` | applied |
| runbook M6 | `plugin/skills/runbook/SKILL.md` | applied |
| runbook M7 | `plugin/skills/runbook/SKILL.md` | applied |
| runbook M8 | `plugin/skills/runbook/SKILL.md` | applied |
| runbook M9 | `plugin/skills/runbook/SKILL.md` | already applied (identical text/target to proof M1) — no further action |
| runbook m10 + m11 | `plugin/skills/runbook/SKILL.md` | applied (same site, one edit) |
| runbook m12 | `plugin/skills/runbook/SKILL.md` | applied |
| runbook m14 | `plugin/skills/runbook/SKILL.md` | applied |
| runbook m15 | `plugin/skills/runbook/SKILL.md` | applied |
| runbook m17 | `plugin/skills/runbook/references/runbook-format.md` | applied |
| requirements C1 | `plugin/skills/requirements/SKILL.md` | applied (folds in proof M1's `/edify:proof` fix for this file) |
| requirements M2 | `plugin/skills/requirements/SKILL.md` | applied |
| requirements M3 (×3 sites) | `plugin/skills/requirements/SKILL.md` | applied |
| requirements M4 | `plugin/skills/requirements/SKILL.md` | applied |
| requirements M5 (×2 sites) | `plugin/skills/requirements/SKILL.md` | applied |
| requirements M6 | `plugin/skills/requirements/SKILL.md` | applied |
| requirements m1 (×2 sites) | `plugin/skills/requirements/SKILL.md` | applied |
| requirements m2 | `plugin/skills/requirements/SKILL.md` | applied |
| requirements m3 | `plugin/skills/requirements/SKILL.md` | applied (routed to a named section instead of the report's raw line-number citation — a line number in skill prose rots the moment something above it is edited) |
| requirements m5 (×3 sites) | `plugin/skills/requirements/SKILL.md` | applied (one of the three sites was already covered by C1's rewrite) |
| requirements m6 | `plugin/skills/requirements/SKILL.md` | applied (both duplicate-budget-statement deletions) |
| requirements m7 | `plugin/skills/requirements/SKILL.md` | applied |
| requirements m8 | `plugin/skills/requirements/SKILL.md` | applied |
| requirements m9 (×2 sites) | `plugin/skills/requirements/SKILL.md` | applied |
| requirements m10 | `plugin/skills/requirements/SKILL.md` | **skipped** — the report itself made this conditional on the re-count: converting the description to block form costs +4 lines, and the file sat at 354/357 after the other edits, so applying it would have pushed to 358 and turned the gate red. Left as the cosmetic it is, per the report's own fallback. |

Nothing was skipped for old-text mismatch — every quoted old string was found
in the working tree (accounting for line-number drift, which the dispatch
said to expect and match on text instead).

## Line budget

| File (allowlisted ceiling) | Before this batch | After edits | After `just format` |
|---|---|---|---|
| `plugin/skills/proof/SKILL.md` (203) | 203 | 198 | 197 |
| `plugin/skills/requirements/SKILL.md` (357) | 357 | 355 | 354 |
| `plugin/skills/design/SKILL.md` (285, at 277 since batch 1) | 277 | 277 | 277 |

All three stayed under ceiling. `proof/SKILL.md` shrank enough (197) to drop
below the generic 200-line skill threshold entirely, so it no longer appears
in precommit's `oversized-file:` list at all — a further ratchet-down
opportunity on `scripts/check_line_limits.allow`, not acted on here since it
wasn't among the dispatched findings.

Non-allowlisted files touched (no ceiling risk): `plugin/skills/proof/references/item-review.md`
(101 → 95), `plugin/skills/runbook/SKILL.md` (149 → 151), `plugin/skills/runbook/references/runbook-format.md`
(138 → 139), `plugin/agents/runbook-corrector.md` (263 → 265), `plugin/skills/design/references/write-outline.md`
and `write-design.md` (unchanged line count, single-word substitution each).

## `just precommit` output (full, untruncated)

```
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
oversized-file: plugin/skills/review/SKILL.md: 231 lines > 200
oversized-file: plugin/skills/requirements/SKILL.md: 354 lines > 200
oversized-file: plugin/skills/design/SKILL.md: 277 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 218 lines > 200
oversized-file: docs/superpowers/design/plugin-transition-evaluation.md: 403 lines > 400
# design links
design-links: 85 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
```

Eight `oversized-file:` lines (one fewer than batch 1's nine, since
`proof/SKILL.md` dropped under the generic 200-line threshold and no longer
lists) — all non-failing, each inside its own allowlisted ceiling. Precommit
passed. No edit here required a fix or revert.

## Notes on findings that touched shared text

- **proof M1 / runbook M9** name the identical edit site
  (`runbook/SKILL.md`'s `/proof` → `/edify:proof` call). Applied once, from
  the proof report (dispatched first); runbook M9 needed no further action
  when reached.
- **proof M1 / requirements C1** both touch requirements/SKILL.md step 5's
  `/proof` invocation. Applied via C1's full step-5/6 rewrite (dispatched
  later, in the requirements report), which already writes `/edify:proof` —
  applying M1 standalone first would have been overwritten by C1's old-text
  match anyway, so it was folded into the later edit instead of duplicated.
- **requirements m2 / m5** both touch the same Recall Pass "Gate anchor"
  paragraph (`plugin/skills/requirements/SKILL.md`); applied together as one
  paragraph edit (m2's added reason, m5's trailing-rationale trim) since they
  overlap the same lines.
