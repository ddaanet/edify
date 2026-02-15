# Step 3.1

**Plan**: `plans/pushback/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Step 3.1: Wire fragment into CLAUDE.md

**Objective**: Add pushback fragment reference to CLAUDE.md

**Implementation**:

Add line `@agent-core/fragments/pushback.md` to CLAUDE.md Core Behavioral Rules section.

**Insertion point**: After `@agent-core/fragments/execute-rule.md` in Core Behavioral Rules section

**Expected Outcome**: CLAUDE.md contains `@agent-core/fragments/pushback.md` reference in Core Behavioral Rules section

**Error Conditions**:
- Fragment reference inserted in wrong section → STOP, move to Core Behavioral Rules
- Fragment file doesn't exist → STOP, verify Phase 1 completed

**Validation**: Grep CLAUDE.md for pushback.md reference, verify it's in Core Behavioral Rules section (between execute-rule and delegation fragments)

---
