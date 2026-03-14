# Brief: Learnings startup report

## 2026-03-14: Learnings diagnostics at session start

**Problem:** Learnings age/weight diagnostics removed from handoff CLI — not actionable mid-session. `/codify` is context-heavy, only actionable at session start when agent has fresh context budget.

**Desired behavior:** SessionStart hook checks learnings entry count, total age, and token weight. Surfaces warning before work begins if thresholds exceeded.

**Origin:** handoff-cli-tool /proof review — H-3 diagnostics simplified, learnings monitoring relocated.
