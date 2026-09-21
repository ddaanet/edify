# Apply batch 1 — ground, recall, formalize, design

All `open-mechanical` findings from the four named reports applied. None
skipped — every quoted old text matched the working tree exactly (Edit tool
would have errored otherwise, and none did).

## Findings applied

| Finding | File | Status |
|---|---|---|
| ground 1 (×4 sites) | `plugin/skills/ground/SKILL.md` | applied |
| ground 2 | `plugin/skills/ground/SKILL.md` | applied |
| ground 4 | `plugin/skills/ground/SKILL.md` | applied |
| ground 5 | `plugin/skills/ground/SKILL.md` | applied |
| ground 7 | `plugin/skills/ground/SKILL.md` | applied |
| ground 11 | `plugin/skills/ground/SKILL.md` | applied |
| ground 6 | `plugin/skills/ground/references/grounding-criteria.md` | applied |
| ground 12 | `plugin/skills/ground/references/grounding-criteria.md` | applied |
| ground 14 | `plugin/skills/ground/references/grounding-criteria.md` | applied |
| recall M3 + m4 | `plugin/skills/recall/SKILL.md` | applied |
| recall M5 | `plugin/skills/recall/SKILL.md` | applied |
| recall m1 | `plugin/skills/recall/SKILL.md` | applied |
| formalize 4 + 5 | `plugin/skills/formalize/SKILL.md` | applied |
| formalize 6 (+ closes 13) | `plugin/skills/formalize/SKILL.md` | applied |
| formalize 7 | `plugin/skills/formalize/SKILL.md` | applied |
| formalize 9 | `plugin/skills/formalize/SKILL.md` | applied |
| formalize 10 | `plugin/skills/formalize/SKILL.md` | applied |
| formalize 12 | `plugin/skills/formalize/SKILL.md` | applied |
| design M3 | `plugin/skills/design/SKILL.md` | applied |
| design m2 | `plugin/skills/design/SKILL.md` | applied |
| design m5 | `plugin/skills/design/SKILL.md` | applied |
| design m1 (×2 sites) | `plugin/skills/design/references/design-content-rules.md` | applied |
| design m6 | `plugin/skills/design/references/write-outline.md` | applied |
| design m7 | `plugin/skills/design/references/write-outline.md` | applied |
| design m6 | `plugin/skills/design/references/write-design.md` | applied |

Notes on wording fidelity to the reports:
- Two edits had minor line-wrap artifacts from literal copy of the report's
  broken quote (ground finding 4's `(persistent,` / `tracked).` split, and the
  session-scraper bullet in grounding-criteria.md). Both reflowed to read as
  one sentence before running the formatter; content unchanged from what the
  report specified.
- formalize finding 6's target path
  (`docs/superpowers/design/invariant-guided-verify-loop.md`) and the
  superseded spec path both verified to exist on disk before the edit landed.
- design M3's `§D-26` citation verified against
  `docs/references/pipeline-contracts.md:55` and `docs/decisions.md:61` before
  use.
- recall M5/M3's fragment section citations (`§Recall Content In Delegation
  Prompts`, `§Recall Artifacts For Sub-Agents`) verified against
  `plugin/fragments/delegation.md` headings before use.

## Line budget

Only `plugin/skills/design/SKILL.md` among the four skills' touched files is
on `scripts/check_line_limits.allow` (ceiling 285). The others (ground,
recall, formalize `SKILL.md`) are uncapped at 200.

| File | Before | After edits | After `just format` |
|---|---|---|---|
| `plugin/skills/design/SKILL.md` (allowlisted, ceiling 285) | 285 | 277 | 277 |

`design/SKILL.md` shrank (M3 −5, m2 −1, net under budget) and stayed under
ceiling after the formatter's reflow. Its own allowlist file documents a
policy that a shrunk file's ceiling should be lowered to match — not done
here, since that wasn't among the findings dispatched and touching
`scripts/check_line_limits.allow` wasn't asked for. Flagging it rather than
acting on it.

For reference, the other three (uncapped, no ceiling risk):

| File | Before | After `just format` |
|---|---|---|
| `plugin/skills/ground/SKILL.md` | 107 | 111 |
| `plugin/skills/recall/SKILL.md` | 94 | 98 |
| `plugin/skills/formalize/SKILL.md` | 95 | 107 |

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
oversized-file: plugin/skills/requirements/SKILL.md: 357 lines > 200
oversized-file: plugin/skills/design/SKILL.md: 277 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 218 lines > 200
oversized-file: plugin/skills/proof/SKILL.md: 203 lines > 200
oversized-file: docs/superpowers/design/plugin-transition-evaluation.md: 403 lines > 400
# design links
design-links: 85 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
```

Nine `oversized-file:` lines — matches the nine files on
`scripts/check_line_limits.allow`, all non-failing (each is inside its own
allowlisted ceiling). Precommit passed. No edit here required a fix or
revert.
