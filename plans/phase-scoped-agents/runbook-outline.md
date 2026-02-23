# Runbook Outline: Phase-Scoped Agent Context

**Design:** `plans/phase-scoped-agents/outline.md`
**Status:** Draft

## Requirements Mapping

| Requirement | Phase | Items |
|---|---|---|
| FR-1: Per-phase agents with phase-scoped context | 1 | 1.1–1.4 |
| FR-2: Same base type, injected context differentiator | 1 | 1.2, 1.3 |
| FR-3: Orchestrate-evolution dispatch compatibility | 2, 3 | 2.1–2.2, Phase 3 inline |

## Key Decisions (from outline)

- Naming: `crew-<plan>-p<N>` multi-phase, `crew-<plan>` single-phase
- Baseline per phase type: TDD → test-driver, general → artisan
- Context layers: frontmatter + baseline + plan context + phase context + footer
- Inline phases: no agent generated (unchanged)
- Orchestrator plan: Phase-Agent Mapping table populated, `Agent:` field per step

---

### Phase 1: Per-phase agent generation functions (type: tdd, model: sonnet)

Core functions for naming, composition, and per-phase baseline selection.

**Affected files:**
- `agent-core/bin/prepare-runbook.py` — new/modified functions
- `tests/test_prepare_runbook_agents.py` — new test file

- Cycle 1.1: Agent naming convention
  - RED: `generate_agent_frontmatter()` with `phase_num=2, total_phases=3` produces frontmatter containing `name: crew-testplan-p2`. Also test single-phase case: `total_phases=1` produces `name: crew-testplan` (no `-pN`).
  - GREEN: Add `phase_num` and `total_phases` params to `generate_agent_frontmatter()`. Use `crew-{name}-p{phase_num}` when `total_phases > 1`, `crew-{name}` otherwise. Update description to `Execute phase {N} of {name}`.

- Cycle 1.2: Per-phase baseline selection
  - RED: New function `get_phase_baseline_type(phase_content)` returns `"tdd"` when content contains `## Cycle` headers, `"general"` otherwise. Test with TDD content (has `## Cycle 1.1:`) and general content (has `## Step 1.1:`).
  - GREEN: Implement `get_phase_baseline_type()` using regex match on `## Cycle` vs `## Step`. Feed result to existing `read_baseline_agent()`.

- Cycle 1.3: Phase agent body composition
  - Depends on: 1.1, 1.2
  - RED: New function `generate_phase_agent(name, phase_num, phase_type, plan_context, phase_context, model, total_phases)` returns markdown with all 5 layers: (1) frontmatter with crew naming, (2) baseline body per phase_type, (3) plan context section, (4) phase context section, (5) clean-tree footer. Assert each layer present and ordered correctly.
  - GREEN: Implement `generate_phase_agent()` composing all layers. Uses `generate_agent_frontmatter()` for (1), `read_baseline_agent()` for (2), wraps plan/phase context in sections for (3)/(4), appends footer for (5).

- Cycle 1.4: Phase type detection from assembled content
  - Depends on: 1.2 (reuses phase classification logic)
  - RED: New function `detect_phase_types(content)` returns `{phase_num: "tdd"|"general"|"inline"}` dict. Test with mixed runbook content having TDD phase (cycles), general phase (steps), inline phase (type: inline tag). Assert correct type per phase.
  - GREEN: Implement `detect_phase_types()` — parse phase headers, classify each by scanning content between phase boundaries. Delegate per-phase classification to `get_phase_baseline_type()` for tdd/general; detect inline via `(type: inline)` tag in phase header.

### Phase 2: Orchestrator plan format and integration (type: tdd, model: sonnet)

Orchestrator plan format changes and integration through `validate_and_create()`.

**Affected files:**
- `agent-core/bin/prepare-runbook.py` — orchestrator generation, validate_and_create
- `tests/test_prepare_runbook_agents.py` — integration tests
- `tests/test_prepare_runbook_orchestrator.py` — regression updates
- `tests/test_prepare_runbook_mixed.py` — regression updates
- `tests/test_prepare_runbook_inline.py` — regression updates
- `tests/test_prepare_runbook_phase_context.py` — regression updates

- Cycle 2.1: Orchestrator plan format — Agent field and Phase-Agent Mapping table
  - Depends on: 1.4 (phase type info for table rows)
  - RED: (a) `generate_default_orchestrator()` output includes `Agent: crew-<name>-p<N>` line for each step entry — test with 2-phase TDD runbook, assert each step has its phase's agent name. (b) Orchestrator plan contains `## Phase-Agent Mapping` section with table rows: phase number, agent name, model, type — test with 3-phase runbook (TDD, general, inline), assert inline phase agent column shows "(orchestrator-direct)".
  - GREEN: Add `phase_agents` parameter (dict of phase_num → agent_name) to `generate_default_orchestrator()`. Emit `Agent: {agent_name}` after each step's `##` header line. Update header text from "Execute steps sequentially using {name}-task agent" to "Execute steps using per-phase agents." Generate mapping table before step list: `| {N} | crew-{name}-p{N} | {model} | {type} |`; inline phases show "(orchestrator-direct)" in agent column.

