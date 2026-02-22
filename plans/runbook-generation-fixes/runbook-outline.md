# Runbook Outline: Runbook Generation Fixes

**Design source:** `plans/runbook-generation-fixes/outline.md`
**Test strategy:** Single new module `tests/test_prepare_runbook_mixed.py` across all TDD phases. Fixture-based multi-phase mixed runbook content.

## Requirements Mapping

| Requirement | Phase | Cycles |
|-------------|-------|--------|
| RC-3/C2: Phase numbering off-by-one (9 of 16 step files) | Phase 1 | 1.1, 1.3 |
| RC-3/M1: PHASE_BOUNDARY misnumbered | Phase 1 | 1.4 |
| RC-3/M2: Unjustified interleaving from sort-based ordering | Phase 1 | 1.4 |
| Phase header preservation (no duplicates) | Phase 1 | 1.2 |
| RC-1/C1: Wrong execution models (frontmatter haiku default) | Phase 2 | 2.1, 2.2, 2.4 |
| RC-1/M3: Model header/body contradiction | Phase 2 | 2.2 |
| RC-1/m3: Agent model conflict | Phase 2 | 2.4 |
| D-1: Step-level model overrides phase model | Phase 2 | 2.3 |
| RC-2/C3: Phase 2 content loss (prerequisites) | Phase 3 | 3.1, 3.2, 3.3 |
| RC-2/M4: Agent embeds Phase 1 only | Phase 3 | 3.2, 3.3 |
| RC-2/M5: Completion validation lost | Phase 3, 4 | 3.2, 4.1 |
| D-5: PHASE_BOUNDARY phase file references | Phase 4 | 4.1 |
| Phase-agent model mapping table | Phase 4 | 4.2 |
| Skill prose: enforce phase header format | Phase 5 | inline |

## Phase Structure

### Phase 1: Phase numbering fix (type: tdd, model: sonnet)

RC-3 fix. `assemble_phase_files()` injects `### Phase N:` headers from filenames when absent.

- Cycle 1.1: Assembly injects phase headers when absent
  - **RED:** Test `assemble_phase_files()` on a 3-phase directory where phase files lack `### Phase N:` headers. Assert assembled content contains `### Phase 1:`, `### Phase 2:`, `### Phase 3:` markers in sequence.
  - **GREEN:** Modify `assemble_phase_files()` to inject `### Phase N: (from file)` header before each phase file's content when no `### Phase N:` header found in the file.
  - Target: `assemble_phase_files()` (line ~489, before `assembled_parts.append(content)`)

- Cycle 1.2: Assembly preserves existing phase headers
  - **RED:** Test `assemble_phase_files()` on phase files that already contain `### Phase N:` headers. Assert no duplicate headers in assembled output.
  - **GREEN:** The injection logic checks for existing headers before adding — skip injection when `### Phase N:` already present in file content.
  - Target: Same injection logic from Cycle 1.1

- Cycle 1.3: Step phase metadata correct in mixed runbook
  - **RED:** Test full pipeline on a 5-phase mixed runbook (TDD + general + inline). Assert `step_phases` maps each step to correct phase number (especially phases 3-5, reproducing C2).
  - **GREEN:** With phase headers injected by 1.1, `extract_sections()` line_to_phase mapping now sees correct phase boundaries. May need no additional code changes — the header injection should fix the root cause.
  - Target: `extract_sections()` phase detection (line ~320-332)

- Cycle 1.4: Orchestrator plan correct PHASE_BOUNDARY labels
  - Depends on: 1.3
  - **RED:** Test orchestrator plan output for a 5-phase mixed runbook. Assert PHASE_BOUNDARY entries have correct phase numbers, no interleaving (M1, M2).
  - **GREEN:** With correct `step_phases` from 1.3, `generate_default_orchestrator()` sorts items correctly. Verify no additional changes needed.
  - Target: `generate_default_orchestrator()` (line ~743)

### Phase 2: Model propagation (type: tdd, model: sonnet)

RC-1 fix. D-1 model priority chain: step body > phase-level > frontmatter > 'haiku'.

Depends on: Phase 1 (correct phase numbering needed for phase-model mapping).

- Cycle 2.1: Extract phase model from phase header metadata
  - **RED:** Test a new `extract_phase_models()` function. Input: assembled content with `### Phase 1: Core (type: tdd, model: sonnet)`. Assert returns `{1: 'sonnet'}`.
  - **GREEN:** Implement `extract_phase_models()` — parse `model: MODEL` from phase header parentheticals. Return dict mapping phase number to model string.
  - Target: New function in prepare-runbook.py

- Cycle 2.2: Phase model overrides frontmatter default
  - Depends on: 2.1
  - **RED:** Test `generate_cycle_file()` / `generate_step_file()` when called with phase-level model. Cycle in phase with `model: sonnet` but frontmatter `model: haiku`. Assert step file has `**Execution Model**: sonnet`.
  - **GREEN:** Thread phase models through the pipeline: `extract_phase_models()` → pass per-step default to `extract_step_metadata()` calls. Update `validate_and_create()` to look up phase model for each step/cycle.
  - Target: `validate_and_create()` (line ~880-898), `generate_cycle_file()` (line 716), `generate_step_file()` (line 687)

- Cycle 2.3: Step-level model overrides phase model
  - Depends on: 2.2
  - **RED:** Test step with explicit `**Execution Model**: opus` inside a phase with `model: sonnet`. Assert step file preserves `opus`.
  - **GREEN:** `extract_step_metadata()` already parses step-level model. Priority chain: if step has explicit model, use it; else use phase model. Verify the threading from 2.2 doesn't override explicit step models.
  - Target: `extract_step_metadata()` (line 573) — verify existing behavior, may need no changes

