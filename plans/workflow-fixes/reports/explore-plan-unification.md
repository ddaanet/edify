# Plan Unification Structural Analysis

**Scope:** Mapping shared structure between /plan-tdd (1052 lines) and /plan-adhoc (1153 lines) to identify unification opportunities.

**Key Finding:** Both skills implement nearly identical execution-planning patterns with TDD-specific augmentations. Shared structure accounts for ~75% of content; divergence is systematic and easily parameterized.

---

## A. Shared Structure

### A1. Skill Frontmatter (lines 1-12 in both)
- **Identical:** name, description, model (sonnet), allowed-tools, requires, outputs
- **Divergence:** plan-tdd adds "type: tdd" validation note
- **Unification:** Single template with optional type specifier

### A2. Tier Assessment (Plan-TDD Phase 0: 61-100, Plan-Adhoc: 35-111)
Both implement identical three-tier evaluation:
- **Tier 1:** Direct implementation (<100 lines, 1 test file, single model)
- **Tier 2:** Lightweight delegation (4-10 cycles TDD / 6-15 files adhoc, agent isolation)
- **Tier 3:** Full runbook (>10 cycles / >15 files, multi-phase orchestration)

**Lines matched:**
- Tier assessment output format (lines 69-79 / 43-52)
- Tier 1 sequence (lines 85-88 / 57-71)
- Tier 2 guidance (lines 90-95 / 73-84)
- Tier 3 routing (line 98 / 120)

### A3. Outline Generation (Plan-TDD 1.5: 131-182, Plan-Adhoc 0.75: 174-218)
Both create `runbook-outline.md` before expansion:

**Shared sections:**
- File: `plans/<feature>/runbook-outline.md` (both 137-139 / 179-180)
- Include components: Requirements mapping, Phase structure, Key decisions, Complexity per phase (140-145 / 181-184)
- Verification quality checklist (149-158 / 186-195):
  - All choices resolved (resolved language check)
  - Inter-step dependencies declared
  - Code fix specificity (affected sites enumerated)
  - Phase boundaries clean
  - Cross-cutting issues scope-bounded
  - Foundation-first ordering
  - Density and checkpoint spacing

**TDD-specific addendum (145-158):** No vacuous cycles, edge-case collapse patterns
**Adhoc-specific:** Same checks apply without "vacuous RED tests" clause

### A4. Consolidation Gate — Outline (Plan-TDD 1.6: 185-230, Plan-Adhoc 0.85: 221-265)
**Identical structure, identical rationale:**
- Scan for trivial phases (≤2 cycles/steps, Low complexity)
- Evaluate merge candidates (same domain, natural continuation, <10 cycles/steps)
- Apply consolidation pattern (lines 206-211 / 241-247 — verbatim match)
- Update traceability

### A5. Complexity Check Before Expansion (Plan-TDD 2.5: 280-321, Plan-Adhoc 0.9: 268-309)
**Identical callback mechanism:**
- Assess expansion scope (lines 286-290 / 274-278)
- Fast-path for pattern-based work
- Callback triggers (same thresholds: 25 steps, 10 per phase, single step too complex)
- Callback levels (lines 305-307 / 292-294)

### A6. Outline Sufficiency Check (Plan-Adhoc 0.95: 312-335 only)
**Not in plan-tdd:** Early termination when outline is execution-ready (no expansion needed)
- Criteria: all targets specified, all choices made, verification criteria present, no unresolved decisions
- Promotion: reformat outline to runbook format, skip Points 1-3 expansion

**Applicability to TDD:** Yes — outlines with <3 phases and <10 cycles often need minimal expansion.

### A7. Phase-by-Phase Expansion (Plan-TDD 3: 354-410, Plan-Adhoc 1: 338-453)
**Parallel structure:**
- For each phase: generate content, review, apply fixes, finalize (lines 360-378 / 343-378)
- Both delegate to review agents (tdd-plan-reviewer / vet-fix-agent)
- Both include Domain Validation skill integration (387-401 / 355-369)

**Key divergence:**
- Plan-TDD: Cycle planning guidance (3.1-3.6: 412-583) → Prose test descriptions, RED/GREEN specs, assertions, stop conditions, dependencies
- Plan-Adhoc: Script evaluation (1.1-1.3: 380-431) → Script size classification (≤25 / 25-100 / >100 lines)
- Plan-Adhoc: Mandatory conformance validation (433-451, sourced from external reference)

### A8. File Size Planning (Plan-TDD 2.7: 324-346, Plan-Adhoc 1.4: 455-473)
**Identical threshold strategy:**
- Current file size + additions, threshold 350 (leaves 50-line margin)
- Planning convention (not runtime enforcement)
- Split step triggers

