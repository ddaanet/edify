# Active Recall System: Design Outline

## Approach

Six phases, dependency-ordered per constraints C-1 through C-3. Each phase is independently deployable — partial completion leaves the system functional.

## Phase 1: Token Count Caching (C-3 prerequisite)

Token counting infrastructure already exists (`src/claudeutils/tokens.py`, `tokens_cli.py` — Anthropic API, model alias resolution, multi-file support). What's missing is a **token count cache** to avoid redundant API calls during migration and authoring workflows.

- **Storage:** sqlite via sqlalchemy — O(1) indexed lookup, handles concurrent worktree access, growth path for future caches (Context7, recall usage)
- **Cache key:** `(md5_hex, model_id)` composite — md5 sufficient for non-adversarial local cache, model in key because different models tokenize differently
- **Schema:** single table via `metadata.create_all()`, no alembic. Columns: `md5 TEXT`, `model TEXT`, `count INTEGER`, `last_used TEXT`. Composite primary key on `(md5, model)`.
- **Cache location:** `platformdirs.user_cache_dir("claudeutils") / "token_cache.db"`
- **Eviction:** `last_used` updated on every hit. Periodic prune of entries older than N days (on write, not on read).
- **Integration:** into existing `count_tokens_for_file()` — check cache before API call
- **CLI unchanged:** `claudeutils tokens <path>` already works, just becomes faster on repeated calls
- **New dependency:** `sqlalchemy` (core + ORM, no alembic, no async)

## Phase 2: Recall Tool Consolidation (FR-8)

Merge three modules into one before changing index structure. Reduces migration surface.

**Current state (discovered via exploration):**
- `recall/` (9 files) — recall *analysis* (measuring agent behavior, not resolution). Models: `IndexEntry`, `RecallAnalysis`, `EntryRecall`, `DiscoveryPattern`. This is a measurement/analytics tool.
- `recall_cli/` (3 files) — `_recall` CLI commands (resolve, check, diff). Uses `when/resolver.py` for actual resolution.
- `when/` (6 files) — core resolver: `WhenEntry` model, fuzzy matching, section extraction, heading search. Also the `_when` CLI.

**Consolidation approach:**
- Merge `when/` resolver, fuzzy, index_parser into `recall/` (the resolver is the core capability)
- Merge `recall_cli/` into `recall/cli.py` (already has a cli.py for analysis — combine under one Click group)
- Unify `IndexEntry` and `WhenEntry` models into single model (they parse the same format with different fields)
- Keep `_recall` as the canonical CLI group. `_when` becomes a thin alias during deprecation, then removed
- `/when` and `/how` skills updated to use `claudeutils _recall resolve` (already do via allowed-tools)
- 22 test files consolidated — shared fixtures, no coverage loss
- Deprecation: `_when` CLI warns on use, removed after one release cycle

## Phase 3: Hierarchical Index Structure (FR-1)

Migrate flat `agents/memory-index.md` to `agents/memory/` hierarchy.

**Structure:**
```
agents/memory/index.md                    # Root (branch): domain list + paths + keywords
agents/memory/cli/index.md               # Leaf: entries for cli.md
agents/memory/testing/index.md           # Leaf: entries for testing.md
agents/memory/workflow/index.md          # Branch: points to sub-domain leaves
agents/memory/workflow/core/index.md     # Leaf: entries from workflow-core.md
agents/memory/workflow/planning/index.md # Leaf: entries from workflow-planning.md
agents/memory/pydantic/index.md          # Branch: points to version leaves
agents/memory/pydantic/v2/index.md       # Leaf: version-specific entries
```

**Index types (no mixed indices):**
- **Branch index:** contains only references to child indices (with keywords, entry counts). No inline entries. Used for root index and intermediate grouping nodes.
- **Leaf index:** contains only entries (`/when trigger | extras`) and/or references to content files. No child references.
- **Rationale:** Mixed indices create discoverability imbalance — inline entries are immediately visible and individually selectable, while child-referenced entries require an extra navigation step. Clean separation ensures uniform discovery paths for all entries.