- Cycle 2.4: Agent frontmatter uses detected model (not hardcoded haiku)
  - Depends on: 2.1
  - **RED:** Test `assemble_phase_files()` output for a TDD runbook where Phase 1 has `model: sonnet`. Assert frontmatter `model:` is `sonnet`, not `haiku`.
  - **GREEN:** Modify `assemble_phase_files()` to detect phase model from first phase (line ~496-500: hardcoded `model: haiku`). Also update the general-runbook path to derive model similarly.
  - Target: `assemble_phase_files()` (line 496-500), frontmatter generation

### Phase 3: Phase context extraction (type: tdd, model: sonnet)

RC-2 fix. D-2: phase preamble → `## Phase Context` section in step/cycle files.

Depends on: Phase 1 (correct phase identification).

- Cycle 3.1: Extract phase preamble from assembled content
  - **RED:** Test a new `extract_phase_preambles()` function. Input: assembled content with phase headers + preamble text before first step/cycle. Assert returns dict mapping phase number to preamble content.
  - **GREEN:** Implement `extract_phase_preambles()` — for each phase, extract content between `### Phase N:` header and first `## Step/Cycle` header. Return `{phase_num: preamble_text}`.
  - Target: New function in prepare-runbook.py

- Cycle 3.2: Step files include phase context section
  - Depends on: 3.1
  - **RED:** Test full pipeline on mixed runbook. Assert generated step files contain `## Phase Context` section with phase preamble content before the step body.
  - **GREEN:** Modify `generate_step_file()` to accept optional `phase_context` parameter. Inject `## Phase Context\n\n{preamble}` after header, before step content. Thread from `validate_and_create()`.
  - Target: `generate_step_file()` (line 687), `validate_and_create()` (line ~888-898)

- Cycle 3.3: Cycle files include phase context section
  - Depends on: 3.1
  - **RED:** Test TDD cycle files from mixed runbook. Assert cycle files contain `## Phase Context` section with phase preamble.
  - **GREEN:** Modify `generate_cycle_file()` to accept optional `phase_context` parameter. Same injection pattern as 3.2.
  - Target: `generate_cycle_file()` (line 716), `validate_and_create()` (line ~880-886)

- Cycle 3.4: Phase context preserved when phase has no preamble
  - **RED:** Test phase that starts directly with `## Cycle 1.1:` after `### Phase 1:` header (no preamble text). Assert no crash, step file has empty or absent phase context section.
  - **GREEN:** `extract_phase_preambles()` returns empty string for phases with no preamble. `generate_step_file()` / `generate_cycle_file()` skip `## Phase Context` section when preamble is empty.
  - Target: `extract_phase_preambles()`, `generate_step_file()`, `generate_cycle_file()`

### Phase 4: Orchestrator plan improvements (type: tdd, model: sonnet)

D-5: Phase file references in PHASE_BOUNDARY markers. Phase-agent model mapping.

Depends on: Phase 2 (correct models).

- Cycle 4.1: PHASE_BOUNDARY entries include phase file path
  - **RED:** Test orchestrator plan output for a phase-file-assembled runbook. Assert PHASE_BOUNDARY entries contain `Phase file: plans/<job>/runbook-phase-N.md`.
  - **GREEN:** Modify `generate_default_orchestrator()` to accept optional `phase_dir` parameter. When provided, PHASE_BOUNDARY lines include `Phase file:` reference.
  - Target: `generate_default_orchestrator()` (line 743), `validate_and_create()` call site

- Cycle 4.2: Phase-agent mapping table with correct models
  - Depends on: 4.1
  - **RED:** Test orchestrator plan for mixed runbook with different phase models. Assert plan contains a phase-model mapping table (e.g., "Phase 1: sonnet, Phase 2: haiku").
  - **GREEN:** Modify `generate_default_orchestrator()` to generate a phase-model table section from the phase models dict. Thread `phase_models` parameter through.
  - Target: `generate_default_orchestrator()` (line 743)

### Phase 5: Skill prose updates (type: inline)

Update runbook skill to enforce phase header format in generated phase files.

- Add directive in Phase 1 expansion section: "Every phase file MUST start with `### Phase N: title (type: TYPE, model: MODEL)` header. prepare-runbook.py uses this for model propagation and context extraction."
- Update Phase 2 (Assembly and Metadata) section: note that prepare-runbook.py injects missing headers from filenames as fallback
- Note in Common Pitfalls: "Missing phase headers in phase files causes model defaults and context loss"

## Cross-Phase Dependencies

```
Phase 1 ← Phase 2 (numbering → model mapping)
Phase 1 ← Phase 3 (numbering → phase identification)
Phase 2 ← Phase 4 (models → orchestrator plan)
Phase 5: independent
```

## Expansion Guidance

**Test module:** All cycles write to `tests/test_prepare_runbook_mixed.py`. Phase 1 creates the module with fixtures; subsequent phases add test classes.

**Fixture design:** A single `MIXED_RUNBOOK_5PHASE` fixture with 5 phases:
- Phase 1: general steps (model: sonnet)
- Phase 2: TDD cycles (model: sonnet)
- Phase 3: general steps (no explicit model — inherits frontmatter)
- Phase 4: TDD cycles (model: opus) — tests model override
- Phase 5: inline (model: sonnet)

This fixture exercises all code paths: general, TDD, inline, model inheritance, model override.

**Phase file fixtures:** For assembly tests (Phase 1, 2.4), create `runbook-phase-N.md` files in `tmp_path` fixture directories.

**Helpers:** Reuse `_setup_git_repo()` and `_setup_baseline_agents()` patterns from `test_prepare_runbook_inline.py`.

**Model for all TDD phases:** sonnet (medium complexity, parsing logic, regex, cross-function threading).

**Phase 5 model:** opus (skill prose — architectural artifact editing).
