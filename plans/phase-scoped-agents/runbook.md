---
name: phase-scoped-agents
type: mixed
model: sonnet
---

# Phase-Scoped Agent Context

**Context**: Generate per-phase agents from runbooks instead of one agent per runbook.
**Design**: `plans/phase-scoped-agents/outline.md`
**Status**: Ready
**Created**: 2026-02-23

---

## Weak Orchestrator Metadata

**Total Steps**: 8 (7 TDD cycles + 1 inline phase)

**Execution Model**:
- Cycles 1.1-1.4: Sonnet (new function design, test writing)
- Cycles 2.1-2.3: Sonnet (integration, regression updates)
- Phase 3: Orchestrator-direct (inline prose edit)

**Step Dependencies**: Sequential within phases, cross-phase as noted
**Error Escalation**: Sonnet → User: architectural ambiguity, test design unclear

**Report Locations**: `plans/phase-scoped-agents/reports/`

**Success Criteria**: All existing tests pass + new tests for per-phase agent generation, orchestrator plan format updated, orchestrate skill reads Agent: field

**Prerequisites**:
- `agent-core/bin/prepare-runbook.py` exists (✓ verified)
- `agent-core/agents/test-driver.md` and `artisan.md` exist (✓ verified)
- `tests/test_prepare_runbook_*.py` exist (✓ 5 files verified)
- `agent-core/skills/orchestrate/SKILL.md` exists (✓ verified)

---

## Common Context

**Requirements (from design):**
- FR-1: Per-phase agents with phase-scoped context — Phase 1 (1.1-1.4)
- FR-2: Same base type, injected context differentiator — Phase 1 (1.2, 1.3)
- FR-3: Orchestrate-evolution dispatch compatibility — Phase 2 (2.1-2.2), Phase 3

**Scope boundaries:**
- IN: prepare-runbook.py per-phase generation, orchestrator plan format, orchestrate skill Section 3.1
- OUT: orchestrate skill rewrite, vet agent generation, ping-pong TDD, post-step remediation

**Key Constraints:**
- Naming: `crew-<plan>-p<N>` multi-phase, `crew-<plan>` single-phase
- Baseline per phase type: TDD → test-driver, general → artisan
- Context layers: frontmatter + baseline + plan context + phase context + footer
- Inline phases: no agent generated (orchestrator-direct, unchanged)
- Orchestrator plan: Phase-Agent Mapping table populated, `Agent:` field per step

**Project Paths:**
- `agent-core/bin/prepare-runbook.py` — main script under modification
- `tests/test_prepare_runbook_agents.py` — NEW test file for Phase 1-2 tests
- `tests/test_prepare_runbook_*.py` — existing test files (200-380 lines, avoid growth past 400)
- `agent-core/skills/orchestrate/SKILL.md` — Section 3.1 prose edit
- `agent-core/agents/test-driver.md` — TDD baseline template
- `agent-core/agents/artisan.md` — general baseline template

**API migration:**
- `validate_and_create()` signature change: `agent_path` → `agents_dir` (breaking, all callers update in Cycle 2.3)
- `derive_paths()` returns `agents_dir` (directory) instead of single `agent_path` (file)
- `_run_validate()` helper in 2 test files; direct `validate_and_create()` calls in 2 other test files

**Design references:**
- Key Decision 3: context layering (frontmatter + baseline + plan + phase + footer)
- Key Decision 6: orchestrator plan format (populated Phase-Agent Mapping)
- Exploration report Section 7: function line numbers

---

### Phase 1: Per-phase agent generation functions (type: tdd, model: sonnet)

Core functions for naming, composition, and per-phase baseline selection.

## Cycle 1.1: Agent naming convention

**RED Phase:**

**Test:** `test_agent_frontmatter_crew_naming_multi_phase` and `test_agent_frontmatter_crew_naming_single_phase`
**Assertions:**
- `generate_agent_frontmatter("testplan", model="sonnet", phase_num=2, total_phases=3)` produces frontmatter containing `name: crew-testplan-p2`
- Description contains `Execute phase 2 of testplan`
- `generate_agent_frontmatter("testplan", model="sonnet", phase_num=1, total_phases=1)` produces frontmatter containing `name: crew-testplan` (no `-pN` suffix)
- Description contains `Execute testplan` (no phase number for single-phase)

**Expected failure:** AttributeError or TypeError — `generate_agent_frontmatter()` doesn't accept `phase_num`/`total_phases` params yet.

