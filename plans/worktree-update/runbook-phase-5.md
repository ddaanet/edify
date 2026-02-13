# Phase 5: Update `new` Command and Task Mode

**Complexity:** High (7 cycles)
**Files:**
- `src/claudeutils/worktree/cli.py`
- `tests/test_worktree_new.py`

**Description:** Refactor `new` command using extracted functions, add `--task` mode combining slug derivation and focused session generation.

**Dependencies:** Phases 1, 2, 4 (needs `wt_path()`, `add_sandbox_dir()`, `focus_session()`)

---

## Cycle 5.1: Refactor `new` to use `wt_path()` — sibling paths and branch reuse

**Objective:** Update `new` command to use `wt_path()` for sibling container paths and detect existing branches for reuse.

**Prerequisite:** Read `src/claudeutils/worktree/cli.py` — understand current `new` command implementation (uses `wt/<slug>` paths, creates branches unconditionally).

**RED Phase:**

**Test:** `test_new_command_sibling_paths`
**Assertions:**
- `claudeutils _worktree new test-wt` creates worktree at `<repo>-wt/test-wt` (not `wt/test-wt`)
- Worktree path is sibling to repo directory
- Container directory created if doesn't exist
- When branch "existing-branch" already exists: `new existing-branch` reuses branch without error (no `-b` flag passed to git)
- When branch doesn't exist: normal branch creation with `-b` flag

**Expected failure:** AssertionError: worktree created at old `wt/<slug>` location, or error when reusing existing branch

**Why it fails:** Command uses hardcoded `wt/` path, doesn't check for existing branches

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_command_sibling_paths -v`

---

**GREEN Phase:**

**Implementation:** Refactor `new` command to use `wt_path()` function and detect existing branches

**Behavior:**
- Replace hardcoded `wt/<slug>` path construction with `wt_path(slug, create_container=True)` call
- Before creating branch: check `git rev-parse --verify <slug>` exit code
- If branch exists (exit 0): use `git worktree add <path> <slug>` (no `-b` flag)
- If branch doesn't exist (exit 1): use existing logic with `-b` flag
- Path output at end uses actual sibling path from `wt_path()`

**Approach:** Replace path logic, add branch detection subprocess call, conditional git worktree add command

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Replace path construction in `new` command with `wt_path(slug, create_container=True)` call
  Location hint: Near start of `new` function, where path is determined
- File: `src/claudeutils/worktree/cli.py`
  Action: Add branch existence check using subprocess to run `git rev-parse --verify <slug>`
  Location hint: Before git worktree add command
- File: `src/claudeutils/worktree/cli.py`
  Action: Conditional git command based on branch existence
  Location hint: Replace unconditional branch creation with conditional logic

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_command_sibling_paths -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py -v`
- All existing `new` command tests still pass

---

## Cycle 5.2: Worktree-based submodule creation with branch reuse

**Objective:** Use `git -C agent-core worktree add` instead of `submodule update --init --reference` for shared object store. Handle both fresh branch creation and existing branch reuse.

**Prerequisite:** Read justfile `wt-new` recipe lines 150-180 — understand worktree-based submodule approach and object store verification.

**RED Phase:**

**Test:** `test_new_worktree_submodule`
**Assertions:**
- After `new <slug>`, `git -C agent-core worktree list` includes `<wt-path>/agent-core`
- Submodule worktree created at correct path (inside parent worktree)
- Submodule branch named same as parent worktree slug
- No `--reference` used (worktree shares object store inherently)
- Submodule is on correct branch (matches slug)
- Old `--reference` logic NOT present in code
- Given existing submodule branch "feature-x" in agent-core: `new feature-x` reuses both parent branch AND submodule branch
- No error from git attempting to create branch that already exists
- Submodule worktree points to existing branch (not new branch)
- Branch refs preserved (not recreated)

**Expected failure:** AssertionError: `--reference` still used, or submodule not created as worktree, or error when reusing existing branch

