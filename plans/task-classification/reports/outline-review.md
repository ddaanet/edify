# Outline Review: task-classification

**Artifact**: plans/task-classification/outline.md
**Date**: 2026-02-24
**Mode**: review + fix-all

## Summary

Well-structured outline covering two complementary features refined through 8 rounds of discussion. The design demonstrates clear reasoning about dropped alternatives and makes explicit decisions. Primary gaps were incomplete scope enumeration (missing 3 code files that hardcode current section names) and insufficient treatment of failure modes from the superseded `operational-tooling.md` decision.

**Overall Assessment**: Needs Iteration

## Requirements Traceability

Requirements are conversation-derived (no formal `requirements.md`). Extracted from outline content and task context.

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| CR-1: `/prime` loads plan artifacts | Approach (Feature 1), D-1 | Complete | -- |
| CR-2: `/prime` chain-calls `/recall` | Approach (Feature 1), D-3 | Complete | -- |
| CR-3: `/prime` in task commands via handoff | Approach (Placement) | Complete | Task command example fixed (removed `&&` chaining) |
| CR-4: No workflow skill modifications | D-1, Scope (OUT) | Complete | -- |
| CR-5: Two-section replacement | Approach (Feature 2) | Complete | -- |
| CR-6: Static classification (no moves) | Approach (Feature 2), D-4 | Complete | -- |
| CR-7: Avoid prior failure modes | D-4 | Complete | Was Partial -- expanded to address all 3 failure modes |
| CR-8: Inline markers without moves | Approach (Feature 2) | Complete | -- |
| CR-9: `#status` display updated | D-7, Scope (IN) | Complete | -- |
| CR-10: `#execute` pickup updated | D-8, Scope (IN) | Complete | -- |
| CR-11: `focus_session()` scope | D-6 | Complete | -- |
| CR-12: Classification heuristic | D-9 | Complete | -- |
| CR-13: Backward compatibility | D-5 | Complete | -- |

**Traceability Assessment**: All requirements covered. Gaps identified and fixed.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Incomplete failure mode analysis for superseded decision**
   - Location: D-4 (line 50, original)
   - Problem: `operational-tooling.md` "When Tracking Worktree Tasks In Session.md" identified three failure modes: (a) merge-commit amend ceremony, (b) manual editing for bare-slug worktrees, (c) drift from filesystem state. Outline only addressed (a). Superseding a codified decision without addressing all its failure modes risks reintroducing the solved problems.
   - Fix: Expanded D-4 to explicitly address all three failure modes. Added "Bare-slug worktrees" and "Filesystem drift" paragraphs to Approach section.
   - **Status**: FIXED

2. **Missing code files in scope**
   - Location: Scope (IN, Feature 2)
   - Problem: Three files with hardcoded "Pending Tasks" / "Worktree Tasks" references were missing from scope: `resolve.py` (merge autostrategy), `session_structure.py` (validation), `aggregation.py` (planstate). Implementing without updating these causes runtime failures.
   - Fix: Added `resolve.py`, `session_structure.py`, and `aggregation.py` to scope with specific change descriptions.
   - **Status**: FIXED

3. **D+B compliance not noted for new skill**
   - Location: Key Decisions (between D-3 and D-4)
   - Problem: `/prime` is a new skill. The D+B convention (`implementation-notes.md` "How to Prevent Skill Steps From Being Skipped") requires every skill step to open with a concrete tool call. Outline didn't note compliance, risking a prose-only step in implementation.
   - Fix: Added D-3a documenting D+B compliance analysis for `/prime` steps.
   - **Status**: FIXED

### Minor Issues

1. **Decision file update not in scope**
   - Location: Scope (IN, Feature 2)
   - Problem: D-4 supersedes a codified decision in `operational-tooling.md` but the scope didn't include updating that decision file.
   - Fix: Added `operational-tooling.md` update to scope section.
   - **Status**: FIXED

2. **Invalid `&&` chaining in task command example**
   - Location: Approach (Feature 1, Placement)
   - Problem: Example used `/prime plans/prepare-runbook-fixes/ && edit` -- skill invocations don't chain with shell `&&`. Misleading for implementation.
   - Fix: Removed `&& edit` from example. Added clarifying note about skill invocation semantics.
   - **Status**: FIXED

3. **Open questions had implicit answers**
   - Location: Open Questions section
   - Problem: Both questions had answers implied by existing decisions (D-8, D-9) but were stated as unresolved. Leaves impression of more ambiguity than exists.
   - Fix: Added recommendations to each question that connect them to existing decisions, while preserving them as open for user confirmation.
   - **Status**: FIXED

## Fixes Applied

- D-4 (line 50) -- expanded to address all three failure modes from superseded `operational-tooling.md` decision
- Approach (Feature 2, after line 39) -- added "Bare-slug worktrees" and "Filesystem drift" paragraphs
- Key Decisions (after D-3) -- added D-3a documenting `/prime` D+B compliance
- Scope IN (Feature 2) -- added `resolve.py`, `session_structure.py`, `aggregation.py`, `operational-tooling.md`
- Task command example (line 25) -- removed `&& edit`, added invocation semantics note
- Open Questions -- added recommendations linking to existing decisions

## Positive Observations

- Clean separation of two features that could easily blur together
- Explicit "what was dropped and why" in Discussion Log and OUT scope -- valuable for future context
- D-4's supersession of a codified decision is honest and well-reasoned (static classification is genuinely cleaner than move semantics)
- Chain-call design (D-3) leverages existing `/recall` infrastructure without duplication
- Classification heuristic (D-9) has clear bright-line rules for common cases

## Recommendations

- Open Questions 1 and 2 have recommendations attached but need user confirmation before closing
- Implementation should validate the `aggregation.py` call site -- it may need to search both "In-tree Tasks" and "Worktree Tasks" or use a different approach (section-agnostic task extraction)
- The `resolve.py` merge autostrategy changes are explicitly OUT of scope for the `_worktree merge` autostrategy fix (separate task). Clarify during implementation whether the section-name update is a minimal rename vs. a behavioral change

---

**Ready for user presentation**: Yes -- all issues fixed, approach is sound, clear enough for user evaluation. Open questions have recommendations but warrant user confirmation.
