# Memory Index Actionability Review

Analysis of each memory-index.md section for trigger clarity, trigger surface, redundancy, dead entries, and missing coverage.

Entries not mentioned are considered acceptable.

---

## agents/decisions/cli.md

**No issues.** 5 entries, all specific to CLI implementation work. Triggers are clear and match situations an agent would encounter when working on CLI code.

---

## agents/decisions/data-processing.md

**Dead entries (domain-specific, rarely triggered):**

- `/how resolve agent ids to sessions` — Very specific to Claude Code session architecture. An agent would need to be implementing session tree traversal to encounter this. Narrow but valid for this codebase.
- `/how extract agent ids from sessions` — Same concern. Paired with above.
- `/how validate session uuid files` — Only relevant when modifying session discovery code.

**Trigger surface gap:**

- `/how detect trivial messages` — An agent working on message filtering might think "skip noise" or "filter short messages" rather than "detect trivial messages." Consider alias: `/how filter trivial prompts`.
- `/how layer feedback extraction` — "Layer" is unusual phrasing. An agent encountering feedback extraction ordering would more likely think "feedback extraction priority" or "feedback filter ordering."

**Assessment:** Most entries are implementation-specific to the edify data processing pipeline. They serve well for maintenance work on those exact modules but have narrow trigger surfaces outside that context.

---

## agents/decisions/pipeline-contracts.md

**Trigger clarity issues:**

- `/when transformation table` — The pipe-delimited keywords help, but the trigger phrase itself is abstract. An agent deciding which review gate to use would think "which reviewer for this artifact" not "transformation table." Consider: `/when choosing review gate for artifact type`.
- `/when phase type model` — Ambiguous. Three unrelated concepts joined by spaces. Could mean "when choosing model for a phase type" or "when phase type affects model selection." The actual content is about TDD vs general typing. Better: `/when declaring phase type tdd or general`.
- `/when expansion reintroduces defects` — Clear trigger, but this is a planning-phase concern. An agent expanding phases wouldn't search for "reintroduces defects" — they'd need this BEFORE the problem occurs. Consider: `/when reviewing expanded phases for regression`.

**Good entries:**

- `/when UNFIXABLE escalation` — Excellent trigger. Matches exact situation.
- `/when vet escalation calibration` — Clear, matches vet review situations.
- `/how review delegation scope template` — Directly actionable.

---

## agents/decisions/deliverable-review.md

**Coverage gap:** Single entry for a 100-line file with multiple sections (artifact types, review axes by type, process steps, output format). Missing entries:

- `/how classify deliverable artifact types` — The type classification table (Code, Test, Agentic prose, etc.)
- `/how review agentic prose artifacts` — Actionability, constraint precision, determinism axes
- `/when reviewing code artifacts` — Robustness, modularity, testability axes

The single entry `/when identifying deliverable artifacts` covers only the identification method, not the review process itself.

---

## agents/decisions/implementation-notes.md

**Dead/near-dead entries:**

- `/when classifying section headers` — Very niche. Only relevant when writing decision files with structural vs semantic headers. The `.` prefix convention is already documented inline.
- `/when formatting index entry lines` — Only relevant when editing memory-index.md itself. Meta-level entry.
- `/when shortening index entry keys` — Same meta-level concern. Only matters during index maintenance.
- `/when marking organizational sections` — Closely related to classifying section headers. Both address the `.` prefix convention.

**Redundancy:**

- `/when classifying section headers` and `/when marking organizational sections` — Both address the structural `.` prefix convention from different angles. An agent would trigger one but not know which. Consider merging into: `/when using dot prefix for structural sections`.

**Trigger surface gap:**

- `/when placing skill constraint rules` — The actual decision is "put negative constraints where positive decisions are made, not in cleanup phases." An agent writing a multi-phase skill would think "where to put DO NOT rules" rather than "placing skill constraint rules."
- `/how implement prose gates` — Good trigger, but an agent might also search "when skill step has no tool call" or "when step gets skipped." The D+B hybrid pattern is critical enough to warrant a second trigger path.

---

## agents/decisions/markdown-tooling.md

**Dead entries (implementation-frozen decisions):**

- `/when extending vs creating cleanup functions` — One-time design decision about markdown.py function organization. Unless the preprocessor is being extended, this never triggers.
- `/how order markdown processing steps` — Same. Locked ordering for existing pipeline.
- `/how detect markdown line prefixes` — Implementation detail of prefix detection algorithm.
- `/how indent nested markdown lists` — "2 spaces." This is a single-line answer frozen in place.
- `/when evolving markdown processing` — Migration path to dprint plugin. Aspirational, no current work.

**Assessment:** 13 entries for a domain (markdown tooling) that is implementation-frozen. Most are archival rather than actionable. Unless the preprocessor is actively modified, these entries consume index space without triggering.

---

## agents/decisions/project-config.md

**Trigger surface gaps:**

