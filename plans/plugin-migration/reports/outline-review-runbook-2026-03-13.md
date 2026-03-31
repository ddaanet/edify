# Runbook Outline Review: plugin-migration

**Artifact**: plans/plugin-migration/runbook-outline.md
**Design**: plans/plugin-migration/outline.md (proofed, authoritative — supersedes design.md)
**Date**: 2026-03-13
**Mode**: review + fix-all

## Summary

Well-structured 7-phase outline with clear phase typing, dependency graph, and complexity assessment. All 14 requirements (FR-1 through FR-12, NFR-1, NFR-2) are mapped. Three issues fixed: Phase 4 step ordering was inverted (created recipes before creating the file they live in), `wt-*` recipe exclusion contradicted the authoritative outline's D-5 decision, and FR-8 mapping was passive rather than active. Phase 7 correctly uses inline type.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps | Coverage | Notes |
|-------------|-------|-------|----------|-------|
| FR-1 (plugin auto-discovery) | 1 | 1.1, 1.2 | Complete | --- |
| FR-2 (just claude launcher) | 4 | 4.1, 4.2 | Complete | Fixed: was 4.1 only, now covers both creation and verification |
| FR-3 (/edify:init scaffolding) | 3 | 3.1 | Complete | --- |
| FR-4 (/edify:update sync) | 3 | 3.2 | Complete | --- |
| FR-5 (stale version nag) | 2 | 2.3 | Complete | --- |
| FR-6 (portable justfile) | 4 | 4.1, 4.2 | Complete | Fixed: was 4.2 only |
| FR-7 (symlink removal migration) | 6 | 6.1 | Complete | --- |
| FR-8 (plan-specific agent coexistence) | 1 | 1.3 | Complete | Fixed: was passive "verified during" → active validation step |
| FR-9 (hooks migrate to plugin) | 2 | 2.1, 2.2 | Complete | --- |
| FR-10 (version provenance) | 2 | 2.3 | Complete | --- |
| FR-11 (edify CLI install) | 2 | 2.3 | Complete | --- |
| FR-12 (version consistency check) | 5 | 5.2 | Complete | --- |
| NFR-1 (dev mode cycle time) | 1 | 1.3 | Complete | Manual validation checkpoint |
| NFR-2 (no token overhead) | 6 | 6.2 | Complete | Context size comparison |

**Coverage Assessment**: All requirements covered. No gaps.

## Phase Structure Analysis

### Phase Balance

| Phase | Steps | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 1: Plugin manifest | 3 | Medium | 19% | Balanced |
| 2: Hook migration | 4 | High | 25% | Largest phase, justified by audit + new script |
| 3: Migration skills | 2 | High | 13% | Balanced (opus model compensates) |
| 4: Justfile modularization | 2 | Medium | 13% | Balanced |
| 5: Version coordination | 2 | Low-Medium | 13% | Balanced |
| 6: Symlink cleanup | 2 | Medium | 13% | Balanced |
| 7: Docs and paths | inline | Low | 6% | Inline — appropriate |

**Balance Assessment**: Well-balanced. No phase exceeds 25%. Phase 2 is largest but complexity justifies the step count.

### Complexity Distribution

- **Low complexity phases**: 1 (Phase 7 inline)
- **Low-Medium complexity phases**: 1 (Phase 5)
- **Medium complexity phases**: 3 (Phases 1, 4, 6)
- **High complexity phases**: 2 (Phases 2, 3)

**Distribution Assessment**: Appropriate. High-complexity phases have correspondingly more steps or opus model assignment.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Phase 4 step ordering inverted**
   - Location: Phase 4, Steps 4.1 and 4.2
   - Problem: Original Step 4.1 added recipes "to portable justfile" but Step 4.2 created `portable.just`. The file must exist before recipes can be added.
   - Fix: Restructured Phase 4. Step 4.1 now creates `portable.just` with full recipe stack. Step 4.2 updates root justfile to import it. Step 4.2 declares dependency on 4.1.
   - **Status**: FIXED

2. **D-5 wt-* recipe exclusion contradicts authoritative outline**
   - Location: Phase 4, Step 4.2 (original)
   - Problem: Runbook-outline said "Do NOT include `wt-*` recipes (manual fallbacks, stay in project justfile)". Outline D-5 explicitly lists `wt-*` in the portable.just recipe stack. The authoritative outline governs.
   - Fix: Added `wt-*` to portable.just recipe list in Step 4.1. Removed exclusion note.
   - **Status**: FIXED