- Cycle 2.2: validate_and_create creates per-phase agents (with inline-skip)
  - Depends on: 1.3, 1.4, 2.1
  - RED: Integration test through `validate_and_create()`. (a) 2-phase mixed runbook (TDD phase 1, general phase 2): assert `crew-<name>-p1.md` and `crew-<name>-p2.md` created, old `<name>-task.md` NOT created, TDD agent contains test-driver baseline, general agent contains artisan baseline, both agents contain plan context, each has its own phase context. (b) 3-phase runbook (TDD, inline, general): assert `crew-<name>-p1.md` and `crew-<name>-p3.md` exist, `crew-<name>-p2.md` does NOT exist, orchestrator plan shows phase 2 as "(orchestrator-direct)".
  - GREEN: Modify `validate_and_create()`: change `agent_path` param to `agents_dir` (Path to `.claude/agents/`). Use `detect_phase_types()` to classify phases. For each non-inline phase, call `generate_phase_agent()` and write to `agents_dir / f"crew-{name}-p{N}.md"`. Skip inline phases (no agent file written). Pass `phase_agents` dict to `generate_default_orchestrator()`. Update `main()` to pass `agents_dir` instead of `agent_path`. Update `derive_paths()` to return `agents_dir` instead of single path.

- Cycle 2.3: Existing test regression updates
  - Depends on: 2.2 (API change: `agent_path` → `agents_dir`)
  - [REGRESSION] — RED is implicit: existing tests fail after 2.2 changes the `validate_and_create` signature.
  - GREEN: Update `_run_validate()` helpers in `test_prepare_runbook_mixed.py` and `test_prepare_runbook_orchestrator.py` to pass `agents_dir` instead of `agent_path`. Update direct `validate_and_create()` calls in `test_prepare_runbook_inline.py` and `test_prepare_runbook_phase_context.py` similarly. Update assertions that check for `<name>-task.md` to check for `crew-<name>[-p<N>].md`. Verify all existing tests pass with the new agent naming format.

### Phase 3: Orchestrate skill update (type: inline)

- Update `agent-core/skills/orchestrate/SKILL.md`:
  - Section 3.1, line 97: Change `subagent_type: "<runbook-name>-task"` to `subagent_type: [from orchestrator plan "Agent:" field for this step]`
  - Section 2, lines 39, 47: Update `<runbook-name>-task` references to describe per-phase agents (verification check, artifact existence description)

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Test file placement:**
- New test file `tests/test_prepare_runbook_agents.py` for Phase 1-2 tests (existing test files at 200-380 lines — avoid growth past 400)
- Phase 1 tests unit-level functions; Phase 2 tests integration through `validate_and_create()`

**API migration details:**
- `validate_and_create()` signature change: `agent_path` → `agents_dir` is a breaking change; all callers update in Phase 2
- `_run_validate()` helper exists in 2 test files (`test_prepare_runbook_mixed.py`, `test_prepare_runbook_orchestrator.py`); the other 2 files (`test_prepare_runbook_inline.py`, `test_prepare_runbook_phase_context.py`) call `validate_and_create()` directly — both patterns need updating but with different mechanics
- `derive_paths()` (line 751) currently returns `agent_path` as a single file path; change to return `agents_dir` as a directory path

**Cycle expansion:**
- Cycle 1.1: existing `generate_agent_frontmatter()` signature (line 794) takes `runbook_name, model` — new params are additive, backward compatibility via defaults
- Cycle 1.3: layer ordering assertion is the key test — verify frontmatter appears before baseline, baseline before plan context, etc.
- Cycle 2.1: two additive changes to `generate_default_orchestrator()` — implement both in one GREEN; the per-step Agent field and the mapping table are independent additions to the same function
- Cycle 2.2: largest cycle — 8 assertions across two RED sub-cases (a) 2-phase and (b) 3-phase-with-inline. If expansion exceeds comfortable size, split at the RED sub-case boundary

**Checkpoint guidance:**
- Phase 1→2 boundary: verify all 4 new functions exist and pass unit tests before starting integration work
- Phase 2→3 boundary: verify `prepare-runbook.py` end-to-end (run against a test runbook, inspect generated agents)

**References to include:**
- Design Key Decision 3 (context layering diagram) for Cycle 1.3 implementation
- Design Key Decision 6 (orchestrator plan format change) for Cycle 2.1
- Exploration report Section 7 (line numbers) for locating functions during implementation
