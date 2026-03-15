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

---

## 2026-03-14: Unresolved mechanical dependencies passed through to steps

**Failure mode:** /runbook skill generated plugin-migration phase steps that reference a tmux verification mechanism ("standard tmux interaction", "same tmux verification mechanism as Step 1.3") without the mechanism being designed. The dependency was flagged during outline /proof, flagged again during corrector review, and assigned a resolution point ("pre-Phase-1 spike or during Phase 1 expansion") — but the runbook skill generated the steps anyway, embedding the unresolved dependency in the text rather than surfacing it structurally.

**What the skill should have done:** When a step depends on a mechanism not yet specified, either:
1. Design the mechanism inline (spike step before the checkpoint step), or
2. Escalate: emit a structured design gap notice, halt runbook generation for that phase, and update the design artifact

**What it did instead:** Generated steps with placeholder language ("standard tmux interaction") that looks specified but isn't. The mechanism for driving a live Claude session via tmux — sending commands, waiting for output, capturing structured results — is genuinely complex and requires design work.

**Directive for /runbook skill:** Add a dependency-resolution check during step generation. When a step references a mechanism not specified in the design artifact, classify as either (a) well-understood (document inline) or (b) novel/unspecified (emit design gap, do not generate the step with placeholder language). Placeholder language in step text is not acceptable — it defers a design decision to the executor.

**Evidence:** `plans/plugin-migration/runbook-phase-1.md` Step 1.3, `runbook-phase-2.md` Step 2.4, `runbook-phase-6.md` Steps 6.1 and 6.3 — all reference tmux mechanism. Corrector review reports at `plans/plugin-migration/reports/` flagged it as unresolved.
