# Deliverable Review: when-recall (Round 2)

**Date:** 2026-02-13
**Ground truth:** `plans/when-recall/design.md`
**Scope:** All production artifacts on `when-recall` branch vs `main`

## 1. Inventory

### Code (14 deliverables)

| File | Lines | Status |
|------|-------|--------|
| `src/claudeutils/when/__init__.py` | 1 | New |
| `src/claudeutils/when/fuzzy.py` | 217 | New |
| `src/claudeutils/when/resolver.py` | 310 | New |
| `src/claudeutils/when/navigation.py` | 191 | New |
| `src/claudeutils/when/index_parser.py` | 89 | New |
| `src/claudeutils/when/cli.py` | 32 | New |
| `src/claudeutils/when/compress.py` | 126 | New |
| `agent-core/bin/when-resolve.py` | 11 | New |
| `agent-core/bin/compress-key.py` | 24 | New |
| `src/claudeutils/validation/memory_index.py` | 279 | Modified |
| `src/claudeutils/validation/memory_index_checks.py` | 351 | Modified |
| `src/claudeutils/validation/memory_index_helpers.py` | 296 | Modified |
| `src/claudeutils/recall/index_parser.py` | 188 | Modified |
| `src/claudeutils/cli.py` | 392 | Modified |

### Test (10 deliverables)

| File | Lines |
|------|-------|
| `tests/test_when_fuzzy.py` | 162 |
| `tests/test_when_resolver.py` | 157 |
| `tests/test_when_resolver_errors.py` | 297 |
| `tests/test_when_navigation.py` | 277 |
| `tests/test_when_index_parser.py` | 174 |
| `tests/test_when_cli.py` | 220 |
| `tests/test_when_compress_key.py` | 151 |
| `tests/test_validation_memory_index.py` | 352 |
| `tests/test_validation_memory_index_autofix.py` | 298 |
| `tests/test_validation_memory_index_formats.py` | 277 |

### Agentic Prose (3 deliverables)

| File | Lines |
|------|-------|
| `agent-core/skills/when/SKILL.md` | 49 |
| `agent-core/skills/how/SKILL.md` | 49 |
| `agent-core/skills/remember/SKILL.md` | Updated |

### Human Documentation / Configuration (14 deliverables)

| File | Change |
|------|--------|
| `agents/memory-index.md` | Migrated format + consumption header |
| `agents/decisions/cli.md` | Heading renames |
| `agents/decisions/data-processing.md` | Heading renames |
| `agents/decisions/implementation-notes.md` | Heading renames + new entries |
| `agents/decisions/markdown-tooling.md` | Heading renames |
| `agents/decisions/project-config.md` | Heading renames |
| `agents/decisions/prompt-structure-research.md` | Heading renames |
| `agents/decisions/runbook-review.md` | Heading renames |
| `agents/decisions/testing.md` | Heading renames |
| `agents/decisions/validation-quality.md` | Heading renames |
| `agents/decisions/workflow-advanced.md` | Heading renames |
| `agents/decisions/workflow-core.md` | Heading renames |
| `agents/decisions/workflow-optimization.md` | Heading renames |
| `agents/decisions/deliverable-review.md` | Minor update |

**Total: 41 deliverables** (14 code, 10 test, 3 agentic prose, 14 documentation/config)

## 2. Gap Analysis

### Design → Implementation Coverage

| Design Step | Deliverable | Status |
|-------------|-------------|--------|
| 1. Fuzzy engine | `when/fuzzy.py` | ✅ |
| 2. Index parser | `when/index_parser.py` | ✅ |
| 3. Navigation | `when/navigation.py` | ✅ |
| 4. Resolver | `when/resolver.py` | ✅ |
| 5. CLI + bin wrapper | `when/cli.py` + `when-resolve.py` | ✅ |
| 6. Validator update | `validation/memory_index*.py` | ✅ |
| 7. Key compression | `when/compress.py` + `compress-key.py` | ✅ |
| 8. Skills | `when/SKILL.md` + `how/SKILL.md` | ✅ |
| 9. Index migration | `memory-index.md` + heading renames | ✅ |
| 10. Remember skill | `remember/SKILL.md` | ✅ |
| 11. Consumption header | `memory-index.md` preamble | ✅ |
| 12. Recall parser | `recall/index_parser.py` | ✅ |

**Missing deliverables:** None.

### Unspecified Deliverables

| File | Assessment |
|------|------------|
| `src/claudeutils/when/compress.py` | Design specified `compress-key.py` as ~30 lines. Implementation splits into module (126 lines) + bin wrapper (24 lines). Acceptable — follows project pattern. |
| `tests/test_when_compress_key.py` | Not in design test list. Logical addition. |
| `tests/test_when_resolver_errors.py` | Design lists one resolver test file. Split is reasonable. |
| `tests/test_validation_memory_index_autofix.py` | Not in design. Logical for updated validation. |
| `tests/test_validation_memory_index_formats.py` | Not in design. Logical for updated validation. |

