# Remember Skill and Learnings Consolidation Pipeline Exploration

**Date:** 2026-02-15
**Scope:** Remember skill structure, learnings consolidation process, memory index creation and validation

## Executive Summary

The remember skill and learnings pipeline implements a four-stage flow: learning creation → staging/retention → consolidation → discovery mechanism updates. Learning entries are filtered by age (7+ active days per `learning-ages.py`), processed through pre-consolidation checks (supersession/contradiction/redundancy), consolidated into permanent documentation across domain-specific files, indexed in `memory-index.md` with `/when` and `/how` operators, and validated via comprehensive trigger format and cross-reference checks. The pipeline enforces behavioral trigger framing (symptom-oriented, not root-cause-oriented) and requires exact key matching in validation (fuzzy matching only at runtime recovery).

---

## 1. Remember Skill Structure

**Location:** `/Users/david/code/claudeutils/agent-core/skills/remember/`

**Core Components:**

### SKILL.md (Main Skill Definition)
**Path:** `/Users/david/code/claudeutils/agent-core/skills/remember/SKILL.md`

**Frontmatter:**
- `name: remember`
- `description: Process pending learnings from session handoffs and update documentation with rules and patterns`
- `allowed-tools: Read, Write, Edit, Bash(git:*), Glob`
- `user-invocable: true`

**Execution Protocol (Steps 1-5):**

1. **Understand Learning** (lines 20-23)
   - Read `agents/learnings.md` for recent learnings
   - Read relevant `agents/decisions/*.md` if exists
   - Understand problem/gap, solution/rule, why important, category

2. **File Selection** (lines 25-35)
   - Behavioral rules → `agent-core/fragments/*.md`
   - Technical details → `agents/decisions/*.md`
   - Implementation patterns → `agents/decisions/implementation-notes.md`
   - Session state → `agents/session.md`
   - Skill-specific → `.claude/skills/*/references/learnings.md`
   - Never: README.md, test files, temp files
   - Detailed routing in `references/consolidation-patterns.md`

3. **Draft Update** (lines 37-52)
   - Principles: Precision > brevity, examples > abstractions, constraints > guidelines
   - Format: `### [Rule Name]`, `**[Imperative/declarative statement]**`, explanation, `**Example:**`
   - Emphasis on measured data over estimates, concrete paths over abstractions

4. **Apply + Verify** (lines 54-73)
   - Edit existing files (preferred), Write only for new files
   - Verify formatting and placement
   - **Step 4a: Update Discovery Mechanisms** (lines 59-74):
     - Append memory index entry to `agents/memory-index.md`
     - Trigger naming: Plain prose, no hyphens, 2-5 words, optimize for discovery
     - Use `agent-core/bin/compress-key.py` to verify uniqueness
     - Operator selection: `/when` for behavioral, `/how` for procedural
     - If new fragment: Add `@`-reference to CLAUDE.md OR `.claude/rules/` entry (path-scoped)
     - If existing fragment updated: Ensure memory index entry reflects update
     - If decision file updated: Verify `.claude/rules/` entry exists

5. **Document** (lines 109-111)
   - Commit message format: `Update [file]: [what]\n\n- [change 1]\n- [change 2]\n- [rationale]`
   - Handoff note explaining significance and referencing commit

**Learnings Quality Criteria (lines 76-90):**
- Principle-level (consolidate): General constraint or pattern, applies beyond incident
- Incident-specific (reject/revise): Describes what happened, not what to do
- Meta-learnings (use sparingly): Rules about rules, only when behavioral constraint required

**Staging Retention Guidance (lines 92-107):**
- **Keep in staging:** Entries < 7 days old, pending cross-references, under active investigation
- **Consolidate:** Entries ≥ 7 active days, proven validity, applied consistently, referenced by multiple sessions
- **Drop:** Superseded by newer entry, contradicted by subsequent work, incident-specific without principle

### Reference Files

**consolidation-patterns.md**
**Path:** `/Users/david/code/claudeutils/agent-core/skills/remember/references/consolidation-patterns.md`

Key sections:
- Target selection by domain (workflow, architecture, CLI, testing)
- Progressive disclosure principle (always-loaded vs skill-triggered vs path-scoped)
- Consolidation workflow (5 steps: categorize, select target, draft, apply, commit)
- **Memory index maintenance after consolidation (lines 64-122):**
  - Append one-line entry to `agents/memory-index.md` in appropriate section
  - Discovery routing: CLAUDE.md @-ref (always-active) OR .claude/rules/ (path-scoped)
  - Heuristic: "always applies" → @-ref; "only when working with X" → path-scoped rule
- Validation checklist before consolidating

**remember-patterns.md**
**Path:** `/Users/david/code/claudeutils/agent-core/skills/remember/examples/remember-patterns.md`

Usage patterns with examples:
- Error handling after failure
- Workflow improvement discovery
- Design decision documentation
- Remove obsolete rule
- Process pending learnings from staging

---

## 2. Remember-Task Agent

**Location:** `/Users/david/code/claudeutils/agent-core/agents/remember-task.md`

