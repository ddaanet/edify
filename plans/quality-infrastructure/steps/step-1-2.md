# Step 1.2

**Plan**: `plans/quality-infrastructure/runbook.md`
**Execution Model**: opus
**Phase**: 1

---

## Step 1.2: Update agent internal references

**Objective**: Update name: frontmatter and all cross-references within renamed agent definitions.

**Execution Model**: Opus

**Prerequisite**: Read each agent file fully before editing — understand cross-reference targets and frontmatter structure.

**Implementation**:

1. Update `name:` frontmatter in all 11 renamed agents to match new filename (sans .md):
   - corrector.md → `name: corrector`
   - design-corrector.md → `name: design-corrector`
   - outline-corrector.md → `name: outline-corrector`
   - runbook-outline-corrector.md → `name: runbook-outline-corrector`
   - runbook-corrector.md → `name: runbook-corrector`
   - tdd-auditor.md → `name: tdd-auditor`
   - artisan.md → `name: artisan`
   - scout.md → `name: scout`
   - test-driver.md → `name: test-driver`
   - runbook-simplifier.md → `name: runbook-simplifier`
   - hooks-tester.md → `name: hooks-tester`

2. Update `description:` frontmatter to use new terminology where applicable (e.g., "Vet review agent" → "Review agent", "quiet task" → "artisan").

3. Apply full terminology table from Common Context within each agent's body text:
   - Cross-agent references (e.g., tdd-auditor referencing corrector instead of vet-fix-agent)
   - Process terminology ("vetting" → "review/correction", "vet report" → "review report")
   - Other agent references (quiet-task → artisan, plan-reviewer → runbook-corrector, etc.)

4. Update `skills:` frontmatter if any agent references renamed skills (vet → review).

**Expected Outcome**: All 11 agent definitions use new names in frontmatter and body. No old-name references within agent-core/agents/.

**Error Conditions**:
- Agent has unexpected frontmatter format → STOP, examine and adapt
- Cross-reference target ambiguous → use terminology table as authoritative source

**Validation**: `grep -rl "vet-fix-agent\|design-vet-agent\|outline-review-agent\|runbook-outline-review-agent\|plan-reviewer\|review-tdd-process\|quiet-task\|quiet-explore\|tdd-task\|runbook-simplification-agent\|test-hooks" agent-core/agents/` returns zero files (excluding this runbook and reports).

---
