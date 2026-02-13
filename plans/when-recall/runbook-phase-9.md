# Phase 9: Index Migration

**Type:** General
**Model:** sonnet
**Checkpoint:** Full checkpoint after this phase (migration is high-risk, validator must pass)
**Dependencies:** Phase 6 (validator supports new format), Phase 7 (compression tool)
**Files:**
- `agents/memory-index.md` (all entries converted)
- `agents/decisions/*.md` (all semantic headings renamed)
- Any files with `@` references to old heading names

**Design reference:** Index Format section, D-8 (Atomic migration), "Scope of heading renames"

**Prior state:**
- Phase 6: Validator supports `/when` format with fuzzy bidirectional integrity
- Phase 7: `compress_key(heading, corpus)` suggests minimal unique triggers
- Current index: ~159 em-dash entries across ~14 sections
- Current headings: ~131 semantic headings across 14 decision files

**Scope IN:** Entry conversion, heading renames, consumption header, section restructuring
**Scope OUT:** Validator changes (Phase 6), skill creation (Phase 8), recall parser (Phase 11)

---

## Step 9.1: Build heading→trigger mapping

**Objective:** Create complete mapping from current headings to new `/when` or `/how` triggers.

**Script Evaluation:** Large — requires sonnet judgment for operator selection and trigger compression.

**Implementation:**
- Load heading corpus from all decision files
- For each semantic heading (non-`.` prefix):
  - Classify as `/when` (behavioral, ~73%) or `/how` (procedural, ~27%) based on content
  - Generate minimal unique trigger (manual or use compress-key tool from Phase 7 if available)
  - Record: `old_heading → (operator, trigger, extras)`
- Write mapping to `plans/when-recall/reports/migration-mapping.md` for review
- Mapping must cover all ~131 semantic headings

**Expected Outcome:** Complete mapping file with all headings covered, triggers verified unique.

**Error Conditions:**
- Trigger collision (two headings → same trigger) → adjust one trigger manually
- Ambiguous operator classification → default to `/when` (behavioral is majority)
- Heading not in any decision file → skip (orphan heading, validator will catch)

**Validation:**
- Every semantic heading has exactly one mapping entry
- No duplicate triggers in mapping
- Each trigger is unique against corpus (verify manually or with compress-key if available)

---

## Step 9.2: Script heading renames in decision files

**Objective:** Rename ~131 semantic headings with When/How to prefix.

**Script Evaluation:** Large — script-assisted bulk rename.

**Implementation:**
- For each mapping entry: `### Old Heading` → `### When New Trigger Text` or `### How to New Trigger Text`
- Heading case: Title Case (first letter of each word capitalized)
- Preserve heading level (H2, H3, H4 unchanged)
- Structural headings (`.` prefix) NOT renamed
- Script processes all decision files atomically

**Expected Outcome:** All semantic headings renamed per mapping. Structural headings untouched.

**Error Conditions:**
- Heading not found in file → warning (may have been renamed already or removed)
- Multiple headings match → error (heading text must be unique per file)

**Validation:**
- `grep -rn '### When\|### How to' agents/decisions/` shows renamed headings
- `grep -rn '###.*—' agents/decisions/` shows zero em-dash remnants in headings
- Structural heading count unchanged

---

## Step 9.3: Grep for `@` references to old headings

**Objective:** Find and update any `@` references to old heading names.

**Script Evaluation:** Medium — grep + targeted edits.

**Implementation:**
- For each renamed heading: grep across all project files for old heading text
- Update references atomically with heading renames
- Common reference locations: CLAUDE.md, session.md, learnings.md, skill files
- Use mapping from 9.1 to find old→new pairs

**Expected Outcome:** Zero dangling references to old heading names.

**Error Conditions:**
- Reference in git-ignored file → skip (not tracked)
- Reference in binary file → skip

**Validation:** `grep -rn` for each old heading name returns zero results across tracked files

---

## Step 9.4: Convert index entries to `/when` format

**Objective:** Convert all ~159 em-dash entries to `/when` or `/how` format.

**Script Evaluation:** Large — script-assisted with sonnet oversight.

