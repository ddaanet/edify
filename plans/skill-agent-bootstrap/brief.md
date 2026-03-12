**⚠ UNREVIEWED — Agent-drafted from session.md task descriptions. Validate before design.**

# Skill Agent Bootstrap

## Problem

Skill pre-work patterns (context loading, recall passes, gate checks) are inconsistently implemented across skills. Agent context injection (operational rules, project conventions) is manual and error-prone. Four related sub-problems:

- **Retrofit skill pre-work:** Skills have ad-hoc pre-work (some run recall, some check gates, some do neither). Need a standardized pre-work phase that all skills execute.

- **Agent rule injection:** Sub-agents launched via Task tool lack operational rules (no-confabulation, error-handling, token-economy) unless manually injected in each prompt. Need automatic injection mechanism.

- **Skill-dev skill:** No tooling exists for developing, testing, or validating skills. Creating a new skill requires manual file creation, frontmatter authoring, and trial-and-error testing.

- **Skill prompt-composer:** Skills compose prompts from fragments manually. Need a composition tool that assembles skill content from reusable fragments with consistent formatting.

## Dependencies

- Interacts with plugin-dev skills (skill-development, agent-development)
- Check platform plugin capabilities before building custom tooling

## Success Criteria

- Design identifies which sub-problems are independent vs. coupled
- Architecture for standardized pre-work that existing skills can adopt incrementally

### Skill Dependencies (for /design)

- Load `plugin-dev:skill-development` and `plugin-dev:agent-development` before design
