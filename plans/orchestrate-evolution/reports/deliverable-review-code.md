# Deliverable Review: Code Artifacts

**Reviewer scope:** `prepare-runbook.py`, `verify-red.sh`, `verify-step.sh`, `pytest_helpers.py`
**Design reference:** `plans/orchestrate-evolution/design.md`
**Date:** 2026-03-02

## Summary

38/38 tests pass. The core implementation is functionally sound: agent caching model (D-2), orchestrator plan format, TDD agent generation (D-5), step file splitting, verification scripts, and corrector agent generation all conform to the design. Four findings identified: one Major (dead code), one Major (phase summaries not generated from preambles), two Minor.

## Findings

### F-1: Dead code — `generate_phase_agent` and `generate_agent_frontmatter` (Major)

**File:** `agent-core/bin/prepare-runbook.py:999-1030`
**Axis:** Excess, modularity

`generate_agent_frontmatter()` (lines 999-1010) and `generate_phase_agent()` (lines 1013-1030) are no longer called from `validate_and_create()` or any test. They were replaced by `generate_task_agent()` and `generate_corrector_agent()` but never removed. Both still use the old `crew-` naming convention, which contradicts the design's `<plan>-task` naming.

Additionally, line 1506 in `generate_default_orchestrator` has a stale fallback `f"crew-{runbook_name}-p{p}"` in the Phase-Agent Mapping table, using the old naming convention.

**Resolution:** Delete `generate_agent_frontmatter`, `generate_phase_agent`, and update line 1506 fallback to use the new naming convention.

### F-2: Phase summaries use static placeholders instead of preamble content (Major)

**File:** `agent-core/bin/prepare-runbook.py:1548-1555` (generation), `1829-1840` (call site)
**Axis:** Conformance, functional completeness

Design specification (line 277): "Phase summaries: IN/OUT scope for checkpoint delegation. Generated from runbook phase descriptions."

The `generate_default_orchestrator` function accepts a `phase_preambles` parameter (line 1389) and documents it (line 1404: "preamble text for summaries"), but the phase summaries section (lines 1548-1555) always emits `- IN: (placeholder)` / `- OUT: (placeholder)` without using the preambles. Furthermore, the call site in `validate_and_create` (line 1829) does not pass `phase_preambles` at all, despite having it available.

This means the orchestrator plan always contains placeholder summaries, so the corrector agent never receives meaningful IN/OUT scope during checkpoint delegation (per design D-3 checkpoint prompt format, lines 219-229).

**Resolution:** Either use `phase_preambles` to populate the IN/OUT entries, or accept that preambles don't map cleanly to IN/OUT and use a different source. Pass `phase_preambles` from `validate_and_create` regardless.

### F-3: Task agent scope enforcement missing "Do NOT read ahead" clause (Minor)

**File:** `agent-core/bin/prepare-runbook.py:1076`
**Axis:** Conformance

Design specification (line 142): `**Scope enforcement:** Execute ONLY the step file provided in your prompt. Do NOT read or execute other step files. Do NOT read ahead in the runbook.`

Implementation (line 1076): `**Scope enforcement:** Execute ONLY the step file assigned by the orchestrator. Do not read or execute other step files.`

The "Do NOT read ahead in the runbook" clause is absent. This clause prevents the task agent from reading subsequent step files to understand future work, which could bias implementation.

**Resolution:** Append the missing clause to the scope enforcement footer.

### F-4: `# Runbook-Specific Context` section from design replaced by `## Common Context` under `# Plan Context` (Minor)

**File:** `agent-core/bin/prepare-runbook.py:1047-1048` (`_build_plan_context_section`)
**Axis:** Conformance

Design specification (lines 123-145) shows the task agent structure with two top-level sections:
- `# Plan Context` containing `## Design` and `## Runbook Outline`
- `# Runbook-Specific Context` containing `[Common Context section from runbook, if any]`

Implementation places Common Context as `## Common Context` under `# Plan Context` (line 1048), merging it into the plan context section instead of keeping it as a separate top-level section.

