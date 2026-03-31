# Outline Review: Plugin Migration (PDR)

**Artifact**: plans/plugin-migration/outline.md
**Date**: 2026-03-12
**Mode**: review + fix-all
**Design reference**: plans/plugin-migration/design.md (authoritative)
**Recall artifact**: plans/plugin-migration/recall-artifact.md (5 entries, 4 resolved)

## Summary

The refreshed outline is well-structured, technically sound, and corrects several material errors in design.md (hooks.json format, hook inventory completeness, artifact counts). Requirements traceability is complete — all FR-* and NFR-* map to components with validation criteria. The outline explicitly identifies design corrections with rationale, which strengthens confidence.

Three fixes applied: generated agent count corrected (5 to 6), explicit Risks section added (PDR criteria gap), and open question linked to FR-9.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | Component 1 (Plugin Manifest) | Complete | Auto-discovery replaces symlinks |
| FR-2 | Component 5 (Justfile) | Complete | `just claude` with `--plugin-dir` |
| FR-3 | Component 4 (Migration Command) | Complete | `/edify:init` with idempotency |
| FR-4 | Component 4 (Migration Command) | Complete | `/edify:update` separate skill |
| FR-5 | Component 7 (Version Check) | Complete | UserPromptSubmit hook, once-per-session |
| FR-6 | Component 5 (Justfile) | Complete | `portable.just` with import |
| FR-7 | Component 6 (Symlink Cleanup) | Complete | Remove symlinks, no other structural changes |
| FR-8 | Component 1 (Plugin Manifest) | Complete | Namespace separation: `edify:` prefix vs `.claude/agents/` |
| FR-9 | Component 2 (Hook Migration) | Complete | Full hook inventory with migration actions |
| NFR-1 | Approach section | Complete | `--plugin-dir` provides live loading |
| NFR-2 | Validation table | Complete | Post-migration comparison specified |

**Traceability Assessment**: All requirements covered with explicit validation criteria.

## Scope-to-Component Traceability

| Scope IN Item | Component | Notes |
|---------------|-----------|-------|
| Directory rename | Implementation Order step 1 | Foundation for all other components |
| Plugin manifest and structure | C1 | Direct match |
| Hook migration to plugin hooks.json | C2 | Full inventory with 10 hooks |
| Fragment version sync mechanism | C3 | Version marker + comparison logic |
| Migration commands | C4 | `/edify:init` + `/edify:update` |
| Justfile modularization | C5 | `portable.just` with import |
| Symlink removal and settings.json cleanup | C6 | Last in execution order |
| Script path and permissions updates | C8 | Covers settings.json permissions, sandbox config |
| Documentation updates | C9 | Fragment updates enumerated |

**Scope Assessment**: All items assigned to components. No orphans.

## Cross-Component Interface Compatibility

| Producer | Consumer | Interface | Compatible |
|----------|----------|-----------|------------|
| C1 (manifest) | C2 (hooks) | Plugin directory structure | Yes — hooks.json at `hooks/hooks.json` |
| C3 (versioning) | C7 (version check) | `.version` / `.edify-version` files | Yes — both read same files |
| C3 (versioning) | C4 (init/update) | `.edify-version` marker | Yes — init writes, update overwrites |
| C1 (manifest) | C5 (justfile) | `--plugin-dir ./edify-plugin` | Yes — path consistent |
| C2 (hooks) | C6 (cleanup) | hooks.json replaces settings.json hooks | Yes — cleanup removes settings.json hooks after C2 verified |

No interface mismatches detected.

## Design.md Consistency Check

The outline explicitly corrects three design.md errors (Design Corrections section):

1. **D-4 hooks.json format**: Design says direct format; outline says wrapper format per official docs. The existing `plugin/hooks/hooks.json` uses direct format (current settings.json format), but plugin hooks.json may require wrapper format. Outline cites official plugin docs as authority. **Verdict**: Outline correction is reasonable; will be validated empirically during implementation (R-1 risk covers this).

2. **Hook inventory**: Design lists 4 hooks; outline lists 10 (all audited). **Verdict**: Outline is correct per filesystem audit.

3. **Artifact counts**: Design says 16 skills, 12 agents; audit shows 33 skills, 13 agents. **Verdict**: Outline is correct per filesystem audit.

**Additional inconsistency found and fixed**: Design.md Component 6 says "16 symlinks" (skills) and "12 symlinks" (agents). Outline correctly uses 33 and 13. The outline's generated agent count was wrong (5 vs actual 6) — fixed.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Generated agent count incorrect**
   - Location: Line 10 (current state) and line 239 (Component 6)
   - Problem: Outline says "5 generated plan-specific agents" and "preserve 5+ `*-task.md`". Filesystem shows 6: handoff-cli-tool-{corrector, impl-corrector, implementer, task, test-corrector, tester}
   - Fix: Updated to "6 generated plan-specific agents" with enumeration; Component 6 updated to "preserve 6 `handoff-cli-tool-*.md` regular files"
   - **Status**: FIXED

2. **Missing Risks section (PDR criteria gap)**
   - Location: Between Rollback Strategy and Open Questions
   - Problem: PDR criteria require "Risks and open questions identified." Open questions existed but risks were implicit (scattered in rollback strategy, component notes). No consolidated risk enumeration.
   - Fix: Added explicit Risks section with 4 identified risks (R-1 through R-4), each with mitigation strategy
   - **Status**: FIXED

### Minor Issues

1. **Open question not linked to requirement**
   - Location: Open Questions section, first item
   - Problem: Hook env var audit question relates to FR-9 implementation risk but didn't reference it
   - Fix: Added "(FR-9)" to the hook script env var audit question
   - **Status**: FIXED

## Fixes Applied

- Line 10 — Generated agent count: "5 generated" to "6 generated" with full enumeration
- Line 239 (Component 6) — "preserve 5+ `*-task.md`" to "preserve 6 `handoff-cli-tool-*.md`"
- After Rollback Strategy — Added Risks section (R-1 through R-4) with mitigations
- Open Questions first bullet — Added "(FR-9)" requirement link

## Positive Observations

- Design Corrections section is excellent practice — explicitly documenting where the outline diverges from the authoritative design.md with rationale
- Hook inventory is thorough: every hook has event type, matcher, current location, and migration action
- Implementation order is dependency-aware with parallelism opportunities identified
- Rollback strategy is practical — symlink cleanup as point-of-no-return with `sync-to-parent` as escape hatch
- Validation table maps each FR to a concrete test method
- Scope boundaries are explicit with clear IN/OUT enumeration
- The `$CLAUDE_PROJECT_DIR` vs `$CLAUDE_PLUGIN_ROOT` distinction is well-articulated (Component 2 hook script changes table)

## Recommendations

- R-1 (hooks.json format) should be resolved early in implementation — a quick `claude --plugin-dir` test with a minimal hooks.json would confirm wrapper vs direct format before building the full configuration
- The 4 hooks needing env var audit (R-2) could be audited as a pre-implementation spike to reduce risk during Component 2 execution
- Consider whether the Design Corrections section should trigger a design.md erratum or amendment, so the authoritative design doesn't contain known-wrong information

---

**Ready for user presentation**: Yes
