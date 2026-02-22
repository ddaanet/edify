# Outline: Runbook Generation Fixes

**Design source:** `plans/hook-batch/reports/runbook-pre-execution-review.md` (3 critical, 4 major, 3 minor)

**Problem:** prepare-runbook.py generates artifacts with systematic defects. Three root causes produce 10 issues. Source phase files are correct — all defects are in generated output (T5 pipeline step).

**Secondary problem:** Phase expansion (outline to runbook-phase-*.md) introduces defects on every phase (see brief.md). All 5 hook-batch phases required review+fix passes. This is an LLM behavioral issue (OUT of scope for code fixes) but Phase 5 prose updates address it preventively by enforcing header format requirements in the expansion prompt.

## Root Cause Analysis

| Root Cause | Defects | Class |
|-----------|---------|-------|
| RC-1: No phase-level model propagation | C1 (wrong models), M3 (header/body contradiction), m3 (agent model conflict) | Model defaults to frontmatter haiku; phase-level model declarations ignored |
| RC-2: Phase context not extracted to step files | C3 (prerequisites lost), M4 (single agent has Phase 1 only), M5 (completion validation lost) | Only `## Common Context` embedded; phase preamble (prerequisites, constraints, validation) discarded |
| RC-3: Phase numbering from file boundaries | C2 (phases 3-5 off-by-one), M1 (PHASE_BOUNDARY misnumbered), M2 (interleaving) | Phase files may lack `### Phase N:` headers; `extract_sections()` relies on content headers, not file boundaries; wrong phases cascade to sort-based interleaving |

## Key Design Decisions

**D-1: Model priority chain.** Step body `**Execution Model**` > phase-level model > frontmatter `model:` > 'haiku'. Parse phase model from phase header metadata (e.g., `### Phase 1: ... (model: sonnet)`) or first `**Execution Model**:` in phase preamble.

**D-2: Phase context injection into step files.** Extract phase preamble (content between `### Phase N:` header and first `## Step/Cycle`) → inject as `## Phase Context` section in each step file, before the step body. Step files become self-contained.

**D-3: Phase numbering from file boundaries during assembly.** `assemble_phase_files()` knows each file's phase number from the filename (`runbook-phase-N.md`). Current implementation concatenates with `'\n'.join(assembled_parts)` without injecting headers. Fix: inject `### Phase N:` headers at file boundaries during assembly if absent. This makes `extract_sections()` phase detection reliable regardless of phase file content.

**D-4: Keep single agent, not per-phase.** Per-phase agents aren't discoverable as Task subagent_types (documented learning). Orchestrator dispatches via built-in types. Phase context in step files (D-2) provides the same benefit without agent discovery issues. No implementation phase — this is a "don't change" decision. The generated single agent remains; D-2 makes it viable.

**D-5: Orchestrator plan references phase files.** PHASE_BOUNDARY entries reference the source phase file for checkpoint context. Orchestrator can read completion validation and phase-level constraints.

## Scope

**IN:**
- prepare-runbook.py: model propagation (D-1), phase context extraction (D-2), phase numbering fix (D-3), orchestrator plan improvements (D-5)
- Tests: comprehensive coverage for fixed behaviors (existing 7 inline tests untouched)
- Runbook skill (SKILL.md): minor prose to enforce phase header format in generated phase files

