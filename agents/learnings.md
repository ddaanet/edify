# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---
## Tool batching unsolved
- Documentation (tool-batching.md fragment) doesn't reliably change behavior
- Direct interactive guidance is often ignored
- Hookify rules add per-tool-call context bloat (session bloat)
- Cost-benefit unclear: planning tokens for batching may exceed cached re-read savings
- Pending exploration: contextual block with contract (batch-level hook rules)

## Vet introduces path bugs
- Anti-pattern: `_find_git_root()` traversing parents of relative `Path("agents")` — loop exits at `Path(".")` without checking it
- Correct pattern: Always `.resolve()` paths before parent traversal in `_find_git_root()` and similar functions
- Rationale: `Path(".").parent == Path(".")` terminates the while loop before checking cwd for `.git`
