# Deliverable Review: Pushback

**Ground truth:** `plans/pushback/outline.md` (outline), `plans/pushback/design.md` (design spec)
**Method:** `agents/decisions/deliverable-review.md`

---

## 1. Inventory

| # | File | Action | Lines | Type |
|---|------|--------|-------|------|
| 1 | `agent-core/fragments/pushback.md` | NEW | 50 | Agentic prose |
| 2 | `agent-core/hooks/userpromptsubmit-shortcuts.py` | MOD | +123/-7 | Code |
| 3 | `tests/test_userpromptsubmit_shortcuts.py` | NEW | 288 | Test |
| 4 | `CLAUDE.md` | MOD | +2 | Configuration |

## 2. Gap Analysis

**Specified in outline/design → delivered:**
- Fragment (`agent-core/fragments/pushback.md`) ✓
- Hook enhancement (`userpromptsubmit-shortcuts.py`) ✓
- CLAUDE.md wiring ✓
- Symlink sync (`just sync-to-parent`) ✓ (runtime operation, not in diff)

**Delivered but not in outline Artifacts section:**
- `tests/test_userpromptsubmit_shortcuts.py` — specified in design.md Testing Strategy (lines 196-200) and produced by Phase 2 TDD cycles. Expected artifact.

**Missing deliverables:** None.
**Unspecified deliverables:** None.

## 3. Per-Deliverable Review

### D-1: `agent-core/fragments/pushback.md` (Agentic Prose)

| Axis | Result | Notes |
|------|--------|-------|
| Conformance | ✅ | All 4 design sections present (motivation, evaluation, momentum, model selection) |
| Functional correctness | ✅ | Rules implement research-grounded techniques accurately |
| Functional completeness | ✅ | Covers FR-1, FR-2, FR-3 |
| Vacuity | ✅ | Every section prescribes specific behavior |
| Excess | ✅ | Nothing beyond specification |
| Actionability | ✅ | Each rule maps to observable agent behavior |
| Constraint precision | ⚠️ | See F-1 |
| Determinism | ✅ | Same proposals → consistent evaluation behavior |
| Scope boundaries | ✅ | Clear IN/OUT, no execution, no external state |

**F-1 (Minor): Fragment heading narrows perceived scope vs design spec.**
- Design spec line 80: `## Pushback`
- Implementation: `## Pushback in Design Discussions`
- The heading implies ALL content is about design discussions. But Agreement Momentum (line 23) and Model Selection (line 31) apply broadly — not just `d:` mode.
- Functional impact: Three of four sections are ambient (unscoped). Only Design Discussion Evaluation is appropriately scoped to `d:` mode. The heading narrows perceived scope of the ambient sections.
- The two-layer architecture intent (fragment = ambient 100% recall, hook = targeted d: reinforcement) is partially undermined by heading-level scoping.

**F-2 (Minor): Section heading deviates from design spec.**
- Design spec line 94: `### Agreement Momentum`
- Implementation line 23: `### Agreement Momentum Detection`
- Extra word "Detection". No functional impact.

### D-2: `agent-core/hooks/userpromptsubmit-shortcuts.py` (Code)

| Axis | Result | Notes |
|------|--------|-------|
| Conformance | ✅ | All 4 design changes implemented: enhanced d: (lines 61-77), aliases (lines 78-106), any-line matching (lines 172-196), fenced block exclusion (lines 113-169) |
| Functional correctness | ✅ | 5/5 tests pass. Fence tracking correct for backtick/tilde, 3+ chars, same-char closing, nested fences |
| Functional completeness | ✅ | All design-specified changes present |
| Vacuity | ✅ | Every function serves a specific behavioral purpose |
| Excess | ✅ | No unspecified functionality |
| Robustness | ✅ | Edge cases handled: empty lines, line_idx bounds, mixed fence types, nested fences |
| Modularity | ✅ | `is_line_in_fence` and `scan_for_directive` are clean single-responsibility functions |
| Testability | ✅ | Both functions independently testable and tested |
| Idempotency | ✅ | Stateless — same input, same output |
| Error signaling | ✅ | Returns None/False for no-match, follows established output patterns |

