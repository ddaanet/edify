# Step 4.1 Review: Outline Review Agent Enhancements

**Artifact**: `agent-core/agents/runbook-outline-review-agent.md`
**Step**: 4.1 (FR-5, FR-11 + deliverable traceability)
**Date**: 2026-02-15
**Mode**: Self-review (agent-creator delegation skipped per orchestrator directive)

## Changes Applied

Three additions to Section 3 (Review Criteria), placed between existing Checkpoint Spacing and Step Clarity criteria:

### 1. Growth Projection Enhancement (FR-5)

**Pre-existing section** at lines 138-143 already covered basic growth projection. Enhanced with:
- Concrete formula: `current_lines + (items x avg_lines_per_item)`
- Refined split-phase wording: "split phases must precede first phase exceeding 350 cumulative lines" (was "phases producing files >350 projected lines must include split point before that phase")
- Fix action includes projected sizes alongside split point recommendation

**Acceptance criteria check:**
- Concrete formula: present (line 140)
- 350-line threshold: present (lines 141, 143)
- Flag >10 items same file: present (line 142)
- Split-phase placement logic: present (line 143)

### 2. Semantic Propagation Checklist (FR-11)

New `**Semantic Propagation:**` section (lines 146-154) with:
- Trigger condition: design introduces new terminology, types, or renames
- Grep-based classification: producer files (rewrite) vs consumer files (update)
- Completeness check: all files referencing old semantics must appear in outline
- Detection patterns: "terminology change", "rename", "semantic shift", "replaces", "supersedes"
- Fix action: list missing consumer files with outline item recommendations

**Acceptance criteria check:**
- Grep-based detection: present (line 152)
- Producer/consumer classification: present (lines 149-150)
- Missing consumer detection: present (line 153)
- Fix action: present (line 154)

### 3. Deliverable-Level Traceability Check

New `**Deliverable-Level Traceability:**` section (lines 156-162) with:
- Cross-reference against design deliverables table, not just FR numbers
- Row-by-row verification: each deliverable row maps to outline step
- Multiple deliverables per FR need multiple step mappings
- Detection: parse `| Artifact | Action | FR |` tables from design
- Fix action: identify unmapped deliverables with phase placement recommendation

**Grounding**: Interactive opus review caught FR-10 having 2 deliverables but only 1 step mapping in this session's outline review.

**Acceptance criteria check:**
- Table extraction: present (line 160)
- Row-by-row verification: present (line 158)
- Multi-deliverable handling: present (line 159)
- Fix action: present (line 162)

## Structural Assessment

- All three sections follow existing pattern: bold header, bullet list, detection method, fix action
- Placement within Section 3 (Review Criteria) is consistent with existing criteria dimensions
- No disruption to flow: Growth Projection -> Semantic Propagation -> Deliverable-Level Traceability -> Step Clarity -> Execution Readiness
- Total agent file grew from ~505 to ~525 lines (within acceptable range)

## Issues Found

None. All three additions are actionable, have concrete detection methods, and include fix actions.

---

**Status**: All criteria met. No UNFIXABLE issues.
