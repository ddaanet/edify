# Brief: Runbook Quality Directives

## Problem

Runbook planning produces noise that correctors don't catch. Three instances observed in bootstrap-tag-support execution:

1. **Over-specific Verify GREEN paths** — runbook template says `**Verify GREEN:** [Test command]`, planners fill with specific pytest paths (`tests/test_foo.py::TestBar::test_baz`). These accumulate staleness: test class renames, file moves, and refactors all invalidate them. The executor derived correct paths from context, ignoring the plan.

2. **Vacuous absence statements** — `**Bootstrap:** Not needed.` appears in cycles where Bootstrap is optional. No gate requires this statement. tdd-cycle-planning.md says "skip Bootstrap" but doesn't say "omit the section entirely." The corrector doesn't flag it.

3. **Redundant integration cycles** — C2.4 was a belt-and-suspenders integration test whose assertions were a subset of C2.2's step file tests. Tier 2 plans skip the outline-corrector and runbook-simplifier gates that Tier 3 has. No structural check for redundant coverage.

Additionally, Tier 2 plans have no output-channel guidance — the planner wrote the full runbook to both conversation (250 lines) and file, violating token economy.

## Evidence

- bootstrap-tag-support runbook: `plans/bootstrap-tag-support/runbook.md` — C2.4 redundant, Verify GREEN paths all specific, Bootstrap absence statements present
- bootstrap-tag-support execution: C2.4 was not executed (merged into C2.2+2.3). Verify GREEN paths were wrong after test file split to `test_prepare_runbook_bootstrap.py`. Full plan output duplicated in conversation.
- Existing `red-lint` recipe in justfile — `just red-lint` exists (format + checks, no tests). No `just green` equivalent.

## Scope

### Edits

**tdd-cycle-planning.md (author artifact):**
- Collapse `**Verify GREEN:**` + `**Verify no regression:**` into single `**Verify GREEN:** just green` (or `just lint` until recipe exists)
- Add explicit "omit Bootstrap section entirely when not needed — do not include absence statements" language
- Template change: remove `[Test command]` placeholder, replace with universal `just green`

**justfile (prerequisite):**
- Add `just green *ARGS` recipe — semantic alias for `just lint` that accepts pytest args passthrough. Makes runbook directives self-documenting.
- Optionally: rename considerations (currently `lint` = format + checks + test, which is semantically `green`)

**/runbook SKILL.md (Tier 2 section):**
- Add consolidation self-check after planning cycles: "Identify any cycle whose assertions are subset of another's. Merge or drop."
- Add output-channel directive: "Write plan directly to `plans/<job>/runbook.md`. Reference path in conversation. Do not output plan content to conversation."

**/review-plan + validate-runbook.py (coupled corrector):**
- Add corrector rules: flag vacuous cycles (integration test whose assertions subset of another), vacuous absence statements (`**Bootstrap:** Not needed`/`None`), Verify GREEN lines containing specific pytest paths
- validate-runbook.py: mechanical check for specific pytest paths in Verify GREEN lines

### Author-Corrector Coupling

| Author Change | Corrector | Update Needed |
|--------------|-----------|---------------|
| tdd-cycle-planning.md (Verify GREEN template) | /review-plan | Flag over-specific Verify GREEN paths |
| tdd-cycle-planning.md (Bootstrap omission) | /review-plan | Flag vacuous absence statements |
| /runbook SKILL.md (consolidation check) | /review-plan | Flag redundant cycle coverage |

All corrector updates must ship in the same batch as author changes.

## Classification Hint

Agentic-prose edits across skill files + corrector. No behavioral code changes (justfile recipe is mechanical). Opus model for skill/corrector edits. Single /inline execution with corrector dispatch.

## Dependencies

- `just green` recipe must exist before tdd-cycle-planning.md references it
- No dependency on other pending plans