**Why it fails:** Current signature is `generate_agent_frontmatter(runbook_name, model=None)` — no phase params.

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py -v -k "naming"`

**GREEN Phase:**

**Implementation:** Extend `generate_agent_frontmatter()` with `phase_num` and `total_phases` params.

**Behavior:**
- When `total_phases > 1`: name is `crew-{name}-p{phase_num}`, description is `Execute phase {phase_num} of {name}`
- When `total_phases == 1` (or defaults): name is `crew-{name}`, description is `Execute {name}`
- Both params default to allow backward-compatible calling (but old `<name>-task` naming is replaced)

**Approach:** Add keyword params with defaults. Conditional formatting in f-string.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Modify `generate_agent_frontmatter()` (line 794) — add `phase_num=1, total_phases=1` params, update name/description format strings
  Location hint: Function signature and return format string

**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v -k "naming"`
**Verify no regression:** `pytest tests/test_prepare_runbook_*.py -v`

---

## Cycle 1.2: Per-phase baseline selection

**RED Phase:**

**Test:** `test_get_phase_baseline_type_tdd` and `test_get_phase_baseline_type_general`
**Assertions:**
- `get_phase_baseline_type("## Cycle 1.1: First\n**RED Phase:**\ntest\n**GREEN Phase:**\nimpl")` returns `"tdd"`
- `get_phase_baseline_type("## Step 1.1: First\nStep content here")` returns `"general"`
- `get_phase_baseline_type("No headers, just prose")` returns `"general"` (default)

**Expected failure:** ImportError or NameError — `get_phase_baseline_type` doesn't exist yet.

**Why it fails:** Function not yet defined in prepare-runbook.py.

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py -v -k "baseline_type"`

**GREEN Phase:**

**Implementation:** New function `get_phase_baseline_type(phase_content)`.

**Behavior:**
- Scans content for `## Cycle` header pattern (regex `^##\s+Cycle\s+\d+\.\d+:`)
- Returns `"tdd"` if found, `"general"` otherwise
- Uses `strip_fenced_blocks()` to avoid matching headers inside code fences

**Approach:** Simple regex search on stripped content.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add new function `get_phase_baseline_type()` after `extract_phase_preambles()`
  Location hint: After line 647 (after `extract_phase_preambles`)

**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v -k "baseline_type"`
**Verify no regression:** `pytest tests/test_prepare_runbook_*.py -v`

---

## Cycle 1.3: Phase agent body composition

Depends on: 1.1, 1.2

**RED Phase:**

**Test:** `test_generate_phase_agent_layers`
**Assertions:**
- `generate_phase_agent("myplan", phase_num=1, phase_type="tdd", plan_context="## Common Context\nShared info", phase_context="Phase 1 preamble text", model="sonnet", total_phases=2)` returns markdown containing:
  - (1) Frontmatter block with `name: crew-myplan-p1` (from `generate_agent_frontmatter`)
  - (2) Test-driver baseline body (contains "Test Driver" from baseline template)
  - (3) Plan context section: `# Runbook-Specific Context` followed by common context
  - (4) Phase context section: `# Phase Context` followed by phase preamble
  - (5) Clean-tree footer: "Clean tree requirement"
- Layer ordering: frontmatter index < baseline index < plan context index < phase context index < footer index

**Expected failure:** ImportError or NameError — `generate_phase_agent` doesn't exist yet.

**Why it fails:** Function not yet defined.

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py -v -k "phase_agent_layers"`

**GREEN Phase:**

**Implementation:** New function `generate_phase_agent()`.

**Behavior:**
- Composes 5 layers in order:
  1. `generate_agent_frontmatter(name, model, phase_num, total_phases)` → frontmatter
  2. `read_baseline_agent(phase_type)` → baseline body
  3. Plan context: `"\n---\n# Runbook-Specific Context\n\n" + plan_context` (if non-empty)
  4. Phase context: `"\n---\n# Phase Context\n\n" + phase_context` (if non-empty)
  5. Footer: `"\n\n---\n\n**Clean tree requirement:** Commit all changes before reporting success. The orchestrator will reject dirty trees — there are no exceptions.\n"`

**Approach:** String concatenation of layers, using existing functions for 1 and 2.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add new function `generate_phase_agent()` after `generate_agent_frontmatter()`
  Location hint: After the updated `generate_agent_frontmatter()` function

**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v -k "phase_agent_layers"`
**Verify no regression:** `pytest tests/test_prepare_runbook_*.py -v`

---

## Cycle 1.4: Phase type detection from assembled content

Depends on: 1.2 (reuses phase classification logic)

**RED Phase:**

