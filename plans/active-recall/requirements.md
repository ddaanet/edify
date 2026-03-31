# Active Recall System

## Requirements

### Functional Requirements

**FR-1: Hierarchical index with embedded keywords and derived generation**
Split flat `agents/memory-index.md` (currently 449 lines, 366 entries) into a root index mapping domains to child index files. Root index lists domain names → child file paths. Child indices contain the actual `/when` and `/how` trigger entries scoped to their domain. Lookup traverses root → child → entry using existing tail-recursion primitive in `/recall` skill.

Memory entries carry their own trigger keywords as structured metadata (embedded in the entry file). The index is a generated artifact — a deterministic build step that reads entry metadata and produces the index. No hand-maintained index; no index drift.

Split threshold is token-counted: files exceeding the token budget are split. This requires token counting infrastructure as a prerequisite to the migration.

Index nesting is not limited to two levels. Project memory entries start two levels deep, but the structure must support deeper nesting for converted documentation sources (FR-4). Deeper-nested files cohabit with shallower entries in the same hierarchy.

The deeper index structure requires re-evaluating `/recall` loop behavior — current tail-recursion assumes flat-to-one-level resolution. Hierarchical traversal may need different recursion semantics.

Acceptance criteria:
- Root index file exists at generated location within memory submodule (FR-9)
- Child index files exist at `<domain>/index.md`, with memory files alongside their referencing index
- Token counting mechanism exists to measure file sizes against budget
- Index generation build step produces correct index from entry metadata
- Concurrent entry writes conflict only on entries, never on index (index regenerates)
- `claudeutils _recall resolve "when <trigger>"` works identically pre/post migration (backward compatible)
- `parse_memory_index()` in `src/claudeutils/recall/index_parser.py` handles hierarchical structure at arbitrary depth
- `/when` and `/how` CLI commands resolve entries through the hierarchy transparently
- `/recall` loop behavior updated for multi-level traversal

**FR-2: Trigger class distinction**
Formalize the two trigger classes (`when` and `how`) with distinct authoring and automation profiles. The class is a per-entry decision, not a per-document-type choice.

- `when` entries: situational triggers matching agent context/situation. Sources include project decisions from incidents/failures, methodological knowledge (e.g., GOF design patterns as solution structures to problem classes), code smells, feature documentation tied to specific problems, and "gotcha" documentation. Hand-curation required. Invalidated by explicit user decision.
- `how` entries: task-descriptive triggers matching agent's current task. Primarily procedural reference. Automation-safe for extraction.

Acceptance criteria:
- Trigger class metadata available in `IndexEntry` model (or derivable from prefix)
- Capture-time writes (FR-10) and automation tools can distinguish classes for routing decisions
- No behavioral change to resolution — both classes resolve identically via `_recall resolve`

**FR-3: Three learning categories with invalidation rules**
Categorize recall entries into three learning types with distinct invalidation conditions:

- **Internal decisions:** Project choices. Invalidated only by explicit user decision.
- **External environment facts:** Dependency/tool facts. Auto-invalidated on version change. Corpus partitioned by dependency — version bump triggers subtree re-evaluation only.
- **Hybrid:** Internal decisions grounded in external facts. Version change triggers re-evaluation; decision may survive if reasoning still holds.

Acceptance criteria:
- Category metadata representable in index entries or child index structure
- External entries partitioned by dependency (e.g., all pytest entries in one child index)
- Version-change detection mechanism defined (design phase — multiple valid approaches)
- Re-evaluation triggers subtree-scoped, not full-corpus

**FR-4: Automated documentation conversion pipeline**
Convert external reference documentation into recall entries via automated pipeline. Conversion is not limited to software documentation — methodology collections (design patterns, refactoring catalogs) and pattern libraries are equally valid sources. Output entries may be `when` or `how` class depending on content (per-entry decision, see FR-2).

Pipeline: source documentation → sonnet-grade extraction agent → corrector pass (FR-11 memory-corrector, validates trigger specificity, deduplication against existing index) → index integration.

