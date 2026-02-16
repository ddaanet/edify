# Runbook Quality Gates — Design Outline

## Problem

The runbook pipeline has validation gaps. Expanded phase files may contain redundant patterns, incorrect model assignments, file lifecycle violations, implausible RED states, and inaccurate test count checkpoints. These defects propagate to execution, wasting cycles on avoidable failures.

## Approach

Two new capabilities integrated into existing pipeline stages:

```
0.85 → [Simplification agent (FR-1)] → 0.9 → 0.95 → Phase 1 (plan-reviewer enriched with FR-2 semantic) → Phase 2 → 2.5 → Phase 3 → [Phase 3.5: Pre-execution validation (FR-2 mechanical, FR-3, FR-4, FR-5)] → Phase 4
```

**Outline-level consolidation (FR-1):** Dedicated simplification agent operates on the outline after Phase 0.85 trivial merging. Detects identical patterns and consolidates before expensive Phase 1 expansion.

**Pre-execution validation (FR-3, FR-4, FR-5, FR-2 mechanical):** Python script with subcommands validates the assembled runbook after Phase 3 holistic review, before prepare-runbook.py.

**Plan-reviewer enrichment (FR-2 semantic):** Model assignment criteria added to plan-reviewer's existing per-phase review. No new pipeline stage.

## Key Decisions

**D-1: FR-1 at outline level.** Consolidation operates on outline items, not expanded phases. Avoids wasting expansion cost on items that will be consolidated. Workwoods evidence: identical patterns (4 status levels, same function) visible from outline titles alone.

**D-2: FR-2 split.** Mechanical check (file path → model mapping) is deterministic → script subcommand in Phase 3.5. Semantic check (task complexity → model assessment) requires judgment → plan-reviewer criteria enrichment in Phase 1.

**D-3: Dedicated simplification agent.** Every pipeline transformation has a dedicated enforcer. Simplification is optimization/transformation, not defect detection — different cognitive task from plan-reviewer's fix-all. Domain knowledge (pattern heuristics, renumbering, outline format) warrants structured capture.

**D-4: Mandatory for all Tier 3.** FR-1 (simplification) and Phase 3.5 (validation) both mandatory. Simplification is cheap on small runbooks and FR-2 model review has consistent value regardless of size.

**D-5: Script output format.** Validation scripts exit 0 (pass), 1 (violations, blocking), or 2 (ambiguous, optional agent delegation). Structured reports with pass/fail per check, violation locations (phase:cycle).

**D-6: All deliverables require opus.** Agent definitions, skill files, pipeline contracts, memory index — all architectural artifacts consumed by LLMs.

## Scope

**In scope:**
- FR-1: Outline-level consolidation (pattern detection, parametrization)
- FR-2: Model selection review (mechanical script + semantic plan-reviewer enrichment)
- FR-3: File lifecycle validation (create→modify dependency graph)
- FR-4: RED plausibility audit (structural script + optional semantic agent)
- FR-5: Test count reconciliation (checkpoint claims vs actual)
- FR-6: Scaling by runbook size
- New agent: runbook simplification agent
- Integration: `/runbook` skill SKILL.md, plan-reviewer, pipeline contracts, memory index

