# Active Recall System: Design Outline (Redraft)

Decomposition via DSM banding + Axiomatic Design zigzag + TRL readiness scale. Replaces prior linear Phase 1-6 outline that conflated sub-problems with execution ordering.

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

**What (FR):** Unify three modules into one recall interface (FR-8). Includes NFR-2 deprecation alias for `_when` CLI.

**How (DP):** Merge `when/` resolver + `recall_cli/` into `recall/`. Unify `IndexEntry` and `WhenEntry` into single model. `_recall` as canonical CLI group, `_when` as thin deprecation alias with warning. 22 test files consolidated with shared fixtures.

**Type:** Implementation (refactor + migration)
**Readiness:** Executable — merge targets identified, model unification approach clear.

**Inputs:** `src/claudeutils/recall/` (9 modules), `src/claudeutils/recall_cli/` (2 modules), `src/claudeutils/when/` (5 modules), 22 test files (pre-existing)
**Outputs:** Unified `src/claudeutils/recall/` module with single `IndexEntry` model, single CLI group, deprecation alias
**Controls:** NFR-2 (backward compat during migration), C-4 (infrastructure accounting)
**Mechanism:** sonnet, worktree

**File set:** `src/claudeutils/recall/`, `src/claudeutils/recall_cli/`, `src/claudeutils/when/`, `tests/` (22 files)

---

### S-C: Memory Format Grounding

**What (FR):** Ground trigger format, when/how distinction, naming conventions before bulk conversion (FR-5). Research may suggest formats beyond current when/how — remain open.

**How (DP):** `/ground` skill — research trigger naming conventions, trigger structure formalization, index hierarchy validation (branching factor, navigation). Produce format specification consumable by S-G's extraction agent.

**Type:** Design input (research)
**Readiness:** Groundable — open research question, unknown output shape.

**Inputs:** Existing 366 entries in `agents/memory-index.md`, current when/how format, brief.md vision (pre-existing)
**Outputs:** `plans/reports/memory-format-grounding.md` — format specification with trigger syntax, validation rules, taxonomy decision
**Controls:** C-1 (must complete before FR-4 bulk conversion)
**Mechanism:** opus, worktree

**File set:** No code changes — research artifact only

---

### S-D: Hierarchical Index Structure

**What (FR):** Migrate flat index to tree structure with arbitrary nesting (FR-1). Includes parser updates, migration tooling, hook/skill path updates, recall loop update for multi-level traversal.

**How (DP):**
- Branch indices (index-of-indices only) vs leaf indices (entries only) — no mixed indices
- Parser detects index type, traverses recursively at arbitrary depth
- Migration script splits `agents/memory-index.md` into `agents/memory/` hierarchy
- Domain path mapping: space → `/` (parent-child) or `-` (compound noun)
- Token budget threshold measurement using S-A cache to determine split boundaries
- pretooluse-recall-check hook updated from `memory-index.md` to `agents/memory/index.md`
- `/when` and `/how` skill paths updated for new index location

**Type:** Implementation
**Readiness:** Designable — structural decisions resolved (branch/leaf, no mixed), but traversal semantics, migration tooling details, token budget threshold, and incremental migration strategy (NFR-3) need design.

**Inputs:**
- Unified `IndexEntry` model from S-B (structural dependency)
- Token cache from S-A (data dependency — split threshold measurement)
**Outputs:**
- `agents/memory/` hierarchy with root branch index + domain leaf indices
- Updated `parse_memory_index()` with recursive traversal
- Migration script/tooling
- Updated hook and skill paths
**Controls:** NFR-1 (scaling), NFR-3 (incremental migration), NFR-4 (token budget targets)
**Mechanism:** sonnet, worktree

**File set:** `src/claudeutils/recall/index_parser.py`, `agents/memory/` (new), `agents/memory-index.md` (removed after migration), migration script, hook config, skill files (`/when`, `/how`), tests

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

**Merge dependency with S-D:** Both modify IndexEntry. S-E must merge after S-D to avoid conflicts. Sequential, not parallel.

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

**File set:** recall skill, 10+ skill files with pipeline recall points

---

### S-G: Automated Documentation Conversion Pipeline

**What (FR):** Convert external documentation into recall entries (FR-4). First target: anthropic plugins exploration report (`plans/reports/anthropic-plugin-exploration.md`) — comparative analysis with actionable findings, tests a different input shape from API docs. Subsequent targets: pytest, click, pydantic.

**How (DP):**
- Pipeline: source docs → sonnet extraction agent → corrector pass → index integration
- Entries can be `when` or `how` per FR-2 (per-entry decision)
- Corrector validates: trigger specificity, no duplicates, actionable content
- Idempotent: re-run on same source produces no duplicates
- Scope includes methodology collections (GOF patterns, refactoring catalogs)
- Context7 MCP as one source option

