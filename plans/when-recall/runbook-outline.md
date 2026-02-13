# `/when` Memory Recall System — Runbook Outline

**Design:** plans/when-recall/design.md
**Created:** 2026-02-12
**Model:** haiku (TDD execution), sonnet (migration/scripting)

---

## Requirements Mapping

| Requirement | Implementation Phase | Notes |
|-------------|---------------------|-------|
| FR-1: Agent invokes `/when <trigger>` | Phase 0-5, 8 (resolver + skills) | Resolver in Phase 3-4, skills in Phase 8 |
| FR-2: Fuzzy matching bridges triggers to headings | Phase 0 (fuzzy engine) | Foundation for all components |
| FR-3: Output includes ancestor + sibling navigation | Phase 2 (navigation module) | Resolver consumes navigation in Phase 3 |
| FR-4: Validator enforces bidirectional integrity | Phase 6 (validator update) | Uses fuzzy engine from Phase 0 |
| FR-5: `/remember` produces `/when` format | Phase 10 (remember skill update) | After format proven stable |
| FR-6: All ~159 entries migrated | Phase 9 (index migration) | Includes heading renames |
| FR-7: Three resolution modes (trigger/.section/..file) | Phase 3 (resolver) | Mode detection + dispatch |
| NFR-1: Fuzzy engine shared across 3 consumers | Phase 0 | Single implementation, imported by resolver/validator/compress-key |
| NFR-2: All components via TDD | Phases 0-7, 11 | RED/GREEN cycles |
| NFR-3: >10% recall within 30 sessions | Phase 11 (recall parser update) | Measurement infrastructure |
| NFR-4: Index remains @-loaded in CLAUDE.md | Phase 9 | Migration preserves @-reference |

---

## Phase Structure

### Phase 0: Fuzzy Engine Foundation (type: tdd)

**Complexity:** Medium
**Model:** haiku
**Dependencies:** None (foundation)

- Cycle 0.1: Character subsequence matching
- Cycle 0.2: Boundary bonus scoring (whitespace, delimiters)
- Cycle 0.3: Consecutive match bonus
- Cycle 0.4: Gap penalties
- Cycle 0.5: Word-overlap tiebreaker
- Cycle 0.6: Minimum score threshold
- Cycle 0.7: Rank matches with limit
- Cycle 0.8: Prefix word inclusion (query: "when X" not "X")

**Rationale:** Foundation for resolver (Phase 3), validator (Phase 6), compress-key (Phase 7). Build first, test thoroughly.

---

### Phase 1: Index Parser (type: tdd)

**Complexity:** Low
**Model:** haiku
**Dependencies:** None (Pydantic only)

- Cycle 1.1: Parse `/when trigger | extras` format
- Cycle 1.2: Extract operator (when/how)
- Cycle 1.3: Split primary trigger and extra triggers
- Cycle 1.4: Validate format (operator prefix, pipe separator)
- Cycle 1.5: Malformed entry handling (skip with warning)

**Rationale:** Independent module, no fuzzy dependency. Can run parallel with Phase 0.

---

### Phase 2: Navigation Module (type: tdd)

**Complexity:** Medium
**Model:** haiku
**Dependencies:** Phase 1 (WhenEntry model for sibling computation)

- Cycle 2.1: Extract heading hierarchy from file content
- Cycle 2.2: Compute ancestor headings (H4→H3→H2→file)
- Cycle 2.3: Handle flat H2 files (workflow-core pattern)
- Cycle 2.4: Structural heading detection (skip `.` prefix)
- Cycle 2.5: Compute sibling entries (requires WhenEntry structures from Phase 1)
- Cycle 2.6: Format navigation links (`/when .Section`, `/when ..file.md`)

**Rationale:** Resolver consumes navigation output. Navigation operates on file content strings and WhenEntry structures, no resolver dependency.

---

### Phase 3: Resolver Core (type: tdd)

**Complexity:** High
**Model:** haiku
**Dependencies:** Phase 0 (fuzzy), Phase 1 (parser), Phase 2 (navigation)

