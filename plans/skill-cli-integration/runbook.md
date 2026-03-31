# Runbook: Skill-CLI Integration

**Tier:** 2 (Lightweight Delegation)
**Design:** `plans/skill-cli-integration/outline.md`
**Dependency order:** Phase 1 → Phase 2 → [RESTART] → Phase 3 + Phase 4 (parallel)

## Common Context

**Outline decisions:** D-1 (trigger convention `^Status\.$`), D-2 (commit composition boundary), D-3 (execute-rule simplification).

**Spike prototype:** `tmp/spike-stop-hook/status-hook.sh` — validated mechanism. Production changes: real CLI call, tightened regex, ANSI reset per line.

**Hook conventions:**
- Registration in `.claude/settings.json` under `hooks.Stop`
- Hook input: JSON on stdin with `last_assistant_message`, `stop_hook_active`
- Hook output: JSON with `systemMessage` (and optionally `additionalContext`)
- Existing Stop hook: `stop-health-fallback.sh` (bash, runs on sessions without SessionStart)

**Hook implementation: Python module** (not bash — bash test suites are ugly). Core logic is a pure function `process_hook(dict) -> dict | None`. Tests import and call directly. CLI entry point reads stdin/writes stdout in `if __name__ == "__main__"`. Self-contained (stdlib only: `json`, `re`, `subprocess`) — no claudeutils imports, runnable via `python3 path/to/module.py`.

---

### Phase 1: Hook core behavior (type: tdd)

**Artifact:** `src/claudeutils/hooks/stop_status_display.py`
**Test file:** `tests/test_stop_hook_status.py`
**Model:** sonnet

**Module structure:**
- `should_trigger(message: str) -> bool` — regex match `^Status\.$`
- `format_ansi(text: str) -> str` — prepend `\033[0m` reset to each line
- `get_status(cmd: tuple[str, ...] = ("claudeutils", "_status")) -> str` — run CLI, return output
- `process_hook(data: dict, status_fn: Callable[[], str] | None = None) -> dict | None` — orchestrate: guard → trigger → status → format → response
- `main()` — stdin JSON → `process_hook()` → stdout JSON

#### Cycle 1.1: Trigger detection + loop guard

**Bootstrap:** Create `src/claudeutils/hooks/__init__.py` (empty) and `src/claudeutils/hooks/stop_status_display.py` with stubs: `should_trigger` returns `False`, `process_hook` returns `None`. Do not commit.

---

**RED Phase:**

**Test:** `test_should_trigger` (parametrized)
**Assertions:**
- `should_trigger("Status.")` → `True`
- `should_trigger("Check the Status.")` → `False` (not start-of-line)
- `should_trigger("Status")` → `False` (no period)
- `should_trigger("Status.\nMore text")` → `False` (multiline)
- `should_trigger("")` → `False`

**Expected failure:** `AssertionError` — stub returns `False` for all inputs, first parametrized case expects `True`

**Verify RED:** `just green`

**Test:** `test_process_hook_loop_guard`
**Assertions:**
- `process_hook({"last_assistant_message": "Status.", "stop_hook_active": True})` → `None`
- `process_hook({"last_assistant_message": "Status.", "stop_hook_active": False}, status_fn=lambda: "mock")` → dict containing `"systemMessage"`

**Expected failure:** `AssertionError` — stub `process_hook` returns `None` for all inputs

**Verify RED:** `just green`

---

**GREEN Phase:**

**Implementation:** Trigger detection with regex and loop guard

**Behavior:**
- `should_trigger`: match message against `^Status\.$` using `re.fullmatch`
- `process_hook`: check `stop_hook_active` first (return None if true), then call `should_trigger` on `last_assistant_message`, on match call `status_fn` (or default `get_status`), return `{"systemMessage": result}`

**Changes:**
- File: `src/claudeutils/hooks/stop_status_display.py`
  Action: Implement `should_trigger` and `process_hook` core flow
  Location hint: Replace stubs

**Verify GREEN:** `just green`

---

#### Cycle 1.2: ANSI formatting + CLI integration

**Prerequisite:** Read `src/claudeutils/hooks/stop_status_display.py` — understand trigger detection from cycle 1.1

---

**RED Phase:**

**Test:** `test_format_ansi`
**Assertions:**
- `format_ansi("line1\nline2\nline3")` → each line starts with `\033[0m`
- `format_ansi("")` → starts with `\033[0m` (reset even for empty)
- First line prepended with extra leading `\033[0m\n` (escape dim "Stop says:" prefix)

**Test:** `test_process_hook_uses_status_fn`
**Assertions:**
- `process_hook(trigger_input, status_fn=lambda: "mock output")` → `systemMessage` contains `"mock output"` with ANSI resets
- Verifies injection works end-to-end

**Test:** `test_process_hook_status_failure`
**Assertions:**
- `process_hook(trigger_input, status_fn=raises_exception)` → `systemMessage` contains "Status unavailable" fallback (not None, not crash)
- Where `raises_exception` is `lambda: (_ for _ in ()).throw(RuntimeError("fail"))`

