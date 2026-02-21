# Hook Batch: Runbook Outline

**Design source:** `plans/hook-batch/outline.md`
**Detailed plan:** `plans/hook-batch/userpromptsubmit-plan.md`
**Created:** 2026-02-21

---

## Requirements Mapping

| FR | Requirement | Phase | Item |
|----|-------------|-------|------|
| FR-1 | Line-based shortcut matching | 1 | Cycle 1.1 |
| FR-2 | r expansion — graduated lookup | 1 | Cycle 1.2 |
| FR-3 | xc/hc message compression | 1 | Cycle 1.3 |
| FR-4 | Additive directive scanning (D-7) | 1 | Cycle 1.4 |
| FR-5 | p: dual output | 1 | Cycle 1.5 |
| FR-6 | b: brainstorm + q: question + learn: directives | 1 | Cycle 1.6 |
| FR-7 | Skill-editing guard pattern | 1 | Cycle 1.7 |
| FR-8 | CCG integration pattern | 1 | Cycle 1.8 |
| FR-9 | PreToolUse recipe-redirect hook | 2 | Cycles 2.1–2.3 |
| FR-10 | PostToolUse auto-format hook | 3 | Steps 3.1–3.2 |
| FR-11 | learning-ages.py --summary flag | 4 | Step 4.1 |
| FR-12 | SessionStart health script | 4 | Step 4.2 |
| FR-13 | Stop health fallback script | 4 | Step 4.3 |
| FR-14 | hooks.json config source of truth | 5 | Step 5.1 |
| FR-15 | sync-hooks-config.py merge helper | 5 | Step 5.2 |
| FR-16 | sync-to-parent hook integration | 5 | Step 5.3 |
| FR-17 | Restart verification | 5 | Step 5.4 |

---

## Phase Structure

### Phase 1: UserPromptSubmit improvements (type: tdd)

**Target file:** `agent-core/hooks/userpromptsubmit-shortcuts.py` (839 lines)
**Test file:** `tests/test_userpromptsubmit_shortcuts.py`
**Model:** sonnet
**Complexity:** High — behavioral logic changes to existing 839-line script; 8 independent features with shared test infrastructure

- **Cycle 1.1:** Line-based shortcut matching — scan prompt lines, trigger on own-line match
- **Cycle 1.2:** r expansion — update COMMANDS['r'] to describe graduated lookup
- **Cycle 1.3:** xc/hc compression — update COMMANDS['xc'] and COMMANDS['hc'] to compressed style
- **Cycle 1.4:** Additive directive scanning — refactor `scan_for_directive` → collect all directives (D-7)
- **Checkpoint:** After Cycle 1.4 — verify additive scanning works with existing d:/p: directives; regression-check Tier 1 shortcuts and Tier 3 continuation
- **Cycle 1.5:** p: dual output — split p:/pending: to match d: dual-output pattern
- **Cycle 1.6:** New directives — add b:/brainstorm:, q:/question:, learn: with dual output
- **Cycle 1.7:** Skill-editing guard — EDIT_SKILL_PATTERN + EDIT_SLASH_PATTERN, additionalContext injection
- **Cycle 1.8:** CCG integration — CCG_PATTERN, additionalContext injection

**Phase 1 state after completion:** `userpromptsubmit-shortcuts.py` ~980 lines; tests pass.

---

### Phase 2: PreToolUse recipe-redirect (type: tdd)

**Target file:** `agent-core/hooks/pretooluse-recipe-redirect.py` (new)
**Test file:** `tests/test_pretooluse_recipe_redirect.py` (new)
**Model:** sonnet
**Complexity:** Medium — new script with testable pattern-matching logic

**Prerequisite:** Read `agent-core/hooks/userpromptsubmit-shortcuts.py` main() for hook output format reference.

- **Cycle 2.1:** Script structure — parse stdin JSON, extract command, silent exit 0 on no match
- **Cycle 2.2:** ln redirect — match `ln` command, inject additionalContext redirecting to `just sync-to-parent`
- **Cycle 2.3:** git worktree and git merge redirects — match both patterns, inject appropriate redirects

