# Runbook Review: Runbook Generation Fixes (Holistic)

**Artifact**: plans/runbook-generation-fixes/runbook-phase-{1-4}.md
**Date**: 2026-02-22T00:00:00Z
**Mode**: review + fix-all (cross-phase only)
**Phase types**: Mixed (4 TDD, 1 inline — Phase 5 is inline, no phase file)
**Scope**: Cross-phase concerns only — per-phase reviews already applied

## Summary

Holistic review covers cross-phase dependency ordering, cycle numbering consistency, `validate_and_create()` parameter threading, file path validation, and requirements satisfaction. All file paths referenced in phase files exist on disk. All outline requirements are mapped to cycles. Cycle numbering is internally consistent and matches runbook-outline counts after legitimate consolidations (outline 1.3+1.4 → runbook 1.3; outline 3.3+3.4 → runbook 3.2+3.3). Two minor issues found and fixed.

**Overall Assessment**: Ready

## Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Phase 4 prerequisite list incomplete — Phase 3 dependency not documented**
   - Location: Phase 4 header prerequisites
   - Problem: Phase 4 Prerequisites lists "Phase 2 complete" but not Phase 3. The cross-phase dependency chain (outline + runbook-outline) says Phase 4 depends on Phase 2 only, and Phase 3 can run concurrently with Phase 4. However, both Phase 3 and Phase 4 modify `validate_and_create()` signature — an executor running them sequentially (the typical case) needs to know the cumulative signature state when implementing Phase 4. Without noting Phase 3's additions, the implementing agent may write incompatible function signatures. The current prerequisite note only mentions Phase 2 state.
   - Fix: Add note about cumulative `validate_and_create()` signature to Phase 4's post-phase state context.
   - **Status**: FIXED

2. **Phase 4 Cycle 4.2 test fixture ambiguity — "inherits frontmatter model" not explicit**
   - Location: Phase 4, Cycle 4.2 RED Phase, Setup
   - Problem: "Phase 3: no explicit model (inherits frontmatter `model: haiku`)" doesn't make clear the frontmatter must explicitly contain `model: haiku`. After Phase 2's Cycle 2.5 removes the haiku default fallback, the pipeline errors on missing model. An executor writing the test fixture might create a runbook with no frontmatter `model:` line, causing the pipeline to error before reaching orchestrator generation — making the RED failure come from the wrong cause (model validation error, not missing `## Phase Models` section).
   - Fix: Clarify the test setup to explicitly state `model: haiku` in frontmatter.
   - **Status**: FIXED

## Cross-Phase Analysis

### Cycle numbering consistency

Phase files match runbook-outline counts exactly:

| Phase | Outline cycles | Runbook-outline cycles | Phase file cycles |
|-------|---------------|----------------------|------------------|
| 1 | 1.1–1.4 (4) | 1.1–1.3 (3, 1.3+1.4 merged) | 1.1–1.3 (3) ✓ |
| 2 | 2.1–2.5 (5) | 2.1–2.5 (5) | 2.1–2.5 (5) ✓ |
| 3 | 3.1–3.4 (4) | 3.1–3.3 (3, 3.2+3.3 merged) | 3.1–3.3 (3) ✓ |
| 4 | 4.1–4.2 (2) | 4.1–4.2 (2) | 4.1–4.2 (2) ✓ |

Consolidations are valid:
- 1.3+1.4 → 1.3: Both were orchestrator plan verification cycles. Merged test covers both `step_phases` correctness (C2) and PHASE_BOUNDARY ordering (M1, M2) in one fixture.
- 3.2+3.3 → 3.2: Outline 3.2 tested step files; 3.3 tested cycle files. Phase file 3.2 tests both. Outline 3.4 (empty preamble) → Phase file 3.3.

Phase completion validation counts in phase file headers are accurate:
- Phase 1: "All 3 cycles pass" ✓
- Phase 2: "All 5 cycles pass" ✓
- Phase 3: "All 3 cycles pass" ✓
- Phase 4: "All 2 cycles pass" ✓

### validate_and_create() cumulative parameter threading

Additions across phases are non-conflicting and additive:

| Phase | Parameter added to validate_and_create() | Passed from main() |
|-------|------------------------------------------|-------------------|
| Phase 2 | `phase_models` | `extract_phase_models(body)` |
| Phase 3 | `phase_preambles` | `extract_phase_preambles(body)` |
| Phase 4 | `phase_dir` | source directory path (directory input branch) |

Phase 4 also passes `phase_models` (received from Phase 2) and `model` (frontmatter) to `generate_default_orchestrator()`. This is valid — `phase_models` is already in the Phase 4 function signature via Phase 2's addition.

Phase 3 and Phase 4 have independent dependency chains (both depend on Phase 1/Phase 2 respectively) and can run concurrently per design. When run sequentially, the implementing agent for Phase 4 must be aware that `validate_and_create()` already has `phase_models` and `phase_preambles` parameters before adding `phase_dir`. Fixed in Phase 4 header.

