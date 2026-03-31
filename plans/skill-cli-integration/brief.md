# Brief: Skill-CLI Integration

## Origin

Deliverable review round 2 finding M#4 (`plans/handoff-cli-tool/reports/deliverable-review.md`).

## Problem

CLI tools (`_commit`, `_handoff`, `_status`) exist and work. Skills (`/commit`, `/handoff`) reimplement what the CLIs do instead of composing with them. Execute-rule.md MODE 1 contains inline STATUS template instead of delegating to `_status`.

Original design specified: "Skill integration (future): After CLI exists, `/commit` skill simplifies to: Gate A -> discovery (`claudeutils _git changes`) -> draft message + gitmoji -> pipe to `claudeutils _commit`."

The "(future)" qualifier created permanent deferral -- three review rounds passed without catching the gap.

## Scope

Three integration points:

1. **`/commit` skill** -- currently reimplements staging, validation, commit. Should compose: discovery (`_git changes`) -> draft message + gitmoji -> pipe to `_commit`
2. **`/handoff` skill** -- currently writes session.md directly. Should compose with `_handoff` CLI
3. **execute-rule.md MODE 1** -- contains inline STATUS rendering template. Should reference `_status` CLI output format or delegate

## Design Questions

- What does each skill still own? (Discovery, message drafting, gitmoji selection, user interaction)
- What does the CLI handle? (Staging, validation, filesystem operations, git operations)
- How do they compose? (Skill calls CLI via Bash, or skill prepares input and pipes)
- Does execute-rule.md STATUS template become a reference to CLI output, or does the CLI implement the template?

## Constraints

- Skills are agentic-prose (opus model for edits)
- CLIs are production code (sonnet for implementation)
- Skills must remain functional during transition (no breaking change)
- Handoff skill has continuation protocol that must be preserved

## References

- `plans/handoff-cli-tool/reports/deliverable-review.md` -- M#4 finding
- `plugin/skills/commit/SKILL.md` -- current commit skill
- `plugin/skills/handoff/SKILL.md` -- current handoff skill
- `plugin/fragments/execute-rule.md` -- MODE 1 STATUS template
- Learnings: "When reviewing CLI-skill integration"
