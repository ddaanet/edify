# Skill-Gated Session Edits

## Problem

Bare directives to worktree agents (`execute and apply fixes inline then handoff and commit`) bypass all workflow gates. The agent executes directly — no Skill tool invocation, no corrector dispatch, no baseline verification. When regressions occur, the agent's own judgment is the only gate, and it classified real failures as "pre-existing."

## Evidence: Two Regressions (2026-03-11)

### Regression 1: `test_continuation_registry.py` (3 failures)

- **Session:** `63af67bf` (main, interactive)
- **Trigger:** User said "jfdi" during requirements review — agent applied one-line fix to `get_cache_path` inline
- **Mechanism:** Changed `Path(tmp_dir)` → `Path(project_dir) / "tmp"`. Agent noticed tests would break, edited them. Ran scoped test (29 pass from single file). Full precommit at commit time showed `test_cli_tokens.py` failures — agent dismissed as "pre-existing"
- **Note:** Out-of-workflow (user-directed inline fix). Less concerning — user accepted risk with "jfdi"

### Regression 2: `test_cli_tokens.py` (2 failures)

- **Session:** `68963394` (ar-token-cache worktree)
- **Trigger:** User said `execute and apply fixes inline then handoff and commit`
- **Mechanism:** Agent ran deliverable review autonomously, found modularity issue, extracted `_count_tokens_for_content` from `count_tokens_for_file`. Did `replace_all` on mock targets across 3 test files. Ran scoped tests (29 pass — token cache tests only). The `replace_all` was syntactically correct but semantically wrong: API key validation tests mocked `count_tokens_for_file` not because they test counting, but to prevent SDK initialization. After rename, the mock still activates but the code path changed — API key validation no longer fires.
- **Full user interaction in session:** `ping`, then `execute and apply fixes inline then handoff and commit`. No Skill tool invoked. No `/inline`. No corrector dispatch.
- **At commit time:** `just precommit` caught the 2 failures. Agent said "pre-existing test failures unrelated to this session's changes" — false. The failures were introduced by `a49020ad` in that session.

## Causal Chain

```
bare directive → no Skill tool → no /inline lifecycle →
  no corrector dispatch → no baseline comparison →
    agent runs scoped tests (module-level green) →
      full suite failures at commit time →
        agent classifies as "pre-existing" (wrong) →
          regression committed
```

## Key Insight

The `/inline` skill exists precisely for this: corrector dispatch, baseline diff, full verification. But it's opt-in — agents don't invoke it unless the user does (or unless a continuation chain routes to it). A bare directive like "execute and apply fixes" reads as "do the work directly," and the agent complies.

## Design Question

Default session behavior should be read-only (research, discussion, status). Edits to production artifacts (source code, tests, config) should require skill invocation — either explicit (`/inline`, `/orchestrate`) or via continuation chain. The skill provides the gates; without it, the agent's own judgment is the only defense, and that judgment failed twice in one session.

## Platform Research (2026-03-13, plugin-migration session)

Grounded findings from Claude Code docs:

**Plugin `agent` key:** Plugin `settings.json` can set `"agent": "agent-name"` — activates that agent as the main thread with its system prompt, tool restrictions, and model. This is the only supported key in plugin settings.json.

**Agent tool restrictions are hard caps.** If the base agent denies Write, no skill can re-enable it. Skill `allowed-tools` only pre-approves tools for auto-permission — it doesn't unlock tools the agent denied.

**Transcript-based skill detection (feasible mechanism):** PreToolUse hooks receive `transcript_path` (conversation JSONL). A hook can:
1. Read transcript JSONL
2. Find most recent Skill tool_use entry (e.g., `skill: "design"`)
3. Check policy: design allows `Write(plans/*)`, commit allows `Write(.git/*)`
4. Compare `tool_input.file_path` against allowed patterns
5. Return allow/deny

**This bypasses the platform limitation.** Instead of skill-scoped tool escalation (which doesn't exist), the hook reads conversation state to check whether an appropriate skill was invoked in this session. Session-level unlock, not active-skill tracking — once `/design` is invoked, `Write(plans/*)` is unlocked for the remainder of the session. No skill start/end detection needed.

**Concerns:**
- Performance: JSONL parsing on every Write/Edit/Bash (transcript grows during session)
- Reliability: Determining "active skill" from transcript is heuristic — no explicit start/end markers
- Fragility: Depends on transcript JSONL format (internal, not public API)

**Per-skill policy examples:**
- `/design`, `/runbook` → `Write(plans/*)`, `Bash(just precommit:*)`
- `/commit` → `Bash(git:*)`, `Write(.git/*)`
- `/handoff` → `Write(agents/session.md)`, `Write(agents/learnings.md)`
- `/inline` → `Write(src/*)`, `Write(tests/*)`, `Bash(just:*)`
- No active skill → read-only (Read, Glob, Grep, Skill, Agent only)

## Scope Boundaries

- **In scope:** Behavioral rule defining when skill invocation is required vs when direct execution is acceptable. Hook or structural enforcement mechanism. PreToolUse hook with transcript-based skill detection and per-skill write policies.
- **Out of scope:** Fixing the two specific regressions (separate task). Changing how `/inline` or corrector works internally.
- **Tension:** "jfdi" and quick fixes are valuable — gating everything through `/inline` adds ceremony. The design must distinguish trivial edits (typo fix, config tweak) from refactors that change behavior.