**Assessment:** No excess. All unspecified deliverables are justified extensions.

## 3. Findings

### Critical

**C-1: worktree CLI deregistered from main CLI group**
- `src/claudeutils/cli.py`: `worktree` import and `add_command(worktree)` replaced by `when_cmd` instead of added alongside
- On main: line 26 imports `worktree`, line 148 registers it
- On when-recall: same lines now import `when_cmd`, register `when_cmd` — worktree gone
- `claudeutils worktree` no longer works on this branch
- Worktree module exists (`src/claudeutils/worktree/cli.py`) but is unreachable via main CLI
- Worktree tests pass because they import directly from `claudeutils.worktree.cli`
- **Merge impact:** Merging to main will create a conflict at these lines. Correct resolution must include BOTH commands.
- Axis: Functional completeness (regression of existing functionality)

### Major

**M-1: `_handle_no_match()` hardcodes `/when` in error suggestions**
- `resolver.py:159`: `msg += f"\n  /when {trigger}"` — always `/when` regardless of operator
- Function signature `_handle_no_match(query, candidates)` doesn't receive operator
- For `/how` queries, suggestions incorrectly show `/when` prefix
- Worse: candidate format for `/how` is `"how to <trigger>"`, so `parts.split(" ", 1)` produces `["how", "to <trigger>"]`, yielding `/when to <trigger>` — doubly wrong
- Axis: Functional correctness (wrong error output for `/how` queries)

**M-2: Duplicate check functions across validation modules**
- `check_orphan_entries`, `check_entry_placement`, `check_structural_entries` defined in BOTH:
  - `memory_index_checks.py` (with fuzzy matching for orphan check)
  - `memory_index_helpers.py` (exact match only for orphan check)
- Facade (`memory_index.py`) imports from helpers — checks versions are dead code
- The dead checks.check_orphan_entries has fuzzy matching (per D-7), the used helpers version does not
- Axis: Modularity (duplicate definitions), Functional completeness (fuzzy matching specified in D-7 but not used for orphan entry detection)

### Minor

**N-1: `_build_heading()` capitalize() degrades acronyms**
- `resolver.py:272`: `" ".join(w.capitalize() for w in words)` lowercases all but first char
- Produces "Tdd", "Api", "Cli" instead of "TDD", "API", "CLI"
- Confirmed: `workflow-core.md:40` reads `## How to Integrate Tdd Workflow`
- Currently functional (migration renamed headings consistently) but degrades readability
- Future heading additions with acronyms will produce ugly headings
- Axis: Accuracy (readability of renamed headings)

**N-2: `_get_suggestions()` reimplements fuzzy matching**
- `resolver.py:126-147`: simple subsequence character counter for error suggestions
- Separate from shared `fuzzy.py` engine — violates NFR-1 (DRY) in spirit
- Likely intentional: main engine has minimum thresholds that filter out weak matches, suggestions need a looser matcher
- Impact is low (error path only)
- Axis: Modularity

**N-3: navigation.py uses dataclass instead of Pydantic BaseModel**
- `navigation.py:9-17`: `HeadingInfo` uses `@dataclass` per `from dataclasses import dataclass`
- Design convention (per index_parser.py and recall/index_parser.py) uses Pydantic BaseModel
- HeadingInfo is internal-only, so Pydantic validation overhead is unjustified
- Axis: Consistency (minor convention deviation)

## 4. Cross-Cutting Checks

**Path consistency:** ✅ All module paths match across imports, bin wrappers, skill definitions, and CLI registration.

**API contract alignment:**
- `fuzzy.py` exports `score_match` and `rank_matches` — consumed by resolver, navigation, validation, and compress modules ✅
- `index_parser.py` exports `WhenEntry` and `parse_index` — consumed by resolver and navigation ✅
- `resolver.py` exports `resolve` and `ResolveError` — consumed by cli.py ✅

**Naming convention uniformity:** ✅ All `when/` modules follow `snake_case` convention. Test files follow `test_when_<module>.py` pattern.

**Skill wrapper consistency:** ✅ Both `/when` and `/how` skills use identical structure, same `allowed-tools` pattern, same bin script entry point.

**Precommit validation:** ✅ `just precommit` passes clean (810/811 tests, 1 xfail unrelated).

## 5. Summary

| Severity | Count |
|----------|-------|
| Critical | 1 |
| Major | 2 |
| Minor | 3 |

**Requirements traceability:** All 7 FRs and 4 NFRs addressed. FR-1 through FR-7 have working implementations. NFR-1 (DRY fuzzy engine) met for primary path, violated only in error suggestion path (N-2). NFR-2 (TDD) met — 42/42 cycles completed. NFR-4 (index @-loaded) met.

**Go/no-go:** Fix C-1 (worktree deregistration) and M-1 (operator in error messages) before merge. M-2 (duplicate functions) is cleanup that can be deferred but should be tracked. Branch is otherwise merge-ready.
