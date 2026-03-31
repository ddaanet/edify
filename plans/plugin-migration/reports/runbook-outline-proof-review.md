# Runbook Outline Review: Plugin Migration (Post-Proof)

**Artifact**: plans/plugin-migration/runbook-outline.md
**Design**: plans/plugin-migration/design.md (5 known errors; outline.md is authoritative)
**Outline**: plans/plugin-migration/outline.md (proofed, authoritative)
**Date**: 2026-03-14
**Mode**: review + fix-all

## Summary

The outline is structurally sound after /proof revisions. Phase reordering (5 after 1), scope absorption (Phase 6 now includes fragment cleanup + deny rule removal), and Phase 7 rename inclusion are well-motivated. Two design dependencies remain unresolved (D-5 redesign for Phase 4, tmux verification mechanism for Phase 1) — these are UNFIXABLE at the outline level and flagged for planner resolution. All other issues are structural/clarity fixes applied directly.

**Overall Assessment**: Ready (after fixes applied)

## Requirements Coverage

| Requirement | Phase | Steps | Coverage | Notes |
|-------------|-------|-------|----------|-------|
| FR-1 | 1, 6 | 1.1, 1.2, 1.3, 6.3 | Complete | Plugin manifest + auto-discovery validation |
| FR-2 | 4 | 4.1, 4.2 | Complete | `just claude` launch wrapper |
| FR-3 | 3 | 3.1 | Complete | `/edify:init` skill |
| FR-4 | 3 | 3.2 | Complete | `/edify:update` skill |
| FR-5 | 2, 5 | 2.3, 5.1 | Complete | Version comparison in setup hook, `.edify.yaml` schema |
| FR-6 | 4 | 4.1, 4.2 | Complete | Portable justfile recipes |
| FR-7 | 6 | 6.1, 6.2, 6.3 | Complete | Symlink removal + doc updates + validation |
| FR-8 | 1 | 1.3 | Complete | Plan-specific agent coexistence verified |
| FR-9 | 1, 2, 6 | 1.2, 2.1-2.4, 6.1, 6.3 | Complete | Hook migration + settings.json cleanup |
| FR-10 | 2 | 2.3 | Complete | Version provenance write |
| FR-11 | 2 | 2.3 | Complete | edify CLI install via uv |
| FR-12 | 5 | 5.2 | Complete | Precommit version consistency check |
| NFR-1 | 1 | 1.3 | Complete | Dev mode cycle validated at checkpoint |
| NFR-2 | 6 | 6.3 | Complete | Architectural validation (same content, different mechanism) |

**Coverage Assessment**: All requirements mapped. FR-5/FR-10 mapping for Step 5.1 corrected (was FR-6).

## Phase Structure Analysis

### Phase Balance

| Phase | Steps | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 1 | 3 | Medium | 17% | Balanced |
| 5 | 2 | Low-Medium | 12% | Small but dependency-justified |
| 2 | 4 | High | 23% | Balanced (checkpoint added at 2.4) |
| 3 | 2 | High | 12% | Balanced (opus work, prose-heavy) |
| 4 | 2 | Medium | 12% | Balanced |
| 6 | 3 | Medium | 17% | Balanced |
| 7 | inline | Low | 7% | Appropriate for mechanical work |

**Balance Assessment**: Well-balanced. No phase exceeds 25%. Phase 5 is small but must stay separate (dependency ordering).

### Complexity Distribution

- Low complexity phases: 1 (Phase 7)
- Low-Medium complexity phases: 1 (Phase 5)
- Medium complexity phases: 3 (Phases 1, 4, 6)
- High complexity phases: 2 (Phases 2, 3)

**Distribution Assessment**: Appropriate. High-complexity phases have checkpoints and manageable step counts.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Missing `posttooluse-autoformat.sh` from hook inventory**
   - Location: Step 1.2
   - Problem: Step 1.2 said "all 9 surviving hooks" but didn't enumerate them. `posttooluse-autoformat.sh` appears in outline.md Component 2 hook inventory but was not mentioned anywhere in the runbook outline.
   - Fix: Added explicit list of all 9 surviving hooks to Step 1.2 with reference to outline.md Component 2 for matchers/event types.
   - **Status**: FIXED

