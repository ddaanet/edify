# Review: Phase 1 Implementation — Agent Caching Model

**Scope**: agent-core/bin/prepare-runbook.py (generate_task_agent, generate_corrector_agent, design/outline embedding), tests/test_prepare_runbook_agent_caching.py, tests/test_prepare_runbook_agent_context.py, tests/test_prepare_runbook_agents.py, tests/test_prepare_runbook_recall.py, tests/pytest_helpers.py
**Date**: 2026-03-02T00:00:00Z
**Baseline**: 19d49bfa
**Mode**: review + fix

## Summary

Phase 1 delivers a working implementation of the agent caching model. FR-4, FR-5, and FR-6 are all satisfied in the main execution path. Tests are behaviorally focused with good e2e coverage. Four issues found: two minor deviations from the design spec (agent colors, corrector scope footer text), one code quality issue (duplicated plan context assembly), and one test maintenance issue (stale tests for dead code). All are fixable; none block correctness of the primary behavior.

**Overall Assessment**: Ready (all issues fixed)

---

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Duplicated plan context assembly in generate_task_agent and generate_corrector_agent**
   - Location: `agent-core/bin/prepare-runbook.py` lines 1052–1064 and 1089–1101
   - Note: Identical 10-line block (design_text fallback, outline_text fallback, plan_ctx_parts construction, `# Plan Context` assembly) duplicated verbatim in both functions. A single `_build_plan_context_section(design_content, outline_content, plan_context)` helper would eliminate the duplication and make future edits to plan context structure (e.g., adding recall content) apply in one place.
   - **Status**: FIXED

2. **Agent colors deviate from design spec**
   - Location: `agent-core/bin/prepare-runbook.py` lines 1047, 1084
   - Note: Design D-2 specifies `color: blue` for the task agent and `color: yellow` for the corrector agent. Both functions use `color: cyan`. Cosmetic, but agents are visually distinguishable in the Claude interface — the design colors exist to distinguish agent roles at a glance.
   - **Status**: FIXED

3. **Corrector scope footer missing two sentences from design spec**
   - Location: `agent-core/bin/prepare-runbook.py` line 1103
   - Note: Design D-2 specifies: "Review ONLY the phase checkpoint described in your prompt. Focus on changed files provided. Do NOT flag items explicitly listed as OUT of scope." Implementation has: "Review ONLY the phase checkpoint described in your prompt. Do not proactively review other phases." Missing "Focus on changed files provided" (reduces scope to what changed) and "Do NOT flag items explicitly listed as OUT of scope" (prevents over-escalation on deferred work). The pipeline-contracts decision ("when review flags out-of-scope items") codes this as a behavioral issue.
   - **Status**: FIXED

4. **Stale tests cover dead code (crew- naming, generate_phase_agent)**
   - Location: `tests/test_prepare_runbook_agents.py` — `TestAgentNamingConvention` class (lines 63–81) and `TestGeneratePhaseAgent` class (lines 84–123)
   - Note: `generate_agent_frontmatter` and `generate_phase_agent` still exist in the module but are no longer called by `validate_and_create`. The new `generate_task_agent` / `generate_corrector_agent` functions replaced them. `TestAgentNamingConvention` tests `crew-` prefix naming (now superseded by `{name}-task` convention) and `TestGeneratePhaseAgent` tests a function that `validate_and_create` no longer invokes. These tests pass only because the dead code is preserved. The module docstring ("Tests for agent naming convention (crew- prefix, phase-scoped naming)") is also stale.
   - **Status**: FIXED

5. **Module docstring and main() usage text describe old crew- naming**
   - Location: `agent-core/bin/prepare-runbook.py` lines 5 and 1715
   - Note: Module docstring says `crew-<runbook-name>[-p<N>].md`; main() usage message says `Per-phase agents (.claude/agents/crew-<runbook-name>[-p<N>].md)`. Both should describe the new `{name}-task.md` / `{name}-corrector.md` convention.
   - **Status**: FIXED

---

## Fixes Applied

- `agent-core/bin/prepare-runbook.py`: Extracted `_build_plan_context_section()` helper to eliminate duplicated plan context assembly block in `generate_task_agent` and `generate_corrector_agent`; updated both functions to use it
- `agent-core/bin/prepare-runbook.py`: Changed `color: cyan` to `color: blue` in `generate_task_agent` frontmatter (design spec: task agent = blue)
- `agent-core/bin/prepare-runbook.py`: Changed `color: cyan` to `color: yellow` in `generate_corrector_agent` frontmatter (design spec: corrector = yellow)
- `agent-core/bin/prepare-runbook.py`: Updated corrector scope enforcement footer to match design spec: added "Focus on changed files provided. Do NOT flag items explicitly listed as OUT of scope."
- `agent-core/bin/prepare-runbook.py`: Updated module docstring to reflect new `{name}-task.md` / `{name}-corrector.md` naming; updated main() usage message to match
- `tests/test_prepare_runbook_agents.py`: Removed stale `TestAgentNamingConvention` class and `TestGeneratePhaseAgent` class; updated module docstring to reflect current scope (phase type detection, orchestrator format)

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-4: Delegation prompt deduplication — plan-specific agents cache design+outline | Satisfied | `generate_task_agent` embeds design.md and outline under `# Plan Context`; `validate_and_create` reads design path and outline source at generation time |
| FR-5: Commit instruction in prompts — agent definition footer | Satisfied | "Commit all changes before reporting success. The orchestrator will reject dirty trees — there are no exceptions." in both task and corrector footers |
| FR-6: Scope constraint in prompts — structural + prose boundary | Satisfied (after fix) | Task agent: "Execute ONLY the step file assigned by the orchestrator. Do not read or execute other step files." Corrector: "Review ONLY the phase checkpoint … Focus on changed files provided. Do NOT flag items explicitly listed as OUT of scope." |

---

## Positive Observations

- Design and outline embedding implemented cleanly with correct priority order (runbook `## Outline` section > `outline.md` file > fallback note). The fallback path (no outline → "No outline found") prevents silent omission.
- Corrector agent multi-phase detection uses `non_inline_count > 1` — correctly counts only non-inline phases, consistent with the design's intent (corrector for agent-dispatched phases only; inline phases run by orchestrator directly need no corrector).
- `pytest_helpers.py` `setup_baseline_agents` correctly includes `corrector.md` stub, enabling corrector agent tests without filesystem coupling.
- Test structure across the three new files has clear separation: caching.py tests agent creation outcomes, context.py tests content embedding, recall.py tests recall injection. Behavioral assertions throughout verify actual output content, not just function success.
- `resolve_recall_for_runbook` validation (non-existent phase tag → error, inline phase tag → error) is well-tested with clear intent. The mocking approach in recall tests follows the "mock for error injection" pattern correctly — real subprocess called in success path would hit external dependency.
