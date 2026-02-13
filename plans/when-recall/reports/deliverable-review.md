# Deliverable Review: when-recall

**Outline (ground truth):** `plans/when-recall/design.md`
**Branch:** `when-recall` (vs `main`)
**Review date:** 2026-02-13

## 1. Inventory

### Code (new)

| File | Lines | Design Spec |
|------|-------|-------------|
| `src/claudeutils/when/__init__.py` | 1 | Empty init |
| `src/claudeutils/when/fuzzy.py` | 217 | ~80 designed |
| `src/claudeutils/when/index_parser.py` | 89 | ~60 designed |
| `src/claudeutils/when/navigation.py` | 191 | ~80 designed |
| `src/claudeutils/when/resolver.py` | 256 | ~150 designed |
| `src/claudeutils/when/cli.py` | 32 | ~40 designed |
| `src/claudeutils/when/compress.py` | 126 | Not in design (design specified agent-core/bin/compress-key.py ~30 lines) |
| `agent-core/bin/compress-key.py` | 25 | ~30 designed (thin wrapper) |

### Code (modified)

| File | Lines | Purpose |
|------|-------|---------|
| `src/claudeutils/cli.py` | +2 | Register `when_cmd` in CLI group |
| `src/claudeutils/recall/index_parser.py` | +31 | Parse /when format (FR-12) |
| `src/claudeutils/recall/recall.py` | -30 | Simplify path matching |
| `src/claudeutils/validation/memory_index.py` | ~94 | New format entry extraction |
| `src/claudeutils/validation/memory_index_checks.py` | ~189 added | New check functions (trigger_format, collisions, fuzzy orphan) |
| `src/claudeutils/validation/memory_index_helpers.py` | -108 | Removed old em-dash/word-count functions |

### Test (new)

| File | Lines |
|------|-------|
| `tests/test_when_fuzzy.py` | 162 |
| `tests/test_when_index_parser.py` | 174 |
| `tests/test_when_navigation.py` | 277 |
| `tests/test_when_resolver.py` | 375 |
| `tests/test_when_cli.py` | 217 |
| `tests/test_when_compress_key.py` | 151 |
| `tests/test_recall_index_parser.py` | 253 |

### Test (modified)

| File | Lines |
|------|-------|
| `tests/test_recall_integration.py` | +89 |
| `tests/test_validation_memory_index.py` | +334 |
| `tests/test_validation_memory_index_autofix.py` | +127 |

### Test (deleted)

| File | Lines |
|------|-------|
| `tests/test_recall_calculation.py` | -30 |

### Configuration

| File | Change |
|------|--------|
| `justfile` | +6 lines |
| `agent-core` | Submodule ref updated |

### Agentic Prose

| File | Lines | Status |
|------|-------|--------|
| `agents/memory-index.md` | 213 | Preamble NOT updated; entries NOT migrated |

## 2. Gap Analysis

Comparing design scope (12 sequenced steps) against deliverables:

| Design Step | Status | Deliverable |
|-------------|--------|-------------|
| 1. Fuzzy engine | **Complete** | `src/claudeutils/when/fuzzy.py` |
| 2. Index parser | **Complete** | `src/claudeutils/when/index_parser.py` |
| 3. Navigation | **Complete** | `src/claudeutils/when/navigation.py` |
| 4. Resolver | **Complete** | `src/claudeutils/when/resolver.py` |
| 5. CLI + bin wrapper | **Partial** | CLI exists (`when/cli.py`), bin wrapper (`agent-core/bin/when-resolve.py`) MISSING |
| 6. Validator update | **Complete** | 3 validator modules updated |
| 7. Key compression | **Complete** | `when/compress.py` + `agent-core/bin/compress-key.py` |
| 8. Skills | **MISSING** | `agent-core/skills/when/SKILL.md` and `agent-core/skills/how/SKILL.md` do not exist |
| 9. Index migration | **MISSING** | Entries still in `Key — description` format; headings not renamed |
| 10. Remember skill | **MISSING** | `agent-core/skills/remember/SKILL.md` not updated for /when format |
| 11. Consumption header | **MISSING** | Preamble still says "scan mentally" |
| 12. Recall tool parser | **Complete** | `recall/index_parser.py` updated for dual format |

