# Deliverable Review: worktree-merge-data-loss

**Date:** 2026-02-16
**Methodology:** agents/decisions/deliverable-review.md
**Design reference:** plans/worktree-merge-data-loss/design.md

## Inventory

| Type | File | Lines |
|------|------|-------|
| Code | `src/claudeutils/worktree/cli.py` | 394 |
| Code | `src/claudeutils/worktree/merge.py` | 349 |
| Code | `src/claudeutils/worktree/utils.py` | 146 |
| Test | `tests/test_worktree_rm_guard.py` (new) | 276 |
| Test | `tests/test_worktree_merge_correctness.py` (new) | 309 |
| Test | `tests/fixtures_worktree.py` (modified) | 339 |
| Test | `tests/test_worktree_commands.py` (modified) | 400 |
| Test | `tests/test_worktree_merge_submodule.py` (modified) | 293 |
| Test | `tests/test_worktree_session_automation.py` (modified) | 229 |
| Agentic prose | `agent-core/skills/worktree/SKILL.md` | 135 |
| **Unspecified** | `scripts/scrape-validation.py` | 559 |

**Design conformance:** 8/9 FRs satisfied, 6/7 design decisions conformed. FR-4 and D-2 partial (exit 2 on `_delete_branch` failure not implemented).

## Critical Findings

None.

## Major Findings

**1. `_delete_branch` swallows unexpected failure instead of exit 2**
- Source: deliverable-review-code.md, Finding #1
- File: `cli.py:351-352`
- Design: FR-4/D-2 specify exit 2 for errors. On `git branch -d` failure, code emits stderr but exits 0.
- Impact: Downstream consumers (SKILL.md Mode C) assume clean removal on exit 0. Branch corruption goes unreported.

**2. Manual sys.stderr capture in merge correctness tests**
- Source: deliverable-review-tests.md, Finding M-1
- File: `test_worktree_merge_correctness.py:178-186, 203-211, 244-252`
- Three tests manually swap `sys.stderr` with StringIO. Fragile (misses fd-level writes), risks test pollution. Connected to code using `sys.stderr.write()` instead of `click.echo(..., err=True)`.

**3. rm exit 2 not handled in SKILL.md Mode C**
- Source: deliverable-review-prose.md, Finding #4
- File: `SKILL.md:94-99`
- Mode C step 3 dispatches on rm exit 0 and exit 1 but omits exit 2. Agent encountering rm exit 2 after successful merge has no instruction. Technically outside FR-9 scope but creates incomplete dispatch.

## Minor Findings

**Style/convention:**
- `sys.stderr.write` vs `click.echo(..., err=True)` inconsistency in merge.py (code #2)
- Section banner comments in fixtures_worktree.py violate deslop convention (tests m-1)
- `_is_branch_merged` trivial docstring restates function name (code #5, tests m-2)

**Conformance:**
- `_classify_branch` placed in utils.py instead of cli.py per design (code #3) — negligible impact
- SKILL.md escalation message adds sentence not in design (prose #1) — improves actionability
- SKILL.md step 3 instruction ordering: amend described before exit code check (prose #3)

## Gap Analysis

| Requirement | Status | Reference |
|-------------|--------|-----------|
| FR-1: rm classifies branch | Covered | cli.py:322-325 |
| FR-2: rm refuses unmerged | Covered | cli.py:339 |
| FR-3: rm allows focused-session | Covered | cli.py:326-327 |
| FR-4: rm exit codes 0/1/2 | **Partial** | Exit 2 missing (Major #1) |
| FR-5: No destructive output | Covered | Test: test_rm_no_destructive_suggestions |
| FR-6: Phase 4 MERGE_HEAD checkpoint | Covered | merge.py:314-319 |
| FR-7: Post-merge ancestry validation | Covered | merge.py:262-288 |
| FR-8: rm reports removal type | Covered | cli.py:389-394 |
| FR-9: Skill handles rm exit 1 | Covered | SKILL.md:94-99 |
| D-1 through D-7 | Conforms | D-2 partial (same as FR-4) |

**Unspecified deliverable:** `scripts/scrape-validation.py` (559 lines) — lint refactor for ruff compliance, not in design scope. Justified: was blocking worktree merge (70 violations).

**Test coverage gap:** No test for `_delete_branch` failure path (connected to Major #1).

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 3 |
| Minor | 6 |

The core data loss fix is correct and well-tested. Both the removal guard (Track 1) and MERGE_HEAD checkpoint (Track 2) work as designed. The three major findings share a theme: incomplete exit 2 handling across code, tests, and skill prose. Major #1 (code) is the root — fixing `_delete_branch` to raise SystemExit(2) would cascade to requiring a test (closing the test gap) and motivating the SKILL.md exit 2 dispatch (Major #3).

**Sub-reports:**
- `plans/worktree-merge-data-loss/reports/deliverable-review-code.md`
- `plans/worktree-merge-data-loss/reports/deliverable-review-tests.md`
- `plans/worktree-merge-data-loss/reports/deliverable-review-prose.md`
