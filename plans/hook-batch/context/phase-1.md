# Phase 1: UserPromptSubmit Improvements

**Type:** TDD | **Model:** sonnet
**Target:** `agent-core/hooks/userpromptsubmit-shortcuts.py` (839 lines)
**Test file:** `tests/test_userpromptsubmit_shortcuts.py` (282 lines)

## Prerequisites

- Read `agent-core/hooks/userpromptsubmit-shortcuts.py` lines 765-839 — current `main()` structure (Tier 1 at 772, Tier 2 at 784-812, Tier 3 at 814-832)
- Read `agent-core/hooks/userpromptsubmit-shortcuts.py` lines 156-206 — current `scan_for_directive()` implementation
- Read `tests/test_userpromptsubmit_shortcuts.py` — existing test classes and helper `call_hook()`
- `scan_for_directive` already scans all lines (not first-line-only). Cycle 1.1 targets only Tier 1 COMMANDS (line 772 `if prompt in COMMANDS`), not directives.
- Existing `TestAnyLineMatching.test_any_line_matching` (line 222) asserts first-directive-only behavior. Cycle 1.3 GREEN must update this test to expect additive behavior.

## Key Decisions

- D-7: Directives are additive (all fire), section-scoped. First-match-return is eliminated.
- Tier 1 (COMMANDS) still first-match-wins — only one shortcut per prompt makes sense.
- Pattern guards (Tier 2.5) are additionalContext-only — no systemMessage. Additive.
- Tier 3 continuation runs even when directives fire (no early return from Tier 2 after D-7).

## Checkpoint: After Cycle 1.3

Run full test suite before proceeding to Cycles 1.4-1.5:

```bash
pytest tests/test_userpromptsubmit_shortcuts.py -v
```

Gate criteria:
- All tests pass (0 failures)
- `call_hook("d: discuss\np: task")` → additionalContext contains both DISCUSS and PENDING
- `call_hook("s")` → systemMessage contains `"[#status]"` (Tier 1 regression)
- `call_hook("s\nsome text")` → additionalContext contains `"[#status]"`, no systemMessage
- Continuation prompt (e.g., `/handoff --commit`) still parses via Tier 3

If any gate fails: STOP. Fix before proceeding to Cycle 1.4.

## Completion Validation

```bash
pytest tests/test_userpromptsubmit_shortcuts.py -v
```

Success criteria:
- All tests pass (0 failures)
- Key tests: test_tier1_shortcut_on_own_line (1.1), test_r_expansion_graduated_lookup + test_xc_hc_bracket_compression (1.2), test_multiple_directives_both_fire (1.3), test_p_directive_dual_output + test_b_brainstorm_directive + test_q_quick_directive + test_learn_directive (1.4), test_skill_editing_guard_verb_noun + test_ccg_guard_hooks_keyword + test_guard_additive_with_directive (1.5)
- Existing classes (TestLongFormAliases, TestEnhancedDDirective, TestFencedBlockExclusion, TestIntegration) all still pass

Line count check: `wc -l agent-core/hooks/userpromptsubmit-shortcuts.py` — expect ~950-980 lines (was 839).

## Stop Conditions

- RED fails to fail → STOP: test too weak or already-passing, diagnose before proceeding
- GREEN passes without implementation → STOP: test too weak, strengthen before committing
- Cycle 1.3 GREEN: if `TestAnyLineMatching.test_any_line_matching` fails unexpectedly → review multi-directive assertion update
- Implementation needs architectural decision → STOP, escalate
