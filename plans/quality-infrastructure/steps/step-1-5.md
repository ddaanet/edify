# Step 1.5

**Plan**: `plans/quality-infrastructure/runbook.md`
**Execution Model**: opus
**Phase**: 1

---

## Step 1.5: Rename skill directory and fragment file

**Objective**: Rename vet/ to review/ skill directory and vet-requirement.md to review-requirement.md fragment, update content.
**Script Evaluation**: Small
**Execution Model**: Opus
**Depends on**: Step 1.1

**Implementation**:
- git mv agent-core/skills/vet/ agent-core/skills/review/
- git mv agent-core/fragments/vet-requirement.md agent-core/fragments/review-requirement.md
- Update review/SKILL.md: all vet to review terminology, agent name references per substitution table. Update trigger phrase, description, all internal references.
- Update review-requirement.md: agent name references per substitution table (vet-fix-agent to corrector, design-vet-agent to design-corrector, etc.), vet to review terminology
- Requires `dangerouslyDisableSandbox: true`
- Commit changes

**Expected Outcome**: Skill directory at review/, fragment at review-requirement.md. Content updated with new terminology.
**Error Conditions**: git mv fails -> STOP, report. Content ambiguity -> STOP, describe alternatives.
**Validation**: `ls agent-core/skills/review/SKILL.md` succeeds; grep both files for old names -> zero hits

---
