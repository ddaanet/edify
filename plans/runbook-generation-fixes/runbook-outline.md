# Runbook Outline: Runbook Generation Fixes

**Design source:** `plans/runbook-generation-fixes/outline.md`
**Test strategy:** Single new module `tests/test_prepare_runbook_mixed.py` across all TDD phases. Fixture-based multi-phase mixed runbook content.

## Requirements Mapping

| Requirement | Phase | Cycles | Notes |
|-------------|-------|--------|-------|
| RC-3/C2: Phase numbering off-by-one (9 of 16 step files) | Phase 1 | 1.1, 1.3 | Header injection fixes root cause |
| RC-3/M1: PHASE_BOUNDARY misnumbered | Phase 1 | 1.3 | Cascades from C2 |
| RC-3/M2: Unjustified interleaving from sort-based ordering | Phase 1 | 1.3 | Correct phase numbers eliminate sort-based interleaving |
| Phase header preservation (no duplicates) | Phase 1 | 1.2 | Guard against re-injection |
| RC-1/C1: Wrong execution models (frontmatter haiku default) | Phase 2 | 2.1, 2.2, 2.4 | Phase model parsed from header metadata |
| RC-1/M3: Model header/body contradiction | Phase 2 | 2.2 | Phase model overrides frontmatter default |
| RC-1/m3: Agent model conflict | Phase 2 | 2.4 | Agent frontmatter uses detected model |
| D-1: Step-level model overrides phase model | Phase 2 | 2.3 | Priority chain verification |
| RC-2/C3: Phase 2 content loss (prerequisites) | Phase 3 | 3.1, 3.2 | Phase preamble extraction and injection |
| RC-2/M4: Agent embeds Phase 1 only | Phase 3 | 3.2 | Step/cycle files get phase context |
| RC-2/M5: Completion validation lost | Phase 3, 4 | 3.2, 4.1 | Phase context + orchestrator phase file refs |
| D-5: PHASE_BOUNDARY phase file references | Phase 4 | 4.1 | Orchestrator can read phase-level constraints |
| Phase-agent model mapping table | Phase 4 | 4.2 | Correct models from Phase 2 |
| No haiku default — model must be specified | Phase 2 | 2.5 | Error if model missing at all levels |
| Skill prose: enforce phase header format | Phase 5 | inline | Preventive — expansion agent guidance |
| Stale implementation-notes.md documentation | Phase 5 | inline | Update post-fix documentation |

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

- Cycle 1.3: Downstream phase metadata and orchestrator plan correct (verification)
  - Depends on: 1.1
  - **RED:** Test full pipeline on a 5-phase mixed runbook (TDD + general + inline):
    - Assert `step_phases` maps each step to correct phase number (especially phases 3-5, reproducing C2)
    - Assert orchestrator plan PHASE_BOUNDARY entries have correct phase numbers, no interleaving (M1, M2)
  - **GREEN:** With phase headers injected by 1.1, `extract_sections()` line_to_phase mapping sees correct phase boundaries, and `generate_default_orchestrator()` sorts items correctly. No additional code changes expected — header injection fixes the root cause. If tests fail, investigation targets: `extract_sections()` phase detection (line ~320-332), `generate_default_orchestrator()` (line ~743).
  - Target: `extract_sections()` (line ~320-332), `generate_default_orchestrator()` (line ~743) — verification only

### Phase 2: Model propagation (type: tdd, model: sonnet)

RC-1 fix. D-1 model priority chain: step body > phase-level > frontmatter > ERROR (no haiku default).

Depends on: Phase 1 (correct phase numbering needed for phase-model mapping).
Post-Phase-1 state: assembled content now contains `### Phase N:` headers (injected by `assemble_phase_files()` when absent). All cycles in this phase can rely on phase headers being present in assembled content.

- Cycle 2.1: Extract phase model from phase header metadata
  - **RED:** Test a new `extract_phase_models()` function. Input: assembled content with `### Phase 1: Core (type: tdd, model: sonnet)`. Assert returns `{1: 'sonnet'}`.
  - **GREEN:** Implement `extract_phase_models()` — parse `model: MODEL` from phase header parentheticals. Return dict mapping phase number to model string.
  - Target: New function in prepare-runbook.py

