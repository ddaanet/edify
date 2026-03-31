# Phases 4-6: Justfile, Cleanup, Cache

**Purpose:** Extract portable recipes, clean up symlinks and configuration, regenerate caches.

**Dependencies:** Phases 1-3 complete (plugin components ready)

**Model:** Haiku (file operations and cleanup)

---

## Phase 4: Justfile Modularization

### Step 4.1: Create portable.just

**Objective:** Extract portable recipes to `plugin/just/portable.just` with minimal bash prolog.

**Execution Model:** Haiku

**Implementation:** Create `plugin/just/portable.just` with extracted recipes (claude, claude0, wt-*, precommit-base) and minimal bash prolog (fail, visible, color variables only).

**Design Reference:** D-5 (justfile import), Design Component 5

**Success Criteria:** portable.just created with 7 recipes + minimal bash prolog

---

### Step 4.2: Update root justfile

**Objective:** Add import statement, remove migrated recipes, keep project-specific.

**Execution Model:** Haiku

**Implementation:** Add `import 'plugin/just/portable.just'` at top, remove claude/wt-*/precommit-base recipes, keep test/format/check/lint/release.

**Success Criteria:** Root justfile imports portable.just, project recipes remain

---

## Phase 5: Cleanup and Validation

### Step 5.1: Remove symlinks

**Objective:** Remove all symlinks from `.claude/skills/`, `.claude/agents/`, `.claude/hooks/`.

**Execution Model:** Haiku

**Implementation:** Remove 16 skill symlinks, 12 agent symlinks (preserve `*-task.md` regular files), 4 hook symlinks.

**Success Criteria:** 32 symlinks removed, plan-specific agents preserved

---

### Step 5.2: Cleanup configuration and documentation

**Objective:** Remove hooks section from settings.json, remove sync-to-parent recipe, update fragment docs.

**Execution Model:** Haiku

**Implementation:**
- Remove `hooks` section from `.claude/settings.json`
- Remove `sync-to-parent` recipe from `plugin/justfile`
- Update fragments: claude-config-layout.md, sandbox-exemptions.md, project-tooling.md, delegation.md

**Success Criteria:** Configuration cleaned, docs updated

---

### Step 5.3: Validate all functionality

**Objective:** Test plugin discovery, hooks, agent coexistence, NFR validation.

**Execution Model:** Sonnet (validation requires analysis)

**Implementation:**
- Plugin discovery: `claude --plugin-dir ./plugin` → verify skills/agents load
- Hook testing: trigger each event type, verify behavior matches baseline
- Agent coexistence: create test `*-task.md`, verify both plugin and local agents visible
- NFR-1: compare edit→restart cycle time with baseline
- NFR-2: measure context size before/after (token count diff ≤ 5%)

**Success Criteria:** All tests pass, NFR requirements satisfied

---

## Phase 6: Cache Regeneration

### Step 6.1: Regenerate root just help cache

**Objective:** Rebuild `.cache/just-help.txt` after import changes.

**Execution Model:** Haiku

**Implementation:** Run `just cache` or manually regenerate with `just --list > .cache/just-help.txt`

**Success Criteria:** Cache contains imported recipes

---

### Step 6.2: Regenerate plugin just help cache

**Objective:** Rebuild `.cache/just-help-plugin.txt` after sync-to-parent removal.

**Execution Model:** Haiku

**Implementation:** Run `gmake -C plugin all` to regenerate

**Success Criteria:** Cache reflects removed recipe