2. **FR-6 mapping error on Step 5.1**
   - Location: Requirements Mapping table
   - Problem: Step 5.1 (`.edify.yaml` creation) was mapped to FR-6 (portable justfile recipes). `.edify.yaml` relates to FR-5 (version comparison) and FR-10 (version provenance), not FR-6.
   - Fix: Changed mapping from FR-6 to FR-5, FR-10.
   - **Status**: FIXED

3. **Missing checkpoint at Phase 2 boundary**
   - Location: Step 2.4
   - Problem: Phase 2 is High complexity with 4 steps but had no formal checkpoint. The verify note existed but no STOP instruction. Checkpoint spacing criteria flag >8 steps without checkpoint, but High complexity phases with integration points warrant checkpoints regardless.
   - Fix: Added "Validation checkpoint" and STOP instruction to Step 2.4.
   - **Status**: FIXED

4. **D-5 redesign dependency unresolved**
   - Location: Phase 4
   - Problem: Phase 4 depends on "D-5 redesign" with "Module boundaries need design work before this phase executes." This is decision language ("decide", "determine") that must be resolved before execution.
   - Recommendation: Resolve D-5 during runbook expansion (single `portable.just` vs thematic modules). Current outline.md D-5 specifies single file.
   - **Status**: UNFIXABLE (design decision — planner must resolve)

5. **Tmux verification mechanism unresolved**
   - Location: Step 1.3
   - Problem: "Requires design: programmatic Claude CLI verification via tmux" — defers design work to execution time. Affects Steps 1.3, 2.4, 6.1, 6.3.
   - Recommendation: Design verification approach during Phase 1 expansion or as pre-phase design spike.
   - **Status**: UNFIXABLE (design decision — planner must resolve)

### Minor Issues

1. **Step misordering in Phase 6**
   - Location: Steps 6.2/6.3
   - Problem: Step 6.3 (doc updates) appeared before Step 6.2 (validation). Validation checkpoint should be last in phase for clean gating.
   - Fix: Renumbered: 6.2 = doc updates, 6.3 = validation checkpoint. Updated requirements mapping.
   - **Status**: FIXED

2. **Ambiguous justfile reference in Step 6.1**
   - Location: Step 6.1
   - Problem: "Remove `sync-to-parent` recipe from justfile" — unclear which justfile (root vs `plugin/justfile`). `sync-to-parent` lives in `plugin/justfile`.
   - Fix: Changed to "Remove `sync-to-parent` recipe from `plugin/justfile`".
   - **Status**: FIXED

3. **Missing cache regeneration in Step 4.2**
   - Location: Step 4.2
   - Problem: Design.md lists `.cache/just-help.txt` and `.cache/just-help-edify-plugin.txt` as modified files. Step 4.2 didn't mention cache regeneration.
   - Fix: Added cache regeneration instruction and files list.
   - **Status**: FIXED

4. **Missing post-phase state note on Step 2.4**
   - Location: Step 2.4
   - Problem: Step references hooks.json from Phase 1 without noting expected state. Post-phase state awareness criteria require explicit state notes when modifying files changed in prior phases.
   - Fix: Added post-phase state note referencing Step 1.2's hooks.json rewrite.
   - **Status**: FIXED

5. **Missing files and dependency on Step 6.2 (doc updates)**
   - Location: Step 6.2
   - Problem: Step had no Files or Depends-on declarations.
   - Fix: Added Files list and dependency on Step 6.1.
   - **Status**: FIXED

6. **Missing dependency on Step 6.3 (validation)**
   - Location: Step 6.3
   - Problem: Validation checkpoint had no explicit dependency declaration.
   - Fix: Added "Depends on: Steps 6.1, 6.2" and "Validation checkpoint" language.
   - **Status**: FIXED

