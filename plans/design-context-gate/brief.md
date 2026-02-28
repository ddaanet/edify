# Design Context Gate

/design skill tail-call decision: invoke /inline in-session vs handoff+commit with /inline as next pending task, based on remaining context budget.

## Conclusions

- /design Phase B (outline sufficient) → check context, tail-call /inline if budget allows
- /design Phase C.5 (full design) → check context, tail-call /inline if budget allows
- Both gates currently tail-call /inline unconditionally — no context check

## Mechanism

Context measurement infrastructure exists in `statusline/context.py`:
- `calculate_context_tokens()` extracts consumed tokens from `current_usage` or transcript JSONL fallback
- `context_window_size` gives total capacity
- Free context = total - consumed

Transport to skill: UPS hook injects context percentage into conversation (same pattern as existing UPS hooks). Skill reads from conversation context. No new CLI needed.

## Open

- Threshold for tail-call vs handoff: operational parameter, needs empirical calibration (log context usage at /design exit points, measure distribution). No confabulated number.
- Whether hook injection should be always-on or gated (e.g., only after /design runs)
