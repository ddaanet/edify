# Brief: wt-exit-ceremony

## Origin

Discussion during wt-rm-dirty deliverable review session (2026-03-01). After review passed (0 Critical/Major/Minor), the transition from worktree to parent session was manual and friction-heavy.

## Problem

After deliverable review passes in a worktree, the user must:
1. Run `hc` (handoff + commit)
2. Switch to parent terminal
3. Remember and type `wt merge <slug>` then `wt-rm <slug>`

No automation guides this transition. The slug must be recalled, the command typed manually.

## Proposed Solution

Two UPS Tier 1 shortcuts:

**`k`/`ok` — acceptance + context transfer:**
- Semantics: "I acknowledge this result, help me transition out"
- Context-dependent behavior: after commit in a worktree with no pending tasks, copies the merge+rm command to clipboard
- Implementation: UPS hook Tier 1 command → `additionalContext` injection → agent runs pbcopy/xclip
- Portability: `pbcopy` (macOS) → `xclip -selection clipboard` or `xsel --clipboard` (Debian, upcoming migration)

**`g`/`go` — forward momentum within session:**
- Semantics: "execute the next thing" (similar to existing `x` but lighter)
- Distinct from `k`: "go" implies work continues in current session; "ok" implies completion acknowledgment + transition
- Collision analysis: "kill" evaluated, no useful meaning in edify context (all kill-like operations have existing mechanisms)

## Worktree Lifecycle Change

The "final step in worktree life" behavior needs codification:
- After deliverable review passes → status shows "Branch complete"
- After commit → `k` copies transition command
- The post-review → commit → transition sequence should be guided, not ad-hoc

## Recalled Context

- UPS hook: `agent-core/hooks/userpromptsubmit-shortcuts.py`
- Tier 1 commands are exact-match, simplest tier (like `c`, `y`)
- `additionalContext` is agent-only, `systemMessage` is user-only (~60 char budget)
- All UPS filtering is script-internal (no `matcher` support)
- `dangerouslyDisableSandbox: true` required for clipboard access

## Semantic Distinction (from brainstorm)

| Situation | `g`/`go` | `k`/`ok` |
|-----------|----------|----------|
| After status display | Execute next task | Acknowledge, might adjust first |
| After commit | Start next pending task | Copy transition command |
| After deliverable review | Start fixing findings | Accept review, proceed to handoff |
| After `d:` conclusion | Execute what was discussed | Accept assessment, think about it |
| Branch complete (no pending) | No target | Transition out (clipboard) |

## Next Step

`/requirements` — capture FRs for both shortcuts and lifecycle behavior change.
