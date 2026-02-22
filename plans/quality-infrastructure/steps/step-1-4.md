# Step 1.4

**Plan**: `plans/quality-infrastructure/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 1.4: Update renamed agent internals

**Objective**: Update YAML frontmatter and cross-references in all 11 renamed agents.
**Script Evaluation**: Small
**Execution Model**: Sonnet
**Depends on**: Step 1.1

**Implementation**:
- Update `name:` YAML frontmatter in all 11 renamed agents to match new filename (without .md)
- Update cross-references between agents per substitution table:
  - tdd-auditor.md: vet-fix-agent to corrector
  - runbook-corrector.md: vet-fix-agent to corrector
  - runbook-outline-corrector.md: vet-fix-agent to corrector
  - outline-corrector.md: vet-fix-agent to corrector
- Update `skills:` frontmatter lists if any reference old agent names
- Grep each renamed file for any remaining old names from substitution table
- Commit changes

**Expected Outcome**: All 11 agents have correct `name:` frontmatter and internal cross-references.
**Error Conditions**: Old names found in grep -> fix before committing
**Validation**: grep all 11 files for all old names from substitution table -> zero hits

---
