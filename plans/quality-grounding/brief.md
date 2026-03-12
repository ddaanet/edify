**⚠ UNREVIEWED — Agent-drafted from session.md task descriptions. Validate before design.**

# Quality Grounding

## Problem

Workflow skills and operational rules contain claims, thresholds, and methodologies that lack external grounding. Per the no-confabulation rule, ungrounded assertions should be flagged and validated.

## Investigation Scope

Four sub-problems, each requiring `/ground` skill execution:

- **Ground workflow skills:** Verify skill behaviors (design, runbook, orchestrate, inline) against external methodology sources. Are the patterns well-established or invented?
- **Safety review expansion:** Assess safety review coverage gaps. What risks exist that current review doesn't check?
- **Decision drift audit:** Compare current decision file content against original intent. Have decisions evolved beyond their evidence base?
- **Prose gate terminology:** Ground prose quality terms ("deslop", "framing", "hedging") in measurable, externally-validated criteria

## Reference

- Existing audit: `plans/reports/workflow-grounding-audit.md`
- No-confabulation rule: `agent-core/fragments/no-confabulation.md`

## Success Criteria

- Each sub-problem has grounding report with sources
- Ungrounded claims flagged with "ungrounded — needs validation" per no-confabulation rule
- Grounded claims annotated with source provenance
