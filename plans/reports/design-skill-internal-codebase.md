# Design Skill Internal Codebase Research

**Date:** 2026-02-25
**Method:** File inspection + git history mining + decision file analysis
**Scope:** `/design` skill process structure, failure patterns, evidenced corrections

---

## Summary

The `/design` skill is the highest-leverage ungrounded workflow skill, gating all downstream work. It has accumulated 8+ structural patches since initial creation — each patch responding to a concrete failure mode observed in production. The current structure reflects accumulated fixes rather than principled architecture, which is precisely what grounding is intended to address. The grounding audit (workflow-grounding-audit.md) explicitly notes it as the highest-priority target.

---

## Current Design Skill Structure

**Source:** `/Users/david/code/claudeutils/.claude/skills/design/SKILL.md`

### Phase 0: Complexity Triage

Four distinct sub-steps, each a structural patch:

**Requirements-clarity gate (pre-triage)**
- Before any artifact reading, validate requirements are actionable
- `requirements.md` exists → verify each FR/NFR has concrete mechanism
- User request only → verify intent is clear enough
- Vague/mechanism-free → route to `/requirements`

**Artifact check**
- Read `plans/<job-name>/` for existing artifacts
- `design.md` exists → route directly to `/runbook`
- `outline.md` sufficient → skip to Phase B
- `outline.md` insufficient → resume from A.5 or A.6
- Otherwise → classify

**Triage Recall (D+B anchor)**
```bash
plugin/bin/when-resolve.py "when behavioral code" "when complexity" "when triage" "when <domain-keyword>" ...
```
- This tool call is a *structural anchor* — prevents classification from being skipped or rationalized away
- Derives domain keywords from task/problem description

**Classification Criteria**
- Complex: architectural decisions, multiple valid approaches, uncertain requirements, significant codebase impact
- Moderate: clear requirements, no architectural uncertainty; behavioral code changes (new functions, changed logic, conditional branches)
- Simple: single file, obvious implementation, no architectural decisions — **no behavioral code changes** (this qualification is a D+B patch)

**Classification Gate (second D+B anchor)**
- Glob or Grep on affected files to confirm whether behavioral code changes are involved
- Produces visible output block before routing (not internal reasoning)

**Routing**
- Simple → check skills/recipes first, skip design
- Moderate → skip design, route to `/runbook`
- Complex → Phases A-C

**Companion tasks rule (structural patch from e1a35cd1)**
- Each companion task bundled into /design invocation gets its own Phase 0 pass
- The /design invocation is the venue; process is not optional per companion task

**Session state check:** if >5 pending tasks, suggest `/shelve`

### Phase A: Research + Outline

**A.0 Requirements Checkpoint**
- Read and summarize requirements.md if present
- Skill dependency scan: requirements mentioning agents/skills/hooks/plugins → load plugin-dev:* skill immediately (anti-pattern: deferring to A.1)