First targets: project dependencies (pytest, click, pydantic) — immediate utility, well-scoped. Additional candidate: `plans/reports/anthropic-plugin-exploration.md` — tests a different input shape (comparative analysis with actionable findings vs API documentation).

Acceptance criteria:
- Pipeline accepts a documentation source and produces candidate recall entries
- Corrector validates each entry: trigger is specific enough, no duplicate with existing entries, content is actionable
- Output integrates into hierarchical index structure (FR-1) within memory submodule (FR-9)
- Pipeline is idempotent — re-running on same source doesn't create duplicates

**FR-5: Memory format grounding**
Ground the recall entry format before bulk conversion (FR-4). Use `/ground` skill to research and formalize:

- Naming conventions for triggers
- Trigger structure (current `/when` and `/how` prefixes, heading alignment)
- `how`/`when` distinction formalization
- Index hierarchy design (root → child navigation, branching factor)
- Embedded keyword metadata format (FR-1)

Research may suggest formats beyond the current when/how structure — remain open to alternatives.

Acceptance criteria:
- Grounding research artifact in `plans/reports/` with external framework references
- Formalized format specification consumable by FR-4's extraction agent
- Keyword metadata schema defined (what fields, where they live in entry files)
- Existing entries validate against the grounded format (backward compatible)

**FR-6: Recall-explore-recall pattern**
Preserve and formalize the two-pass recall pattern: agent recalls based on initial understanding, explores codebase, recalls again with enriched context. Second pass matches entries invisible from initial request alone.

Skills needing recall invoke `/recall` via Skill tool mid-execution (subroutine call). This is proven — worktree skill already nests /handoff and /commit via Skill tool. No continuation-prepend alternative needed.

Acceptance criteria:
- Pattern documented as a retrievable decision entry
- `/recall` skill's tail-recursion primitive supports this naturally (already exists — confirm no regression)
- Pipeline recall points (design A.1, runbook Phase 0.5) implement the pattern
- Nested `/recall` invocation from other skills works without special infrastructure

**FR-7: Recall mode simplification**
Reduce formal recall modes from five to two:

- `default`: per-key, convergence-based, scored selection (8/10 pipeline recall points). Two recursion loops: structural (navigate hierarchy until leaf entries reached — depth determined by index structure, not fixed) and semantic (loaded content reveals new relevant domains → re-enter structural traversal → converge when no new domains discovered). Replaces flat-index "two-pass" which assumed all entries visible from one read.
- `all`: per-file, tail-recursive (design A.1, runbook Tier 3 Phase 0.5)

Drop `broad` (absorbed by `all`), `deep` (absorbed by `default` two-pass), and `everything` (impractical at scale).

Acceptance criteria:
- `/recall` skill supports two modes
- `broad`, `deep`, and `everything` removed (no aliases — clean removal)
- No behavioral regression at existing pipeline recall points

**FR-8: Recall tool consolidation**
Consolidate the two recall CLI modules (`src/claudeutils/recall/` and `src/claudeutils/recall_cli/`) and the when resolver (`src/claudeutils/when/`) into a unified recall interface.

Acceptance criteria:
- Single CLI entry point for recall operations (resolve, check, diff)
- `when` resolver integrated (not a separate module)
- Resolver reads from memory submodule (FR-9) instead of `agents/` working tree paths
- Backward-compatible CLI: `claudeutils _recall resolve` still works (time-limited — plan deprecation and removal of old paths)
- Test coverage maintained (currently 20+ test files across the three modules)

**FR-9: Memory submodule storage**
Memory content (decisions, index, triggers) lives in a git submodule, decoupled from feature branch lineage. All worktrees see updates via a single shared branch with fast-forward-on-first-read semantics.

- **Write path:** Standard git operations within the submodule (`git -C memory/ add && commit`)
- **Read path:** Direct file access — agents Read/Edit memory files normally
- **Propagation:** Session start or first access fast-forwards to latest on shared branch (`git -C memory/ pull --ff-only`)
- **Merge review:** Standard git diff/merge tooling — no plumbing layer

