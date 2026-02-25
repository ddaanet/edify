# Full Gate Audit — Prose-Only Gates in Skills and Agents

**Date:** 2026-02-25
**Scope:** All `agent-core/skills/*/SKILL.md`, `agent-core/agents/*.md`, `.claude/agents/*.md` (excluding `crew-*`)
**Method:** Each procedural step analyzed for D+B compliance — does a step requiring judgment/decision open with or follow directly from a tool call?

---

## Summary

30 SKILL.md files, 13 agent files, and 5 hand-authored `.claude/agents/` files audited. **12 genuine prose-only gates identified** across 7 files. Most procedural steps are adequately anchored or naturally follow from prior tool output. The majority of apparent "judgment steps" are classification/analysis steps that follow immediately from file content already loaded in the same procedural block.

---

## Findings by File

### 1. `/commit` — `agent-core/skills/commit/SKILL.md`

**Step 1 gate — Vet checkpoint classification:**

```
Classify changed files — production artifacts (code, scripts, plans, skills, agents)?
- No production artifacts? Proceed to validation.
- Trivial? (≤5 net lines, ≤2 files, additive, no behavioral change) Self-review via git diff HEAD.
- Non-trivial? Check for review report in plans/*/reports/ or tmp/.
```

**Status: PROSE-ONLY GATE.**

The step opens with tool calls (`git diff --name-only`, `git status --porcelain`) — so file discovery is anchored. However the **classification of "production artifacts vs non-production"** and the **"trivial vs non-trivial" branch** are pure judgment applied to the diff output with no further tool call. The agent sees the diff, then decides in prose which branch to take. This is a genuine decision gate — the classification determines whether review is required.

**Root cause:** The diff is loaded, but the classification rubric ("production artifacts", "trivial") requires pattern-matching judgment without any structural anchor (e.g., no Grep for known patterns, no script that classifies).

**Fix direction:** Add a Bash step or Grep after the git commands that explicitly searches for known artifact paths (`plans/`, `agent-core/`, `src/`) to ground the "production artifact" classification before the branch decision.

---

### 2. `/handoff` — `agent-core/skills/handoff/SKILL.md`

**Step 1 gate — Uncommitted prior handoff detection:**

```
Uncommitted prior handoff: Read agents/session.md. If it contains prior uncommitted handoff content
(# Session Handoff: header, Completed section, pending tasks not from this conversation), preserve as base state in Step 2
```

**Status: PROSE-ONLY GATE.**

The Read call is specified: `Read agents/session.md`. But the **condition** — "pending tasks not from this conversation" — requires the agent to compare session.md content against the current conversation history. This is a judgment call without a structural anchor. The agent must recognize what constitutes "this conversation" versus prior handoff content, purely from prose reasoning.

