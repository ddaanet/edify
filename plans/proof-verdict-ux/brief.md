## Simplify proof verdict UX

### Origin

During /proof of outline-proofing design (session c8972892, 2026-03-20). User found a/r/k/s verdict vocabulary confusing: approving the agent's revision suggestion should trigger the revision, but the explicit verdict system treats "approve" and "revise" as separate actions.

### Problem

The agent presents an item and often includes analysis ("this needs X"). When the user agrees with the analysis, the natural response is approval — but the verdict system expects "revise" because the item content would change. The distinction between "approve the agent's suggestion" and "revise the item" is artificial in conversational context.

### Direction

Remove explicit a/r/k/s verdict menu. Natural language already carries the verdict:
- "y" / agreement with agent's suggestion = approve (or approve+revise if agent suggested changes)
- Specific feedback = revise
- "kill" / "remove" = kill
- "skip" / "later" = skip

The conversational medium handles verdict detection without explicit mechanism.
