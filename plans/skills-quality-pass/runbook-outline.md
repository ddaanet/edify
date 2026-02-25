# Skills Quality Pass — Runbook Outline

**Design:** `plans/skills-quality-pass/design.md`
**Recall:** `plans/skills-quality-pass/recall-artifact.md` (10 keys — resolve via `agent-core/bin/when-resolve.py`)
**Reports:** `plans/skills-quality-pass/reports/skill-inventory.md`, `plans/skills-quality-pass/reports/full-gate-audit.md`

---

## Requirements Mapping

| FR | Description | Phase | Steps | Notes |
|---|---|---|---|---|
| FR-1 | Description tightening (18 skills) | 2, 3, 4, 5 | 2.2, 2.3, 3.1, 3.2, 3.3, 4.2, 5.1, 5.2 | 18 skills across 8 steps |
| FR-2 | Preamble removal (13 skills) | 2, 3, 4, 5 | 2.3, 3.1, 3.2, 3.4, 3.5, 4.2, 4.4, 5.1, 5.2 | 13 skills across 9 steps |
| FR-3 | C/C+ extraction to references/ (5 skills) | 3 | 3.1, 3.2, 3.3, 3.4, 3.5 | ~14 new reference files |
| FR-4 | B-/B trim/extract (5 skills) | 4 | 4.1, 4.2, 4.3, 4.4, 4.5 | ~7 new reference files |
| FR-5 | D+B gate anchoring (12 gates, 7 files) | 1, 2, 4 | 1.1, 2.1, 2.2, 2.3, 3.1, 4.5 | Gates 1-12 per full-gate-audit.md |
| FR-6 | Correctness fixes (3 targeted) | 3, 4, 5 | 3.4, 4.5, 5.2 | orchestrate paths, requirements stale section, worktree CLI |
| FR-7 | Doc update (implementation-notes + memory-index) | — | — | Out of scope — deferred to `/codify` (content in learnings.md line 87, per task constraint) |
| FR-8 | Redundant always-loaded removal (6 skills) | 2, 3, 4, 5 | 2.1, 3.3, 3.4, 4.2, 5.1, 5.2 | 6 skills with fragment duplication |
| FR-9 | Tail section removal (12 skills) | 2, 3, 4, 5 | 2.2, 2.3, 3.3, 3.4, 3.5, 4.2, 4.5, 5.1, 5.2 | 12 skills with redundant tail sections |
| FR-10 | Conditional path extraction (absorbed into FR-3) | 3 | 3.1, 3.2, 3.3, 3.4, 3.5 | Executed jointly with FR-3 per design |

| NFR | Enforcement | Phases | Steps |
|---|---|---|---|
| NFR-1 (control flow correctness) | Steps with conditional-branch skills include path enumeration | 2, 3, 4 | 2.1, 2.2, 2.3, 3.1, 3.4, 4.5 |
| NFR-2 (user reporting correctness) | Same steps verify user-visible output per path | 2, 3, 4 | 2.1, 2.2, 3.1, 3.4, 4.5 |
| NFR-3 (opus for prose) | All steps: opus execution model | 1-5 | All |
| NFR-4 (bootstrapping order) | Phase 1 → restart → Phases 2-5 | 1 | 1.1 (enables all subsequent) |
| NFR-5 (extraction completeness) | Verify trigger + Read for each moved block | 3, 4 | 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3 |
| NFR-6 (description format) | All description edits: "This skill should be used when..." | 2-5 | All FR-1 steps |
| NFR-7 (D+B gate safety) | Gate steps verify no outcome change on existing paths | 1, 2, 3, 4 | 1.1, 2.1, 2.2, 2.3, 3.1, 4.5 |

---

## Key Decisions Reference

- D-1: No optimize-skill skill → design.md
- D-2: Bootstrapping order → design.md (NFR-4 enforcement)
- D-3: Description format preservation → design.md (NFR-6 enforcement)
- D-4: Progressive disclosure targets → design.md + grounding report compression budgets
- D-5: Control flow verification → design.md (NFR-1/NFR-2 enforcement)
- D-6: Gate fix pattern → design.md (tool call → prose judgment → if/then)

