# Brief: Decision Drift Audit

## Problem

Decision files (`agents/decisions/*.md`) may contain content that has evolved beyond its original evidence base — stale tooling references, assumptions about capabilities that changed, superseded state. 22 decision files exist. No systematic audit has been performed.

Clean decision files are a prerequisite for system-property-tracing (which needs to know what properties the system claims to defend).

## Scope

Two sequential phases:

### Phase 1: Automated consistency scan

Check decision files against code for internal consistency:
- Stale file/path references (referenced files that no longer exist)
- Changed APIs (decisions referencing functions/commands that changed signature)
- Removed capabilities (decisions about features that were removed or superseded)
- Programmatic threshold grounding (which constants are calibrated from usage vs invented — absorbed from markdown-migration)

Mechanical verification. Automatable.

### Phase 2: Human proof review

Review automated findings plus judgment calls automation can't make:
- Undocumented convention drift (practice moved to Y, nothing says Y anywhere)
- Rationale currency (decision says "we use X because Y is too slow" — is Y still slow?)
- Evidence base validity (does the original justification still hold?)

## Origin

Split from quality-grounding SP-2 during /proof review (2026-03-12). Independent sub-problem — no dependency on quality-grounding's other sub-problems.

## Dependencies

- **system-property-tracing (downstream):** Clean decision files feed property inventory
- **quality-grounding SP-1 (none):** Independent — can run in parallel

## Success Criteria

- All 22 decision files scanned for internal consistency (Phase 1)
- Stale/drifted claims flagged and either updated or marked "ungrounded — needs validation"
- Human-reviewed findings validated (Phase 2)
- Programmatic thresholds assessed for grounding (absorbed from markdown-migration)

## References

- `agents/decisions/*.md` — 22 decision files
- `plans/quality-grounding/brief.md` — parent plan (SP-2 extracted)
- `plans/system-property-tracing/brief.md` — downstream consumer
