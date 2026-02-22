## 2026-02-22: Precommit hook for python3/uv/ln blacklist enforcement

**Context:** Agent invoked `python3 agent-core/bin/when-resolve.py` — denied by blacklist. Script has shebang (`#!/usr/bin/env python3`) and is executable. Correct invocation: `agent-core/bin/when-resolve.py` directly. Agent silently worked around denial instead of diagnosing.

**Scope:** PreToolUse hook that intercepts Bash commands matching blacklisted invocation patterns and redirects to correct form.

**Redirect patterns:**

| Pattern | Redirect | Validation |
|---------|----------|------------|
| `python3 <path>` | `<path>` (direct script call) | File exists on disk, is executable, has shebang |
| `python3 -m pytest` | `pytest` (CLI equivalent) | Module has direct CLI |
| `python3 -c "..."` | Block outright | No redirect — use Write tool or existing CLI |
| `uv run <command>` | `<command>` (direct invocation) | .venv must be active; uv run is unnecessary in sandbox |
| `ln` / `ln -sf` | Block with message: "use `just sync-to-parent`" | Specific to symlink management in .claude/ |

**Design decisions from discussion:**

- `python3 -c` blacklisted outright: inline code execution is unreadable, untestable, usually a workaround for not knowing the right CLI tool. Agents have Read/Write/Edit tools for data manipulation.
- Each pattern needs different validation logic — not a simple text substitution. The hook is a routing table with per-pattern checks.
- `uv run` unnecessary when .venv is active (sandbox environment). Redirect to bare command.
- `ln` redirect specifically targets symlink management — `just sync-to-parent` encodes correct paths and ordering.

**Post-implementation:** Remove the inline "Script invocation" rule from CLAUDE.md — the hook mechanically enforces it via redirect. The rule is a stopgap until the hook lands.

**Model:** sonnet (small conditional routing, needs to be correct)
