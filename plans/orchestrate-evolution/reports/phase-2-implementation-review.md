# Review: Phase 2 Implementation — Orchestrator Plan Format + verify-step.sh

**Scope**: Commits 773b1324..da820a73 (Cycles 2.1–2.4), baseline 17958e8f
**Date**: 2026-03-02T00:00:00Z
**Mode**: review + fix

## Summary

Phase 2 delivers the orchestrator plan structured format rewrite and the `verify-step.sh` verification script. The structured header (`**Agent:**`, `**Corrector Agent:**`, `**Type:**`), pipe-delimited step list with `max_turns`, `PHASE_BOUNDARY` markers, `INLINE | Phase N | —` format, and phase summaries all match the design specification. The verification script matches the design contract. All 32 tests pass, precommit is green.

Four issues found: one minor test structure issue, one correctness bug in phase summary title generation (H2-in-summary double-header), one magic number repeated across four callsites, and one early-return path inconsistency. All four fixed.

**Overall Assessment**: Ready (post-fix)

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`test_verify_step_dirty_states` uses if/elif dispatch inside parametrized body**
   - Location: `tests/test_verify_step.py:90-144`
   - Note: The parametrized test body dispatches on `scenario` with `if/elif` blocks, each containing full setup + assertion sequences. This is the anti-pattern for parametrize — each variant should share the test body with scenario-specific setup extracted as a setup step, not branched inline. The current structure will grow linearly with scenarios and makes each variant harder to read in isolation.
   - **Status**: FIXED

2. **Phase summary title logic uses raw preamble first line — produces double-header**
   - Location: `agent-core/bin/prepare-runbook.py:1448-1454`
   - Note: When a `preamble` exists, `summary_title` is set to `preamble.strip().split("\n")[0]`. Phase preambles are extracted from the text between `### Phase N:` headers and the first step/cycle — so the first line IS the `### Phase N:` header (e.g., `### Phase 2: TDD (type: tdd, model: sonnet)`). This produces `### ### Phase 2: TDD (type: tdd, model: sonnet)` in the output — a double H3 prefix. The design spec shows `### Phase 0: Foundation` format.
   - **Status**: FIXED

3. **Magic number `30` for default `max_turns` repeated at four callsites**
   - Location: `agent-core/bin/prepare-runbook.py:1138, 1344, 1358, 1412`
   - Note: `30` is the default `max_turns` value, hardcoded at: `extract_step_metadata` fallback (line 1138), two `max_turns_lookup` build sites in `generate_default_orchestrator` (lines 1344, 1358), and the lookup default in the render loop (line 1412). A named constant prevents drift if the default changes.
   - **Status**: FIXED

4. **Early-return path for empty items builds header inconsistently with main path**
   - Location: `agent-core/bin/prepare-runbook.py:1372-1377`
   - Note: The empty-items early return constructs the header via three separate string concatenation lines. The main path uses an f-string template. Both produce the same structure but the early-return path separates `**Agent:**` onto a line that doesn't use the shared constant. After extracting the `_DEFAULT_MAX_TURNS` constant (fix #3), the header template is also refactored here for alignment.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_verify_step.py` — Extracted `_make_dirty_state(repo_path, scenario)` helper. Replaced if/elif dispatch with shared test body: `_setup_git_repo` + `_create_justfile` + `_make_dirty_state` + single `subprocess.run` + shared assertions. Both scenarios now covered by identical test logic.

- `agent-core/bin/prepare-runbook.py` — Added `_DEFAULT_MAX_TURNS = 30` module-level constant after `DEFAULT_TDD_COMMON_CONTEXT`. Replaced all 4 hardcoded `30` values: `extract_step_metadata` fallback, two `max_turns_lookup` build sites in `generate_default_orchestrator`, and the render-loop lookup default.

- `agent-core/bin/prepare-runbook.py:1446-1453` — Fixed phase summary title logic. Removed preamble-first-line extraction (fragile: if preamble starts with a `### Phase` line it produces double H3 prefix). Replaced with unconditional `Phase N:` title, matching the design spec format `### Phase 0: Foundation`.

- `agent-core/bin/prepare-runbook.py:1374-1380` — Aligned empty-items early-return header with the main path: replaced three-line string concatenation with a single implicit-concatenation f-string return.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Orchestrator plan structured header | Satisfied | `**Agent:**`, `**Corrector Agent:**`, `**Type:**` fields in `generate_default_orchestrator` |
| Step list pipe-delimited format | Satisfied | `- filename \| Phase N \| model \| max_turns [| PHASE_BOUNDARY]` |
| `max_turns` extraction from step content | Satisfied | `extract_step_metadata` returns `max_turns`; defaults to `_DEFAULT_MAX_TURNS` |
| `max_turns` propagated to step entries | Satisfied | `max_turns_lookup` built at item-collection time, used at render time |
| PHASE_BOUNDARY on last step of phase | Satisfied | `is_phase_boundary = (i+1==len(items)) or (items[i+1][0] != phase)` |
| INLINE marker for inline phases | Satisfied | `- INLINE \| Phase N \| —` with optional `\| PHASE_BOUNDARY` |
| Phase Summaries section | Satisfied | `## Phase Summaries` with `### Phase N:` subsections + IN:/OUT: entries |
| Single-phase: `**Corrector Agent:** none` | Satisfied | `corrector_agent = "none"` when `unique_phases == 1` |
| Multi-phase: `**Corrector Agent:** <name>-corrector` | Satisfied | `corrector_agent = f"{runbook_name}-corrector"` when `unique_phases > 1` |
| verify-step.sh: git clean check | Satisfied | `git status --porcelain` → DIRTY + exit 1 |
| verify-step.sh: submodule pointer check | Satisfied | `git submodule status \|\| true` + grep for `^+` → SUBMODULE + exit 1 |
| verify-step.sh: precommit check | Satisfied | `just precommit \|\| { echo PRECOMMIT: ...; exit 1 }` |
| verify-step.sh: exit 0/1 contract | Satisfied | exit 0 + CLEAN on all-pass; exit 1 on any failure |
| No old H2-per-step format | Satisfied | `## step-N-N` pattern removed; tested in `test_orchestrator_plan_structured_format` |

**Gaps:** None.

---

## Deferred Items

The following items were identified but are out of scope:

- **IN:/OUT: placeholder values** — Reason: `- IN: (placeholder)` / `- OUT: (placeholder)` are emitted for all phases. The design says these should be "generated from runbook phase descriptions," but no extraction mechanism is specified at the implementation level. Populated from preamble text is the natural approach, deferred to Phase 3/4 or a follow-up task. The section structure is correct; content population is a quality improvement.

---

## Positive Observations

- `max_turns_lookup` construction is clean: metadata extraction happens at item-collection time, not repeated in the render loop. Avoids re-parsing content per-render.
- `verify-step.sh` correctly applies `|| true` on `git submodule status` with a non-empty guard before the grep — handles repos without submodules (no false positive). Matches project error-handling standards.
- `set -xeuo pipefail` with `exec 2>&1` in verify-step.sh ensures all diagnostic output is captured under the `2>&1` redirect that the orchestrator will see.
- `test_verify_step_clean_state` and `test_verify_step_dirty_states` use real git repos in `tmp_path` — correct e2e over mocked subprocess per testing decisions.
- `test_max_turns_extraction_and_propagation` tests `extract_step_metadata` in isolation first, then verifies end-to-end orchestrator output — correct layered test coverage.
- `test_orchestrator_plan_structured_format` combines positive field assertions with negative old-format assertions (`## step-N-N not in content`) — complete format contract verification.
