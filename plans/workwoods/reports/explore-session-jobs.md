# Exploration: Session.md and Jobs.md Usage Patterns

## Summary

Session.md and jobs.md are complementary state tracking files that coordinate worktree-aware session management across the codebase. Session.md tracks task execution state and carries forward work context between agent sessions. Jobs.md tracks plan lifecycle status (requirements → designed → planned → complete) with enforcement via validators. Both files are read by multiple parsing modules, CLI tools, and skills, with structured update protocols during handoff and worktree merge operations.

## Key Findings

### 1. Session.md Format and Structure

**File location:** `/Users/david/code/claudeutils-wt/design-workwoods/agents/session.md`

**Current example from actual codebase:**
```markdown
# Session: Worktree — Design workwoods

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Design workwoods** — `/design plans/workwoods/requirements.md` | opus
  - Plan: workwoods | Status: requirements
```

**Allowed sections** (from handoff/SKILL.md lines 94-101):
- `## Completed This Session` — Grouped by category/feature, tracking what was done this session
- `## Pending Tasks` — Carries forward from prior sessions, mutated only to mark completed or add new
- `## Worktree Tasks` — Tasks in active worktrees, preserved during handoff
- `## Blockers / Gotchas` — Issues discovered, root cause, impact, resolution
- `## Reference Files` — File references for context (validated by session_structure.py)
- `## Next Steps` — 1-2 sentence direction for next agent

**Target size:** 75-150 lines. Session.md is working memory (volatile, session-scoped), not persistent documentation.

**Task notation** (from handoff/SKILL.md lines 58-64):
```
- [ ] **Task Name** — description | model | restart?
- [x] **Completed Task** — description | model
- [ ] **Task in Worktree** → `slug` — description | model
```

**Fields:**
- Task Name: Prose identifier, must be unique across session.md and disjoint from learning keys in learnings.md (enables task-context.sh lookup)
- Description: Brief description
- Model: `haiku`, `sonnet`, `opus` (default: sonnet)
- Restart: Optional flag (only if session restart needed, omit otherwise)
- Slug: Worktree identifier (→ `slug` format, Unicode arrow U+2192)

**Task carry-forward protocol** (from handoff/SKILL.md lines 41-46):
- Read current Pending Tasks and Worktree Tasks sections
- Carry them forward verbatim — preserve every sub-item, metadata line, blocker
- Apply ONLY these mutations: mark completed `[x]`, append new tasks, update specific metadata
- DO NOT rewrite, compress, summarize, or de-duplicate existing sub-items
- Sub-items accumulate context from prior sessions and cannot be reconstructed

**Haiku task requirements** (from handoff/SKILL.md lines 66-90):
When scheduling haiku for implementation work, provide execution criteria:
- Runbook execution: `Plan: plan-name` reference
- Ad-hoc implementation: Acceptance criteria bullet list
- Script/tool enhancement: Test command or expected behavior
Example: `- [ ] **Enhance prepare-runbook.py** — Add phase file assembly | haiku\n  - Accept directory input, detect runbook-phase-*.md files\n  - Sort by phase number, prepend TDD frontmatter\n  - Verify: just test passes`

**Multiple handoffs before commit** (from handoff/SKILL.md lines 48-54):
If prior handoff content in session.md hasn't been committed, merge current work into it incrementally using Edit, not Write. This prevents losing accumulated context from multiple handoffs in same session.

### 2. Jobs.md Format and Structure

**File location:** `/Users/david/code/claudeutils-wt/design-workwoods/agents/jobs.md`

