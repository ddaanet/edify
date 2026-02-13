# `/when` Memory Recall System — Design

## Problem

Memory index achieves 0% recall across 200 sessions (7,483 opportunities). The current passive catalog format (`Key — description`) with "mentally scan" instructions produces zero retrieval behavior. Agents never form retrieval intentions from reference material.

**Root cause:** Passive awareness is non-functional for LLMs. Agents use what's in context or ignore it — they don't proactively scan catalogs for applicable knowledge.

## Requirements

### Functional

- FR-1: Agent invokes `/when <trigger>` to retrieve decision content — addressed by resolver script + skill wrappers
- FR-2: Fuzzy matching bridges compressed triggers to readable headings — addressed by fuzzy engine
- FR-3: Output includes ancestor (broader) and sibling (related) navigation — addressed by resolver output format
- FR-4: Validator enforces bidirectional integrity (trigger↔heading) — addressed by validator update
- FR-5: `/remember` produces `/when` format entries — addressed by remember skill update
- FR-6: All entries migrated to new format — addressed by index migration (current count: ~160 entries including exempt sections; actual migration scope depends on entry count at execution time)
- FR-7: Three resolution modes: trigger, .section, ..file — addressed by resolver modes

### Non-Functional

- NFR-1: Fuzzy engine shared across resolver, validator, key compression tool (DRY)
- NFR-2: All components implemented with TDD (red/green/refactor)
- NFR-3: Success criteria: >10% recall within 30 sessions post-deployment
- NFR-4: Index remains @-loaded in CLAUDE.md (token budget ~5000 tokens)

### Out of Scope

