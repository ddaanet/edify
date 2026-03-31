# Active Recall System: Design Outline (Rev 2)

Decomposition via DSM banding + Axiomatic Design zigzag + TRL readiness scale. Rev 2 incorporates FR-9 (memory submodule), FR-10 (capture-time writes), FR-11 (memory-corrector), C-5, C-6 from 2026-03-06 requirements update.

## Sub-Problems

### S-A: Token Count Cache

**What (FR):** Token counting with caching for repeated calls (C-3 prerequisite for FR-1 split threshold).

**How (DP):** sqlite cache via sqlalchemy wrapping existing `count_tokens_for_file()`. Composite key `(md5_hex, model_id)`, `last_used` for eviction, `platformdirs.user_cache_dir("claudeutils") / "token_cache.db"`.

**Type:** Implementation
**Readiness:** Executable — all design decisions resolved (storage, schema, key structure, integration point).

**Inputs:** `src/claudeutils/tokens.py`, `tokens_cli.py` (pre-existing)
**Outputs:** Cached token counting API — `count_tokens_for_file()` checks cache before Anthropic API call
**Controls:** NFR-4 (token budget as design target)
**Mechanism:** sonnet, worktree

**File set:** `src/claudeutils/tokens.py`, new `src/claudeutils/token_cache.py` (or similar), tests

---

### S-B: Recall Module Consolidation

**What (FR):** Unify three modules into one recall interface (FR-8). Includes NFR-2 backward compatibility for all existing CLI commands.

**How (DP):** Merge `when/` resolver + `recall_cli/` into `recall/`. Unify `IndexEntry` and `WhenEntry` into single model. `_recall` as canonical CLI group, `_when` as thin deprecation alias with warning. `_recall check`, `_recall diff` preserved in unified module (path updates deferred to S-J). 22 test files consolidated with shared fixtures.

**Note:** Resolver path configuration remains pointing at current `agents/` locations. Path update to submodule location is S-J's responsibility — S-B consolidates the code, S-J changes where it reads from.

**Type:** Implementation (refactor + migration)
**Readiness:** Executable — merge targets identified, model unification approach clear.

**Inputs:** `src/claudeutils/recall/` (9 modules), `src/claudeutils/recall_cli/` (2 modules), `src/claudeutils/when/` (5 modules), 22 test files (pre-existing)
**Outputs:** Unified `src/claudeutils/recall/` module with single `IndexEntry` model, single CLI group, deprecation alias
**Controls:** NFR-2 (backward compat during migration), C-4 (infrastructure accounting)
**Mechanism:** sonnet, worktree

**NFR-2 CLI disposition:**
- `claudeutils _recall resolve` — preserved (canonical)
- `claudeutils _recall check` — preserved in unified module
- `claudeutils _recall diff` — preserved in unified module
- `claudeutils _when` — thin deprecation alias with warning → removal after migration

**File set:** `src/claudeutils/recall/`, `src/claudeutils/recall_cli/`, `src/claudeutils/when/`, `tests/` (22 files)

---

### S-C: Memory Format Grounding

**What (FR):** Ground trigger format, when/how distinction, naming conventions before bulk conversion (FR-5). Research may suggest formats beyond current when/how — remain open.

**How (DP):** `/ground` skill — research trigger naming conventions, trigger structure formalization, index hierarchy validation (branching factor, navigation). Produce format specification consumable by S-G's extraction agent and S-K's corrector validation criteria.

**Type:** Design input (research)
**Readiness:** Groundable — open research question, unknown output shape.

**Inputs:** Existing 366 entries in `agents/memory-index.md`, current when/how format, brief.md vision (pre-existing)
**Outputs:** `plans/reports/memory-format-grounding.md` — format specification with trigger syntax, validation rules, taxonomy decision, embedded keyword metadata schema (FR-1)
**Controls:** C-1 (must complete before FR-4 bulk conversion)
**Mechanism:** opus, worktree

**File set:** No code changes — research artifact only

---

### S-I: Worktree Multi-Submodule Refactor

**What (C-6):** Refactor worktree lifecycle code to support multiple submodules with per-submodule strategy dispatch. Prerequisite infrastructure for FR-9 memory submodule.

**How (DP):**
- Extract hardcoded `plugin` references (42 occurrences across 4 files: `git_ops.py`, `merge.py`, `merge_state.py`, `cli.py`) into configurable submodule registry
- Per-submodule strategy: `plugin` uses branch-per-worktree (current behavior), `memory` uses single-shared-branch (new)
- Strategy dispatch in worktree create/merge/remove operations
- Submodule registry as configuration (not hardcoded) — future submodules add config, not code