**Out of scope:**
- Execution-time monitoring (orchestrator's job)
- Design-level quality (design-vet-agent)
- Per-phase TDD discipline review (plan-reviewer handles in Phase 1)
- Modifying orchestrate skill or prepare-runbook.py internals

## Architecture

### Outline-Level Consolidation (FR-1)

**Trigger:** After Phase 0.85 (trivial merging), before Phase 0.9 (complexity check). Mandatory for all Tier 3 runbooks.

**Dedicated agent:** `agent-core/agents/runbook-simplification-agent.md`

**Process:**
- Read `runbook-outline.md` (post-0.85 state)
- Detect consolidation patterns:
  - Identical-pattern items (same function/file, same test structure, varying only fixture data) → single parametrized item
  - Independent functions in same module → batch into single item
  - Sequential additions to same output/data structure → merge
- Rewrite outline with consolidations applied
- Update item numbering and requirements mapping table
- Write report at `plans/<job>/reports/simplification-report.md`

**Post-consolidation:** Outline re-enters pipeline at Phase 0.9 (complexity check). No re-review by outline-review-agent needed — simplification agent validates its own output against outline structure rules.

### Plan-Reviewer Enrichment (FR-2 Semantic)

**Change:** Add model assignment criteria to plan-reviewer's per-phase review (Phase 1 step 4) and holistic review (Phase 3).

**New criteria (added to review-plan skill or plan-reviewer agent):**
- Flag steps where task complexity doesn't match model tag
- Synthesis tasks (combining multiple sources) assigned below sonnet → flag
- Mechanical grep-and-delete assigned above haiku → flag
- Advisory finding (not blocking) — model assignment is judgment, not hard rule

**No new pipeline stage.** Enriches existing reviews.

### Pre-execution Validation (FR-2 Mechanical, FR-3, FR-4, FR-5)

**Trigger:** After Phase 3 (holistic review) passes, before Phase 4 (prepare-runbook.py). Mandatory for all Tier 3.

**`validate-runbook.py`** — Single script, 4 subcommands (orchestrator-invoked internal tooling):

- `validate-runbook.py model-tags <runbook-or-dir>` — FR-2 mechanical
  - Parse `**Execution Model**:` tags and `File:` references
  - Match file paths against artifact-type override rules (skills/ → opus, fragments/ → opus, agents/ → opus, workflow-*.md → opus)
  - Flag mismatches: artifact-type file with non-opus model tag
  - Exit 0 (pass) or exit 1 (violations)

- `validate-runbook.py lifecycle <runbook-or-dir>` — FR-3
  - Parse `File:` + `Action:` references from all phases
  - Build create→modify dependency graph
  - Flag: modify-before-create, duplicate creation, future-phase reads
  - Exit 0 (pass) or exit 1 (violations)

- `validate-runbook.py test-counts <runbook-or-dir>` — FR-5
  - Extract `**Test:**` fields from TDD cycles
  - Parse checkpoint "All N tests pass" claims
  - Account for parametrized tests, cumulative counts, deleted tests
  - Flag mismatches with expected vs claimed count
  - Exit 0 (pass) or exit 1 (violations)

- `validate-runbook.py red-plausibility <runbook-or-dir>` — FR-4 structural
  - For each RED, check if prior GREENs created the module/function the RED expects to fail on
  - Flag "already-passing" states where prior GREEN satisfies new test
  - Structural only (module existence, function creation)
  - Exit 0 (pass), 1 (violations), or 2 (ambiguous cases needing semantic analysis)

**Optional agent (FR-4 semantic extension):**
- Trigger: red-plausibility exits with code 2 (ambiguous)
- Reads structural report + phase files with flagged cycles
- Evaluates: does prior implementation state cause the expected RED failure?
- Output: `plans/<job>/reports/validation-red-semantic.md`

**Script outputs:** `plans/<job>/reports/validation-{model-tags,lifecycle,test-counts,red-plausibility}.md`

### Scaling (FR-6)

| Runbook Size | Simplification | Phase 3.5 Scripts | Phase 3.5 Agent |
|---|---|---|---|
| Small (≤3 phases, ≤15 items) | Runs (mandatory) | Single pass, all checks | Skip unless exit 2 |
| Large (>3 phases or >15 items) | Runs (mandatory) | Single pass, all checks | Optional (ambiguity-triggered) |

Scripts are fast regardless of size (text parsing). Simplification agent cost bounded by outline size.

### Incremental Adoption (NFR-2)

- Phase 3.5 checks accept `--skip-{model-tags,lifecycle,test-counts,red-plausibility}` flags
- Missing script degrades gracefully: runbook skill checks existence before invoking, proceeds if not found
- Simplification agent: runbook skill checks agent definition exists, skips if not found
- Each capability deployable independently

### Integration

**Deliverables:**
- `agent-core/agents/runbook-simplification-agent.md` — new agent definition (opus)
- `agent-core/bin/validate-runbook.py` — new validation script (general)
- `agent-core/skills/runbook/SKILL.md` — add consolidation step after 0.85, add Phase 3.5 (opus)
- `agent-core/agents/plan-reviewer.md` — add model assignment criteria (opus)
- `agents/decisions/pipeline-contracts.md` — add transformations to table (opus)
- `agents/memory-index.md` — add entries for new decisions (opus)

**Pipeline contracts additions:**
- T2.5 (Outline → Simplified outline): between T2 and T3, runbook-simplification-agent
- T4.5 (Assembled runbook → Validated runbook): between T4 and T5, validate-runbook.py

## Implementation Notes

**All deliverables except validate-runbook.py are architectural artifacts → opus required.**

**Test strategy:** validate-runbook.py gets unit tests with fixture runbooks (TDD). Agent-based changes validated via acceptance criteria (manual inspection).

**Skill dependencies:** `plugin-dev:agent-development` needed for simplification agent creation.

## References

- `plans/runbook-quality-gates/requirements.md` — source requirements
- `plans/runbook-quality-gates/reports/explore-pipeline.md` — pipeline exploration
- `plans/runbook-quality-gates/reports/explore-validation.md` — validation infrastructure
- `agent-core/skills/runbook/SKILL.md` — runbook skill (primary integration target)
- `agents/decisions/pipeline-contracts.md` — pipeline contracts
- `agents/decisions/defense-in-depth.md` — quality gate layering pattern
