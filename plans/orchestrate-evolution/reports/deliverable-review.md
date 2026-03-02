# Deliverable Review: orchestrate-evolution

**Date:** 2026-03-02
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | Lines (+/-) |
|------|------|-------------|
| Code | `agent-core/bin/prepare-runbook.py` | +348/-88 |
| Code | `agent-core/skills/orchestrate/scripts/verify-step.sh` | +28 |
| Code | `agent-core/skills/orchestrate/scripts/verify-red.sh` | +24 |
| Code | `tests/pytest_helpers.py` | +7/-1 |
| Test | `tests/test_prepare_runbook_agent_caching.py` | +389 |
| Test | `tests/test_prepare_runbook_agent_context.py` | +264 |
| Test | `tests/test_prepare_runbook_agents.py` | +5/-254 |
| Test | `tests/test_prepare_runbook_boundary.py` | +2/-2 |
| Test | `tests/test_prepare_runbook_inline.py` | +3/-3 |
| Test | `tests/test_prepare_runbook_mixed.py` | +16/-13 |
| Test | `tests/test_prepare_runbook_orchestrator.py` | +198 |
| Test | `tests/test_prepare_runbook_phase_context.py` | +9/-9 |
| Test | `tests/test_prepare_runbook_recall.py` | +5/-7 |
| Test | `tests/test_prepare_runbook_tdd_agents.py` | +364 |
| Test | `tests/test_verify_red.py` | +76 |
| Test | `tests/test_verify_step.py` | +127 |
| Agentic prose | `agent-core/skills/orchestrate/SKILL.md` | +163/-212 |
| Agentic prose | `agent-core/agents/refactor.md` | +14/-39 |
| Agentic prose | `agent-core/fragments/delegation.md` | +9/-6 |

**Totals:** 19 files, +2051/-634 net. Code: 4 files (+318 net). Test: 12 files (+1170 net). Agentic prose: 3 files (-71 net).

**Design conformance:** All 6 design-specified deliverable files produced. No missing deliverables. Test files excess but justified by design Testing Strategy section.

## Critical Findings

None.

## Major Findings

### M-1: Phase summaries vacuous — preambles parameter unused

- **File:** `agent-core/bin/prepare-runbook.py:1548-1555` (generation), `:1829-1840` (call site)
- **Axis:** Conformance, functional completeness
- **Design ref:** Lines 277-278 — "Phase summaries: IN/OUT scope for checkpoint delegation. Generated from runbook phase descriptions."
- **Description:** `generate_default_orchestrator` accepts `phase_preambles` parameter (line 1389) but never uses it. The Phase Summaries section always emits `- IN: (placeholder)` / `- OUT: (placeholder)`. Additionally, `validate_and_create` at line 1829 doesn't pass `phase_preambles` to the call despite having it available. SKILL.md Section 3.5 reads these values for corrector checkpoint delegation — the corrector receives placeholder text instead of actual scope.

### M-2: Dead code — old per-phase agent generation functions

- **File:** `agent-core/bin/prepare-runbook.py:999-1030`
- **Axis:** Excess, modularity
- **Description:** `generate_agent_frontmatter()` (lines 999-1010) and `generate_phase_agent()` (lines 1013-1030) are never called from any production or test code. They were replaced by `generate_task_agent()` and `generate_corrector_agent()` but not removed. Both use the superseded `crew-` naming convention. Additionally, line 1506 has a stale fallback `f"crew-{runbook_name}-p{p}"` in the Phase-Agent Mapping table.

### M-3: SKILL.md missing refactor agent invocation

- **File:** `agent-core/skills/orchestrate/SKILL.md` — absent from execution loop
- **Axis:** Functional completeness
- **Design ref:** Architecture > Orchestrate Skill > "What changes from current skill" — "Refactor agent invoked for complexity warnings with deslop directives"
- **Description:** The design lists refactor agent invocation as a change from the current skill, triggered by complexity warnings. SKILL.md has no reference to the refactor agent. The refactor.md updates (deslop directives, factorization-before-splitting, resume pattern) are implemented but the orchestration loop never dispatches the agent. No mechanism exists for correctors to signal complexity warnings to the orchestrator.

## Minor Findings

### Scope enforcement and content precision

