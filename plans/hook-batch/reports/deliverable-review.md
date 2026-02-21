# Deliverable Review: hook-batch

**Date:** 2026-02-21
**Methodology:** agents/decisions/deliverable-review.md
**Design baseline:** plans/hook-batch/outline.md + plans/hook-batch/userpromptsubmit-plan.md

## Inventory

| Type | File | Lines |
|------|------|-------|
| Code | agent-core/hooks/userpromptsubmit-shortcuts.py | 955 |
| Code | agent-core/hooks/pretooluse-recipe-redirect.py | 35 |
| Code | agent-core/hooks/posttooluse-autoformat.sh | 21 |
| Code | agent-core/hooks/sessionstart-health.sh | 41 |
| Code | agent-core/hooks/stop-health-fallback.sh | 46 |
| Code | agent-core/bin/learning-ages.py | 238 |
| Code | agent-core/bin/sync-hooks-config.py | 137 |
| Test | tests/test_userpromptsubmit_shortcuts.py | 225 |
| Test | tests/test_userpromptsubmit_new_directives.py | 103 |
| Test | tests/test_userpromptsubmit_scanning.py | 264 |
| Test | tests/test_pretooluse_recipe_redirect.py | 199 |
| Config | agent-core/hooks/hooks.json | 57 |
| Config | agent-core/justfile | 104 |
| Config (gen) | .claude/settings.json | 157 |
| **Total** | **14 files** | **2582** |

**Tests:** 33 total (21 UPS + 12 scanning/directives + 10 recipe-redirect), all passing.

## Critical Findings

None.

## Major Findings

1. **Tier 2.5 pattern guards block Tier 3 continuation parsing**
   - `userpromptsubmit-shortcuts.py:917-928`
   - Design requirement: userpromptsubmit-plan.md execution order steps 3-5 specify "Combine Tier 2.5 + Tier 3 results if both match, output." Runbook outline Cycle 1.3: "Falls through to Tier 2.5 and Tier 3 after collecting directives."
   - Implementation: `if context_parts:` at line 917 returns after collecting ANY Tier 2 or Tier 2.5 output. Tier 3 continuation parsing never runs when pattern guards fire.
   - Impact: `fix the skill /handoff and /commit` → skill-editing guard fires (Tier 2.5), but the `/handoff and /commit` continuation chain (Tier 3) is lost. The agent gets the editing reminder without the continuation context.
   - Practical frequency: Low — requires editing-verb+skill-noun or platform-keyword combined with multi-skill continuation in the same prompt. But the design explicitly specifies the combination.
   - Fix: When only Tier 2.5 (no Tier 2 directives) collected context, fall through to Tier 3 and combine. When Tier 2 directives fired, returning before Tier 3 is arguably correct (directives change mode).

## Minor Findings

**Test structure:**
- `call_hook` helper duplicated across 3 UPS test files (22 lines × 3 = 66 lines of identical boilerplate). Shared `conftest.py` fixture or `tests/helpers.py` module would eliminate this. Already noted in vet-review.md and tdd-process-review.md.

**Code duplication:**
- Health check logic (dirty tree, learnings summary, stale worktrees, JSON output) duplicated between `sessionstart-health.sh` (lines 12-41) and `stop-health-fallback.sh` (lines 17-46). If a health check is added or modified, both files need updating.
- `sync-hooks-config.py` `merge_hooks` (lines 71-109) has identical merge logic for matcher=None and matcher!=None branches. Single function with predicate parameter would halve the code.

**Dead code:**
- `is_line_in_fence()` (lines 155-211) is not called by any production code. `scan_for_directives()` has its own inline fence tracking. The function is only used in tests for verifying fence detection independently. Not harmful but 57 lines of untested-in-production code.

**Error handling:**
- `posttooluse-autoformat.sh` lines 14-15: `2>/dev/null` suppresses ruff stderr. Design says "stderr on failure (non-fatal)." Suppression is defensible (keeps hook stdout clean for JSON parsing) but contradicts the design's explicit intent.

**Configuration:**
- `hooks.json` specifies `"timeout": 5` only for UserPromptSubmit. Other hooks have no timeout. All hooks should arguably have timeouts for operational safety, though the lightweight scripts (< 50 lines) are unlikely to hang.

## Gap Analysis

| FR | Requirement | Status | Reference |
|----|-------------|--------|-----------|
| FR-1 | Line-based shortcut matching | Covered | `main()` lines 865-881; TestTier1Commands (5 tests) |
| FR-2 | r graduated lookup | Covered | COMMANDS['r'] lines 46-52; test_r_expansion_graduated_lookup |
| FR-3 | xc/hc bracket compression | Covered | COMMANDS['xc'/'hc'] lines 42-57; test_xc_hc_bracket_compression |
| FR-4 | Additive directive scanning (D-7) | Covered | scan_for_directives(); TestAdditiveDirectives (3 tests) |
| FR-5 | p: dual output | Covered | main() lines 893-894; test_p_directive_dual_output |
| FR-6 | b: + q: + learn: directives | Covered | Lines 94-131; TestNewDirectives (5 tests) |
| FR-7 | Skill-editing guard | Covered | Lines 136-146, 905-909; test_skill_editing_guard_* (2 tests) |
| FR-8 | CCG integration | Covered | Lines 147-152, 911-914; test_ccg_guard_* (2 tests) |
| FR-9 | PreToolUse recipe-redirect | Covered | pretooluse-recipe-redirect.py; TestRedirectPatterns (6 tests) |
| FR-10 | PostToolUse auto-format | Covered | posttooluse-autoformat.sh (21 lines, manual validation) |
| FR-11 | learning-ages.py --summary | Covered | Lines 202-212; called by health scripts |
| FR-12 | SessionStart health script | Covered | sessionstart-health.sh (3 checks + flag file) |
| FR-13 | Stop health fallback | Covered | stop-health-fallback.sh (flag check + 3 checks) |
| FR-14 | hooks.json config source of truth | Covered | hooks.json (5 events registered) |
| FR-15 | sync-hooks-config.py | Covered | sync-hooks-config.py (137 lines, idempotent merge) |
| FR-16 | sync-to-parent integration | Covered | justfile lines 93-94 |
| FR-17 | Restart verification | Covered | settings.json has all entries |

**Missing deliverables:** None.
**Unspecified deliverables:** None.

## Summary

- **Critical:** 0
- **Major:** 1 (Tier 2.5/Tier 3 combination gap)
- **Minor:** 6

All 17 functional requirements are implemented with test coverage. The vet review (vet-review.md) already caught and fixed the --summary flag loss and minor style issues. The one major finding is a design conformance gap in the tier interaction model: pattern guards prevent continuation parsing from running, contrary to the plan's specified execution order.