**Test:** `test_detect_phase_types_mixed`
**Assertions:**
- Given content with 3 phases:
  - Phase 1 has `## Cycle 1.1:` headers (TDD content)
  - Phase 2 has `(type: inline)` in phase header
  - Phase 3 has `## Step 3.1:` headers (general content)
- `detect_phase_types(content)` returns `{1: "tdd", 2: "inline", 3: "general"}`

**Expected failure:** ImportError or NameError — `detect_phase_types` doesn't exist yet.

**Why it fails:** Function not yet defined.

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py -v -k "detect_phase_types"`

**GREEN Phase:**

**Implementation:** New function `detect_phase_types(content)`.

**Behavior:**
- Parses phase headers from content using `^###?\s+Phase\s+(\d+):` pattern
- For each phase, extracts content between its header and the next phase header (or end)
- Classifies each:
  - If phase header contains `(type: inline)` → `"inline"`
  - Otherwise, delegates to `get_phase_baseline_type(phase_content)` → `"tdd"` or `"general"`
- Returns dict of `{phase_num: type_str}`

**Approach:** Reuse `strip_fenced_blocks()` for safe header matching. Split content at phase boundaries, classify each segment.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add new function `detect_phase_types()` after `get_phase_baseline_type()`
  Location hint: After the new `get_phase_baseline_type()` function

**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v -k "detect_phase_types"`
**Verify no regression:** `pytest tests/test_prepare_runbook_*.py -v`

---

### Phase 2: Orchestrator plan format and integration (type: tdd, model: sonnet)

Orchestrator plan format changes and integration through `validate_and_create()`.

## Cycle 2.1: Orchestrator plan format — Agent field and Phase-Agent Mapping table

Depends on: 1.4 (phase type info for table rows)

**RED Phase:**

**Test:** `test_orchestrator_agent_field_per_step` and `test_orchestrator_phase_agent_mapping_table`

**Sub-case (a) — Agent field per step:**
- `generate_default_orchestrator("testjob", cycles=[...], phase_agents={1: "crew-testjob-p1", 2: "crew-testjob-p2"})` output includes:
  - `Agent: crew-testjob-p1` after phase 1 step headers
  - `Agent: crew-testjob-p2` after phase 2 step headers
  - Header text does NOT contain "using testjob-task agent"

**Sub-case (b) — Phase-Agent Mapping table:**
- `generate_default_orchestrator("testjob", ..., phase_agents={1: "crew-testjob-p1", 2: "(orchestrator-direct)", 3: "crew-testjob-p3"}, phase_types={1: "tdd", 2: "inline", 3: "general"})` output includes:
  - `## Phase-Agent Mapping` section
  - Table row containing `1`, `crew-testjob-p1`, `tdd`
  - Table row containing `2`, `(orchestrator-direct)`, `inline`
  - Table row containing `3`, `crew-testjob-p3`, `general`

**Expected failure:** TypeError — `generate_default_orchestrator()` doesn't accept `phase_agents` or `phase_types` params.

**Why it fails:** Current signature has no `phase_agents` or `phase_types` parameters.

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py -v -k "orchestrator"`

**GREEN Phase:**

**Implementation:** Extend `generate_default_orchestrator()` with `phase_agents` and `phase_types` params.

**Behavior:**
- New params: `phase_agents` (dict of phase→agent_name), `phase_types` (dict of phase→type_str)
- Header text: "Execute steps using per-phase agents." (replaces old `{name}-task` reference)
- After step `##` header line, emit `Agent: {phase_agents[phase]}` line
- Before step list, generate `## Phase-Agent Mapping` table with columns: Phase, Agent, Model, Type
- Inline phases show "(orchestrator-direct)" in Agent column

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Modify `generate_default_orchestrator()` (line 987) — add params, emit Agent: lines, generate mapping table
  Location hint: Function signature and the step iteration loop

