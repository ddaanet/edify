# Deliverable Review: Agent Definitions (workflow-rca-fixes)

**Scope**: 7 agent files modified/created by workflow-rca-fixes (20 FRs, 6 phases)
**Date**: 2026-02-15
**Methodology**: 9-axis prose review (conformance, functional correctness, completeness, vacuity, excess, actionability, constraint precision, determinism, scope boundaries)

## Summary

Agent definitions are well-implemented across the reviewed FRs. Skills frontmatter injection (FR-12, FR-13) is correctly applied to all 5 specified agents. The vet status taxonomy (FR-7) and investigation protocol (FR-8) are thorough and actionable. Two findings warrant attention: FR-18 (review-fix integration) was only implemented in vet-fix-agent but the design and requirements specify it should also apply to outline-review-agent and plan-reviewer; runbook-outline-review-agent lacks `skills:` frontmatter despite being a review agent modified in Phase 4.

## Findings by File

---

### agent-core/agents/vet-fix-agent.md (454 lines)

**FR-12 (skills frontmatter):** `skills: ["project-conventions", "error-handling", "memory-index"]` -- matches design spec exactly.

**FR-13 (memory index injection):** memory-index skill is listed in frontmatter. The skill itself contains the Bash transport prolog with `when-resolve.py` invocation examples. The agent definition does not repeat transport instructions inline (correct -- skill injection handles it).

**FR-7 (vet status taxonomy):** Four statuses (FIXED, DEFERRED, OUT-OF-SCOPE, UNFIXABLE) defined at line 333-338 with criteria and disambiguation guidance. Subcategory codes (U-REQ, U-ARCH, U-DESIGN) at line 336. Taxonomy reference to `vet-taxonomy.md` at line 18. Report template includes Status field with all four options at lines 254, 264, 271.

**FR-8 (investigation-before-escalation):** 4-gate checklist at lines 340-345. Gates are sequenced (scope OUT check -> design deferral -> codebase pattern -> escalation). Each gate diverts to correct status. Actionable: agent can execute each gate mechanically.

**FR-18 (review-fix integration):** Implemented at lines 355-360. Three-step protocol: Grep target file for heading, Edit within section if exists, append if no match.

No findings for this file. Implementation is complete and well-structured.

---

### agent-core/agents/design-vet-agent.md (386 lines)

**FR-12 (skills frontmatter):** `skills: ["project-conventions"]` -- matches design spec.

**FR-20 (cross-reference validation):** Implemented at lines 132-139 as "Cross-Reference Validation" subsection under Analyze Design. Specifies Glob of `agent-core/agents/` and `.claude/agents/`. Includes severity calibration (critical for deliverable targets, major for prose). Includes instruction to show Glob output for correction.

**FR-20 (mechanism-check validation):** Implemented at lines 141-148 as "Mechanism-Check Validation" subsection. Red flags listed ("improve", "enhance", "better", "strengthen"). Required alternatives listed (algorithm, data structure, control flow, specific prose, pattern reference). Severity calibration (major for core FR, minor for supplementary).

No findings for this file. Both FR-20 criteria are concrete and actionable.

---

### agent-core/agents/outline-review-agent.md (347 lines)

**FR-12 (skills frontmatter):** `skills: ["project-conventions"]` -- matches design spec.

#### Finding 1

- **File**: `agent-core/agents/outline-review-agent.md` (entire file)
- **Axis**: Conformance (FR-18)
- **Severity**: Major
- **Description**: FR-18 requires review-fix integration rule in outline-review-agent ("Applies to outline-review-agent, vet-fix-agent, and plan-reviewer" per requirements.md). The design Phase 3 deliverables table only lists vet-fix-agent.md for FR-18, so the implementation followed the design. However, the requirements document explicitly names outline-review-agent as a target. The agent's Step 5 (Apply Fixes) at line 130 says "Apply fixes using Edit tool" but has no heading-match check before insertion. The Expansion Guidance append at Step 5.5 is a known section name, but general fix application lacks the merge-not-append protocol.

  **Root cause**: Design Phase 3 deliverables table narrowed FR-18 scope to vet-fix-agent only, while requirements.md names all three agents. This is a design-requirements gap, not an implementation defect.

