# Deliverable Review: active-recall (S-A Token Count Cache)

**Date:** 2026-03-08
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | Lines |
|------|------|-------|
| Code | src/claudeutils/token_cache.py | +111 |
| Code | src/claudeutils/tokens.py | +14/-2 |
| Code | src/claudeutils/tokens_cli.py | +2/-7 |
| Code | tests/conftest.py | +14/-2 |
| Test | tests/test_token_cache.py | +320 |
| Test | tests/test_cli_tokens.py | +9/-4 |
| Configuration | .gitignore | +1 |
| Configuration | pyproject.toml | +1 |
| Configuration | uv.lock | +152/-98 |

**Design conformance:** All S-A specified deliverables present. No missing deliverables. Agentic prose files (design/SKILL.md, write-outline.md) listed by inventory script but show no diff from merge base — false positive.

## Critical Findings

None.

## Major Findings

1. **tokens.py:191 — Incomplete exception coverage in cache init fallback** (Robustness)
   - `except OSError` did not catch SQLAlchemy exceptions (`OperationalError`, `DatabaseError`) from `get_default_cache()`. Cache initialization with corrupted DB or disk-full during table creation would crash instead of falling back gracefully.
   - **Fixed:** Broadened to `except Exception` with `noqa: BLE001`.

2. **token_cache.py:96-101 — No error handling for cache operations** (Robustness)
   - `cached_count_tokens_for_file` had no try/except around `cache.get()` and `cache.put()`. SQLAlchemy `OperationalError` during DB access would propagate up, crashing token counting instead of falling back to uncached.
   - **Fixed:** Wrapped both operations in try/except with logged warnings.

## Minor Findings

- **Double file read on cache miss** (Modularity): `cached_count_tokens_for_file` reads the file for md5 hash, then `count_tokens_for_file` reads it again for the API call. **Fixed:** Extracted `_count_tokens_for_content(content, model, client)` helper from `count_tokens_for_file`; cache wrapper passes already-read content directly.
- **Missing test coverage for fallback paths** (Coverage): No tests for cache operation failures or non-OSError cache init failures. **Fixed:** Added 3 tests (`test_cache_get_error_falls_back_to_api`, `test_cache_put_error_still_returns_count`, `test_count_tokens_for_files_fallback_on_cache_init_error`).

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| sqlite cache via sqlalchemy | Covered | token_cache.py |
| Composite key (md5_hex, model_id) | Covered | TokenCacheEntry model |
| last_used for eviction | Covered | get() updates, put() sets |
| platformdirs cache location | Covered | get_default_cache() |
| Wrapping count_tokens_for_file | Covered | cached_count_tokens_for_file() |
| Integration with count_tokens_for_files | Covered | tokens.py lazy import |
| Graceful fallback on cache failure | Covered (after fix) | tokens.py, token_cache.py |
| Tests | Covered | 16 tests across 4 classes |

## Summary

- Critical: 0
- Major: 2 (both fixed inline)
- Minor: 2 (both fixed — double read eliminated, fallback tests added)

All findings resolved inline — no pending fix task needed.