This is a reasonable simplification (fewer top-level headings, same content), but deviates from the design's structure.

**Resolution:** Accept as intentional simplification (recommended) or restructure to match design exactly. If accepting, update the design document to reflect the actual structure.

## Non-Findings (Conformance Verified)

- **Agent caching model (D-2):** `generate_task_agent` creates single `{name}-task.md` with design+outline embedding, scope enforcement footer, clean tree footer. Correct baseline selection (artisan for general/mixed, test-driver for TDD). Corrector agent generated for multi-phase plans only, always model: sonnet.
- **TDD agent generation (D-5):** Four agent types generated via data-driven `_TDD_ROLES` constant. Tester/implementer use `tdd` (test-driver.md) baseline; test-corrector/impl-corrector use `corrector` baseline. All four embed `# Plan Context`. Role-specific footers present.
- **Step file splitting:** `split_cycle_content` correctly separates on `**GREEN Phase:**` marker. `validate_and_create` writes `step-N-M-test.md` and `step-N-M-impl.md` per cycle.
- **Orchestrator plan format:** Structured header with `**Agent:**`, `**Corrector Agent:**`, `**Type:**` fields. Pipe-delimited step entries with `filename | Phase | model | max_turns [| role] [| PHASE_BOUNDARY]`. TDD plans include `**Tester Agent:**` and `**Implementer Agent:**` fields.
- **max_turns extraction:** `extract_step_metadata` parses `**Max Turns**:` field, defaults to `_DEFAULT_MAX_TURNS` (30). Propagated to orchestrator plan step entries.
- **verify-step.sh:** Matches design specification exactly — git status, submodule check (with `|| true` guard for repos without submodules), precommit validation. Exit 0/1 contract honored.
- **verify-red.sh:** Matches design specification — takes test file path argument, runs pytest, inverts exit code. Input validation (argument count, file existence) present. Exit 0 = RED confirmed, exit 1 = not RED.
- **pytest_helpers.py:** `setup_baseline_agents` correctly adds corrector.md baseline alongside existing artisan.md and test-driver.md. test-driver.md header updated to match `# TDD Task Agent - Baseline Template` pattern used in assertions.
- **Pure TDD runbooks:** Skip task agent generation (line 1721: `if runbook_type != "tdd"`), generate only the 4 TDD agents. Orchestrator plan shows `**Agent:** none` for pure TDD.
- **Mixed runbooks:** Generate task agent (for general phases) AND TDD agents (for TDD phases). Both agent types created correctly.
- **Backward compatibility (NFR-2):** Old `generate_phase_agent` is dead code (not breaking), new functions are additive. Clean break as specified.

## Test Coverage Assessment

| Feature | Test file | Coverage |
|---------|-----------|----------|
| Single task agent | `test_prepare_runbook_agent_caching.py` | Good (multi-phase, mixed, inline) |
| Corrector agent | `test_prepare_runbook_agent_caching.py` | Good (multi-phase yes, single-phase no) |
| Design embedding | `test_prepare_runbook_agent_context.py` | Good (present, missing) |
| Outline embedding | `test_prepare_runbook_agent_context.py` | Good (runbook section, file, priority, fallback) |
| Orchestrator plan format | `test_prepare_runbook_orchestrator.py` | Good (structure, boundaries, summaries, max_turns) |
| TDD agents | `test_prepare_runbook_tdd_agents.py` | Good (4 types, baselines, plan context, directives) |
| Step splitting | `test_prepare_runbook_tdd_agents.py` | Good (split vs unsplit) |
| Role markers | `test_prepare_runbook_tdd_agents.py` | Good (TEST/IMPLEMENT presence and ordering) |
| verify-red.sh | `test_verify_red.py` | Good (pass, fail, missing file) |
| verify-step.sh | `test_verify_step.py` | Good (clean, uncommitted, untracked) |
| Phase summaries content | — | Gap (only checks structure exists, not content generation from preambles) |