- Cycle 3.1: Mode detection (trigger vs `.section` vs `..file`)
- Cycle 3.2: Trigger mode — fuzzy match against index entries, return matching heading
- Cycle 3.3: Section mode — global unique heading lookup in decision files
- Cycle 3.4: File mode — relative path resolution (agents/decisions/ base)
- Cycle 3.5: Section content extraction from decision file (heading to next same-level heading)
- Cycle 3.6: Output formatting (heading + content + navigation links) **[Checkpoint: core resolver logic complete]**
- Cycle 3.7: Error handling — trigger not found, suggest top 3 closest matches via fuzzy
- Cycle 3.8: Error handling — section not found, list all available headings
- Cycle 3.9: Error handling — file not found, list all .md files in agents/decisions/

**Rationale:** Core logic integrating all prior phases. Sequential dependency on fuzzy/parser/navigation. Checkpoint after 3.6 recommended due to 9-cycle length.

---

### Phase 4: CLI Integration (type: tdd)

**Complexity:** Low
**Model:** haiku
**Dependencies:** Phase 3 (resolver)

- Cycle 4.1: Click command setup (`when_cmd` function)
- Cycle 4.2: Operator argument (when/how)
- Cycle 4.3: Query argument (nargs=-1, variadic)
- Cycle 4.4: Invoke resolver with joined query
- Cycle 4.5: Error handling (print to stderr, exit 1)

**Rationale:** Thin CLI wrapper around resolver. Straightforward integration.

---

### Phase 5: Bin Script Wrapper (type: general)

**Complexity:** Trivial
**Model:** haiku
**Dependencies:** Phase 4 (CLI must be registered)

- Step 5.1: Create `agent-core/bin/when-resolve.py` with shebang
- Step 5.2: Call `claudeutils.when.cli.when_cmd()` with sys.argv

**Rationale:** Non-code artifact, no tests needed. Create after CLI proven.

---

### Phase 6: Validator Update (type: tdd)

**Complexity:** Medium
**Model:** haiku
**Dependencies:** Phase 0 (fuzzy), Phase 1 (parser)
**Prior State:** Fuzzy engine provides score_match() and rank_matches(), WhenEntry model defines entry structure

- Cycle 6.1: Replace em-dash parsing with `/when` format parsing (reuse Phase 1 parser)
- Cycle 6.2: Format validation (operator prefix required, trigger non-empty, extras comma-separated)
- Cycle 6.3: Fuzzy bidirectional integrity (each entry fuzzy-expands to exactly one heading)
- Cycle 6.4: Collision detection (no two triggers resolve to same heading via fuzzy)
- Cycle 6.5: Remove word count check (obsolete for trigger format)
- Cycle 6.6: Update autofix for new format (placement, ordering, structural entry removal)
- Cycle 6.7: Update EXEMPT_SECTIONS (empty set after migration completes)

**Rationale:** Critical for migration safety. Uses fuzzy engine from Phase 0, reuses WhenEntry from Phase 1.

---

### Phase 7: Key Compression Tool (type: tdd)

**Complexity:** Low
**Model:** haiku
**Dependencies:** Phase 0 (fuzzy)

- Cycle 7.1: Load heading corpus from decision files
- Cycle 7.2: Generate candidate triggers (word-drop algorithm)
- Cycle 7.3: Verify uniqueness via fuzzy scoring
- Cycle 7.4: Suggest minimal unique trigger

**Rationale:** Migration helper tool. Independent from resolver/skills.

---

### Phase 8: Skill Wrappers (type: general)

**Complexity:** Trivial
**Model:** haiku
**Dependencies:** Phase 5 (bin script must exist)

- Step 8.1: Create `/when` skill SKILL.md with frontmatter
- Step 8.2: Create `/how` skill SKILL.md with frontmatter
- Step 8.3: Test skill triggering (manual verification)

**Rationale:** Non-code artifacts using plugin-dev:skill-development guidance. Create after bin script proven.

---

### Phase 9: Index Migration (type: general)

**Complexity:** High
**Model:** sonnet
**Dependencies:** Phase 6 (validator must support new format), Phase 7 (compression tool)
**Prior State:** Validator supports `/when` format and fuzzy matching, compress-key verifies trigger uniqueness