**F-3 (Minor): Directive text duplication.**
- `DIRECTIVES['d']` (lines 61-77) and `DIRECTIVES['discuss']` (lines 78-94) are identical 17-line strings.
- Same for `DIRECTIVES['p']` (lines 95-100) and `DIRECTIVES['pending']` (lines 101-106).
- A shared variable per directive would be DRY and prevent divergence on future edits:
  ```python
  _DISCUSS_EXPANSION = '...'
  DIRECTIVES = {'d': _DISCUSS_EXPANSION, 'discuss': _DISCUSS_EXPANSION, ...}
  ```

**F-4 (Minor): O(n²) fence scanning.**
- `is_line_in_fence` rescans from line 0 per call; `scan_for_directive` calls it per line.
- Acceptable for prompt-length inputs. Design explicitly permits simpler implementation (line 149).
- A single-pass `scan_for_directive` tracking fence state would be O(n) but adds complexity the design chose to avoid.

### D-3: `tests/test_userpromptsubmit_shortcuts.py` (Test)

| Axis | Result | Notes |
|------|--------|-------|
| Conformance | ✅ | Covers all 4 design test areas (design.md lines 196-200) |
| Functional correctness | ✅ | 5/5 pass |
| Functional completeness | ✅ | All specified scenarios covered |
| Vacuity | ✅ | Every test verifies specific behavior |
| Excess | ✅ | No unspecified tests |
| Specificity | ✅ | Each test targets one behavior. Fence test checks per-line status |
| Coverage | ✅ | Backtick, tilde, mixed fences; line 2/3 directives; fenced exclusion; first-match priority; dual output; Tier 1 regression |
| Independence | ✅ | Tests verify behavior (output structure) not implementation. `is_line_in_fence` direct call is acceptable for utility with clear behavioral contract |

### D-4: `CLAUDE.md` Wiring (Configuration)

| Axis | Result | Notes |
|------|--------|-------|
| Conformance | ✅ | Design line 159: "after `execute-rule.md`" → Implementation: line 15, directly after line 13 (`execute-rule.md`) |
| Functional correctness | ✅ | @-reference syntax correct, file exists, fragment loads |
| Functional completeness | ✅ | Single specified change made |
| Vacuity | ✅ | Reference loads 50 lines of real behavioral rules |
| Excess | ✅ | Only the specified reference added |

## 4. Cross-Cutting Checks

**Path consistency:** ✅ Fragment, hook, and test paths consistent across CLAUDE.md, design.md, outline.md, session.md.

**API contract alignment:** ✅
- Fragment references `d:` directive (line 7) → matches hook DIRECTIVES key
- `scan_for_directive` returns `(key, value)` tuple → consumed correctly at hook line 775-776
- Dual output pattern (additionalContext + systemMessage) → consistent with established COMMANDS pattern
- Non-discuss directives use same-to-both pattern → preserves existing behavior

**Naming convention uniformity:** See F-1 (heading deviation) and F-2 (section naming deviation).

## 5. Summary

| Severity | Count | Findings |
|----------|-------|----------|
| Critical | 0 | — |
| Major | 0 | — |
| Minor | 4 | F-1 heading scope, F-2 section naming, F-3 directive duplication, F-4 O(n²) scan |

**Requirements traceability:**

| Req | Status | Deliverable |
|-----|--------|-------------|
| FR-1 (structural pushback) | ✅ | D-1 evaluation rules + D-2 hook injection |
| FR-2 (agreement momentum) | ✅ | D-1 momentum section |
| FR-3 (model selection) | ✅ | D-1 model selection section |
| NFR-1 (genuine, not reflexive) | ✅ | Evaluator framing throughout, "articulate WHY" rules |
| NFR-2 (lightweight) | ✅ | Fragment = zero per-turn cost, hook = string modification only |

**Verdict:** All deliverables conform to design spec. Four minor findings, zero blocking issues. Implementation is functionally complete with clean test coverage.
