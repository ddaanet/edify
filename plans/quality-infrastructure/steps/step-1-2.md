# Step 1.2

**Plan**: `plans/quality-infrastructure/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 1.2: Embed vet-taxonomy and delete deprecated agents

**Objective**: Embed vet-taxonomy.md content into corrector.md, delete vet-taxonomy.md and vet-agent.md.
**Script Evaluation**: Small
**Execution Model**: Sonnet
**Depends on**: Step 1.1

**Implementation**:
- Read agent-core/agents/vet-taxonomy.md (62 lines: status table, subcategory codes, investigation format, deferred items template)
- Read agent-core/agents/corrector.md
- Insert full taxonomy content into corrector.md after the role description section, before any existing status taxonomy reference. Preserve all tables and examples.
- Delete agent-core/agents/vet-taxonomy.md
- Delete agent-core/agents/vet-agent.md (deprecated per D-1: zero active call sites)
- Commit changes

**Expected Outcome**: corrector.md contains embedded taxonomy. vet-taxonomy.md and vet-agent.md deleted.
**Error Conditions**: Insertion point ambiguous -> STOP, describe section boundaries found
**Validation**: grep for taxonomy table headers in corrector.md succeeds; verify deleted files absent

---
