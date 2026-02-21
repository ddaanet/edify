# Outline Review: Quality Infrastructure Reform

**Artifact**: plans/quality-infrastructure/outline.md
**Date**: 2026-02-21
**Mode**: review + fix-all

## Summary

Well-structured outline with clear design decisions grounded in exploration data (D-1 backed by reviewer usage report). All three FRs traced to phases with explicit dependency ordering. Seven issues found — all fixed: count inaccuracies, a missing code rule that would be lost on deslop.md deletion, incomplete reference sweep for deslop removal, and missing terminology propagation items.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 (deslop restructuring) | D-3, D-4, Phase 2 | Complete | Prose→communication.md, code stays in project-conventions, deslop.md deleted |
| FR-1: prose rules → communication.md | Phase 2a | Complete | 5 rules, examples stripped, principle discarded |
| FR-1: code rules → pipeline-only | D-3, Phase 2b-2d | Complete | project-conventions skill injection; missing "expose fields" rule added |
| FR-1: remove deslop.md from CLAUDE.md | Phase 2e | Complete | Reference removal + file deletion |
| FR-1: inject code deslop mechanism | D-3 | Complete | skills: frontmatter on artisan + test-driver |
| FR-2 (code density decisions) | Phase 3 | Complete | 5 entries in cli.md + memory-index triggers |
| FR-2: general-first framing | Phase 3a | Complete | References /ground framing rule |
| FR-3a (review/correct renames) | D-1, D-2, D-6, D-7, Phase 1a/1d | Complete | 6 renames + 1 deprecation + 1 embed |
| FR-3a: vet-agent open question | D-1 | Complete | Resolved: deprecate (zero active call sites) |
| FR-3a: vet-taxonomy embed | D-2 | Complete | Inline in corrector.md |
| FR-3a: report naming (correction) | Phase 1e | Complete | Added terminology propagation item |
| FR-3a: vet-requirement.md | D-6 | Complete | Rename to review-requirement.md |
| FR-3a: /vet skill | D-7 | Complete | Rename to /review |
| FR-3b (execution renames) | Phase 1a | Complete | 5 renames listed |
| FR-3c (plan-specific deletions) | Phase 1c | Complete | 8 files listed |
| FR-3d (unchanged agents) | — | Complete | Out of scope by design (no changes needed) |
| Dependencies: FR-1/FR-3 interaction | D-6 | Complete | vet-requirement renamed, not absorbed |
| Dependencies: FR-3 restart | Phase 1f | Complete | Restart note added |
| Dependencies: FR-2 ordering | D-5 | Complete | FR-3 → FR-1 → FR-2 |
| Non-Requirements: no new agents | Scope Boundaries (OUT) | Complete | Explicitly excluded |

**Traceability Assessment**: All requirements covered.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Missing code rule: "Expose fields directly"**
   - Location: Phase 2b (project-conventions update)
   - Problem: deslop.md has 7 code rules; project-conventions has only 6 (missing "Expose fields directly until access control needed"). Deleting deslop.md in Phase 2e without adding this rule to project-conventions would lose it permanently.
   - Fix: Added explicit step in Phase 2b to add the missing code rule.
   - **Status**: FIXED

2. **Incomplete deslop reference sweep**
   - Location: Phase 2e (cleanup)
   - Problem: Phase 2e only removed deslop.md from CLAUDE.md @-references and deleted the file. Five additional files reference "deslop" (agent-core/README.md, memory-index SKILL.md, agents/memory-index.md, agents/decisions/operational-practices.md, agents/session.md) and would retain stale references.
   - Fix: Added file list to Phase 2e for remaining deslop reference updates.
   - **Status**: FIXED

3. **Missing terminology propagation items**
   - Location: Phase 1e (reference updates)
   - Problem: Requirements terminology table includes "vet report"→"review report", "vet-fix report"→"correction", and "vetting"→"review/correction". Phase 1e listed file-level updates but not these term-level substitutions, which would leave stale terminology in updated files.
   - Fix: Added terminology propagation bullet to Phase 1e.
   - **Status**: FIXED