---

## Phase Structure

### Phase 1: Agent D+B gates — bootstrap (type: general, model: opus)

**Complexity:** Low — 3 surgical insertions across 3 files
**Rationale:** NFR-4 mandates fixing corrector agents before skills reviewed by those agents.

- Step 1.1: Fix agent D+B gates (3 agents, gates 9-11)
  - `agent-core/agents/corrector.md` — gate 10: Add Read of input file path at Step 1 before task-type validation
  - `agent-core/agents/design-corrector.md` — gate 11: Add `Grep pattern="^## (Step|Cycle)" path=<file>` before document type validation
  - `agent-core/agents/runbook-outline-corrector.md` — gate 9: Add `Bash: wc -l <target-files>` before growth projection in Step 3
  - **NFR-7 check:** Verify each insertion produces data for existing judgment — does not introduce new decision criteria
  - **Verification:** Read each modified file, trace control flow, confirm no path changes

**Checkpoint:** Light — `just dev`, functional check
**Post-phase:** Session restart required. Agent definitions modified — Claude Code caches agent content aggressively. Without restart, corrector agents may execute from stale cached versions.

---

### Phase 2: Skill D+B gates + light fixes (type: general, model: opus)

**Depends on:** Phase 1 + session restart
**Complexity:** Medium — 5 D+B gates across 3 skills, plus FR-1/2/8/9 per file (prose atomicity)
**Rationale:** These skills need D+B gates and light-touch edits but not body surgery.

- Step 2.1: commit skill (gate 4, FR-8)
  - `agent-core/skills/commit/SKILL.md` (151 lines)
  - Gate 4: Add Grep for artifact paths (`agent-core/`, `plans/`, `src/`) after git diff, before production artifact classification
  - FR-8: Remove secrets rule that restates always-loaded fragment (identify, confirm redundancy with fragment, remove)
  - **NFR-7 check:** Grep output feeds existing classification rubric — no new criteria
  - **NFR-1 check:** commit has conditional branches (trivial/non-trivial/no-production) — enumerate paths, verify each

