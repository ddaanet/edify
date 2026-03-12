**⚠ UNREVIEWED — Agent-drafted from session.md task descriptions. Validate before design.**

# Design Pipeline Evolution

## Problem

The `/design` skill needs two extensions that both modify its triage and execution logic:

- **Design decomposition tier:** Current triage has Tier 1 (inline), Tier 2 (moderate), Tier 3 (complex). Missing: a decomposition tier where the primary output is breaking a large problem into independent sub-problems, each routed back through triage independently. Currently this happens informally in Tier 3 outlines.

- **Model directive pipeline:** Some design decisions are model-sensitive (opus for architecture, sonnet for implementation). The design skill doesn't currently route model-specific directives — it runs at whatever model the session uses. Need a mechanism to flag design sections requiring specific model capabilities.

## Constraints

- Both changes modify the same skill (`agent-core/skills/design/SKILL.md`)
- Must not break existing Tier 1/2/3 routing
- Decomposition tier may subsume parts of current Tier 3 behavior

## Success Criteria

- Design identifies interaction between decomposition tier and model directive routing
- Clear boundary between what decomposition handles vs. what outline expansion handles