**Actual current structure:**
```markdown
# Jobs

Plan lifecycle tracking. Updated when plans change status.

**Status:** `requirements` → `designed` → `planned` → `complete`

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| continuation-prepend | requirements | Problem statement only |
| error-handling | requirements | Outline complete, Phase B blocked on workflow improvements |
| orchestrate-evolution | designed | Design.md complete, vet in progress, planning next |
| plugin-migration | planned | Runbook assembled: 15 steps, haiku execution ready |
| workwoods | requirements | Cross-tree worktree awareness, vet tracking, plan state inference, bidirectional merge |
| ... | ... | ... |

## Complete (Archived)

*48 plans completed and deleted. Git history preserves all designs/reports.*

Use `git log --all --oneline -- plans/<name>/` to find commits, `git show <hash>:<path>` to retrieve files.

**Recent:**
- `grounding-skill` — Ground skill with diverge-converge research procedure
- `when-recall` — `/when` memory recall system — 12 phases, merged to main, 2 deliverable reviews
- ... (other completed plans)
```

**Status values** (from jobs.md line 5):
- `requirements` — Problem statement documented, no design yet
- `designed` — Design document complete
- `planned` — Runbook created and prepared (not "in progress", but "ready to execute")
- `complete` — Plan finished, moved to archived section
- `—` (em-dash) — Special marker for non-plan items like "reports" directory

**Table format:**
- Column 1: Plan name (matches directory name in plans/)
- Column 2: Status value
- Column 3: Notes (free-form, includes context, blockers, completion details)

**Status transition rules** (from handoff/SKILL.md lines 233-236):
- Plan completed → Move from Plans section to "Complete (Archived)" with one-liner summary
- Design created → Move from Requirements to Designed
- Runbook created → Move from Designed to Planned

**Complete section notes** (from jobs.md lines 28-31):
- Completed plans are deleted from plans/ (no directory remains)
- Git history preserves all designs/reports via `git log --all -- plans/<name>/`
- Retrieval via `git show <hash>:<path>`
- Only recent completed plans shown in "Recent" list for reference

### 3. Session.md Parsing and Consumption

**Primary parsing module:** `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/session.py`

**Key functions:**

1. **`extract_task_blocks(content, section=None)`** (lines 18-82)
   - Parses session.md content into TaskBlock dataclass instances
   - TaskBlock fields: `name` (extracted from markdown), `lines` (all lines), `section` ("Pending Tasks" or "Worktree Tasks")
   - Pattern: `^- \[[ x>]\] \*\*(.+?)\*\*` (matches `- [ ]`, `- [x]`, `- [>]` with task name)
   - Collects continuation lines (indented lines following task)
   - Stops at next task, next section header, or blank line
   - Optional section filter to return only tasks from specific section

2. **`find_section_bounds(content, header)`** (lines 85-115)
   - Locates line bounds for section header (e.g., "## Pending Tasks")
   - Returns `(start_line_index, end_line_index)` tuple
   - Used to find insertion points for new content

3. **`move_task_to_worktree(session_path, task_name, slug)`** (lines 118-184)
   - Moves task from Pending Tasks to Worktree Tasks section
   - Adds slug marker to first line: `→ \`slug\``
   - Creates Worktree Tasks section if missing
   - Raises ValueError if task not found

4. **`remove_worktree_task(session_path, slug, worktree_branch)`** (lines 217-262)
   - Removes task from Worktree Tasks after completion
   - Checks worktree branch's session.md via `git show` to verify task completed
   - Only removes if task no longer in Pending Tasks in worktree branch
   - Idempotent: safe to call multiple times

**Worktree-specific helpers:**

5. **`_task_is_in_pending_section(task_name, worktree_branch, git_root)`** (lines 198-214)
   - Uses `git show <branch>:agents/session.md` to read worktree's session state
   - Checks if task name exists in worktree's Pending Tasks section
   - Cross-tree validation (reads from worktree branch via git)

6. **`_find_git_root(start_path)`** (lines 187-195)
   - Locates git repo root by searching for .git directory
   - Used by worktree operations to establish git context

**Usage patterns in codebase:**
- `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/cli.py` (lines 66-72): `focus_session()` calls `extract_task_blocks()` to find and filter single task for worktree
- `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/merge.py` (lines 58-100): `_resolve_session_md_conflict()` extracts task blocks from both sides of merge conflict to find new tasks from worktree

