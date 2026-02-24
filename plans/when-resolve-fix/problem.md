# Diagnostic: `when-resolve.py` Section-Not-Found Failure

**Date:** 2026-02-24
**Trigger:** `when adding a new variant to enumerated system`
**Error:** `Section not found in agents/decisions/workflow-planning.md: When Adding A New Variant To Enumerated System`

## Root Cause

`_resolve_trigger()` reconstructs the section heading from the index trigger via `_build_heading()`, then does an **exact text match** against headings in the decision file.

The memory-index trigger was abbreviated — missing the article `"an"`:

| Source | Text |
|--------|------|
| memory-index.md trigger | `adding a new variant to enumerated system` |
| `_build_heading()` output | `When Adding A New Variant To Enumerated System` |
| Actual heading (workflow-planning.md:305) | `### When Adding A New Variant To An Enumerated System` |

`_heading_matches()` compares lowercased text equality → mismatch → `ResolveError`.

## Code Path

```
when-resolve.py
  → _resolve_trigger()                    resolver.py:194
    → _build_heading(operator, trigger)   resolver.py:296
    → scan file for _heading_matches()    resolver.py:243-249
    → actual_heading = None               (no match)
    → ResolveError: "Section not found"  resolver.py:252
```

## Contributing Design Tension

Triggers are intentionally short/memorable (articles omitted). But heading lookup requires exact text equality. The system assumes trigger → heading is losslessly reconstructable, which breaks on omitted articles.

## Fix Applied (Data)

Updated `agents/memory-index.md` line 308:
```
- /when adding a new variant to enumerated system | grep downstream enumeration sites
+ /when adding a new variant to an enumerated system | grep downstream enumeration sites
```

## Deferred Fix (Code)

Replace exact heading match in `_resolve_trigger()` with fuzzy heading matching — same approach `_resolve_section()` already uses for the `.SectionName` operator. Robust to abbreviated triggers and future heading rewording.

**Scope:** `src/claudeutils/when/resolver.py` `_resolve_trigger()` lines 241-253. Replace the exact `_heading_matches()` scan with a scored fuzzy scan over all `##`-prefixed lines, selecting the best match above threshold.

**Risk:** Low — `_resolve_section()` already has this pattern. Needs test coverage for the fuzzy fallback case.
