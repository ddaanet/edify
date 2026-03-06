# Outline Review: active-recall

**Artifact**: plans/active-recall/outline.md
**Date**: 2026-03-06
**Mode**: review + fix-all (PDR criteria)

## Summary

The outline is well-structured with clear phase ordering, explicit rationale for key decisions, and good traceability to most requirements. Primary gaps were: NFR-1/NFR-2 not explicitly addressed, PreToolUse hook work listed in scope but unassigned to a phase, a scope contradiction around version-change detection, and the Phase 4/5 ordering risk acknowledged but under-mitigated. All issues fixed.

**Overall Assessment**: Needs Iteration — all issues fixed, but design discussion conclusions (key structure, Context7 cache model) need user confirmation that requirements.md updates are complete before design proceeds.

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | Phase 3 | Complete | Structure, parser, migration, recall loop |
| FR-2 | Phase 4 | Complete | Trigger class metadata, automation profile note added |
| FR-3 | Phase 4 | Complete | Category metadata, path-derived classification |
| FR-4 | Phase 6 | Complete | Pipeline, corrector, idempotency, Context7 |
| FR-5 | Phase 5 | Complete | Grounding research, format spec output |
| FR-6 | Cross-Cutting | Complete | Expanded with acceptance criteria verification |
| FR-7 | Phase 4 | Complete | Mode reduction, pipeline point updates |
| FR-8 | Phase 2 | Complete | Three-module merge, deprecation plan |
| NFR-1 | Phase 3 (added) | Complete | O(log_k(N)) lookup, context budget analysis |
| NFR-2 | Phase 3 (added) | Complete | All CLI commands enumerated with disposition |
| NFR-3 | Phase 3 | Complete | Mixed-format parser, incremental migration |
| NFR-4 | Phase 3 / Q-1 | Partial | Referenced as design target; threshold deferred to design (appropriate) |
| C-1 | Phase ordering | Complete | Phase 5 before Phase 6 |
| C-2 | Phase ordering | Complete | Phase 3 before Phase 6 |
| C-3 | Phase ordering | Complete | Phase 1 before Phase 3 |
| C-4 | Phase 3 (added) | Complete | Full infrastructure accounting table added |

**Traceability Assessment**: All requirements covered. NFR-4 threshold appropriately deferred to design phase.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **NFR-1 (scaling capacity) not addressed**
   - Location: Phase 3
   - Problem: No discussion of lookup performance at scale or context budget impact
   - Fix: Added "Scaling (NFR-1)" subsection with O(log_k(N)) analysis and context budget note
   - **Status**: FIXED

2. **NFR-2 (backward compatibility) incompletely addressed**
   - Location: Phase 2-3
   - Problem: Only `_when` deprecation mentioned. `_recall check`, `_recall diff`, hook, skills not enumerated
   - Fix: Added "Backward compatibility (NFR-2)" subsection listing all CLI commands and their disposition
   - **Status**: FIXED

3. **C-4 (infrastructure accounting) not systematically verified**
   - Location: Outline-wide
   - Problem: C-4 lists 9 specific infrastructure items; outline mentions most but doesn't cross-reference
   - Fix: Added "Existing infrastructure accounting (C-4)" table mapping each item to its handling phase
   - **Status**: FIXED

4. **Phase 4/5 ordering risk under-mitigated**
   - Location: Phase 4
   - Problem: Phase 4 commits to metadata taxonomy before Phase 5 grounding validates it. Risk section notes this but Phase 4 itself doesn't acknowledge it
   - Fix: Added "Ordering note" at top of Phase 4 with explicit risk acceptance rationale (metadata fields are additive, code structure unaffected)
   - **Status**: FIXED

### Minor Issues

1. **tiktoken encoding claim inaccurate**
   - Location: Phase 1, key decision
   - Problem: "cl100k_base encoding, used by Claude models" — Claude does not use cl100k_base (that's OpenAI's tokenizer)
   - Fix: Reworded to "practical approximation" with note that Claude's tokenizer is not publicly available
   - **Status**: FIXED

2. **Entry count discrepancy**
   - Location: Phase 5
   - Problem: "362 entries" vs requirements' "366 entries"
   - Fix: Updated to 366 (matches requirements)
   - **Status**: FIXED

