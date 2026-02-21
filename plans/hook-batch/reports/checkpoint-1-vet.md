# Vet Review: Phase 1 Checkpoint — Hook Batch

**Scope**: Phase 1 UserPromptSubmit improvements (changed files: userpromptsubmit-shortcuts.py, test_userpromptsubmit_shortcuts.py, test_userpromptsubmit_new_directives.py)
**Date**: 2026-02-21
**Mode**: review + fix

## Summary

Phase 1 implements all 9 design items from the outline correctly: line-based Tier 1 matching, graduated `r` expansion, `xc`/`hc` bracket format, additive directive scanning (D-7), dual-output for `p:`/`b:`/`q:`/`learn:`, `b:` brainstorm directive, and Tier 2.5 pattern guards. Design decisions D-5 (brainstorm semantics), D-7 (additive directives), and the Tier 2.5 additionalContext-only guard behavior are all correctly implemented.

One dead function (`scan_for_directive` singular) remains from the pre-refactor codebase and must be removed. The test file exceeds the 400-line limit and must be split. These are the only blocking issues.

**Overall Assessment**: Needs Minor Changes (all fixable)

---

## Issues Found

### Critical Issues

1. **`just dev` fails — test file exceeds 400-line limit**
   - Location: `tests/test_userpromptsubmit_shortcuts.py` (438 lines)
   - Problem: Line count check in `just dev` fails. Blocks CI.
   - Fix: Split into `test_userpromptsubmit_shortcuts.py` (Tier 1 + pattern guards + integration) and `test_userpromptsubmit_scanning.py` (fence detection + any-line + enhanced d: + long-form aliases + additive directives).
   - **Status**: FIXED

### Major Issues

1. **Dead function `scan_for_directive` (singular)**
   - Location: `agent-core/hooks/userpromptsubmit-shortcuts.py:212-262`
   - Problem: `scan_for_directive` (single-directive version) is never called. `main()` uses `scan_for_directives` (plural). The function is 51 lines of dead code including a full docstring and fence-tracking logic that duplicates `scan_for_directives`.
   - Fix: Delete the function.
   - **Status**: FIXED

### Minor Issues

1. **Fence-tracking logic triplicated**
   - Location: `is_line_in_fence`, `scan_for_directive` (removed), `scan_for_directives` — all contain identical fence-tracking blocks
   - Note: After removing `scan_for_directive`, duplication drops to two sites. `is_line_in_fence` exists for testing and potential future use. The remaining duplication is acceptable: `scan_for_directives` uses a single-pass approach that cannot call `is_line_in_fence` without regressing to O(n²).
   - **Status**: OUT-OF-SCOPE — single-pass vs per-line tradeoff is intentional; no fix needed.

2. **`call_hook` helper duplicated across two test files**
   - Location: `tests/test_userpromptsubmit_shortcuts.py:24-54` and `tests/test_userpromptsubmit_new_directives.py:24-51`
   - Note: Both files define identical `call_hook` helpers. Deduplication would require a conftest fixture or shared module. The `importlib` loading pattern (hyphen in filename) makes this more complex than standard fixture injection. The duplication is small (27 lines) and isolated.
   - **Status**: DEFERRED — the hook module load pattern (`importlib` for hyphenated filename) makes shared fixtures non-trivial; acceptable for now.

---

## Fixes Applied

- `tests/test_userpromptsubmit_shortcuts.py` — Split: removed `TestLongFormAliases`, `TestEnhancedDDirective`, `TestFencedBlockExclusion`, `TestAnyLineMatching`, `TestAdditiveDirectives` from this file (moved to new file)
- `tests/test_userpromptsubmit_scanning.py` — Created: contains `TestLongFormAliases`, `TestEnhancedDDirective`, `TestFencedBlockExclusion`, `TestAnyLineMatching`, `TestAdditiveDirectives` with boilerplate
- `agent-core/hooks/userpromptsubmit-shortcuts.py:212-262` — Deleted `scan_for_directive` (singular, dead code)

---

## Design Anchoring

| Design Item | Status | Evidence |
|-------------|--------|----------|
| D-5: b: = brainstorm (diverge without converging) | Satisfied | `_BRAINSTORM_EXPANSION` lines 92-98; `[BRAINSTORM]` system message |
| D-7: Additive directives, section-scoped | Satisfied | `scan_for_directives` + `main()` Tier 2 loop |
| Tier 2.5: additionalContext-only (no systemMessage for guards) | Satisfied | `main()` lines 927-937; `test_skill_editing_guard_verb_noun` asserts `"systemMessage" not in result` |
| xc/hc bracket format | Satisfied | COMMANDS dict lines 39-55 |
| r graduated lookup | Satisfied | COMMANDS dict lines 43-49 |
| Line-based Tier 1 matching | Satisfied | `main()` lines 887-903 |
| plan override (D-7 supersedes Step 2 first-match-wins) | Satisfied | `scan_for_directives` returns all matches |

---

## Positive Observations

- D-7 additive directive implementation is clean: two-pass approach (find indices, then slice sections) handles overlapping section boundaries correctly.
- Tier 2.5 guards correctly produce no `systemMessage` — stays invisible to user, only injects agent context.
- `xc`/`hc` expansions correctly note skill continuation chains, not just command flags — aligns with design intent.
- `r` graduated lookup description clearly enumerates the 3-step process without the old error-first framing.
- Test assertions in `TestPatternGuards.test_pattern_guard_no_false_positives` verify "the skill level is high" doesn't trigger — good boundary case.

## Recommendations

None beyond the applied fixes.
