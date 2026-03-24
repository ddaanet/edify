# Classification: Fix handoff-cli RC7 findings

**Date:** 2026-03-24
**Input:** plans/handoff-cli-tool/reports/deliverable-review.md (RC7: 0C/0M/6m)
**Plan status:** reviewed
**Round:** 7

## Composite Decomposition

| # | Finding | Behavioral? | Classification | Action |
|---|---------|-------------|----------------|--------|
| m-1 | Vacuous disjunction in commit_format test | No (assertion rewrite) | Simple | Replace `assert A or B` with direct check for no-prefix |
| m-2 | Parametrize over shared fixture | No (restructure) | Simple | Collapse 4 cases to single combined assertion test |
| m-3 | ParsedTask import path inconsistency | No (import literal) | Simple | `validation.task_parsing` → `session.parse` |
| m-4 | No test for just-lint + no-vet combination | Yes (new test function) | Moderate | Add combined-options test |
| m-5 | Imprecise "clean" assertion | No (string literal) | Simple | `"clean" in output.lower()` → `"Tree is clean."` |
| m-6 | Imprecise "Git status" assertion | No (string literal) | Simple | `"Git status"` → `"**Git status:**"` |

## Overall

- **Classification:** Conformance/coverage batch — all mechanisms specified by review
- **Implementation certainty:** High — exact file:line references and fix approaches provided
- **Requirement stability:** High — RC7 findings with specific locations and expected behavior
- **Behavioral code check:** m-4 adds a test function (Moderate); remaining non-behavioral
- **Work type:** Production
- **Artifact destination:** production (tests)
- **Model:** sonnet
- **Evidence:** RC7 review provides file:line references, expected behavior, and fix mechanisms for all items

## Routing

All items execution-ready with known approaches. Route: `/inline plans/handoff-cli-tool execute`