- Cycle 2.2: Phase model overrides frontmatter default
  - Depends on: 2.1
  - **RED:** Test full pipeline on mixed runbook where Phase 1 has `model: sonnet` but frontmatter `model: haiku`. Assert generated step file has `**Execution Model**: sonnet`.
  - **GREEN:** Thread phase models through the pipeline:
    1. In `validate_and_create()` (line ~866): call `extract_phase_models()` on assembled content to get `{phase_num: model}` dict
    2. In cycle generation loop (line ~880-886): look up `phase_models.get(cycle['major'], model)` as `default_model` argument to `generate_cycle_file()`
    3. In step generation loop (line ~888-898): look up `phase_models.get(phase, model)` as `default_model` argument to `generate_step_file()`
  - Target: `validate_and_create()` (line ~866, ~880-898), `generate_cycle_file()` (line 716), `generate_step_file()` (line 687)

- Cycle 2.3: Step-level model overrides phase model
  - Depends on: 2.2
  - **RED:** Test step with explicit `**Execution Model**: opus` inside a phase with `model: sonnet`. Assert step file preserves `opus`.
  - **GREEN:** `extract_step_metadata()` (line 573) already parses step-level model via regex and returns it when present, falling back to `default_model`. With 2.2's threading, `default_model` is now the phase model instead of frontmatter model. The priority chain (step body > phase > frontmatter) is satisfied by the existing `extract_step_metadata()` logic — no code changes expected.
  - Target: `extract_step_metadata()` (line 573) — verification only

- Cycle 2.4: Agent frontmatter uses detected model (not hardcoded haiku)
  - Depends on: 2.1
  - **RED:** Test `assemble_phase_files()` output for a TDD runbook where Phase 1 has `model: sonnet`. Assert frontmatter `model:` is `sonnet`, not `haiku`.
  - **GREEN:** Modify `assemble_phase_files()` to detect phase model from first phase (line ~496-500: hardcoded `model: haiku`). Also update the general-runbook path to derive model similarly.
  - Target: `assemble_phase_files()` (line 496-500), frontmatter generation

- Cycle 2.5: Missing model produces error (no haiku default)
  - Depends on: 2.2
  - **RED:** Test runbook with no model at any level: no frontmatter `model:`, no phase `model:`, no step `**Execution Model**:`. Assert the pipeline errors (non-zero exit or False return), not silently defaults to haiku.
  - **GREEN:** Remove `'haiku'` fallback from the priority chain. In `extract_step_metadata()`: change `default_model='haiku'` parameter default. In `validate_and_create()`: after `extract_phase_models()`, verify that every step/cycle resolves to an explicit model. Error if any step has no model at any level. In `assemble_phase_files()`: remove hardcoded `model: haiku` (already addressed by 2.4 for TDD path; also verify general path).
  - Target: `extract_step_metadata()` (line 573), `validate_and_create()` (line ~866), `assemble_phase_files()` (line 496-500)

### Phase 3: Phase context extraction (type: tdd, model: sonnet)

RC-2 fix. D-2: phase preamble → `## Phase Context` section in step/cycle files.

Depends on: Phase 1 (correct phase identification).
Post-Phase-1 state: assembled content contains `### Phase N:` headers, enabling reliable phase boundary detection for preamble extraction.

- Cycle 3.1: Extract phase preamble from assembled content
  - **RED:** Test a new `extract_phase_preambles()` function. Input: assembled content with phase headers + preamble text before first step/cycle. Assert returns dict mapping phase number to preamble content.
  - **GREEN:** Implement `extract_phase_preambles()` — for each phase, extract content between `### Phase N:` header and first `## Step/Cycle` header. Return `{phase_num: preamble_text}`.
  - Target: New function in prepare-runbook.py

- Cycle 3.2: Step and cycle files include phase context section
  - Depends on: 3.1
  - **RED:** Test full pipeline on mixed runbook:
    - Assert generated step files contain `## Phase Context` section with phase preamble content before the step body
    - Assert generated TDD cycle files contain `## Phase Context` section with phase preamble
  - **GREEN:** Modify both `generate_step_file()` and `generate_cycle_file()` to accept optional `phase_context` parameter. Inject `## Phase Context\n\n{preamble}` after header metadata, before content. In `validate_and_create()`: call `extract_phase_preambles()` on assembled content, pass `phase_preambles.get(phase, '')` to step generation calls (line ~888-898) and `phase_preambles.get(cycle['major'], '')` to cycle generation calls (line ~880-886).
  - Target: `generate_step_file()` (line 687), `generate_cycle_file()` (line 716), `validate_and_create()` (line ~866 for extraction, ~880-898 for threading)

- Cycle 3.3: Phase context preserved when phase has no preamble
  - **RED:** Test phase that starts directly with `## Cycle 1.1:` after `### Phase 1:` header (no preamble text). Assert `extract_phase_preambles()` returns empty string for that phase. Assert generated step file does NOT contain `## Phase Context` section.
  - **GREEN:** `extract_phase_preambles()` returns empty string for phases with no preamble. `generate_step_file()` / `generate_cycle_file()` skip `## Phase Context` section when preamble is empty/whitespace-only.
  - Target: `extract_phase_preambles()`, `generate_step_file()`, `generate_cycle_file()`