### 4. Jobs.md Parsing and Consumption

**Primary parsing module:** `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/validation/jobs.py`

**Key functions:**

1. **`parse_jobs_md(jobs_path)`** (lines 12-44)
   - Parses jobs.md Plans table into dict mapping plan name → status string
   - Finds "## Plans" section, reads table rows
   - Splits on pipe delimiter, extracts columns: `| plan-name | status | notes |`
   - Returns `dict[str, str]` keyed by plan name

2. **`get_plans_directories(plans_dir)`** (lines 47-79)
   - Scans plans/ directory for actual plan content
   - Includes both directories and .md files (except README.md)
   - Skips plans/claude/ (gitignored, ephemeral plan-mode files)
   - Returns `set[str]` of plan names

3. **`validate(root)`** (lines 82-118)
   - Consistency check: Plans in directory must match jobs.md entries
   - Plans in jobs.md (status != "complete") must exist in directory
   - Plans in directory (except "reports") must be listed in jobs.md
   - Returns list of error strings (empty if valid)

**Validation enforcement:**
- Integrated into precommit checks via validation/cli.py
- Called during `just precommit` (fails if inconsistency detected)
- Prevents drift between jobs.md table and actual plans/ directories

### 5. Handoff Skill: Session.md Update Protocol

**Location:** `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/skills/handoff/SKILL.md`

**Step 1: Gather Context** (lines 30-35)
- Review conversation to identify completed tasks
- Identify pending/remaining tasks
- Note blockers and gotchas
- Check for uncommitted prior handoff content in session.md
- If found, use incremental Edit strategy rather than full Write

**Step 2: Update session.md** (lines 37-56)
- Carry forward Pending Tasks and Worktree Tasks verbatim
- Mark completed tasks `[x]` (or remove per retention rules)
- Append new tasks discovered this session
- Update metadata only if changed this session
- For multiple handoffs before commit: Use Edit to merge into existing structure

**Step 4b: Check for Invalidated Learnings** (lines 170-176)
- Review learnings.md (loaded via CLAUDE.md @-reference)
- If any learning claims something now false (enforcement added, workflow changed), remove it
- Changes and learning cleanup must be atomic within same commit

**Step 6: Update jobs.md** (lines 229-241)
- When plan status changes: Move between sections
- Completed → Move to "Complete (Archived)" with one-liner summary
- Design created → Move from Requirements to Designed
- Runbook created → Move from Designed to Planned
- Format for Complete section: `- plan-name — brief description of what was delivered`

**Step 7: Trim Completed Tasks** (lines 243-268)
- Delete completed tasks ONLY if BOTH: (1) from previous conversation, (2) work committed
- Always keep: Pending Tasks, Blockers, Next Steps
- Extract learnings BEFORE deleting
- Do NOT delete tasks completed in current conversation
- Do NOT list tasks in "Previous Session" headers

**Step 8: Display STATUS** (lines 269-281)
- If `--commit` flag NOT specified: Display STATUS (showing Pending Tasks, first command)
- If `--commit` flag WAS specified: Skip display (will be shown after /commit)

### 6. Worktree Integration: Cross-Tree Session Management

**File:** `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/skills/worktree/SKILL.md`

**Worktree Task Format** (lines 26-28):
```markdown
## Worktree Tasks

- [ ] **Task Name** → `<slug>` — description | model
```
Arrow U+2192 (→) followed by backtick-quoted slug. Section preserved during handoff.

**Mode A: Single Task Creation** (lines 33-45)
1. Read agents/session.md to locate task in Pending Tasks
2. Invoke: `claudeutils _worktree new --task "<task name>"`
3. Command automatically moves task from Pending Tasks to Worktree Tasks with slug marker
4. No manual session.md editing required