### Minor Issues

1. **Agent count: "7 review/correct agents" → 6**
   - Location: Phase 1a, line 55
   - Problem: Listed 6 rename targets but claimed 7. The 7th (vet-agent) is deprecated per D-1, not renamed.
   - Fix: Changed count to 6.
   - **Status**: FIXED

2. **Skill consumer count: "7 agents" → 6**
   - Location: D-3
   - Problem: Claimed "7 agents load it via skills: frontmatter." Verified 6: design-vet-agent, outline-review-agent, plan-reviewer, refactor, runbook-outline-review-agent, vet-fix-agent.
   - Fix: Changed to 6 with explicit agent list.
   - **Status**: FIXED

3. **Scope boundary count: "12 agent renames" → 10**
   - Location: Scope Boundaries (IN)
   - Problem: With D-1 (deprecation) and D-2 (embed), actual renames are 10, not 12. The other 2 operations are a deletion and an embed.
   - Fix: Changed to "10 agent renames (5 review/correct + 5 execution)".
   - **Status**: FIXED

4. **Brittle line number reference in Phase 2d**
   - Location: Phase 2d
   - Problem: Referenced "lines 94-101" in quiet-task.md, which will shift after Phase 1 renames the file. Section name ("Code Quality") is the durable reference.
   - Fix: Changed to section name reference with content description instead of line numbers.
   - **Status**: FIXED

5. **Missing restart requirement for FR-3**
   - Location: Phase 1f
   - Problem: Requirements Dependencies section states "FR-3 (rename) requires restart after completion." Outline had no mention of this operational requirement.
   - Fix: Added restart note to Phase 1f.
   - **Status**: FIXED

6. **Phase 2a merge format unspecified**
   - Location: Phase 2a
   - Problem: "Add 5 prose rules" doesn't clarify format (with/without ❌/✅ examples) or placement (new section vs interleaved with existing rules). communication.md is ambient context — examples would bloat it.
   - Fix: Specified "rules only — strip examples" and "as new subsection".
   - **Status**: FIXED

7. **Principle line discard not explicit**
   - Location: Phase 2a
   - Problem: "Discard principle line" didn't quote the content, making it unclear which line.
   - Fix: Added the quote for identification.
   - **Status**: FIXED

## Fixes Applied

- D-3 — Changed "7 agents" to "6 agents" with explicit list
- Phase 1a — Changed "7 review/correct agents" to "6 review/correct agents"
- Scope Boundaries — Changed "All 12 agent renames" to "10 agent renames (5 review/correct + 5 execution)"
- Phase 1e — Added terminology propagation bullet (report naming, process naming)
- Phase 1f — Added session restart requirement note
- Phase 2a — Specified subsection format, stripped examples, quoted principle line
- Phase 2b — Added missing "Expose fields directly" code rule step
- Phase 2d — Replaced line number reference with section name + content description
- Phase 2e — Added 5 additional files with stale "deslop" references

## Positive Observations

- D-1 (deprecate vet-agent) is well-grounded in exploration data — the report provides thorough evidence for zero active usage
- Phase ordering rationale (D-5) is clear and correct — rename first so subsequent work uses new names
- Scope boundaries are explicit with clear IN/OUT classification
- Phase type annotations (general vs inline) match complexity — Phase 1 warrants expansion, Phases 2-3 are additive edits
- Design decisions are numbered and provide rationale, not just conclusions

## Recommendations

- Phase 1 is large (~37 files). Consider whether the runbook should split 1a-1f into sub-phases or keep as one phase with sub-steps. The general phase type allows this flexibility during expansion.
- The "deslop" term appears in 5+ non-CLAUDE.md files. Some of these may be descriptive uses (e.g., "deslop refactoring" in session notes) rather than references to the fragment. The execution agent should distinguish between fragment references (update/remove) and descriptive uses (context-dependent — may keep or update).

---

**Ready for user presentation**: Yes
