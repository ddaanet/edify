# Read Tool Context Optimization — Test Protocol

## Hypothesis

When the same file is Read multiple times in a Claude Code conversation, the platform may optimize context by replacing older reads rather than accumulating them. If true, `/recall` can re-read freely without context growth concerns.

## Why This Matters

The `/recall` skill's cumulative design assumes reads accumulate. If the platform deduplicates:
- "Skip already-loaded files" logic is unnecessary — just re-read
- Broad mode (whole-file) after default mode (section-level) has no redundancy cost
- Token budget for recall is simpler to reason about

## Test Environment

- **Clean-slate session:** `just claude0` (or `claude --system-prompt ""`) — no CLAUDE.md, no fragments, minimal base context
- Use statusline after each step to observe context/token usage
- **Read multiple files per step** for ~10-15K token delta per measurement (single files produce ~2K delta, invisible against base context noise)

## Test Files

Use these 5 decision files (batch gives ~10-15K tokens total):

- `agents/decisions/testing.md`
- `agents/decisions/implementation-notes.md`
- `agents/decisions/operational-practices.md`
- `agents/decisions/orchestration-execution.md`
- `agents/decisions/workflow-core.md`

## Tests

### T1: Whole-file Read deduplication

1. Read all 5 files (whole file)
2. statusline — note context size
3. Read all 5 files again (identical)
4. statusline — note context size
5. Compare: doubled, or replaced?

### T2: Range Read accumulation

1. Read all 5 files lines 1-50
2. statusline — note context size
3. Read all 5 files lines 51-100
4. statusline — note context size
5. Compare: are both ranges in context, or does the second replace the first?

### T3: Range Read followed by whole-file Read

1. Read all 5 files lines 1-50
2. statusline — note context size
3. Read all 5 files (whole file)
4. statusline — note context size
5. Compare: does whole-file replace the range reads, or do both persist?

### T4: Whole-file Read followed by range Read

1. Read all 5 files (whole file)
2. statusline — note context size
3. Read all 5 files lines 1-50
4. statusline — note context size
5. Compare: does range read replace the whole-file reads (losing lines 51+)?

### T5: Multi-file interleaved re-read

Run after T1-T4, informed by their results.

1. Read files A, B, C (whole file)
2. statusline — note context size
3. Read files D, E (whole file)
4. statusline — note context size
5. Read file A again (whole file)
6. statusline — note context size
7. Compare: does re-reading A grow context (accumulates) or stay flat (replaces)? Do B, C persist alongside the re-read A?

## Expected Outcomes

| Result | Implication for /recall |
|--------|------------------------|
| No optimization (all reads accumulate) | "Skip already-loaded" logic is necessary, re-reads are wasteful |
| Whole-file deduplicates, ranges accumulate | Broad mode can re-read freely, section-level recall should track loads |
| Everything deduplicates | Re-read freely in all modes, remove tracking logic |
| Per-file replacement (T5: A replaced, B/C persist) | Platform tracks by file path — re-reading a file is free, different files accumulate |

## Protocol Notes

- Run each test in a **separate clean-slate session** (context from prior tests would confound measurements)
- Prompt the agent minimally between steps — just "read these files". Avoid conversation that adds context.
- Read statusline token count after each step (~1K granularity, real-time). Record before/after for each step.

## Context

- `/recall` skill: `plugin/skills/recall/SKILL.md`
- Recall pass design: `plans/recall-pass/outline.md`
- Discussion conclusions from design session: broad mode uses direct Read, section-level uses when-resolve.py
