# L1 Prose+Config Review: handoff-cli-tool (RC13)

**Design reference:** `plans/handoff-cli-tool/outline.md`
**Files reviewed:** 4 (2 agentic prose, 2 configuration)
**Prior review:** RC12 prose review (5 minor, 0 major, 0 critical)
**Delta since RC12:** None. All 4 files unchanged since RC12 review.

## RC12 Finding Verification

| RC12 ID | Description | Status |
|---------|-------------|--------|
| m-18 | "STOP -- fix issues and retry" competes with communication rule 1 | OPEN |
| m-19 | H-2 reference identifier unresolvable by agents | OPEN |
| m-20 | design/SKILL.md changes are standalone bugfix, scope attribution | OPEN (scope note, not defect) |
| m-21 | settings.local.json trailing newline change only | OPEN (vacuity note, not defect) |
| m-22 | .gitignore broadening unrelated to plan scope | OPEN (scope note, not defect) |

All 5 RC12 minors remain open. None were addressed because all are minor with no functional impact, and the C-1 fix (commit `b6a715fb`) was code-only.

## Findings

**m-18** `agent-core/skills/handoff/SKILL.md:146` -- actionability -- "STOP -- fix issues and retry" competes with communication rule 1 ("stop on unexpected results... STOP and wait for guidance"). The instruction tells the agent to both stop and self-correct. An agent following communication rule 1 literally would stop and wait; an agent reading the skill instruction locally would attempt fixes autonomously.
Severity: Minor

**m-19** `agent-core/skills/handoff/SKILL.md:27` -- constraint precision -- "The CLI's committed detection (H-2) handles uncommitted prior handoffs" references H-2 as an outline identifier. Agents cannot resolve this to a CLI behavior. The surrounding instruction ("skill always writes full state") is self-contained and actionable without the reference.
Severity: Minor

**m-20** `agent-core/skills/design/SKILL.md:135-142` -- scope boundaries -- Simple routing fix (removed "implement directly," added "chain to /inline") is a standalone bugfix for the competing-execution-paths learning. Outline line 373 lists "Skill modifications" as OUT. Scope attribution note, not a defect.
Severity: Minor

**m-21** `.claude/settings.local.json` -- vacuity -- Change adds trailing newline to `{}`. POSIX compliance. No functional effect.
Severity: Minor

**m-22** `.gitignore:17` -- scope boundaries -- `/.vscode/` to `/.vscode` broadens directory-only to file-or-directory match. Handles sandbox-created `.vscode` character device. Unrelated to plan scope.
Severity: Minor

## Completeness Check

| Outline Requirement | Status | Evidence |
|--------------------|--------|----------|
| Coupled skill update: precommit gate | Delivered | handoff/SKILL.md Step 7, line 144-146 |
| Coupled skill update: `just precommit` runs before `_handoff` CLI | Delivered | Step 7 runs after all writes, before STATUS display |
| allowed-tools expansion for `just`, `git`, `claudeutils` | Delivered | Frontmatter line 4 |
| Legacy uncommitted-prior-handoff detection removed | Delivered | Lines 27-28 replaced with single bullet delegating to CLI |
| Legacy merge directive removed | Delivered | "Multiple handoffs before commit" paragraph deleted |

## Summary

- Critical: 0
- Major: 0
- Minor: 5 (carried from RC12, all unchanged)

No new findings. All 4 files are byte-identical to the RC12 review. The 5 minors are unchanged: 2 functional (m-18 actionability, m-19 constraint precision) and 3 scope/vacuity notes (m-20, m-21, m-22). The coupled skill update specified by the outline is fully delivered.