**Design decisions:**
- Key structure: prefix-free, colon-delimited domains — `<key>` at root, `<domain>: <key>` nested. Prefix-free constraint functions as quality signal (verbose keys creating prefix collisions should be tightened). (From design discussion.)
- Domain path mapping: space in domain name maps contextually to `/` (hierarchical parent-child) or `-` (compound noun). `workflow planning` → `workflow/planning/` (planning is sub-domain of workflow). `code smells` → `code-smells/` (compound noun, no parent-child). Decision made at domain creation, validated by corrector during bulk conversion.
- Hyphen (`-`) for compound-noun separators — consistent with project convention (decision files, plan directories all use hyphens)
- Version sub-domains: dependency domains can have version children. `pydantic/v2/` enables FR-3 subtree-scoped re-evaluation at version granularity.
- Domain names derived from decision file names (strip `agents/decisions/` prefix, strip `.md`)
- Related files grouped: `workflow-core.md`, `workflow-advanced.md`, `workflow-planning.md`, `workflow-execution.md`, `workflow-optimization.md` → `workflow/` branch with per-file leaves
- Split trigger: file exceeds token budget (design target from NFR-4, determined in design phase)
- Branch index format: domain name + path + entry count + keywords (keywords enable domain selection without loading child indices)
- Leaf index format: same as current memory-index entries (`/when trigger | extras`)
- Memory content files (decision file sections) remain in `agents/decisions/` — index reorganization only, not content relocation

**Parser changes:**
- `parse_memory_index()` updated: detect branch index (contains child references) vs leaf index (contains entries) — two distinct line types, no mixed mode
- Branch index lines: `## domain-name` followed by child path, entry count, and keywords
- Leaf index lines: `/when trigger | extras` or `/how trigger | extras`
- Recursive traversal: root (branch) → intermediate branches → leaves, arbitrary depth
- `_recall resolve` follows the chain transparently

**Recall loop update (FR-1 acceptance criterion):**
- Current: skill reads memory-index.md, selects entries, resolves via CLI
- New: skill reads `agents/memory/index.md` (root), navigates to relevant domain indices, selects entries
- `default` mode: resolve until all items are entries (not further indices) — FR-7 requirement
- `all` mode: tail-recursive through domain indices

**Scaling (NFR-1):**
- Hierarchical lookup is O(log_k(N)) with branching factor k — root index narrows to domain, domain index narrows to entry
- Agent context budget: only root index + selected domain index loaded per recall invocation (not full corpus)
- Branching factor and per-file token budget (NFR-4, Q-1) jointly determine max entries per level — design phase sets thresholds

**Backward compatibility (NFR-2):**
- `claudeutils _recall resolve` — preserved, follows hierarchy transparently
- `claudeutils _recall check` — preserved, validates against hierarchical structure
- `claudeutils _recall diff` — preserved, diff semantics unchanged
- `claudeutils _when` — thin alias during deprecation, removed after one release cycle
- `/when` and `/how` skills — updated to use `_recall resolve` (already do via allowed-tools)
- pretooluse-recall-check hook — updated for new index path (see Phase 3 hook update below)

**Migration strategy (NFR-3):**
- Write `agents/memory/index.md` referencing both migrated domain files and unmigrated sections inline
- Parser handles mixed format: child references AND inline entries in same file
- Migrate one domain at a time, validate `_recall resolve` works after each

**PreToolUse hook update:**
- pretooluse-recall-check hook references memory-index.md path — update to `agents/memory/index.md`
- Hook logic may need adjustment for hierarchical traversal (currently checks flat index)

**Existing infrastructure accounting (C-4):**
- `src/claudeutils/recall/` (9 modules) — consolidated in Phase 2
- `src/claudeutils/recall_cli/` (2 modules) — merged in Phase 2
- `src/claudeutils/when/` (5 modules) — merged in Phase 2
- `agents/memory-index.md` (366 entries) — migrated in Phase 3
- `/recall` skill — updated for two modes in Phase 4 (FR-7)
- `/when` and `/how` skills — updated for `_recall resolve` path in Phase 2
- pretooluse-recall-check hook — updated for new index path in Phase 3
- 20+ test files — consolidated in Phase 2 (22 files identified)

## Phase 4: Trigger Class Formalization (FR-2) + Learning Categories (FR-3)

Metadata additions to the unified index model. Lightweight — builds on consolidated model from Phase 2.

**Ordering note:** Phase 4 commits to metadata fields before Phase 5 grounding validates the taxonomy. Risk: grounding may suggest alternatives to `when`/`how` or `internal`/`external`/`hybrid`. Mitigation: metadata fields are additive (new fields on existing model) — if grounding changes taxonomy, model fields change but code structure (Phase 2-3) is unaffected. Accept this risk to avoid blocking all metadata work on grounding research.