Acceptance criteria:
- Memory submodule exists with shared branch
- All worktrees can read current memory content after fast-forward
- Writes from any worktree are visible to others after propagation
- Worktree lifecycle code (`src/claudeutils/worktree/`) handles multiple submodules with per-submodule strategy (C-6)
- `claudeutils _recall resolve` reads from submodule path transparently

**FR-10: Capture-time memory writes**
Eliminate learnings.md staging area and /codify batch consolidation. Write decisions and memory entries to permanent locations at capture time — when the agent has richest context for routing (which file, which section, trigger keywords).

- `remember: X` (or `learn: X`) → triggers `/remember` skill which handles routing, corrector validation, and index regeneration
- `/remember` skill enforces process via tool-gating: agent cannot skip corrector pass
- Corrector (FR-11) invoked as delegated agent (clean context — separate from skill format)
- Skill supports continuation-prepend for resume state under context pressure
- learnings.md goes away (no staging area)
- /codify goes away as a skill (no batch consolidation)
- /handoff becomes lighter (no learnings section to manage)
- Eliminates: soft-limit management, "don't codify on branches" constraint

Acceptance criteria:
- `/remember` skill defined with tool-gating enforcing corrector pass
- Skill routes entry to correct decision file in memory submodule
- Entry includes embedded keyword metadata (FR-1) for index generation
- Memory-corrector (FR-11) validates the write via agent delegation
- Skill supports continuation-prepend for handoff under context pressure
- No learnings.md in project root
- /codify skill removed
- /handoff skill updated (no learnings section)

**FR-11: Memory-corrector agent**
Clean-context agent validates all memory writes — not just bulk conversion (FR-4) but every `learn:` capture and manual entry. CURATE role in lifecycle between CREATE (session agent) and CONSUME (resolver).

- **Quality criteria:** trigger specificity, format compliance, duplicate detection, when/how classification, keyword quality
- **Pattern:** follows vet-false-positives "Do NOT Flag" shape — categorical suppression taxonomy, not confidence scores

Acceptance criteria:
- Corrector agent defined with quality criteria
- All memory write paths route through corrector
- Corrector rejects or requests revision for entries failing quality criteria
- False positive suppression taxonomy documented

**FR-12: Usage scoring**
Track per-entry resolution frequency as informational signal. Absorbed from recall-pipeline.
- Acceptance: `claudeutils _recall stats` shows per-entry resolution count and last-used date
- Note: Zero resolutions does not imply low value — scoring informs human judgment, not automated pruning

**FR-13: Recall deduplication**
Detect and merge duplicate recall entries across decision files (`agents/decisions/*.md`). Duplicates arise from parallel worktrees writing similar entries independently. Absorbed from recall-pipeline.
- Acceptance: Two entries with identical trigger phrases but different wording → flagged for merge with diff shown
- Acceptance: Entries with overlapping semantic scope but different triggers → flagged as candidates (not auto-merged)

### Non-Functional Requirements

**NFR-1: Scaling capacity**
Hierarchical index must support thousands of entries (projected from bulk documentation conversion) without degrading lookup performance or agent context budget.

**NFR-2: Backward compatibility**
All existing CLI commands (`claudeutils _recall resolve`, `claudeutils _recall check`, `claudeutils _recall diff`, `claudeutils _when`) must continue working during migration. Old paths are time-limited — plan deprecation schedule and removal.

**NFR-3: Incremental migration**
Migration from flat to hierarchical index can proceed incrementally — partial hierarchy (some domains split, others still flat) must work correctly.

**NFR-4: Token budget targets**
Index and content files should target a token budget as a design goal (not a hard constraint). Design phase determines the specific threshold and measurement approach.

### Constraints

**C-1: Memory format grounding prerequisite**
FR-5 (memory format grounding) must complete before FR-4 (automated documentation conversion). Bulk conversion without grounded format produces entries that need rework.

**C-2: Hierarchical index before bulk conversion**
FR-1 (hierarchical index) must be operational before FR-4 bulk conversion populates thousands of entries into the system.

