# SP-2 Prose Rewrite: claudeutils → edify

## Summary

Rewritten all `claudeutils` references in agentic prose and documentation to `edify`.

## Files Modified

| File | Occurrences |
|------|-------------|
| agents/session.md | 5 |
| agents/learnings.md | 2 |
| agents/plan-archive.md | 1 |
| agents/ROADMAP.md | 1 |
| agents/SYSPROMPT_GENERATION_GUIDE.md | 8 |
| agents/role-code.md | 0 |
| agents/decisions/cli.md | 5 |
| agents/decisions/data-processing.md | 5 |
| agents/decisions/defense-in-depth.md | 1 |
| agents/decisions/implementation-notes.md | 5 |
| agents/decisions/markdown-tooling.md | 5 |
| agents/decisions/operational-tooling.md | 0 |
| agents/decisions/orchestration-execution.md | 0 |
| agents/decisions/pipeline-review.md | 0 |
| agents/decisions/project-config.md | 6 |
| agents/decisions/testing.md | 5 |
| agents/decisions/workflow-advanced.md | 2 |
| agents/role-code.sys.md | 0 |
| agents/role-lint.sys.md | 0 |
| agents/role-planning.sys.md | 0 |
| agents/role-review.sys.md | 0 |
| agents/archive/2026-01-07-bug4-complete.md | 1 |
| agents/archive/2026-01-07-context.md | 1 |
| README.md | 18 |
| research/sonnet-zero-subagent.md | 2 |
| research/sonnet-zero-comparison.md | 1 |
| research/sonnet-minimal-subagent.md | 1 |
| research/sonnet-base-subagent.md | 1 |
| research/sonnet-base-agent.md | 1 |
| package.json | 1 |

**Total files:** 30

**Total occurrences replaced:** 74

## Notes

- One occurrence intentionally preserved: `agents/session.md` reference to "runtime refs to `claudeutils`" in SP-2 scope description (contextual reminder of deferred work)
- All directory path references (`src/claudeutils/` → `src/edify/`) and CLI command references successfully rewritten
- No files excluded per scope rules (plans/ handled separately, src/ and tests/ handled separately, plugin/ handled separately)

## Verification

Final grep confirms 0 remaining `claudeutils` references in scope (except 1 context reference in session.md as documented above).
