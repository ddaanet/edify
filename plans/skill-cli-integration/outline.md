# Outline: Skill-CLI Integration

## Design Decisions

### D-1: STATUS rendering via Stop hook + trigger convention

**Mechanism:** Agent outputs `Status.` as final line → Stop hook detects `^Status\.$` → hook runs `claudeutils _status` → returns ANSI-colored `systemMessage` → user sees rich output bypassing dim styling.

**Agent contribution:** Emit trigger string. No rendering, no Bash call to `_status`.

**Hook contract:**
- Trigger regex: `^Status\.$` (full line match, prevents false positives)
- Runs `claudeutils _status` on match
- Returns `systemMessage` with ANSI reset (`\033[0m`) at start of each line
- `additionalContext` tells agent status was displayed (prevents re-render)
- Infinite loop guard via `stop_hook_active` check

**Source:** Spike validated (`plans/stop-hook-status-spike/brief.md`). Prototype: `tmp/spike-stop-hook/status-hook.sh`.

### D-2: /commit skill composition boundary

| Skill owns | CLI owns (`_commit`) |
|-----------|---------------------|
| Branch-diff discovery for vet classification | File staging (`git add`) |
| Message drafting (from discovery or `--context`) | Validation gates (precommit, lint) |
| Gitmoji selection | Submodule handling (stage + commit + pointer) |
| Settings triage (local.json cleanup) | Parent commit |
| Context-mode logic | Input validation (clean files, missing sections) |
| Vet checkpoint classification (trivial/non-trivial/report) | Vet check execution (pattern match + mtime) |

**Composition:** Skill builds structured markdown input → pipes to `claudeutils _commit` via Bash stdin → outputs `Status.` trigger on success.

**CLI input format (from `commit.py` parser):**
```
## Files
- path/to/file1.py
- path/to/file2.md

## Options
- no-vet
- just-lint

## Submodule plugin
> Submodule commit message

## Message
Parent commit message with gitmoji prefix
```

### D-3: execute-rule.md MODE 1 simplification

**Remove:** Rendering template (~100 lines of format specification, section-by-section rules).

**Keep:** Behavioral specification — when MODE 1 triggers, shortcut vocabulary, mode definitions, graceful degradation for missing session.md.

**Replace with:** "Run: output `Status.` — Stop hook renders via `_status` CLI."

**Graceful degradation:** Moves from fragment prose to `_status` CLI implementation (exit code 2 on missing session.md already handled).

### D-4: SP-3 deferred

`_handoff` CLI handles status line overwrite + completed section write (with mode detection). Skill manages 4+ additional sections (tasks, blockers, references, next steps). Partial composition adds split-write complexity for minimal gain. Incremental accumulation model evaluated and rejected (batch synthesis wins on consistency, crash recovery, and judgment quality).

## Dependency Order

```
SP-H (Stop hook)
  ↓ requires restart
SP-1 (execute-rule.md) ─┐
SP-2 (/commit skill)  ──┘ parallel after restart
```

SP-H must ship first — trigger string is meaningless without the hook. SP-1 and SP-2 are independent after hook is installed.

## Sub-Problem Routing

| SP | Artifact destination | Route |
|----|---------------------|-------|
| SP-H | production (hook script + settings.json) | `/runbook` — behavioral code (bash conditionals), Moderate minimum |
| SP-1 | agentic-prose (fragment) | `/inline` — prose edit, scope well-defined. Blocked by SP-H. |
| SP-2 | agentic-prose (skill) | `/inline` — prose edit, composition boundary defined. Blocked by SP-H. |

## Files Affected

**SP-H:**
- NEW: `src/claudeutils/hooks/__init__.py`, `src/claudeutils/hooks/stop_status_display.py`
- NEW: `tests/test_stop_hook_status.py`
- EDIT: `.claude/settings.json` (register Stop hook)

**SP-1:**
- EDIT: `plugin/fragments/execute-rule.md` (MODE 1 section)

**SP-2:**
- EDIT: `plugin/skills/commit/SKILL.md` (execution steps)