- Cross-file explicit relations
- Hook-based auto-injection (future)
- `/what` and `/why` operators (dropped — passive knowledge, LLMs don't probe)
- Measurement tooling redesign (recall tool parser updated in step 12 to handle new format, but no architectural changes to recall analysis)

## Architecture

### System Overview

```
Agent context (memory-index.md loaded via @)
  │
  ├─ Sees: /when writing mock tests | mock patch, test doubles
  │
  ├─ Invokes: /when skill → resolver.py when writing mock tests
  │
  └─ Receives: Section content + navigation links
```

**Three resolution modes:**

| Mode | Syntax | Resolution |
|------|--------|------------|
| Trigger | `/when writing mock tests` | Fuzzy match index → heading → content |
| Section | `/when .Mock Patching` | Global unique heading lookup → content |
| File | `/when ..testing.md` | File relative to `agents/decisions/` → full content |

### Component Architecture

```
src/claudeutils/when/
  __init__.py          (empty)
  fuzzy.py             (~80 lines) — Shared fuzzy engine
  resolver.py          (~150 lines) — Resolution logic (3 modes)
  navigation.py        (~80 lines) — Ancestor + sibling link computation
  index_parser.py      (~60 lines) — Parse /when format entries
  cli.py               (~40 lines) — Click CLI entry point

agent-core/bin/
  when-resolve.py      (thin CLI wrapper, calls claudeutils.when)

agent-core/skills/when/
  SKILL.md             (/when skill wrapper)
agent-core/skills/how/
  SKILL.md             (/how skill wrapper)

agent-core/bin/
  compress-key.py      (~30 lines) — Key compression tool
```

### Module Responsibilities

**fuzzy.py — Shared Fuzzy Engine**

Single implementation used by resolver, validator, and key compression tool. Custom fzf-style scoring (~80 lines) with boundary bonuses tuned for short-key domain.

```python
def score_match(query: str, candidate: str) -> float: ...
def rank_matches(query: str, candidates: list[str], limit: int = 5) -> list[tuple[str, float]]: ...
```

Algorithm: Modified fzf V2 scoring (per fzf-research.md) with:
- Character-level subsequence matching
- Boundary bonuses (whitespace=10, delimiter=9, camelCase=7)
- Consecutive match bonus (4 per character)
- First character multiplier (2x)
- Gap penalties (start=-3, extension=-1)
- Word-overlap tiebreaker for equal fzf scores
- Minimum score threshold to prevent spurious matches on short queries

Query includes prefix word: `/when writing mock tests` → query "when writing mock tests" (not "writing mock tests"). This disambiguates when `/when` and `/how` entries coexist for similar topics.

**resolver.py — Resolution Logic**

Three modes determined by leading `.` in query:

```python
def resolve(operator: str, query: str, index_path: Path, decisions_dir: Path) -> str:
    """
    operator: "when" or "how"
    query: trigger text (may start with . or ..)
    Returns: formatted output string (content + navigation)
    Raises: ResolveError on no match (caller formats error message)
    """
```

Mode detection:
- `..filename.md` → file mode (strip `..`, resolve relative to decisions_dir)
- `.Section Title` → section mode (strip `.`, lookup heading globally)
- anything else → trigger mode (fuzzy match against index)

**Note on heading levels:** Decision files use both flat H2 (workflow-core.md: 13 sections, no nesting) and nested H2/H3 (testing.md: structural H2 parents with semantic H3 children). The resolver must handle both patterns — index entries can point to H2 or H3 headings.

**navigation.py — Link Computation**

```python
def compute_ancestors(heading: str, file_path: str, file_content: str) -> list[str]: ...
def compute_siblings(heading: str, file_content: str, index_entries: list[WhenEntry]) -> list[str]: ...
```

Ancestors: Walk up heading hierarchy (H4→H3→H2→file). Always include `..file.md` link.
Siblings: Other index entries whose headings share the same parent heading.

**Structural heading handling:** Structural headings (`.` prefix) are organizational and should be skipped as navigation targets. If an ancestor heading is structural, include it as a `.Section` link but label it as a container, not a content section.

**index_parser.py — Parse `/when` Format**

Uses Pydantic BaseModel (per project convention) rather than dataclass:

```python
class WhenEntry(BaseModel):
    operator: str          # "when" or "how"
    trigger: str           # primary trigger text
    extra_triggers: list[str]  # synonyms after |
    line_number: int
    section: str           # file section in index (H2 heading = file path)

def parse_index(index_path: Path) -> list[WhenEntry]: ...
```

Format: `/when trigger text | extra, triggers`
- Prefix (`/when` or `/how`) determines operator
- Text before `|` is primary trigger
- Text after `|` is comma-separated extra triggers (optional)

**cli.py — Click Entry**

```python
@click.command()
@click.argument("operator", type=click.Choice(["when", "how"]))
@click.argument("query", nargs=-1, required=True)
def when_cmd(operator: str, query: tuple[str, ...]) -> None:
    """Resolve a /when or /how trigger."""
```

Registered in main CLI group via `cli.add_command()` in `src/claudeutils/cli.py` (following pattern of `recall`, `validate`, `statusline`).

### Index Format

**Current format:**
```
Mock patching pattern — patch where object is used not where defined
```

**New format:**
```
/when writing mock tests | mock patch, test doubles
```

**Format specification:**
- Line starts with `/when` or `/how` (operator prefix)
- Space-separated trigger text follows operator
- Optional `|` delimiter followed by comma-separated extra triggers
- No description field — content lives in decision file heading
- Plain prose triggers (no hyphens — "auth error" = 2 tokens, "auth-error" = 3)
- Trigger length: 2-5 words typical

**Heading correspondence:**
- `/when writing mock tests` → decision file heading: `### When Writing Mock Tests`
- `/how encode paths` → decision file heading: `### How to Encode Paths`
- Heading prefix generated from operator: "when" → "When", "how" → "How to"

**Section organization (unchanged):**
- Sections grouped by target file (H2 = file path)
- Entries in file order within sections
- Exempt sections removed ("Behavioral Rules" — fragments are @-loaded, indexing is noise)
- "Technical Decisions (mixed)" converted to file-grouped sections

### Output Format

```
# When Writing Mock Tests

<full section content from decision file>

Broader:
/when .Mock Patching
/when ..testing.md

Related:
/when testing strategy | markdown cleanup, TDD
/when success metrics | test pass criteria
```

**Broader (ancestors):** Navigate up heading hierarchy.
- H3 learning → parent H2 section link
- H4 learning → parent H3 + grandparent H2
- Always include `..file.md` link at end

**Related (siblings):** Other `/when` entries under the same parent heading. Computed by mapping entries to containing section in decision file.

**Error output:**
- Trigger not found → "No match for '<query>'. Did you mean:\n  /when <closest1>\n  /when <closest2>"
- `.section` not found → "Section '<name>' not found. Available:\n  .Section1\n  .Section2"
- `..file.md` not found → "File '<name>' not found in agents/decisions/. Available:\n  ..cli.md\n  ..testing.md"

### Validator Changes

**Current:** Exact lowercase match (`key.lower() == title.lower()`).
**New:** Fuzzy match via shared engine. Entry trigger must fuzzy-expand to exactly one heading.

**Affected files:**
- `src/claudeutils/validation/memory_index.py` — facade: `extract_index_entries()` format parsing
- `src/claudeutils/validation/memory_index_checks.py` — `check_em_dash_and_word_count()` replaced with trigger format checks
- `src/claudeutils/validation/memory_index_helpers.py` — `extract_index_structure()` and `autofix_index()` adapted for new format, EXEMPT_SECTIONS updated

**Invocation:** Precommit runs `claudeutils validate` (via justfile), which calls `validate_memory_index()` from the package. There is no separate bin script — validation lives entirely in `src/claudeutils/validation/`.

**Note on internal duplication:** `memory_index_helpers.py` and `memory_index_checks.py` both define check functions (e.g., `check_em_dash_and_word_count`, `check_duplicate_entries`). The facade (`memory_index.py`) imports from helpers. Both files need consistent updates.

**Validation checks (updated):**

| Check | Current | New |
|-------|---------|-----|
| Format | em-dash separator, 8-15 words | `/when` prefix, trigger + optional extras |
| Entry↔Heading | Exact lowercase match | Fuzzy match (unique expansion) |
| Bidirectional | Orphan headers, orphan entries | Same, via fuzzy engine |
| Collision | Duplicate keys | No two triggers resolve to same heading |
| Autofix | Placement, ordering, structural | Same mechanics, new format parsing |
| Word count | 8-15 words total | Removed (triggers are intentionally short) |

**New validation rules:**
- Operator prefix required (`/when` or `/how`)
- Primary trigger uniqueness across index
- Extra triggers: comma-separated, no empty segments
- Each trigger fuzzy-expands to exactly one heading
- Each heading reachable by exactly one entry

**Autofix preserved:** Section placement, ordering, structural entry removal — same mechanics, adapted for new format.

**Backward compatibility:** During migration, both old format (`Key — description`) and new format (`/when trigger | extras`) may temporarily coexist. The validator must handle this transitional state or the migration must be atomic (all entries converted in one commit). Design choice: **atomic migration** — convert all entries and rename all headings in a single commit, avoiding dual-format complexity in the validator.

**Exempt section changes:** "Behavioral Rules" section removed entirely (per design). "Technical Decisions (mixed)" section entries redistributed to file-based sections — this creates new index sections for files currently without sections (e.g., `data-processing.md`, `cli.md`, `markdown-tooling.md`, `validation-quality.md`, `defense-in-depth.md`). EXEMPT_SECTIONS constant updated to empty set after migration.

### Key Compression Tool

```
$ compress-key.py "How to Encode Paths"
how encode path        # unique, 3 words
encode path            # ambiguous (also matches "When Encoding Paths Needed")
```

Uses fuzzy engine to verify uniqueness against full heading corpus. Suggests minimal trigger that uniquely resolves. Useful during migration and when `/remember` generates new entries.

### Skill Wrappers

Two thin skills, same resolver:

**`/when` skill:**
```yaml
---
name: when
description: Recall behavioral knowledge. Invoke when facing a decision or pattern you've seen before.
allowed-tools: Bash(agent-core/bin/when-resolve.py:*)
user-invocable: true
---
```

Execution: `agent-core/bin/when-resolve.py when <trigger>`

**`/how` skill:**
```yaml
---
name: how
description: Recall procedural knowledge. Invoke when you need to know how to do something.
allowed-tools: Bash(agent-core/bin/when-resolve.py:*)
user-invocable: true
---
```

Execution: `agent-core/bin/when-resolve.py how <trigger>`

**Tool permission note:** Skills use the bin script as entry point (matching `Bash(agent-core/bin/when-resolve.py:*)`). The bin script calls into `claudeutils.when` internally. This follows the same pattern as worktree skill using `Bash(claudeutils _worktree:*)`.

### Consumption Header Update

Replace passive "scan mentally" instruction with active invocation:

```markdown
# Memory Index

Active knowledge retrieval. Invoke `/when` or `/how` to recall decisions.

**Invocation:**
/when <trigger>        # behavioral knowledge (when to do X)
/how <trigger>         # procedural knowledge (how to do X)

**Navigation:**
/when .Section Title   # section content by heading name
/when ..file.md        # entire decision file (relative to agents/decisions/)
```

### `/remember` Skill Update

Update entry generation to produce `/when` format:

**Current:** "Add one-line entry (summary + file reference) to appropriate section"

**New:** Generate `/when` or `/how` entry with trigger naming guidelines:
- Plain prose, no hyphens or special characters
- 2-5 words typical
- Optimize for discovery: what would agent type when facing this problem?
- Use key compression tool to verify uniqueness
- Choose operator based on knowledge type:
  - `/when` for behavioral (when to do X, when X applies)
  - `/how` for procedural (how to do X, technique for X)

### Fragment Promotion Rule

Promote learning to fragment when:
```
token_count(fragment_content) <= token_count(index_entry) + margin
```

Where margin = ~2 tokens (overhead of `/` and entry formatting). If full content costs roughly the same as the index entry, it's ambient knowledge — always load it via @-reference instead.

## Key Design Decisions

### D-1: Two-field format

`/when trigger | extra triggers` — not three-field with description.

**Rationale:** Fuzzy matching eliminates need for exact header-title field. Description is redundant — content lives in decision file. Shorter entries = more token-efficient index.

### D-2: Sections in files, not file atomization

Keep decisions grouped in `agents/decisions/*.md` files.

**Rationale:** Prompt caching research showed prefix-level caching (not file-level dedup). Splitting headings into individual files (120+) would create many files with no caching benefit and significant management overhead.

### D-3: Two operators only

`/when` (behavioral) + `/how` (procedural). No `/what` or `/why`.

**Rationale:** LLMs don't proactively seek definitions or rationale. `/what` and `/why` are passive knowledge — exactly the pattern that failed with 0% recall. Only behavioral triggers ("/when X happens, do Y") and procedural triggers ("/how to do X") create retrieval intention.

Corpus analysis showed: 27% of entries are `/how` candidates, remaining 73% fit `/when`. `/what` and `/why` candidates (16 entries) can be rephrased as `/when` or `/how`. Note: corpus analysis was performed at 122 entries; index has since grown to ~160.

### D-4: Custom fuzzy engine over library

~80 line custom implementation over pfzy/RapidFuzz.

**Rationale:** pfzy has async API overhead and is designed for interactive filtering. RapidFuzz uses edit distance (wrong algorithm family). Custom engine allows tuning scoring constants for short-key domain (increased boundary bonuses, reduced gap penalties). Three consumers (resolver, validator, compression tool) need identical scoring behavior.

### D-5: Direct content output

Script outputs content directly, no file-path indirection.

**Rationale:** Agent needs the content, not a file path. File-path indirection adds a Read round-trip. Direct output is one tool call.

### D-6: Heading renames match triggers

`/when writing mock tests` → heading `### When Writing Mock Tests`

**Rationale:** One-to-one correspondence simplifies validation and debugging. Heading prefix ("When"/"How to") generated from operator, rest matches trigger. Fuzzy engine bridges any compression gap.

### D-7: Validator uses fuzzy engine (not exact match)

Current validator uses `key.lower() == title.lower()`. New validator uses `fuzzy.score_match()`.

**Rationale:** Triggers are fuzzy-compressed ("write mock test") while headings are readable prose ("When Writing Mock Tests"). Exact match would force either verbose triggers or cryptic headings. Fuzzy bridge (per learnings) maintains density in index and clarity in headings.

### D-8: Atomic migration (no dual-format validator)

Migration converts all entries and renames all headings in a single commit. The validator does not support dual-format parsing.

**Rationale:** Dual-format support adds complexity to every validation check (format detection, conditional parsing, mixed error messages). Atomic migration is feasible because: (a) entry conversion is scripted, (b) heading renames are scripted, (c) validator changes ship in the same commit. The precommit validator catches any mismatches immediately.

### D-9: Word count removed

Current: 8-15 word hard limit. New: no word count constraint.

**Rationale:** `/when` triggers are intentionally short (2-5 words). Extra triggers after `|` vary in length. Word count was designed for `Key — description` format; doesn't apply to trigger format. Trigger quality is validated by fuzzy uniqueness, not word count.

## Implementation Notes

### Recall tool compatibility

The existing recall analysis tool (`src/claudeutils/recall/`) parses the current `Key — description` format via `recall/index_parser.py`. After migration to `/when trigger | extras` format, the recall tool's index parser will break.

**Impact:** The recall tool measures effectiveness (NFR-3: >10% recall within 30 sessions). It must work with the new format to validate success criteria.

**Approach:** Update `src/claudeutils/recall/index_parser.py` to parse new format, or have it consume entries from the shared `when/index_parser.py`. Included as step 12 in migration sequencing.

### Decision file heading renames

Semantic headings need renaming. Each current heading (e.g., `### Mock Patching Pattern`) becomes prefixed (e.g., `### When Writing Mock Tests` or `### How to Patch Mocks`).

**Process:**
1. Build mapping: current heading → new heading (from migrated index)
2. Script applies renames across all decision files
3. Precommit validator catches any mismatches

**Risk:** Heading renames may break `@` references or documentation links. Mitigate: grep for old heading text before rename, update references atomically.

**Scope of heading renames:** Only semantic headings (non-`.` prefix) get renamed. Structural headings (`.` prefix like `.Test Organization`, `.Mock Patching`) remain unchanged — they are organizational, not indexed. Current counts: ~123 semantic H3+ headings across 11 decision files, ~70 structural headings. Exact rename scope determined at execution time.

### Validator refactoring

Validation lives in a single location: `src/claudeutils/validation/memory_index*.py` (3 modules: facade, checks, helpers). Precommit invokes this via `claudeutils validate` (justfile recipe). Core validation logic (bidirectional integrity, autofix) remains; format parsing changes.

**Affected modules:**
- `src/claudeutils/validation/memory_index.py`: `extract_index_entries()` — new format parsing
- `src/claudeutils/validation/memory_index_checks.py`: Format validation rules — replace `check_em_dash_and_word_count()` with trigger format check
- `src/claudeutils/validation/memory_index_helpers.py`: Autofix — adapt for new format, update EXEMPT_SECTIONS
- New dependency: fuzzy engine in `src/claudeutils/when/fuzzy.py` (imported by validator)

### Testing strategy

**TDD for all components.** Each module gets behavioral tests first.

**Spike candidates:**
- Fuzzy engine scoring — needs experimentation with scoring constants before TDD
- Heading rename script — test with subset of decision files first

**Test structure mirrors source (per project convention — flat test directory, prefixed names):**
```
tests/
  test_when_fuzzy.py           — Scoring, ranking, edge cases
  test_when_resolver.py        — Three modes, error handling
  test_when_navigation.py      — Ancestors, siblings, edge cases
  test_when_index_parser.py    — Format parsing, malformed entries
  test_when_cli.py             — CLI invocation, output format
  test_validation_memory_index.py — Updated for new format (extend existing)
```

**Note:** Project uses flat test directory with `test_<domain>_<module>.py` naming (see existing `test_recall_*.py`, `test_validation_*.py`), not nested `tests/<domain>/` subdirectories.

**TDD compatibility:** Each module in `src/claudeutils/when/` has clear inputs/outputs suitable for isolated TDD cycles:
- `fuzzy.py`: pure functions, no I/O
- `index_parser.py`: file input, structured output
- `resolver.py`: depends on fuzzy + parser (mockable)
- `navigation.py`: pure functions on file content strings
- `cli.py`: Click test runner integration

### Migration sequencing

Components have dependencies. Recommended build order:

1. **Fuzzy engine** (`src/claudeutils/when/fuzzy.py`) — no dependencies, foundation for everything
2. **Index parser** (`src/claudeutils/when/index_parser.py`) — depends on format spec only
3. **Navigation** (`src/claudeutils/when/navigation.py`) — depends on file content parsing (no resolver dependency)
4. **Resolver** (`src/claudeutils/when/resolver.py`) — depends on fuzzy + parser + navigation
5. **CLI** (`src/claudeutils/when/cli.py` + `agent-core/bin/when-resolve.py`) — depends on resolver
6. **Validator update** (`src/claudeutils/validation/memory_index*.py`) — depends on fuzzy + parser
7. **Key compression tool** (`agent-core/bin/compress-key.py`) — depends on fuzzy
8. **Skills** (`agent-core/skills/when/`, `agent-core/skills/how/`) — depends on CLI (requires restart)
9. **Index migration** (agents/memory-index.md + heading renames) — depends on all above (migration validates with new validator)
10. **Remember skill update** (`agent-core/skills/remember/SKILL.md`) — depends on format spec
11. **Consumption header** (agents/memory-index.md preamble) — depends on skills being ready
12. **Recall tool parser update** (`src/claudeutils/recall/index_parser.py`) — update to parse new format (NFR-3 measurement depends on this)

**Dependency correction:** Navigation (step 3) does not depend on the resolver — it operates on file content and heading strings directly. The resolver depends on navigation (to compute output links). This ordering allows navigation to be tested independently before resolver integration.

### Existing code reuse

| Existing | Reuse in `/when` |
|----------|-----------------|
| `src/claudeutils/recall/index_parser.py` | Reference for format parsing (different format, similar structure). Uses Pydantic BaseModel pattern to follow. |
| `src/claudeutils/recall/relevance.py` | Keyword overlap logic — informational only (fuzzy engine replaces) |
| `src/claudeutils/validation/memory_index*.py` | Extend with new format support, keep autofix mechanics |
| `src/claudeutils/validation/common.py` | Shared utilities if applicable |

## Requirements Traceability

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes | Resolver script + skill wrappers (Component Architecture, Skill Wrappers) |
| FR-2 | Yes | Fuzzy engine (fuzzy.py module, D-4, D-7) |
| FR-3 | Yes | Navigation module (navigation.py, Output Format) |
| FR-4 | Yes | Validator Changes section |
| FR-5 | Yes | `/remember` Skill Update section |
| FR-6 | Yes | Index migration (Migration sequencing step 9) |
| FR-7 | Yes | Three resolution modes (Resolver, mode detection) |
| NFR-1 | Yes | Fuzzy engine shared across 3 consumers (D-4) |
| NFR-2 | Yes | Testing strategy section (TDD for all components) |
| NFR-3 | Yes | Requirements section (>10% recall within 30 sessions) |
| NFR-4 | Yes | Consumption Header Update (index remains @-loaded) |

**Gaps:** None. All requirements traced to design elements.

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agents/decisions/implementation-notes.md` — implementation patterns, Python quirks
- `agents/decisions/testing.md` — TDD conventions
- `plans/when-recall/reports/corpus-analysis.md` — entry pattern classification
- `plans/when-recall/reports/fzf-research.md` — fuzzy algorithm research
- `plans/when-recall/reports/explore-design-context.md` — validator/skill/package structure (note: was generated from a different worktree; `agent-core/bin/validate-memory-index.py` reference is stale — bin script does not exist in this repo)

**Context7 references:**
- Click CLI framework (query: "click command group subcommand") — if needed for CLI structure

**Additional research allowed:** Planner may explore `src/claudeutils/` for implementation patterns and `tests/` for test structure conventions.

## Next Steps

1. `/plan-tdd` to create TDD runbook from this design
2. Load `plugin-dev:skill-development` before planning (skill wrappers needed)
3. Fuzzy engine spike may precede formal TDD cycles (scoring constant tuning)