**Expected failure:** `AssertionError` — cycle 1.1 returns raw status output without ANSI formatting

**Verify RED:** `just green`

---

**GREEN Phase:**

**Implementation:** ANSI formatting and status provider integration

**Behavior:**
- `format_ansi`: prepend `\033[0m` to each line, add leading `\033[0m\n` for dim-escape
- `get_status`: run `subprocess.run(cmd, capture_output=True, text=True)`, return stdout, raise on failure
- `process_hook`: wrap status call in try/except, format output, package as systemMessage
- `main`: read stdin as JSON, call `process_hook`, print result as JSON if not None

**Changes:**
- File: `src/claudeutils/hooks/stop_status_display.py`
  Action: Implement `format_ansi`, `get_status`, `main`, wire formatting into `process_hook`
  Location hint: Add functions, update `process_hook` to call `format_ansi`

**Verify GREEN:** `just green`

---

### Phase 2: Hook registration (type: inline)

**Model:** sonnet

Register Python hook in `.claude/settings.json` alongside existing `stop-health-fallback.sh`.

**Edit:** `.claude/settings.json` — add second entry to `hooks.Stop[0].hooks` array:
```json
{
  "type": "command",
  "command": "python3 $CLAUDE_PROJECT_DIR/src/claudeutils/hooks/stop_status_display.py"
}
```

**Verify:** `just precommit` passes. `jq '.hooks.Stop' .claude/settings.json` shows both hooks.

**⚠️ RESTART BOUNDARY:** Hook config changes require session restart. Phases 3 and 4 execute in a new session.

---

### Phase 3: execute-rule.md simplification (type: inline)

**Model:** opus (agentic-prose)
**Blocked by:** Phase 2 + restart

**Edit:** `plugin/fragments/execute-rule.md` — MODE 1 section

**Remove:** The rendering template — everything between "**STATUS display format:**" and the end of MODE 1's rendering specification (~100 lines). Includes:
- STATUS display format code block
- In-tree list format
- Worktree section rendering rules
- Unscheduled Plans rendering rules
- Parallel task detection rendering
- "Status source" line referencing `claudeutils _worktree ls`

**Keep:**
- MODE 1 trigger definitions (what makes something MODE 1)
- "**Behavior:** Display pending tasks with metadata, then wait for instruction."
- Graceful degradation rules (missing session.md, old format, old section name)
- Planstate-derived commands table (agent needs this for `x`/`r` task pickup, independent of STATUS rendering)
- Session continuation rules
- Next task when in-tree blocked

**Add:** After "Behavior" line:
```
**Rendering:** Output `Status.` as final line — Stop hook renders via `_status` CLI.
```

**Update all STATUS references in other modes:**
- MODE 3 (EXECUTE+COMMIT): "display STATUS" → "output `Status.`"
- MODE 5 (WORKTREE SETUP): if it references STATUS display → same update
- Post-commit display in shortcuts table: reference updated MODE 1

**Verify:** `just precommit` passes. Grep for orphaned "Display STATUS per execute-rule.md MODE 1" in the same file.

---

### Phase 4: Commit skill composition (type: inline)

**Model:** opus (agentic-prose)
**Blocked by:** Phase 2 + restart
**Parallel with:** Phase 3

**Edit:** `plugin/skills/commit/SKILL.md`

**Composition boundary (from D-2):**

| Skill keeps | Moves to CLI |
|------------|-------------|
| Step 1 discovery (git diff, git status, artifact-prefix grep) | Step 4 staging (`git add`) |
| Step 1 vet classification (trivial/non-trivial/report check) | Validation gates (precommit/lint) |
| Step 1b submodule info gathering (what changed in submodule) | Submodule commit execution |
| Step 1c settings triage | — |
| Step 2 draft message | — |
| Step 3 gitmoji selection | — |

**Replace Step 4 (Stage, commit, verify)** with CLI composition step:

Build structured markdown input per CLI format:
- `## Files` — from git status (unstaged + staged files)
- `## Options` — from skill flags: `--test` → `just-lint`, `--lint` → `just-lint`, `--no-vet` or trivial classification → `no-vet`
- `## Submodule <path>` — if submodule changes detected, include submodule commit message (blockquote format)
- `## Message` — drafted message with gitmoji prefix

Pipe to CLI:
```
echo "$INPUT" | claudeutils _commit
```

On CLI exit 0: success. On exit 1: validation failure (surface CLI output). On exit 2: parse error (surface and fix input).

**Replace Post-Commit section:** Remove "Then display STATUS per execute-rule.md MODE 1." Replace with:
```
Output `Status.` — Stop hook renders.
```

**Remove:** Step 1b detailed submodule commit procedure (CWD rule, git -C patterns). CLI handles this. Skill only gathers submodule change info for the `## Submodule` input section.

**Verify:** `just precommit` passes. Read through skill flow end-to-end for coherence.
