## 2026-03-23: _worktree ls output is a context hog

`edify _worktree ls` dumps every plan across every tree. In a project with 60+ plans and 4 worktrees, the output consumed ~6K tokens in a single handoff call. The /handoff skill calls it for command derivation — it only needs plan statuses for tasks referenced in session.md, not every plan in every tree.

Options:
- Filter flag: `_worktree ls --plans foo,bar` — return only named plans
- Task-scoped mode: `_worktree ls --session agents/session.md` — auto-filter to session.md plan directories
- Porcelain already exists (`--porcelain`) but still lists everything