**Type:** Implementation (refactor)
**Readiness:** Executable — scope clear (42 hardcoded refs), strategy dispatch pattern straightforward.

**Inputs:** `src/claudeutils/worktree/` (4 affected files, pre-existing)
**Outputs:** Configurable submodule handling in worktree lifecycle, strategy dispatch for branch-per-worktree vs single-shared-branch
**Controls:** C-6 (multi-submodule support)
**Mechanism:** sonnet, worktree

**File set:** `src/claudeutils/worktree/git_ops.py`, `merge.py`, `merge_state.py`, `cli.py`, tests

---

### S-J: Memory Submodule Setup

**What (FR):** Create memory submodule with shared branch, configure propagation, update resolver paths (FR-9). Satisfies C-5 (cross-worktree visibility).

**How (DP):**
- Initialize memory submodule with single shared branch
- Fast-forward-on-first-read propagation: session start or first access runs `git -C memory/ pull --ff-only`
- Write path: standard git operations within submodule (`git -C memory/ add && commit`)
- Read path: direct file access — agents Read/Edit memory files at `memory/` path
- Update resolver path configuration (from S-B's consolidated module) to read from `memory/` submodule
- Migrate existing `agents/decisions/`, `agents/memory-index.md` content into submodule (or prepare migration path for S-D to build hierarchy directly in submodule)

**Type:** Implementation (infrastructure)
**Readiness:** Designable — submodule creation is mechanical, but migration strategy (migrate existing content first vs build new hierarchy directly) and propagation hook integration need design decisions.

**Inputs:**
- Multi-submodule support from S-I (structural dependency — worktree code must handle memory submodule)
**Outputs:** Memory submodule with shared branch, propagation mechanism, resolver path update
**Controls:** C-5 (cross-worktree visibility), FR-9 acceptance criteria
**Mechanism:** sonnet, worktree

**File set:** `.gitmodules`, `memory/` (new submodule), resolver config in `src/claudeutils/recall/`, propagation hook/script

**Design question (S-J/S-D ordering):** S-D builds the hierarchical index. Two options: (a) S-J migrates existing flat content into submodule, S-D later restructures it into hierarchy inside submodule; (b) S-J creates empty submodule structure, S-D builds hierarchy directly inside it. Option (b) avoids double-migration but requires S-J before S-D implementation. Option (a) lets S-D start design in parallel. Recommended: S-J creates submodule with minimal scaffolding, S-D builds hierarchy directly in submodule. S-D's design phase can proceed without S-J; only S-D's implementation needs the submodule to exist.

---

### S-D: Hierarchical Index Structure

**What (FR):** Migrate flat index to tree structure with arbitrary nesting (FR-1). Includes parser updates, migration tooling, hook/skill path updates, recall loop update for multi-level traversal. Index is a generated artifact from embedded entry metadata.

**How (DP):**
- Branch indices (index-of-indices only) vs leaf indices (entries only) — no mixed indices
- Parser detects index type, traverses recursively at arbitrary depth
- Index generation build step: reads embedded keyword metadata from entry files, produces index deterministically
- Migration script splits `agents/memory-index.md` entries into `memory/` submodule hierarchy (target location from S-J)
- Domain path mapping: space → `/` (parent-child) or `-` (compound noun)
- Token budget threshold measurement using S-A cache to determine split boundaries
- pretooluse-recall-check hook updated to new index location in submodule
- `/when` and `/how` skill paths updated for submodule location

**Type:** Implementation
**Readiness:** Designable — structural decisions resolved (branch/leaf, no mixed, generated index), but traversal semantics, migration tooling details, token budget threshold, index generation mechanism, and incremental migration strategy (NFR-3) need design.

**Inputs:**
- Unified `IndexEntry` model from S-B (structural dependency)
- Token cache from S-A (data dependency — split threshold measurement)
- Memory submodule from S-J (structural dependency — target location for hierarchy, needed for implementation only)
**Outputs:**
- `memory/` hierarchy with root branch index + domain leaf indices (generated)
- Index generation build step (reads entry metadata, produces indices)
- Updated `parse_memory_index()` with recursive traversal
- Migration script/tooling
- Updated hook and skill paths
**Controls:** NFR-1 (scaling), NFR-3 (incremental migration), NFR-4 (token budget targets)
**Mechanism:** sonnet, worktree

**File set:** `src/claudeutils/recall/index_parser.py`, `memory/` hierarchy (in submodule), `agents/memory-index.md` (removed after migration), index generation script, migration script, hook config, skill files (`/when`, `/how`), tests

**Tear decision (S-C/S-D coupling):** FR-5 scope includes "index hierarchy design" but structural decisions (branch/leaf, no mixed indices) are already resolved from design discussion. S-D proceeds with current hierarchy design. If S-C produces different hierarchy recommendations, they feed into S-D's design phase as revision input, not a blocker. The C→D knowledge edge is limited to entry format, not index structure. S-D does NOT depend on S-C.

---

### S-E: Trigger Class & Category Metadata

**What (FR):** Formalize trigger classes (FR-2) and learning categories (FR-3) as IndexEntry metadata.

**How (DP):**
- `IndexEntry.trigger_class: Literal["when", "how"]` — explicit field for implicit prefix distinction
- `IndexEntry.category: Literal["internal", "external", "hybrid"] = "internal"` — default preserves backward compat
- Category derivable from index path (dependency-named domain = external)
- Per-entry class decision, not per-document

**Type:** Implementation
**Readiness:** At most groundable (readiness propagation) — depends on S-C (knowledge dependency: taxonomy validation). If S-C validates when/how taxonomy, readiness upgrades to executable. If S-C suggests alternatives, S-E adapts.

**Inputs:**
- Format specification from S-C (knowledge dependency — taxonomy)
- Unified `IndexEntry` model from S-B (structural dependency)
**Outputs:** IndexEntry with trigger_class and category fields, updated tests
**Controls:** FR-2 (per-entry class decision), FR-3 (partition by dependency)
**Mechanism:** sonnet, worktree

**File set:** `src/claudeutils/recall/models.py`, tests

**Recall note (automation profiles):** Per "when converting external documentation to recall entries" — `how` entries are automation-safe for extraction, `when` entries require hand-curation from operational experience. This distinction informs S-G's pipeline design (corrector intensity differs by class) and S-E's metadata model (class must be available for routing decisions).

**Merge dependency with S-D:** Both modify IndexEntry. S-E must merge after S-D to avoid conflicts. Sequential, not parallel.

---

### S-K: Memory-Corrector Agent

**What (FR):** Clean-context agent that validates all memory writes — bulk conversion (FR-4), `/remember` skill writes (FR-10), and manual entries (FR-11). CURATE role in lifecycle between CREATE (session agent) and CONSUME (resolver).

**How (DP):**
- Agent definition with system prompt encoding quality criteria
- **Quality criteria:** trigger specificity, format compliance (against S-C spec), duplicate detection (against current index), when/how classification accuracy, keyword quality, entry points to permanent documentation (not orphan index entries — per "when adding entries without documentation" decision)
- **Pattern:** follows vet-false-positives "Do NOT Flag" shape — categorical suppression taxonomy, not confidence scores
- **Invocation:** delegated agent called by `/remember` skill (S-L) and extraction pipeline (S-G) — not a standalone workflow
- **Clean context:** agent loads only format spec + current index for dedup check, not session context (avoids anchoring on author's reasoning)
- **Recall loading:** agent definition must include recall mechanism (per "when corrector agents lack recall mechanism" — corrector agents without recall cannot flag project-specific failure modes). Self-contained loading in agent body (option a from the decision)

**Type:** Implementation (agent definition + integration points)
**Readiness:** Designable — agent architecture pattern clear (corrector precedent: design-corrector, outline-corrector, runbook-corrector agents in `.claude/agents/`), but quality criteria weights, suppression taxonomy, and integration protocol need design. Depends on S-C for format spec that defines "compliance."

**Inputs:**
- Format specification from S-C (knowledge dependency — defines valid format for compliance check)
**Outputs:** Memory-corrector agent definition (`.claude/agents/`), quality criteria documentation, suppression taxonomy
**Controls:** FR-11 acceptance criteria
**Mechanism:** opus (agent definition is agentic prose), worktree

**File set:** `.claude/agents/memory-corrector.md` (new), quality criteria reference doc

---

### S-F: Recall Mode Simplification

**What (FR):** Reduce 5 modes to 2 (FR-7). Update 10 pipeline recall points across skills.

**How (DP):**
- Two modes: `default` (per-key, convergence-based) and `all` (per-file, tail-recursive)
- `default` has two recursion loops: structural (navigate hierarchy until leaf entries reached) and semantic (loaded content reveals new relevant domains → re-enter structural traversal → converge when no new domains discovered). Replaces flat-index "two-pass" which assumed all entries visible from one read.
- Remove `broad`, `deep`, `everything` — clean removal, no aliases
- `/recall` skill updated for hierarchical traversal semantics
- 10 pipeline recall points updated in skills

**Type:** Implementation
**Readiness:** Executable (modes decided) — but structurally depends on S-D for hierarchical traversal to be meaningful.

**Inputs:** Hierarchical index from S-D (structural dependency — recursion semantics), consolidated module from S-B (structural dependency)
**Outputs:** Updated `/recall` skill with 2 modes, 10 skill files with updated pipeline recall points
**Controls:** FR-7 acceptance criteria (no behavioral regression)
**Mechanism:** sonnet, worktree

**Design consideration (recognition gap):** Per "when evaluating recall system effectiveness" — hierarchical lookup improves retrieval mechanics but does not address recognition (agent knowing when to look something up). Mode simplification must preserve forced-injection paths (PreToolUse hook, pipeline recall points) that bypass the recognition problem.

**File set:** recall skill, 10+ skill files with pipeline recall points

---

### S-G: Automated Documentation Conversion Pipeline

**What (FR):** Convert external documentation into recall entries (FR-4). First target: anthropic plugins exploration report (`plans/reports/anthropic-plugin-exploration.md`) — comparative analysis with actionable findings, tests a different input shape from API docs. Subsequent targets: pytest, click, pydantic.

**How (DP):**
- Pipeline: source docs → sonnet extraction agent → corrector pass (S-K memory-corrector) → index regeneration (S-D build step)
- Entries can be `when` or `how` per FR-2 (per-entry decision). Pattern/antipattern catalogs default to `when` — the model knows *how* from training; value-add is the situational trigger
- Entries include embedded keyword metadata (FR-1) for index generation
- Corrector validates: trigger specificity, no duplicates, actionable content, format compliance
- Idempotent: re-run on same source produces no duplicates (corrector dedup check)
- Scope includes methodology collections (GOF patterns, refactoring catalogs)
- Context7 MCP as one source option

**Type:** Implementation
**Readiness:** Groundable (propagated) — pipeline architecture needs design (designable intrinsically), but depends on S-C (knowledge: format spec) which is groundable. Readiness propagation: at most groundable until S-C completes, then designable.

**Inputs:**
- Format specification from S-C (knowledge dependency — trigger syntax, validation rules)
- Hierarchical index from S-D (structural dependency — target for integrated entries)
- Token cache from S-A (data dependency — measure generated entry sizes)
- Memory-corrector from S-K (structural dependency — corrector pass in pipeline)
**Outputs:** Extraction pipeline, first target entries integrated into hierarchy
**Controls:** C-1 (format grounding before bulk conversion), C-2 (hierarchy before bulk conversion)
**Mechanism:** sonnet (pipeline), opus (extraction agent design), worktree

**File set:** New pipeline module, generated entry files under `memory/` submodule

---

### S-L: Capture-Time Memory Writes

**What (FR):** Eliminate learnings.md staging area and /codify batch consolidation. Write decisions and memory entries to permanent locations at capture time (FR-10). Delivered as `/remember` skill.

**How (DP):**
- `/remember` skill with tool-gating enforcing corrector pass (agent cannot skip validation)
- `remember: X` directive triggers skill invocation
- Skill handles: routing (target decision file, section), trigger keyword extraction, when/how classification
- Corrector (S-K) invoked as delegated agent — clean context, separate from skill format
- Continuation-prepend support for resume state under context pressure (handoff mid-remember). Uses continuation-passing infrastructure (D-2 `[CONTINUATION: ...]` suffix, D-5 sub-agent isolation by convention)
- Write entry to memory submodule (S-J) with embedded keyword metadata (FR-1)
- Entry must route to permanent documentation (decision file, methodology doc) — not create orphan index entries. Per "when adding entries without documentation": index entries must point somewhere
- Index regeneration triggered after write (S-D build step)
- Remove: `agents/learnings.md`, `/codify` skill, learnings section from `/handoff` skill
- Update `/handoff` — no learnings management, lighter handoff
- Update `learn:`/`remember:` directive behavior in execute-rule.md fragment

**Type:** Implementation (skill definition + write-path tooling)
**Readiness:** Designable — skill architecture clear (tool-gating, agent delegation for corrector, continuation-prepend), but integration details need design: routing heuristic (how skill determines target file/section — Q-6), corrector invocation protocol (synchronous vs deferred — Q-5, resolved during S-K design), index regeneration trigger (immediate vs batched), graceful degradation if corrector rejects.

**Inputs:**
- Memory submodule from S-J (structural dependency — write target)
- Memory-corrector from S-K (structural dependency — validation)
- Hierarchical index from S-D (structural dependency — index regeneration after write)
- Trigger class metadata from S-E (knowledge dependency — when/how classification for new entries)
**Outputs:** `/remember` skill definition, capture-time write tooling, updated `remember:`/`learn:` directive, removed learnings.md + /codify + /handoff learnings section
**Controls:** FR-10 acceptance criteria
**Mechanism:** opus (behavioral changes to agent directives), worktree

**File set:** `/remember` skill definition, new write-path module, `agents/learnings.md` (removed), `/codify` skill (removed), `/handoff` skill (updated), `execute-rule.md` fragment (updated), tests

---

### S-H: Integration Validation

**What (FR):** Verify recall-explore-recall pattern (FR-6) and cross-sub-problem regression after all implementation.

**How (DP):**
- Document recall-explore-recall as retrievable decision entry (FR-6 acceptance criterion)
- Verify pipeline recall points implement convergence-based pattern post-migration
- Confirm `/recall` tail-recursion handles hierarchical traversal
- Verify nested `/recall` invocation from other skills works without special infrastructure (FR-6 acceptance criterion)
- End-to-end `_recall resolve` through full hierarchy in memory submodule
- Verify cross-worktree memory visibility (C-5): write in one worktree, fast-forward in another, resolve succeeds
- Verify capture-time write path (FR-10): `remember:` → `/remember` skill → corrector agent validates → index regenerated → resolvable

**Type:** Validation
**Readiness:** Executable — structurally dependent on S-D (hierarchy), S-F (modes), S-J (submodule), S-L (capture-time writes).

**Inputs:**
- Hierarchical index from S-D (structural dependency — end-to-end traversal target)
- Simplified modes from S-F (structural dependency — pipeline recall points use new modes)
- Memory submodule from S-J (structural dependency — cross-worktree verification)
- Capture-time writes from S-L (structural dependency — write-path verification)
**Outputs:** Decision entry documenting the pattern, regression verification report
**Controls:** FR-6 acceptance criteria, C-5 verification
**Mechanism:** sonnet, in-tree (small, verification only)

**File set:** Decision entry file, test verification

---

## Dependency Graph

```
Edges (source → target, type):
  S-A → S-D  (data: token cache for split threshold measurement)
  S-B → S-D  (structural: unified IndexEntry model, consolidated parser)
  S-B → S-E  (structural: unified IndexEntry model for field additions)
  S-B → S-F  (structural: consolidated module for skill integration)
  S-C → S-E  (knowledge: taxonomy validation — may change trigger classes)
  S-C → S-G  (knowledge: format spec for extraction agent prompts)
  S-C → S-K  (knowledge: format spec defines compliance criteria)
  S-I → S-J  (structural: multi-submodule support for memory submodule lifecycle)
  S-J → S-D  (structural: submodule exists as target location — implementation only, design can proceed)
  S-D → S-E  (merge: both modify IndexEntry — S-E merges after S-D)
  S-D → S-F  (structural: hierarchical traversal for recursive mode semantics)
  S-D → S-G  (structural: hierarchy exists as target for generated entries)
  S-D → S-H  (structural: hierarchy for end-to-end traversal verification)
  S-D → S-L  (structural: index regeneration after capture-time writes)
  S-A → S-G  (data: token cache for measuring generated entry sizes)
  S-K → S-G  (structural: corrector pass in pipeline)
  S-K → S-L  (structural: corrector validates capture-time writes)
  S-J → S-L  (structural: submodule as write target)
  S-E → S-L  (knowledge: trigger class for new entry classification)
  S-F → S-H  (validation: pattern verified with new modes and hierarchy)
  S-J → S-H  (structural: cross-worktree verification)
  S-L → S-H  (structural: capture-time write-path verification)

Absent edges (explicitly independent):
  S-A ⊥ S-B  (disjoint file sets, no data flow)
  S-A ⊥ S-C  (code vs research, no interaction)
  S-A ⊥ S-I  (disjoint: token cache vs worktree code)
  S-B ⊥ S-C  (code vs research, no interaction)
  S-B ⊥ S-I  (disjoint: recall modules vs worktree code)
  S-C ⊥ S-I  (research vs worktree code, no interaction)
  S-C ⊥ S-D  (TEAR: hierarchy structure independent of entry format — see S-D)
  S-E ⊥ S-F  (disjoint file sets: models.py vs skill files)
  S-E ⊥ S-G  (disjoint: metadata fields vs pipeline module)
  S-F ⊥ S-G  (disjoint: skill mode logic vs pipeline module)
  S-F ⊥ S-L  (disjoint: mode simplification vs write-path)
  S-G ⊥ S-L  (disjoint: bulk pipeline vs capture-time writes — both use S-K corrector but don't interact)
  S-K ⊥ S-D  (disjoint: agent definition vs parser/hierarchy code)
  S-K ⊥ S-F  (disjoint: agent definition vs mode logic)
  S-I ⊥ S-E  (disjoint: worktree code vs recall metadata)
  S-I ⊥ S-F  (disjoint: worktree code vs recall modes)
```

## Bands (Partial Ordering)

```
Band 0 (roots — no dependencies):
  S-A: Token Count Cache              [executable]
  S-B: Recall Module Consolidation    [executable]
  S-C: Memory Format Grounding        [groundable]
  S-I: Worktree Multi-Submodule       [executable]

  Parallelism: 4 concurrent — all file sets disjoint.

Band 1 (depends on Band 0):
  S-J: Memory Submodule Setup         [designable]
    needs: S-I (structural)
  S-D: Hierarchical Index Structure   [designable]
    needs: S-A (data), S-B (structural), S-J (structural — implementation only)

  Note: S-D design can start once S-A and S-B complete. S-D implementation
  gates on S-J. S-C may still be in progress (groundable, longer duration).
  S-J and S-D design are parallelizable; S-D implementation is sequential after S-J.

Band 2 (depends on Bands 0-1):
  S-E: Trigger Class & Category       [groundable → executable after S-C]
    needs: S-B (structural), S-C (knowledge), S-D (merge order)
  S-F: Recall Mode Simplification     [executable]
    needs: S-B (structural), S-D (structural)
  S-K: Memory-Corrector Agent         [designable]
    needs: S-C (knowledge)
  S-G: Documentation Pipeline         [groundable → designable after S-C]
    needs: S-A (data), S-C (knowledge), S-D (structural), S-K (structural)

  Parallelism: S-E, S-F, S-K pairwise file-set-disjoint — 3 concurrent.
  S-G gates on S-K (corrector) in addition to S-C and S-D.
  Max 4 concurrent if S-C completed. If S-C pending, only S-F starts.

Band 3 (depends on Bands 1-2):
  S-L: Capture-Time Memory Writes     [designable]
    needs: S-J (structural), S-K (structural), S-D (structural), S-E (knowledge)
  S-H: Integration Validation          [executable]
    needs: S-D (structural), S-F (validation), S-J (structural), S-L (structural)

  S-L must complete before S-H (S-H verifies capture-time write-path).
  Effective ordering: S-L → S-H (terminal).
```

## Tear Points

**T-1: S-C/S-D (format grounding / hierarchical index):**
Index hierarchy structure (branch/leaf, no mixed indices) is resolved from design discussion. S-D proceeds without waiting for S-C. If S-C's hierarchy recommendations differ, they enter S-D's design as revision input. Risk: rework on parser if grounding changes branching factor or navigation semantics. Mitigation: parser's recursive traversal is format-agnostic — hierarchy depth/shape changes don't affect traversal algorithm.

**T-2: S-C/S-E (format grounding / metadata):**
Not torn — S-E explicitly waits for S-C. This is the Phase 4/5 inversion fix. Readiness propagation: S-E is groundable until S-C completes. Cost: S-E is blocked during Band 0-1. Benefit: no rework if grounding changes taxonomy.

**T-3: S-J/S-D (submodule setup / hierarchical index):**
S-D's design phase can proceed without S-J (design questions are about hierarchy structure, not storage location). Only S-D's implementation needs the submodule to exist. S-J is a Band 1 prerequisite for S-D implementation, not S-D design. Risk: low — submodule path is a configuration input to S-D, not an architectural constraint.

## Completeness Check (100% Rule)

| FR/NFR/C | Sub-problem | Coverage |
|----------|------------|----------|
| FR-1 | S-A (cache prereq) + S-D (hierarchy + generated index) | Token-counted splits, arbitrary nesting, parser, migration, embedded keywords, index generation |
| FR-2 | S-E | Trigger class metadata |
| FR-3 | S-E | Learning categories, dependency partitioning |
| FR-4 | S-G | Extraction pipeline, corrector, first targets |
| FR-5 | S-C | Format grounding research |
| FR-6 | S-H | Pattern documentation and regression verification |
| FR-7 | S-F | Mode reduction, pipeline point updates |
| FR-8 | S-B | Module merge, model unification, deprecation alias |
| FR-9 | S-I (prereq) + S-J (submodule) | Multi-submodule refactor, submodule creation, propagation, path update |
| FR-10 | S-L | Capture-time writes, learnings.md removal, /codify removal, /handoff update |
| FR-11 | S-K | Memory-corrector agent definition, quality criteria, suppression taxonomy |
| NFR-1 | S-D | Hierarchical lookup scales with tree depth, not entry count |
| NFR-2 | S-B (deprecation alias) + S-D (path migration) | Backward compat during transition |
| NFR-3 | S-D | Incremental migration strategy |
| NFR-4 | S-A (measurement) + S-D (threshold) | Token budget as design target |
| C-1 | S-C → S-G edge | Format before bulk conversion |
| C-2 | S-D → S-G edge | Hierarchy before bulk conversion |
| C-3 | S-A → S-D edge | Token counting before split |
| C-4 | S-B + accounting table below | Infrastructure accounting |
| C-5 | S-J + S-H (verification) | Cross-worktree visibility via shared branch |
| C-6 | S-I | Multi-submodule support with per-submodule strategy |

**C-4 infrastructure accounting:**

| Infrastructure item | Handling sub-problem |
|---|---|
| `src/claudeutils/recall/` (9 modules) | S-B (consolidation target) |
| `src/claudeutils/recall_cli/` (2 modules) | S-B (merged into recall/) |
| `src/claudeutils/when/` (5 modules) | S-B (merged into recall/) |
| `agents/memory-index.md` (366 entries) | S-D (migrated to hierarchy in submodule) |
| `agents/learnings.md` | S-L (removed) |
| `/recall` skill | S-F (mode simplification) |
| `/when` and `/how` skills | S-D (path updates), S-B (CLI alias) |
| `/codify` skill | S-L (removed) |
| pretooluse-recall-check hook | S-D (path update to submodule) |
| 22 test files | S-B (consolidated with shared fixtures) |

**Mutual exclusivity check:** No two sub-problems produce the same deliverable. S-I (worktree multi-submodule) and S-J (memory submodule setup) are distinct: S-I refactors the worktree lifecycle code to be submodule-aware, S-J creates and configures the specific memory submodule. S-K (corrector agent definition) is consumed by both S-G (pipeline) and S-L (capture-time) but neither produces it. S-D produces the hierarchy and index generation; S-L and S-G produce entries that flow into S-D's generated index — producer/consumer, not overlap.

## Readiness Summary

| Sub-problem | Readiness | Blocker | Pipeline routing |
|------------|-----------|---------|-----------------|
| S-A | Executable | — | `/runbook` → `/orchestrate` |
| S-B | Executable | — | `/runbook` → `/orchestrate` |
| S-C | Groundable | — | `/ground` |
| S-I | Executable | — | `/runbook` → `/orchestrate` |
| S-J | Designable | S-I | `/design` → `/runbook` |
| S-D | Designable | S-A, S-B, S-J (impl) | `/design` → `/runbook` |
| S-E | Groundable (propagated) | S-C, S-D | Wait for S-C → `/runbook` |
| S-F | Executable | S-D | `/runbook` → `/orchestrate` |
| S-K | Designable | S-C | Wait for S-C → `/design` → `/runbook` |
| S-G | Groundable (propagated) | S-A, S-C, S-D, S-K | Wait for S-C → `/design` → `/runbook` |
| S-L | Designable | S-J, S-K, S-D, S-E | `/design` → `/runbook` |
| S-H | Executable | S-D, S-F, S-J, S-L | `/runbook` or inline |

## Scope Boundaries

**IN:**
- Token count caching (sqlite/sqlalchemy)
- Module consolidation (recall + recall_cli + when → unified recall)
- Memory format grounding research
- Worktree multi-submodule refactor (42 hardcoded refs → configurable registry)
- Memory submodule creation with shared branch + fast-forward propagation
- Hierarchical index with arbitrary nesting, branch/leaf separation, generated from embedded metadata
- Trigger class and learning category metadata
- Recall mode reduction (5 → 2)
- Memory-corrector agent (validates all memory writes)
- Capture-time memory writes (eliminates learnings.md, /codify)
- Documentation conversion pipeline (first targets: plugin exploration report, pytest, click, pydantic)
- Hook and skill path updates
- 22 test files migrated
- Deprecation alias for `_when` CLI
- Cross-worktree memory visibility verification

**OUT:**
- Post-resolve scoring / usage tracking
- Stage provenance tags
- Recall-artifact rejection tracking
- Lifecycle role contract enforcement
- PreToolUse lint-gated recall hook
- SWE-ContextBench benchmarking
- Version-change detection implementation (mechanism selected in design, implementation deferred)
- Concurrent write conflict resolution beyond fast-forward (Q-3 — design identifies strategy, implementation deferred if complex)

## Open Questions for Design

- Q-1: Token budget threshold for index/content splits (NFR-4) — measured during S-D design using S-A cache
- Q-2: Grouping heuristic for related decision files → domain mapping — resolved during S-D design
- Q-3: Concurrent write handling (FR-9 Q-3) — fast-forward fails → strategy needed. Resolved during S-J design. May defer implementation if complex
- Q-4: Version-change detection mechanism for FR-3 external entries — mechanism selection during S-E design, implementation deferred past this project (OUT of scope). FR-3 acceptance criterion "Version-change detection mechanism defined (design phase)" is satisfied by design-only output from S-E; implementation is deferred
- Q-5: Corrector timing (FR-11 Q-5) — synchronous vs post-handoff vs async. Resolved during S-K design. Trade-off: write latency vs quality assurance
- Q-6: Capture-time write routing heuristic (FR-10 Q-4) — how agent determines target file/section. Resolved during S-L design
- Q-7: Migration strategy for existing content into submodule — migrate flat first (S-J) then restructure (S-D), or create empty submodule (S-J) and build hierarchy directly (S-D). Resolved during S-J design

## Risks

- **S-C invalidating S-D decisions:** Mitigated by tear point T-1 — hierarchy structure is format-agnostic. Only entry format changes would affect parser, not traversal.
- **S-C invalidating when/how taxonomy:** Mitigated by NOT tearing T-2 — S-E waits for S-C. Cost is schedule (S-E blocked during Bands 0-1), benefit is no rework.
- **Test migration scope (S-B):** 22 test files, shared fixtures, import path changes. High mechanical effort but well-scoped.
- **Pipeline recall point updates (S-F):** 10+ skills reference recall modes. Broad but mechanical.
- **Backward compat window:** Old CLI paths need deprecation. Risk of breaking worktree sessions using old paths during S-D migration.
- **S-D scope:** Largest sub-problem (parser, migration, hook, skill paths, index generation). May need internal decomposition during `/design` phase. Leaf-schedulable at this level — enters pipeline once, runbook handles internal steps.
- **Multi-submodule refactor ripple (S-I):** 42 references across 4 files. Risk: subtle behavioral differences between branch-per-worktree and single-shared-branch strategies during edge cases (merge conflicts, interrupted operations). Mitigation: existing test coverage for worktree operations provides regression detection.
- **Known submodule failure modes (S-I, S-J):** Four documented failure patterns from recall: (1) `core.worktree` config stale after worktree removal — must restore to main checkout path; (2) submodule commits diverge during orchestration — linear history verification needed at phase boundaries; (3) task agents skip parent repo submodule pointer updates — orchestrator must check `git status` post-step; (4) no-op merge orphans branch — always create merge commit. S-I's strategy dispatch and S-J's propagation mechanism must account for all four.
- **Capture-time write quality (S-L):** Agent determines file/section routing at capture time with limited context for structural decisions. Risk: misrouted entries accumulate. Mitigation: S-K corrector validates every write, but corrector timing (Q-5) affects feedback latency.
- **Submodule propagation reliability (S-J):** Fast-forward-on-first-read assumes linear history on shared branch. Concurrent writes from multiple worktrees could create non-fast-forwardable state. Mitigation: Q-3 design decision; single-shared-branch model constrains this by design.