**Mode B: Parallel Group Setup** (lines 47-81)
1. Read both session.md AND jobs.md to identify pending tasks and plan status
2. Analyze: plan directory independence, logical dependencies (from Blockers/Gotchas), model tier compatibility, restart flags
3. Select largest independent group
4. Invoke `claudeutils _worktree new --task` for each task sequentially
5. Output consolidated launch commands

**Mode C: Merge Ceremony** (lines 84-114)
1. Invoke `/handoff --commit` to ensure clean tree
2. Use Bash to invoke: `claudeutils _worktree merge <slug>` (three-phase merge)
3. Exit code 0: Success → Invoke `claudeutils _worktree rm <slug>` to cleanup (removes from Worktree Tasks if task completed in worktree)
4. Exit code 1: Conflicts/precommit failure → Manual resolution → Re-run merge (idempotent)
5. Exit code 2: Fatal error → Review stderr, resolve, retry

**Automation notes** (lines 116-126):
- Slug derivation is deterministic (task name → slug repeatable)
- Merge is idempotent (safe to retry)
- Session.md task movement automated (no manual editing)
- Parallel execution requires individual merge for each worktree

### 7. Session Structure Validation

**File:** `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/validation/session_structure.py`

**Validation checks:**

1. **`parse_sections(lines)`** (lines 17-37)
   - Parses session.md into named sections
   - Returns dict mapping section name → list of (line_number, line_text)

2. **`check_worktree_format(section_lines)`** (lines 59-78)
   - Verifies Worktree Tasks entries have → slug format
   - Checks for Unicode arrow (U+2192) in task line
   - Error: "worktree task missing → slug: **task-name**"

3. **`check_cross_section_uniqueness(pending_tasks, worktree_tasks)`** (lines 81-104)
   - Ensures no task appears in both Pending Tasks AND Worktree Tasks
   - Case-insensitive comparison
   - Error: "line N: task in both Pending (line M) and Worktree: **task-name**"

4. **`check_reference_files(section_lines, root)`** (lines 107-126)
   - Validates Reference Files section entries point to existing files
   - Matches pattern: `- \`filepath\``
   - Error: "line N: reference file not found: filepath"

**Validation enforcement:** Integrated into precommit via validation/cli.py

### 8. Session Context Recovery: Task-Context Tool

**File:** `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/bin/task-context.sh`

**Purpose:** Recover full session.md from git history where a specific task was introduced

**Usage:** `task-context.sh '<task-name>'`

**Implementation:**
1. Find oldest commit where task name's string count changed in agents/session.md
2. Uses: `git log --all -S "<task-name>" --format=%H -- agents/session.md | tail -1`
3. Output session.md content from that commit via `git show <commit>:agents/session.md`

**Rationale:** Task names serve as prose identifiers (unique across session.md, disjoint from learning keys). Enables reverse lookup: given a task, find the session.md where it was first introduced.

**Called by:** Execute-rule.md specifies "Task Pickup: Context Recovery" rule - before starting a pending task, run this script to recover session context where it was introduced.

### 9. Focused Session Creation for Worktrees

**File:** `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/bin/focus-session.py`

**Purpose:** Create minimal session.md focused on single task for worktree isolation

**Usage:** `focus-session.py '<task-name>' > tmp/focused-session.md`

**Steps:**
1. Extract task and related context from session.md
2. Find plan references from task text (formats: `plans/plan-name/` and `Plan: plan-name`)
3. Extract document summaries from plan directory (rca.md, requirements.md, design.md, etc.)
4. Build Context section with relevant excerpts
5. Output minimal session.md suitable for focused worktree work

**Implementation details:**