7. **Phase 6 dependency incomplete**
   - Location: Phase Dependencies section
   - Problem: Phase 6 listed dependencies on Phases 1, 2, 5 but Phases 3 and 4 should also complete first for clean validation (new skills should be discoverable, justfile imports should work).
   - Fix: Added note that Phases 3, 4 are not strict dependencies but should complete first.
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping: Step 5.1 FR-6 → FR-5, FR-10
- Requirements Mapping: Step 6.2 added (fragments), Step 6.3 renumbered (validation)
- Step 1.2: Added explicit list of all 9 surviving hooks
- Step 2.4: Added post-phase state note and validation checkpoint
- Step 4.2: Added cache regeneration instruction
- Step 6.1: Clarified `plugin/justfile` for sync-to-parent removal
- Step 6.2: Renumbered from 6.3, added Files and Depends-on
- Step 6.3: Renumbered from 6.2, added Depends-on and checkpoint language
- Phase Dependencies: Added Phase 3/4 note to Phase 6 dependencies
- Expansion Guidance: Updated checkpoint references, added hook inventory note, added consolidation candidates, added unresolved design dependencies

## Design Alignment

- **Architecture**: Aligned. Outline follows bootstrap strategy (build inside `plugin/`, rename last)
- **Module structure**: Aligned. Plugin manifest, hooks.json, skills all in correct locations per outline.md
- **Key decisions**: D-1 through D-7 correctly referenced. D-4 wrapper format matches proofed outline (corrects design.md). D-5 single-vs-modular tension flagged as UNFIXABLE
- **Design.md vs outline.md**: Outline correctly treats outline.md as authoritative. Design.md deliverables for `.version` file and `userpromptsubmit-version-check.py` are superseded (version in `plugin.json`, check in `edify-setup.sh`)

## Growth Projection

| File | Current Lines | Phase | Projected Lines | Assessment |
|------|--------------|-------|----------------|------------|
| `plugin/hooks/hooks.json` | 57 | 1, 2 | ~100 (rewrite with 9 hooks + setup hook) | No concern |
| `justfile` | 638 | 4 | ~500 (recipes removed, import added) | Net reduction |
| `plugin/justfile` | 108 | 6 | ~100 (sync-to-parent removed) | No concern |
| New: `edify-setup.sh` | 0 | 2 | ~60-80 | No concern |
| New: `plugin.json` | 0 | 1 | ~5 | No concern |
| New: `.edify.yaml` | 0 | 5 | ~5 | No concern |
| New: `init/SKILL.md` | 0 | 3 | ~60-100 | No concern |
| New: `update/SKILL.md` | 0 | 3 | ~30-50 | No concern |

No files approach the 350-line threshold. No split recommendations needed.

## Positive Observations

- Phase reordering (5 after 1) correctly establishes `.edify.yaml` before Phase 2's setup hook
- Step 1.2 explicitly omits `pretooluse-symlink-redirect.sh` — clean separation of deletion (Phase 2) from migration (Phase 1)
- Phase 7 inline designation is appropriate — mechanical replacement, all decisions pre-resolved
- Requirements mapping uses step-indexed format (from /proof verdict 1) — easier to trace during expansion
- Expansion guidance section is comprehensive and actionable
- Bootstrap constraint is well-documented with recall entry references

## Recommendations

- Resolve D-5 (thematic modules vs single `portable.just`) before Phase 4 expansion. Current outline.md specifies single file — use that as default if no redesign occurs
- Design tmux verification mechanism as a pre-Phase-1 spike or during Phase 1 expansion. The mechanism is reused in Phases 2 and 6
- Consider whether Phase 4 should depend on Phase 5 (`.edify.yaml` exists for `portable.just` sync policy). Currently independent — may be correct if sync is Phase 2/3 concern only

---

**Ready for full expansion**: Yes (2 UNFIXABLE items are design dependencies flagged in expansion guidance — planner resolves during expansion)