- **m-1:** Task agent scope enforcement footer (`:1076`) missing "Do NOT read ahead in the runbook" clause specified in design line 142.
- **m-2:** `_build_plan_context_section` (`:1047-1048`) places Common Context under `# Plan Context` as `## Common Context` instead of design's separate `# Runbook-Specific Context` section. Functionally equivalent — note as intentional simplification.
- **m-3:** SKILL.md inline phase content source (line 58) assumes `runbook-phase-P.md` exists, which requires phase-directory layout. Single-file runbooks with inline phases would fail this path. Should reference orchestrator plan's `## Phase Files` section or the runbook itself.
- **m-4:** SKILL.md completion diff (line 225) uses `git log --all --oneline | tail -1` (first-ever repo commit) as baseline. Overly broad — should capture start commit or use a more targeted approach.
- **m-5:** SKILL.md single-phase completion (line 228) omits outline reference. Design's single-phase corrector prompt (lines 199-203) includes `**Runbook outline:** plans/<name>/outline.md`.

### Determinism and constraint precision

- **m-6:** SKILL.md phase boundary detection (lines 161-162) uses phase field comparison ("If phase changes") rather than the explicit `PHASE_BOUNDARY` marker in the generated orchestrator plan. The marker is the design's specified mechanism (design line 268) and more deterministic.
- **m-7:** SKILL.md inline phase review threshold (line 62) "≤5 net lines across ≤2 files" for self-review vs corrector delegation is ungrounded. Per project rules (No Confabulation), should be stated as a heuristic.

### Refactor agent alignment

- **m-8:** refactor.md resume pattern (line 198) uses trigger "interrupted mid-refactoring" instead of design's "precommit still has warnings after changes." Missing the "once" constraint and error-return behavior from design specification.

### Test coverage gaps

- **m-9:** No test for TDD corrector agents' (`test-corrector`, `impl-corrector`) `model: sonnet` frontmatter field. The general corrector test covers `{name}-corrector.md` but TDD correctors lack this assertion.
- **m-10:** No test for TDD tester/implementer agents' role-specific footers (scope enforcement content). Design ambiguity — D-5 role descriptions don't explicitly list scope/clean-tree footers, but D-2 "same pattern" phrasing implies them.
- **m-11:** `test_verify_step.py` does not test submodule pointer check path or precommit failure path. Both implemented in verify-step.sh but untested.
- **m-12:** `test_verify_red.py` missing test for zero-argument invocation (script handles it at lines 5-8).
- **m-13:** Weak assertion in `test_tester_contains_test_quality_directive` (line 211) — `"test quality" in content.lower()` matches too broadly. Compare with implementer test which checks `"Role: Implementer"`.

### Acceptable enhancements beyond design

- **m-14:** SKILL.md checkpoint template adds `**Review recall:**` protocol (lines 183-184) — not in design, but aligns with project recall patterns. Acceptable.
- **m-15:** SKILL.md checkpoint template adds `**First:** Run just dev` (line 177) — not in design, but aligns with project convention. Acceptable.
- **m-16:** SKILL.md Section 6 adds deliverable review pending task creation and lifecycle entry — not in design's completion section. Beneficial workflow chaining.

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| FR-2: Post-step remediation | Covered | SKILL.md Section 3.4 |
| FR-3: RCA task generation | Covered | SKILL.md Section 3.4 line 156 |
| FR-4: Delegation prompt deduplication | Covered | prepare-runbook.py generate_task_agent, _build_plan_context_section |
| FR-5: Commit instruction in prompts | Covered | prepare-runbook.py:1077 clean tree footer |
| FR-6: Scope constraint in prompts | Partially covered | prepare-runbook.py:1076 — missing "read ahead" clause (m-1) |
| FR-7: Precommit verification | Covered | verify-step.sh |
| FR-8: Ping-pong TDD orchestration | Covered | SKILL.md Section 3.2, generate_tdd_agents, _TDD_ROLES |
| FR-8a: Mechanical RED gate | Covered | verify-red.sh, SKILL.md Section 3.2 Step B |
| FR-8b: Mechanical GREEN gate | Covered | SKILL.md Section 3.2 Step E (just test + verify-step.sh) |
| FR-8c: Role-specific correctors | Covered | generate_tdd_agents: test-corrector, impl-corrector |
| FR-8d: Agent resume across TDD cycles | Covered | SKILL.md Section 3.2 "Agent resume across cycles" |
| NFR-1: Context bloat mitigation | Covered | File references only, agent caching model |
| NFR-2: Backward compatibility | Covered | Clean break, old functions dead (M-2 cleanup needed) |
| NFR-3: Sonnet orchestrator | Covered | SKILL.md line 12, delegation.md line 13 |
| Design: Refactor agent invocation | **Missing** | M-3 — not wired in SKILL.md |
| Design: Phase summaries from descriptions | **Vacuous** | M-1 — always "(placeholder)" |

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 3 |
| Minor | 16 |

No Critical findings. Three Major findings: vacuous phase summaries (M-1), dead code from old agent model (M-2), missing refactor agent wiring (M-3). Sixteen Minor findings across scope enforcement gaps, determinism improvements, test coverage, and design-deviating enhancements.