- `/how manage memory index growth` — An agent encountering a growing index would think "index too large" or "prune index" not "manage memory index growth." The actual decision is "don't prune, append-only" — but the trigger doesn't convey the answer direction.
- `/how surface skills through discovery layers` — Good trigger for someone building a skill. But the actual failure mode is "skill exists but agents don't use it" — consider additional trigger: `/when skill is not being discovered`.

**Good entries:**

- `/when finding project root in scripts` — Clear, specific, matches exact situation.
- `/when using heredocs in sandbox` — Excellent — matches the exact error an agent would encounter.

---

## agents/decisions/prompt-structure-research.md

**Dead entries:**

- `/when evaluating prompt structure tools` — Research conclusion: no tool exists. This is archival, not actionable.
- `/when applying prompt research` — Status update (two items done, one remaining). Not a decision to recall.

**Trigger surface gap:**

- `/when ordering content for position bias` — An agent editing CLAUDE.md fragment order would think "where to put this fragment" or "fragment ordering." The trigger assumes knowledge of "position bias" as a concept.
- `/when managing rule count budget` — Actionable, but an agent might think "too many rules" or "context too long" rather than "rule count budget."

**Redundancy:**

- `/when ordering content for position bias` and `/how order fragments by position bias` — These are the same topic. One is the research rationale, the other is the implementation. An agent would trigger both for the same situation.

---

## agents/decisions/runbook-review.md

**No significant issues.** 5 entries, all tightly scoped to runbook planning. Triggers match situations a planner would encounter.

**Minor:** `/when planning for file growth` could also trigger as `/when projecting lines per cycle` since the actual work is estimation during planning.

---

## agents/decisions/testing.md

**Trigger surface gaps:**

- `/how test markdown cleanup` — Very specific to markdown module. An agent testing other cleanup functions wouldn't find this.
- `/when evaluating test success metrics` — Generic trigger, but the content is a simple checklist (all pass, no regressions, follows patterns). Low value as a recalled decision.

**Good entries:**

- `/when writing red phase assertions` — Excellent. Matches exact TDD situation.
- `/when detecting vacuous assertions from skipped RED` — Clear, matches error recovery.
- `/when preferring e2e over mocked subprocess` — Good trigger for test architecture decisions.

---

## agents/decisions/validation-quality.md

**Dead entries (implementation-frozen):**

- `/how define feedback type enum` — "Use StrEnum." One-time decision.
- `/how detect noise in command output` — Specific marker list for feedback pipeline. Only relevant if modifying noise detection.
- `/how categorize feedback by keywords` — Keyword-to-category mapping table. Frozen unless pipeline changes.
- `/how deduplicate feedback entries` — "First 100 characters." Implementation detail.
- `/when filtering for rule extraction` — Specific filter thresholds for `rules` command.

**Assessment:** Similar to markdown-tooling — 12 entries for a domain (feedback pipeline) that appears implementation-complete. Most entries are frozen implementation details rather than decisions an agent would need to recall.

---

## agents/decisions/workflow-advanced.md

**Dead/near-dead entries:**

- `/when dogfooding process design` — Meta-principle ("use your own process"). Rarely triggers as a recall.
- `/when applying feedback loop insights` — Abstract meta-pattern. An agent wouldn't search for "feedback loop insights."
- `/how transmit recommendations inline` — Specific to outline review agents. Narrow but valid.

**Trigger surface gaps:**

