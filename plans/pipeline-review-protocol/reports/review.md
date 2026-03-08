# Review: Pipeline Review Protocol Implementation

**Scope**: Changed files since baseline 2ad4760b — /proof skill, /design, /requirements, /runbook integrations, discussion-protocol.md deletion
**Date**: 2026-03-08
**Mode**: review + fix

## Summary

The implementation delivers all 5 design components: /proof skill (C1), 5 integration points (C2), author-corrector coupling in /design (C3), automatic corrector dispatch in proof (C4), and discussion-protocol.md deletion. The skill is well-structured and follows project conventions. Two issues: the outline specifies "Post-C.3" placement for the /design integration point but the implementation places it at C.4.5 (after C.4's UNFIXABLE handling), and the /proof skill's Integration Points table shows "Post-C.4" where the outline specifies "Post-C.3". The C.4.5 placement is actually better than "Post-C.3" because it runs after UNFIXABLE issues are addressed — a substantive improvement that should be reflected consistently.

**Overall Assessment**: Ready (post-fix)

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Integration Points table label mismatch: "Post-C.4" vs actual location**
   - Location: `.claude/skills/proof/SKILL.md:132` (Integration Points table)
   - Problem: The table shows `/design | Post-C.4 (Post-design review)` but outline.md specifies "Post-C.3 (Post-design)". The actual implementation in write-design.md places it at C.4.5 (after C.4). The label should match the actual implementation stage label — C.4.5 is the correct anchor, not "Post-C.4".
   - Fix: Update the Integration Points table row to use "Phase C.4.5" to match the write-design.md section header.
   - **Status**: FIXED

2. **Proof skill references `discussion-protocol.md` content in a way that could mislead**
   - Location: `.claude/skills/proof/SKILL.md:17`
   - Problem: The skill says "The previous 21-line `discussion-protocol.md` reference file failed to enforce." The reference to a deleted file by name in a live skill is informational but could confuse implementers who search for the file. The note is appropriate as historical context — this is acceptable. On reflection this is minor, not major.
   - **Status**: OUT-OF-SCOPE — historical context is intentional, serves as evidence citation.

### Minor Issues

1. **Phase 3.25 "When to skip" is ambiguous**
   - Location: `agent-core/skills/runbook/references/tier3-planning-process.md` — Phase 3.25 "When to skip"
   - Problem: "if user has no feedback, 'proceed' with empty decision list skips corrector dispatch" — this behavior is not documented in the /proof skill itself. The /proof skill's terminal action "apply" section says "If artifact is a planning artifact: dispatch lifecycle-appropriate corrector" without a "skip if empty decision list" clause. The runbook assumes /proof behavior that /proof doesn't implement.
   - Fix: Add a skip condition to /proof's Corrector Dispatch section: skip when accumulated decision list is empty (no structural changes to apply).
   - **Status**: FIXED

2. **tier3-outline-process.md Phase 3.25 bullet already present**
   - Location: `agent-core/skills/runbook/references/tier3-outline-process.md:16`
   - Note: Initial analysis flagged this as missing. Confirmed Phase 3.25 bullet is present in the diff. No action needed.
   - **Status**: OUT-OF-SCOPE — not an issue, bullet is present

3. **/proof skill allowed-tools includes Task but no rationale comment**
   - Location: `.claude/skills/proof/SKILL.md:9` (frontmatter)
   - Problem: `Task` is in allowed-tools for corrector dispatch, which is correct. However, per project convention, the skill's content should make the Task usage clear. It is clear in the Corrector Dispatch section — this is acceptable.
   - **Status**: OUT-OF-SCOPE — Task usage is documented in Corrector Dispatch section.

4. **write-outline.md Phase B label renamed but design SKILL.md still says "Phase B (discussion)"**
   - Location: `agent-core/skills/design/SKILL.md:142`
   - Problem: `write-outline.md` renamed Phase B to "User Validation" but `SKILL.md` still references "Phase B (discussion + outline sufficiency gate)". The parenthetical "discussion" is now stale — it should say "user validation" to match the updated phase name.
   - Fix: Update SKILL.md line 142 parenthetical.
   - **Status**: FIXED

## Fixes Applied

- `agent-core/skills/proof/SKILL.md:132` — Updated Integration Points table: `/design` row Stage changed from "Post-C.4 (Post-design review)" to "Phase C.4.5 (Post-design review)" to match the write-design.md section header
- `agent-core/skills/proof/SKILL.md` — Added skip condition to Corrector Dispatch section: empty decision list skips corrector dispatch
- `agent-core/skills/design/SKILL.md:142` — Updated Phase B parenthetical from "discussion" to "user validation"

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| C1: /proof skill with reword-accumulate-sync loop | Satisfied | `agent-core/skills/proof/SKILL.md` — full loop mechanics present |
| C2: 5 integration points (/requirements step 5, /design Phase B + Post-C.3/C.4.5, /runbook Phase 0.75 step 5 + Post-Phase 3/3.25) | Satisfied | requirements SKILL.md step 5, write-outline.md Phase B, write-design.md C.4.5, tier3-planning-process.md step 5 + Phase 3.25 |
| C3: Author-corrector coupling check in /design | Satisfied | `agent-core/skills/design/SKILL.md` — Author-Corrector Coupling section with dependency table |
| C4: Automatic corrector dispatch after proof "apply" | Satisfied | `/proof` Corrector Dispatch section with dispatch table |
| discussion-protocol.md deletion | Satisfied | File deleted from `agent-core/skills/design/references/` |
| No references to deleted file in executable files | Satisfied | Only reference is in `/proof` SKILL.md as historical evidence citation |

**D-1 (Skill not reference file):** Satisfied — skill tool invocation is the gate, clearly stated.
**D-2 (Inline execution):** Satisfied — `context: fork` absent from frontmatter.
**D-4 (No continuation push/pop):** Satisfied — suspension uses existing prepend mechanism.
**D-5 (Post-expansion as integration point):** Satisfied — Phase 3.25 added.
**D-6 (Requirements as prevention layer):** Satisfied — layered defect model documented.
**D-7 (Name: proof):** Satisfied.
**Author-corrector coupling is /design responsibility:** Satisfied — coupling check in design SKILL.md.

---

## Positive Observations

- The /proof skill is lean and imperative — no narrator comments, no premature abstractions. Loop mechanics are clear.
- Convergence guidance and termination rule from discussion-protocol.md were preserved in write-outline.md Phase B.
- The corrector dispatch table is complete with all artifact patterns from the outline's corrector dispatch table.
- Phase 3.25 "When to skip" rationale is well-grounded in evidence (wrong-RED/bootstrap defect class).
- The `requirements.md` row in the dispatch table correctly marks it as user-validated directly (no corrector).
- Author-corrector coupling produces mandatory visible output — enforced with "mandatory" label.
