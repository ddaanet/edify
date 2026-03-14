# Step 1.3

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Extract git utilities and establish package structure. Foundation for all subcommands.

---

---

## Step 1.3: Add `claudeutils _git changes` command

**Objective:** Unified parent + submodule view returning BOTH status AND diff in one call. Consumers: commit skill (input for `## Files` and `## Submodule`), handoff CLI (H-3 diagnostics).

**Script Evaluation:** Medium (~80 lines new code + tests)

**Execution Model:** Sonnet

**Prerequisite:** Read `src/claudeutils/git.py` (Step 1.1 output) — uses `_git()` and `discover_submodules()`

**Implementation:**

Create `src/claudeutils/git_cli.py` (CLI commands for the `_git` group):
- `@click.group(name="_git", hidden=True)` group
- `@git_group.command(name="changes")` — runs `git status --porcelain` AND `git diff` for parent, then for each discovered submodule. Output is a data transformation — paths are rewritten, not raw git passthrough. If tree is clean, output says so. If dirty, output includes both the file list AND the diff. Output format:

**Path prefixing:** Submodule file paths must be prefixed with submodule directory. `git -C agent-core status --porcelain` outputs relative paths — prefix each with `agent-core/`. This is a data transformation, not git passthrough.

**Clean sections omitted:** Only dirty repos shown in output. Token economy — only report deviations.

**Blank line separation:** Within a section, status and diff are separated by a blank line.

```markdown
## Parent
<git status --porcelain output>

<git diff output>
```

**Whole-tree clean:**
```markdown
Tree is clean.
```

When submodules present and dirty:
```markdown
## Parent
<status + diff>

## Submodule: agent-core
<status + diff (paths prefixed with agent-core/)>
```

Register in main `cli.py`: `from claudeutils.git_cli import git_group` + `cli.add_command(git_group)`

Internal Python functions (`git_status()`, `git_diff()` in `git.py`) serve commit CLI validation (C-2/C-3) separately from the unified CLI command.

**Tests:** `tests/test_git_cli.py`
- Tests use `tmp_path` to create real git repos with submodules
- `test_git_changes_clean_repo`: CliRunner invokes `_git changes`, output contains "clean"
- `test_git_changes_dirty_repo`: Create dirty file, output contains filename and diff under `## Parent`
- `test_git_changes_with_submodule`: Create repo with dirty submodule, output contains `## Submodule:` section with status and diff. Must verify submodule file paths include the submodule prefix (e.g., `agent-core/fragments/foo.md` not `fragments/foo.md`)
- `test_git_changes_clean_submodule_omitted`: Parent dirty + submodule clean → only parent section shown, no submodule section present in output

**Expected Outcome:** `claudeutils _git changes` produces structured markdown output with both status and diff. Exit 0 always (informational).

**Error Conditions:**
- Not in a git repo → `_git()` raises CalledProcessError. Let it propagate (informational command).

**Validation:** `just precommit` — all tests pass.

---

**Phase 1 Checkpoint:** `just precommit` — all existing tests pass, new infrastructure tests pass.
