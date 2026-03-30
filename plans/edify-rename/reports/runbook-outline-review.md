# Runbook Outline Review: Edify Rename SP-1

**Artifact**: plans/edify-rename/runbook-outline.md
**Design**: plans/edify-rename/outline.md (SP-1 section)
**Requirements**: plans/edify-rename/requirements.md
**Date**: 2026-03-30
**Mode**: review + fix-all

## Summary

Compact, well-structured Tier 3 outline for a mechanical grep-replace rename across two boundaries (submodule internal, parent repo). Phase structure maps cleanly to D-4 two-commit pattern. Parallel dispatch model is sound. Minor issues in requirements mapping completeness, verification coverage, and count discrepancies — all fixed.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps | Coverage | Notes |
|------------|-------|-------|----------|-------|
| FR-2 (URL update) | 2 | 2.1 | Complete | .gitmodules URL change |
| FR-3 (directory rename) | 2 | 2.1 | Complete | git mv agent-core plugin |
| FR-4 (config path propagation) | 2 | 2.1, 2.2 | Complete | .gitmodules structural in 2.1, remaining config files in 2.2 |
| FR-5 (source code paths) | 2 | 2.2 | Complete | src/*.py agent-core refs |
| FR-6 (test paths) | 2 | 2.2 | Complete | tests/*.py agent-core refs |
| FR-7 (agentic prose paths) | 1, 2 | 1.2, 2.2 | Complete | Split across submodule (1.2) and parent (2.2) |
| FR-8 (active plan paths) | 2 | 2.2 | Complete | plans/*/ scope in parallel batch |
| FR-9b (CLI command in submodule) | 1 | 1.2 | Complete | claudeutils -> edify inside submodule only; SP-2 handles rest |

**Coverage Assessment**: All SP-1 requirements covered. FR-9b scope boundary correctly noted (submodule portion only).

## Phase Structure Analysis

### Phase Balance

| Phase | Steps | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 1 (Submodule) | 3 | Medium | 50% | Balanced |
| 2 (Parent) | 3 | Medium | 50% | Balanced |

**Balance Assessment**: Well-balanced. Symmetric discovery-batch-verify pattern in both phases.

### Complexity Distribution

- Low complexity: 0 phases
- Medium complexity: 2 phases (both are mechanical grep-replace with verification)
- High complexity: 0 phases

**Distribution Assessment**: Appropriate for mechanical rename work. No phase requires design decisions.

## Review Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Requirements mapping table missing columns**
   - Location: Requirements Mapping section
   - Problem: Table had only Requirement and Phase columns, missing Steps and Notes for full traceability
   - Fix: Added Steps and Notes columns with specific step references and scope clarifications
   - **Status**: FIXED

2. **FR-9b scope boundary unclear**
   - Location: Requirements Mapping, FR-9b row
   - Problem: Mapping said "Phase 1" without clarifying this covers only the submodule portion (design says FR-9b spans SP-1 + SP-2)
   - Fix: Added note "claudeutils -> edify inside submodule only; rest of tree handled by SP-2"
   - **Status**: FIXED

3. **Count discrepancy undocumented**
   - Location: Scope section, measured counts
   - Problem: Outline says 55 files with agent-core refs; design says 49. No note about which is authoritative
   - Fix: Added parenthetical noting discrepancy and directing to Step 1.1 discovery as source of truth
   - **Status**: FIXED

4. **.gitmodules section header name field**
   - Location: Step 2.1
   - Problem: Step mentioned updating URL and path but didn't explicitly call out the `[submodule "agent-core"]` header name field change
   - Fix: Added explicit mention of section header name field update
   - **Status**: FIXED

5. **Missing post-phase state declaration**
   - Location: Step 2.1
   - Problem: Phase 2 depends on Phase 1 completion but had no explicit dependency declaration
   - Fix: Added "Depends on: Phase 1 complete (submodule committed with internal refs updated)"
   - **Status**: FIXED

6. **`.envrc` symlink verification missing**
   - Location: Step 2.3
   - Problem: Step 2.1 fixes the symlink but Step 2.3 verification didn't check it resolves
   - Fix: Added `readlink .envrc` verification to Step 2.3
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping — expanded table with Steps and Notes columns
- FR-9b row — added SP-1/SP-2 scope boundary note
- Scope section — added count discrepancy note pointing to Step 1.1 as authoritative
- Step 2.1 — added .gitmodules section header name field mention and Phase 1 dependency
- Step 2.3 — added .envrc symlink resolution verification
- End of file — appended Expansion Guidance section

## Design Alignment

- **Architecture**: Aligned. Two-phase structure maps to D-4 two-commit pattern
- **Atomic commits**: D-3 satisfied — Phase 1 commits inside submodule, Phase 2 commits parent with submodule pointer
- **No shims**: D-5 satisfied — clean break, no compatibility layer
- **Full-tree grep**: C-3 satisfied — Step 1.1 and 2.2 use grep discovery, not manual file lists
- **Key decisions**: D-3, D-4, D-5, C-3 all referenced in outline Key Decisions section

## Parallel Dispatch Feasibility

- Step 1.2: ~9 directory-scoped agents inside submodule — feasible, scopes don't overlap
- Step 2.2: ~10 directory/file-scoped agents in parent repo — feasible, scopes don't overlap
- No cross-scope dependencies within batch steps
- Agent prompt template needs: scope glob, replacement pairs, grep-then-edit instruction
- Recall injection: 5 entries from `plans/edify-rename/recall-artifact.md` — compact, correct count

## Verification Completeness

- Phase 1: grep for zero `agent-core` AND zero `claudeutils` matches — covers both replacement identities
- Phase 2: grep for zero `agent-core` with correct exclusions (.git, plugin/, plans/edify-rename/)
- Phase 2: `just test` + `just precommit` — full validation
- Added: `.envrc` symlink verification (was missing)
- Exclusion note: `plans/edify-rename/` correctly excluded from both verification greps

## LLM Failure Mode Analysis

- **Vacuity**: Step 1.1 (discovery) produces a file list consumed by Step 1.2 — not vacuous despite no code change
- **Ordering**: Foundation-first within each phase: discovery -> batch -> verify. Correct
- **Density**: 6 steps across 2 phases — no collapsible groups, no adjacent steps testing same function
- **Checkpoints**: After Step 1.3 and Step 2.3 — one per phase, appropriate for 3-step phases
- **Growth projection**: N/A — rename operations don't grow file sizes meaningfully

## Positive Observations

- Symmetric phase structure (discovery -> batch -> verify) is clean and predictable
- Execution Model section is well-specified for Tier 3 lightweight orchestration
- Recall injection correctly references the artifact (5 entries, path-based)
- Error escalation covers the three likely failure modes (permission, residual matches, test failures)
- Weak Orchestrator Metadata section provides all fields needed for dispatch

## Recommendations

- During expansion, agent prompt template should emphasize grep-then-edit (not blind `replace_all`) per C-3 spirit
- Step 2.2 plans/*/ scope should explicitly exclude plans/edify-rename/ in agent instructions
- If any Step 2.2 scope has <3 files, merge with adjacent scope to reduce dispatch overhead

---

**Ready for full expansion**: Yes