### File path validation

All paths referenced across phases verified to exist:

| Path | Phase reference | Status |
|------|----------------|--------|
| `agent-core/bin/prepare-runbook.py` | All phases | Exists ✓ |
| `tests/test_prepare_runbook_inline.py` | All phases (regression check) | Exists ✓ |
| `tests/test_prepare_runbook_mixed.py` | All phases (new, created in Phase 1) | New file — correct ✓ |
| `.claude/skills/runbook/SKILL.md` | Phase 5 inline | Exists ✓ |
| `agents/decisions/implementation-notes.md` | Phase 5 inline | Exists ✓ |

Function references validated against actual prepare-runbook.py line numbers:

| Function | Cited line | Actual line | Match |
|----------|-----------|-------------|-------|
| `extract_sections()` | ~298-427 | 298 | ✓ |
| `assemble_phase_files()` | ~430-515 | 430 | ✓ |
| `extract_step_metadata()` | ~573-606 | 573 | ✓ |
| `generate_step_file()` | ~687-713 | 687 | ✓ |
| `generate_cycle_file()` | ~716-740 | 716 | ✓ |
| `generate_default_orchestrator()` | ~743-805 | 743 | ✓ |
| `validate_and_create()` | ~808-929 | 808 | ✓ |
| `extract_cycles()` | ~103 | 103 | ✓ |
| `parse_frontmatter()` | ~63 | 63 | ✓ |

### Requirements satisfaction

All requirements from `plans/runbook-generation-fixes/outline.md` are mapped:

| Requirement | Phase | Cycles | Covered |
|-------------|-------|--------|---------|
| RC-3/C2: Phase numbering off-by-one | 1 | 1.1, 1.3 | ✓ |
| RC-3/M1: PHASE_BOUNDARY misnumbered | 1 | 1.3 | ✓ |
| RC-3/M2: Unjustified interleaving | 1 | 1.3 | ✓ |
| Phase header preservation (no duplicates) | 1 | 1.2 | ✓ |
| RC-1/C1: Wrong execution models | 2 | 2.1, 2.2, 2.4 | ✓ |
| RC-1/M3: Model header/body contradiction | 2 | 2.2 | ✓ |
| RC-1/m3: Agent model conflict | 2 | 2.4 | ✓ |
| D-1: Step-level model overrides phase model | 2 | 2.3 | ✓ |
| No haiku default — model must be specified | 2 | 2.5 | ✓ |
| RC-2/C3: Phase 2 content loss (prerequisites) | 3 | 3.1, 3.2 | ✓ |
| RC-2/M4: Agent embeds Phase 1 only | 3 | 3.2 | ✓ |
| RC-2/M5: Completion validation lost | 3, 4 | 3.2, 4.1 | ✓ |
| D-5: PHASE_BOUNDARY phase file references | 4 | 4.1 | ✓ |
| Phase-agent model mapping table | 4 | 4.2 | ✓ |
| Skill prose: enforce phase header format | 5 | inline | ✓ |
| Stale implementation-notes.md documentation | 5 | inline | ✓ |

### Cross-phase dependency ordering

Dependency chain from runbook-outline: Phase 1 ← Phase 2, Phase 1 ← Phase 3, Phase 2 ← Phase 4, Phase 5 independent.

Phase file "Post-Phase-N state" notes correctly document upstream state for each phase:
- Phase 2: "Post-Phase-1 state: assembled content contains `### Phase N:` headers" ✓
- Phase 3: "Post-Phase-1 state: assembled content contains `### Phase N:` headers, enabling reliable phase boundary detection" ✓
- Phase 4: "Post-Phase-2 state: `extract_phase_models()` exists and `validate_and_create()` threads per-phase models" ✓

No cross-phase dependency ordering violations found. All phases use results from upstream phases without forward references.

### Model declarations

All TDD phases declare `model: sonnet` in their headers, consistent with runbook-outline guidance ("Model for all TDD phases: sonnet").

Phase 5 (inline) has no phase file — correct per design.

## Fixes Applied

- Phase 4 header — Added cumulative signature note to "Post-Phase-2 state" context: "Phase 3 additions (if run sequentially before Phase 4): `phase_preambles` parameter added to `validate_and_create()`. When implementing Phase 4, the function signature already includes `phase_models` (Phase 2) and `phase_preambles` (Phase 3) parameters."

- Phase 4, Cycle 4.2 RED Phase setup — Clarified test fixture: Changed "Phase 3: no explicit model (inherits frontmatter `model: haiku`)" to make explicit that the runbook frontmatter must contain `model: haiku`, ensuring the test creates a valid fixture (model present at frontmatter level, absent at phase level for Phase 3).

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
