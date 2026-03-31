# Runbook Review: Plugin Migration Phases (Post-/proof)

**Artifact**: `plans/plugin-migration/runbook-phase-{1,2,3,4,5,6}.md`
**Date**: 2026-03-14T00:00:00Z
**Mode**: review + fix-all
**Phase types**: All general (6 phases)
**Scope**: Post-/proof consistency review — verifying /proof verdicts applied correctly and consistently

---

## Summary

Reviewed all 6 phase files for consistency with the /proof verdict list. Four issues found across phases 2, 3, 5, and 6 — all fixable inline. Primary failure mode: stale references to the pre-/proof design (`edify-setup.sh` as a separate hook, hook count of 10, "conversational design" in expected outcome). One requirements coverage gap in Phase 6.2 (missing `delegation.md` check from outline spec) corrected with verification note.

**Overall Assessment**: Ready (all issues fixed)

---

## Findings

### Critical Issues

1. **Phase 6.1 prerequisites: wrong hook count**
   - Location: `runbook-phase-6.md`, Step 6.1 Prerequisites
   - Problem: "contains all 10 hooks (9 surviving + setup hook)" — the /proof verdict merged setup into `sessionstart-health.sh` rather than creating a separate `edify-setup.sh`. No new hook was added; hook count remains 9.
   - Fix: Changed to "contains all 9 surviving hooks (setup integrated into `sessionstart-health.sh`, no new hook added)"
   - **Status**: FIXED

2. **Phase 6.1 error condition contradicts /proof verdict on `handoff-cli-tool-*.md`**
   - Location: `runbook-phase-6.md`, Step 6.1 Error Conditions
   - Problem: Error condition said "If `handoff-cli-tool-*.md` files are accidentally symlinks → do not delete, escalate" — directly contradicting the /proof verdict ("remove `handoff-cli-tool-*.md` files unconditionally") and the implementation step which deletes them with `rm -f`.
   - Fix: Changed to "If `handoff-cli-tool-*.md` files cannot be deleted (permission error, unexpected file type) → investigate before proceeding"
   - **Status**: FIXED

### Major Issues

3. **Phase 3.1 duplicate implementation bullet (orphan from pre-/proof text)**
   - Location: `runbook-phase-3.md`, Step 3.1 Implementation, item 1
   - Problem: After the /proof edit added the CLAUDE.md conditional (exists → rewrite refs; not exists → generate from template), the standalone line "Generate CLAUDE.md from `plugin/templates/CLAUDE.template.md`" remained as an orphan bullet. This line now appears twice — once as the else-branch of the conditional (correct) and once as a standalone unconditional action (wrong, would override the conditional logic).
   - Fix: Removed the duplicate standalone line at line 29 (original)
   - **Status**: FIXED

4. **Phase 3.1 expected outcome: stale "conversational design" description**
   - Location: `runbook-phase-3.md`, Step 3.1 Expected Outcome
   - Problem: Expected Outcome said "skill frontmatter and conversational design" — the /proof verdict changed the skill from conversational to concrete action-oriented (with explicit conditional logic for CLAUDE.md). The expected outcome was not updated to reflect this change.
   - Fix: Changed to "skill frontmatter and concrete action-oriented behavior (CLAUDE.md conditional, fragment copy, scaffold, `.edify.yaml` write)"
   - **Status**: FIXED

5. **Phase 5.1 `.edify.yaml` comment references deleted `edify-setup.sh`**
   - Location: `runbook-phase-5.md`, Step 5.1 Implementation (YAML content block)
   - Problem: The comment `# Written by /edify:init, updated by edify-setup.sh on session start` will be written literally into the `.edify.yaml` file. After /proof, setup runs inside `sessionstart-health.sh`, not a separate `edify-setup.sh`.
   - Fix: Changed comment to `# Written by /edify:init, updated by sessionstart-health.sh on session start`
   - **Status**: FIXED

### Minor Issues

6. **Phase 2 step numbering gap without explanation**
   - Location: `runbook-phase-2.md`, phase header
   - Problem: Steps jump from 2.1 to 2.3 with no indication of why. Executors will wonder if a file is missing. The gaps are intentional (2.2 absorbed into 2.1, 2.4 absorbed into 2.3) per the /proof verdicts but the rationale is invisible.
   - Fix: Added step numbering note to phase header explaining absorbed steps and preserving outline traceability via original step IDs
   - **Status**: FIXED

7. **Phase 6.2 missing `delegation.md` check from outline specification**
   - Location: `runbook-phase-6.md`, Step 6.2 Prerequisites and Implementation
   - Problem: The outline (line 230) specified `fragments/delegation.md` as a 4th fragment to check/update for `sync-to-parent` references. The phase file only listed 3 fragments in prerequisites and implementation. Verified: `delegation.md` currently has no `sync-to-parent` references, so no edit is needed — but the executor should confirm this rather than assume.
   - Fix: Added `delegation.md` to prerequisites read list with note "currently clean, confirm before skipping"; added item 4 in implementation: check and skip if no references found
   - **Status**: FIXED

---

## Fixes Applied

- `runbook-phase-6.md` Step 6.1 Prerequisites — hook count corrected from 10 to 9 with rationale
- `runbook-phase-6.md` Step 6.1 Error Conditions — removed contradictory "do not delete" guard for `handoff-cli-tool-*.md`
- `runbook-phase-3.md` Step 3.1 Implementation — removed orphan duplicate "Generate CLAUDE.md from template" bullet
- `runbook-phase-3.md` Step 3.1 Expected Outcome — updated from "conversational design" to concrete action description
- `runbook-phase-5.md` Step 5.1 Implementation — `.edify.yaml` comment updated from `edify-setup.sh` to `sessionstart-health.sh`
- `runbook-phase-2.md` Phase header — added step numbering note explaining absorbed steps 2.2 and 2.4
- `runbook-phase-6.md` Step 6.2 Prerequisites + Implementation — added `delegation.md` with verify-and-skip instruction

---

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
