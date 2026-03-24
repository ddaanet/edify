# Classification: Fix handoff-cli RC8 findings

**Date:** 2026-03-24
**Input:** plans/handoff-cli-tool/reports/deliverable-review.md (RC8: 0C/0M/6m)
**Plan status:** reviewed
**Round:** 8

## Composite Decomposition

| # | Finding | Behavioral? | Classification | Action |
|---|---------|-------------|----------------|--------|
| m-1 | Bare pytest.raises without match (test_session_commit.py:101) | No (test param) | Simple | Add `match="no-edit contradicts"` |
| m-2 | Heading format not verified in handoff parse test (test_session_handoff.py:45-46) | No (assertion) | Simple | Add `assert any("### " in line ...)` |
| m-3 | Empty Files section not rejected (commit.py _validate) | Yes (new branch) | Moderate | Add `if not files: raise CommitInputError(...)` |
| m-4 | ci.message or "" fallback masks unreachable state (commit_pipeline.py:336) | Yes (assertion) | Moderate | Replace with `assert ci.message is not None` |
| m-5 | _strip_hints fragile continuation detection (commit_pipeline.py:204) | Yes (logic change) | Moderate | Fix continuation detection condition |
| m-6 | ParsedTask import bypasses S-4 interface in render.py | No (import fix) | Simple | `validation.task_parsing` → `session.parse` |

## Overall

- **Classification:** Mixed — Simple (m-1/m-2/m-6) + Moderate (m-3/m-4/m-5)
- **Implementation certainty:** High for all except m-5 (Moderate — logic change needs care)
- **Requirement stability:** High — RC8 findings with specific locations and expected behavior
- **Behavioral code check:** m-3/m-4/m-5 add/change production logic paths
- **Work type:** Production
- **Artifact destination:** production (src + tests)
- **Model:** sonnet
- **Evidence:** RC8 review provides file:line references, expected behavior, and fix mechanisms for all items

## Routing

Moderate items present → `/runbook plans/handoff-cli-tool`
- General phases: m-1, m-2, m-6 (simple test/import fixes, no behavioral code)
- TDD phases: m-3, m-4, m-5 (behavioral code changes in production)