**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v -k "orchestrator"`
**Verify no regression:** `pytest tests/test_prepare_runbook_*.py -v`

---

## Cycle 2.2: validate_and_create creates per-phase agents (with inline-skip)

Depends on: 1.3, 1.4, 2.1

**RED Phase:**

**Test:** `test_validate_creates_per_phase_agents` and `test_validate_inline_phase_no_agent`

**Sub-case (a) — 2-phase mixed runbook (TDD phase 1, general phase 2):**
- Call `validate_and_create()` with `agents_dir` param (new signature)
- Assert: `crew-<name>-p1.md` file exists in agents_dir
- Assert: `crew-<name>-p2.md` file exists in agents_dir
- Assert: `<name>-task.md` does NOT exist (old naming gone)
- Assert: Phase 1 agent file contains "Test Driver" (test-driver baseline)
- Assert: Phase 2 agent file contains "Artisan" (artisan baseline)
- Assert: Both agents contain plan context ("Shared info" from Common Context)
- Assert: Phase 1 agent contains Phase 1 preamble; Phase 2 agent contains Phase 2 preamble

**Sub-case (b) — 3-phase runbook (TDD, inline, general):**
- Assert: `crew-<name>-p1.md` exists (TDD phase)
- Assert: `crew-<name>-p3.md` exists (general phase)
- Assert: `crew-<name>-p2.md` does NOT exist (inline phase — no agent)
- Assert: Orchestrator plan contains "(orchestrator-direct)" for phase 2

**Expected failure:** TypeError — `validate_and_create()` doesn't accept `agents_dir` param.

**Why it fails:** Current signature has `agent_path` (single file), not `agents_dir` (directory).

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py -v -k "validate_creates"`

**GREEN Phase:**

**Implementation:** Modify `validate_and_create()` to create per-phase agents.

**Behavior:**
- Replace `agent_path` param with `agents_dir` (Path to agents directory)
- Use `detect_phase_types()` to classify all phases from assembled content
- For each non-inline phase: call `generate_phase_agent()`, write to `agents_dir / f"crew-{name}-p{N}.md"`
- For single non-inline phase: use `crew-{name}.md` (no -pN)
- Build `phase_agents` dict, pass to `generate_default_orchestrator()`
- Stage all created agent files with `git add`
- Remove old single-agent creation code

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Modify `validate_and_create()` (line 1090) — new param, per-phase loop
  Location hint: Lines 1187-1205 (current agent creation block)
- File: `agent-core/bin/prepare-runbook.py`
  Action: Modify `derive_paths()` (line 751) — return `agents_dir` instead of single `agent_path`
  Location hint: Lines 762-764
- File: `agent-core/bin/prepare-runbook.py`
  Action: Update `main()` — pass `agents_dir` to `validate_and_create()`
  Location hint: Lines 1420-1432

**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v -k "validate_creates"`
**Verify no regression:** Existing tests will FAIL (expected — Cycle 2.3 handles regression)

---

## Cycle 2.3: Existing test regression updates

Depends on: 2.2 (API change: `agent_path` → `agents_dir`)

[REGRESSION] — RED is implicit: existing tests fail after 2.2 changes the `validate_and_create` signature.

**GREEN Phase:**

**Implementation:** Update all existing test files to use new `agents_dir` signature.

**Behavior:**
- `_run_validate()` helpers (2 files) change from passing `tmp_path / ".claude" / "agents" / f"{name}-task.md"` to `tmp_path / ".claude" / "agents"`
- Direct `validate_and_create()` calls (2 files) same change
- Assertions checking `agent_path.exists()` or agent content now check `agents_dir / f"crew-{name}[-p{N}].md"`
- For tests using single-phase runbooks: agent is `crew-{name}.md` (no -pN)
- For tests using multi-phase runbooks: agents are `crew-{name}-p{N}.md`

**Changes:**
- File: `tests/test_prepare_runbook_mixed.py`
  Action: Update `_run_validate()` helper and assertions
  Location hint: Lines 86-95 (helper), agent path assertions throughout
- File: `tests/test_prepare_runbook_orchestrator.py`
  Action: Update `_run_validate()` helper and assertions
  Location hint: Lines 26-44 (helper), assertions throughout
- File: `tests/test_prepare_runbook_inline.py`
  Action: Update direct `validate_and_create()` calls and assertions
  Location hint: Lines 168-182, 214-225, 258-267, 297-306, 340-348
- File: `tests/test_prepare_runbook_phase_context.py`
  Action: Update direct `validate_and_create()` calls and assertions
  Location hint: Lines 95, 193

**Verify GREEN:** `pytest tests/test_prepare_runbook_*.py -v`
**Verify no regression:** Full test suite passes

---

### Phase 3: Orchestrate skill update (type: inline)

- Update `agent-core/skills/orchestrate/SKILL.md`:
  - Section 3.1, line 97: Change `subagent_type: "<runbook-name>-task"` to `subagent_type: [from orchestrator plan "Agent:" field for this step]`
  - Section 2, line 39: Update `.claude/agents/<runbook-name>-task.md` to `.claude/agents/crew-<runbook-name>[-p<N>].md`
  - Section 2, line 47: Update `Plan-specific agent: .claude/agents/<runbook-name>-task.md` to describe per-phase agents
