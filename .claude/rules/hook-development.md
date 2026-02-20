---
paths:
  - ".claude/hooks/**/*"
  - ".claude/hooks.json"
---

# Hook Development Context

**Before editing hook files, load the hook development guide:**

```
/plugin-dev:hook-development
```

This provides hook event types, prompt-based hooks API, validation patterns, and integration with ${CLAUDE_PLUGIN_ROOT}.

**Configuration reference:** Read `agent-core/fragments/claude-config-layout.md` for hook configuration locations, output formats, activation requirements, and security patterns.

### Hook Error Protocol (D-6)

Hook failures are visible but non-fatal for the session:

| Failure Mode | Behavior | Rationale |
|-------------|----------|-----------|
| Hook crash (non-zero exit) | stderr visible, session continues | Degraded mode preferable to session abort |
| Hook timeout | Session proceeds without hook output | Hook is advisory, not blocking |
| Invalid output (malformed JSON) | Fallback to no-hook behavior | Partial output is worse than no output |

Hook errors should be logged (stderr visible) for diagnostics, but must not abort the session or skill chain.