- `extract_task()` (lines 17-58): Finds task line + continuation lines, extracts plan references
- `extract_section()` (lines 61-87): Extracts markdown section (## header) content with line limit
- `extract_doc_summary()` (lines 90-154): Type-specific excerpts:
  - RCA: Executive Summary + Fix Tasks (10+15 lines)
  - Requirements: Requirements section (15 lines)
  - Design: Problem + Requirements sections (8+12 lines)
  - Problem: First 15 lines after title
  - Runbook: Overview/Summary section (10 lines)
- `create_focused_session()` (lines 157-200): Builds minimal session.md with task + context + available docs list

### 10. Session Merge During Worktree Conflicts

**File:** `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/merge.py` (lines 58-100)

**Function:** `_resolve_session_md_conflict(conflicts)`

**Strategy:** Keep ours (main branch), extract new tasks from theirs (worktree branch)

**Implementation:**
1. Read both sides of conflict via `git show :2:agents/session.md` (ours) and `:3:agents/session.md` (theirs)
2. Extract task blocks from both: `extract_task_blocks(content)`
3. Find new tasks: `[task for task in theirs if task.name not in ours_names]`
4. Find Pending Tasks section bounds in ours
5. Insert full task blocks at insertion point (sorted by name)
6. Add blank line separation before next section header if needed
7. Return resolved content

**Rationale:** Carries forward new tasks discovered in worktree while preserving main's session state. Non-destructive (both sides' tasks preserved).

### 11. Jobs.md Merge Conflict Resolution

**Test case:** `/Users/david/code/claudeutils-wt/design-workwoods/tests/test_worktree_merge_jobs_conflict.py`

**Pattern:** Worktree merges with jobs.md changes are auto-resolved with warnings

**Example scenario (lines 13-100):**
- Main: `| plan-a | planned |`
- Worktree: Changes to `| plan-a | complete |`
- Result: Auto-resolved (deterministic strategy), merge succeeds with warning about jobs.md change

**Implementation:** Not visible in provided excerpt but implied in merge ceremony. Uses deterministic conflict resolution strategies for session files.

### 12. Session.md in Mode-Based Execution

**File:** `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/fragments/execute-rule.md`

**Status Mode (MODE 1)** reads and displays session.md content:
- Reads `agents/session.md` Pending Tasks section
- Scans `agents/jobs.md` for status values
- Displays first pending task with command to start it
- Lists all pending tasks with metadata (model, restart flag)
- Shows Worktree Tasks section (if tasks in active worktrees)
- Shows Unscheduled Plans (in jobs.md but no associated pending task)
- Detects parallelizable groups (2+ independent tasks)

**Task metadata format in display:**
```
Next: <first pending task name>
  `<command to start it>`
  Model: <recommended model> | Restart: <yes/no>

Pending:
- <task 2 name> (<model if non-default>)
  - Plan: <plan-directory> | Status: <status> | Notes: <notes>
```

**Status source:** Authoritative from `agents/jobs.md` (not inferred from session.md)

### 13. Learning Consolidation Trigger from Handoff

**File:** `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/skills/handoff/SKILL.md` (lines 178-215)

**Step 4c: Consolidation Trigger Check**

Runs `agent-core/bin/learning-ages.py agents/learnings.md` to check if consolidation needed.

**Trigger conditions:**
- File exceeds 150 lines, OR
- 14+ active days since last consolidation

**If triggered:**
1. Filter entries with age ≥ 7 active days (batch ≥ 3 entries)
2. Delegate to remember-task agent with entry list
3. Read report; if escalations exist (contradictions, file limits):
   - Note contradictions in Blockers/Gotchas
   - Execute refactor flow for file-limit escalations (split file, run autofix, re-invoke remember-task)
4. Check for remaining escalations, stop if UNFIXABLE

**Learning-ages.py:** Calculates age in active days (last commit touching each learning)

## Patterns and Cross-Cutting Observations

### Pattern 1: Carry-Forward Data vs. Prose Generation

Session.md Pending Tasks use a strict carry-forward protocol: read existing tasks, apply minimal mutations (mark completed, append new), preserve all sub-items. This differs from typical handoff patterns that regenerate prose. The rationale: sub-items accumulate context from prior sessions that cannot be reconstructed from conversation history alone.

