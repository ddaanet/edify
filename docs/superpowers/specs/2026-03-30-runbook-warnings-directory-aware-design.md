# Directory-Aware File Reference Validation

## Problem

`validate_file_references()` in `prepare-runbook.py` checks backtick-wrapped file paths against the filesystem. For greenfield plans where steps create new files, this produces ~95 false-positive warnings. Real issues (path typos, hallucinated filenames) are buried in noise.

## Solution

Add a parent-directory existence check before warning. If the parent directory doesn't exist, the path is greenfield — skip it. If the parent exists but the file doesn't, it's a likely typo — warn.

One line added to `validate_file_references()`:

```python
if not Path(ref).parent.exists():
    continue
```

Placed after existing skip checks (report paths, creation verbs), before the `Path(ref).exists()` check.

## What stays

- `extract_file_references()` — unchanged
- All existing skip logic (report paths, `plans/*/reports/`, creation verbs, runbook self-reference)
- Same-step creation-verb suppression — now redundant for greenfield paths but harmless

## Files

- `plugin/bin/prepare-runbook.py` — add parent-directory check in `validate_file_references()`
- `tests/test_prepare_runbook_fenced.py` — add test: existing-parent warns, non-existent-parent silent

## Context

This replaces the `plans/runbook-warnings/` plan which proposed cross-step creation-verb detection — a heuristic-on-heuristic approach. The directory-aware check solves the same problem without format changes or new parsing logic.
