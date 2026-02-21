# Phase 4: Session Health Checks

**Type:** General | **Model:** haiku
**Target files:**
- `agent-core/bin/learning-ages.py` (modify — add `--summary` flag)
- `agent-core/hooks/sessionstart-health.sh` (new)
- `agent-core/hooks/stop-health-fallback.sh` (new)

## Prerequisites

- Read `agent-core/bin/learning-ages.py` full file — understand main() structure: `total_entries`, `entries_7plus`, `entries_with_ages`, `staleness_days` variables computed before report generation
- `--summary` flag should reuse existing computation variables, not duplicate logic
- Read `agent-core/hooks/sessionstart-health.sh` — verify does NOT exist yet
- Verify SessionStart hook input JSON format includes `session_id` field

## Key Decisions

- D-4: Dual delivery — SessionStart (primary) + Stop fallback (handles #10373 for new sessions)
- Flag file `$TMPDIR/health-{session_id}` coordinates both scripts
- D-1: Command hooks (type: command)
- D-2: Bash for both scripts (simple command orchestration)
- SessionStart output: systemMessage (user-visible health status, not agent context injection)
- Stop output: systemMessage (same format, only when firing as fallback)
- Three health checks: git dirty tree, learnings health, stale worktrees

## Completion Validation

Success criteria:
- `python3 agent-core/bin/learning-ages.py agents/learnings.md --summary` → single line output
- `agent-core/hooks/sessionstart-health.sh` exists, executable, passes validation
- `agent-core/hooks/stop-health-fallback.sh` exists, executable, passes validation
- Flag file coordination works: SessionStart writes flag → Stop sees flag → Stop skips
- `pytest tests/ -v` → all existing tests pass (no regression)

Depends on: Step 4.2 depends on Step 4.1 (--summary flag).