**FR-2: Trigger class:**
- Already implicit in `/when` vs `/how` prefix. Make explicit in `IndexEntry.trigger_class: Literal["when", "how"]`
- Per-entry decision, not per-document. Same domain index can mix `when` and `how` entries
- No behavioral change to resolution — metadata only
- Recall-informed: `when` entries require hand-curation (situational triggers from operational experience); `how` entries are automation-safe (task-descriptive, extractable from documentation headings). This distinction affects FR-4 pipeline design — corrector intensity differs by class.

**FR-3: Learning categories:**
- Add `IndexEntry.category: Literal["internal", "external", "hybrid"] = "internal"` (default preserves backward compat)
- External entries grouped by dependency in index hierarchy (e.g., `agents/memory/pytest/index.md`)
- Category derivable from index path: entries under a dependency-named domain are external
- Version detection: deferred to design (Q-1 — multiple valid approaches)

**Recall mode simplification (FR-7):**
- Remove `everything` mode from `/recall` skill
- Remove `broad` and `deep` modes (no aliases)
- Two modes remain: `default` (per-key, two passes) and `all` (per-file, tail-recursive)
- Update 10 pipeline recall points across skills

## Phase 5: Memory Format Grounding (FR-5)

Research prerequisite before bulk conversion. Uses `/ground` skill.

- Ground trigger naming conventions, when/how distinction, index hierarchy design
- Research may suggest formats beyond current when/how — remain open
- Produce format specification in `plans/reports/memory-format-grounding.md`
- Validate existing 366 entries against grounded format
- Output consumed by Phase 6 extraction agent

## Phase 6: Automated Documentation Conversion Pipeline (FR-4)

Bulk conversion with grounded format. Depends on Phases 1, 3, 5.

- Pipeline: source docs → sonnet extraction agent → corrector pass → index integration
- First targets: pytest, click, pydantic (project dependencies)
- Entries can be `when` or `how` per FR-2 (per-entry decision)
- Scope includes methodology collections (GOF patterns, refactoring catalogs)
- Corrector validates: trigger specificity, no duplicates, actionable content
- Idempotent: re-run on same source produces no duplicates
- Context7 MCP as one source option (query-keyed cache, not bulk import)

## Cross-Cutting: Recall-Explore-Recall Pattern (FR-6)

Not a separate phase — documented as a decision entry during Phase 4. Pattern already works via `/recall` skill's tail-recursion. Confirm no regression after Phase 3 index changes.

- Document pattern as a retrievable `when` entry in the recall index (FR-6 acceptance criterion)
- Verify pipeline recall points (design A.1, runbook Phase 0.5) implement the two-pass pattern post-migration
- Confirm `/recall` tail-recursion primitive handles hierarchical traversal (Phase 3 parser changes)

## Scope Boundaries

**IN:**
- Token counting infrastructure
- Module consolidation (recall + recall_cli + when → unified recall)
- Hierarchical index with arbitrary nesting depth
- Trigger class and learning category metadata
- Recall mode reduction (5 → 2)
- Format grounding research
- Documentation conversion pipeline (first targets)
- PreToolUse hook update for new paths
- 22 test files migrated

**OUT:**
- Post-resolve scoring / usage tracking
- Stage provenance tags
- Recall-artifact rejection tracking
- Lifecycle role contract enforcement
- PreToolUse lint-gated recall hook
- SWE-ContextBench benchmarking
- Version-change detection implementation (mechanism selected in design via Q-4, but implementation deferred past this project)

## Open Questions for Design

- Q-1: Token budget threshold for index/content file splits (NFR-4 says "design target")
- Q-2: Grouping heuristic for related decision files (e.g., all `workflow-*.md` → `workflow/` domain)
- Q-3: Root index metadata format — how much information per domain entry to enable agent selection without reading child indices?
- Q-4: Version-change detection mechanism for FR-3 external entries
- Q-5: Migration tooling — script to split memory-index.md into hierarchy, or manual?

## Risks

- **Test migration scope:** 22 test files, shared fixtures, import path changes. High mechanical effort.
- **Pipeline recall point updates:** 10+ skills reference recall modes or CLI paths. Broad but mechanical.
- **Backward compat window:** Old CLI paths need deprecation schedule. Risk of breaking worktree sessions using old paths during migration.
- **Format grounding (Phase 5) may invalidate Phase 4 decisions:** Grounding research could suggest different metadata model. Mitigated by Phase 5 being research-only — format spec feeds Phase 6, doesn't retroactively change Phase 2-4 code structure.