- Step 9.1: Build heading→trigger mapping (159 entries, use compress-key for uniqueness)
- Step 9.2: Script heading renames in decision files (~131 semantic headings, preserve structural `.` headings)
- Step 9.3: Grep for `@` references to old headings (update atomically with renames)
- Step 9.4: Convert index entries to `/when` format (script-assisted, operator selection per entry type)
- Step 9.5: Run validator to verify migration correctness **[Checkpoint: validator must pass before proceeding]**
- Step 9.6: Update consumption header (remove "scan mentally", add `/when`/`/how` invocation examples)
- Step 9.7: Remove "Behavioral Rules" exempt section (fragments are @-loaded, indexing is noise)
- Step 9.8: Redistribute "Technical Decisions (mixed)" entries to file-grouped sections (create new sections for files without entries)

**Rationale:** Large-scope migration requiring sonnet judgment and scripting. Atomic commit (all entries + all headings + validator + consumption header). Validator checkpoint critical before documentation updates.

---

### Phase 10: Remember Skill Update (type: general)

**Complexity:** Low
**Model:** haiku
**Dependencies:** Phase 9 (format must be proven stable)

- Step 10.1: Update entry generation to produce `/when` format
- Step 10.2: Add trigger naming guidelines (plain prose, 2-5 words)
- Step 10.3: Reference compress-key tool for uniqueness verification

**Rationale:** Skill content update. Wait for migration to prove format stability.

---

### Phase 11: Recall Parser Update (type: tdd)

**Complexity:** Low
**Model:** haiku
**Dependencies:** Phase 1 (parser implementation proven)

- Cycle 11.1: Consume `when/index_parser.py` or reimplement format
- Cycle 11.2: Update `recall/index_parser.py` for `/when` format
- Cycle 11.3: Verify recall analysis still produces valid reports

**Rationale:** Update measurement infrastructure to work with new format. Can wait until after migration.

---

## Key Decisions Reference

Design decisions guide implementation:

- **D-1 (Two-field format):** `/when trigger | extras` — no description field
- **D-2 (Sections in files):** Keep decisions grouped, no file atomization
- **D-3 (Two operators):** `/when` + `/how`, no `/what`/`/why`
- **D-4 (Custom fuzzy engine):** ~80 lines, tuned scoring constants
- **D-5 (Direct output):** Script outputs content, not file path
- **D-6 (Heading renames match triggers):** `### When <trigger>`
- **D-7 (Validator uses fuzzy):** Not exact match
- **D-8 (Atomic migration):** All entries + headings in one commit
- **D-9 (No word count):** Removed from validator

---

## Expansion Guidance

**Phase type distribution:**
- TDD phases (0-7, 11): Behavioral modules with clear inputs/outputs
- General phases (5, 8-10): Non-code artifacts (skills, migration, documentation)

**Parallelization opportunities:**
- Phase 0 (fuzzy) + Phase 1 (parser) + Phase 2 (navigation) — no dependencies
- Phase 6 (validator) + Phase 7 (compress-key) — both depend on Phase 0 only

**Integration points:**
- Phase 3 (resolver) integrates fuzzy + parser + navigation
- Phase 4 (CLI) integrates resolver
- Phase 9 (migration) uses validator + compress-key

**Migration sequencing:**
1-7: Build components
8: Skills (requires bin script from 5)
9: Migrate (requires validator from 6, compress-key from 7)
10-11: Post-migration updates

**Checkpoint recommendations:**
- Mid-phase after Cycle 3.6 (resolver core logic complete, error handling follows)
- Full checkpoint after Phase 3 (resolver core with all error modes complete)
- Full checkpoint after Phase 6 (validator update critical for migration)
- Full checkpoint after Phase 9 (migration is high-risk, validator pass required before docs)

**File size monitoring:**
- Phase 0 (fuzzy.py): ~80 lines (safe)
- Phase 3 (resolver.py): ~150 lines (safe)
- Phase 2 (navigation.py): ~80 lines (safe)
- No splits anticipated

**Domain validation:** No domain-specific validation skill exists for memory index components.