**Why it fails:** Command still uses old `submodule update --init --reference` approach, and branch reuse not implemented

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_worktree_submodule -v`

---

**GREEN Phase:**

**Implementation:** Replace submodule initialization with worktree-based approach, with branch detection for both fresh and existing branches

**Behavior:**
- Check if submodule branch exists: `git -C agent-core rev-parse --verify <slug>` (same pattern as 5.1)
- If submodule branch exists: `git -C agent-core worktree add <wt-path>/agent-core <slug>` (no `-b`)
- If submodule branch doesn't exist: `git -C agent-core worktree add <wt-path>/agent-core -b <slug>`
- Remove all `--reference` logic and `git checkout -B` step (worktree handles branch automatically)

**Approach:** Conditional pattern for submodule in agent-core directory, matching parent branch detection from 5.1. Reference justfile recipe for command structure.

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Replace `submodule update --init --reference` logic in `new` command
  Location hint: In submodule initialization section
- File: `src/claudeutils/worktree/cli.py`
  Action: Add submodule branch detection check
  Location hint: Before submodule worktree creation
- File: `src/claudeutils/worktree/cli.py`
  Action: Conditional submodule worktree add command (with or without `-b` flag)
  Location hint: Replace existing submodule initialization
- File: `src/claudeutils/worktree/cli.py`
  Action: Remove `checkout -B` step (no longer needed with worktree)
  Location hint: Delete old checkout logic

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_worktree_submodule -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py::test_new_command_sibling_paths -v`
- Cycle 5.1 test still passes

---

## Cycle 5.3: Sandbox registration — both main and worktree settings files

**Objective:** Register container directory in sandbox permissions for both main repo and worktree.

**RED Phase:**