**Unspecified deliverables:**
- `src/claudeutils/when/compress.py` (126 lines) — Not in component architecture diagram, but is the module backing `compress-key.py`. Reasonable decomposition. **Accepted.**

**Summary:** 7/12 steps complete, 1 partial, 4 missing. The missing steps (5-partial, 8-10, 11) correspond to unexecuted runbook phases 5, 8, 9, 10. Session.md documents the blocker: validator exact-key design conflict blocks migration (Phase 9), which cascades to phases 8 and 10.

### Requirements Coverage

| Req | Addressed | Notes |
|-----|-----------|-------|
| FR-1 | **Partial** | Resolver + CLI exist; skill wrappers missing (agent can't invoke `/when` yet) |
| FR-2 | **Yes** | Fuzzy engine implemented and tested |
| FR-3 | **Yes** | Navigation module with ancestors + siblings |
| FR-4 | **Yes** | Validator updated with fuzzy matching, collision detection |
| FR-5 | **No** | Remember skill not updated |
| FR-6 | **No** | Migration not executed |
| FR-7 | **Yes** | Three resolution modes in resolver |
| NFR-1 | **Yes** | Fuzzy engine shared across resolver, validator, compression |
| NFR-2 | **Yes** | TDD for all components (42 cycles, 8 phases) |
| NFR-3 | **Partial** | Recall parser updated but measurement not possible until migration |
| NFR-4 | **Deferred** | Index remains @-loaded; format migration pending |

## 3. Per-Deliverable Review

### fuzzy.py — Code

| Axis | Finding | Severity |
|------|---------|----------|
| Conformance | Design specifies ~80 lines; actual 217. Well-decomposed into 7 functions. Larger due to DP matrix factoring and threshold logic. | Minor |
| Functional correctness | Scoring algorithm matches design spec (boundary bonuses, consecutive bonus, gap penalties, word-overlap tiebreaker). Constants match design. | Pass |
| Completeness | `score_match` and `rank_matches` — both specified functions present. | Pass |
| Robustness | Handles empty query (returns 0.0), query longer than candidate (returns 0.0), single-char threshold. | Pass |
| Modularity | Clean separation: DP matrix, backtrace, scoring, ranking. Private helpers well-bounded. | Pass |
| Testability | Pure functions, no I/O. | Pass |
| Idempotency | Stateless pure functions. | Pass |

### index_parser.py — Code

| Axis | Finding | Severity |
|------|---------|----------|
| Conformance | Matches design: WhenEntry model with Pydantic BaseModel, parse_index function. | Pass |
| Functional correctness | Parses `/when trigger | extras` format correctly. Tracks H2 sections. | Pass |
| Robustness | Handles OSError on file read, ValidationError on malformed entries, empty triggers. Logs warnings, continues processing. | Pass |
| Modularity | Single-purpose module. | Pass |

### navigation.py — Code

| Axis | Finding | Severity |
|------|---------|----------|
| Conformance | Design specifies ~80 lines; actual 191. Uses `dataclass` for HeadingInfo instead of Pydantic BaseModel. Design only requires Pydantic for WhenEntry. | Pass |
| Functional correctness | `compute_ancestors`: walks heading hierarchy correctly, always appends `..file.md` link. `compute_siblings`: maps entries to headings via fuzzy matching, excludes structural parent grouping. | Pass |
| Completeness | `extract_heading_hierarchy`, `compute_ancestors`, `compute_siblings`, `format_navigation` — all design functions present. | Pass |
| Robustness | Handles missing headings (returns empty list), None parent. | Pass |
| Excess | `_map_entries_to_headings` uses fuzzy scoring to map triggers to headings — not explicitly in design but necessary for sibling computation. | Pass |

### resolver.py — Code

| Axis | Finding | Severity |
|------|---------|----------|
| **Conformance** | **Design specifies `resolve(operator, query, index_path, decisions_dir)` — implementation drops `operator` parameter entirely.** CLI accepts operator via Click argument but suppresses unused-arg warning (`# noqa: ARG001`). Operator never reaches resolver. | **Critical** |
| **Conformance** | **Design: "Query includes prefix word: query 'when writing mock tests' (not 'writing mock tests')." Implementation passes bare trigger text without operator prefix.** Candidates are built as `f"{e.operator} {e.trigger}"` but query lacks operator prefix, defeating disambiguation between /when and /how entries on same topic. | **Major** |
| Conformance | `_resolve_section` only matches H2 headings (`##` not `###`). Design says "global unique heading lookup" — should include H3+. | Major |
| **Functional correctness** | `_build_heading` generates "When X" / "How to X" prefixed headings. Validator uses exact key match. Entry key "writing mock tests" ≠ heading "When Writing Mock Tests". **This is the known design conflict documented in session.md and `migration-findings.md`.** | **Critical** |
| Completeness | Three modes (trigger, section, file) all implemented with error handling and suggestions. | Pass |
| Robustness | File-not-found, section-not-found, no-match — all handled with descriptive error messages and suggestions. | Pass |
| Error signaling | Raises `ResolveError` (caller handles); CLI prints to stderr and exits 1. | Pass |

### cli.py — Code

| Axis | Finding | Severity |
|------|---------|----------|
| Conformance | Matches design Click structure. Operator choice, variadic query. Registered in main CLI group. | Pass |
| **Functional correctness** | **`operator` parameter is unused (`# noqa: ARG001`). This means `/when` and `/how` produce identical results.** Design requires operator-aware resolution for disambiguation. | **Critical** |
| Error signaling | ResolveError → stderr + exit(1). | Pass |

### compress.py — Code

| Axis | Finding | Severity |
|------|---------|----------|
| Conformance | Design specifies `compress-key.py ~30 lines` as a bin script. Implementation split into module (126 lines) + bin wrapper (25 lines). Good decomposition. | Pass |
| Functional correctness | `compress_key` generates candidates via word-drop, verifies uniqueness via fuzzy scoring, returns shortest unique trigger. | Pass |
| Completeness | `load_heading_corpus`, `generate_candidates`, `verify_unique`, `compress_key` — complete pipeline. | Pass |
| Robustness | Empty corpus returns False for uniqueness. Fallback to full heading lowercased. | Pass |

### Validator modules — Code

| Axis | Finding | Severity |
|------|---------|----------|
| Conformance | `check_em_dash_and_word_count` replaced with `check_trigger_format`. New `check_collisions` added. Fuzzy orphan detection. All per design. | Pass |
| **Functional correctness** | **Validator enforces `/when`/`/how` format (`check_trigger_format`), but index hasn't been migrated. Precommit fails with 152+ errors.** Phase 6 (validator) shipped before Phase 9 (migration). Branch is in broken-precommit state. | **Critical** |
| Completeness | All design validation checks present: format, bidirectional, collision, autofix, structural removal. Word count removed per D-9. | Pass |
| Modularity | Check functions properly split across `memory_index_checks.py` and `memory_index.py`. | Pass |

### recall/index_parser.py — Code

| Axis | Finding | Severity |
|------|---------|----------|
| Conformance | Dual-format support (new `/when`/`/how` + old em-dash). Design step 12 requires this. | Pass |
| Functional correctness | New format parsed correctly: operator extracted, trigger before pipe, extras after pipe. Keywords extracted from both. | Pass |

### recall/recall.py — Code

| Axis | Finding | Severity |
|------|---------|----------|
| Conformance | Simplified `_matches_file_or_parent` — removed suffix matching (`_paths_match_by_suffix`, `_suffix_matches`). | Pass |
| Excess | Simplification goes beyond step 12 scope (recall parser update). May be intentional cleanup. | Minor |

### Test files — Test

| Axis | Finding | Severity |
|------|---------|----------|
| Coverage | All 6 new modules have dedicated test files. test_when_resolver.py (375 lines) — tests all three modes, error paths, output formatting. test_when_fuzzy.py (162 lines) — scoring, ranking, edge cases. test_when_navigation.py (277 lines) — hierarchy, ancestors, siblings, structural headings. | Pass |
| Specificity | Tests verify specific behavior (fuzzy scores, heading resolution, navigation links), not just "doesn't crash". | Pass |
| Independence | Tests use fixtures and tmp_path, not implementation details. | Pass |
| Test suite | **807/808 passed, 1 xfail** (known preprocessor bug, unrelated). | Pass |

### agents/memory-index.md — Agentic Prose

| Axis | Finding | Severity |
|------|---------|----------|
| **Conformance** | Preamble not updated (design specifies new consumption header with invocation instructions). Still says "Condensed knowledge catalog. Read referenced files." | **Major** |
| **Completeness** | Entries not migrated to /when format (FR-6). Still in `Key — description` format. | **Major** |
| Excess | 8 blank lines between preamble and first section (lines 15-22). Vacuous whitespace. | Minor |

## 4. Cross-Cutting Checks

### Path consistency
- Design: `agent-core/bin/when-resolve.py` — **does not exist**
- Design: `agent-core/skills/when/SKILL.md` — **does not exist**
- Design: `agent-core/skills/how/SKILL.md` — **does not exist**
- All other paths consistent between design and implementation.

### API contract alignment
- **`resolve()` signature mismatch**: Design specifies 4 parameters (`operator`, `query`, `index_path`, `decisions_dir`); implementation has 3 (`query`, `index_path`, `decisions_dir`). CLI accepts `operator` but discards it.
- **`_build_heading()` generates prefixed headings** but validator/index uses exact key matching. This creates an irreconcilable state: resolver expects headings like "When Writing Mock Tests" but current headings are "Mock Patching Pattern". Neither the old headings nor any future renamed headings can satisfy both the resolver and the exact-key validator simultaneously.

### Naming consistency
- Module naming follows project convention (`test_when_*.py`, `src/claudeutils/when/*.py`).
- `WhenEntry` model name consistent across parser and navigation consumer.

## 5. Findings Summary

### By Severity

| Severity | Count |
|----------|-------|
| Critical | 4 |
| Major | 4 |
| Minor | 3 |

### Critical Findings

1. **resolver.py: `operator` parameter missing from `resolve()` signature** — `/when` and `/how` produce identical results, violating FR-1 and design D-6. Design mandates operator-aware resolution.
2. **cli.py: `operator` unused (`# noqa: ARG001`)** — Accepted but discarded. The lint suppression makes this a deliberate omission, not an oversight.
3. **`_build_heading()` ↔ exact-key validator conflict** — Resolver generates "When X" headings; validator requires entry key to exactly match heading. Entry key "writing mock tests" ≠ heading "When Writing Mock Tests". This is the documented design conflict blocking migration.
4. **Precommit broken** — Phase 6 validator enforces new format before Phase 9 migration executed. Branch cannot pass precommit. 152+ entries fail `check_trigger_format`.

### Major Findings

5. **Missing: `agent-core/bin/when-resolve.py`** — Bin wrapper not created (Phase 5 unexecuted). Skills depend on this.
6. **Missing: Skill wrappers** — `/when` and `/how` skills don't exist (Phase 8 unexecuted). FR-1 not deliverable without them.
7. **`_resolve_section` limited to H2** — Design says "global unique heading lookup" but implementation filters to H2 only, excluding H3+ headings.
8. **Index migration not executed** — FR-6 unmet. Entries in old format.

### Minor Findings

9. **fuzzy.py size** — 217 lines vs ~80 designed. Well-decomposed but significantly larger.
10. **recall.py excess cleanup** — Path matching simplification beyond step 12 scope.
11. **memory-index.md blank lines** — 8 blank lines (15-22) between preamble and first section.

## 6. Blocking Assessment

**The branch is not mergeable in current state.** Two categories of blockers:

**Design conflict (requires decision):**
- Critical #3: `_build_heading()` prefix vs exact-key matching. Three approaches documented in `plans/when-recall/reports/migration-findings.md`. Session.md records user chose exact keys. Approach A (don't prefix headings, change `_build_heading`) is recommended.

**Execution gap (requires implementation):**
- Critical #1-2: Wire `operator` through to resolver
- Critical #4: Either revert validator to accept old format OR execute migration atomically
- Majors #5-6: Create bin wrapper and skills
- Major #8: Execute migration

**Unblocked by design conflict:**
- Major #7: Extend `_resolve_section` to match H3+ headings

**Recommended resolution order:**
1. Fix `_build_heading()` conflict (Critical #3) — unblocks migration
2. Wire `operator` into resolver (Critical #1-2)
3. Create bin wrapper (Major #5)
4. Execute atomic migration: entries + headings + consumption header (Critical #4, Major #8)
5. Create skill wrappers (Major #6)
6. Extend section mode to H3+ (Major #7)
7. Update remember skill (deferred from scope)
