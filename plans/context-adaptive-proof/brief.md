## Context-adaptive /proof — fork+summary when context heavy

### Origin

During /proof of outline-proofing design (session 83b685c4), the proof session hit the context limit at Item 3 of 7. The session had accumulated 150k tokens of discussion — design decisions, divergence analysis, grounding searches — leaving no room to finish the review. The accumulated decisions had to be captured as notes in lifecycle.md and deferred to a fresh session.

### Problem

/proof is inherently context-heavy: it loads the artifact, presents items sequentially, and each item can trigger discussion, grounding, and revision accumulation. For complex designs with rich discussion, the context window fills before the review completes.

The current workaround was manual: capture accumulated state in lifecycle.md, write "proof-suspended" status, start fresh session, scrape previous session log to recover context. This worked but was ad-hoc.

### Proposed mechanism

When /proof detects context pressure (approaching window limit mid-review):
1. **Fork:** Write accumulated decisions + remaining items to a proof-state file
2. **Summary:** Compress discussion context into key decisions and rationale
3. **Resume:** Fresh session reads proof-state file, resumes at next pending item with compressed context

### Key constraint (grounded)

Session logs contain dialogue only, not thinking tokens. A 150k-token context window might produce a 20-30k token session log. The session-scraper prototype (`plans/prototypes/session-scraper.py`) can extract and excerpt the dialogue, making recovery feasible without re-reading the full context.

### Design questions

- When does /proof detect "context heavy"? Token counting isn't available to the agent. Heuristic: item number + discussion turns per item?
- Should the fork happen automatically or require user signal?
- Is the proof-state file just an enriched lifecycle.md, or a separate artifact?
- Does session-scraper integration belong in /proof itself or as a separate recovery skill?