**Type:** Implementation
**Readiness:** Groundable (propagated) — pipeline architecture needs design (designable intrinsically), but depends on S-C (knowledge: format spec) which is groundable. Readiness propagation: at most groundable until S-C completes, then designable.

**Inputs:**
- Format specification from S-C (knowledge dependency — trigger syntax, validation rules)
- Hierarchical index from S-D (structural dependency — target for integrated entries)
- Token cache from S-A (data dependency — measure generated entries)
**Outputs:** Extraction pipeline, first target entries integrated into hierarchy
**Controls:** C-1 (format grounding before bulk conversion), C-2 (hierarchy before bulk conversion)
**Mechanism:** sonnet (pipeline), opus (extraction agent design), worktree

**File set:** New pipeline module, generated index files under `agents/memory/`

---

### S-H: Integration Validation

**What (FR):** Verify recall-explore-recall pattern (FR-6) and cross-sub-problem regression after all implementation.

**How (DP):**
- Document recall-explore-recall as retrievable decision entry (FR-6 acceptance criterion)
- Verify pipeline recall points implement convergence-based pattern post-migration
- Confirm `/recall` tail-recursion handles hierarchical traversal
- End-to-end `_recall resolve` through full hierarchy

**Type:** Validation
**Readiness:** Executable — structurally dependent on S-D (hierarchy must exist for traversal verification) and S-F (modes must be simplified for pipeline point verification).

**Inputs:**
- Hierarchical index from S-D (structural dependency — end-to-end traversal target)
- Simplified modes from S-F (structural dependency — pipeline recall points use new modes)
**Outputs:** Decision entry documenting the pattern, regression verification report
**Controls:** FR-6 acceptance criteria
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
  S-D → S-E  (merge: both modify IndexEntry — S-E merges after S-D)
  S-D → S-F  (structural: hierarchical traversal for recursive mode semantics)
  S-A → S-G  (data: token cache for measuring generated entry sizes)
  S-D → S-G  (structural: hierarchy exists as target for generated entries)
  S-D → S-H  (structural: hierarchy must exist for end-to-end traversal verification)
  S-F → S-H  (validation: pattern verified with new modes and hierarchy)

Absent edges (explicitly independent):
  S-A ⊥ S-B  (disjoint file sets, no data flow)
  S-A ⊥ S-C  (code vs research, no interaction)
  S-B ⊥ S-C  (code vs research, no interaction)
  S-C ⊥ S-D  (TEAR: hierarchy structure independent of entry format — see S-D)
  S-E ⊥ S-F  (disjoint file sets: models.py vs skill files)
  S-E ⊥ S-G  (disjoint: metadata fields vs pipeline module)
  S-E ⊥ S-H  (disjoint: metadata fields vs pattern verification)
  S-F ⊥ S-G  (disjoint: skill mode logic vs pipeline module)
  S-G ⊥ S-H  (disjoint: pipeline module vs pattern verification)
```

## Bands (Partial Ordering)

```
Band 0 (roots — no dependencies):
  S-A: Token Count Cache          [executable]
  S-B: Recall Module Consolidation [executable]
  S-C: Memory Format Grounding     [groundable]

  Parallelism: 3 concurrent — all file sets disjoint.

Band 1 (depends on Band 0):
  S-D: Hierarchical Index Structure [designable]
    needs: S-A (data), S-B (structural)

  Parallelism: 1. S-C may still be in progress (groundable, longer duration).

Band 2 (depends on Band 1):
  S-E: Trigger Class & Category    [groundable → executable after S-C]
    needs: S-B (structural), S-C (knowledge), S-D (merge order)
  S-F: Recall Mode Simplification  [executable]
    needs: S-B (structural), S-D (structural)
  S-G: Documentation Pipeline      [groundable → designable after S-C]
    needs: S-A (data), S-C (knowledge), S-D (structural)

  Parallelism: S-E, S-F, S-G are pairwise file-set-disjoint.
  Max 3 concurrent if S-C has completed. If S-C pending, only S-F starts.
  S-E and S-G gate on S-C completion.

Band 3 (depends on Band 1 + Band 2):
  S-H: Integration Validation      [executable]
    needs: S-D (structural), S-F (validation)

  Parallelism: 1. Terminal node.
