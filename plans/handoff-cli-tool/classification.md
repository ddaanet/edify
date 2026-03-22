# Classification: Fix handoff-cli findings

**Date:** 2026-03-22
**Input:** plans/handoff-cli-tool/reports/deliverable-review.md (5C/11M/12m)
**Plan status:** rework

## Composite Decomposition

| Cluster | Findings | Behavioral Code? | Classification | Destination |
|---------|----------|-------------------|----------------|-------------|
| A: Commit pipeline correctness | C#2, C#3, C#4, MN-1 | Yes | Moderate | production |
| B: Status completeness | M#7, M#8, M#9, M#12, MN-5 | Yes | Moderate | production |
| C: Bug fixes | M#10, M#11 | Yes | Moderate | production |
| D: Dead code removal | M#6 | No | Simple | production |
| E: SKILL.md fix | C#1 | No | Simple | agentic-prose |
| F: Test improvements | C#5, M#13, M#14, M#15, M#16 | Yes | Moderate | production |
| G: Minor quality (deferred) | MN-2, MN-3, m-1…m-5 | Mixed | Simple | production |

## Overall

- **Classification:** Moderate (composite)
- **Implementation certainty:** High
- **Requirement stability:** High
- **Work type:** Production
- **Model:** sonnet (downgraded from opus — high certainty rework)

## Scope

**In scope:** All Critical (5) + all Major (11) + co-located Minor (MN-1, MN-5, m-4) = 19 findings
**Deferred:** MN-2, MN-3, m-1, m-2, m-3, m-5, no ANSI = 7 findings

## Routing

Moderate (non-prose) → `/runbook plans/handoff-cli-tool`
