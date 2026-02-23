# Deliverable Review: phase-scoped-agents

**Date:** 2026-02-23
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | Lines |
|------|------|-------|
| Code | agent-core/bin/prepare-runbook.py | +198/-29 |
| Test | tests/test_prepare_runbook_agents.py | +353 (new) |
| Test | tests/test_prepare_runbook_mixed.py | +1/-1 |
| Test | tests/test_prepare_runbook_orchestrator.py | +3/-3 |
| Test | tests/test_prepare_runbook_phase_context.py | +2/-2 |
| Agentic prose | agent-core/skills/orchestrate/SKILL.md | +3/-3 |
| Planning artifact | .claude/agents/phase-scoped-agents-task.md | +167 (generated, not deliverable) |

**Total deliverable lines:** 560 net (excluding generated planning artifact)
**All 45 tests pass.**

## Critical Findings

None.

## Major Findings

**1. prepare-runbook.py:5,21,32,1464 — Stale docstring and usage text**
- Axis: Conformance, Functional correctness
- The module docstring (lines 5, 21, 32) and `--help` usage text (line 1464) still reference the old `<runbook-name>-task.md` naming convention
- Design Key Decision 7: "The `<plan>-task` naming convention is replaced by `crew-<plan>[-p<N>]`"
- Users running the script or reading `--help` get incorrect guidance about output file naming
- Lines:
  - `5: 1. Plan-specific agent (.claude/agents/<runbook-name>-task.md)`
  - `21: #   .claude/agents/foo-task.md (uses artisan.md baseline)`
  - `32: #   .claude/agents/tdd-test-task.md (uses test-driver.md baseline)`
  - `1464: "  - Plan-specific agent (.claude/agents/<runbook-name>-task.md)"`

## Minor Findings

**2. prepare-runbook.py:1097 — Dead-code fallback header text**
- `f"Execute steps sequentially using {runbook_name}-task agent."` fires only when `phase_agents` is None
- Normal execution path via `validate_and_create()` always populates `phase_agents`
- Retained for backward compatibility of direct `generate_default_orchestrator()` callers, but references the superseded naming convention

**3. test_prepare_runbook_inline.py — Stale variable naming at 5 call sites**
- `derive_paths()` second return value is now `agents_dir` (a directory) but local variable is still named `agent_path` (lines 168, 214, 258, 297, 340)
- Runbook Cycle 2.3 specified this file for update but the rename was not applied
- Tests pass because values flow positionally — no functional impact
- Consistency gap: the other 3 test files (mixed, orchestrator, phase_context) were correctly updated

**4. test_prepare_runbook_agents.py:167-175 — Loose table row assertions**
- Phase-Agent Mapping table test uses `"| 1 |" in result` and `"tdd" in result` — could match unintended content in larger output
- Acceptable for current function scope but fragile if output grows

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| FR-1: Per-phase agents with phase-scoped context | Covered | Cycles 1.1-1.4, `generate_phase_agent()`, `detect_phase_types()` |
| FR-2: Same base type, injected context differentiator | Covered | `get_phase_baseline_type()` → test-driver/artisan, context layers |
| FR-3: Orchestrate-evolution dispatch compatibility | Covered | `Agent:` field per step, `subagent_type` reads from plan |
| Key Decision 1: `crew-<plan>-p<N>` naming | Covered | `generate_agent_frontmatter()`, `validate_and_create()` |
| Key Decision 2: Baseline per phase type | Covered | `get_phase_baseline_type()` + `read_baseline_agent()` |
| Key Decision 3: 5-layer context composition | Covered | `generate_phase_agent()` with ordering test |
| Key Decision 4: Common context in every agent | Covered | `validate_and_create()` passes `plan_context` |
| Key Decision 5: Phase preamble as phase context | Covered | `extract_phase_preambles()` → `generate_phase_agent()` |
| Key Decision 6: Orchestrator plan format | Covered | `Phase-Agent Mapping` table, `Agent:` per step |
| Key Decision 7: Old naming replaced | Partial | Code emits new names; docstring/usage still references old |
| Key Decision 8: Orchestrate-evolution compat | Covered | SKILL.md Section 3.1 reads `Agent:` field |
| Inline phase → no agent | Covered | `(orchestrator-direct)` in mapping, no file created |
| Existing test regression updates | Partial | 3 of 4 test files updated; inline test has stale variable names |

**Missing deliverables:** None.
**Unspecified deliverables:** `.claude/agents/phase-scoped-agents-task.md` — generated planning artifact from pre-change code (expected, not excess).

## Summary

- Critical: 0
- Major: 1 (stale docstring/usage in prepare-runbook.py) — **FIXED**
- Minor: 3 — 2 fixed (fallback text, stale test variable naming), 1 deferred (loose assertions)
