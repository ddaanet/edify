# Deliverable Review

## When Identifying Deliverable Artifacts

A **deliverable** is a production artifact that persists in the repository after plan execution and affects system behavior. It is the unit of review.

**Identification method:** Compare the plan's outline (In-scope section) against the repository diff. Every file created or modified that is not a planning/execution artifact (plans/, tmp/, reports/) is a deliverable.

**Derivation:** The outline specifies *what should exist*. The repo diff shows *what was produced*. The gap between these two sets is findings: missing deliverables (incompleteness) or unspecified deliverables (excess).

## .Artifact Types

Each deliverable is classified into exactly one type. The type determines which review axes apply.

| Type | Examples | Identification |
|------|----------|----------------|
| **Code** | `*.py` source modules | Implementation logic |
| **Test** | `test_*.py` files | Behavioral verification |
| **Agentic prose** | `SKILL.md`, agent definitions, skill instructions | Instructions consumed by LLM agents |
| **Human documentation** | Fragments, reference docs, config comments | Instructions consumed by humans |
| **Configuration** | `.gitignore`, `justfile`, `pyproject.toml`, cache files | Build/tool/environment setup |

## .Review Axes

### .Universal (all artifact types)

| Axis | Question | Grounding |
|------|----------|-----------|
| **Conformance** | Does it satisfy the conditions imposed by the design spec? | IEEE 1012 V&V |
| **Functional correctness** | Accurate results with needed precision? | ISO 25010 |
| **Functional completeness** | Covers all specified tasks and objectives? | ISO 25010 |
| **Vacuity** | Does it do real work, or is it ceremonial? | Inverse of completeness — artifact exists but contributes nothing |
| **Excess** | Anything present that wasn't specified? | Inverse of ISO 25010 Functional Appropriateness |

### .Code (+ universal)

| Axis | Question |
|------|----------|
| **Robustness** | Error handling, edge cases, recovery paths? |
| **Modularity** | Clear boundaries, single responsibility? |
| **Testability** | Can behavior be verified through tests? |
| **Idempotency** | Safe to re-run from same state after crash/retry? |
| **Error signaling** | Exit codes and stderr communicate unambiguously to callers? |

### .Test (+ universal)

| Axis | Question |
|------|----------|
| **Specificity** | Fails for the right reason and only that reason? |
| **Coverage** | Are specified critical scenarios covered? |
| **Independence** | Verifies behavior, not implementation? |

### .Agentic prose (+ universal)

| Axis | Question |
|------|----------|
| **Actionability** | Can the agent execute without interpretation? Every step → tool call or state change? |
| **Constraint precision** | Measurable criteria, not judgment words ("relevant", "appropriate")? |
| **Determinism** | Same input state → same output from any agent? |
| **Scope boundaries** | IN/OUT explicit? Agent knows when to stop? |

### .Human documentation (+ universal)

| Axis | Question |
|------|----------|
| **Accuracy** | Technically correct, matches implementation? |
| **Consistency** | Terminology, paths, naming uniform across documents? |
| **Completeness** | Covers all user tasks and needs? |
| **Usability** | Reader can find, understand, and apply the information? |

## .Process

### .Input

- **Outline** — the human-validated design document (ground truth for conformance)
- **Deliverable inventory** — file list with line counts and token counts
- **Token budget** — session context limit minus system prompt overhead

### .Steps

1. **Inventory** — List all deliverables from repo diff against outline scope. Classify each by artifact type. Measure tokens.
2. **Gap analysis** — Compare inventory against outline In-scope items. Flag missing deliverables and unspecified deliverables.
3. **Per-deliverable review** — For each deliverable, evaluate against the axes for its type. Record findings with file:line references.
4. **Cross-cutting checks** — After individual reviews: path consistency across documents, API contract alignment between modules, naming convention uniformity.
5. **Findings classification** — Each finding is one of:
   - **Critical** — Incorrect behavior, data loss, security issue
   - **Major** — Missing functionality, broken references, vacuous artifact
   - **Minor** — Style, clarity, naming inconsistency

### .Output

Per-deliverable finding list with: file:line, axis violated, severity, description.
Summary: counts by severity and axis, gap analysis results.

## .Review Delegation

### When Orchestrator Handles Review Delegation

**Decision Date:** 2026-02-18

**Rule:** Orchestrator delegates ALL reviews after execution agents commit. Execution agents never delegate reviews.

**Why execution agents can't delegate:**
1. Sub-agents lack Task and Skill tools — cannot delegate to any reviewer.
2. All reviews must be delegated to prevent implementer bias — implementer never reviews own work.

**Domain-specific routing:** corrector (code), skill-reviewer (skills), agent-creator (agents), runbook-corrector (planning), corrector + doc-writing skill (human docs). See artifact review routing table in `plugin/fragments/review-requirement.md`.

### When Deliverable Review Catches Drift

**Decision Date:** 2026-02-18

**Rule:** Post-orchestration deliverable review catches inter-file consistency gaps that per-step vet misses.

**Gap:** Per-step vet validates each step's artifacts against that step's scope. It cannot catch gaps between files that weren't both in scope at the same time.

**What deliverable review catches:** Stale copies, broken references, missing cross-references, naming inconsistencies across the deliverable set.

**Evidence:** memory-index skill drifted during execution (3 entries missing); workflows-terminology.md referenced non-existent agent; runbook skill missing general-patterns.md reference. Each step's artifacts were internally consistent — gaps only visible holistically.

### When Resolving Deliverable Review Findings

**Decision Date:** 2026-02-28

**Rule:** Every finding must resolve to one of: (1) fix inline now, or (2) pending task as issue tracker entry. There is no third option.

**Anti-pattern:** "Minor findings deferred — no pending task created." Deferral without a tracking mechanism is abandonment. The finding disappears from all active surfaces. Severity classification exists for report readers to assess risk, not as skip permission for executors.

**Second anti-pattern:** Severity-as-priority-filter. Agent treats Minor severity as implicit permission to drop findings during fix execution. Conflates "low impact if wrong" with "acceptable to skip."

**Correct pattern:** The fix task created by `/deliverable-review` scopes ALL findings (Critical, Major, Minor). The executing agent fixes each one or creates a pending task. "Noted in report" is not a resolution — reports are not checked proactively.

**Evidence:** Two occurrences of identical pattern. Learning created after first; learning present in context during second but agent rationalized past it via ambiguous "deferral" language in review skill (since fixed).

## .Sources

- [ISO/IEC 25010:2023](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010) — Product quality model (functional suitability, reliability, maintainability)
- [IEEE 1012](https://standards.ieee.org/ieee/1012/5609/) — V&V: conformance of development products to activity requirements
- [ISO/IEC 26514](https://www.iso.org/standard/43073.html) — Documentation quality: accuracy, consistency, completeness, usability
- [AGENTIF benchmark](https://keg.cs.tsinghua.edu.cn/persons/xubin/papers/AgentIF.pdf) — Constraint precision in agentic instructions
- [arXiv 2601.03359](https://arxiv.org/abs/2601.03359) — Prompt instruction constraint optimization
- [Anthropic: Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — Outcome-focused evaluation, avoiding brittleness
