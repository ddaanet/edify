# Read Tool Context Optimization — Results

**Date:** 2026-02-24
**Protocol:** `plans/reports/recall-context-optimization-test.md`

## T1: Whole-file Read Deduplication

**Result: No deduplication. Reads accumulate.**

| Step | Context (k) | Delta |
|------|-------------|-------|
| Baseline (session start, CLAUDE.md loaded) | 37 | — |
| Read 5 decision files (whole) | 62 | +25 |
| Read same 5 files again (identical) | 87 | +25 |

Delta is identical — second read added the same ~25k as the first. No replacement, no dedup.

## T2–T5: Not Executed

T1 result is decisive: the platform performs no application-level deduplication of Read tool output. Each Read appends a new content block to the conversation regardless of prior reads of the same file. T2–T5 would provide granularity (range behavior, interleaving patterns) but the core question is answered.

## Conclusion

**No optimization exists.** Every Read call accumulates in context. This confirms the existing decision in `agents/decisions/implementation-notes.md` ("When Prompt Caching Differs From File Caching"):

> Each Read appends new content block to conversation. "Caching" = prompt prefix matching at API level (92% reuse, 10% cost). No application-level dedup.

## Implications for /recall

| Design element | Status | Rationale |
|---|---|---|
| Skip already-loaded tracking | **Necessary** | Re-reads cost ~5k/file, not free |
| Broad mode skip logic | **Necessary** | Whole-file re-reads are expensive |
| Tail-recursive saturation exit | **Necessary** | Without it, re-scanning would re-load |
| "Redundant context is cheap" claim | **Corrected** | Was in SKILL.md line 101; updated to remove false cheapness claim |

**Cost model:** 5 decision files = ~25k tokens. Full corpus (~8 files) would be ~40k. In a 200k context window, a single `/recall broad` pass consumes ~12-20% of available context. Re-reads double that cost with zero information gain.
