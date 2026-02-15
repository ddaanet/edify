# Step 5.4 Self-Review: design-vet-agent criteria additions

**File:** `agent-core/agents/design-vet-agent.md`
**FR:** FR-20
**Reviewer:** task agent (agent-creator delegation skipped per orchestrator instruction)

## Changes Applied

**Cross-Reference Validation** (added after Missing Context in section 2):
- Glob `agent-core/agents/` and `.claude/agents/` to verify agent names resolve to files
- Checks deliverables tables, phase specs, and prose agent references
- Flags mismatches with near-miss typo examples (outline-review-agent vs runbook-outline-review-agent)
- Includes Glob output for correction; severity: critical for deliverable targets, major for ambiguous prose
- Added cross-reference item to Completeness checklist with forward reference

**Mechanism-Check Validation** (added after Cross-Reference Validation in section 2):
- Verifies each behavioral FR/deliverable has concrete implementation mechanism
- Red flags: "improve", "enhance", "better", "strengthen" without specifying how
- Required: algorithm, data structure, control flow, specific prose, or pattern reference
- Flags mechanism-free specs a planner cannot implement; severity: major for core FRs, minor for supplementary
- Added mechanism-check item to Feasibility checklist with forward reference

## Verification

- Both criteria placed within existing section 2 (Analyze Design), maintaining document flow
- Completeness and Feasibility checklists updated with forward references to new subsections
- Cross-reference criterion specifies exact Glob directories and validation logic per step file
- Mechanism-check has concrete red flag words and mechanism requirement examples per step file
- Both grounded in session findings: design targeted wrong agent (cross-ref), FR-18 lacked mechanism (mechanism-check)
- No structural disruption: new subsections follow existing Missing Context pattern

## Assessment

All acceptance criteria from step-5-4.md satisfied. No issues found.