**Fix direction:** Add a concrete detection heuristic anchored by a Bash date comparison (e.g., check if the session.md header date differs from today's date), or simplify to: presence of `# Session Handoff:` header = prior handoff exists.

**Step 2 gate — Command derivation for tasks with plan directory:**

```
Command derivation: For tasks with a plan directory, derive the backtick command from the plan's current lifecycle status:
- requirements → /design plans/{name}/requirements.md
...
```

**Status: PROSE-ONLY GATE.**

This classification happens without an explicit tool call to read the plan's current lifecycle status. The agent is expected to infer status from what's already in context (session.md), but for accuracy this requires reading the plan's actual state. For new tasks or tasks where status isn't current in session.md, this is judgment without file confirmation.

**Fix direction:** Add explicit `Bash: claudeutils _worktree ls` before this step to load current plan statuses, anchoring the derivation in actual filesystem state.

---

### 3. `/requirements` — `agent-core/skills/requirements/SKILL.md`

**Mode detection gate:**

```
Heuristic: Scan conversation history before /requirements invocation. If feature/task discussion present → extract mode. Otherwise → elicit mode.
```

**Status: PROSE-ONLY GATE.**

The mode detection is pure conversation-scanning — no tool call anchors it. The agent applies a judgment heuristic ("substantive discussion" vs "minimal context") to conversation history without any structural anchor. This gate determines which of two distinct procedural paths is followed (Extract vs Elicit).

**Mitigating factor:** The skill is explicitly designed for Opus, which has better judgment for this inference. Still a structural gap.

**Fix direction:** Add a file-based signal first: check `plans/<job>/requirements.md` existence before defaulting to conversation scanning. File presence is a stronger signal than conversation inference.

---

### 4. `/design` — `agent-core/skills/design/SKILL.md`

**Triage Recall (D+B anchor) — correctly anchored:**

```bash
agent-core/bin/when-resolve.py "when behavioral code" "when complexity" "when triage" "when <domain-keyword>" ...
```

**Status: ANCHORED.** The design skill explicitly notes this is a D+B anchor and opens with a Bash call. Correctly implemented.

**Post-Outline Complexity Re-check gate:**

```
The outline resolves the architectural uncertainty that justified "complex" classification. Re-assess before continuing ceremony.

Downgrade criteria (all must hold):
- Changes additive, no implementation loops
- No open questions remain
- Scope boundaries explicit (IN/OUT enumerated)
- No cross-file coordination requiring sequencing

If met: Skip A.6. Proceed to Phase B with sufficiency assessment.
```

**Status: PROSE-ONLY GATE.**

This re-assessment follows outline writing, so the outline is in context. But the re-assessment criteria are pure prose judgment with no tool call anchor — "no open questions remain", "scope boundaries explicit" are evaluated by reading the outline already in context. No file read or Bash call opens this decision. The agent applies a multi-criteria judgment that determines whether to skip A.6 entirely.

**Fix direction:** Add `Read plans/<job>/outline.md` as an explicit anchor before this re-assessment block, even though the outline was just written. This creates an explicit tool-call boundary.

**Outline Sufficiency Gate (Phase B exit):**

```
After user validates the outline, assess whether it already contains enough specificity to skip design generation.

Sufficiency criteria (all must hold):
- Approach is concrete (specific algorithm/pattern chosen, not "explore options")
- Key decisions are resolved (no open questions remaining)
- Scope boundaries are explicit (IN/OUT enumerated)
- Affected files are identified
- No architectural uncertainty remains
```

**Status: PROSE-ONLY GATE.**

Immediately after Phase B user discussion, this gate determines whether to skip Phase C entirely. There is no tool call opening this assessment — it's pure judgment on the outline state after user feedback. This is a high-stakes decision (skip Phase C = no formal design document).

**Fix direction:** Add `Read plans/<job>/outline.md` anchor before the sufficiency criteria.

**Direct Execution Criteria gate (C.5):**

```
Design can resolve complexity — a job correctly classified as Complex may produce Simple execution. Assess whether the completed design can be executed directly or needs runbook planning.

Direct execution criteria (all must hold):
- All decisions pre-resolved...
- All changes are prose edits or additive (no behavioral code changes)...
```

**Status: PROSE-ONLY GATE** (partially mitigated).

After Phase C completes, this gate determines whether to execute directly or route to `/runbook`. No tool call opens the assessment — it's judgment on the design document. Note: C.4 does read the design-corrector review report, so design content IS recently loaded. This is borderline but flagged because the decision gate itself has no explicit anchor, and the same pattern appears identically in the Phase B Sufficiency path where no design-corrector read occurs.

**Fix direction:** Make the gate explicitly reference the just-read review report path (anchor via the C.4 Read call) or add a brief `Read plans/<job>/design.md` before the criteria.

---

### 5. `/codify` — `agent-core/skills/codify/SKILL.md`

**Step 1 gate — Eligibility assessment:**

```
Run agent-core/bin/learning-ages.py to get the ages report
Entries ≥7 active days → eligible for consolidation
```

**Status: ANCHORED.** Opens with `agent-core/bin/learning-ages.py` Bash call. The 7-day threshold is applied to script output — numeric, not judgment. Correctly anchored.

**Step 2 gate — File selection routing:**

```
Behavioral rules → agent-core/fragments/*.md: Workflow patterns...
Technical details → agents/decisions/*.md: Architecture...
Implementation patterns → agents/decisions/implementation-notes.md...
Agent templates → agent-core/agents/*.md: Route when learning is actionable for a specific agent role...
```

**Status: PROSE-ONLY GATE.**

After reading the eligible learnings, the agent must decide which target file to route each learning to. This is judgment — no tool call anchors the routing decision. The routing table is a prose heuristic applied without any structural enforcement. The agent applies domain-matching logic ("behavioral" vs "technical" vs "implementation patterns") with no preceding Grep or Read to confirm which domain files contain related content.

**Fix direction:** Add a Grep step searching candidate target files for related headings before routing, anchoring the routing in actual file state rather than domain-matching intuition.

---

### 6. `corrector` — `agent-core/agents/corrector.md`

**Step 0 — Validate Task Scope:**

```
This agent reviews implementation changes, not planning artifacts or design documents.

Runbook rejection: If task prompt contains path to runbook.md:
[return error]
```

**Status: PROSE-ONLY GATE** (low severity).

The task prompt path check is pattern-matching on the incoming task prompt — no tool call anchors it. The agent reads its own task prompt and decides to reject or proceed without verifying file type via any tool.

**Fix direction:** Add a Read of the input file at the start of Step 1, letting file content confirm type rather than relying solely on path parsing.

**Priority:** Low — this is input validation before tool calls begin. If the agent misreads the prompt type, subsequent file reads will surface the actual content.

---

### 7. `design-corrector` — `agent-core/agents/design-corrector.md`

**Step 0 — Validate Document Type:**

```
Before proceeding, verify the document is a design document:
- Filename should be design.md or contain "design" in path
- Content should contain architectural decisions, requirements, or specifications
- Should NOT be a runbook (no ## Step or ## Cycle headers, no YAML type: tdd)
```

**Status: PROSE-ONLY GATE** (low severity).

The content check ("should contain architectural decisions") is judgment without a tool call anchor. The runbook marker check (`## Step` / `## Cycle` headers) could be verified by Grep but isn't.

**Fix direction:** Add `Grep pattern="^## (Step|Cycle)" path=<file>` before this gate to structurally check for runbook markers.

**Step 1.5 — Recall Context:**

```
Recall context: Bash: agent-core/bin/recall-resolve.sh plans/<job-name>/recall-artifact.md
```

**Status: ANCHORED.** Opens with Bash call. Correctly implemented.

---

### 8. `runbook-outline-corrector` — `agent-core/agents/runbook-outline-corrector.md`

**Step 3 — Growth Projection:**

```
For each target file, estimate net new lines added per item from outline descriptions
Formula: current_lines + (items × avg_lines_per_item) — use outline step descriptions to estimate avg_lines_per_item
Flag when projected cumulative size exceeds 350 lines
```

**Status: PROSE-ONLY GATE** (low severity).

"Estimate net new lines" from "outline descriptions" is judgment — no Bash call to `wc -l` on target files grounds the `current_lines` variable. The estimate is derived from prose descriptions without checking actual file sizes.

**Fix direction:** Add `Bash: wc -l <target-files>` for files referenced in the outline before the growth projection step.

**Step 2 — Recall Context:**

```
Recall context: Bash: agent-core/bin/recall-resolve.sh plans/<job>/recall-artifact.md
```

**Status: ANCHORED.**

---

## Well-Anchored Files (No Gates Found)

The following files have no prose-only gates — all judgment steps follow correctly from tool output or are correctly excluded:

- `agent-core/skills/reflect/SKILL.md` — Phase 4.5 explicitly opens with `when-resolve.py`; Phase 2 excluded (context analysis IS the procedure)
- `agent-core/skills/release-prep/SKILL.md` — Every step has explicit tool calls with code blocks
- `agent-core/skills/orchestrate/SKILL.md` — Post-step verification opens with `git status`; design rule comment confirms intentionality
- `agent-core/skills/recall/SKILL.md` — Pass 1 target selection follows from memory-index Read (the Read IS the anchor)
- `agent-core/skills/prioritize/SKILL.md` — Scoring follows from session.md + references reads
- `agent-core/skills/deliverable-review/SKILL.md` — Layer 1 gate driven by inventory script output
- `agent-core/skills/review-plan/SKILL.md` — Recall anchored; Grep specified for all pattern scanning
- `agent-core/agents/outline-corrector.md` — Recall anchored in Step 2; review criteria follow from loaded files
- `agent-core/agents/artisan.md` — Execution only, no judgment gates
- `agent-core/agents/test-driver.md` — All phases have explicit verification tool calls
- `agent-core/agents/refactor.md` — Step 1 explicitly reads quality check output; Step 6 has Bash safety check
- `agent-core/agents/runbook-corrector.md` — Delegates to review-plan skill which is anchored
- `agent-core/agents/runbook-simplifier.md` — Step 1 reads all context explicitly
- `agent-core/agents/tdd-auditor.md` — Step 1 explicitly lists all Bash commands
- `agent-core/agents/scout.md` — Search-only, no judgment gates beyond search itself
- `agent-core/agents/brainstorm-name.md` — Single-purpose, no procedural gates
- `agent-core/agents/hooks-tester.md` — Each test case has explicit tool action specified
- `.claude/agents/hb-p1.md` — First action is explicit Read
- `.claude/agents/runbook-generation-fixes-task.md` — Plan-specific template, common context specifies all checks
- `.claude/agents/quality-infrastructure-task.md` — Plan-specific template
- `.claude/agents/remember-skill-update-task.md` — Plan-specific template
- `.claude/agents/phase-scoped-agents-task.md` — Plan-specific template

**Pure documentation files (no procedural gates):**
- `gitmoji/SKILL.md`, `token-efficient-bash/SKILL.md`, `error-handling/SKILL.md`, `project-conventions/SKILL.md`, `memory-index/SKILL.md`, `plugin-dev-validation/SKILL.md`, `brief/SKILL.md`, `next/SKILL.md`, `shelve/SKILL.md`, `when/SKILL.md`, `how/SKILL.md`, `handoff-haiku/SKILL.md`, `opus-design-question/SKILL.md`, `doc-writing/SKILL.md`, `worktree/SKILL.md`, `ground/SKILL.md`

---

## Consolidated Findings

### Genuine Prose-Only Gates (12 total)

| # | File | Gate | Severity |
|---|------|------|----------|
| 1 | `agent-core/skills/commit/SKILL.md` | Production artifact vs trivial classification after git diff | Medium |
| 2 | `agent-core/skills/handoff/SKILL.md` | "Pending tasks not from this conversation" detection | Low |
| 3 | `agent-core/skills/handoff/SKILL.md` | Command derivation from plan status (no prior status read) | Medium |
| 4 | `agent-core/skills/requirements/SKILL.md` | Extract vs Elicit mode detection (conversation scanning) | Medium |
| 5 | `agent-core/skills/design/SKILL.md` | Post-Outline Complexity Re-check (no tool call opens it) | High |
| 6 | `agent-core/skills/design/SKILL.md` | Outline Sufficiency Gate (no tool call opens it) | High |
| 7 | `agent-core/skills/design/SKILL.md` | Direct Execution Criteria C.5 (no tool call opens it) | Medium |
| 8 | `agent-core/skills/codify/SKILL.md` | Target file routing (domain-matching judgment, no Grep anchor) | Medium |
| 9 | `agent-core/agents/runbook-outline-corrector.md` | Growth Projection (no wc -l of target files) | Low |
| 10 | `agent-core/agents/corrector.md` | Task type validation (prose pattern match on task prompt) | Low |
| 11 | `agent-core/agents/design-corrector.md` | Document type validation (content-based, not Grep-anchored) | Low |
| 12 | `agent-core/skills/design/SKILL.md` | Classification gate (borderline — recall Bash IS the partial anchor) | Low |

---

## Priority Fix List

**High priority (gate determines major routing, no anchor):**

1. `/Users/david/code/claudeutils/agent-core/skills/design/SKILL.md` — Post-Outline Complexity Re-check gate: Add `Read plans/<job>/outline.md` before assessment criteria block
2. `/Users/david/code/claudeutils/agent-core/skills/design/SKILL.md` — Outline Sufficiency Gate (Phase B exit): Add `Read plans/<job>/outline.md` anchor before sufficiency criteria
3. `/Users/david/code/claudeutils/agent-core/skills/design/SKILL.md` — Direct Execution Criteria C.5: Explicitly reference the C.4 design-corrector read, or add `Read plans/<job>/design.md` anchor

**Medium priority (judgment determines branch, partial anchor exists):**

4. `/Users/david/code/claudeutils/agent-core/skills/commit/SKILL.md` — Classify production artifacts: Add Grep for artifact paths (`agent-core/`, `plans/`, `src/`) as structural anchor after git diff
5. `/Users/david/code/claudeutils/agent-core/skills/handoff/SKILL.md` — Command derivation: Add `Bash: claudeutils _worktree ls` before derivation step
6. `/Users/david/code/claudeutils/agent-core/skills/requirements/SKILL.md` — Mode detection: Add Glob/Read of `plans/<job>/requirements.md` existence as primary signal before conversation scanning
7. `/Users/david/code/claudeutils/agent-core/skills/codify/SKILL.md` — File routing: Add Grep targeting candidate domain files before routing decision

**Low priority (input validation, minor):**

8. `/Users/david/code/claudeutils/agent-core/skills/handoff/SKILL.md` — Prior handoff detection: Simplify "not from this conversation" to structural date check
9. `/Users/david/code/claudeutils/agent-core/agents/runbook-outline-corrector.md` — Growth Projection: Add `wc -l` Bash calls for target files
10. `/Users/david/code/claudeutils/agent-core/agents/corrector.md` — Task type validation: Add Read of input file at Step 1 start
11. `/Users/david/code/claudeutils/agent-core/agents/design-corrector.md` — Document type validation: Add `Grep pattern="^## (Step|Cycle)"` before content-based check

---

## Patterns Observed

**Most common gap:** The `/design` skill has 3 routing/sufficiency gates that all rely on loaded outline/design content without an explicit tool call at the decision point. These are all solvable with a Read of the just-written artifact — the pattern is consistent and the fix is mechanical.

**Well-implemented pattern:** The D+B anchor is correctly applied in `reflect` Phase 4.5, `orchestrate` Step 3.3, `design` Triage Recall, and all corrector agent recall steps. These are the reference implementations to follow.

**Borderline cases:** Classification judgment that immediately follows a required tool call (e.g., design triage classification after the recall Bash call) is generally acceptable — the tool output IS the anchor for the judgment. The issue arises when a gate appears without any preceding tool call in its procedural block, or when the preceding tool call is in an earlier named step.

**Not flagged correctly:** Several files initially appeared to have prose-only gates but were correctly excluded: `reflect` Phase 2 (context analysis IS the procedure), `recall` Pass 1 (memory-index Read IS the anchor), `deliverable-review` Layer 1 (script output drives the gate), `orchestrate` Step 3.2 (follows from Task return value). These distinctions matter — over-flagging creates noise that undermines the audit's usefulness.