**Evidence:** handoff/SKILL.md lines 41-46: "Do NOT rewrite, compress, summarize, or de-duplicate existing task sub-items. Sub-items are accumulated context from prior sessions."

### Pattern 2: Cross-Tree State Verification

The codebase uses git cross-tree reads to verify state before mutations:
- `_task_is_in_pending_section()` reads worktree branch's session.md via `git show` to check task completion
- `remove_worktree_task()` checks worktree branch's Pending Tasks before removing from main
- Merge conflict resolution reads both sides via `:2:` and `:3:` git shows

This enables safe multi-branch coordination without requiring shared database.

### Pattern 3: Deterministic Task-to-Slug Mapping

Task names are prose identifiers that map deterministically to slugs:
- `derive_slug(task_name)` in worktree/cli.py (line 23-35): `re.sub(r"[^a-z0-9]+", "-", task_name.lower()).strip("-")`
- Same task name always produces same slug
- Enables consistent worktree reference across sessions

### Pattern 4: Structured Parsing Instead of Regex Search

Session.md parsing uses structured block extraction (TaskBlock dataclass) rather than ad-hoc regex searches:
- `extract_task_blocks()` returns list of TaskBlock(name, lines, section)
- Preserves full line list (enables lossless write-back)
- Tracks section membership (Pending vs. Worktree)
- Used consistently across worktree/session.py, worktree/merge.py, worktree/cli.py

### Pattern 5: Idempotent Multi-Phase Operations

Worktree merge is designed as idempotent three-phase operation:
- Phase 1: Submodule resolution
- Phase 2: Parent repo merge
- Phase 3: Precommit validation
- Can be safely re-run after manual fixes (resumes from current phase)
- Prevents double-merging or partial-state corruption

### Pattern 6: Validation Enforcement in Precommit

Both session.md and jobs.md have validation rules integrated into precommit:
- session_structure.py: Worktree format, cross-section uniqueness, reference file existence
- jobs.py: Plan directory consistency
- Called via `just precommit` (fails if violations found)
- Prevents drift at commit boundary rather than downstream

### Pattern 7: Multi-Handoff Merging Before Commit

The codebase supports multiple handoffs before a single commit:
- If session.md has uncommitted prior handoff content, current handoff merges incrementally (Edit strategy) rather than replacing (Write strategy)
- Preserves accumulated context across multiple session segments
- Enables continued work without commit between handoffs

**Evidence:** handoff/SKILL.md lines 48-54: "Do NOT Write a fresh session.md that discards the prior handoff's completed tasks, pending tasks, or blockers."

### Pattern 8: Focused Session for Worktree Isolation

Creating a worktree generates a filtered, minimal session.md:
- Single task + its context (related plan documents)
- Document excerpts (RCA, requirements, design) extracted and summarized
- Prevents context bloat, focuses worktree agent on isolated task
- Separate from main session.md (worktree has its own session)

## Missing Pieces and Gaps

### Gap 1: Jobs.md Status Updates Across Worktrees

Jobs.md is updated during handoff (step 6) when plan status changes, but the mechanism for detecting status change (how does handoff know design/runbook was created?) is not explicitly detailed. The update is manual based on agent observation during conversation, not automated detection.

**Evidence:** handoff/SKILL.md line 233-236 says "When plan status changes during this session" but does not specify how status change is detected.

### Gap 2: Parallel Workstation Awareness

While the codebase supports parallel worktrees, there's no explicit cross-worktree locking or ordering constraints. Mode B (parallel group) analyzes plan directory independence and logical dependencies, but the enforcement is implicit (agent detects via Blockers/Gotchas section). No explicit constraint file or ordering table exists.

**Evidence:** worktree/SKILL.md lines 51-63 describes analysis but no persistent constraint tracking.

### Gap 3: Session History Tracking

Session.md is ephemeral (volatile state, discarded after commit). Only the git log preserves session history. No automatic session archive or rollup mechanism exists to track how tasks evolved across multiple sessions.