### A9. Assembly and Metadata (Plan-TDD 4: 587-608, Plan-Adhoc 2: 476-551)
**Pre-assembly validation (lines 593-596 / 482-495):**
- Verify phase files exist
- Check reviews completed
- Confirm no ESCALATION flags

**Metadata preparation (lines 598-602 / 487-490):**
- Count total steps
- Extract Common Context
- Verify Design Decisions ready

**Manual assembly prohibition (lines 603-606 / 498-501):** Both forbid manual concatenation, require prepare-runbook.py

**Weak Orchestrator Metadata (lines 615-665 / 506-549):**
- Both specify identical metadata structure (Total Steps, Execution Model, Dependencies, Error Escalation, Report Locations, Prerequisites, Success Criteria)
- Shared principle: "Orchestrator metadata is coordination info only" (line 550 / 549)

### A10. Consolidation Gate — Runbook (Plan-TDD 4.5: 699-753, Plan-Adhoc 2.5: 554-611)
**Identical gate for merged trivial work:**
- Identify isolated trivial work (lines 705-708 / 560-563)
- Check merge candidates (same-file, setup, cleanup patterns)
- Apply consolidation (lines 717-735 / 572-593)
- Constraints and rationale (identical)

### A11. Final Holistic Review (Plan-TDD 5: 756-830, Plan-Adhoc 3: 614-672)
**Shared review pattern:**
- Collect per-phase results (lines 762-764 / N/A for adhoc — reviews as Point 1)
- Cross-phase consistency verification
- File path validation

**Delegation pattern:**
- Plan-TDD: tdd-plan-reviewer agent (lines 766 / N/A)
- Plan-Adhoc: vet-agent (lines 622 / task delegation lines 621-640)

**Revision loop (Plan-Adhoc lines 654-670):** Read report, check assessment, fix all issues, iterate until "Ready"

### A12. Prepare Artifacts and Handoff (Plan-TDD 5 steps 5-7: 800-826, Plan-Adhoc 4: 698-779)
**Identical final sequence:**
1. Run prepare-runbook.py with dangerouslyDisableSandbox: true
2. Copy `/orchestrate {name}` to clipboard
3. Tail-call `/handoff --commit`

**prepare-runbook.py behavior (both line 800-802 / 759-763):**
- Detects TDD vs general type
- Creates plan-specific agent (.claude/agents/)
- Generates step files
- Creates orchestrator plan
- Stages artifacts for commit

### A13. Checkpoints (Plan-TDD: 879-964, Plan-Adhoc: 783-836)
**Identical checkpoint structure:**
- Light checkpoint: Fix + Functional (every phase boundary)
- Full checkpoint: Fix + Vet + Functional (final boundary or marked phases)
- Process steps (same three-step protocol for each)
- Integration test pattern (xfail → passing)
- Checkpoint placement rules

### A14. Output Locations and Artifacts
Both write to identical paths:
- Runbook: `plans/<name>/runbook.md`
- Phase files: `plans/<name>/runbook-phase-N.md` (adhoc also phase-grouped)
- Reviews: `plans/<name>/reports/*-review.md`
- Step files: `plans/<name>/steps/step-*.md` (generated by prepare-runbook.py)
- Plan-specific agent: `.claude/agents/<name>-task.md`
- Orchestrator plan: `plans/<name>/orchestrator-plan.md`

### A15. Common Pitfalls / Anti-Patterns
Both share identical warnings section covering:
- Direct implementation vs runbook choice
- File path verification (Glob/Grep requirement)
- Outline generation criticality
- Phase-by-phase expansion requirement
- Design decision timing
- Success criteria precision

---

## B. Divergent Structure

### B1. Step/Cycle Planning Guidance (Plan-TDD only: 412-583)

**TDD-specific sections:**
- Cycle numbering (lines 418-421): X.Y format, start at 1.1
- RED specifications (lines 423-439): Test function name, assertions, expected failure, why it fails, verify command
- Prose test descriptions (lines 441-471): Specific assertion format, quality requirements, behavioral specificity validation
- Mandatory conformance test cycles (lines 480-498): External reference consumption, precision prose, assertion quality

**Prose assertion quality rules (lines 462-471):**
- Specific values: "returns string containing 🥈 emoji"
- Specific errors: "raises ValueError with message 'invalid input'"
- Specific structure: "output dict contains 'count' key with integer > 0"
- Validation rule: "Prose must specify exact expected values, patterns, or behaviors"