**Phase 2 state after completion:** New `pretooluse-recipe-redirect.py`; 3 redirects tested; all existing tests pass.

---

### Phase 3: PostToolUse auto-format (type: general)

**Target file:** `agent-core/hooks/posttooluse-autoformat.sh` (new)
**Model:** haiku
**Complexity:** Low — new Bash script, external formatter integration

**Prerequisite:** Check `which ruff` and `which docformatter` to verify tool availability.

- **Step 3.1:** Create auto-format script — extract `file_path`, skip non-.py, run ruff + docformatter
- **Step 3.2:** Validate — manual test with a Python file, verify silent on success

**Phase 3 state after completion:** New `posttooluse-autoformat.sh`; ruff runs on .py Write/Edit completions.

---

### Phase 4: Session health checks (type: general)

**Target files:**
- `agent-core/bin/learning-ages.py` (modify — add --summary flag)
- `agent-core/hooks/sessionstart-health.sh` (new)
- `agent-core/hooks/stop-health-fallback.sh` (new)

**Model:** haiku
**Complexity:** Medium — 3 files, flag file coordination between SessionStart and Stop

- **Step 4.1:** learning-ages.py --summary — add flag for one-liner output; test: run with --summary, get single line
- **Step 4.2:** sessionstart-health.sh — 3 checks (git status, learning-ages --summary, worktree age), write flag file
- **Step 4.3:** stop-health-fallback.sh — check flag file, run checks if absent (handles #10373 for new sessions)

**Phase 4 state after completion:** `learning-ages.py` has --summary; 2 new health scripts; flag file coordination working.

---

### Phase 5: Hook infrastructure + integration (type: general)

**Target files:**
- `agent-core/hooks/hooks.json` (new — config source of truth)
- `agent-core/bin/sync-hooks-config.py` (new — merge helper)
- `agent-core/justfile` (modify — add hooks sync to sync-to-parent recipe)

**Model:** haiku (except Step 5.3 — sonnet for justfile edit with merge logic)
**Complexity:** Medium — config tooling + merge logic

**Prerequisite:** Read `.claude/settings.json` hooks section to understand existing hook registrations and merge targets.

- **Step 5.1:** Create hooks.json — all agent-core hook registrations (5 events)
- **Step 5.2:** Create sync-hooks-config.py — read hooks.json, merge into settings.json, preserve existing entries, dedup by command string
- **Step 5.3:** Update sync-to-parent — add `python3 agent-core/bin/sync-hooks-config.py` after symlink sync
- **Step 5.4:** Run and verify — `just sync-to-parent` (dangerouslyDisableSandbox), confirm settings.json has new hooks, note restart requirement

**Phase 5 state after completion:** hooks.json created; settings.json updated; sync-to-parent deploys hooks automatically.

---

## Key Decisions Reference

| Decision | Implementation Impact |
|----------|----------------------|
| D-1: Command hooks only | All scripts: `type: command`, no LLM cost |
| D-2: Python for UPS + recipe-redirect; Bash for others | Phase 1/2: Python. Phase 3/4: Bash |
| D-3: File-specific ruff, not `just format` | Step 3.1: `ruff check --fix-only --quiet <file>` + `ruff format --quiet <file>` |
| D-4: Dual delivery SessionStart + Stop fallback | Phase 4: flag file `$TMPDIR/health-{session_id}` coordinates the two |
| D-5: b: = brainstorm (diverge without converging) | Cycle 1.6: BRAINSTORM_EXPANSION is diverge-only, no rankings |
| D-6: PreToolUse is informative (exit 0, additionalContext only) | Phase 2: no blocking, no systemMessage |
| D-7: Additive section-scoped directives | Cycle 1.4: refactor from first-match-return to collect-all |
| D-8: hooks.json is config source of truth | Phase 5: sync-hooks-config.py merges, settings.json is output |

---

## Cycle/Step Detail

### Phase 1 Cycle Detail

**Cycle 1.1: Line-based shortcut matching**
- Target: `main()` at line 772, `if prompt in COMMANDS`
- Change: Replace with scan of prompt.split('\n') stripped lines; first line matching a COMMANDS key triggers
- For multi-line prompt with embedded shortcut: output additionalContext (same expansion); systemMessage only when prompt is single-line shortcut
- Verification: `call_hook("s")` unchanged. `call_hook("s\nsome text")` produces additionalContext with status expansion.

**Cycle 1.2: r expansion**
- Target: `COMMANDS` dict, `'r'` key (line ~52)
- Change: Replace expansion string with graduated lookup description:
  - Check conversation context for in-progress task → resume directly
  - If not visible, read session.md
  - If no in-progress in session.md, check git status for uncommitted work
  - Report only if genuinely nothing to resume
- Verification: `call_hook("r")` → additionalContext contains graduated lookup steps (not just "Error if no in-progress")

**Cycle 1.3: xc/hc message compression**
- Target: `COMMANDS` dict, `'xc'` and `'hc'` keys
- Change: Compress to bracket-style with continuation chain note
  - xc: `'[execute, commit] — execute task, then /handoff and /commit continuation chain'`
  - hc: `'[handoff, commit] — /handoff then /commit continuation chain'`
- Verification: `call_hook("xc")` → systemMessage is `'[execute, commit]...'`

**Cycle 1.4: Additive directive scanning**
- Target: `scan_for_directive()` function + `main()` Tier 2 block
- Change:
  - Rename `scan_for_directive` → `scan_for_directives` returning `List[Tuple[str, str]]`
  - Each directive is section-scoped: content from its line to next directive line or end of prompt
  - `main()` Tier 2 block collects all directives; no early return after first match
  - Build combined additionalContext from all directive expansions (newline-separated)
  - Build combined systemMessage from all directive concise messages
  - Falls through to Tier 2.5 and Tier 3 after collecting directives (pattern guards and continuation also fire)
- Depends on: Cycle 1.1 (main() Tier 1 structure must be stable before refactoring Tier 2)
- Verification: `call_hook("d: discuss this\np: new task")` → additionalContext contains both DISCUSS and PENDING expansions

**Cycle 1.5: p: dual output**
- Target: directive dispatch in `main()` (post-1.4 additive structure)
- Change: Add `p`/`pending` to the dual-output directive set (currently only `d`/`discuss`)
  - systemMessage: `'[PENDING] Capture task, do not execute.'`
  - additionalContext: full `_PENDING_EXPANSION`
- Depends on: Cycle 1.4 (additive directive structure in place)
- Verification: `call_hook("p: some task")` → systemMessage is `'[PENDING] Capture task, do not execute.'`; additionalContext is full expansion

**Cycle 1.6: New directives (b:, q:, learn:) with dual output**
- Target: constants section (add 3 expansion strings) + `DIRECTIVES` dict
- Change:
  - `_BRAINSTORM_EXPANSION`: diverge without converging; no evaluation/ranking; dual output
  - `_QUICK_EXPANSION`: terse response; no ceremony; dual output
  - `_LEARN_EXPANSION`: append to learnings.md; format guide; dual output
  - Add to DIRECTIVES: `'b': _BRAINSTORM_EXPANSION, 'brainstorm': _BRAINSTORM_EXPANSION, 'q': _QUICK_EXPANSION, 'question': _QUICK_EXPANSION, 'learn': _LEARN_EXPANSION`
- Depends on: Cycle 1.4 (additive structure handles new directives automatically), Cycle 1.5 (dual output pattern already established)
- Verification: `call_hook("b: ideas for this")` → systemMessage `'[BRAINSTORM]...'`; `call_hook("q: what is X")` → systemMessage `'[QUICK]...'`; `call_hook("learn: pattern about Y")` → systemMessage `'[LEARN]...'`

**Cycle 1.7: Skill-editing guard**
- Target: new constants + new detection block in `main()` as Tier 2.5 (after Tier 2, which now collects directives without returning — per Cycle 1.4)
- Change:
  - Add `EDIT_SKILL_PATTERN` (editing verbs + skill/agent noun)
  - Add `EDIT_SLASH_PATTERN` (editing verbs + /skill-name)
  - Detection: check full prompt against both patterns; if match, add to additionalContext collector
  - Injection: additionalContext only (no systemMessage — invisible to user)
  - Content: "Load /plugin-dev:skill-development before editing skill files. Load /plugin-dev:agent-development before editing agent files. Skill descriptions require 'This skill should be used when...' format."
  - Additive: collects alongside directive and continuation outputs
- Verification: `call_hook("fix the commit skill")` → additionalContext contains 'plugin-dev:skill-development'
- Verification: `call_hook("update /design description")` → additionalContext contains 'plugin-dev:skill-development'
- Regression: `call_hook("the skill is working well")` → no injection (no editing verb)

**Cycle 1.8: CCG integration**
- Target: new constant + new detection block in `main()` after Cycle 1.7 guard
- Change:
  - Add `CCG_PATTERN` matching platform keywords: hook, hooks, PreToolUse, PostToolUse, SessionStart, UserPromptSubmit, mcp server, slash command, settings.json, .claude/, plugin.json, keybinding, IDE integration, agent sdk
  - Detection: check full prompt; if match, add to additionalContext collector
  - Content: "Platform question detected. Use claude-code-guide agent (Task subagent_type='claude-code-guide') for authoritative Claude Code documentation."
  - Additive: combines with other guards
- Depends on: Cycle 1.7 (additionalContext collector pattern in place)
- Verification: `call_hook("how do hooks work")` → additionalContext contains 'claude-code-guide'
- Regression: `call_hook("fix the bug")` → no injection

---

### Phase 1 Checkpoint Detail

**Checkpoint after Cycle 1.4:**
- Run full test suite: all existing tests must pass
- Verify: `call_hook("d: discuss this\np: new task")` returns both expansions in additionalContext
- Verify: `call_hook("s")` still returns status expansion (Tier 1 regression)
- Verify: Tier 3 continuation parsing still works for non-shortcut, non-directive prompts

---

### Phase 2 Cycle Detail

**Cycle 2.1: Script structure and pass-through**
- Target: new file `agent-core/hooks/pretooluse-recipe-redirect.py`
- Change: Create script that reads stdin JSON, extracts `tool_input.command` (default ''), exits 0 silently on unknown command
- Output format: `{hookSpecificOutput: {hookEventName: "PreToolUse", additionalContext: "..."}}`
- Verification: `echo '{"tool_name":"Bash","tool_input":{"command":"echo hello"}}' | python3 pretooluse-recipe-redirect.py` → no output, exit 0

**Cycle 2.2: ln redirect**
- Target: `pretooluse-recipe-redirect.py` — add redirect pattern
- Change: If command starts with 'ln ' or equals 'ln', inject additionalContext: "`ln` is blocked. Use `just sync-to-parent` to create symlinks (encodes correct paths and ordering)."
- Verification: input `{"tool_input": {"command": "ln -sf agent-core/skills .claude/skills"}}` → additionalContext contains 'just sync-to-parent'

**Cycle 2.3: git worktree and git merge redirects**
- Target: `pretooluse-recipe-redirect.py` — add remaining redirect patterns
- Change:
  - `git worktree` → "Use `claudeutils _worktree` instead of `git worktree` (handles session.md, submodules, and branch management)"
  - `git merge` → "Use `claudeutils _worktree merge` instead of `git merge` (handles session resolution, submodule conflicts, and merge invariants)"
- Verification: `git worktree add` → additionalContext contains 'claudeutils _worktree'; `git merge main` → additionalContext contains 'claudeutils _worktree merge'
- Regression: `git status` → no output (not a redirect pattern)

---

### Phase 3 Step Detail

**Step 3.1: Create auto-format script**
- Target: new `agent-core/hooks/posttooluse-autoformat.sh`
- Read stdin JSON, extract `file_path` from `tool_input` using `python3 -c` or `jq` (no raw Bash JSON parsing per D-2 rationale)
- Skip if not `.py` file (extension check)
- Run: `ruff check --fix-only --quiet "$file"` then `ruff format --quiet "$file"`
- Run: `docformatter --in-place "$file"` if available (`which docformatter`)
- Silent on success; stderr on failure (non-fatal, exit 0 regardless)

**Step 3.2: Validate auto-format**
- Create or use a test Python file with formatting issues
- Pipe simulated PostToolUse JSON to script, verify file gets formatted
- Verify non-.py files are skipped (no output, exit 0)
- Verify missing ruff doesn't crash (graceful skip)

---

### Phase 4 Step Detail

**Step 4.1: learning-ages.py --summary flag**
- Target: `agent-core/bin/learning-ages.py` main() argument parsing
- Change: Detect `--summary` in sys.argv; if present, output one-liner and exit
  - One-liner format: `"{total_entries} entries ({entries_7plus} ≥7 days)"` optionally with consolidation staleness
  - Output uses variables already computed in main() — can be extracted before full report generation
- Validation: `python3 agent-core/bin/learning-ages.py agents/learnings.md --summary` → single line to stdout, exit 0

**Step 4.2: sessionstart-health.sh**
- Target: new `agent-core/hooks/sessionstart-health.sh`
- Change: Create script
  - Read session_id from stdin JSON (field: `session_id`)
  - Write flag: `$TMPDIR/health-${session_id}` on fire
  - Health check 1: `git status --porcelain` → if non-empty, warn about dirty tree
  - Health check 2: `python3 agent-core/bin/learning-ages.py agents/learnings.md --summary` → one-liner
  - Health check 3: `git worktree list` → check age of last commit per worktree (flag if >7 days)
  - Output: systemMessage with combined health status
- Note: script path uses `$CLAUDE_PROJECT_DIR` for portability

**Step 4.3: stop-health-fallback.sh**
- Target: new `agent-core/hooks/stop-health-fallback.sh`
- Change: Create script
  - Read session_id from stdin JSON
  - Check `$TMPDIR/health-${session_id}` — if present, exit 0 (SessionStart already fired)
  - If absent: run same 3 health checks + write flag
  - Handles #10373: new interactive sessions where SessionStart output is discarded
- Validation: Run manually with fake session_id; verify flag file logic works

---

### Phase 5 Step Detail

**Step 5.1: hooks.json**
- Target: new `agent-core/hooks/hooks.json`
- Structure mirrors settings.json `hooks` key
- Content:
  ```json
  {
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "python3 $CLAUDE_PROJECT_DIR/agent-core/hooks/userpromptsubmit-shortcuts.py", "timeout": 5}]}],
    "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "python3 $CLAUDE_PROJECT_DIR/agent-core/hooks/pretooluse-recipe-redirect.py"}]}],
    "PostToolUse": [{"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "bash $CLAUDE_PROJECT_DIR/agent-core/hooks/posttooluse-autoformat.sh"}]}],
    "SessionStart": [{"matcher": "*", "hooks": [{"type": "command", "command": "bash $CLAUDE_PROJECT_DIR/agent-core/hooks/sessionstart-health.sh"}]}],
    "Stop": [{"matcher": "*", "hooks": [{"type": "command", "command": "bash $CLAUDE_PROJECT_DIR/agent-core/hooks/stop-health-fallback.sh"}]}]
  }
  ```
- Note: Existing PreToolUse Write|Edit matchers (block-tmp, symlink-redirect) stay in .claude/settings.json only — not in hooks.json (project-local, not agent-core)

**Step 5.2: sync-hooks-config.py**
- Target: new `agent-core/bin/sync-hooks-config.py`
- Logic:
  1. Find settings.json: `$CLAUDE_PROJECT_DIR/.claude/settings.json` (or parent of agent-core)
  2. Read hooks.json from agent-core/hooks/
  3. For each event in hooks.json: merge into settings.json hooks section
     - Same-matcher merges: append new hook commands to existing matcher's hooks list
     - New matchers: add new matcher entry
     - Dedup: skip if command string already present (idempotent)
  4. Write settings.json (requires dangerouslyDisableSandbox — in denyWithinAllow)
- Usage: `python3 agent-core/bin/sync-hooks-config.py` (run from project root or via just recipe)

**Step 5.3: Update sync-to-parent**
- Target: `agent-core/justfile`, `sync-to-parent` recipe
- Change: Append after existing symlink sync steps:
  ```just
  echo "Syncing hook configuration..."
  python3 agent-core/bin/sync-hooks-config.py
  ```
- Note: justfile recipes run from project root (not script directory). sync-hooks-config.py writes settings.json; sandbox bypass required at invocation

**Step 5.4: Run sync-to-parent + verify**
- Run `just sync-to-parent` with dangerouslyDisableSandbox
- Check: `cat .claude/settings.json` — verify all 5 new hook entries present
- Verify existing hooks preserved (UserPromptSubmit entry, PreToolUse Write|Edit entries, PostToolUse Bash entry)
- Note restart required (hooks discovered at session start)

---

## Cross-Phase Dependencies

- Phase 2 (recipe-redirect) references hook output format from Phase 1 (userpromptsubmit) — investigation prerequisite at Cycle 2.1
- Phase 4 Step 4.2/4.3 depend on Phase 4 Step 4.1 (--summary flag used in health scripts)
- Phase 5 Step 5.1 registers all scripts from Phases 1-4 — all scripts must exist before sync
- Phase 5 Step 5.3 depends on Step 5.2 (sync-hooks-config.py must exist before recipe runs)

## Test Count Reference

- Phase 1: ~20 test cases in `test_userpromptsubmit_shortcuts.py` (existing + new)
- Phase 2: ~8 test cases in `test_pretooluse_recipe_redirect.py` (new)
- Phase 3-5: general steps, no pytest test files

## Scope Boundaries

**IN:** 8 UPS cycles (covering 9 feature items — b:, q:, learn: combined in Cycle 1.6), PreToolUse recipe-redirect, PostToolUse auto-format, SessionStart+Stop health, learning-ages --summary, hooks.json, sync-hooks-config.py, justfile update, restart verification

**OUT:** Sandbox denylist configuration (manual), upstream #10373 fix, AskUserQuestion removal (done)

---

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Consolidation candidates:**
- Cycles 1.2 (r expansion) and 1.3 (xc/hc compression) both modify COMMANDS dict string values with no branching logic. Consider merging into a single cycle during expansion. If kept separate, they can be expanded minimally (string replacement + verification).
- Phase 3 has only 2 steps, both Low complexity. If expansion adds no substance beyond what Step Detail already specifies, keep the phase compact rather than inflating.

**Cycle expansion:**
- Cycle 1.4 is the most complex cycle — the scan_for_directive → scan_for_directives refactor changes return type, iteration behavior, and main() control flow. RED tests should cover: single directive, multiple directives, mixed directive+non-directive lines, section scoping (content between directives).
- Cycle 1.6 adds 3 directives with 5 dict entries. RED should parametrize across all aliases rather than testing each individually.
- Phase 2 cycles: verify that Cycle 2.1 tests pass-through for *all* non-redirect commands, not just `echo hello`. Include `git status`, `python3 script.py` as non-redirect verification.

**Checkpoint guidance:**
- Phase 1 checkpoint after Cycle 1.4 is mandatory — validates the additive scanning refactor before building on it.
- Phase 5 Step 5.4 serves as integration checkpoint for the entire runbook.

**Growth projection:**
- `userpromptsubmit-shortcuts.py`: 839 lines → ~980 lines projected (17% growth). Well within limits; no split needed.
- Test file: 282 lines + ~20 new test cases → ~400 lines projected. Monitor during expansion; if approaching 400 lines, split test classes into separate files by tier.

**References to include:**
- Cycle 1.4: see `scan_for_directive()` at line 156 of userpromptsubmit-shortcuts.py for current implementation
- Cycle 1.1: see `main()` Tier 1 block at line 772 (`if prompt in COMMANDS`)
- Cycle 1.7/1.8: see `userpromptsubmit-plan.md` items 6-7 for pattern specs
- Phase 2: see `userpromptsubmit-plan.md` execution order for tier structure reference (note: D-7 supersedes its first-match-wins for Tier 2)
