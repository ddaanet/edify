# Step 1.1

**Plan**: `plans/quality-infrastructure/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 1.1: Rename agent definition files and embed taxonomy

**Objective**: Git mv all 11 agent files to new names, embed vet-taxonomy.md content into corrector.md, delete vet-agent.md and vet-taxonomy.md.

**Execution Model**: Sonnet

**Implementation**:

1. Git mv 6 review/correct agents (in agent-core/agents/):
   - vet-fix-agent.md → corrector.md
   - design-vet-agent.md → design-corrector.md
   - outline-review-agent.md → outline-corrector.md
   - runbook-outline-review-agent.md → runbook-outline-corrector.md
   - plan-reviewer.md → runbook-corrector.md
   - review-tdd-process.md → tdd-auditor.md

2. Git mv 5 execution agents (in agent-core/agents/):
   - quiet-task.md → artisan.md
   - quiet-explore.md → scout.md
   - tdd-task.md → test-driver.md
   - runbook-simplification-agent.md → runbook-simplifier.md
   - test-hooks.md → hooks-tester.md

3. Embed taxonomy: Read vet-taxonomy.md (63 lines: status table, subcategory codes, investigation format, deferred items template). Read corrector.md. Find the "Status taxonomy" reference or the section that references vet-taxonomy.md. Replace the reference with the full taxonomy content inline. Preserve the taxonomy's heading structure within corrector.md.

4. Git rm vet-taxonomy.md (content now embedded in corrector.md).

5. Git rm vet-agent.md (deprecated per D-1: zero active call sites — exploration report confirms no production delegation).

**Expected Outcome**: 11 renamed files, 2 deleted files, taxonomy content embedded in corrector.md.

**Error Conditions**:
- Git mv fails → STOP, verify source file exists at expected path
- Taxonomy embed location unclear in corrector.md → Read full file, search for "taxonomy" or "vet-taxonomy" reference, place near existing status/classification content

**Validation**: `ls agent-core/agents/corrector.md design-corrector.md outline-corrector.md runbook-outline-corrector.md runbook-corrector.md tdd-auditor.md artisan.md scout.md test-driver.md runbook-simplifier.md hooks-tester.md` succeeds. `ls agent-core/agents/vet-agent.md agent-core/agents/vet-taxonomy.md` fails (deleted). `grep -c "UNFIXABLE Subcategory Codes" agent-core/agents/corrector.md` returns 1.

---
