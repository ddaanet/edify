# Outline Review: worktree-merge-resilience (round 2)

**Artifact**: plans/worktree-merge-resilience/outline.md
**Date**: 2026-02-23
**Mode**: review + fix-all

## Summary

Post-discussion revision is substantially improved. The diff3 segment-level approach replaces ours-wins, the resolution matrix is complete and correct, and the two-layer defense is well-grounded in the observed failure modes. Five issues found: no critical issues, two major (missing requirement traceability tags and unspecified conflict-path return behavior), three minor (vague line references, unspecified parser location, imprecise trigger mechanism). All fixed.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Detect orphaned content | Detection: Post-merge structural validation | Complete | Orphan check + structural invariant |
| FR-2: Segment-level diff3 merge | Prevention: Segment-level diff3 resolver | Complete | Full resolution matrix, merge base involved |
| FR-3: Integration into merge pipeline | Pipeline integration | Complete | _phase4 insertion, all 5 state machine paths, timing nuance documented |
| FR-4: Conflicts surface to user | Conflict output | Complete | Markers written, stderr report, stays in conflict list for exit code 3 |
| NFR-1: Block on detection | Pipeline integration (On failure) | Complete | Exit non-zero, emits line numbers |
| NFR-2: No false positives | False positive prevention | Complete | Aligned with extract_titles() skip, structural-only checks, clean-file fixture |

**Traceability Assessment**: All requirements covered with explicit section tags (FR-1 through FR-4, NFR-1, NFR-2).

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Missing explicit requirement tags on outline sections**
   - Location: Section headings (Prevention, Detection, Pipeline integration, Conflict output)
   - Problem: No FR-*/NFR-* references in section headings or bodies. Traceability was implicit based on content, not explicit via tags. With 6 requirements across multiple sections, implicit coverage risks drift during implementation.
   - Fix: Added FR/NFR tags to section headings: Prevention (FR-2, FR-4), Detection (FR-1, NFR-1), Pipeline integration (FR-3), Conflict output (FR-4), False positive prevention (NFR-2).
   - **Status**: FIXED

2. **Conflict-path return behavior unspecified**
   - Location: Conflict output section
   - Problem: The outline described writing conflict markers and reporting to stderr, but did not specify what happens to the `conflicts` list return value. Current `resolve_learnings_md()` always removes `agents/learnings.md` from the list and calls `git add`. On conflict, the file must NOT be added and must remain in the conflicts list so the caller reports it and exits with code 3. Without this specification, an implementer could `git add` the conflicted file.
   - Fix: Added paragraph specifying: on conflict, do NOT remove from conflicts, do NOT `git add`; on success, `git add` and remove as today.
   - **Status**: FIXED

### Minor Issues

1. **Affected file line reference imprecise**
   - Location: Line 53 (Affected file line)
   - Problem: "replace `resolve_learnings_md()` internals (lines 145-167)" — line 145 is the function signature, line 146-147 is the docstring. The body to rewrite is lines 148-167. Saying "internals" while citing the full function range is ambiguous about whether the signature changes.
   - Fix: Changed to "rewrite `resolve_learnings_md()` body (lines 148-167, keeping function signature at line 145)"
   - **Status**: FIXED

2. **Segment parser location unspecified**
   - Location: Key decisions, "Segment parser reuse"
   - Problem: "Lives in a shared location importable by both" is vague. Implementation would need to decide where to put it. `src/edify/validation/learnings.py` already defines `extract_titles()` with the same `TITLE_PATTERN` regex and is the natural home.
   - Fix: Added candidate location: `src/edify/validation/learnings.py`.
   - **Status**: FIXED

3. **Trigger mechanism imprecise for `merged` state**
   - Location: Pipeline integration, Trigger line
   - Problem: "check `git diff --name-only` against merge base or pre-merge HEAD" is vague. In the `merged` state, there are no staged changes (merge already committed). The trigger needs two detection paths: `git diff --cached --name-only` for pre-commit states, `git diff-tree` for already-committed states.
   - Fix: Replaced with specific git commands for both cases.
   - **Status**: FIXED

4. **Function signature compatibility not addressed**
   - Location: Prevention section
   - Problem: Outline described the diff3 approach needing a base input but didn't address whether the function signature changes or whether callers need updating. An implementer might add a `base` parameter and then need to update all callers.
   - Fix: Added "Function signature change" subsection clarifying base is read internally from `:1:` stage, no caller changes needed.
   - **Status**: FIXED

5. **Timing nuance for `merged` state not documented**
   - Location: Pipeline integration
   - Problem: Outline says "Block (exit non-zero)" uniformly, but in the `merged` state the commit already exists. Blocking at _phase4 top means the user creates a fix commit, not a pre-commit block. This difference matters for the user's mental model.
   - Fix: Added "Timing nuance" paragraph explaining the `merged` state behavior.
   - **Status**: FIXED

## Fixes Applied

- Section headings: Added FR/NFR requirement tags to Prevention, Detection, Pipeline integration, Conflict output sections
- Line 20-22: Added "Function signature change" subsection (base read internally, no caller changes)
- Line 47-49: Added conflict-path return behavior (no `git add`, stay in conflicts list, exit code 3)
- Line 53: "replace internals (lines 145-167)" changed to "rewrite body (lines 148-167, keeping function signature at line 145)"
- Line 86: Trigger mechanism replaced with specific git commands for staged and committed states
- Line 88-90: Added timing nuance paragraph for `merged` state
- Line 107: "Lives in a shared location" changed to candidate location in `src/edify/validation/learnings.py`

## Positive Observations

- Resolution matrix is complete (13 rows covering all 3-way combinations of absent/present/modified) with correct semantics for each case
- Convergent edit handling (both modified identically = no conflict) is a good design choice that reduces unnecessary manual resolution
- Two-layer defense is well-motivated: diff3 prevents conflict-path orphans, structural validator catches clean-merge orphans
- Misplaced content deferral is well-reasoned — both confirmed instances were conflict-path artifacts that diff3 would prevent
- Scope boundaries are precise and appropriate
- The "Block, not warn" rationale is strong (cost asymmetry)
- Testing approach covers all layers: parser, resolver, validator, integration

## Recommendations

- The `merged` state timing nuance could be addressed architecturally: move validation before the commit in _phase4 (read from staged content via `git show :0:agents/learnings.md` or from working tree). This would make blocking uniform across all states. Worth considering during implementation.
- The segment parser's heading pattern (`^## (.+)$`) should explicitly handle the `## ` prefix with exactly one space, matching `TITLE_PATTERN` in the existing validator. Edge case: headings with trailing whitespace.
- Integration tests that exercise the `merged` state path (where validation runs post-commit) should verify the error message suggests a fix commit rather than implying the commit was blocked.

---

**Ready for user presentation**: Yes