---

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Cycle expansion specifics:**

Phase 0 (Fuzzy Engine):
- Cycles 0.2-0.4: Include scoring constant values in test assertions (boundary bonus=10/9/7, consecutive=4, gap=-3/-1)
- Cycle 0.5: Word-overlap tiebreaker requires test cases with identical fzf scores
- Cycle 0.8: Prefix word test must verify "when X" query not "X" alone

Phase 3 (Resolver Core):
- Cycle 3.2: Test both exact trigger match and fuzzy match scenarios
- Cycle 3.5: Content extraction must handle both flat H2 files and nested H2/H3 structures
- Cycle 3.7-3.9: Error suggestions limited to top 3 matches (prevent overwhelming output)
- Mid-phase checkpoint after 3.6: Commit core resolver logic before error handling cycles

Phase 6 (Validator):
- Cycle 6.1: Reuse WhenEntry parser from Phase 1, don't reimplement
- Cycle 6.3: Fuzzy uniqueness test requires heading corpus fixture
- Cycle 6.6: Autofix mechanics preserved from current validator, format parsing changes only

Phase 9 (Migration):
- Step 9.1: Use compress-key tool to verify each trigger is unique before building mapping
- Step 9.5: Hard gate — validator must pass with zero errors before 9.6-9.8
- Atomic commit: All changes in single commit (entries + headings + references + docs)

**Checkpoint validation:**

After Phase 3 (resolver complete):
- Verify all three modes work (trigger, .section, ..file)
- Test navigation links in output (ancestor + sibling)
- Confirm error messages list alternatives

After Phase 6 (validator ready):
- Run validator on existing index (should fail — old format)
- Create small test index in new format (should pass)
- Verify fuzzy matching triggers validation errors appropriately

After Phase 9 (migration complete):
- Run full precommit validation (must pass)
- Manually test `/when` and `/how` skills (requires restart)
- Verify no broken `@` references from heading renames

**Parallelization execution:**

Phases 0, 1, 2 are fully independent:
- No shared files (fuzzy.py, index_parser.py, navigation.py)
- No logical dependencies (can develop simultaneously)
- Integration point is Phase 3 (resolver imports all three)

Phases 6 and 7 both depend only on Phase 0:
- Can run in parallel after Phase 0 complete
- No cross-dependencies (validator and compress-key independent)
- Both critical for Phase 9 migration

**References to include:**

Design sections for phase context:
- Phase 0: "D-4: Custom fuzzy engine" (scoring algorithm specification)
- Phase 2: "Structural heading handling" (navigation must skip `.` prefix)
- Phase 3: "Note on heading levels" (flat H2 vs nested H2/H3)
- Phase 6: "Validation checks (updated)" table (format rules)
- Phase 9: "Scope of heading renames" (semantic vs structural distinction)

Existing code patterns:
- `src/claudeutils/recall/index_parser.py`: WhenEntry Pydantic pattern
- `src/claudeutils/validation/memory_index*.py`: Autofix mechanics preservation
- `tests/test_recall_*.py`: Test structure conventions

**Common context for TDD phases:**

All TDD phases (0-4, 6-7, 11) should reference:
- `agents/decisions/testing.md`: TDD conventions (RED/GREEN/refactor, behavioral verification)
- `agents/decisions/implementation-notes.md`: Python patterns (Pydantic over dataclass, Path.cwd() not os.getcwd())

**Scope boundaries:**

Out of scope for all phases (design explicitly excludes):
- Cross-file explicit relations (future work)
- Hook-based auto-injection (future work)
- `/what` and `/why` operators (design decision D-3: dropped)
- Recall analysis architectural changes (parser update only in Phase 11)

Migration phase scope (IN):
- ~159 index entries converted to `/when` format
- ~131 semantic headings renamed with When/How to prefix
- Consumption header updated with invocation examples
- "Behavioral Rules" section removed (fragments @-loaded)
- "Technical Decisions (mixed)" redistributed to file-grouped sections

Migration phase scope (OUT):
- Validator refactoring (already done in Phase 6)
- Skill creation (already done in Phase 8)
- Recall tool changes (deferred to Phase 11)