- GREEN specifications (lines 502-526): Implementation description, behavior, approach hints (NOT code), changes, verify commands
- NO prescriptive code rule (lines 528-533): "Do NOT include complete function implementations, code blocks, exact logic"
- Creation vs transformation cycles (lines 543-556): Investigation prerequisites for code comprehension
- Dependencies (lines 558-568): Sequential (default), cross-phase [DEPENDS: X.Y], regression [REGRESSION], parallel
- Stop conditions (lines 571-575): Auto-generated by prepare-runbook.py from Common Context
- Dependency validation (lines 577-581): Topological sort, no circular/forward refs

**Cycle breakdown guidance (lines 834-856):**
- 1-3 assertions per cycle
- Empty-first cycle ordering (anti-pattern: don't test empty case first)
- Dependency markers
- References patterns.md for detailed guidance

### B2. Script Evaluation in Steps (Plan-Adhoc only: 1.1-1.3: 380-431)

**Step type classification by size:**
- **Small (≤25 lines):** Write complete inline script
- **Medium (25-100 lines):** Prose description of implementation
- **Large (>100 lines):** Mark as requiring separate planning session

**Step type classification by function (lines 397-404):**
- **Transformation** (delete, move, rename, replace): Self-contained recipe
- **Creation** (new test, new code): MUST include investigation prerequisite (Read file, understand behavior/flow)

**Mandatory conformance validation (lines 433-451):**
- Trigger: External reference in design (shell prototype, API spec, mockup)
- Requirement: Validation steps verify conformance to reference
- Validation precision: Exact expected strings from reference
- Lifecycle: Reference consumed at planning time, expected behavior becomes test assertions

### B3. Post-assembly Review Delegation Pattern (Plan-Adhoc 3 only: 614-672)

**Full Task delegation specification (lines 620-641):**
```
Task(
  subagent_type="vet-agent",
  model="sonnet",
  prompt=[explicit delegation text]
)
```

**Review focus (lines 624-639):**
- Cross-phase issues (not re-reviewing individual phases)
- File path validation (Glob verification)
- Requirements satisfaction check
- Report location and format

**Revision loop (lines 654-670):**
- Read review report
- Check assessment status (Ready / Needs Minor / Needs Significant)
- Fix ALL issues before proceeding
- Re-review if significant changes
- Iterate until "Ready"

### B4. TDD Review Protocol (Plan-TDD delegate to tdd-plan-reviewer: reviewed via review-tdd-plan skill)

**Key areas (lines 766-777):**
- Cross-phase consistency (cycle numbering, dependencies across phases)
- Prescriptive code in GREEN phases (critical violation)
- RED/GREEN sequencing (within and across phases)
- Overall cycle progression and incremental coherence
- Metadata alignment

**Critical TDD anti-patterns checked by review-tdd-plan skill (lines 36-210):**
- GREEN phase implementation code violations
- RED/GREEN sequencing errors
- Implementation hint vs prescription boundaries
- Weak RED assertions (structural not behavioral)
- Prose test quality (full code vs description)
- Metadata accuracy
- Empty-first cycle ordering
- Consolidation quality
- File reference validation

### B5. Architecture Differences in Expansion

**Plan-TDD Phase 3 expansion:**
- Per-phase cycle generation (X.1, X.2, ... X.N)
- Background review pattern (launch review, continue to next phase)
- Cross-phase review in Phase 5 (holistic after all phases)
- Domain validation skill integration

**Plan-Adhoc Point 1 expansion:**
- Per-phase step generation (1.1, 1.2, ... N.M)
- Sequential phase review (review after each phase before next)
- Optional final holistic review at Point 3
- Domain validation skill integration (same)

### B6. prepare-runbook.py Detection Logic

**TDD detection (lines 438-455, 448-450):**
```python
has_cycles = bool(re.search(r'^##+ Cycle\s+\d+\.\d+:', content, re.MULTILINE))
has_steps = bool(re.search(r'^##+ Step\s+\d+\.\d+:', content, re.MULTILINE))
if has_cycles:
    is_tdd = True
```

**Validation differences:**
- TDD: validate_cycle_structure (RED/GREEN/Stop conditions), validate_cycle_numbering
- General: validate_phase_numbering (non-monotonic, gap checking)

**Output naming:**
- TDD: `step-{major}-{minor}.md` (e.g., step-1-1.md)
- General: `step-{N}.md` or `step-{N}-{M}.md` (e.g., step-1.md or step-1-2.md)

**Common Context injection (lines 47-60, 475-479):**
- TDD DEFAULT_TDD_COMMON_CONTEXT injected if missing (standard stop/error conditions)
- General: No injection (stop conditions per-step)

### B7. Orchestrate Skill Handling

**Both use orchestrate.md but with differences:**
- TDD completion (lines 248-266): vet-fix-agent review, then review-tdd-process for process analysis
- General completion (lines 268-271): Suggest vet-fix-agent review then commit

**Phase boundary detection (lines 113-150, orchestrate 3.3):**
- Both read next step header, compare Phase field
- TDD: Phase = major cycle number (0, 1, 2, ...)
- General: Phase = explicit Phase metadata from header

---

## C. Step Type Differences

### C1. Headers and Format

**Plan-TDD Cycles:**
- Header: `## Cycle X.Y: [Name] {[DEPENDS: A.B]} {[REGRESSION]}`
- Sections: **Objective**, **RED Phase**, **GREEN Phase**, optional **REFACTOR**
- Prose format: Assertions use bulleted descriptions with specific values/patterns
- Stop conditions: Inherited from Common Context or cycle-specific

**Plan-Adhoc Steps:**
- Header: `## Step N: [Title]` or `## Step N.M: [Title]`
- Sections: **Objective**, **Script Evaluation** (classification), **Execution Model**, **Implementation**, **Expected Outcome**, **Unexpected Result Handling**, **Error Conditions**, **Validation**, **Success Criteria**, **Report Path**
- Script format: Varies by size (inline code ≤25 lines, prose 25-100 lines, reference >100 lines)
- Stop conditions: Per-step, embedded in **Error Conditions** section

### C2. Content Expectations

**TDD cycles expect:**
- RED: Test name, specific prose assertions, expected failure mode, why it fails, verify command
- GREEN: Implementation behavior description (not code), hints referencing design decisions, file changes, verify commands
- Investigation prerequisites for creation cycles only

**Adhoc steps expect:**
- Script evaluation classification upfront
- For creation steps: investigation prerequisites
- Execution model assignment (haiku/sonnet/opus per step)
- Explicit error handling and validation

### C3. Metadata Placement

**TDD (frontmatter + title):**
```markdown
## Cycle 1.1: Load Configuration [DEPENDS: 1.0] [REGRESSION]
**Objective**: [goal]
```

**Adhoc (step header → body metadata):**
```markdown
## Step 1: Load Configuration
**Objective**: [goal]
**Script Evaluation**: Prose description
**Execution Model**: Haiku
**Report Path**: [path]
```

### C4. Dependencies

**TDD:**
- Default: sequential within phase
- Cross-phase: `[DEPENDS: X.Y]`
- Regression: `[REGRESSION]`
- Parallel: explicit (rare)

**Adhoc:**
- Default: sequential
- Per-step or phase-level in Common Context
- Explicit declaration required

---

## D. Review Gate Differences

### D1. TDD Review Gate (tdd-plan-reviewer agent via review-tdd-plan skill)

**When:** After each phase (Phase 3 per-phase) and final holistic (Phase 5)

**What it checks:**
- GREEN phases: No implementation code (descriptive + hints only)
- RED phases: Prose quality (specific assertions, behavioral not structural)
- RED/GREEN sequencing: Will test actually fail before implementation?
- File path validation: Glob verify each referenced file
- Metadata accuracy: Total Steps count matches actual
- Empty-first cycle ordering
- Consolidation quality
- Mandatory sections (RED/GREEN for all non-spike cycles)

**Fixes:**
- Removes prescriptive code from GREEN
- Strengthens vague prose in RED (adds specific values/patterns)
- Consolidates trivial cycles
- Corrects sequencing violations (non-fixable: escalates)
- Updates metadata

**Escalation:** UNFIXABLE if cycle decomposition or outline revision needed

### D2. Adhoc Review Gate (vet-fix-agent on per-phase basis, then optional vet-agent holistically)

**When:** After each phase (Point 1 review) and optionally at final (Point 3)

**What it checks (per-phase):**
- Clarity and execution readiness
- File path existence
- Specification completeness (no "determine"/"decide" language)
- Step scope (not too large)

**What it checks (final holistic, Point 3):**
- Cross-phase consistency
- Step numbering
- Dependency ordering
- Metadata accuracy (step counts, model assignments)
- File path validation
- Requirements satisfaction

**Fixes:** ALL issues (critical, major, minor)

**Escalation:** UNFIXABLE if design decisions needed or scope conflicts exist

### D3. Outline Review Gate (runbook-outline-review-agent for both)

**Both delegate to identical agent at identical point:**
- Plan-TDD Phase 1.5 step 3
- Plan-Adhoc Point 0.75 step 3

**What it validates:**
- Requirements coverage (all FR-* mapped)
- Design alignment
- Phase structure (balanced, logical grouping)
- Complexity distribution
- Dependency sanity
- Vacuity (no scaffold-only cycles)
- Foundation-first ordering (intra-phase)
- Density (no adjacent edge-case clusters)
- Checkpoint spacing
- Execution readiness

**Appendix:** `## Expansion Guidance` section with consolidation candidates, cycle expansion notes, checkpoint recommendations

---

## E. prepare-runbook.py Detection

### E1. Type Detection

**Frontmatter parsing (lines 63-100):**
- Both read optional `type: tdd` field
- Default: `type: general`
- Validates type in [tdd, general]

**Phase file detection (lines 398-435, assemble_phase_files):**
- Scans for `runbook-phase-*.md` files
- Detects type from first phase file:
  ```python
  has_cycles = bool(re.search(r'^##+ Cycle\s+\d+\.\d+:', content))
  has_steps = bool(re.search(r'^##+ Step\s+\d+\.\d+:', content))
  if has_cycles: is_tdd = True
  ```

### E2. Validation Differences

**TDD validation (lines 908-943):**
- extract_cycles (detects X.Y headers, validates numbering)
- validate_cycle_numbering (errors: no cycles, duplicates, bad start; warnings: gaps)
- validate_cycle_structure (errors: missing RED/GREEN, missing stop conditions; warnings: missing dependencies)
- extract_sections (for Common Context, Orchestrator)

**General validation (lines 949-953, 769-775):**
- extract_sections (for Steps, phases, Common Context)
- validate_phase_numbering (errors: non-monotonic phases; warnings: gaps)

### E3. Phase Detection for Stop Conditions

**TDD special handling (lines 163-207, validate_cycle_structure):**
- Spike cycles (0.x): No RED/GREEN required
- Regression cycles ([REGRESSION] in title): GREEN only
- Standard cycles: Both RED and GREEN required
- Stop/Error Conditions: Can be in cycle OR Common Context (inherited)

**Default injection (lines 47-60, 475-479):**
```python
DEFAULT_TDD_COMMON_CONTEXT = """## Common Context
**TDD Protocol:** ...
**Stop/Error Conditions (all cycles):**
STOP IMMEDIATELY if: RED phase test passes (expected failure) ...
```

### E4. Step File Generation

**TDD (lines 809-817):**
```python
for cycle in sorted(cycles, key=lambda c: (c['major'], c['minor'])):
    step_file_name = f"step-{cycle['major']}-{cycle['minor']}.md"
    # Calls generate_cycle_file(cycle, runbook_path, model)
    # Phase metadata = cycle['major'] (major cycle number)
```

**General (lines 818-829):**
```python
for step_num in sorted(sections['steps'].keys()):
    step_file_name = f"step-{step_num.replace('.', '-')}.md"
    # Calls generate_step_file(step_num, step_content, runbook_path, default_model, phase)
    # Phase metadata extracted from step_phases dict
```

**Metadata header (lines 655-681, 684-708):**
- Both include: Plan path, Execution Model, Phase
- Both extract report_path if present
- Both format uniformly

---

## F. Orchestrate Differences

### F1. Step/Cycle Invocation

**Both invoke via Task tool:**
```
Task(subagent_type="<runbook-name>-task", ...)
```

**Model selection (lines 69-81):**
- Both read **Execution Model** field from step file header
- Extract via regex: `\*\*Execution Model\*\*:\s*(\w+)` (case-insensitive)
- Default model if not specified

### F2. Phase Boundary Detection

**Shared logic (orchestrate 3.3, lines 113-150):**
1. After step completes, read next step file header (first 10 lines)
2. Compare Phase field with current step's phase
3. If same phase: proceed to next step
4. If phase changed: delegate to vet-fix-agent for checkpoint

**Phase field usage:**
- TDD: Phase = major cycle number (0, 1, 2, ...)
- General: Phase = explicit metadata field

### F3. Checkpoint Delegation

**Both use identical delegation template (orchestrate 125-150):**
```
Delegate to vet-fix-agent:
- First: Run `just dev`, fix failures, commit
- Scope: IN/OUT context, changed files, phase objective
- Review: test quality, implementation quality, integration, design anchoring
- Report path: plans/<name>/reports/checkpoint-N-vet.md
```

### F4. TDD-Specific Completion (orchestrate 6, lines 248-266)

**After all steps succeed:**
1. Delegate to vet-fix-agent for quality review (write to `vet-review.md`)
2. Delegate to review-tdd-process for process analysis (write to `tdd-process-review.md`)
3. Report overall success with both reports

**General completion (lines 268-271):**
- Report overall success
- Suggest vet-fix-agent review
- Suggest `/commit` next

---

## G. Candidate Unified Structure

### Unification Strategy

**Core insight:** 75% of code is identical structure with TDD-specific augmentations. A unified `/plan` skill can parameterize differences while preserving specialized logic.

### G1. Unified Skill Frontmatter
```yaml
---
name: plan
description: |
  Create execution runbooks (general or TDD) with multi-phase planning process.
  Routes based on design type: TDD mode → cycle-based planning, general → step-based planning.
model: sonnet
allowed-tools: [Task, Read, Write, Edit, Skill, Bash(...prepare-runbook.py...)]
requires: [Design document, CLAUDE.md]
outputs: [Runbook, phase files, Common Context]
---
```

### G2. Unified Phase Structure

**Collapse to common phases with TDD/General branches:**

```
Phase 0: Tier Assessment (UNIFIED)
  - Evaluate complexity
  - Route to Tier 1/2/3

Phase 0.5: Codebase Discovery (UNIFIED)
  - Glob/Grep file locations
  - Memory index scan
  - Validate assumptions

Phase 0.75: Runbook Outline (UNIFIED)
  - Create runbook-outline.md
  - Requirements mapping
  - Phase structure
  - Delegate to runbook-outline-review-agent

Phase 0.85: Consolidation Gate (UNIFIED)
  - Scan for trivial phases
  - Merge candidates

Phase 0.9: Complexity Check (UNIFIED)
  - Assess expansion scope
  - Apply fast-path
  - Callback mechanism

Phase 0.95: Outline Sufficiency (UNIFIED)
  - Check if outline is execution-ready
  - Skip expansion if yes

Phase 1: Phase-by-Phase Expansion (BIFURCATED)

  [TDD MODE]
  1.1-1.6: Cycle Planning Guidance
    - Cycle numbering (X.Y format)
    - RED specifications (test assertions, expected failure)
    - GREEN specifications (behavior hints, not code)
    - Investigation prerequisites
    - Stop/Error Conditions
    - Dependencies

  [GENERAL MODE]
  1.1-1.3: Script Evaluation
    - Small (≤25): inline script
    - Medium (25-100): prose description
    - Large (>100): separate planning
    - Mandatory conformance validation

  [SHARED]
  - Domain validation skill integration
  - Per-phase review delegation

Phase 1.4: File Size Planning (UNIFIED)
  - Track file growth
  - Plan splits proactively

Phase 2: Assembly and Metadata (UNIFIED)
  - Validate phase files
  - Extract Common Context
  - Prepare metadata
  - (do NOT manually assemble)

Phase 2.5: Consolidation Gate (UNIFIED)
  - Merge trivial work
  - Update metadata

Phase 3: Final Holistic Review (BIFURCATED)

  [TDD MODE]
  - Delegate to tdd-plan-reviewer
  - Cross-phase consistency, prescriptive code, RED/GREEN sequencing

  [GENERAL MODE]
  - Delegate to vet-agent
  - Cross-phase consistency, file paths, requirements

Phase 4: Prepare Artifacts (UNIFIED)
  - Run prepare-runbook.py (auto-detects TDD vs general)
  - Copy orchestrate command to clipboard
  - Tail-call /handoff --commit

Checkpoints: Integration Points (UNIFIED)
  - Light checkpoint (Fix + Functional) every phase
  - Full checkpoint (Fix + Vet + Functional) at boundaries
  - Integration test pattern (xfail → passing)
```

### G3. Shared Sections (No Changes Needed)

These sections should be unified 1:1 with no branching:

1. **Tier Assessment** (lines 61-100 / 35-111) — Identical output format
2. **Outline Generation** (lines 131-182 / 174-218) — Identical components and verifications
3. **Consolidation Gate — Outline** (lines 185-230 / 221-265) — Identical process
4. **Complexity Check Before Expansion** (lines 280-321 / 268-309) — Identical callback logic
5. **Outline Sufficiency Check** (lines 312-335 from adhoc only) — Apply to TDD as well (shortcut for small TDD)
6. **File Size Planning** (lines 324-346 / 455-473) — Identical threshold strategy
7. **Assembly and Metadata** (lines 587-608 / 476-551) — Identical validation and metadata structure
8. **Consolidation Gate — Runbook** (lines 699-753 / 554-611) — Identical merge strategy
9. **Checkpoints** (lines 879-964 / 783-836) — Identical tier strategy
10. **Common Pitfalls** (lines 1099-1127) — Shared anti-patterns

### G4. Conditional Sections (Requires Parameterization)

**Plan-TDD only → Keep as parameterized subsection:**

1. **Cycle Planning Guidance** (3.1-3.6: 412-583)
   - Trigger: `if runbook_type == "tdd"`
   - Contains: Numbering rules, RED specs (prose assertions), GREEN hints (no code), investigation prerequisites, stop conditions
   - Location: Section "Phase 1.1-1.6: Cycle Planning (TDD only)"
   - Reusability: None (TDD-specific)

2. **TDD Review via tdd-plan-reviewer** (Phase 5: 766-777)
   - Trigger: `if runbook_type == "tdd"`
   - Contains: Review scope (prescriptive code, RED/GREEN violations, cross-phase consistency)
   - Reusability: None (references tdd-plan-reviewer agent)

3. **TDD Completion** (orchestrate 6, lines 248-266)
   - Trigger: `if runbook_type == "tdd"`
   - Contains: vet-fix-agent + review-tdd-process delegation
   - Reusability: Reference from orchestrate skill

**Plan-Adhoc only → Keep as parameterized subsection:**

1. **Script Evaluation** (1.1-1.3: 380-431)
   - Trigger: `if runbook_type == "general"`
   - Contains: Size classification (≤25/25-100/>100), step type (transformation/creation)
   - Location: Section "Phase 1.1-1.3: Script Evaluation (General only)"
   - Reusability: None (general-specific)

2. **Mandatory Conformance Validation** (1: 433-451)
   - Trigger: `if design_has_external_reference()`
   - Contains: Reference consumption, validation step generation
   - Reusability: Could apply to TDD (not currently implemented)

3. **Post-assembly Holistic Review** (Point 3: 614-672)
   - Trigger: `if runbook_type == "general"`
   - Contains: Full Task delegation template, revision loop
   - Reusability: Can be unified with TDD final review (both delegate to review agent)

### G5. Unified Detection (prepare-runbook.py)

**Single detection logic handles both:**
- Frontmatter `type: tdd` or `type: general` (default)
- Or infer from headers: `## Cycle X.Y:` (TDD) vs `## Step N:` (general)
- Phase file auto-detection (current implementation, no change needed)

**Single agent generation path:**
- Detects type
- Selects baseline: tdd-task.md (TDD) or quiet-task.md (general)
- Generates step files with uniform naming
- Same orchestrator template (both models + phase metadata)

### G6. Merge Candidates (Clean 1:1 Consolidation)

**These can become unified sections with zero branching:**

1. **Section: "Tier Assessment and Routing"** (combine 61-100 + 35-111)
   - Output format identical
   - All three tiers exist in both skills
   - No TDD-specific language needed

2. **Section: "Outline Generation and Review"** (combine 131-182 + 174-218)
   - Outline structure identical
   - Verification checklist identical
   - Consolidation gate identical
   - runbook-outline-review-agent same for both

3. **Section: "Complexity Management and Fast-Paths"** (combine 280-321 + 268-309 + 312-335)
   - Callback mechanism identical
   - Fast-path logic identical
   - Outline sufficiency check applies to TDD (shortcut feature)

4. **Section: "File Size Awareness"** (combine 324-346 + 455-473)
   - Identical threshold (350 lines, 50-line margin)
   - Same rationale

5. **Section: "Assembly, Metadata, and Artifact Preparation"** (combine 587-608 + 476-551 + Point 4)
   - Identical pre-assembly validation
   - Identical metadata structure
   - Identical prepare-runbook.py invocation
   - Both have identical final sequence

6. **Section: "Checkpoints and Validation"** (combine 879-964 + 783-836)
   - Identical tier strategy (light/full)
   - Identical process (Fix/Vet/Functional)
   - Identical integration test pattern

### G7. Clean Branching Points (Minimal Divergence)

**Only these sections need explicit branching:**

1. **Phase 1 Expansion (split by runbook_type):**
   - TDD: Cycle Planning Guidance (lines 412-583) — Section 3.1-3.6
   - General: Script Evaluation (lines 380-431) — Section 1.1-1.3
   - General: Conformance Validation (lines 433-451) — Section 1 (conditional, could apply to TDD)
   - Both: Domain Validation skill integration (lines 387-401 / 355-369) — Unified

2. **Phase 3 Final Review (split by runbook_type):**
   - TDD: tdd-plan-reviewer agent (lines 766-777)
   - General: vet-agent Task delegation (lines 621-640)
   - Both: Read report, check assessment, fix issues — Unified

3. **orchestrate Completion (split by runbook_type):**
   - TDD: vet-fix-agent + review-tdd-process (lines 248-266)
   - General: Suggest vet-fix-agent review (lines 268-271)

### G8. Implementation Approach

**Create unified `/plan` skill with:**

1. **Single SKILL.md file** (target ~1200 lines, reduced from 2205 by deduplication)
   - Base structure: Tiers, outline, expansion
   - Conditional sections marked with `[TDD MODE]` and `[GENERAL MODE]`
   - Cross-references between sections instead of repetition

2. **Conditional formatting:**
   ```markdown
   ## Phase 1: Expansion

   [TDD MODE]
   Use cycle planning guidance (Section 1.1):
   - Cycle numbering X.Y format
   - [detailed TDD content]

   [GENERAL MODE]
   Use script evaluation (Section 1.1):
   - Size classification
   - [detailed general content]
   ```

3. **Shared agent specs:**
   - tdd-plan-reviewer (keep unchanged)
   - vet-fix-agent (keep unchanged)
   - runbook-outline-review-agent (keep unchanged)
   - quiet-task (keep unchanged)
   - tdd-task (keep unchanged)

4. **Unified prepare-runbook.py** (already unified, no changes needed)
   - Already detects both types
   - Already generates correct artifacts for both

5. **orchestrate updates** (add TDD-type detection):
   - Read runbook type from frontmatter
   - Apply conditional completion logic
   - Phase boundary detection already works for both

---

## H. Gaps in Current Structure

### H1. Missing from Both Skills

1. **Outline → Runbook traceability:** Which outline requirements map to which steps/cycles?
   - Currently: outline-review-agent adds "## Expansion Guidance" to outline
   - Gap: No automatic propagation to runbook or cross-phase review

2. **Model selection guidance per phase:**
   - Both mention haiku/sonnet/opus but lack decision framework
   - Current: Haiku for execution, sonnet for review, opus rare
   - Missing: When to escalate step from haiku to sonnet during planning

3. **Prerequisite validation at execution:**
   - Both specify prerequisites in Common Context
   - Missing: Verification script or execution gate

4. **Conformance validation in TDD:**
   - Plan-adhoc has "Mandatory Conformance Validation" (lines 433-451)
   - Plan-TDD has "Mandatory Conformance Test Cycles" (lines 480-498)
   - Gap: TDD version less detailed on precision requirements

5. **LLM failure mode re-validation after expansion:**
   - Outline is reviewed for vacuity, density, checkpoints
   - Phase expansion can re-introduce defects
   - Currently: tdd-plan-reviewer checks (but per-phase, not holistic re-check of outline requirements)
   - Missing: Cross-phase LLM failure mode detection

---

## I. Unification Benefits

### I1. Maintenance Burden Reduction
- Single source for shared sections (75% of code)
- Bug fixes apply to both automatically
- Pattern updates propagate once

### I2. Consistency Improvements
- Tier assessment identical across both
- Outline structure guaranteed consistent
- Checkpoint strategy unified

### I3. Token Efficiency
- Eliminate redundant explanations
- Cross-reference instead of repeat
- Estimated savings: 400-600 lines (target ~1200 unified vs 2205 current)

### I4. Discovery and Learning
- Single skill easier to navigate than two parallel versions
- Clear branching makes TDD vs general choices explicit
- Gradient from general to TDD (not two separate paths)

### I5. Extensibility
- Adding new runbook type (e.g., exploratory, concurrent) requires single parametrization point
- Review agents can be plugged in per type
- orchestrate handles both uniformly

---

## J. Implementation Roadmap

### Phase 1: Consolidate Shared Sections
1. Create `/plan` skill with unified base
2. Merge Tier Assessment (0% branching)
3. Merge Outline Generation (0% branching)
4. Merge Consolidation Gates (0% branching)

### Phase 2: Add Conditional Logic
1. Mark TDD-specific sections with clear boundaries
2. Mark general-specific sections with clear boundaries
3. Add "runbook_type" parameter to all decision points

### Phase 3: Validate and Test
1. Run both TDD and general workflows against unified skill
2. Verify prepare-runbook.py handles both
3. Verify orchestrate handles both

### Phase 4: Deprecate Originals
1. Update /design to recommend `/plan` (not `/plan-tdd` or `/plan-adhoc`)
2. Migrate existing runbooks to unified format
3. Archive old skills (git history preserves them)

---

## Summary

**Unified skill structure:** 75% shared, 25% conditional

**Merge candidates (0% branching):**
- Tier Assessment
- Outline Generation and Review
- Consolidation Gates (both)
- Complexity Check and Fast-Paths
- File Size Planning
- Assembly and Artifact Preparation
- Checkpoints and Integration Tests

**Conditional sections (requires explicit branching):**
- Phase 1 expansion (Cycle Planning vs Script Evaluation)
- Phase 3 final review (tdd-plan-reviewer vs vet-agent)
- orchestrate completion (TDD-specific steps)

**Key insight:** Both skills implement the same planning workflow. TDD adds cycle structure and RED/GREEN validation. General adds script classification and conformance validation. A single `/plan` skill with conditional sections reduces maintenance burden while preserving specialization.

**Recommended next step:** Create unified `/plan` skill preserving both workflows, then deprecate original `/plan-tdd` and `/plan-adhoc` in favor of the unified entry point.