**C-3: Token counting before hierarchical split**
FR-1 requires token counting infrastructure to determine split boundaries. Token counting mechanism must exist before migration begins.

**C-4: Existing infrastructure**
Current infrastructure: `src/claudeutils/recall/` (9 modules), `src/claudeutils/recall_cli/` (2 modules), `src/claudeutils/when/` (5 modules), `agents/memory-index.md` (366 entries), `agents/learnings.md` (staging area — removed by FR-10), `/recall` skill, `/when` and `/how` skills, `/codify` skill (removed by FR-10), pretooluse-recall-check hook, 20+ test files. All must be accounted for during consolidation.

**C-5: Cross-worktree memory visibility**
Memory must be accessible from all worktrees without merge-from-main. The submodule shared-branch model (FR-9) satisfies this — all worktrees fast-forward to the same branch head.

**C-6: Worktree multi-submodule support**
Worktree lifecycle code (`src/claudeutils/worktree/`) currently hardcodes `plugin` (38 occurrences across 4 files). Must be refactored to support multiple submodules with per-submodule strategy dispatch: plugin uses branch-per-worktree, memory submodule uses single-shared-branch. This is prerequisite infrastructure for FR-9.

### Out of Scope

- SWE-ContextBench benchmarking — mentioned in brief as positioning, not implementation work
- Stage provenance tags in recall-artifact.md — grounding report Pattern 1, deferred
- Recall-artifact rejection tracking — grounding report Pattern 2 annotated removal, deferred
- Lifecycle role contract enforcement — grounding report Pattern 3, convention not mechanically enforced
- PreToolUse hook for lint-gated recall — separate from core recall system (defense-in-depth.md)

### Dependencies

- `/ground` skill — required for FR-5 (memory format grounding)
- Context7 MCP — potential source for FR-4 documentation extraction
- Recall lifecycle grounding report (`plans/reports/recall-lifecycle-grounding.md`) — informs FR-7 mode simplification and pipeline integration
- Worktree multi-submodule refactor (C-6) — prerequisite for FR-9 memory submodule

### Open Questions

- Q-1: How does version-change detection work for FR-3 external entries? Multiple valid approaches (manual recipe, lockfile diff, index metadata). Design phase evaluates trade-offs.
- Q-2: Which documentation sources follow initial targets (pytest, click, pydantic)? Candidates include Python stdlib, methodology collections (GOF patterns, refactoring catalogs), tool configs (ruff, mypy).
- Q-3: Memory submodule concurrent write handling — two worktrees writing simultaneously. Fast-forward fails → pull-rebase-push resolves, but file-level semantic conflicts need strategy (design phase).
- Q-4: Session cost of capture-time writes (FR-10) — append-only vs whole-file edit, quality tradeoff, correction strategies.
- Q-5: Corrector timing (FR-11) — synchronous (per-write, blocks on validation) vs post-handoff (per-session batch) vs asynchronous (background). Trade-off between write latency and quality assurance.

### References

- `plans/active-recall/brief.md` — architectural discussion distillation (2026-03-02, 2026-03-06)
- `plans/reports/recall-lifecycle-grounding.md` — lifecycle patterns, mode assignments, three-tier model
- `plans/reports/recall-lifecycle-internal-codebase.md` — internal inventory
- `plans/reports/recall-lifecycle-external-research.md` — external frameworks
- `plans/reports/anthropic-plugin-exploration.md` — FR-4 extraction pipeline test target candidate
- Task context: git commit `fc0d9b8a` — session that produced the architectural discussion
- Discussion: submodule vs orphan branch — submodule chosen for equivalent merge complexity with standard tooling, direct file access, existing worktree infrastructure leverage

### Skill Dependencies (for /design)

- Load `plugin-dev:hook-development` before design (pretooluse-recall-check hook affected by FR-8 consolidation)
- Load `plugin-dev:skill-development` before design (recall skill restructuring in FR-7)
- Load `plugin-dev:agent-development` before design (FR-11 memory-corrector agent definition)