**Frontmatter:**
- `name: remember-task`
- `description: Use when delegating learnings consolidation during handoff. Pre-filtered 7+ day entries, pre-consolidation checks, reports to tmp/consolidation-report.md`
- `model: sonnet`
- `color: green`
- `tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]`

**Key Differences from Interactive `/remember` (line 13-16):**
- Operates on pre-filtered batch (≥7 active days), not entire learnings file
- Consolidation decision already made by handoff trigger logic
- Focus: pre-consolidation checks, protocol execution, reporting

**Pre-Consolidation Checks (lines 47-80):**

1. **Supersession Detection** (lines 51-58)
   - Identify entry pairs where newer contradicts older on same topic
   - Method: Keyword overlap + negation patterns (>50% keyword overlap, negation words like "no longer", "instead")
   - Action: Drop older entry, note in report
   - Conservative bias: When uncertain, consolidate both

2. **Contradiction Detection** (lines 60-68)
   - Find entries contradicting existing documentation
   - Method: Semantic comparison with target file content (keyword match, compare statements)
   - Action: Escalate to orchestrator
   - Conservative bias: When uncertain, escalate (false positive better than silent conflict)

3. **Redundancy Detection** (lines 70-78)
   - Find entries duplicating existing documentation
   - Method: Keyword/phrase overlap scoring (>70% overlap = redundant)
   - Action: Drop from batch
   - Conservative bias: When uncertain, consolidate anyway (prefer over-documentation)

**Consolidation Protocol** (lines 87-135)
- Mirrors remember skill steps 1-4a
- Per-phase source: `agent-core/skills/remember/SKILL.md` (manual sync required on updates)

**Reporting Format** (lines 137-187)
- Summary: Entries processed, consolidated, dropped, escalated, skipped
- Supersession decisions with rationale
- Redundancy decisions with overlap scores
- Contradictions (ESCALATION) with conflict description
- File limits (ESCALATION) with action required
- Discovery updates (memory index, CLAUDE.md refs, .claude/rules/ entries)
- Consolidation details per entry

**Return Protocol** (lines 189-202)
- Success: Return filepath only `tmp/consolidation-report.md`
- Failure: Return error message with diagnostics
- Never return report content directly

---

## 3. Learnings Creation and Staging Pipeline

**Learning Creation Flow:**

### 3.1 Initial Learning Capture

