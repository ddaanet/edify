# Deliverable Review: inline-execute

**Date:** 2026-02-27
**Methodology:** agents/decisions/deliverable-review.md
**Design reference:** plans/inline-execute/outline.md
**Requirements:** plans/inline-execute/requirements.md

## Inventory

| Type | File | + | - |
|------|------|---|---|
| Code | agent-core/bin/triage-feedback.sh | +83 | -0 |
| Test | tests/test_triage_feedback.py | +372 | -0 |
| Agentic prose | agents/decisions/execution-strategy.md | +5 | -1 |
| Agentic prose | agents/decisions/pipeline-contracts.md | +17 | -0 |
| Agentic prose | agents/memory-index.md | +4 | -1 |
| Agentic prose | agent-core/fragments/continuation-passing.md | +3 | -2 |
| Agentic prose | agent-core/skills/design/SKILL.md | +19 | -13 |
| Agentic prose | agent-core/skills/inline/SKILL.md | +177 | -0 |
| Agentic prose | agent-core/skills/inline/references/corrector-template.md | +100 | -0 |
| Agentic prose | agent-core/skills/memory-index/SKILL.md | +4 | -1 |
| Agentic prose | agent-core/skills/runbook/SKILL.md | +2 | -21 |
| **Total** | **11 files** | **+786** | **-39** |

**Design conformance:** All 7 IN-scope items covered. 2 unspecified deliverables (execution-strategy.md, continuation-passing.md) — both justified by design decisions D-2/D-6.

## Critical Findings

1. **Classification format mismatch between /design and triage-feedback.sh**
   - File: `agent-core/bin/triage-feedback.sh:34` cross-referenced with `agent-core/skills/design/SKILL.md:106`
   - Axis: functional correctness (cross-cutting)
   - /design Phase 0 classification block uses list markers: `- **Classification:** Simple`
   - triage-feedback.sh grep pattern `^\*\*Classification:\*\*` requires `**Classification:**` at line start — won't match `- **` prefix
   - Test fixtures use no-list-marker format, so tests pass, but actual /design output won't parse
   - Impact: FR-6 comparison silently degrades to "no-classification" (safe — empty-classification guard applied by Layer 1 corrector), but intended triage comparison is non-functional
   - Fix: update grep to handle optional list marker: `grep -E "(^-?\s*\*\*Classification:\*\*|^-?\s*Classification:)"`

## Major Findings

1. **Inline divergence message missing evidence summary** (Layer 1, FIXED)
   - File: `agent-core/bin/triage-feedback.sh:65`
   - Axis: conformance (FR-7)
   - FR-7 format: `"Triage: predicted [X], evidence suggests [Y] ([summary])."` — script omitted parenthesized summary
   - Fixed: added `(files=$files_changed, reports=$reports_count, code=$behavioral_code)`

2. **Underclassified-via-reports path untested** (Layer 1, FIXED)
   - File: `tests/test_triage_feedback.py`
   - Axis: coverage
   - FR-6 underclassified = Simple + (behavioral_code OR reports > 0). Only behavioral_code branch tested.
   - Fixed: added `test_underclassified_simple_with_reports`

3. **Tier 2 lightweight cycle planning removed from /runbook** (Layer 1, FIXED)
   - File: `agent-core/skills/runbook/SKILL.md:138`
   - Axis: functional completeness (FR-10)
   - FR-10 requires "/runbook retains Tier 2 lightweight cycle planning." Execution delegation removed planning alongside execution mechanics.
   - Fixed: restored Tier 2 TDD/general planning guidance before `/inline` invocation

4. **/inline missing from Pivot Transactions table** (Layer 2)
   - File: `agent-core/fragments/continuation-passing.md:98-104`
   - Axis: functional completeness
   - /inline added to Cooperative Skills table (line 71) but missing from Pivot Transactions table
   - Tier 2 delegated execution: test-driver commits per cycle — multiple commits, compensation impractical (same as /orchestrate)
   - Tier 1 direct execution: no intermediate commits — not a pivot
   - Missing entry: `/inline` completes (Tier 2) = Yes; (Tier 1) = No

## Minor Findings

**Code/Test (Layer 1, all FIXED):**
- `triage-feedback.sh:15` — files_changed counted via fragile `grep -v "file.*changed"` on `--stat`; replaced with `--name-only | wc -l`
- `triage-feedback.sh:35-51` — empty classification (parse failure) fell through to "match"; now correctly routes to "no-classification"
- `test_triage_feedback.py:239` — overclassified test didn't assert inline message; assertion added
- `test_triage_feedback.py:325` — misleading `second_baseline` variable name; renamed

**Prose (Layer 1):**
- `agent-core/skills/inline/SKILL.md:82-84` — Phase 2.4 Reference Loading not traced to outline; excess but useful (DEFERRED)

**Cross-cutting (Layer 2):**
- `agent-core/skills/design/SKILL.md` — A.3-5 (Research and Outline) restructured into A.3-4 + A.5 with gate/artifact requirement; not in FR-1/FR-9 scope (excess, functionally reasonable)

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| FR-1: Classification persistence | Covered | design/SKILL.md:114 |
| FR-2: Pre-work context loading | Covered | inline/SKILL.md:54-84 |
| FR-3: Execute work | Covered | inline/SKILL.md:86-119 |
| FR-4: Corrector dispatch | Covered | inline/SKILL.md:123-137, corrector-template.md |
| FR-5: Evidence collection | Covered | triage-feedback.sh:14-28 |
| FR-6: Triage comparison | Covered (format mismatch — Critical #1) | triage-feedback.sh:33-52 |
| FR-7: Triage log | Covered | triage-feedback.sh:69-82 |
| FR-8: Deliverable-review chain | Covered | inline/SKILL.md:148-153 |
| FR-9: /design exit paths | Covered | design/SKILL.md:331,424 |
| FR-10: /runbook exit paths | Covered (after fix) | runbook/SKILL.md:122,138 |
| NFR-1: Lightweight chaining | Covered | inline/SKILL.md:22-28 (entry points) |
| NFR-2: Mechanical detection | Covered | triage-feedback.sh (all deterministic) |
| NFR-3: Single corrector pattern | Covered | corrector-template.md |
| C-1: /design writes, /inline reads | Covered | design/SKILL.md:114, inline/SKILL.md:141 |
| C-2: Verbatim classification format | Covered (format mismatch risk — Critical #1) | design/SKILL.md:114 |
| C-3: Initial estimate heuristics | Covered | execution-strategy.md, pipeline-contracts.md |
| C-4: Does not replace /orchestrate | Covered | inline/SKILL.md:19 |
| T6.5 pipeline contracts | Covered | pipeline-contracts.md:17 |
| Memory-index entries | Covered | memory-index.md, memory-index/SKILL.md |
| Continuation protocol | Covered | continuation-passing.md:71,80 |

## Summary

| Severity | Count | Fixed by Layer 1 | Remaining |
|----------|-------|-------------------|-----------|
| Critical | 1 | 0 | 1 |
| Major | 4 | 3 | 1 |
| Minor | 6 | 4 | 2 |

**Layer 1 agents:** 2 opus correctors (code+test, prose). Applied 7 fixes total. All tests pass (14/14).

**Layer 2 cross-cutting:** Found 1 Critical (format mismatch invisible to per-file review — /design produces list-marker format, script expects bare format, tests verify bare format) and 1 Major (pivot table gap).

**Delegation reports:** `deliverable-review-code-test.md`, `deliverable-review-prose.md`
