# Classification: Fix handoff-cli RC4 findings

**Date:** 2026-03-23
**Input:** plans/handoff-cli-tool/reports/deliverable-review.md (RC4: 0C/2M/9m)
**Plan status:** rework
**Round:** 4 (prior: RC1=5C/11M/12m, RC2=1C/4M/6m, RC3=2M+6m pre-existing)

## Composite Decomposition

| # | Finding | Behavioral? | Classification | Destination | Action |
|---|---------|-------------|----------------|-------------|--------|
| M-1 | H-2 committed detection test | Yes (new test fn) | Moderate | production | Add test: commit session.md, call write_completed, assert overwrite |
| M-2 | `_init_repo` duplication | Yes (new helper fn) | Moderate | production | Add `init_repo_minimal(path)` to pytest_helpers.py, replace 5 local variants |
| m-1 | HandoffState `step_reached` field | Yes (new field, updated fn sig) | Moderate | production | Add field with default, update save_state signature |
| m-2 | No ANSI color in `_status` | Yes (new logic paths) | Moderate | production | Add `color: bool` param to render fns, use click.style() |
| m-3 | ▶ format deviation | No (format string edit) | Simple | production | Edit render.py:44 format string to match design spec |
| m-4 | `_strip_hints` continuation | Yes (new conditional) | Moderate | production | Track in_hint state, skip indented continuation lines |
| m-5 | Parallel cap-at-5 untested | Yes (new test fn) | Moderate | production | Add test: 6 independent tasks, verify cap returns 5 |
| m-6 | or-disjunction assertions | No (edit existing) | Simple | production | Split `assert A or B` into separate focused assertions |
| m-7 | Integration test incomplete | No (extend existing) | Simple | production | Add completed-section and status-line assertions |
| m-8 | .gitignore/settings.local.json | — | Skip | — | Benign, no action |
| m-9 | worktree/cli.py:311 hardcodes agent-core | — | Skip | — | Pre-existing, not regression |

## Overall

- **Classification:** Moderate (composite — 6 Moderate + 3 Simple actionable)
- **Implementation certainty:** High — file:line refs, approach specified
- **Requirement stability:** High — design specs and observable behaviour
- **Behavioral code check:** Yes (new helper, new conditionals, new test functions)
- **Work type:** Production
- **Artifact destination:** production
- **Model:** sonnet
- **Evidence:** M-1/M-2 test coverage/quality; m-1 spec conformance; m-2/m-4 add conditional logic; m-3/m-6/m-7 mechanical edits

## Routing

Moderate (non-prose) → `/runbook plans/handoff-cli-tool`
