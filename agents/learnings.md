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
## RED pass blast radius assessment
- Anti-pattern: Handling unexpected RED pass as isolated cycle issue (skip or retry)
- Correct pattern: Run blast radius across all remaining phase cycles — test each RED assertion against current state
- Classification: over-implementation (commit test, skip GREEN), test flaw (rewrite assertions), correct (proceed)
- Critical finding: Test flaws are deliverable defects — feature silently skipped when test passes for wrong reason
- Protocol: `plans/orchestrate-evolution/reports/red-pass-blast-radius.md`
## Common context signal competition
- Anti-pattern: Phase-specific file paths and function names in global common context section of agent definition
- Correct pattern: Common context must be phase-neutral (project conventions, package structure). Phase-specific paths belong in cycle step files only
- Rationale: Persistent common context is stronger signal than one-time step file input. At haiku capability, persistent signal wins when step file task is semantically ambiguous
- Evidence: 1/42 cycles derailed (3.5), caused by fuzzy.py paths in common context competing with resolver.py in step file
## Vacuous assertion from skipped RED
- Anti-pattern: Committing a test that never went RED without evaluating assertion strength
- Correct pattern: When RED passes unexpectedly, verify assertions would catch the defect class — not just "doesn't crash" but "produces correct results"
- Example: `assert isinstance(relevant, list)` passes on empty list — pipeline silently returns no matches but test passes
- Detection: Check if key assertions distinguish "correct output" from "empty/default output"
## Index exact keys not fuzzy
- Anti-pattern: Using fuzzy matching in validator to bridge compressed triggers to verbose headings
- Correct pattern: Index entry key must exactly match heading key — fuzzy matching is only for resolver runtime recovery
- Rationale: Exact keys are deterministic and debuggable; fuzzy in validation creates invisible mismatches when scores drift below threshold
## DP zero-ambiguity in subsequence matching
- Anti-pattern: Initializing DP matrix with 0.0 for all cells — impossible states (i>0, j=0) indistinguishable from base case (i=0)
- Correct pattern: Initialize score[i>0][j] with -inf, only score[0][j] = 0.0. Impossible subsequences propagate -inf
- Rationale: When score[i-1][j-1] = 0 (no valid match for i-1 chars), transition score[i-1][j-1] + MATCH_SCORE produces positive score from nothing
- Evidence: "when mock tests" scored 128.0 against candidate with no 'o' or 'k' — matched only 5 of 15 chars