```

## Tear Points

**T-1: S-C/S-D (format grounding / hierarchical index):**
Index hierarchy structure (branch/leaf, no mixed indices) is resolved from design discussion. S-D proceeds without waiting for S-C. If S-C's hierarchy recommendations differ, they enter S-D's design as revision input. Risk: rework on parser if grounding changes branching factor or navigation semantics. Mitigation: parser's recursive traversal is format-agnostic — hierarchy depth/shape changes don't affect traversal algorithm.

**T-2: S-C/S-E (format grounding / metadata):**
Not torn — S-E explicitly waits for S-C. This is the Phase 4/5 inversion fix. Readiness propagation: S-E is groundable until S-C completes. Cost: S-E is blocked during Band 0-1. Benefit: no rework if grounding changes taxonomy.

## Completeness Check (100% Rule)

| FR/NFR | Sub-problem | Coverage |
|--------|------------|----------|
| FR-1 | S-A (cache prereq) + S-D (hierarchy) | Token-counted splits, arbitrary nesting, parser, migration |
| FR-2 | S-E | Trigger class metadata |
| FR-3 | S-E | Learning categories, dependency partitioning |
| FR-4 | S-G | Extraction pipeline, corrector, first targets |
| FR-5 | S-C | Format grounding research |
| FR-6 | S-H | Pattern documentation and regression verification |
| FR-7 | S-F | Mode reduction, pipeline point updates |
| FR-8 | S-B | Module merge, model unification, deprecation alias |
| NFR-1 | S-D | O(log_k(N)) hierarchical lookup |
| NFR-2 | S-B (deprecation alias) + S-D (path migration) | Backward compat during transition |
| NFR-3 | S-D | Incremental migration strategy |
| NFR-4 | S-A (measurement) + S-D (threshold) | Token budget as design target |
| C-1 | S-C → S-G edge | Format before bulk conversion |
| C-2 | S-D → S-G edge | Hierarchy before bulk conversion |
| C-3 | S-A → S-D edge | Token counting before split |
| C-4 | S-B | Infrastructure accounting |

**Mutual exclusivity check:** FR-1 spans S-A (cache prerequisite) and S-D (hierarchy implementation) — this is a prerequisite-to-consumer relationship, not scope overlap. S-A's deliverable (cache API) is fully distinct from S-D's deliverable (hierarchy + parser + migration). S-B provides model consumed by S-D, S-E, S-F (structural prerequisite, not overlap). No two sub-problems produce the same deliverable.

## Readiness Summary

| Sub-problem | Readiness | Blocker | Pipeline routing |
|------------|-----------|---------|-----------------|
| S-A | Executable | — | `/runbook` → `/orchestrate` |
| S-B | Executable | — | `/runbook` → `/orchestrate` |
| S-C | Groundable | — | `/ground` |
| S-D | Designable | S-A, S-B | `/design` → `/runbook` |
| S-E | Groundable (propagated) | S-C, S-D | Wait for S-C → `/runbook` |
| S-F | Executable | S-D | `/runbook` → `/orchestrate` |
| S-G | Groundable (propagated) | S-A, S-C, S-D | Wait for S-C → `/design` → `/runbook` |
| S-H | Executable | S-D, S-F | `/runbook` or inline |

## Scope Boundaries

**IN:**
- Token count caching (sqlite/sqlalchemy)
- Module consolidation (recall + recall_cli + when → unified recall)
- Memory format grounding research
- Hierarchical index with arbitrary nesting, branch/leaf separation
- Trigger class and learning category metadata
- Recall mode reduction (5 → 2)
- Documentation conversion pipeline (first targets: pytest, click, pydantic)
- Hook and skill path updates
- 22 test files migrated
- Deprecation alias for `_when` CLI

**OUT:**
- Post-resolve scoring / usage tracking
- Stage provenance tags
- Recall-artifact rejection tracking
- Lifecycle role contract enforcement
- PreToolUse lint-gated recall hook
- SWE-ContextBench benchmarking
- Version-change detection implementation (mechanism selected in design, implementation deferred)

## Open Questions for Design

- Q-1: Token budget threshold for index/content splits (NFR-4) — measured during S-D design using S-A cache
- Q-2: Grouping heuristic for related decision files → `workflow/` domain mapping — resolved during S-D design
- Q-3: Root index metadata format (keywords, entry counts per domain) — resolved during S-D design
- Q-4: Version-change detection mechanism for FR-3 external entries — mechanism selection during S-D/S-E design (per requirements Q-1), implementation deferred past this project (OUT of scope)
- Q-5: Migration tooling approach (script vs manual) — resolved during S-D design

## Risks

- **S-C invalidating S-D decisions:** Mitigated by tear point T-1 — hierarchy structure is format-agnostic. Only entry format changes would affect parser, not traversal.
- **S-C invalidating when/how taxonomy:** Mitigated by NOT tearing T-2 — S-E waits for S-C. Cost is schedule (S-E blocked during Bands 0-1), benefit is no rework.
- **Test migration scope (S-B):** 22 test files, shared fixtures, import path changes. High mechanical effort but well-scoped.
- **Pipeline recall point updates (S-F):** 10+ skills reference recall modes. Broad but mechanical.
- **Backward compat window:** Old CLI paths need deprecation. Risk of breaking worktree sessions using old paths during S-D migration.
- **S-D scope:** Largest sub-problem (parser, migration, hook, skill paths). May need internal decomposition during `/design` phase. Leaf-schedulable at this level — enters pipeline once, runbook handles internal steps.