3. **FR-8 mapping was passive, not active**
   - Location: Requirements Mapping table
   - Problem: FR-8 mapped to "1.2 (verified during plugin validation)" — passive observation during hooks.json creation, not an active coexistence test.
   - Fix: Remapped FR-8 to Step 1.3 with explicit coexistence validation (plan-specific agents + plugin agents both discoverable). Added FR-8 detail to Step 1.3 body.
   - **Status**: FIXED

### Minor Issues

1. **FR-2 and FR-6 mapping incomplete after Phase 4 restructure**
   - Location: Requirements Mapping table
   - Problem: FR-2 mapped only to 4.1, FR-6 only to 4.2. After restructure, both requirements span both steps.
   - Fix: Updated FR-2 → 4.1, 4.2 and FR-6 → 4.1, 4.2.
   - **Status**: FIXED

2. **Phase 6 Step 6.1 missing post-phase state awareness**
   - Location: Phase 6, Step 6.1
   - Problem: Step 6.1 modifies files created/changed in Phases 1 and 2 but didn't note expected state. Expanding agent needs to know what state these files are in post-Phase-2.
   - Fix: Added post-phase state note listing hooks.json contents, plugin.json existence, and edify-setup.sh wiring.
   - **Status**: FIXED

3. **Phase 6 Step 6.1 missing explicit dependency declaration**
   - Location: Phase 6, Step 6.1
   - Problem: Phase Dependencies section documents Phase 6 depends on Phases 1, 2 but Step 6.1 itself lacked a `Depends on:` declaration.
   - Fix: Added `Depends on: Phases 1, 2 (plugin fully verified)`.
   - **Status**: FIXED

4. **Phase 7 missing explicit dependency declaration**
   - Location: Phase 7 header
   - Problem: Phase Dependencies section shows Phase 7 depends on Phase 6, but Phase 7 body didn't state this.
   - Fix: Added `Depends on: Phase 6 (symlinks removed, sync-to-parent deleted)` to Phase 7 header area.
   - **Status**: FIXED

5. **Expansion Guidance lacked checkpoint spacing and consolidation recommendations**
   - Location: Expansion Guidance section
   - Problem: Original guidance was a flat list of per-phase notes. Missing checkpoint recommendations, consolidation analysis, and recall entry references.
   - Fix: Restructured into categorized sections: phase-specific guidance, checkpoint guidance, consolidation candidates, bootstrap constraint. Added recall entry references for SessionStart discard and hook path resolution.
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping: FR-2 → 4.1, 4.2 (was 4.1); FR-6 → 4.1, 4.2 (was 4.2); FR-8 → 1.3 (was 1.2)
- Step 1.3: Added explicit FR-8 coexistence validation detail
- Phase 4: Restructured — 4.1 creates portable.just (full D-5 stack including wt-*), 4.2 updates root justfile with import. Added dependency declaration.
- Step 6.1: Added post-phase state note and explicit dependency declaration
- Phase 7: Added explicit dependency on Phase 6
- Expansion Guidance: Restructured into categorized sections with checkpoint guidance, consolidation analysis, and recall references

## Design Alignment

- **Architecture**: Aligned. Bootstrap strategy (build inside plugin/, rename last) correctly reflected throughout.
- **Module structure**: Aligned. All target files use `plugin/` paths per bootstrap constraint.
- **Key decisions**: All 7 decisions (D-1 through D-7) referenced in outline and correctly applied. D-4 wrapper format corrected (outline corrects design.md). D-5 recipe list now matches outline.
- **Design corrections**: Runbook-outline correctly works from proofed outline.md, not stale design.md. Five design.md errors documented in outline's Design Corrections section are properly avoided.

## Positive Observations

- Phase typing is correct: general for implementation phases, inline for Phase 7 (mechanical prose/config with all decisions pre-resolved)
- Dependency graph enables parallelism: Phases 2, 3, 4, 5 can run concurrently after Phase 1
- Bootstrap constraint is properly enforced: symlink cleanup (Phase 6) is gated behind plugin verification
- Recall artifact referenced in header — downstream consumers can resolve entries
- Hook inventory uses audited data from outline Component 2, not stale design.md counts
- Step 2.3 correctly references SessionStart discard issue (#10373) and UPS fallback

## Recommendations

- Phase 2 Step 2.3 (edify-setup.sh) is the most complex individual step — consider splitting into sub-steps during expansion (env var export, venv install, version comparison as separate concerns)
- Phase 3 opus model assignment is appropriate — agentic prose skills require careful reasoning about conditional logic and idempotency
- `portable.just` needs its own bash prolog per outline §Component 5 import boundary constraints — expansion should detail the minimal prolog contents

---

**Ready for full expansion**: Yes
