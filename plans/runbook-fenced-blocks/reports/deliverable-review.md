# Deliverable Review: runbook-fenced-blocks

**Date:** 2026-02-23
**Methodology:** agents/decisions/deliverable-review.md
**Layer 1:** Skipped (2 files, boundary threshold)
**Layer 2:** Full interactive review

---

## Inventory

| Type | File | Lines added | Lines removed |
|------|------|-------------|---------------|
| Code | agent-core/bin/prepare-runbook.py | +158 | -12 |
| Test | tests/test_prepare_runbook_fenced.py | +342 | -0 |

**Design baseline:** plans/runbook-fenced-blocks/test-plan.md (no design.md — moderate-complexity task).

**Conformance summary:** All 8 functions in the Affected Functions table wired. All 9 cycles executed. 1 extra test added (unpaired-inner-fence, justified). Baseline conformance satisfied with one latent bug not covered by the test suite.

---

## Critical Findings

None.

---

## Major Findings

**M-1: `extract_sections()` second pass — phase boundary not fence-gated**

`prepare-runbook.py:556`

```python
if re.match(phase_pattern, line):   # no `not in_fence` guard
    save_current()
    current_section = None
    current_content = []
    continue
```

When a fenced `### Phase N:` header appears inside step content (e.g., a step that shows an example runbook structure), the second pass triggers `save_current()` prematurely and clears `current_section`. Step content after the fenced phase header is lost — the step is silently truncated.

All three loops that use `tracker` in the first pass are fence-gated. All guards in `extract_cycles()` are fence-gated. This one line in the second pass was missed.

Trace for Cycle 3 test content: step 1.1 content is saved truncated (missing fenced content and closing fence), but `len(sections["steps"]) == 2` still holds — the test passes without detecting the truncation.

**M-2: Test missing — step content completeness under fenced phase header**

`tests/test_prepare_runbook_fenced.py`

No test verifies that step content is complete when a fenced `### Phase N:` header appears inside the step. The Cycle 3 test checks `len(sections["steps"]) == 2` but not that either step's content is intact past the fence. This is the test gap that allows M-1 to go undetected.

Required test: fixture with fenced `### Phase N:` inside step content; assert the full step content (including text after the fence) is present.

---

## Minor Findings

**m-1: Dead call in `strip_fenced_blocks()`**

`prepare-runbook.py:438`

```python
content.splitlines(keepends=True)   # result is discarded
```

Result is not assigned. Line is a no-op — function continues with `content.splitlines()` on line 442. No behavioral impact, but dead code.

**m-2: Vacuous guard in `_fence_tracker()` opening detection**

`prepare-runbook.py:402, 415`

```python
elif stripped.startswith("```"):
    ...count backticks...
    if backtick_count >= 3:   # always True: startswith("```") guarantees >= 3
```

Same pattern for tilde at line 415. The inner `if` can never be False given the outer `startswith` guard. Should be removed or replaced with an assertion.

**m-3: Indentation tolerance exceeds CommonMark spec**

`prepare-runbook.py:357` (`stripped = line.lstrip()`)

CommonMark § 4.5: "up to 3 spaces of indentation" before fence marker. `line.lstrip()` strips all leading whitespace. A 4-space-indented line starting with ` ``` ` would be treated as a fence opener by the tracker, but is an indented code block by CommonMark and should NOT open a fenced block. Low-risk in practice (phase files rarely have 4-space indented fences), but incorrect per spec.

**m-4: Test docstring describes wrong failure mode**

`tests/test_prepare_runbook_fenced.py:125`

```
Opening 3-backtick inside 4-backtick fence incorrectly toggles the
fence state with toggle-based logic.
```

This is inaccurate: toggle logic produces the correct result for paired inner fences (the ` ```python ` and ` ``` ` cancel each other, so the step header happens to be seen as in-fence). The docstring should describe the actual property being tested (paired inner fences don't close the outer fence) and reference `test_extract_sections_four_backtick_unpaired_inner_fence` as the test that covers the toggle failure mode.

**m-5: `strip_fenced_blocks()` preserves inner fence delimiter lines**

`prepare-runbook.py:444-449`

When an inner fence delimiter (e.g., ` ```python `) appears inside an outer fence, it is preserved rather than stripped:

```python
if in_fence and not (
    line.lstrip().startswith("```") or line.lstrip().startswith("~~~")
):
    result.append("\n")   # strip
else:
    result.append(line + ...)  # preserve ← applies to inner delimiters too
```

The condition keeps any line that starts with backticks/tildes, regardless of whether it's a real fence boundary or an inner delimiter. For `extract_phase_models` and `assemble_phase_files` use cases this doesn't affect correctness (inner ` ```python ` won't match phase header patterns). But it violates the stated contract ("fenced block content replaced by empty lines") for fence delimiter lines nested inside outer fences.

---

## Gap Analysis

| Design requirement | Status | Reference |
|-------------------|--------|-----------|
| `extract_cycles()` fence-aware | ✓ Covered | prepare-runbook.py:120-150 |
| `extract_sections()` pass 1 — phase detection | ✓ Covered | prepare-runbook.py:486-495 |
| `extract_sections()` pass 1 — inline phase extraction | ✓ Covered | prepare-runbook.py:502-531 |
| `extract_sections()` pass 2 — step header detection | ✓ Covered | prepare-runbook.py:562 |
| `extract_sections()` pass 2 — phase boundary detection | ✗ Missing guard | prepare-runbook.py:556 (M-1) |
| `extract_phase_models()` fence-aware | ✓ Covered | prepare-runbook.py:600 |
| `extract_phase_preambles()` fence-aware | ✓ Covered | prepare-runbook.py:637 |
| `assemble_phase_files()` detection fence-aware | ✓ Covered | prepare-runbook.py:704 |
| `extract_file_references()` replace naive re.sub | ✓ Covered | prepare-runbook.py:844 |
| `_fence_tracker()` — 3-backtick | ✓ Covered | Cycle 1 |
| `_fence_tracker()` — count-based (4+) | ✓ Covered | Cycle 4 |
| `_fence_tracker()` — tilde fences | ✓ Covered | Cycle 5 |
| `strip_fenced_blocks()` helper | ✓ Covered | Cycle 7 |
| Test: step content completeness under fenced phase header | ✗ Missing | M-2 |

---

## Summary

**Critical:** 0
**Major:** 2 (M-1: latent second-pass truncation bug; M-2: missing test for it)
**Minor:** 5

M-1 and M-2 are coupled — the same fix (add `not in_fence` guard to the second-pass phase pattern check, add a test asserting step content integrity) resolves both. The fix is a 1-line change; the test adds one scenario to `TestFencedPhaseHeaders`.
