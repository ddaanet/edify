# prepare-runbook.py: Inline Phase Detection Fails With Compound Type Tags

## Problem

`prepare-runbook.py` fails to detect inline phases when the phase heading contains metadata beyond `(type: inline)`.

**Observed:** Running `prepare-runbook.py plans/recall-tool-anchoring/runbook.md` produces:
```
WARNING: Gap in phase numbers: 1 -> 4
```
Phases 2 and 3 (both inline) are silently skipped. Orchestrator plan contains no inline entries.

**Expected:** Inline phases detected, orchestrator plan contains `Execution: inline` entries for phases 2 and 3.

## Root Cause

Two regex patterns require `)` immediately after `inline`:

**Line 484** (`extract_sections`):
```python
inline_phase_pattern = r"^###? Phase\s+(\d+):.*\(type:\s*inline\)"
```

**Line 671** (`detect_phase_types`):
```python
inline_re = re.compile(r"\(type:\s*inline\)", re.IGNORECASE)
```

Both match `(type: inline)` but fail on `(type: inline, model: sonnet)` because the comma and additional metadata prevent `)` from following `inline`.

The runbook skill's phase heading format includes model: `### Phase 2: ... (type: inline, model: sonnet)`. This is the format specified in the skill's "Per-Phase Type Model" section and used by the outline.

## Fix

Change both regexes to allow optional content between `inline` and `)`:

```python
# Line 484
inline_phase_pattern = r"^###? Phase\s+(\d+):.*\(type:\s*inline[^)]*\)"

# Line 671
inline_re = re.compile(r"\(type:\s*inline[^)]*\)", re.IGNORECASE)
```

`[^)]*` matches any characters except `)` — handles `model: sonnet`, future metadata, etc.

## Scope

- 2 regex changes in `agent-core/bin/prepare-runbook.py`
- Test: existing inline detection tests + new test for compound tags
- Verify: re-run against `plans/recall-tool-anchoring/runbook.md`, confirm inline entries in orchestrator plan

## Workaround (applied)

Manually added inline phase entries to `plans/recall-tool-anchoring/orchestrator-plan.md` after generation.
