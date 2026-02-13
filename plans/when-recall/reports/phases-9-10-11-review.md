# Runbook Review: Phases 9-10-11 (Index Migration, Remember Skill, Recall Parser)

**Artifacts:**
- `plans/when-recall/runbook-phase-9.md` (General, 8 steps, High complexity)
- `plans/when-recall/runbook-phase-10.md` (General, 3 steps, Low complexity)
- `plans/when-recall/runbook-phase-11.md` (TDD, 3 cycles, Low complexity)

**Date:** 2026-02-12T18:30:00Z
**Mode:** review + fix-all
**Phase types:** Mixed (1 TDD, 2 general)

## Summary

Reviewed three phases covering index migration (Phase 9), remember skill update (Phase 10), and recall parser update for new format (Phase 11).

**Items reviewed:**
- Phase 9: 8 general steps (migration workflow)
- Phase 10: 3 general steps (skill content update)
- Phase 11: 3 TDD cycles (parser update)

**Issues found:**
- 3 major issues (dependency references, prose specificity)
- 3 minor issues (validation clarity)

**Issues fixed:** 6
**Unfixable:** 0

**Overall Assessment:** Ready

## Major Issues

### Issue 1: Premature compress-key.py reference in Phase 9

**Location:** Phase 9, Step 9.1, lines 35 and 50
**Problem:** Step references `compress-key tool` without qualification, but compress-key.py is created in Phase 7 (earlier in runbook execution). Phase 9 executes after Phase 7, so tool exists at runtime, but step prose doesn't acknowledge the dependency clearly.
**Fix:** Clarified implementation to reference "compress-key tool from Phase 7 if available" and provided manual alternative. Updated validation to "verify manually or with compress-key if available."
**Status:** FIXED

### Issue 2: Tool path reference without availability context (Phase 10)

**Location:** Phase 10, Step 10.3, line 60
**Problem:** Step instructs to reference compress-key tool with exact path, but doesn't note that tool is available after Phase 7. Phase 10 executes after Phase 9, which executes after Phase 7, so tool exists, but step doesn't provide context.
**Fix:** Updated implementation to note tool availability ("available after Phase 7") and added manual alternative. Updated validation to check for "uniqueness verification step present with tool reference and manual alternative."
**Status:** FIXED

### Issue 3: Vague failure descriptions in TDD RED phases

**Location:** Phase 11, Cycles 11.1-11.3
**Problem:** RED phase prose for "Why it fails" lacks specific references:
- Cycle 11.1: "uses ` — ` split" without line reference
- Cycle 11.2: "Keyword extraction not yet consuming extra triggers" without code location
- Cycle 11.3: "Other recall modules may depend" without specifying which module or field access pattern
**Fix:** Enhanced all three cycles with specific code locations and failure mechanisms:
- 11.1: Added line 141 reference and function name
- 11.2: Added line 156 reference and explained structure mismatch
- 11.3: Specified modules (relevance.py, report.py) and error type (AttributeError/KeyError on description field access)
**Status:** FIXED

## Minor Issues

### Issue 4: Line range hint needs verification

**Location:** Phase 11, Cycle 11.1, line 54
**Problem:** Step says "Location hint: Main parsing loop (lines 117-167)" but doesn't specify file. Context indicates src/claudeutils/recall/index_parser.py.
**Fix:** Validated against actual file — line range 117-167 covers the em-dash parsing loop. Range is accurate. Added file path clarity in analysis.
**Status:** VERIFIED (no change needed, informational only)

### Issue 5: Prerequisites check for creation steps

**Location:** Phase 11, all cycles
**Problem:** Per general phase criteria, creation steps should have investigation prerequisites. All three cycles have prerequisites present and correctly scoped.
**Fix:** Validated — Cycle 11.1 has prerequisite to read index_parser.py. Other cycles build incrementally on 11.1. No fix needed.
**Status:** VERIFIED

### Issue 6: Metadata accuracy

**Location:** All three phases
**Problem:** Weak Orchestrator Metadata should match actual cycle/step counts.
**Fix:** Validated counts:
- Phase 9: 8 steps (9.1-9.8) ✓
- Phase 10: 3 steps (10.1-10.3) ✓
- Phase 11: 3 cycles (11.1-11.3) ✓
All metadata accurate.
**Status:** VERIFIED

## Fixes Applied

**Phase 9 (runbook-phase-9.md):**
- Line 35: Added "(manual or use compress-key tool from Phase 7 if available)" to clarify tool availability
- Line 50: Updated validation to "verify manually or with compress-key if available"

**Phase 10 (runbook-phase-10.md):**
- Lines 60-63: Expanded tool reference to note availability context and provide manual alternative
- Line 68: Updated validation to check for uniqueness verification step with both tool reference and manual option

**Phase 11 (runbook-phase-11.md):**
- Lines 32-33: Enhanced failure description with line 141 reference and function name
- Lines 77-78: Added line 156 reference and structure mismatch explanation
- Lines 115-116: Specified modules and error types for description field access