---

### agent-core/agents/plan-reviewer.md (182 lines)

**FR-12 (skills frontmatter):** `skills: ["project-conventions", "review-plan"]` -- matches design spec (already had review-plan, project-conventions added).

#### Finding 2

- **File**: `agent-core/agents/plan-reviewer.md` (entire file)
- **Axis**: Conformance (FR-18)
- **Severity**: Major
- **Description**: Same as Finding 1. FR-18 requirements.md text: "Applies to outline-review-agent, vet-fix-agent, and plan-reviewer fix application." Plan-reviewer's fix process (lines 90-94) applies fixes via Edit tool but has no heading-match / merge-not-append protocol. The design Phase 3 deliverables table only targets vet-fix-agent for FR-18, so this is a design-requirements gap.

No other findings. Agent is compact and well-structured for its purpose.

---

### agent-core/agents/refactor.md (266 lines)

**FR-12 (skills frontmatter):** `skills: ["project-conventions", "error-handling"]` -- matches design spec.

#### Finding 3

- **File**: `agent-core/agents/refactor.md`, line 136
- **Axis**: Functional correctness
- **Severity**: Minor
- **Description**: Step 5 "Update Documentation" uses raw `grep -r` commands instead of the Grep tool. Lines 136 and 157 contain `grep -r "old_reference" plans/` in bash blocks. The agent's tool list includes Grep, and project conventions (injected via skills) require using Grep tool over bash grep. However, these are example code blocks within documentation, not executable instructions per se -- the agent would interpret them. Low practical impact since the agent has access to Grep tool and project-conventions skill guides it to use Grep.

#### Finding 4

- **File**: `agent-core/agents/refactor.md`, line 152
- **Axis**: Functional correctness
- **Severity**: Minor
- **Description**: Step 5.4 "Regenerate step files" uses `python agent-core/bin/prepare-runbook.py` instead of invoking directly via shebang (`agent-core/bin/prepare-runbook.py`). Per sandbox-exemptions fragment, the script has a permissions.allow pattern matching `Bash(agent-core/bin/prepare-runbook.py:*)` and using `python3` prefix breaks the pattern match. Minor since refactor agent typically operates on code, not runbook regeneration.

No conformance findings. Skills injection is correct per design.

---

### agent-core/agents/runbook-outline-review-agent.md (523 lines)

**FR-5 (growth projection):** Implemented at lines 138-144 as "Growth Projection" subsection under Review Criteria. Formula specified: `current_lines + (items x avg_lines_per_item)`. Thresholds: 350 cumulative (with 400 enforcement). >10 items same file flag. Split recommendation in Expansion Guidance.

**FR-11 (semantic propagation):** Implemented at lines 146-154 as "Semantic Propagation" subsection. Grep-based classification into producer/consumer. Detection triggers specified ("terminology change", "rename", "semantic shift", "replaces", "supersedes"). Fix action specified (list missing consumer files, recommend outline items).

#### Finding 5

- **File**: `agent-core/agents/runbook-outline-review-agent.md`, frontmatter (line 1-13)
- **Axis**: Completeness (FR-12 adjacency)
- **Severity**: Minor
- **Description**: This agent has no `skills:` frontmatter. The design (Phase 1 deliverables table) specifies skills injection for 5 agents: vet-fix-agent, design-vet-agent, outline-review-agent, plan-reviewer, and refactor. runbook-outline-review-agent is NOT in that list, so this is technically conformant with the design. However, it is a review agent that applies fixes (Fix-all policy, line 206), produces prose reports, and uses bash commands -- making it a natural candidate for project-conventions at minimum. The absence is a design gap rather than an implementation defect; the agent was not included in FR-12's scope.

#### Finding 6

- **File**: `agent-core/agents/runbook-outline-review-agent.md`, lines 138-144
- **Axis**: Constraint precision (FR-5)
- **Severity**: Minor
- **Description**: Growth projection formula says "use outline step descriptions to estimate avg_lines_per_item" but does not specify how to derive the estimate from descriptions. This leaves the estimation method to agent judgment. For a haiku/sonnet executor, this could produce inconsistent projections. However, line-count estimation from prose descriptions is inherently approximate -- specifying a fixed multiplier would be false precision. The threshold-based approach (flag at 350, enforce at 400) provides a 50-line buffer that absorbs estimation variance. Acceptable given the domain.