**In agents/learnings.md** (line 1-47)
- **Format:** H2 headers (## Learning Title) with content
- **Placement:** Append new learnings at bottom (append-only structure)
- **Title constraints:** Max 5 words (validated by `learnings.py`)
- **Soft limit:** 80 lines — when approaching, use `/remember` to consolidate older entries
- **Retention:** Keep 3-5 most recent learnings for continuity after consolidation

**Example structure:**
```markdown
# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate...

---
## Tool batching unsolved
- Documentation (tool-batching.md fragment) doesn't reliably change behavior
- Direct interactive guidance is often ignored
...

## RED pass blast radius assessment
- Anti-pattern: Handling unexpected RED pass as isolated cycle issue
...
```

### 3.2 Validation Pipeline

**learnings.py**
**Path:** `/Users/david/code/claudeutils/src/claudeutils/validation/learnings.py`

**Constraints enforced:**
- Title format: `## Title` (markdown H2 header)
- Max word count: 5 words per title (configurable, default MAX_WORDS=5)
- Uniqueness: No duplicate titles (case-insensitive)
- No empty titles

**Key functions:**
- `extract_titles(lines)` → List of (line_number, title_text) tuples
  - Skips first 10 lines (preamble/header)
  - Matches `## Title` pattern
- `validate(path, root, max_words=5)` → List of error strings
  - Enforces title format, word count, uniqueness
  - Returns empty list if no errors

**Validation in precommit hook:**
- Runs via `just precommit` as part of validation suite
- Blocks commits with validation errors

### 3.3 Learning Ages Calculation

**learning-ages.py**
**Path:** `/Users/david/code/claudeutils/agent-core/bin/learning-ages.py`

**Purpose:** Calculate git-active-day age per learning entry for consolidation eligibility

**Key Functions:**

1. **extract_titles(lines)** (lines 24-39)
   - Extract (line_number, title_text) from H2 headers
   - Skips first 10 lines (preamble)

2. **get_commit_date_for_line(filepath, line_number)** (lines 42-75)
   - Uses `git blame -C -C --first-parent --line-porcelain` to get line's creation date
   - Returns ISO date string (YYYY-MM-DD) or None on error
   - Handles renames/copies and merge commits via first-parent chain

3. **get_active_days_since(start_date)** (lines 78-108)
   - **Semantic:** Calculate active days (unique commit dates) since start_date
   - Uses `git log --format=%ad --date=short --since={start_date}`
   - Returns count of unique commit dates (0 if entry added today)
   - Used to determine consolidation eligibility (≥7 active days)

4. **get_last_consolidation_date(filepath)** (lines 111-153)
   - Find most recent consolidation by detecting removed H2 headers in git log
   - Walks `git log -p --first-parent` looking for lines matching `-## ` pattern
   - Returns (date_string, active_days_since_consolidation) or (None, None)
   - **Staleness metric:** Tells when consolidation last occurred

**Report Output:** Markdown report to stdout with:
- File line count
- Last consolidation date and staleness (active days)
- Total entries and count ≥7 days old
- Table: "Entries by Age" sorted descending by active days

**Usage:**
```bash
learning-ages.py [learnings-file]
# Default: agents/learnings.md
# Output: Markdown report to stdout
# Exit: 0 on success, 1 on error (stderr)
```

**Integration points:**
- Called during handoff to identify consolidation-eligible entries
- Filters entries ≥7 active days for remember-task agent batch
- Provides staleness feedback to user

---

## 4. Learnings Consolidation into Permanent Documentation

### 4.1 Target File Selection

**Consolidation Patterns Reference**
**Path:** `/Users/david/code/claudeutils/agent-core/skills/remember/references/consolidation-patterns.md`

**Domain-based routing:**

| Domain | Target File | Pattern |
|--------|------------|---------|
| Workflow patterns | `agent-core/fragments/*.md` | Handoff, TDD, planning methodology |
| Architecture decisions | `agents/decisions/*.md` | Module structure, path handling, rules |
| CLI patterns | `agents/decisions/cli.md` | Commands, flags, output formatting |
| Testing patterns | `agents/decisions/testing.md` | Test structure, assertions, mocking |
| Implementation details | `agents/decisions/implementation-notes.md` | Python quirks, API details, mock patterns |
| Session state | `agents/session.md` | Current work, active tasks, blockers |
| Skill-specific patterns | `.claude/skills/{skill}/references/learnings.md` | Progressive disclosure by skill trigger |

**Progressive disclosure principle:**
- **Always loaded (use sparingly):** CLAUDE.md, session.md
- **Loaded by path trigger:** decisions/ (via .claude/rules/)
- **Loaded by skill trigger:** skill references/learnings.md (best discoverability)
- **Loaded on demand:** Plan files, archives

### 4.2 Consolidation Format and Principles

**Update format (from SKILL.md lines 46-52):**
```markdown
### [Rule Name]
**[Imperative/declarative statement]**
[Supporting explanation]
**Example:** [Concrete demonstration]
```

**Drafting principles:**
- Precision over brevity (unambiguous, clear boundaries)
- Examples over abstractions (concrete paths, actual code)
- Constraints over guidelines ("Do not" > "avoid", "Always" > "consider")
- Atomic changes (one concept, self-contained)
- Measured data only (no estimates)
- Lead with directive, follow with rationale (no preamble)
- Concrete ✅/❌ pairs where possible

**Anti-patterns to avoid:**
- Hedging qualifiers ("might", "consider", "you could")
- Abstract principles without examples
- Guidelines instead of constraints
- Archival/historical content mixed with active rules

### 4.3 Document Verification

After consolidation, verify:
- Updated section reads correctly
- Formatting matches target file conventions
- Placement aligns with section organization
- No duplication with existing content

---

## 5. Memory Index Entry Creation and Structure

**Location:** `/Users/david/code/claudeutils/agents/memory-index.md`

### 5.1 Entry Format and Operators

**Two-operator system:**

| Operator | Use Case | Example |
|----------|----------|---------|
| `/when` | Behavioral knowledge — when to do X, when X applies | `/when RED pass blast radius assessment` |
| `/how` | Procedural knowledge — how to do X, technique for X | `/how format runbook phase headers` |

**Entry syntax:**
```markdown
/when <trigger>
/how <trigger>
```

**Advanced syntax (pipe-delimited synonyms):**
```markdown
/when choosing review gate | transformation table artifact type T1-T6 pipeline stages
/how prevent skill steps from being skipped | prose gates no tool call D+B hybrid
```

Pipe delimiter (`|`) adds additional keyword triggers (synonyms) for discovery.

### 5.2 Trigger Naming Constraints

**Trigger specification (SKILL.md lines 64-68):**
- Plain prose, no hyphens or special characters
- 2-5 words typical
- **Optimize for discovery:** What would agent type when facing this problem?
- Use `agent-core/bin/compress-key.py` to verify uniqueness
- **Behavioral trigger framing (learnings.md lines 39-42):** Key describes situation agent encounters, not root cause
  - ✅ "Choosing review gate" (symptom agent observes)
  - ❌ "Transformation table" (internal jargon/root cause)
  - ❌ "T1-T6 pipeline stages" (technical implementation detail)

**Symptom-oriented framing example (learnings.md line 39-42):**
```
## Symptom-oriented index trigger keys
- Anti-pattern: Key describes root cause or uses internal jargon (e.g., "transformation table", "prose gates")
- Correct pattern: Key describes situation agent encounters (e.g., "choosing review gate", "prevent skill steps from being skipped")
- Rationale: Agents search by symptom (what they observe), not root cause (what the entry teaches)
```

### 5.3 Organization by File

Memory index organized in sections by decision file:

```markdown
## agents/decisions/cli.md

/when getting current working directory
/how output errors to stderr
...

## agents/decisions/data-processing.md

/how write init files
/when placing helper functions
...

## agents/decisions/pipeline-contracts.md

/when choosing review gate | transformation table artifact type...
...
```

**Section structure:**
- H2 header with file path (e.g., `## agents/decisions/cli.md`)
- Entries under section (one per line, no bullets)
- Entries listed in file order (validated by `check_entry_sorting`)

### 5.4 Entry Consolidation After Learning Update

**Step 4a: Update Discovery Mechanisms (SKILL.md lines 59-74, remember-task.md lines 131-135):**

1. **Append to memory index:** Add one-line entry to `agents/memory-index.md` in appropriate file section
   - Entry format: `/when trigger` or `/how trigger`
   - Placement: In correct file section, in file order
   - Trigger: Behavioral (symptom-oriented), 2-5 words, discovered via compress-key.py

2. **If new fragment created:** Add `@`-reference to CLAUDE.md OR `.claude/rules/` entry (path-scoped)
   - Heuristic: Always-active rule → @-ref in CLAUDE.md; File-type-specific rule → `.claude/rules/` with path frontmatter
   - Example @-ref: `@agent-core/fragments/sandbox-exemptions.md`
   - Example path-scoped rule: `.claude/rules/skill-development.md` with `path: [".claude/skills/**/*.md"]`

3. **If existing fragment updated:** Verify memory index entry reflects updated content (add new entry or update existing)

4. **If decision file updated:** Verify `.claude/rules/` entry exists for path trigger

---

## 6. Memory Index Validation Pipeline

**Location:** `/Users/david/code/claudeutils/src/claudeutils/validation/memory_index.py`
**Secondary checks:** `/Users/david/code/claudeutils/src/claudeutils/validation/memory_index_checks.py`
**Helpers:** `/Users/david/code/claudeutils/src/claudeutils/validation/memory_index_helpers.py`

### 6.1 Semantic vs Structural Headers

**Semantic headers (indexed):** H2+ followed by space and non-dot
```markdown
## When Writing Mock Tests       ← Indexed, needs memory-index.md entry
### Mocking patterns             ← Indexed, needs memory-index.md entry
```

**Structural headers (exempt):** H2+ followed by space and dot
```markdown
## .Implementation details       ← NOT indexed, no entry needed
### .Advanced                    ← NOT indexed, no entry needed
```

Regex patterns (memory_index_helpers.py lines 7-9):
```python
SEMANTIC_HEADER = re.compile(r"^(##+) ([^.].+)$")
STRUCTURAL_HEADER = re.compile(r"^(##+) \..+$")
```

### 6.2 Validation Checks (Non-Autofixable)

**validate() function (memory_index.py lines 231-279)**

**Non-autofixable checks** (run first, block if failures):

1. **check_duplicate_entries()** (memory_index_checks.py lines 17-73)
   - Detect duplicate index entries (same key appearing twice)
   - Error: `"memory-index.md:{i}: duplicate index entry '{key}' (first at line {seen_entry_keys[key]})"`
   - Key extraction: `/when X` → "when x", `/how X` → "how to x", `X — Y` → "x"

2. **check_trigger_format()** (memory_index_checks.py lines 76-133)
   - **Non-autofixable check enforcing entry format**
   - **Validates operator prefix:** Entry must start with `/when ` or `/how `
   - **Validates non-empty trigger:** After operator, trigger text must not be empty
   - **Validates sections:** Entries in exempt sections pass (historical format preserved)
   - **Error cases:**
     ```
     Invalid operator prefix (use /when or /how): '/what X'
     Entry missing operator prefix: 'X — Y' (old em-dash format)
     /when has empty trigger: '/when '
     /how has empty trigger: '/how '
     ```

3. **_check_orphan_headers()** (memory_index.py lines 112-149)
   - Detect semantic headers with no memory-index.md entry
   - Uses fuzzy matching (score_match) with 50.0 threshold as fallback for compression
   - Entry keys include operator prefix, headers don't — compared after extracting key
   - Error: `"  {filepath}:{lineno}: orphan semantic header '{title}' ({level} level) has no memory-index.md entry"`

4. **check_orphan_entries()** (memory_index_helpers.py lines 260-278)
   - Detect orphan index entries with no matching semantic headers
   - Strips operator prefix from entry key (`_strip_operator_prefix`) for structural comparison
   - Error: `"  memory-index.md:{lineno}: orphan index entry '{key}' has no matching semantic header in agents/decisions/"`

5. **check_collisions()** (memory_index_checks.py lines 213-245)
   - Detect multiple entries resolving to same heading via fuzzy matching
   - Uses `_resolve_entry_heading()` to find best fuzzy match (50.0 threshold)
   - Error: `"  collision: entries '{k}' (line {ln}), ... resolve to same heading '{heading}'"`
   - Rationale: Prevents ambiguous triggers mapping to same documentation

6. **_check_duplicate_headers()** (memory_index.py lines 152-164)
   - Detect duplicate headers across different files
   - Error: `"  Duplicate header '{title}' found in multiple files: {filepath}:{lineno}"` (only if in different files)

### 6.3 Validation Checks (Autofixable)

**Autofixable checks** (run after non-autofixable, can be auto-corrected by default):

1. **check_entry_placement()** (memory_index_helpers.py lines 240-257)
   - Verify entries are in correct file sections
   - Compares entry section name against source file from headers
   - Error: `"  memory-index.md:{lineno}: entry '{key}' in section '{section}' but header is in '{source_file}'"`
   - **Autofix:** Moves entry to correct section

2. **check_entry_sorting()** (memory_index_checks.py lines 136-189)
   - Verify entries within sections match file order
   - Extracts source line numbers from headers, compares entry order
   - Error: `"  Section '{section_name}': entries not in file order"`
   - **Autofix:** Reorders entries to match file order

3. **check_structural_entries()** (memory_index_helpers.py lines 281-296)
   - Detect entries pointing to structural (dot-prefixed) sections
   - Strips operator prefix for comparison against structural set
   - Error: `"  memory-index.md:{lineno}: entry '{key}' points to structural section"`
   - **Autofix:** Removes structural entries via `autofix_index()`

### 6.4 Autofix Process

**autofix_index()** (memory_index_helpers.py lines 218-237)

**Autofix rebuilds index with correct:**
- Section ordering (semantic file sections first, ordered alphabetically)
- Entry ordering within sections (by source line number in file)
- Structural entries removed (dot-prefixed sections cleaned up)

**Process:**
1. Extract current index structure (`extract_index_structure()`)
2. Build corrected file entries map (`_build_file_entries_map()`)
3. Rebuild index content (`_rebuild_index_content()`)
4. Write corrected index back to disk

**Rebuild rules:**
- Preamble preserved exactly
- Exempt sections (non-file-path sections) preserved as-is
- File sections output in sorted order
- Entries within sections sorted by source line number
- Empty file sections (all entries removed) kept as stubs

### 6.5 Key Transformation Rules

**Entry key extraction (memory_index.py lines 39-63):**

```python
def _extract_entry_key(line: str) -> str | None:
    if line.startswith(("/when ", "/how ")):
        operator, rest = line.split(" ", 1)
        trigger = rest.split("|", 1)[0].strip()  # Extract before pipe
        # Map /how to "how to" for heading matching
        operator_prefix = "how to" if operator == "/how" else "when"
        return f"{operator_prefix} {trigger}".lower()
    if " — " in line:
        key = line.split(" — ")[0].strip()
        return key.lower()
    return line.lower()
```

**Operator prefix mapping (for heading matching):**
- `/when X` → `"when x"` (heading comparison key)
- `/how X` → `"how to x"` (heading comparison key)
- `X — Y` → `"x"` (em-dash format, deprecated)

**Prefix stripping** (memory_index_helpers.py lines 22-34):
```python
def _strip_operator_prefix(key: str) -> str:
    """Strip operator prefix for structural comparison."""
    if key.startswith("when "):
        return key[5:]       # Remove "when " prefix
    if key.startswith("how to "):
        return key[7:]       # Remove "how to " prefix
    return key               # Old format, no prefix
```
- Used for structural header comparison (structural headers have no prefix)

### 6.6 Fuzzy Matching for Runtime Recovery

**Fuzzy threshold:** 50.0 (used in _check_orphan_headers, _resolve_entry_heading)

**score_match() function** (from claudeutils.when.fuzzy module)
- Scores entry keys against headers despite compression/rewording
- Example: `/when choosing review gate` fuzzy-matches `When Choosing Review Gate` header
- **Used only for validation orphan check as fallback** — exact match attempted first
- **Does NOT replace exact key matching requirement** (index entry key must exactly match heading key)

**Rationale (learnings.md lines 30-33):**
```
## Index exact keys not fuzzy
- Anti-pattern: Using fuzzy matching in validator to bridge compressed triggers to verbose headings
- Correct pattern: Index entry key must exactly match heading key — fuzzy matching is only for resolver runtime recovery
- Rationale: Exact keys are deterministic and debuggable; fuzzy in validation creates invisible mismatches
```

### 6.7 Validation Output

**validate() returns:** List of error strings (empty if no errors)

**Error classification:**
- Non-autofixable: Blocks precommit (must be fixed manually)
- Autofixable: Can be auto-corrected by default (with `autofix=True`)

**Precommit hook integration:**
- Called during `just precommit` validation suite
- Blocks commits with non-autofixable errors
- Auto-corrects autofixable errors if `autofix=True` (default)

---

## 7. Key Learning Format and Behavioral Trigger Framing

### 7.1 Current Learnings Examples

**From agents/learnings.md (current state):**

**Example 1: Symptom-Oriented (Correct)**
```markdown
## Symptom-oriented index trigger keys
- Anti-pattern: Index entry key describes root cause or uses internal jargon
  (e.g., "transformation table", "prose gates", "non-cognitive solutions")
- Correct pattern: Key describes situation agent encounters
  (e.g., "choosing review gate", "prevent skill steps from being skipped")
- Rationale: Agents search by symptom (what they observe), not root cause
```
- Trigger would be: `/when choosing review gate` (symptom)
- NOT: `/when transformation table` (jargon/root cause)

**Example 2: Exact Key Matching (Correct)**
```markdown
## Index exact keys not fuzzy
- Anti-pattern: Using fuzzy matching in validator to bridge compressed triggers to verbose headings
- Correct pattern: Index entry key must exactly match heading key — fuzzy matching is only for resolver runtime recovery
- Rationale: Exact keys are deterministic and debuggable
```
- Memory index entry must exactly match semantic header (after operator prefix extraction)
- Fuzzy matching only used at runtime recovery in `/when` skill

**Example 3: DP Zero-Ambiguity (Implementation Detail)**
```markdown
## DP zero-ambiguity in subsequence matching
- Anti-pattern: Initializing DP matrix with 0.0 for all cells
- Correct pattern: Initialize score[i>0][j] with -inf, only score[0][j] = 0.0
- Evidence: "when mock tests" scored 128.0 against candidate with no 'o' or 'k'
```
- Consolidates to: `agents/decisions/implementation-notes.md`
- Index entry: `/how initialize DP matrix for subsequence matching` (procedural, how-to)

### 7.2 Entry Title Constraints

**From learnings.py:**
- Format: `## Title` (markdown H2 header)
- Max 5 words per title
- No duplicates (case-insensitive)
- No empty titles

**Examples:**
- ✅ `## Tool batching unsolved` (4 words)
- ✅ `## RED pass blast radius assessment` (5 words)
- ❌ `## Tool batching documentation and implementation issues unsolved` (7 words, exceeds max)

---

## 8. Trigger Format Validation: check_trigger_format Function

**Location:** `/Users/david/code/claudeutils/src/claudeutils/validation/memory_index_checks.py` lines 76-133

**Function signature:**
```python
def check_trigger_format(entries: dict[str, tuple[int, str, str]]) -> list[str]
```

**Input:** Dictionary of entries from `extract_index_entries()` mapping key → (lineno, full_entry, section)

**Validation Rules:**

1. **Operator prefix required (lines 93-119):**
   - Entry must start with `/when ` or `/how `
   - Allow `/when` and `/how` without trailing space (empty trigger case handled below)
   - Error if operator is invalid (e.g., `/what`, `/where`)
   - Error if entry starts with `/` but not `/when` or `/how` (invalid operator)
   - Error if entry doesn't start with `/` and isn't in exempt section (old em-dash format)

2. **Non-empty trigger required (lines 125-131):**
   - After operator and any pipes, trigger text must not be empty
   - Extracts trigger: `rest.split("|", 1)[0].strip()` (text before pipe)
   - Error if trigger is empty after extraction and stripping

3. **Exempt sections (lines 87-89):**
   - Entries in exempt sections pass all checks (historical format preserved)
   - `EXEMPT_SECTIONS` defined in memory_index_helpers.py (currently empty set)

**Error messages generated:**
```
memory-index.md:{lineno}: invalid operator prefix (use /when or /how): '{full_entry}'
memory-index.md:{lineno}: entry missing operator prefix (no operator prefix): '{full_entry}'
memory-index.md:{lineno}: /when has empty trigger: '{full_entry}'
memory-index.md:{lineno}: /how has empty trigger: '{full_entry}'
```

**Integration:**
- Called by `validate()` function (line 255 in memory_index.py)
- Non-autofixable: Must be manually fixed before commit
- Blocks precommit validation if any errors found

---

## 9. Integration Points and Data Flow

### 9.1 End-to-End Consolidation Flow

```
User adds learning → agents/learnings.md
         ↓
Handoff triggers consolidation check
         ↓
learning-ages.py calculates ages
         ↓
Filter entries ≥7 active days
         ↓
Remember-task agent batch input
         ↓
Pre-consolidation checks
  ├─ Supersession detection
  ├─ Contradiction detection
  └─ Redundancy detection
         ↓
Surviving entries → Consolidation protocol
         ↓
Update target file (fragment, decision file, skill reference)
         ↓
Add memory-index.md entry
         ↓
Add CLAUDE.md @-ref OR .claude/rules/ entry
         ↓
Remove from agents/learnings.md (keep 3-5 most recent)
         ↓
Write consolidation-report.md
         ↓
Commit changes
```

### 9.2 Discovery Mechanism Chain

**Entry point:** `/when <trigger>` or `/how <trigger>` skill invocation

**Resolution chain:**
1. Check memory-index.md entry exists for trigger
2. Extract section (file path)
3. Read target file
4. Find matching semantic header (exact or fuzzy match as fallback)
5. Return section content

**Index structure enables:**
- Quick section lookup (file path)
- Semantic header -> file navigation
- Pipe-delimited synonym expansion
- Fuzzy fallback for compressed triggers

### 9.3 Validation Integration

**Precommit hook:** `.claude/hooks/pretooluse-*.sh` (settings.json PreToolUse)

**Validation sequence:**
1. `check_trigger_format()` — Non-autofixable, must pass
2. `check_duplicate_entries()` — Non-autofixable
3. `_check_orphan_headers()` — Non-autofixable (fuzzy matching as fallback)
4. `check_orphan_entries()` — Non-autofixable
5. `check_collisions()` — Non-autofixable
6. `_check_duplicate_headers()` — Non-autofixable
7. `check_entry_placement()` → Autofixable
8. `check_entry_sorting()` → Autofixable
9. `check_structural_entries()` → Autofixable

---

## 10. Compression Key Utility

**Location:** `/Users/david/code/claudeutils/agent-core/bin/compress-key.py`

**Purpose:** Verify trigger uniqueness against existing semantic headers

**Invocation:**
```bash
compress-key.py <heading> [decisions-dir]
# Default decisions-dir: agents/decisions/
```

**Usage during consolidation (SKILL.md lines 68-69):**
```
Generate `/when` or `/how` entry in `agents/memory-index.md`:
- Trigger naming: Use key compression tool (`agent-core/bin/compress-key.py`)
  to verify uniqueness
```

**Functionality:**
1. Load heading corpus from all semantic headers in decisions/ directory
2. Compress new heading using `compress_key()` from claudeutils.when.compress
3. Return compressed key (removed common words, shortened)
4. Verify compressed key doesn't collide with existing corpus

---

## 11. Known Patterns and Constraints

### 11.1 Learning Quality Tiers

**Principle-level (consolidate immediately):**
- States general constraint or pattern
- Applies beyond specific incident
- Example: "Always load skill context before editing"

**Incident-specific (reject/revise):**
- Describes what happened, not what to do
- Narrow to one case
- Should be revised to extract principle

**Meta-learnings (use sparingly):**
- Rules about rules
- Only when behavioral constraint required
- Example: "Soft limits normalize deviance"

### 11.2 Retention Rules by Age

| Age | Action | Reason |
|-----|--------|--------|
| < 7 days | Keep in staging | Insufficient validation |
| 7+ days, proven | Consolidate | Ready for permanent docs |
| Superseded | Drop | Newer entry covers same topic |
| Contradicted | Escalate | Conflict with existing documentation |
| Redundant (>70% overlap) | Drop | Already documented elsewhere |

### 11.3 Exact Key Matching Requirement

**Critical constraint (learnings.md lines 30-33):**
- Index entry key must EXACTLY match semantic header key
- Fuzzy matching is ONLY for runtime recovery (/when skill)
- Fuzzy in validation creates invisible mismatches when scores drift below threshold
- Entry keys include operator prefix (`"when X"`, `"how to X"`)
- Semantic headers have NO operator prefix — extraction required for comparison

**Example mapping:**
- Semantic header: `## When Writing Mock Tests`
- Entry key extraction: `/when writing mock tests` → `"when writing mock tests"` (lowercase)
- Comparison: `"when writing mock tests"` exactly matches header key `"when writing mock tests"` (after casing normalization)

---

## 12. Files Summary

### Core Infrastructure

| Path | Purpose |
|------|---------|
| `/Users/david/code/claudeutils/agent-core/skills/remember/SKILL.md` | Remember skill execution protocol and constraints |
| `/Users/david/code/claudeutils/agent-core/agents/remember-task.md` | Delegated consolidation agent (sonnet) |
| `/Users/david/code/claudeutils/agent-core/bin/learning-ages.py` | Calculate per-entry git-active-day age for consolidation eligibility |
| `/Users/david/code/claudeutils/agent-core/bin/compress-key.py` | Verify trigger uniqueness against semantic header corpus |

### Skill References

| Path | Purpose |
|------|---------|
| `/Users/david/code/claudeutils/agent-core/skills/remember/references/consolidation-patterns.md` | Target file selection, progressive disclosure, consolidation workflow |
| `/Users/david/code/claudeutils/agent-core/skills/remember/references/rule-management.md` | Rule tiering, budgeting, maintenance strategies (reference only, not inspected) |
| `/Users/david/code/claudeutils/agent-core/skills/remember/examples/remember-patterns.md` | Usage patterns: error handling, workflow improvement, design decisions |

### Validation and Learnings

| Path | Purpose |
|------|---------|
| `/Users/david/code/claudeutils/src/claudeutils/validation/learnings.py` | Learning title format, max word count, uniqueness validation |
| `/Users/david/code/claudeutils/src/claudeutils/validation/memory_index.py` | Main validation orchestrator, non-autofixable checks |
| `/Users/david/code/claudeutils/src/claudeutils/validation/memory_index_checks.py` | Individual check functions (trigger format, duplicates, orphans, collisions) |
| `/Users/david/code/claudeutils/src/claudeutils/validation/memory_index_helpers.py` | Header extraction, index structure manipulation, autofix logic |

### Active Documentation

| Path | Purpose |
|------|---------|
| `/Users/david/code/claudeutils/agents/learnings.md` | Append-only staging for active learnings (≥7 days consolidated) |
| `/Users/david/code/claudeutils/agents/memory-index.md` | Index entries by decision file section, `/when` and `/how` triggers |
| `/Users/david/code/claudeutils/agent-core/fragments/*.md` | Behavioral rules and cross-cutting concerns |
| `/Users/david/code/claudeutils/agents/decisions/*.md` | Technical and architectural decisions (17 decision files) |

### Configuration

| Path | Purpose |
|------|---------|
| `/Users/david/code/claudeutils/.claude/settings.json` | Hook configuration (PreToolUse, PostToolUse, UserPromptSubmit) |
| `/Users/david/code/claudeutils/.claude/rules/*.md` | Path-scoped rule files for domain-specific constraints |

---

## 13. Patterns and Anti-Patterns

### 13.1 Correct Patterns

**Symptom-oriented trigger naming:**
```
✅ /when choosing review gate           (symptom: agent choosing between gates)
❌ /when transformation table           (jargon: internal implementation)
```

**Exact key matching in index:**
```
✅ Memory index entry: /when choosing review gate
   Semantic header: ## When Choosing Review Gate
   Match: Exact (after operator extraction + lowercasing)

❌ Memory index entry: /when review gate
   Semantic header: ## When Choosing Review Gate
   Match: FUZZY only (if in validation orphan check)
```

**Progressive disclosure for learnings:**
```
✅ Always-active rule → @-ref in CLAUDE.md
✅ File-type-specific → .claude/rules/descriptive-name.md with path frontmatter
✅ Skill-specific patterns → .claude/skills/{skill}/references/learnings.md
```

**Consolidation trigger rules:**
- 7+ active days from git blame
- Pre-consolidation checks (supersession, contradiction, redundancy)
- Conservative bias: When uncertain, consolidate (false positives acceptable)

### 13.2 Anti-Patterns

**Index entry validation using fuzzy matching to bridge compression:**
```
❌ Validator uses fuzzy matching to accept partial matches
✅ Validator requires exact key match; fuzzy only at runtime resolution
```

**Keeping learnings in session.md permanently:**
```
❌ Keeps session bloat, loses historical context
✅ Consolidate to permanent docs, remove from session after consolidation
```

**DP matrix initialization for subsequence matching:**
```
❌ Initialize all cells with 0.0
   → impossible states indistinguishable from base case
   → false positives in matching

✅ Initialize score[i>0][j] = -inf, score[0][j] = 0.0
   → impossible states propagate -inf
   → matches only when valid
```

---

## 14. Current State and Known Issues

### 14.1 Learnings File State

**Current:** 47 lines, 7 entries
- All entries recent (working pool)
- No entries ready for consolidation (all < 7 days based on session context)
- Entries track recent findings: tool batching, RED pass blast radius, context signal competition, DP algorithms, index format constraints

### 14.2 Memory Index State

**Current:** 80+ entries across 17 decision files
- Organized by file section
- All entries in `/when` or `/how` format
- Many entries have pipe-delimited synonyms for keyword expansion
- Validation status: PASSING (as of precommit checks)

### 14.3 Known Constraints and Gotchas

**Behavioral trigger framing (not always applied):**
- Older entries use root-cause/jargon language
- Recent consolidations use symptom-oriented framing (e.g., learnings.md lines 39-42)
- Learning staging process should enforce behavioral framing at entry time (consider hook or remember skill validation)

**Exact key matching requirement enforcement:**
- Validator uses fuzzy matching as fallback in orphan header check
- Intention: Only for runtime recovery fallback, not to accept partial matches
- Risk: Fuzzy scores drifting below threshold creates invisible mismatches
- Mitigation: compress-key.py verification during trigger naming

**Rule file directive adherence unreliable:**
- Agents ignore injected "load X before modifying" directives from .claude/rules/
- Same failure mode as passive index (2.9% baseline recall)
- Session learnings.md lines 44-46 notes this finding
- Blocking hooks or inline code comments may be more effective than rules

---

## 15. Entry Points and APIs

### 15.1 User-Facing Commands

**Interactive `/remember` skill:**
```bash
/remember
# Invokes agent-core/skills/remember/SKILL.md
# Steps: Understand → File selection → Draft → Apply → Update discovery
```

**Memory index query:**
```bash
/when <trigger>          # Behavioral knowledge recall
/how <trigger>           # Procedural knowledge recall
```

### 15.2 Programmatic APIs

**Learning age calculation:**
```python
from agent-core/bin/learning-ages.py
# Usage: learning-ages.py [learnings-file]
# Output: Markdown report with per-entry ages
```

**Validation:**
```python
from src.claudeutils.validation.learnings import validate
errors = validate(Path("agents/learnings.md"), project_root)

from src.claudeutils.validation.memory_index import validate
errors = validate("agents/memory-index.md", project_root, autofix=True)
```

**Trigger compression verification:**
```bash
compress-key.py "When Choosing Review Gate" [decisions-dir]
# Output: Compressed key for uniqueness checking
```

---

## 16. Testing Coverage

**Learnings validation tests:**
- Path: `/Users/david/code/claudeutils/tests/test_validation_learnings.py`
- Covers: Title format, word count, uniqueness, preamble handling

**Learning ages tests:**
- Path: `/Users/david/code/claudeutils/tests/test_learning_ages.py`
- Path: `/Users/david/code/claudeutils/tests/test_learning_ages_integration.py`
- Covers: Age calculation, git blame integration, consolidation date detection

**Memory index validation tests:**
- Implied in test suite (not separately enumerated in glob results)
- Covers: Trigger format, duplicates, orphans, collisions, placement, sorting

---

## Conclusion

The remember skill and learnings consolidation pipeline implements a four-stage flow with strong constraints around learning quality, trigger framing (symptom-oriented, not jargon), exact key matching for validation (fuzzy only at runtime), and conservative pre-consolidation checks. The system prioritizes discoverability through behavioral triggers and progressive disclosure (always-loaded CLAUDE.md refs, skill-triggered references, path-scoped rules). Validation is comprehensive but has known gaps (rule file adherence ~2.9% baseline), and the pipeline can be strengthened by enforcing behavioral trigger framing at learning staging time (possibly via hook or remember skill validation).
