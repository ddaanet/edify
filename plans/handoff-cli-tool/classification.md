# Classification: Fix handoff-cli round 3 findings

**Date:** 2026-03-23
**Input:** plans/handoff-cli-tool/reports/deliverable-review.md (round 3: 0C/0M(delta), 2M+6m(pre-existing))
**Plan status:** rework
**Round:** 3 (prior: round 2 = 1C/4M/6m, round 1 = 5C/11M/12m)

## Prior Rounds

Round 2: 10 findings fixed (integration-first TDD). Round 3 Simple batch: 5 of 6 minor pre-existing fixed, 1 dropped (m-pre-2 ▶ format — design spec outdated). Round 3 delta: 2 minor fixed (m#1 regex, m#2 dropped).

## Composite Decomposition (remaining)

| # | Finding | Behavioral Code? | Classification | Destination |
|---|---------|-------------------|----------------|-------------|
| M-pre-1 | Parallel detection ignores Blockers/Gotchas | Yes | Moderate | production |
| M-pre-2 | Stale vet output lacks file-level detail | Yes | Moderate | production |
| m-pre-3 | Completed parser strips blank lines between `###` groups | Yes | Moderate | production |

## Overall

- **Classification:** Moderate (composite, 3 items)
- **Implementation certainty:** High — affected functions identified, target behavior specified
- **Requirement stability:** High — design spec (ST-1, C-1) and markdown preservation
- **Behavioral code check:** Yes (all 3 — new parser logic, changed output format, changed parsing logic)
- **Work type:** Production
- **Artifact destination:** production
- **Model:** sonnet
- **Evidence:** All items have concrete file:line refs; M-pre-1/M-pre-2 traced to design spec gaps; m-pre-3 observable in parser output

## Routing

Moderate (non-prose) → `/runbook plans/handoff-cli-tool`