- `/how name tasks as prose keys` — An agent creating a task would think "task naming" not "prose keys." Consider: `/how name session tasks`.
- `/when writing test descriptions in prose` — Good trigger but could also match: `/when writing RED phase in runbook` (since that's where prose descriptions go).
- `/when scanning requirements for skills` — An agent starting design wouldn't think "scanning requirements for skills." The action is "load skill-development rules early." Consider: `/when requirements mention agent or skill creation`.

**Redundancy:**

- `/how expand outlines into phases` and `/how review phases iteratively` — Closely related. Both describe the same expansion workflow. An agent doing phase expansion would trigger both and get overlapping content.

---

## agents/decisions/workflow-core.md

**Trigger clarity issues:**

- `/when using oneshot workflow` — The content describes the entire weak orchestrator pattern validation. The trigger implies choosing between oneshot and another workflow, but the content is more of a status report.
- `/how integrate tdd workflow` — Same issue. The content is a comprehensive status report of TDD integration, not a procedural "how to."
- `/how document three stream planning` — Niche. Only relevant when managing multiple parallel work streams.

**Dead entries:**

- `/how store learnings in handoffs` — Historical decision (removed agents/learnings/ directory). Implementation is already done; this is archival.
- `/how squash tdd cycle commits` — Specific git procedure. Only relevant during TDD cycle squashing, which is a rare manual operation.

---

## agents/decisions/workflow-optimization.md

**Trigger surface gaps:**

- `/when template context contradicts rules` — An agent wouldn't search for this. The situation is "agent ignores my instruction" — they'd think "directive conflict" or "why is agent doing X instead of Y." The entry title describes the root cause, not the symptom.
- `/when orchestrator model differs from step` — Same pattern. Symptom is "step agent using wrong model" not "orchestrator model differs."
- `/how implement continuation passing` — Long entry (20+ lines referenced). An agent encountering skill chaining would think "skill chain" or "tail call" rather than "continuation passing."

**Good entries:**

- `/when context already loaded for delegation` — Matches exact "should I delegate?" decision point.
- `/when vet catches structural issues` — Clear trigger during vet review.

---

## agents/decisions/orchestration-execution.md

**Trigger clarity issues:**

- `/when context defines scope boundary` — Abstract. An agent dealing with scope creep wouldn't search this phrase. The actual lesson is "give agents only the files they need."
- `/when no post-dispatch communication available` — Describes a limitation, not a decision point. The actionable trigger would be: `/when partitioning work for parallel agents`.
- `/when always scripting non-cognitive solutions` — Trigger is the principle itself, not a situation. An agent wouldn't search "always scripting non-cognitive solutions" — they'd be in a situation like "should I write a script or use agent judgment."
- `/when script validates it should generate` — Cryptic trigger. "It should generate" is unclear without reading the content. The actual decision is "scripts should generate metadata, not just validate it."

**Redundancy with CLAUDE.md fragments:**

- `/when delegation requires commit instruction` — The vet-requirement fragment already covers this ("commit your output before returning"). The memory index entry adds the specific root cause (agents leave tree dirty) but the behavior is already in always-loaded context.
- `/when assessing RED pass blast radius` — Already in learnings.md as "RED pass blast radius assessment." Dual indexing between learnings and memory index.

---

## agents/decisions/operational-practices.md

**Dead/near-dead entries:**

- `/when classifyHandoffIfNeeded bug occurs` — Bug workaround entry. Valid while bug exists, but very narrow trigger. An agent would encounter the error message, not search for this phrase.
- `/when DP matrix has zero-ambiguity` — Extremely niche. Only relevant to one specific algorithm (subsequence matching scorer).
- `/when fixture shadowing creates dead code` — Narrow pytest antipattern. Triggers only when debugging unreachable test code.

**Trigger surface gaps:**

- `/when behavioral triggers beat passive knowledge` — Meta-principle about the index itself. An agent adding to the index would think "what format for new entry" not "behavioral triggers beat passive knowledge."
- `/when enforcement cannot fix judgment` — Philosophy entry. An agent wouldn't search this. The actionable lesson is embedded in design conversations, not recall moments.
- `/when task names must be branch-suitable` — Good trigger for task creation, but an agent might think "naming task" rather than "branch-suitable."

---

## Unindexed File: agents/decisions/defense-in-depth.md

**Missing from index entirely.** 95-line file with the defense-in-depth quality gate pattern. Suggested entries:

- `/when designing quality gates` — The core decision (layered defense, no single gate trusted)
- `/how layer quality gate defenses` — The four-layer pattern (execution flow, automated checks, quality review, conformance)
- `/when reviewing quality gate design` — The checklist at the end

This file is referenced by testing.md and workflow-core.md decisions. Its absence from the index means an agent designing a new quality process would not discover it.

---

## Systemic Patterns

### 1. Archival entries masquerading as actionable knowledge

~25-30% of entries document implementation-frozen decisions that will never trigger during normal work. Entire sections (markdown-tooling, validation-quality, data-processing) are largely archival. These entries dilute the index's signal-to-noise ratio.

**Recommendation:** Consider a `[frozen]` marker for implementation-complete decisions. Or accept the cost: at ~25 tokens/entry, 30 archival entries cost ~750 tokens — modest but noisy for scanning.

### 2. Trigger phrasing matches root cause, not symptom

Many entries are titled after the decision/root cause rather than the situation that would prompt recall. Examples: "template context contradicts rules," "enforcement cannot fix judgment," "behavioral triggers beat passive knowledge." An agent encounters the symptom (agent ignoring instruction, judgment failing, knowledge not recalled) and wouldn't search for the root cause phrase because they don't yet know the root cause.

**Recommendation:** Phrase triggers as the observable situation, not the underlying cause. The cause is what the entry teaches; the situation is what triggers recall.

### 3. Meta-index entries

Several entries exist about the index itself: formatting index entry lines, shortening index entry keys, marking organizational sections, writing memory index entry keys, managing memory index growth, behavioral triggers beat passive knowledge. These are maintenance instructions for a rarely-modified artifact.

**Recommendation:** Consolidate into a single "how to maintain memory index" entry, or accept them as low-frequency but valid.

### 4. Missing coverage for defense-in-depth.md

The only completely unindexed decision file. Contains a reusable pattern (layered quality gates) that applies across the entire workflow.

### 5. Redundancy clusters

Three pairs have significant overlap:
- `classifying section headers` / `marking organizational sections`
- `ordering content for position bias` / `order fragments by position bias`
- `expand outlines into phases` / `review phases iteratively`

Each pair would trigger for the same situation, forcing the agent to invoke both and reconcile.

### 6. Domain-frozen sections inflate the index

markdown-tooling (13 entries), validation-quality (12 entries), and data-processing (16 entries) together account for 41 of ~150 entries (27%). These domains appear implementation-complete based on jobs.md and session.md. Their entries are valid but rarely actionable.
