# Memory Index Migration Findings

## Design Conflict: Fuzzy vs Exact Key Matching

The `/when` system has a design conflict between the validator and resolver around key matching:

### Current State

- **Validator** (`memory_index_helpers.py:check_orphan_entries`): Uses **exact** dict lookup (`key not in headers`)
- **Validator** (`memory_index.py:_check_orphan_headers`): Uses **fuzzy** `score_match()` with threshold 50.0
- **Validator** (`memory_index_checks.py:check_collisions`): Uses **fuzzy** `score_match()` with threshold 50.0
- **Resolver** (`resolver.py:_resolve_trigger`): Uses **fuzzy** `rank_matches()` for runtime queries
- **Resolver** (`resolver.py:_build_heading`): Adds "When "/"How to " prefix to trigger text to reconstruct heading

### The Problem

Design D-6 says: `/when writing mock tests` → heading `### When Writing Mock Tests`

This creates a key mismatch:
- Entry key extracted: `"writing mock tests"` (trigger without operator)
- Heading key extracted: `"when writing mock tests"` (full title lowercased)
- These don't match exactly → fuzzy matching was used to bridge the gap

User directive: **exact keys only in index, fuzzy matching only for resolver recovery.**

### Three Fix Approaches

**A. Don't prefix headings** (simplest migration, requires resolver change)
- Headings stay as descriptive phrases: `### Mock Patching Pattern`
- Entry: `/how mock patching pattern` → key: `"mock patching pattern"`
- Heading key: `"mock patching pattern"` → exact match ✓
- Change `_build_heading` to NOT add prefix
- Tests affected: `test_when_resolver.py` (all "When X" headings in fixtures)

**B. Prefix headings + operator-prefixed key extraction** (no resolver change, validator change)
- Headings: `### When Writing Mock Tests`
- Entry: `/when writing mock tests` → key extraction prepends operator → `"when writing mock tests"`
- Heading key: `"when writing mock tests"` → exact match ✓
- Change `_extract_entry_key` and 3 other key extraction sites in validator
- Complication: `/how` headings use "How to " (3 words) vs key would need "how to " prefix
- Tests affected: `test_validation_memory_index.py`

**C. Strip prefix from heading keys** (headings prefixed, validator strips)
- Headings: `### When Writing Mock Tests`
- Heading key extraction strips "When "/"How to " → `"writing mock tests"`
- Entry key: `"writing mock tests"` → exact match ✓
- Change `collect_semantic_headers` to strip prefix
- Tests affected: validator tests, possibly autofix tests

### Recommendation

**Approach A** is simplest:
- No heading renames needed during migration (keep existing heading titles)
- Just change entry format from `Key — desc` to `/when key` or `/how key`
- One code change: `_build_heading` → just capitalize words, no prefix
- Resolver still uses fuzzy for runtime queries (unchanged)
- Validator already does exact matching in `check_orphan_entries` (helpers version)
- Remove fuzzy from `_check_orphan_headers` and `check_collisions`

### Code Changes Required (Approach A)

| File | Change | Lines |
|------|--------|-------|
| `resolver.py:_build_heading` | Remove "When "/"How to " prefix | ~3 |
| `memory_index.py:_check_orphan_headers` | Replace fuzzy with exact set lookup | ~15 |
| `memory_index_checks.py:check_collisions` | Replace fuzzy with exact lookup | ~20 |
| `memory_index.py` | Remove `score_match` import | 1 |
| `memory_index_checks.py` | Remove `score_match` import (if no other uses) | 1 |

### Test Changes Required (Approach A)

| File | Change |
|------|--------|
| `test_when_resolver.py` | ~20 heading references: "When X" → "X" (e.g., "When Writing Mock Tests" → "Writing Mock Tests") |
| `test_validation_memory_index.py:test_fuzzy_bidirectional_integrity` | Rewrite for exact matching |
| `test_validation_memory_index.py:test_collision_detection` | Rewrite for exact matching (collisions = same key, not fuzzy overlap) |

### Migration Scope (after code fix)

- ~152 entries in `agents/memory-index.md`: change from `Key — description` to `/when key` or `/how key`
- No heading renames in decision files
- Update preamble with invocation instructions
- Atomic: all entries in one commit with code changes

### Entry Classification

Each entry needs `/when` (behavioral, 73%) or `/how` (procedural, 27%) operator. Migration script at `tmp/migrate-index.py` has the full 152-entry mapping already defined.
