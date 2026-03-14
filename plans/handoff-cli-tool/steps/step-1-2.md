# Step 1.2

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Extract git utilities and establish package structure. Foundation for all subcommands.

---

---

## Step 1.2: Create `claudeutils/session/` flat package structure

**Objective:** Create flat package with individual module files for all three commands. Register `_handoff`, `_commit`, `_status` as individual hidden commands in main CLI.

**Script Evaluation:** Small (~30 lines, mostly stubs)

**Execution Model:** Sonnet

**Prerequisite:** Read `src/claudeutils/cli.py:145-152` — understand existing `cli.add_command(worktree)` registration pattern to replicate for individual session commands.

**Implementation:**

Create flat directory structure (no subdirectories):
```
src/claudeutils/session/
  __init__.py           (empty)
  cli.py                Individual Click commands: _handoff, _commit, _status
  parse.py              (placeholder — session.md parser, Phase 2)
  handoff.py            (placeholder — handoff pipeline, Phase 4)
  commit.py             (placeholder — commit parser + pipeline, Phases 5-6)
  commit_gate.py        (placeholder — scripted vet check, Phase 5)
  status.py             (placeholder — STATUS rendering, Phase 3)
```

`session/cli.py`:
- Define individual Click commands (stubs for now): `handoff_cmd`, `commit_cmd`, `status_cmd`
- Each command is a `@click.command()` with `hidden=True` — not a group

Main `cli.py` registration:
- `from claudeutils.session.cli import handoff_cmd, commit_cmd, status_cmd`
- `cli.add_command(handoff_cmd, "_handoff")` — same `cli.add_command()` pattern as worktree
- `cli.add_command(commit_cmd, "_commit")`
- `cli.add_command(status_cmd, "_status")`
- Each command registered with `hidden=True` so it does not appear in `--help`

**Expected Outcome:** `claudeutils _handoff --help`, `claudeutils _commit --help`, `claudeutils _status --help` all work. `claudeutils --help` does NOT show them (hidden).

**Error Conditions:**
- Missing `__init__.py` → import failures

**Validation:** `claudeutils _handoff --help` succeeds; `just precommit` passes.

---