**OUT:**
- Phase expansion quality (LLM behavior, not structural — review+fix loop is the mitigation)
- Per-phase agent generation (D-4: not viable, Task tool can't discover custom agents)
- validate-runbook.py functional changes (validators independent; new test fixtures may update)
- Orchestrate skill changes (consumes artifacts, no changes needed if artifacts are correct)
- `assemble_phase_files()` type detection from first file only — existing behavior, mixed type detection already works via `type: mixed` in extracted sections

**Test strategy:** All TDD cycles across Phases 1-4 contribute to a single new test module `tests/test_prepare_runbook_mixed.py`. Tests use fixture runbook content (multi-phase, mixed types) to exercise the full pipeline end-to-end.

## Phase Structure

### Phase 1: Phase numbering fix (type: tdd)

RC-3 fix. `assemble_phase_files()` injects `### Phase N:` headers from filenames. Fixes C2, M1, M2.

- Cycle 1.1: Assembly injects phase headers when absent — verify assembled content has `### Phase N:` markers matching filename sequence
- Cycle 1.2: Assembly preserves existing phase headers — when phase file already has `### Phase N:` header, don't inject duplicate
- Cycle 1.3: Step phase metadata matches actual phase numbers in mixed runbook — verify `step_phases` correct for phases 3-5 in a 5-phase mixed runbook (reproduces C2)
- Cycle 1.4: Orchestrator plan produces correct PHASE_BOUNDARY labels — no interleaving in mixed runbooks (reproduces M1, M2)

Complexity: Medium (parsing logic, regex, mixed content scenarios). Model: sonnet.

### Phase 2: Model propagation (type: tdd)

RC-1 fix. Phase-level model parsed and used as default for steps without explicit model. Fixes C1, M3, m3.

- Cycle 2.1: Extract phase model from phase header metadata — `### Phase 1: ... (model: sonnet)` → phase model = sonnet
- Cycle 2.2: Phase model overrides frontmatter default — steps in phase with `model: sonnet` get sonnet, not frontmatter haiku
- Cycle 2.3: Step-level model overrides phase model — step with explicit `**Execution Model**: opus` keeps opus despite phase model being sonnet
- Cycle 2.4: Agent frontmatter uses first phase's model (not global) — generated agent model reflects the primary execution model. Also fix hardcoded `model: haiku` in `assemble_phase_files()` TDD frontmatter generation (line 498) to use detected phase model

Depends on: Phase 1 (correct phase numbering needed for phase-model mapping). Complexity: Medium. Model: sonnet.

### Phase 3: Phase context extraction (type: tdd)

RC-2 fix. Phase preamble extracted and injected into step files. Fixes C3, M4, M5.

- Cycle 3.1: Extract phase preamble from assembled content — content between phase header and first step/cycle header captured per phase
- Cycle 3.2: Step files include phase context section — generated step files have `## Phase Context` before step body
- Cycle 3.3: Cycle files include phase context section — TDD cycle files also get phase context (prerequisites are critical for TDD, per C3 evidence)
- Cycle 3.4: Phase context preserved when phase has no preamble — phases that start directly with steps/cycles produce empty context (no crash)

Depends on: Phase 1 (correct phase identification). Complexity: Medium. Model: sonnet.

### Phase 4: Orchestrator plan improvements (type: tdd)

D-5. Add phase file references to PHASE_BOUNDARY markers. Fixes M5 (orchestrator can access completion validation).

- Cycle 4.1: PHASE_BOUNDARY entries include phase file path — `Phase file: plans/<job>/runbook-phase-N.md` in boundary entries
- Cycle 4.2: Phase-agent mapping table generated with correct models — table reflects phase-level models, not global default

Depends on: Phase 2 (correct models). Complexity: Low. Model: sonnet.

### Phase 5: Skill prose updates (type: inline)

Update runbook skill to enforce phase header format in generated phase files.

- Add directive in Phase 1 expansion: "Every phase file MUST start with `### Phase N: title (type: TYPE, model: MODEL)` header. prepare-runbook.py uses this for model propagation and context extraction."
- Update Phase 2 assembly section: note that prepare-runbook.py injects missing headers from filenames (fallback, not primary)
- Note in Common Pitfalls: "Missing phase headers in phase files causes model defaults and context loss"

## Cross-Phase Dependencies

- Phase 2 depends on Phase 1 (phase numbering correctness)
- Phase 3 depends on Phase 1 (phase identification)
- Phase 4 depends on Phase 2 (model correctness)
- Phase 5 independent (prose edits)

## Affected Files

| File | Phases | Changes |
|------|--------|---------|
| `agent-core/bin/prepare-runbook.py` | 1, 2, 3, 4 | Core fixes |
| `tests/test_prepare_runbook_mixed.py` (new) | 1, 2, 3, 4 | Test coverage for mixed runbook scenarios |
| `.claude/skills/runbook/SKILL.md` | 5 | Prose: enforce phase header format |

## Evidence Mapping

| Issue | Root Cause | Fix Phase | Notes |
|-------|-----------|-----------|-------|
| C1: Wrong execution models | RC-1 | Phase 2 | Frontmatter `model: haiku` hardcoded in `assemble_phase_files()` line 498 |
| C2: Phase metadata off-by-one | RC-3 | Phase 1 | 9 of 16 step files affected |
| C3: Phase 2 content loss | RC-2 | Phase 3 | Phase preamble discarded during extraction |
| M1: PHASE_BOUNDARY misnumbered | RC-3 | Phase 1 | Cascades from C2 |
| M2: Unjustified interleaving | RC-3 | Phase 1 | Caused by sort-based ordering without phase headers |
| M3: Model header/body contradiction | RC-1 | Phase 2 | Header says haiku, body says sonnet |
| M4: Agent embeds Phase 1 only | RC-2 | Phase 3 | Single agent gets first phase context only |
| M5: Completion validation lost | RC-2 + D-5 | Phase 3, 4 | Orchestrator plan needs phase file references |
| m3: Agent model conflict | RC-1 | Phase 2 | Frontmatter vs embedded content |
| m1: Growth projection understates risk | — | OUT | hook-batch content issue, not prepare-runbook.py |
| m2: Validation-only step | — | OUT | hook-batch runbook structure, not tooling |