### Phase 4: Orchestrator plan improvements (type: tdd, model: sonnet)

D-5: Phase file references in PHASE_BOUNDARY markers. Phase-agent model mapping.

Depends on: Phase 2 (correct models).
Post-Phase-2 state: `extract_phase_models()` exists and `validate_and_create()` threads per-phase models to step/cycle generation. Phase models dict is available for orchestrator plan generation.

- Cycle 4.1: PHASE_BOUNDARY entries include phase file path
  - **RED:** Test orchestrator plan output for a phase-file-assembled runbook. Assert PHASE_BOUNDARY entries contain `Phase file: plans/<job>/runbook-phase-N.md`.
  - **GREEN:** Add `phase_dir` parameter to `generate_default_orchestrator()` (line 743). When provided, append `Phase file: {phase_dir}/runbook-phase-{phase}.md` to PHASE_BOUNDARY entries (line ~798-800). In `validate_and_create()`: pass source directory path to `generate_default_orchestrator()` call (line ~904-908).
  - Target: `generate_default_orchestrator()` (line 743, ~798-800), `validate_and_create()` (line ~904-908)

- Cycle 4.2: Phase-agent mapping table with correct models
  - Depends on: 4.1
  - **RED:** Test orchestrator plan for mixed runbook with different phase models. Assert plan contains a phase-model mapping table (e.g., "Phase 1: sonnet, Phase 2: haiku").
  - **GREEN:** Add `phase_models` parameter to `generate_default_orchestrator()` (line 743). Generate a `## Phase Models` section with a table mapping phase numbers to models. In `validate_and_create()`: pass `phase_models` dict (already computed in Phase 2) to `generate_default_orchestrator()` call.
  - Target: `generate_default_orchestrator()` (line 743), `validate_and_create()` (line ~904-908)

### Phase 5: Skill prose updates (type: inline, model: opus)

Update runbook skill to enforce phase header format in generated phase files.

- Add directive in Phase 1 expansion section: "Every phase file MUST start with `### Phase N: title (type: TYPE, model: MODEL)` header. prepare-runbook.py uses this for model propagation and context extraction."
- Update Phase 2 (Assembly and Metadata) section: note that prepare-runbook.py injects missing headers from filenames as fallback
- Note in Common Pitfalls: "Missing phase headers in phase files causes model defaults and context loss"
- Update `agents/decisions/implementation-notes.md` line 350: "Common Context lives in `runbook-phase-1.md` only" → document that phase preamble is now injected into all step/cycle files via `## Phase Context` section
- Update `agents/decisions/implementation-notes.md` line 226: fix stale reference `assemble-runbook.py` → `prepare-runbook.py`

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

**No-model fixture:** A separate `RUNBOOK_NO_MODEL` fixture with no `model:` in frontmatter and no phase/step model annotations. Used by Cycle 2.5 to test error on missing model.

**Phase file fixtures:** For assembly tests (Phase 1, 2.4), create `runbook-phase-N.md` files in `tmp_path` fixture directories.

**Helpers:** Reuse `_setup_git_repo()` and `_setup_baseline_agents()` patterns from `test_prepare_runbook_inline.py`.

**Model for all TDD phases:** sonnet (medium complexity, parsing logic, regex, cross-function threading).

**Phase 5 model:** opus (skill prose — architectural artifact editing).

**Checkpoint guidance:**
- Checkpoint after Phase 1: verify `extract_sections()` produces correct `step_phases` for all 5 phases
- Checkpoint after Phase 2: verify model priority chain end-to-end (frontmatter → phase → step override)
- Phase 3 and 4 are lower risk — standard checkpoints at phase boundaries sufficient

**Collapsible candidates:**
- Cycle 1.3 is verification-only (no code changes expected). If it passes without changes, note as confirmation that header injection was sufficient.
- Cycle 2.3 is verification-only. If it passes without changes, the existing `extract_step_metadata()` priority logic is confirmed correct.

**`validate_and_create()` threading:**
- Phase 2 adds `extract_phase_models()` call and per-step model lookup
- Phase 3 adds `extract_phase_preambles()` call and per-step context threading
- Phase 4 adds `phase_dir` and `phase_models` parameters to `generate_default_orchestrator()` call
- All three modify the same function — later phases build on earlier phases' additions. Expansion should note the cumulative parameter changes.
