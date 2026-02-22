# Runbook Review: Phase 1 — Phase numbering fix

**Artifact**: plans/runbook-generation-fixes/runbook-phase-1.md
**Date**: 2026-02-22T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (3 cycles)

## Summary

Phase 1 implements `assemble_phase_files()` header injection across 3 TDD cycles. One critical RED/GREEN sequencing violation was found and fixed: Cycle 1.1 GREEN's behavior spec included the guard logic that belongs in Cycle 1.2, which would have caused Cycle 1.2's RED test to pass immediately (not fail). All file references are valid. Prose test quality is good — assertions are specific and behaviorally verifiable.

**Overall Assessment**: Ready (after fix applied)

## Findings

### Critical Issues

1. **RED/GREEN sequencing violation: Cycle 1.2 RED won't fail after Cycle 1.1 GREEN**
   - Location: Cycle 1.1 GREEN Phase — Behavior section
   - Problem: Cycle 1.1 GREEN specified "check if content already starts with `### Phase N:` pattern / If not present, prepend" — this guard is the behavioral addition Cycle 1.2 is supposed to introduce. After a correctly implemented Cycle 1.1 GREEN (with guard), Cycle 1.2's test `test_assembly_preserves_existing_phase_headers` would pass immediately without any new code. RED phase would not fail, violating TDD RED→GREEN discipline.
   - Fix: Cycle 1.1 GREEN behavior updated to unconditional injection (no guard). Added explicit note: "No guard yet — unconditional injection (guard added in Cycle 1.2)." Approach updated from conditional to unconditional prepend. This makes Cycle 1.2's RED correctly fail (duplicate headers produced) and Cycle 1.2 GREEN correctly adds the guard.
   - **Status**: FIXED

### Major Issues

None.

### Minor Issues

None.

## Fixes Applied

- Cycle 1.1 GREEN Behavior section — removed conditional guard ("If not present") from behavior spec, changed to unconditional injection, added explicit note that guard is deferred to Cycle 1.2
- Cycle 1.1 GREEN Approach section — updated from conditional ("If absent, prepend") to unconditional ("prepend unconditionally")

## Verification Notes

- `test_prepare_runbook_mixed.py` does not exist yet — expected for TDD phase (new file being created)
- `test_prepare_runbook_inline.py` exists with 7 tests — matches runbook's regression assertion
- `agent-core/bin/prepare-runbook.py` exists; all referenced functions verified: `assemble_phase_files()` (line 430), `extract_sections()` (line 298), `extract_cycles()` (line 103), `parse_frontmatter()` (line 63), `generate_default_orchestrator()` (line 743)
- Cycle 1.3 RED failure rationale is accurate: current code lacks phase header injection, causing incorrect `step_phases` mappings

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