- Step 2.2: handoff skill (gates 5+8, FR-1, FR-9)
  - `agent-core/skills/handoff/SKILL.md` (163 lines)
  - Gate 5: Add `Bash: claudeutils _worktree ls` before command derivation step
  - Gate 8: Simplify prior handoff detection to structural date check (presence of `# Session Handoff:` header with date ≠ today)
  - FR-1: Tighten description — sharper triggers, less verbose, third-person
  - FR-9: Remove redundant tail sections (Additional Resources / Integration)
  - **NFR-7 check:** `_worktree ls` output feeds existing derivation table — no new criteria. Date check simplifies judgment (narrows, doesn't expand)
  - **NFR-1 check:** handoff has conditional branches (prior handoff / no prior) — enumerate, verify

- Step 2.3: codify skill (gate 7, FR-1, FR-2, FR-9)
  - `agent-core/skills/codify/SKILL.md` (170 lines)
  - Gate 7: Add Grep searching candidate domain files for related headings before file routing decision
  - FR-1: Tighten description
  - FR-2: Remove "When to Use" preamble, fold counter-conditions into description
  - FR-9: Remove redundant tail sections
  - **NFR-7 check:** Grep output grounds existing routing table — no new routes added

**Checkpoint:** Light — `just dev`, functional check

---

### Phase 3: C/C+ body surgery (type: general, model: opus)

**Depends on:** Phase 1 + session restart
**Complexity:** High — 5 major extractions creating ~14 new reference files, 4 D+B gates, description/preamble/tail work
**Rationale:** Largest compression opportunity (~970 lines removable). Prose atomicity: all FRs per skill in one step.

- Step 3.1: design skill (gates 1-3+12, FR-1, FR-2, FR-3, FR-10)
  - `agent-core/skills/design/SKILL.md` (521 lines → ~371)
  - Create `agent-core/skills/design/references/` directory
  - Gate 1: Add `Read plans/<job>/outline.md` before Post-Outline Complexity Re-check
  - Gate 2: Add `Read plans/<job>/outline.md` before Outline Sufficiency Gate (Phase B exit)
  - Gate 3: Add `Read plans/<job>/design.md` before Direct Execution Criteria C.5
  - Gate 12: Add `Glob agent-core/skills/*/SKILL.md` or behavioral-code Grep to classification gate
  - FR-1: Tighten description
  - FR-2: Remove "When to Use" preamble
  - FR-3 + FR-10: Extract to references/:
    - Research protocol (A.3-5) → `references/research-protocol.md`
    - Discussion protocol (B) → `references/discussion-protocol.md`
    - C.1 content rules → `references/design-content-rules.md`
    - Remove A.1 clarification paragraphs
    - Remove binding constraints + output expectations tails
  - Leave trigger + Read instruction in body for each extracted section
  - **NFR-1/NFR-2 (D-5):** Design skill has complex conditional branches (Simple/Moderate/Complex routing, phase gates). Enumerate ALL execution paths before editing. After editing, verify user-visible output (classification blocks, routing messages) on each path.
  - **NFR-5:** Verify each references/ file has a load point in SKILL.md body

- Step 3.2: runbook skill (FR-1, FR-2, FR-3, FR-10)
  - `agent-core/skills/runbook/SKILL.md` (1027 lines → ~677)
  - Existing `references/` has 5 files; add 3 new
  - FR-1: Tighten description
  - FR-2: Remove "When to Use" preamble
  - FR-3 + FR-10: Extract to references/:
    - Tier 3 planning phases 0.5–3.5 → `references/tier3-planning-process.md`
    - TDD Cycle Planning Guidance → `references/tdd-cycle-planning.md`
    - Conformance Validation → `references/conformance-validation.md`
    - Unify duplicate consolidation gates (phases 0.85 and 2.5) during extraction
  - Leave trigger + Read instruction in body for each extracted section
  - **NFR-5:** Verify each new references/ file has a load point

- Step 3.3: token-efficient-bash skill (FR-1, FR-3, FR-8, FR-9, FR-10)
  - `agent-core/skills/token-efficient-bash/SKILL.md` (523 lines → ~323)
  - Create `agent-core/skills/token-efficient-bash/references/` directory
  - FR-1: Tighten description
  - FR-3 + FR-10: Extract to references/:
    - 3 worked examples → `references/examples.md`
    - Anti-patterns → `references/anti-patterns.md`
    - Directory changes → `references/directory-changes.md`
  - FR-8: Reconcile with error-handling fragment — remove duplicated content
  - FR-9: Remove token economy before/after comparison, Summary tail
  - Leave trigger + Read for each extracted section
  - **NFR-5:** Verify load points

- Step 3.4: orchestrate skill (FR-2, FR-3, FR-6, FR-8, FR-9, FR-10)
  - `agent-core/skills/orchestrate/SKILL.md` (521 lines → ~391)
  - Create `agent-core/skills/orchestrate/references/` directory
  - FR-2: Remove "When to Use" preamble
  - FR-3 + FR-10: Extract to references/:
    - Common Scenarios → `references/common-scenarios.md`
    - Continuation protocol → `references/continuation.md`
    - Condense Weak Orchestrator Pattern rationale (inline, not extracted)
    - Extract progress tracking detail → `references/progress-tracking.md`
  - FR-6: Replace absolute paths with relative in References section
  - FR-8: Remove escalation rule that restates always-loaded fragment
  - FR-9: Remove redundant tail sections
  - **NFR-1 check:** orchestrate has conditional paths (continuation, error handling) — verify after edits

- Step 3.5: review skill (FR-2, FR-3, FR-9, FR-10)
  - `agent-core/skills/review/SKILL.md` (384 lines → ~244)
  - Create `agent-core/skills/review/references/` directory
  - FR-2: Remove "When to Use" preamble
  - FR-3 + FR-10: Extract to references/:
    - Analyze Changes 10-category checklist → `references/review-axes.md`
    - Common Scenarios → `references/common-scenarios.md`
    - Example Execution → `references/example-execution.md`
    - Remove security section that duplicates system-level guidance
  - FR-9: Remove redundant tail sections
  - Leave trigger + Read for each extracted section
  - **NFR-5:** Verify each references/ file has a load point

**Checkpoint:** Full — `just dev`, then opus `/deliverable-review` of each restructured SKILL.md against design compression targets and NFR-5 extraction completeness (5 skills)

---

### Phase 4: B-/B trim/extract (type: general, model: opus)

**Depends on:** Phase 1 + session restart
**Complexity:** Medium — 5 skills with moderate extraction/trimming, 1 D+B gate
**Rationale:** Smaller compression than Phase 3 but still significant restructuring.

- Step 4.1: review-plan skill (FR-4)
  - `agent-core/skills/review-plan/SKILL.md` (587 lines → ~487)
  - Create `agent-core/skills/review-plan/references/` directory
  - Extract violation/correct examples → `references/review-examples.md`
  - Extract output format template → `references/report-template.md`
  - Remove Key Principles tail section
  - Leave trigger + Read for each extracted section
  - **NFR-5:** Verify each references/ file has a load point

- Step 4.2: reflect skill (FR-1, FR-2, FR-4, FR-8, FR-9)
  - `agent-core/skills/reflect/SKILL.md` (304 lines → ~234)
  - Existing `references/` has 2 files; add 2 new
  - FR-1: Tighten description
  - FR-2: Remove "When to Use" preamble
  - FR-4: Extract to references/:
    - Key Design Decisions → `references/rca-design-decisions.md`
    - Examples → `references/rca-examples.md`
  - FR-8: Remove Integration section that restates always-loaded content
  - FR-9: Remove redundant tail sections
  - Leave trigger + Read for each extracted section

- Step 4.3: plugin-dev-validation skill (FR-4)
  - `agent-core/skills/plugin-dev-validation/SKILL.md` (528 lines → ~408)
  - Create `agent-core/skills/plugin-dev-validation/references/` directory
  - Extract Good/Bad Examples per artifact type → `references/examples-per-type.md`
  - Remove Alignment Criteria section (duplicates review criteria)
  - Remove Usage Notes tail section
  - Leave trigger + Read for extracted section
  - **NFR-5:** Verify references/ file has a load point

- Step 4.4: shelve skill (FR-2, FR-4)
  - `agent-core/skills/shelve/SKILL.md` (136 lines → ~81)
  - FR-2: Remove "When to Use" preamble
  - FR-4:
    - Remove 40-line Example Interaction (models "I'll help you..." register — sycophantic pattern)
    - Condense Critical Constraints section

- Step 4.5: requirements skill (FR-4, FR-5 gate 6, FR-6, FR-9)
  - `agent-core/skills/requirements/SKILL.md` (278 lines → ~213)
  - Existing `references/` has 1 file
  - Gate 6: Add Glob/Read of `plans/<job>/requirements.md` as primary signal before Extract vs Elicit mode detection (conversation scanning becomes fallback)
  - FR-4: Unify extract/elicit shared steps; condense Key Principles table
  - FR-6: Remove stale "Integration Notes" section
  - FR-9: Remove redundant tail sections
  - **NFR-7 check:** Glob result feeds mode detection — file exists → extract, absent → elicit (conversation scan). Existing heuristic preserved as fallback.
  - **NFR-1 check:** requirements has Extract/Elicit branching — verify both paths after gate addition

**Checkpoint:** Light — `just dev`, functional check

---

### Phase 5: Light-touch batch (type: general, model: opus)

**Depends on:** Phase 1 + session restart
**Complexity:** Low per file — mechanical description/preamble/tail edits across 15 skills
**Rationale:** Identical operation pattern (read → apply applicable FRs → verify). Batched with variation table.

- Step 5.1: Batch A — 8 skills

  | Skill | FR-1 | FR-2 | FR-8 | FR-9 | Notes |
  |---|---|---|---|---|---|
  | error-handling | ✓ | | ✓ | | FR-8: Assess if skill adds value beyond fragment. If entirely redundant, reduce to redirect stub or remove. |
  | gitmoji | ✓ | ✓ | | ✓ | |
  | ground | ✓ | | | ✓ | |
  | how | ✓ | | | | |
  | when | ✓ | | | | |
  | memory-index | ✓ | | | | |
  | next | ✓ | ✓ | | | |
  | prioritize | ✓ | | | ✓ | |

  **Per-skill operation:**
  1. Read SKILL.md
  2. FR-1: Rewrite description frontmatter — tighter triggers, third-person, within "This skill should be used when..." format (NFR-6)
  3. FR-2: Delete "When to Use" / "When NOT to Use" section. Fold any counter-conditions into description
  4. FR-8: Confirm redundancy with source fragment, remove duplicated content
  5. FR-9: Delete "Additional Resources" / "Integration" / "Summary" / "Key Principles" tail sections that restate body or obvious workflow position
  6. Verify no content loss (extracted → body retains trigger + Read; deleted → truly redundant)

- Step 5.2: Batch B — 7 skills

  | Skill | FR-1 | FR-2 | FR-6 | FR-8 | FR-9 | Notes |
  |---|---|---|---|---|---|---|
  | recall | ✓ | | | | | |
  | deliverable-review | ✓ | ✓ | | | ✓ | |
  | doc-writing | ✓ | ✓ | | | | |
  | release-prep | | ✓ | | | ✓ | |
  | worktree | ✓ | | ✓ | | | FR-6: Replace `list_plans(Path('plans'))` with `claudeutils _worktree ls` in Mode B step 1 |
  | handoff-haiku | | ✓ | | ✓ | | FR-8: Task metadata format restates execute-rule.md |
  | opus-design-question | | ✓ | | | | |

  Same per-skill operation as Step 5.1.

**Checkpoint:** Full — `just dev`, then opus spot-check review of 3-4 representative skills from each batch (verify NFR-6 description format, no content loss from FR-9 tail removal)

---

## Expansion Guidance

**All phases are general type with opus execution.** No TDD phases — no behavioral code changes, so no tests needed.

**Prose atomicity enforced:** Every step that modifies a skill file includes ALL applicable FRs for that file. No skill is touched in multiple steps.

### Execution Model: Parallel Agents

**Phase 1** executes alone (bootstrap + restart). After restart, **4 background opus agents** run in parallel — all file sets are disjoint:

| Agent | Phase | Steps | Files |
|---|---|---|---|
| A | 2 | 2.1-2.3 | commit, handoff, codify (3 skills) |
| B | 3 | 3.1-3.5 | design, runbook, token-efficient-bash, orchestrate, review (5 skills + ~14 new references/) |
| C | 4 | 4.1-4.5 | review-plan, reflect, plugin-dev-validation, shelve, requirements (5 skills + ~7 new references/) |
| D | 5 | 5.1-5.2 | 15 light-touch skills |

**Within each agent:** Steps execute sequentially — context accumulates (file reads persist, recall loaded once). No re-reading between steps.

### Recall Injection

**All dispatched agents** (execution AND review) receive recall context in their prompt:

**Execution agents (A-D):** First action before any step work:
1. Read `plans/skills-quality-pass/recall-artifact.md` to get entry keys
2. Run `agent-core/bin/when-resolve.py` with all 10 keys in a single batch call
3. Carry resolved content as context for all subsequent steps

**Review agents** (corrector at checkpoints, `/deliverable-review`): Same recall resolution instruction in dispatch prompt. Recall enables project-specific review criteria (D+B safety patterns, format preservation, control flow regression).

### Baked Learnings

Two learnings from `agents/learnings.md` are not yet in decision files and cannot be resolved via `when-resolve.py`. Include verbatim in every agent dispatch prompt:

**Skill editing constraints** (learnings.md lines 83-88):
- Platform constraint: skill `description` frontmatter MUST use "This skill should be used when..." format
- Extraction safety: every content block moved to references/ must leave a trigger condition + Read instruction in the main SKILL.md body. Verify each references/ file has a corresponding load point.
- Control flow verification: after restructuring skills with conditional branches, enumerate all execution paths and verify user-visible output on each path. Prior deslop on design skill combined two fast paths and regressed user-facing classification message.
- D+B gate additions: adding tool calls to anchor prose-only gates must not change the gate's decision outcome on existing paths.

**Model selection for discovery/audit** (learnings.md lines 79-82):
- Sonnet minimum for any discovery/audit touching skills, agents, or fragments. These are architectural prose artifacts — assessing their quality requires the same judgment tier as editing them.

**Agent lifecycle:** Resume agents until observable quality degradation (wrong file references, stale content, tool call failures). Do NOT use a fixed token threshold — context size is a proxy, quality is the signal.

**Checkpoints after convergence:** When all 4 agents complete, run aggregate checkpoint: `just dev` + opus `/deliverable-review` sampling skills from each agent's file set (verify NFR-1 control flow, NFR-5 extraction completeness, NFR-6 description format).

### Content Guidance

**Phase 5 expansion:** Expand as 2 batched steps with variation tables (shown above). Each step's body repeats the per-skill operation pattern; the table provides per-skill FR applicability. The opus agent reads all skills in the batch, applies applicable FRs sequentially, verifies each.

**D+B gate pattern (D-6):** All gate fixes follow: add tool call producing output → existing prose judgment operates on that output → if/then with branch targets. The tool call IS the anchor. Judgment following loaded data is acceptable.

**Control flow verification (D-5):** Required for skills with conditional branches after restructuring. Applies to: design (Step 3.1), commit (Step 2.1), handoff (Step 2.2), codify (Step 2.3), orchestrate (Step 3.4), requirements (Step 4.5). Each step must enumerate paths before and verify after.

**Description format (D-3, NFR-6):** All description rewrites retain "This skill should be used when..." format. Improve wording within format: tighter triggers, remove verbose preamble, ensure third-person. Do NOT replace with noun phrases.

**References file convention:** New references/ files should follow existing project patterns (see `agent-core/skills/runbook/references/` for examples). Each extracted file gets a clear filename, H1 header matching content, and the source SKILL.md retains a trigger condition + Read instruction pointing to the reference.

**error-handling skill contingency (Step 5.1):** The 20-line skill may be entirely redundant with the always-loaded fragment. If assessment confirms full redundancy, reduce body to a 1-line redirect ("See agent-core/fragments/error-handling.md") rather than delete (preserves the description entry for skill discovery).

## Weak Orchestrator Metadata

**Total Steps:** 16 (1 bootstrap + 15 parallel across 4 agents)
**Execution Model:** Opus for all steps (NFR-3: architectural artifacts)
**Step Dependencies:** Phase 1 → restart → Phases 2-5 in parallel (4 background opus agents, disjoint file sets).
**Error Escalation:** Opus → User (single model tier, no lower-model fallback)
**Report Locations:** `plans/skills-quality-pass/reports/`
**Success Criteria:** All 30 skills pass `just precommit`; FR-1 through FR-10 (except FR-7, deferred to `/codify`) addressed per requirements mapping; no control flow regressions in conditional-branch skills.
**Checkpoints:** Light after Phase 1 (pre-restart). Per-phase checkpoints per outline. Aggregate full checkpoint after all 4 agents converge: `just dev` + opus `/deliverable-review` sampling across all phases.

**Prerequisites:**
- Design document complete (✓ `plans/skills-quality-pass/design.md`)
- Scout reports available (✓ `plans/skills-quality-pass/reports/skill-inventory.md`, `full-gate-audit.md`)
- Grounding report available (✓ `plans/reports/skill-optimization-grounding.md`)
- plugin-dev:skill-development loaded (✓ documentation perimeter requirement)