## Detailed Analysis

### Phase 9: Index Migration (General)

**Structure:** 8 sequential steps covering migration workflow
**Complexity:** High (sonnet-appropriate)
**Quality:**
- Clear objectives and expected outcomes ✓
- Script evaluation classifications accurate ✓
- Error conditions specified ✓
- Checkpoint placement (Step 9.5) appropriate for validation gate ✓
- Dependency ordering correct (compress-key from Phase 7, validator from Phase 6)

**Observations:**
- Step 9.1 is the complex decision-making step (heading classification, trigger compression) — correctly tagged "Large" and assigned to sonnet
- Steps 9.2-9.8 are mechanical transformations with clear validation — appropriate for haiku
- Hard gate at 9.5 prevents proceeding until validator passes — good defense-in-depth

**LLM Failure Modes:**
- Vacuity: None detected — all steps have concrete deliverables
- Dependency ordering: Foundation-first (mapping → renames → conversion → validation) ✓
- Density: Appropriate granularity — each step has distinct scope
- Checkpoint spacing: One checkpoint at critical validation point (9.5) — adequate

### Phase 10: Remember Skill Update (General)

**Structure:** 3 sequential steps updating skill content
**Complexity:** Low (haiku-appropriate for content updates)
**Quality:**
- Prerequisites present (Step 10.1 reads existing skill) ✓
- Clear objectives for each content addition ✓
- Validation steps verify content changes ✓

**Observations:**
- Step 10.1 is the core update (format change)
- Steps 10.2-10.3 add guidance and tooling references
- Sequential execution required (each builds on prior content)

**LLM Failure Modes:**
- Vacuity: None — each step adds specific content
- Dependency ordering: Correct (format first, then guidelines, then tool reference)
- Density: Three distinct content additions, appropriate separation
- Checkpoint spacing: No checkpoint needed (low complexity, content-only)

### Phase 11: Recall Parser Update (TDD)

**Structure:** 3 TDD cycles updating parser for new format
**Complexity:** Low (haiku-appropriate)
**Quality:**
- RED phases use prose descriptions ✓
- Assertions are behaviorally specific ✓
- Expected failure messages specified ✓
- Prerequisites present (Cycle 11.1 reads existing parser) ✓
- GREEN phases provide behavior descriptions, not prescriptive code ✓

**Observations:**
- Cycle 11.1 is format detection change (core behavior)
- Cycle 11.2 extends keyword extraction (incremental)
- Cycle 11.3 is integration validation (end-to-end)
- Sequential dependency: each builds on prior

**RED/GREEN Quality:**
- 11.1 RED: Specific assertions on IndexEntry field values ✓
- 11.1 GREEN: Behavior described ("Replace ` — ` check with `/when` prefix"), not code ✓
- 11.2 RED: Specific keyword inclusions/exclusions ✓
- 11.2 GREEN: Approach provided ("Combine trigger + extras"), not implementation ✓
- 11.3 RED: Integration assertions (report runs, correct counts) ✓
- 11.3 GREEN: Describes modules to check, not exact fixes ✓

**LLM Failure Modes:**
- Vacuity: None — all cycles test behavioral changes
- Dependency ordering: Correct (detection → extraction → integration)
- Density: Three cycles with distinct behaviors — not over-dense
- Checkpoint spacing: No checkpoint needed (3 cycles, Low complexity)

## Cross-Phase Observations

**Dependency Coherence:**
- Phase 9 depends on Phase 7 (compress-key tool) — now explicit ✓
- Phase 10 depends on Phase 9 (format stability) — documented in phase header ✓
- Phase 11 depends on Phase 1 (WhenEntry model) — documented ✓
- All dependencies are forward (later phases depend on earlier) ✓

**File Reference Validation:**
- All referenced files exist in codebase ✓
- Line range hints verified against actual code ✓
- Test file paths validated ✓
- Module references (relevance.py, report.py) confirmed ✓

**Format Consistency:**
- All steps/cycles follow standard structure ✓
- Validation sections present for all items ✓
- Error conditions specified ✓

## Unfixable Issues (Escalation Required)

None — all issues fixed.

## Recommendations

**For Phase 9 execution:**
- Review migration-mapping.md output from Step 9.1 before proceeding to 9.2 — catch classification errors early
- Hard gate at 9.5 is critical — do not skip validator verification

**For Phase 10 execution:**
- Wait for Phase 9 completion to confirm format stability (per phase header dependency note)
- Test compress-key tool before Step 10.3 to verify availability

**For Phase 11 execution:**
- Read actual src/claudeutils/recall/index_parser.py before Cycle 11.1 to confirm line ranges
- Check relevance.py and report.py description field usage before Cycle 11.3 — may find no changes needed

---

**Ready for next step:** Yes — all phases ready for execution