#### Finding 7

- **File**: `agent-core/agents/runbook-outline-review-agent.md`, lines 146-154
- **Axis**: Actionability (FR-11)
- **Severity**: Minor
- **Description**: Semantic propagation detection triggers are string patterns ("terminology change", "rename", etc.) to grep for in the design document. These are reasonable heuristics but depend on design authors using these exact terms. A design that introduces a new type system without using the word "rename" or "terminology change" would not trigger detection. The heuristic is documented as detection patterns rather than exhaustive rules, so this is acceptable as a best-effort gate.

---

### agent-core/agents/vet-taxonomy.md (62 lines)

**FR-7 (vet status taxonomy):** Four statuses defined with criteria at lines 7-12. Subcategory codes (U-REQ, U-ARCH, U-DESIGN) at lines 20-24 with "When to use" criteria. Examples for each code at lines 28-38. Investigation summary format at lines 42-51 with all 4 gates. Deferred Items report template at lines 55-62.

No findings. Taxonomy document is complete, precise, and well-structured.

---

## Cross-Cutting Analysis

### FR-18 Design-Requirements Gap

Findings 1 and 2 trace to the same root cause: the requirements document (FR-18 acceptance criteria) names three agents (outline-review-agent, vet-fix-agent, plan-reviewer), but the design Phase 3 deliverables table only lists vet-fix-agent.md. The implementation correctly followed the design. This is a design narrowing that was either intentional (tacit scope reduction) or an oversight during design. The practical impact is limited: outline-review-agent already has the Expansion Guidance section as a known append target, and plan-reviewer applies fixes to runbook structure where heading duplication is less likely than in prose documents.

### Skills Coverage Gap

Five agents received `skills:` frontmatter per FR-12 design. One review agent (runbook-outline-review-agent) was not included despite performing the same class of work (review + fix-all + prose report). This is a design scope boundary, not an implementation defect. A future task could extend FR-12 to this agent.

### Consistency of Status Taxonomy

The four-status taxonomy appears in three locations with consistent definitions:
- `vet-fix-agent.md` lines 333-338 (agent procedure)
- `vet-taxonomy.md` lines 7-12 (reference document)
- `vet-requirement.md` lines 97-103 (orchestrator protocol, loaded via CLAUDE.md)

All three are aligned. The vet-fix-agent references vet-taxonomy.md at line 18 for the full reference.

### Investigation Protocol Consistency

The 4-gate investigation protocol appears in:
- `vet-fix-agent.md` lines 340-345 (agent execution)
- `vet-requirement.md` lines 115-119 (orchestrator validation)
- `vet-taxonomy.md` lines 42-51 (reference format)

Gate ordering and diversion logic are consistent across all three.

## Summary Table

| # | File | Line | Axis | Severity | Description |
|---|------|------|------|----------|-------------|
| 1 | outline-review-agent.md | entire | Conformance (FR-18) | Major | Missing review-fix integration rule (design-requirements gap) |
| 2 | plan-reviewer.md | entire | Conformance (FR-18) | Major | Missing review-fix integration rule (design-requirements gap) |
| 3 | refactor.md | 136 | Functional correctness | Minor | Raw grep in example bash blocks instead of Grep tool |
| 4 | refactor.md | 152 | Functional correctness | Minor | `python` prefix on prepare-runbook.py breaks permissions pattern |
| 5 | runbook-outline-review-agent.md | frontmatter | Completeness | Minor | No skills: frontmatter despite being review+fix agent (design gap) |
| 6 | runbook-outline-review-agent.md | 138-144 | Constraint precision | Minor | Growth estimation method left to agent judgment |
| 7 | runbook-outline-review-agent.md | 146-154 | Actionability | Minor | Semantic propagation triggers depend on exact author phrasing |

**Severity distribution**: 0 Critical, 2 Major, 5 Minor
**Classification**: Both Major findings are design-requirements gaps (FR-18 scope narrowing in design), not implementation defects. All Minor findings are within acceptable tolerances for prose agent definitions.
