# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/codify` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

## When companion tasks bundled into /design invocation
- Anti-pattern: Session note says "address X during /design." Agent treats companion work as exempt from design process — no recall, no skill loading, no classification gate. Rationalizes "well-specified from prior RCA" to skip all process steps.
- Correct pattern: Companion tasks get their own triage pass through the same Phase 0 gates. "Address during /design" means the /design session is the venue, not that process is optional. Each workstream needs: recall, classification, routing.
- Evidence: 4 triage fixes to design skill attempted without /recall or /skill-development loading. /reflect identified same pattern class as "Simple triage skips recall" learning.
## When recall gate has skip condition
- Anti-pattern: "Read X (skip if already in context)" as a recall gate. Agent rationalizes the skip condition without verifying — substitutes related activity for the required Read. The escape hatch IS the failure mode.
- Correct pattern: Anchor recall with a tool call that proves work happened. `when-resolve.py` is the gate: it's a Bash call (unskippable), requires trigger knowledge (forces prior Read of memory-index), and produces output (proves resolution). One gate anchor is sufficient — passphrase/proof-of-Read mechanisms are redundant when the resolution tool already proves both.
- Evidence: /reflect Phase 4.5 skipped recall entirely. Same class as "treating recall-artifact summary as recall pass" — agent substitutes adjacent activity for the specific required action.
## When selecting model for discovery and audit
- Anti-pattern: Using haiku scouts to audit prose quality or detect structural anti-patterns in LLM-consumed instruction files (skills, agents, fragments). Haiku grades generously, misses dominant failure patterns, and produces false positives that require opus validation — double work.
- Correct pattern: Sonnet minimum for any discovery/audit touching skills, agents, or fragments. These are architectural prose artifacts — assessing their quality requires the same judgment tier as editing them. The "model by complexity" rule applies to analysis, not just edits.
- Evidence: Haiku scout graded 0 skills at C (sonnet found 3), missed description anti-pattern as dominant issue (18/30), produced 15 gate findings vs sonnet's 12 (3 false positives from over-flagging steps where preceding tool output naturally feeds judgment).
## When optimizing skill prose quality
- Reference: `plans/reports/skill-optimization-grounding.md` — Segment → Attribute → Compress framework adapted from LLMLingua/ProCut. 9 content categories with compression budgets per category.
- Triggers: deslop, compression, segment, attribute, budget, skill optimization, prose quality pass
## When editing skill files
- Platform constraint: skill `description` frontmatter MUST use "This skill should be used when..." format (plugin-dev:skill-development, skill-reviewer enforce this). Improve wording within this format, do not replace the format.
- Extraction safety: every content block moved to references/ must leave a trigger condition + Read instruction in the main SKILL.md body. Verify each references/ file has a corresponding load point.
- Control flow verification: after restructuring skills with conditional branches, enumerate all execution paths and verify user-visible output on each path. Prior deslop on design skill combined two fast paths and regressed user-facing classification message.
- D+B gate additions: adding tool calls to anchor prose-only gates must not change the gate's decision outcome on existing paths. The added Read/Bash provides data for judgment — it should not introduce new content that shifts the judgment itself.
- Triggers: editing skills, skill surgery, deslop, extraction, progressive disclosure, restructuring conditional branches
## When dispatching parallel agents with shared recall
- Anti-pattern: Each parallel agent independently resolves the same recall artifact keys (N agents × 10 when-resolve.py calls = N×10 redundant Bash calls + parsing). Design/audit reports also re-read by each agent.
- Correct pattern: Pre-resolve recall to a shared file (`plans/<job>/reports/resolved-recall.md`) before dispatch. All agents Read one file instead of each running the resolver. Same approach for any shared context (design doc summaries, audit findings) — resolve once, share the output.
- Evidence: 4 execution agents each ran when-resolve.py with 10 keys independently. Pre-resolved file created for 5 convergence review agents, eliminating ~50 redundant Bash calls.
## When reviewing skills after batch edits
- Anti-pattern: Single reviewer agent for all modified skills. Context fills with 28 skill reads before review begins. Quality degrades as context grows.
- Correct pattern: Parallel reviewers split by relatedness (phase groupings natural — related skills, similar edit patterns, cross-skill consistency visible within group). Separate behavior invariance agent for conditional-branch skills. All read-only, no file conflicts.
- Evidence: 5 parallel opus reviewers (4 skill quality + 1 behavior invariance) completed convergence review. Found 7 majors that single reviewer might have missed in later skills due to context pressure.
## When splitting decision files with memory-index entries
- The validation script handles relocating memory-index entries to match their actual file locations. Do not manually move entries between sections during a file split — add new entries, let the validator handle section assignment.
- Evidence: Split workflow-optimization.md → workflow-execution.md, manually reorganized 14 memory-index entries between sections. User corrected: validator does this automatically.
## When naming learning headings
- Anti-pattern: naming the heading after the antipattern itself ("When recall step uses skip condition language"). This describes what went wrong, not where you are.
- Correct pattern: name after the situation at the decision point — the activity you're doing when the rule applies ("When recall gate has skip condition" → you're at the gate, evaluating it).
- Routes to both: **handoff** (writing new ## headings for learnings mid-session) and **codify** (consolidating learnings into permanent docs). Both contexts produce ## headings that become memory-index triggers.
- Same principle applies to memory-index trigger naming: trigger = situation, not antipattern label.
## When redesigning a process skill
- The skill's own failure modes govern its redesign if you use it on itself (circular dependency).
- Correct pattern: ground against external frameworks first. The grounding step externalizes the design reasoning — principles come from outside the system, not from the skill's own reasoning. Then the redesign is execution of grounded conclusions (moderate complexity), not design from scratch (complex).
- Corollary: by the grounded skill's own classification criteria, the redesign has clear requirements (grounding gaps with proposed fixes), no architectural uncertainty (grounding resolved it), and bounded scope → Moderate, routes to direct execution or /runbook, not full /design.
- Evidence: /design grounding produced 8 principles and 7 gaps from 6 external frameworks. All 7 gap fixes were prose-only edits to existing sections — direct execution, no runbook needed.
## When requirements capture needs recall
- /requirements skill lacks a recall pass. /design has A.1 (recall), but /requirements goes straight from conversation extraction to codebase discovery. This session needed `/recall deep` before `/requirements` to load 33 entries from 9 decision files — data-processing patterns, feedback pipeline architecture, CLI conventions, session format knowledge. Without recall, requirements would have been naive (e.g., UUID-only filtering when agent files also contain commit data).
- Correct pattern: /requirements should have a recall step between mode detection and conversation scanning, producing a recall artifact. The recall grounds the extraction — agent knows what infrastructure exists before interpreting what the user asked for.
- Fixed: Added recall pass to /requirements (invokes `/recall all`), updated /design A.1 to also invoke `/recall all`. Both skills now produce entry-keys-only recall artifacts — downstream consumers resolve fresh content via when-resolve.py.
## When writing recall artifacts
- Anti-pattern: Full excerpts per entry (heading + source + relevance + content excerpt). Creates stale snapshots — if decision files change between artifact creation and consumption, excerpts are outdated.
- Correct pattern: Entry keys only. Artifact lists trigger phrases with 1-line relevance notes. Downstream consumers batch-resolve via `when-resolve.py` to get current content. No staleness, no excerpt duplication.
- Evidence: `plans/skills-quality-pass/recall-artifact.md` used keys-only format; `plans/task-lifecycle/recall-artifact.md` used full excerpts. Keys-only is structurally superior — the artifact is a curated index, not a cache.
## When routing prototype/exploration work through pipeline
- Anti-pattern: Design skill's behavioral-code gate routes ALL non-prose work to /runbook. /runbook tier assessment counts files against production conventions (test mirrors, module splitting, lint gates). A C-3 prototype script in plans/prototypes/ gets assessed as Tier 3 (~20 TDD cycles). Procedural momentum from practiced pipeline (/design → /runbook → /orchestrate) overrides explicit prototype constraint.
- Correct pattern: Artifact destination determines ceremony level. Prototype scripts (plans/prototypes/, one-off analysis, spikes) don't need runbooks, TDD, or test files. Design resolves complexity; post-design a prototype is direct implementation regardless of behavioral code. The classification model conflates code type (behavioral vs prose) with work type (production vs exploration) — needs grounding.
- Fix: `plans/complexity-routing/problem.md` — grounding pass to rebuild classification + routing model from established frameworks.
- Evidence: Session-scraping prototype interrupted by user after /runbook began Phase 0.5 discovery for a "quick prototype."