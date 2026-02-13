# Pipeline Contracts

Centralized I/O contracts for the design-to-deliverable pipeline. Authoritative source — skills reference this document for their input/output specifications.

## Transformation Table

| # | Transformation | Input | Output | Defect Types | Review Gate | Review Criteria |
|---|---------------|-------|--------|-------------|-------------|----------------|
| T1 | Requirements → Design | requirements.md or inline | design.md | Incomplete, infeasible | design-vet-agent (opus) | Architecture, feasibility, completeness |
| T2 | Design → Outline | design.md | runbook-outline.md | Missing reqs, wrong decomposition | runbook-outline-review-agent | Requirements coverage, phase structure, LLM failure modes |
| T3 | Outline → Phase files | runbook-outline.md | runbook-phase-N.md | Vacuity, prescriptive code, density | plan-reviewer | Type-aware: TDD discipline + general quality + LLM failure modes |
| T4 | Phase files → Runbook | runbook-phase-*.md | runbook.md | Cross-phase inconsistency | plan-reviewer (holistic) | Cross-phase consistency, numbering, metadata |
| T5 | Runbook → Step artifacts | runbook.md | steps/step-*.md, agent | Generation errors | prepare-runbook.py | Automated validation |
| T6 | Steps → Implementation | step-*.md | Code/artifacts | Wrong behavior, stubs, drift | vet-fix-agent (checkpoints) | Scope IN/OUT, design alignment |

## Review Delegation Scope Template

Every review delegation must include execution context (per `agent-core/fragments/vet-requirement.md`):

**Required:**
- **Scope IN:** What was produced (files, sections, features)
- **Scope OUT:** What is NOT yet done — reviewer must NOT flag these
- **Changed files:** Explicit file list
- **Requirements:** What the output should satisfy

**Optional (phased work):**
- **Prior state:** What earlier transformations established
- **Design reference:** Path to design document

## UNFIXABLE Escalation

Reviewers at every gate follow fix-all pattern:
1. Fix all issues directly (critical, major, minor)
2. Label truly unfixable issues as `UNFIXABLE` with rationale
3. Caller greps for UNFIXABLE — if found, stop and escalate to user
4. No recommendation dead-ends — fix or escalate, nothing in between

## Phase Type Model

Runbook phases declare type: `tdd` or `general` (default: general).

Type determines:
- **Expansion format:** TDD cycles (RED/GREEN) vs general steps (script evaluation)
- **Review criteria:** TDD discipline for TDD phases, step quality for general phases
- **LLM failure modes:** Apply universally regardless of type

Type does NOT affect: tier assessment, outline generation, consolidation gates, assembly, orchestration, checkpoints.