**Implementation:**
- For each em-dash entry `Key — description`:
  - Find corresponding heading in mapping (9.1)
  - Generate `/when trigger | extra_triggers` or `/how trigger | extra_triggers`
  - Extra triggers derived from old key text (keyword extraction, synonyms)
- Preserve section structure (H2 file-path headings unchanged)
- Remove entries without heading matches (orphans cleaned up)

**Expected Outcome:** All entries in `/when` or `/how` format. Zero em-dash entries remaining.

**Error Conditions:**
- Entry with no heading match → remove (orphan entry, was already invalid)
- Entry in exempt section → handle per 9.7 and 9.8

**Validation:**
- `grep ' — ' agents/memory-index.md` returns zero matches (no em-dash entries)
- `grep '^/when\|^/how' agents/memory-index.md | wc -l` matches expected entry count

---

## Step 9.5: Run validator to verify migration correctness

**[Checkpoint: validator must pass before proceeding to 9.6-9.8]**

**Objective:** Verify migrated index passes all validation checks.

**Script Evaluation:** Direct — run existing tooling.

**Implementation:**
- Run `claudeutils validate memory-index`
- Must pass with zero errors
- Autofix may run (placement, ordering) — this is expected and correct

**Expected Outcome:** Validator passes. Zero errors. Autofix may reorder entries.

**Error Conditions:**
- Orphan entries → fix entry or heading in mapping
- Orphan headings → add missing entries
- Collision → adjust triggers to be unique
- **HARD GATE:** Do NOT proceed to 9.6-9.8 until validator passes with zero errors

**Validation:** `claudeutils validate memory-index` exit code 0, zero error output

---

## Step 9.6: Update consumption header

**Objective:** Replace passive "scan mentally" instruction with active invocation guidance.

**Script Evaluation:** Small — targeted text replacement.

**Implementation:**
Replace the current consumption header in `agents/memory-index.md` preamble with:

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

Remove old "scan mentally" instruction, "Consumption pattern" paragraph, and any references to "mentally scan loaded content."

**Expected Outcome:** Header provides active invocation examples. No passive scanning language.

**Error Conditions:** None expected (simple text replacement).

**Validation:** Read first 15 lines of `agents/memory-index.md` — verify new header format.

---

## Step 9.7: Remove "Behavioral Rules" exempt section

**Objective:** Remove the exempt section that indexes fragments already @-loaded in CLAUDE.md.

**Script Evaluation:** Small — section deletion.

**Implementation:**
- Find `## Behavioral Rules (fragments — already loaded)` section
- Delete section header and all entries within it
- These entries reference fragments loaded via CLAUDE.md `@` — indexing them is noise (per design)

**Expected Outcome:** Section and all its entries removed from `agents/memory-index.md`.

**Error Conditions:**
- Section not found → already removed or renamed (warning)
- Entries within section have headings in decision files → those headings remain (just not indexed)

**Validation:**
- `grep 'Behavioral Rules' agents/memory-index.md` returns zero results
- Entry count decreased by section entry count

---

## Step 9.8: Redistribute "Technical Decisions" entries

**Objective:** Convert the catch-all "Technical Decisions (mixed)" section into file-grouped sections.

**Script Evaluation:** Medium — parse entries, route to correct sections.

**Implementation:**
- Parse entries currently in "Technical Decisions (mixed — check entry for specific file)" section
- Each entry references a specific decision file (via old `Key — description` or new `/when` format)
- Create new H2 sections for files that don't already have sections:
  - `## agents/decisions/data-processing.md`
  - `## agents/decisions/cli.md`
  - `## agents/decisions/markdown-tooling.md`
  - `## agents/decisions/validation-quality.md`
  - `## agents/decisions/defense-in-depth.md`
- Move entries to their correct file section
- Remove the "Technical Decisions (mixed)" section header
- Run autofix to sort entries within new sections

**Expected Outcome:** No catch-all section remains. All entries in file-specific sections.

**Error Conditions:**
- Entry with unclear file reference → check heading location in decision files
- New section creates duplicate with existing → merge entries

**Validation:**
- `grep 'Technical Decisions' agents/memory-index.md` returns zero results
- `claudeutils validate memory-index` passes (sections match files)
