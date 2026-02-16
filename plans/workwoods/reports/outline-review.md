# Outline Review: Workwoods

**Artifact**: plans/workwoods/outline.md
**Date**: 2026-02-16T00:00:00Z
**Mode**: review + fix-all

## Summary

The outline is technically sound with clear phase decomposition and appropriate TDD/general typing. All requirements are traceable to specific phases. The approach (filesystem inference replacing manual tracking) is feasible and well-scoped. Fixed issues relate to traceability clarity, test coverage specification, and risk documentation.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | Phase 3, Phase 4 | Complete | Cross-tree aggregation + upgraded wt-ls CLI |
| FR-2 | Phase 2 | Complete | Vet staleness via mtime |
| FR-3 | Phase 1 | Complete | Plan state inference module |
| FR-4 | Phase 5 | Complete | Worktree skill update for bidirectional merge |
| FR-5 | Phase 5 | Complete | Document existing additive merge behavior |
| FR-6 | Phase 1, Phase 6 | Complete | Foundation + elimination migration |
| NFR-1 | Approach, Phase 3 | Complete | Computed on demand, no stored state |
| NFR-2 | Approach | Complete | Read-only aggregation design |
| NFR-3 | Approach | Complete | Git-versioned or computed strategy |
| C-1 | Phase 2 | Complete | Filesystem mtime for vet staleness |
| C-2 | Phase 3 | Complete | Git commit hash for work counting |
| C-3 | Constraints | Complete | Noted as already satisfied |

**Traceability Assessment**: All requirements covered with explicit phase mappings added.

## Review Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Missing explicit requirements coverage in Approach**
   - Location: Approach section
   - Problem: Requirements mapping not visible in overview section, making traceability less obvious
   - Fix: Added "Requirements coverage" subsection with explicit FR/NFR/C mappings to phases
   - **Status**: FIXED

2. **Test coverage not specified in TDD phases**
   - Location: Phase 1, Phase 2, Phase 3, Phase 4
   - Problem: TDD phases lack explicit test coverage scope, making it unclear what edge cases to test
   - Fix: Added "Test coverage" bullet to each TDD phase with specific edge cases (Phase 1: artifact combinations; Phase 2: mtime edge cases, missing reports; Phase 3: multiple worktrees, dirty/clean states; Phase 4: output formatting, sorting)
   - **Status**: FIXED

3. **Vet naming convention not explicit in Phase 2**
   - Location: Phase 2
   - Problem: "Vet chain definition: source artifact → expected vet report (naming convention)" doesn't specify the actual naming convention
   - Fix: Added explicit examples (outline.md → reports/design-vet.md, runbook-phase-N.md → reports/checkpoint-N.md)
   - **Status**: FIXED

4. **Phase 3 commit counting details missing**
   - Location: Phase 3
   - Problem: "commit count since last handoff" doesn't specify the git command or anchor mechanism (C-2)
   - Fix: Added explicit git command reference (\`git log -1 --format=%H -- agents/session.md\` as anchor) and noted C-2
   - **Status**: FIXED

5. **Phase 4 rich output format underspecified**
   - Location: Phase 4
   - Problem: "human-readable multi-line per tree" doesn't list what fields are displayed
   - Fix: Added explicit field list (worktree name, plan, status, commits since handoff, latest commit subject, vet chain status, clean/dirty)
   - **Status**: FIXED

6. **Phase 5 session snippet squash undefined**
   - Location: Phase 5, D-5
   - Problem: Requirements mention "volatile — squashed on merge" but outline doesn't clarify what this means
   - Fix: Added clarification task ("clarify and document how status snippets are handled on merge") in Phase 5 and expanded D-5 to note the need for definition
   - **Status**: FIXED

7. **Phase 6 execute-rule.md duplication risk**
   - Location: Phase 6
   - Problem: Both Phase 5 and Phase 6 mention updating execute-rule.md STATUS section
   - Fix: Added note in Phase 6 to verify no duplication with Phase 5
   - **Status**: FIXED

8. **Missing Dependencies section**
   - Location: Outline structure
   - Problem: D-6 mentions worktree-merge-data-loss dependency but no Dependencies section aggregates all dependencies
   - Fix: Added Dependencies section with external (worktree-merge-data-loss, worktree-update R1) and internal phase dependencies
   - **Status**: FIXED

9. **Missing Risks section**
   - Location: Outline structure
   - Problem: Several risks implied (session snippet squash undefined, mtime reliability per C-1, naming conventions per Phase 2) but not explicitly documented
   - Fix: Added Risks section with R-1 (session snippet squash), R-2 (transition validation complexity), R-3 (vet naming conventions), R-4 (filesystem mtime reliability)
   - **Status**: FIXED

10. **Scope section lacks phase references**
    - Location: Scope section
    - Problem: In-scope items don't reference which phases implement them
    - Fix: Added phase numbers to each in-scope item for traceability
    - **Status**: FIXED

## Fixes Applied

- Approach section — Added "Requirements coverage" subsection with FR/NFR/C → phase mappings
- Phase 1 — Added test coverage specification (artifact combinations, state transitions, next action derivation)
- Phase 2 — Added explicit vet naming convention examples, filesystem mtime note (C-1), test coverage specification
- Phase 3 — Added explicit git command for commit counting (C-2), clean/dirty state command, NFR-1 note, test coverage specification
- Phase 4 — Added explicit field list for rich output format, sorting note (FR-1), test coverage specification
- Phase 5 — Expanded session snippet squash task with clarification directive, added worktree-merge-data-loss dependency note (D-6)
- Phase 6 — Added verification note to avoid execute-rule.md duplication, test coverage specification
- D-5 — Expanded to note session snippet squash needs definition with specific question
- Dependencies section — Created with external (worktree-merge-data-loss, worktree-update R1) and internal phase dependencies
- Risks section — Created with R-1 (session snippet squash), R-2 (transition validation), R-3 (naming conventions), R-4 (mtime reliability)
- Scope section — Added phase references to each in-scope item

## Positive Observations

- **Clear phase decomposition**: TDD phases (1-4, 6 validation) separated from general phases (5, 6 skill updates) with appropriate typing
- **Explicit design decisions**: D-1 through D-6 document key architectural choices with rationale
- **Resolved open questions**: All four open questions from requirements resolved with explicit answers
- **Scope discipline**: Out-of-scope items explicitly listed with rationale (separate plans, deferred features)
- **Module structure decision**: D-1 creates planstate module independent of worktree operations, enabling reuse
- **Backward compatibility**: D-2 preserves old wt-ls format via --porcelain flag
- **Incremental migration**: D-3 transition strategy (both sources, warn on drift, remove after validation) reduces risk

## Recommendations

**For design phase:**
- **Session snippet squash definition**: Phase 5 needs to define what "status snippet" refers to (session.md heading? specific section?) and what "squashed" means (removed? merged? overwritten?). Analyze `_resolve_session_md_conflict()` code for current behavior.
- **Vet naming convention validation**: Phase 2 test coverage should include tests for non-standard naming to detect convention violations early.
- **Transition validation metrics**: Phase 6 should define what constitutes "acceptable drift" during transition (e.g., all plans in jobs.md present in planstate inference, but planstate may discover additional unlisted plans).

**For execution:**
- **Phase 5 dependency gate**: Confirm worktree-merge-data-loss Track 1 + Track 2 are deployed before starting Phase 5. Check via git log or deployment status.
- **execute-rule.md coordination**: Verify Phase 5 and Phase 6 execute-rule.md changes don't conflict. Consider consolidating into single update in Phase 5 if STATUS section migration can be done once.

---

**Ready for user presentation**: Yes
