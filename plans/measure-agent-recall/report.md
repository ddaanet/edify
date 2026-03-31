# Measurement: Spontaneous Agent Recall Rate

**Result: 0% spontaneous recall rate across 129 invocations in 69 sessions.**

## Method

Scanned all Claude Code session JSONL logs for the edify project (~265 session files) for Bash tool calls containing `when-resolve.py` or `_recall resolve`. Classified each invocation by examining preceding context (10 entries before each hit) to determine trigger source.

### Classification criteria

- **User-triggered:** Preceding user prompt contains `/when`, `/how`, `/recall`, or explicit recall instruction (e.g., "memory supercession pass")
- **Hook-injected:** Preceding system-reminder contains recall directive
- **Skill-procedural:** Invocation occurs within a skill execution (skill command or skill body in preceding context), orchestration phase, or discussion-mode grounding (pushback fragment mandates `_recall resolve` during `d:` evaluation)
- **Spontaneous:** None of the above — agent independently decided to look something up

### Pipeline

1. Session-scraper `search` identified 735 keyword hits across 69 sessions
2. Automated classifier (`tmp/classify-recall.py`) filtered to 141 actual Bash tool_use blocks and classified by preceding context
3. 37 items initially classified "spontaneous" were manually reviewed
4. 12 discarded as non-recall commands (tool testing, `--help`, worktree creation with matching branch name)
5. Remaining 25 reclassified: 11 discussion-grounding, 6 orchestration-phase, 5 user-triggered, 3 skill-procedural

## Results

| Category | Count | % |
|----------|-------|---|
| Skill-procedural | 113 | 87.6% |
| User-triggered | 16 | 12.4% |
| Hook-injected | 0 | 0.0% |
| Spontaneous | 0 | 0.0% |

**Total actual recall invocations:** 129 (across 69 sessions)

### Skill-procedural breakdown

The 113 skill-procedural invocations include:
- `/design` triage recall gate (mandatory recall before complexity classification)
- `/runbook` recall resolution steps
- Orchestration phase recall (runbook step instructions)
- Discussion-mode (`d:`) grounding (pushback fragment: "resolve topic-relevant recall entries")

### Discussion-grounding subcategory

11 invocations occurred during `d:` discussion mode. The pushback fragment explicitly mandates: "resolve topic-relevant recall entries: `edify _recall resolve 'when <topic>' ...`". These are procedural — the agent follows a documented instruction, not independent judgment.

## Interpretation

The 0% spontaneous rate confirms the recognition bottleneck diagnosis by direct measurement. Agents never independently decided to consult the recall system. Every invocation was either:
- Explicitly requested by the user (12.4%)
- Mandated by a skill procedure or fragment instruction (87.6%)

The original "actionable index" concept — entries loaded in context that would self-trigger agent recognition — did not produce spontaneous recall behavior. Agents had the recall tools available but never used them without procedural instruction or user prompting.

This is a stronger finding than the previously cited 4.1% statistic (which measured user-initiated `/when`/`/how` skill invocations, not agent recall). The 4.1% showed users rarely tested the tool; the 0% shows agents never spontaneously used it.

## Data

- Session scraper: `plans/prototypes/session-scraper.py`
- Classification script: `tmp/classify-recall.py`
- Reclassification script: `tmp/reclassify-spontaneous.py`
- Raw classification data: `tmp/recall-classification.json`
- Sessions scanned: 265 files, 69 containing recall-related tool calls
- Date range: 2026-02-13 to 2026-03-11