**Evidence:** handoff/SKILL.md line 262 says "Claude Code injects recent git log at session start" but no automatic session timeline/archive.

### Gap 4: Jobs.md Reconciliation with Actual Runbook Status

Jobs.md status (requirements/designed/planned/complete) is updated manually during handoff. There's no automated detection of actual runbook state (e.g., if runbook files exist, status could be inferred as "planned"). Status tracking is trust-based on handoff.md updates.

**Evidence:** validation/jobs.py only validates directory consistency, not status correctness against actual design/runbook artifacts.

### Gap 5: Learnings Consolidation Scope

The handoff skill performs learnings consolidation trigger check but the actual consolidation logic (decision of which learnings to keep vs. move to permanent locations) is delegated to remember-task agent. The criteria for "ready for consolidation" are based on file age/size, but subject-matter criteria are opaque.

**Evidence:** handoff/SKILL.md lines 178-215 show trigger conditions but agent decision is deferred to remember-task.

## File Paths (Absolute)

### Core Session/Jobs Files
- `/Users/david/code/claudeutils-wt/design-workwoods/agents/session.md` — Current session state
- `/Users/david/code/claudeutils-wt/design-workwoods/agents/jobs.md` — Plan lifecycle tracking
- `/Users/david/code/claudeutils-wt/design-workwoods/agents/learnings.md` — Institutional knowledge

### Parsing/Validation Modules
- `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/session.py` — Session.md parsing utilities
- `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/validation/session_structure.py` — Session.md validation
- `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/validation/session_refs.py` — Tmp/ reference validation
- `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/validation/jobs.py` — Jobs.md validation

### Worktree Integration
- `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/cli.py` — Worktree CLI commands
- `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/merge.py` — Worktree merge operations

### Skills and Tools
- `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/skills/handoff/SKILL.md` — Handoff skill (session.md update protocol)
- `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/skills/worktree/SKILL.md` — Worktree skill (multi-mode task management)
- `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/bin/task-context.sh` — Task context recovery tool
- `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/bin/focus-session.py` — Focused session creation

### Supporting Documentation
- `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/skills/handoff/references/template.md` — Session.md template
- `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/fragments/execute-rule.md` — Mode-based execution (STATUS display)

### Tests
- `/Users/david/code/claudeutils-wt/design-workwoods/tests/test_worktree_merge_jobs_conflict.py` — Jobs.md merge conflict test
- `/Users/david/code/claudeutils-wt/design-workwoods/tests/test_validation_session_structure.py` — Session.md validation tests
- `/Users/david/code/claudeutils-wt/design-workwoods/tests/test_validation_jobs.py` — Jobs.md validation tests

## Implementation Notes for Workwoods Plan

**For cross-tree worktree awareness:**
- Session.md is already structured for worktree integration (Worktree Tasks section with slug markers)
- Use `extract_task_blocks()` from session.py for parsing multi-tree task state
- Extend `_task_is_in_pending_section()` pattern for cross-tree queries
- Merge conflict resolution already handles session.md (new task extraction)

**For vet tracking across trees:**
- Add vet status field to jobs.md Notes column (e.g., "Design.md complete, vet in progress")
- Extend session.md task metadata to track vet reports location (e.g., `Plan: workwoods | Vet: plans/workwoods/reports/design-vet.md`)
- Use structured validation to enforce vet completeness before status transitions

**For plan state inference:**
- Implement artifact detector: scan plans/<name>/ directory for design.md, runbook.md, etc.
- Map artifacts to implicit status: design.md exists → can transition to "designed", runbook.md exists → can transition to "planned"
- Use in jobs.md validator to warn if status contradicts actual artifacts

**For bidirectional merge:**
- Current merge strategy: keep ours (main), extract new tasks from theirs (worktree)
- For bidirectional: compare both sides' jobs.md status updates, apply both if non-conflicting
- Use deterministic rule for conflicts (e.g., later timestamp wins, or require explicit merge resolution)

