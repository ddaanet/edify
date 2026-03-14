# Brief: Resolve CLI learning references

## 2026-03-14: Recall resolve must process learning keys

**Problem:** System invariants documented as learnings need to be referenceable from recall artifacts. Current `claudeutils _recall resolve` only processes decision file entries (`agents/decisions/`). Learning keys (e.g., `when invariant: worktree cap`) are unresolvable.

**Blocker for:** Invariant documentation workflow — invariants live in learnings until system-property-tracing plan provides a proper home. Recall artifacts can reference them but resolve fails.

**Scope:** Extend `_recall resolve` to search `agents/learnings.md` in addition to decision files.
