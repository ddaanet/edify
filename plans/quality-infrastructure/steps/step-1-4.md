# Step 1.4

**Plan**: `plans/quality-infrastructure/runbook.md`
**Execution Model**: opus
**Phase**: 1

---

## Step 1.4: Rename skill directory and fragment

**Objective**: Rename vet skill to review, rename vet-requirement fragment to review-requirement, update internal content of both.

**Execution Model**: Opus

**Prerequisite**: Read SKILL.md and review-requirement.md fully before editing.

**Implementation**:

1. `git mv agent-core/skills/vet/ agent-core/skills/review/`

2. Update agent-core/skills/review/SKILL.md:
   - Frontmatter: `name: vet` → `name: review`
   - Update description to use "review" language
   - Apply full terminology table throughout body text:
     - vet-fix-agent → corrector
     - vet-agent → remove or update (deprecated per D-1)
     - All other old names → new names per table
   - Remove vet-taxonomy.md reference (now embedded in corrector.md)

3. `git mv agent-core/fragments/vet-requirement.md agent-core/fragments/review-requirement.md`

4. Update review-requirement.md content:
   - Title: "Vet Requirement" → "Review Requirement"
   - Rule text: "delegate to `vet-fix-agent`" → "delegate to `corrector`"
   - Routing table: vet-fix-agent → corrector, design-vet-agent → design-corrector
   - Process description: "vet" → "review", "vetting" → "review/correction"
   - Template: vet-fix-agent → corrector throughout
   - Remove reference to "agent-core/agents/vet-taxonomy.md" — note taxonomy is now in corrector.md
   - "vet-fix report" → "correction"
   - Section heading "Vet Requirement" → "Review Requirement", "Vet process" → "Review process"
   - Preserve semantic meaning — only change terminology, not behavior

**Expected Outcome**: Skill directory at agent-core/skills/review/ with updated SKILL.md. Fragment at agent-core/fragments/review-requirement.md with updated content. No references to old names within either file.

**Error Conditions**:
- Git mv fails on directory → Try `mkdir -p` target then mv individual files
- Content update ambiguous (e.g., "vet" in a general English context vs agent name) → Change only when "vet" refers to the review process/agent, not general English usage

**Validation**: `ls agent-core/skills/review/SKILL.md` succeeds. `ls agent-core/fragments/review-requirement.md` succeeds. `grep "vet-fix-agent" agent-core/skills/review/SKILL.md agent-core/fragments/review-requirement.md` returns zero hits.

---