**Test:** `test_new_sandbox_registration`
**Assertions:**
- After `new <slug>`, `.claude/settings.local.json` contains container path in `permissions.additionalDirectories`
- Worktree settings file `<wt-path>/.claude/settings.local.json` also contains container path
- Both files are valid JSON
- Container path is absolute (not relative)
- Deduplication works (running command twice doesn't add duplicate entries)

**Expected failure:** AssertionError: settings files don't exist or don't contain container path

**Why it fails:** Sandbox registration not yet called from `new` command

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_sandbox_registration -v`

---

**GREEN Phase:**

**Implementation:** Call `add_sandbox_dir()` function for both main and worktree settings

**Behavior:**
- Determine container path (absolute) from `wt_path()` result
- Call `add_sandbox_dir(container, ".claude/settings.local.json")` for main repo
- Call `add_sandbox_dir(container, f"{wt_path}/.claude/settings.local.json")` for worktree
- Function handles file creation, nested keys, deduplication (from Phase 2)

**Approach:** Two function calls at appropriate point in `new` command (after worktree creation)

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `add_sandbox_dir()` calls in `new` command
  Location hint: After worktree and submodule creation, before env init
- File: `src/claudeutils/worktree/cli.py`
  Action: Call for main settings: `add_sandbox_dir(container, ".claude/settings.local.json")`
  Location hint: Use container path from `wt_path()` result
- File: `src/claudeutils/worktree/cli.py`
  Action: Call for worktree settings: `add_sandbox_dir(container, f"{wt_path}/.claude/settings.local.json")`
  Location hint: After main settings call

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_sandbox_registration -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py -v`
- All previous Cycle 5 tests still pass

---

## Cycle 5.4: Environment initialization — `just setup` with warning on failure

**Objective:** Run `just setup` in worktree after creation, warn if unavailable (don't fall back to manual commands).

**RED Phase:**

**Test:** `test_new_environment_initialization`
**Assertions:**
- After `new <slug>`, `just setup` invoked with `cwd=<wt-path>`
- If `just` command available: `just setup` runs, exit code captured
- If `just` unavailable (command not found): warning printed, no error raised
- If `just setup` fails (exit ≠ 0): warning printed with stderr, no error raised (prerequisite failure, not fatal)
- No fallback commands executed (no `uv sync`, `direnv allow` called directly)

**Expected failure:** Error raised when `just` missing, or subprocess called without `cwd` parameter, or fallback commands attempted

**Why it fails:** Environment initialization not implemented, or incorrect error handling

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_environment_initialization -v`

---

**GREEN Phase:**

**Implementation:** Add environment initialization step with graceful failure handling

**Behavior:**
- Check if `just` available: `subprocess.run(['just', '--version'], ...)` with `check=False`
- If available: run `just setup` with `cwd=<wt-path>` and `check=False`
- Capture stderr and exit code
- If exit ≠ 0: print warning with stderr (don't raise exception)
- If `just` unavailable: print warning message (prerequisite missing)
- No fallback to manual commands (user must fix prerequisite)

**Approach:** Subprocess calls with error handling, conditional warnings, no exceptions raised

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add environment initialization in `new` command
  Location hint: After sandbox registration, before final output
- File: `src/claudeutils/worktree/cli.py`
  Action: Check for `just` availability
  Location hint: Use subprocess.run with check=False to test command existence
- File: `src/claudeutils/worktree/cli.py`
  Action: Run `just setup` with cwd parameter if available
  Location hint: subprocess.run with cwd=<wt-path>
- File: `src/claudeutils/worktree/cli.py`
  Action: Print warning messages for failures (don't raise exceptions)
  Location hint: Check exit codes, print to stderr or stdout as appropriate

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_environment_initialization -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py -v`
- All previous Cycle 5 tests still pass

---

## Cycle 5.5: Add `--task` option with `--session-md` default

**Objective:** Add `--task` flag to enable task-based worktree creation mode.

**RED Phase:**

**Test:** `test_new_task_option`
**Assertions:**
- `claudeutils _worktree new --task "Implement feature"` works (no positional slug required)
- `--session-md` option available with default value `agents/session.md`
- `--task` and positional slug are mutually exclusive (error if both provided)
- `--session` option ignored when `--task` provided (warning printed)
- Help text shows `--task` and `--session-md` options

**Expected failure:** click.UsageError: missing required argument slug, or no error when both slug and --task provided

**Why it fails:** `--task` option doesn't exist, slug still required

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_task_option -v`

---

**GREEN Phase:**

**Implementation:** Add Click options and mutual exclusivity validation

**Behavior:**
- Make slug argument optional: `@click.argument('slug', required=False)`
- Add `--task` option: `@click.option('--task', help="Task name from session.md")`
- Add `--session-md` option: `@click.option('--session-md', default='agents/session.md', help="Path to session.md")`
- At function start: validate exactly one of (slug, --task) provided (raise UsageError if both or neither)
- If `--task` and `--session` both provided: print warning, ignore `--session`

**Approach:** Click decorators for options, validation logic at function start

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Modify slug argument to be optional in `new` command
  Location hint: Change `@click.argument('slug')` to `@click.argument('slug', required=False)`
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `--task` option decorator
  Location hint: Before `def new(...)` function signature
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `--session-md` option decorator
  Location hint: After `--task` option
- File: `src/claudeutils/worktree/cli.py`
  Action: Add mutual exclusivity validation at function start
  Location hint: First lines of function, raise click.UsageError if invalid combination

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_task_option -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py -v`
- All previous explicit mode tests still pass

---

## Cycle 5.6: Task mode — slug derivation, focused session, tab-separated output

**Objective:** Implement task mode logic combining all helper functions and special output format.

**RED Phase:**

**Test:** `test_new_task_mode_integration`
**Assertions:**
- `claudeutils _worktree new --task "Implement feature X"` derives slug `"implement-feature-x"`
- Focused session generated from `agents/session.md` (calls `focus_session()`)
- Focused session written to temporary file for session creation
- Worktree created at derived slug path
- Output format: `<slug>\t<path>` (tab-separated, not just path)
- Temporary session file cleaned up after creation

**Expected failure:** AssertionError: wrong output format (no tab separator), or focused session not generated, or slug not derived

**Why it fails:** Task mode logic not implemented (slug derivation, focus_session call, output format)

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_task_mode_integration -v`

---

**GREEN Phase:**

**Implementation:** Wire task mode logic using helper functions from previous phases

**Behavior:**
- When `--task` provided:
  1. Derive slug: `slug = derive_slug(task_name)`
  2. Generate focused session: `session_content = focus_session(task_name, session_md_path)`
  3. Write to temp file: use `tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)`
  4. Proceed with normal `new` logic using derived slug and temp session path
  5. At end: print `f"{slug}\t{wt_path}"` (tab-separated) instead of just path
  6. Clean up temp file in finally block
- When explicit slug mode: output just path (existing behavior)

**Approach:** Conditional logic branch for task mode, compose helper functions, special output format

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add task mode branch in `new` command
  Location hint: Early in function, after validation
- File: `src/claudeutils/worktree/cli.py`
  Action: Call `derive_slug(task_name)` to get slug
  Location hint: In task mode branch
- File: `src/claudeutils/worktree/cli.py`
  Action: Call `focus_session(task_name, session_md_path)` to generate content
  Location hint: After slug derivation
- File: `src/claudeutils/worktree/cli.py`
  Action: Create temp file with focused session content
  Location hint: Use `tempfile` module, write content
- File: `src/claudeutils/worktree/cli.py`
  Action: Update output format — tab-separated for task mode, path-only for explicit mode
  Location hint: At end of function, conditional print based on mode
- File: `src/claudeutils/worktree/cli.py`
  Action: Add finally block to clean up temp file
  Location hint: Wrap main logic in try-finally

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_task_mode_integration -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py -v`
- All previous tests still pass (explicit mode unchanged)

---

## Cycle 5.7: Session file handling — warn and ignore `--session` when branch exists

**Objective:** Handle session file logic correctly when reusing existing branches (session already committed).

**RED Phase:**

**Test:** `test_new_session_handling_branch_reuse`
**Assertions:**
- When branch exists and `--session` provided: warning printed, `--session` ignored
- No attempt to commit session to existing branch (branch already has its session)
- When branch doesn't exist and `--session` provided: normal session commit flow
- Warning message mentions branch reuse as reason for ignoring `--session`

**Expected failure:** AssertionError: no warning printed, or session commit attempted on existing branch, or error raised

**Why it fails:** Session handling doesn't account for branch reuse scenario

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_session_handling_branch_reuse -v`

---

**GREEN Phase:**

**Implementation:** Add conditional session handling based on branch existence

**Behavior:**
- When branch exists (from 5.1 detection) AND `--session` provided:
  - Print warning: "Branch <slug> exists, ignoring --session (session already committed)"
  - Skip session commit logic
- When branch doesn't exist and `--session` provided:
  - Proceed with existing session commit flow (unchanged)
- When `--task` mode: session handling via temp file (from 5.6), branch reuse logic still applies

**Approach:** Conditional logic linking branch existence check from 5.1 to session commit decision

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add session handling conditional in `new` command
  Location hint: Where session commit logic exists
- File: `src/claudeutils/worktree/cli.py`
  Action: Check branch existence flag from earlier detection
  Location hint: Use same boolean/result from 5.1's branch check
- File: `src/claudeutils/worktree/cli.py`
  Action: Print warning and skip session commit if branch exists
  Location hint: Conditional around session commit code
- File: `src/claudeutils/worktree/cli.py`
  Action: Preserve existing session commit flow for new branches
  Location hint: Else branch of conditional

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_session_handling_branch_reuse -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py -v`
- All Phase 5 tests still pass

---

**Checkpoint: Post-Phase 5**

**Type:** Full checkpoint (Fix + Vet + Functional)

**Process:**
1. **Fix:** Run `just dev`. If failures, sonnet quiet-task diagnoses and fixes. Commit when passing.
2. **Vet:** Review all Phase 1-5 changes for quality, clarity, design alignment. Apply all fixes. Commit.
3. **Functional:** Review all implementations against design.
   - Check: Are path computations real or stubbed? Does branch detection actually work?
   - Check: Is task mode integration tested end-to-end or just mocked?
   - If stubs found: STOP, report which implementations need real behavior
   - If all functional: Proceed to Phase 6

**Rationale:** Phase 5 is major integration point — `new` command orchestrates all prior functions. Validate completeness before proceeding to `rm` and `merge` commands.