**A.1 Documentation Checkpoint (5-level hierarchy)**
1. Local knowledge: memory-index, when-resolve.py, agents/decisions/*.md, plan-archive
2. Key skills: plugin-dev:* when touching plugin components
3. Context7: library docs — direct from main session (not in sub-agents)
4. Local explore: delegate to scout agent
5. Web research: WebSearch/WebFetch

**Recall Artifact Generation (A.1 output)**
- Write `plans/<job>/recall-artifact.md` after documentation loading
- Structured markdown, one section per entry with source + relevance + key excerpt
- Curated (not exhaustive) — only entries that informed design decisions
- Rationale: documentation findings in context window don't survive to downstream pipeline stages (runbook, orchestration, execution, review)

**A.2 Explore Codebase**
- Delegate when scope is open-ended or spans >3 unknown files
- Read directly when files are known and few (≤3)
- Scout agent writes to `plans/<job-name>/reports/explore-<topic>.md`

**A.3-5 Research and Outline**
- External research protocol in `references/research-protocol.md`
- Recall diff: `plugin/bin/recall-diff.sh <job-name>` before outline production
- Outline content: approach, key decisions, open questions, scope boundaries
- Escape hatch: if user input already specifies approach+decisions+scope, compress A+B into single validation message

**Post-Outline Complexity Re-check (structural patch from 41a4b163)**
- Read `plans/<job>/outline.md` to ground re-assessment
- Downgrade criteria (all must hold): additive changes, no loops, no open questions, explicit scope, no cross-file sequencing
- If met: skip A.6, proceed to Phase B sufficiency assessment
- If not met: continue to A.6

**A.6 FP-1 Checkpoint: Review Outline**
- Delegate to `outline-corrector` (Task tool)
- outline-corrector applies all fixes directly, writes review report
- Handle ESCALATION if unfixable issues noted

### Phase B: Iterative Discussion

**Protocol in `references/discussion-protocol.md`:**
- Open outline for user review
- User provides feedback; designer applies deltas to outline.md (not inline conversation)
- Re-review via outline-corrector after changes
- Loop until user validates
- If 3 rounds without convergence: ask whether to proceed or restart with different constraints
- If feedback fundamentally changes approach: restart Phase A

**Outline Sufficiency Gate (structural patch from 98790750)**
- Read outline to ground assessment
- Sufficiency criteria (all must hold): concrete approach chosen, key decisions resolved, explicit scope IN/OUT, affected files identified, no architectural uncertainty remaining
- If sufficient: confirm with user, assess execution readiness

**Execution Readiness Gate (structural patch from 785687cb)**
- Criteria: all decisions pre-resolved, all changes prose/additive, insertion points identified, no cross-file coordination, no implementation loops
- If execution-ready: execute inline, delegate to corrector, invoke `/handoff [CONTINUATION: /commit]`
- If not execution-ready: route to `/runbook`

### Phase C: Generate Design

**C.1 Create Design Document**
- Recall diff before writing
- Content rules in `references/design-content-rules.md`
- Output: `plans/<job-name>/design.md`

**C.2 Checkpoint Commit (structural patch from 4c93a35f)**
- Commit design.md before review
- Rationale: preserves design state, enables diffing, isolates review changes

**C.3 Review Design**
- Delegate to `design-corrector` (opus model)
- Includes recall-artifact review entries in corrector prompt

**C.4 Check for Unfixable Issues**
- design-corrector applies all fixes directly
- Step handles residual UNFIXABLE issues only

**C.5 Execution Readiness and Handoff**
- Read design.md to ground assessment
- Same execution readiness criteria as sufficiency gate
- Route to direct execution or `/runbook`

### Constraint Section

- High-capability model only
- Delegate exploration (cost/context management)
- Dense output
- Classification tables are constraints (not guidelines) — planners must follow literally

---

## Reference Files

**`references/research-protocol.md`** — A.3-A.5 protocol
- Context7 called directly from main session (unavailable in sub-agents)
- Grounding invocation rule: methodology/framework/scoring/taxonomy designs must invoke `/ground`
- Recall diff before outline output

**`references/discussion-protocol.md`** — Phase B protocol
- Plugin-topic detection reminder during discussion
- Convergence: 3-round limit before asking to proceed or restart

**`references/design-content-rules.md`** — Phase C.1 content rules
- Density checkpoint (>8 items/phase or <100 LOC total → restructure)
- Repetition helper prescription (5+ operations on same pattern → extract helper)
- Agent-name validation (Glob agent directories before finalizing design)
- Late-addition completeness check (post-outline-review FRs need re-validation)
- Classification tables are binding
- TDD mode additions: spike test strategy, Diamond Shape integration-first
- References section (backward-looking provenance)
- Documentation Perimeter section (forward-looking: what planner must read)
- Skill-loading directives for plugin-related topics
- Execution model directives (opus for workflow/skill/agent edits)

---

## Failure Patterns Evidenced in Git History

### 1. Classification Primacy Bias + Skipping Recall (e1a35cd1, 2026-02-24)

**Commit:** `🤖 Restructure design skill triage with 4 structural fixes`

**Failures addressed:**
- Classification listed Simple→Moderate→Complex, causing primacy bias toward Simple
- Triage recall was prose-only gate — agents rationalized skipping it
- Classification Criteria, Gate, and Routing were interleaved — not cleanly separated
- Companion tasks bundled into /design invocations were treated as exempt from Phase 0 process

**Fixes applied:**
- Reordered to Complex→Moderate→Simple (prevents primacy toward Simple)
- Added D+B anchor: `when-resolve.py` call before classification (structural, unskippable)
- Separated Classification Criteria / Gate / Routing as distinct sections
- Added companion task rule: each bundled task gets own Phase 0 pass

**Learning captured:** "When companion tasks bundled into /design invocation" — agent treats companion work as exempt from design process, rationalizes skip based on "well-specified from prior RCA"

### 2. Prose-Only Recall Gates Rationalized Away (multiple commits, culminating 59904514)

**Commit:** `🤖 Anchor recall gates with when-resolve.py in /reflect and /runbook`

**Pattern:** Prose gates ("Read X (skip if already in context)") consistently fail. Agents rationalize the skip condition by substituting related activity for the specific required action.

**Applied to /design:** D+B anchor in triage and classification gate — tool calls that prove work happened, cannot be skipped without visible evidence.

**Learning captured:** "When recall gate has skip condition" — escape hatch IS the failure mode. Anchor with tool call that proves work happened: `when-resolve.py` is the gate.

### 3. Ceremony Momentum After Complexity Resolves (41a4b163, 2026-02-18)

**Commit:** `🤖 Add design skill complexity gates and review runbook evolution outline`

**Failure:** One-shot complexity triage at `/design` entry, no re-assessment when outline resolves architectural uncertainty. Process continues at "complex" even when outline reveals 2-file prose edits.

**Evidence:** outline-corrector + design.md + design-corrector cost ~112K tokens for work that could have been done inline.

**Fix:** Post-outline complexity re-check gate. If all downgrade criteria met: skip A.6, proceed to Phase B with sufficiency assessment.

**Decision captured:** `agents/decisions/workflow-optimization.md` — "When design ceremony continues after uncertainty resolves"

### 4. Always Routing to /runbook After Design (785687cb, 2026-02-18; 98790750, 2026-02-16)

**Commits:** `🤖 Add execution readiness gate to design skill`, `🤖 Update deliverable-review and design skills`

**Failure:** Complex design classification persists through pipeline even when design resolves the uncertainty. Every job routed to /runbook regardless of actual execution complexity.

**Evidence:** Error-handling runbook used 11 opus agents for ~250 lines of prose; runbook-corrector caught a regression *introduced* by the generation process itself.

**Fix:** Execution readiness gate at sufficiency gate and C.5. All-prose phases with no feedback loop → execute inline from design outline.

**Decision captured:** "When design resolves to simple execution" — updated to replace ≤3 files heuristic with coordination complexity discriminator (2026-02-19).

### 5. Simple Triage Bypassing Safety Checks (7df2529f, 2026-02-15)

**Commit:** `🤖 RCA: design skill "execute directly" bypasses safety checks`

**Failure:** Simple triage path directly executed without checking for applicable skills and project recipes first.

**Fix:** Simple routing now checks skills/recipes before executing. All other operational rules (skills, project tooling, communication) remain in effect even on Simple path.

### 6. Behavioral Code Misclassified as Simple (workflow-planning.md, 2026-02-21)

**Decision:** "When triaging behavioral code changes as simple"

**Failure:** Assessing complexity from conceptual simplicity ("just read a config file") rather than structural criteria. Resolving ambiguity downward due to implementation eagerness.

**Root cause chain:** Motivated reasoning → resolved ambiguity downward → Simple path had no test gate → behavioral code shipped untested.

**Fix in current skill:** Explicit behavioral code check in classification gate with D+B anchor (Glob/Grep to confirm). Classification block must produce visible output showing the check result.

### 7. Skill Dependency Loading Deferred (dfa0d953, 2026-02-05)

**Commit:** `🔧 Add restart triggers and skill dependency scan`

**Failure:** When requirements explicitly mentioned agent/skill/hook creation, skill loading was deferred to A.1 judgment rather than immediate load at A.0.

**Fix:** A.0 now scans requirements for skill dependency indicators and loads immediately.

### 8. Design Agent Reference Names Not Verified (workflow-execution.md, 2026-02-15)

**Decision:** "When design references need verification"

**Failure:** Opus review missed `outline-corrector` vs `runbook-outline-corrector` — two distinct agents with different purposes.

**Fix in design-content-rules.md:** Agent-name validation step — Glob agent directories, every agent name in design must resolve to actual file.

### 9. Late-Added Requirements Bypass Validation (workflow-planning.md, 2026-02-15)

**Decision:** "When requirements added after review"

**Failure:** FR-18 added during design session bypassed outline-level validation, resulting in mechanism-free specification that downstream planners could not implement.

**Fix in design-content-rules.md:** Late-addition completeness check — post-outline-review FRs need re-validation for traceability and mechanism specification.

### 10. Checkpoint Commit Missing Before Review (4c93a35f, 2026-02-07)

**Commit:** `🤖 Update design skill: checkpoint, vet wording, opus directive`

**Failure:** Design document reviewed without prior commit meant review changes weren't isolatable in git history.

**Fix:** C.2 checkpoint commit step added between C.1 (write design) and C.3 (review).

---

## Learnings Applicable to Design Process

From `/Users/david/code/claudeutils/agents/learnings.md`:

**"When companion tasks bundled into /design invocation"**
- Anti-pattern: Agent treats companion work as exempt from design process — no recall, no skill loading, no classification gate. Rationalizes "well-specified from prior RCA" to skip all process steps.
- Correct: Each companion task gets its own Phase 0 pass. /design invocation is the venue, process is not optional.

**"When recall gate has skip condition"**
- Anti-pattern: "Read X (skip if already in context)" — agent rationalizes skip condition without verifying, substitutes related activity for required Read.
- Correct: Anchor recall with tool call that proves work happened. `when-resolve.py` is the gate.

**"When selecting model for discovery and audit"**
- Anti-pattern: Using haiku scouts to audit prose quality or detect structural anti-patterns.
- Correct: Sonnet minimum for discovery/audit touching skills, agents, or fragments.

**"When dispatching parallel agents with shared recall"**
- Anti-pattern: Each parallel agent independently resolves same recall artifact keys.
- Correct: Pre-resolve recall to shared file before dispatch.

From `agents/decisions/workflow-optimization.md`:

**"When design ceremony continues after uncertainty resolves"**
- One-shot complexity triage with no re-assessment. Fix: two gates (entry + post-outline).

**"When design resolves to simple execution"**
- Always routing to /runbook even when design resolves complexity. Fix: execution readiness gate.

From `agents/decisions/workflow-planning.md`:

**"When triaging behavioral code changes as simple"**
- Conceptual simplicity overrides structural criteria. Root cause: motivated reasoning → downward ambiguity resolution.

**"When requirements mention agent or skill creation"**
- Anti-pattern: deferring skill loading to A.1 when A.0 requirements explicitly call for it.

---

## Gap Analysis: Known Weaknesses vs Current Structure

### Gap 1: Ungrounded Foundation

The grounding audit (`/Users/david/code/claudeutils/plans/reports/workflow-grounding-audit.md`) explicitly states:
> "`/design` in particular has accumulated 4+ structural patches (triage gate, sufficiency gate, recall artifact, D+B anchors) that might have been unnecessary with grounded foundations."

The skill is reactive-patched rather than principled. Current structure reflects:
- Empirical discovery of failure modes → patch → repeat
- No external methodology reference for complexity triage (what does established requirements engineering say about this?)
- No external reference for design methodology (what do established architectural decision processes look like?)
- The audit identifies /design as highest-leverage target precisely because of this accumulation

### Gap 2: Requirements-Clarity Gate Not Anchored

The requirements-clarity gate at the top of Phase 0 is **prose-only** — "validate requirements are actionable" is a judgment with no D+B anchor. Given the pattern that all prose gates get rationalized, this is structurally weak. An agent eager to proceed can rationalize "requirements are clear enough."

### Gap 3: Companion Task Phase 0 Process Not Enforced

The companion task rule was added in the last structural fix (e1a35cd1). It's prose: "each companion task gets its own pass through Phase 0 — recall, classification, routing." There's no structural mechanism enforcing this. The learning entry was added precisely because agents bypass it.

### Gap 4: Sufficiency Gate Decision Quality

The Outline Sufficiency Gate asks the designer to assess 5 criteria after user validation. This is a self-assessment with no external anchor. The criteria themselves are reasonable, but the assessment relies on the same LLM that produced the outline and discussion — potential for rationalized sufficiency ("criteria are close enough").

### Gap 5: No Methodology Grounding for Complexity Assessment

The classification criteria (Complex/Moderate/Simple) are entirely project-invented. There's no grounding in:
- Established software complexity metrics
- Requirements engineering literature on actionability/completeness assessment
- Design methodology best practices

The grounding audit notes: "Absorbs structured-bugfix process as routing outcome" — meaning there's a known routing extension (structured-bugfix as a new triage path) that hasn't been incorporated.

### Gap 6: Recall Artifact Staleness Accepted Without Mechanism

The skill notes: "If documentation changes between design and execution, the artifact becomes stale — this is accepted. Re-running the design pass is the refresh mechanism." This is a gap without a detection mechanism. Stale recall artifacts could silently misdirect downstream agents.

### Gap 7: Post-Outline Re-check Criteria Overlap with Sufficiency Gate

The Post-Outline Complexity Re-check (section of Phase A) and the Outline Sufficiency Gate (Phase B) both assess similar criteria. The distinction is:
- Re-check: happens before A.6, asks "can we skip design ceremony entirely?"
- Sufficiency gate: happens after user discussion, asks "can we skip /runbook?"

These are subtly different but the criteria lists are similar enough that an agent may conflate them or skip one having satisfied the other.

### Gap 8: No Feedback Loop for Triage Accuracy

There's no post-execution mechanism to verify triage was correct. If a "Simple" task turns out to require behavioral code changes, or a "Moderate" task turns out to be architectural, there's no signal feeding back to improve the triage criteria. The patches have all come from explicit failure discoveries, not systematic measurement.

---

## Structural Patterns

**Pattern 1: D+B Anchor for Prose Gates**
Every gate that was prose-only eventually failed. The fixes converted them to require a tool call (Grep, Glob, or when-resolve.py). Current structure has two explicit D+B anchors in triage; requirements-clarity gate remains prose-only.

**Pattern 2: Separation of Concerns After Interleaving**
Initial design interleaved classification criteria with routing logic. Failure: agents classified and routed simultaneously, skipping intermediate steps. Fix: explicit separate sections for Criteria / Gate / Routing.

**Pattern 3: Visible Output Before Routing**
Classification gate now requires producing a visible output block (Classification:, Behavioral code check:, Evidence:) before routing. This prevents silent internal reasoning from skipping classification entirely.

**Pattern 4: Escape Hatches Become Failure Modes**
Multiple fixes removed or constrained escape hatches. "Skip if already in context" was the dominant escape hatch pattern. Fix: require tool call proof, not self-assessment.

**Pattern 5: Structural Patches Accumulate Without Grounding**
The audit identified 4+ structural patches on /design. Each patch is locally correct but globally unsystematic. A grounded design would start from established methodology and derive the structure, rather than discovering failure modes empirically.

---

## Key File Paths

- `/Users/david/code/claudeutils/.claude/skills/design/SKILL.md` — main skill
- `/Users/david/code/claudeutils/.claude/skills/design/references/research-protocol.md` — A.3-A.5
- `/Users/david/code/claudeutils/.claude/skills/design/references/discussion-protocol.md` — Phase B
- `/Users/david/code/claudeutils/.claude/skills/design/references/design-content-rules.md` — Phase C.1
- `/Users/david/code/claudeutils/plans/reports/workflow-grounding-audit.md` — grounding priority + provenance
- `/Users/david/code/claudeutils/agents/decisions/workflow-optimization.md` — "design ceremony" and "design resolves to simple" decisions
- `/Users/david/code/claudeutils/agents/decisions/workflow-planning.md` — triage behavioral code, late-addition requirements decisions
- `/Users/david/code/claudeutils/agents/decisions/workflow-core.md` — TDD/oneshot integration, three-tier assessment
- `/Users/david/code/claudeutils/agents/decisions/workflow-execution.md` — outline-first design, model selection, agent-name validation
- `/Users/david/code/claudeutils/agents/learnings.md` — companion task + recall gate learnings