3. **PreToolUse hook work unassigned**
   - Location: Scope boundaries IN list vs phases
   - Problem: "PreToolUse hook update for new paths" listed as in-scope but no phase describes the work
   - Fix: Added "PreToolUse hook update" subsection to Phase 3 and referenced in C-4 accounting
   - **Status**: FIXED

4. **FR-6 approach too thin**
   - Location: Cross-Cutting section
   - Problem: Missing verification against FR-6 acceptance criteria (retrievable entry, pipeline point confirmation)
   - Fix: Added three bullet points mapping to FR-6 acceptance criteria
   - **Status**: FIXED

5. **Version-change detection scope contradiction**
   - Location: Scope OUT vs Open Questions Q-4
   - Problem: Listed as OUT ("deferred to design — Q-1") but Q-4 asks design to resolve it — contradictory
   - Fix: Clarified OUT scope: mechanism selected in design (Q-4), implementation deferred past project
   - **Status**: FIXED

6. **Key structure design decision missing**
   - Location: Phase 3
   - Problem: Session handoff documents "prefix-free, colon-delimited domains" key structure decision — not in outline
   - Fix: Added key structure decision to Phase 3 design decisions
   - **Status**: FIXED

7. **FR-2 trigger class distinction lacks recall context**
   - Location: Phase 4, FR-2
   - Problem: Recall entry "when converting external documentation to recall entries" provides critical automation profile distinction (when=hand-curation, how=automation-safe) that should inform FR-2 and FR-4 design
   - Fix: Added recall-informed note to FR-2 about corrector intensity differing by class
   - **Status**: FIXED

## Fixes Applied

- Phase 1: Corrected tiktoken rationale (not Claude's tokenizer, practical approximation)
- Phase 3: Added NFR-1 scaling subsection (O(log_k(N)), context budget)
- Phase 3: Added NFR-2 backward compatibility subsection (all CLI commands enumerated)
- Phase 3: Added PreToolUse hook update subsection
- Phase 3: Added C-4 infrastructure accounting table
- Phase 3: Added key structure design decision (prefix-free, colon-delimited)
- Phase 4: Added ordering risk note at section top
- Phase 4 FR-2: Added recall-informed automation profile note
- Phase 5: Fixed entry count 362 -> 366
- Cross-Cutting FR-6: Added acceptance criteria verification bullets
- Scope OUT: Clarified version-change detection (mechanism in design, implementation deferred)

## Positive Observations

- Phase dependency ordering correctly satisfies C-1 through C-3
- "Each phase is independently deployable" — good incremental delivery stance
- Phase 2 consolidation-before-migration is sound sequencing (reduces migration surface)
- Codebase exploration results embedded in outline (module counts, model names) — grounded, not speculative
- Context7 correctly scoped as "query-keyed cache, not bulk import" — matches design discussion
- NFR-3 mixed-format parser approach is pragmatic for incremental migration
- Risk section identifies the Phase 4/5 ordering tension proactively

## Recommendations

- **User confirmation needed:** Session handoff lists three design discussion conclusions to integrate into requirements.md. Verify requirements.md reflects current decisions before design phase begins
- **Phase 4/5 ordering:** Consider whether Phase 5 (grounding) should move before Phase 4, or whether the current ordering (with accepted rework risk) is preferred. User input would resolve this
- **Token budget threshold (Q-1):** Design should establish concrete threshold early — it affects Phase 3 split decisions and NFR-1 scaling properties
- **Recall anti-pattern awareness:** The resolved recall entry "when evaluating recall system effectiveness" warns that tool-based recall improvements don't address the recognition problem. Design should consider how hierarchical structure affects recognition (does domain-level selection help or hurt agent discovery of relevant entries?)

## Recall Context Applied

Resolved entries from `plans/active-recall/recall-artifact.md` that informed review:
- "when converting external documentation to recall entries" — applied to FR-2 automation profile distinction
- "when evaluating recall system effectiveness" — recognition vs retrieval gap, noted in recommendations
- "when recall loads new entries mid-artifact" — verified outline doesn't have mid-artifact consistency issues
- "when too many rules in context" — relevant to NFR-1 scaling (context budget for large index)

---

**Ready for user presentation**: Yes — all issues fixed. User input recommended on Phase 4/5 ordering preference and requirements.md update confirmation before proceeding to design.
