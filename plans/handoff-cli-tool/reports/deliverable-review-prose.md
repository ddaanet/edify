# Deliverable Review — Prose & Configuration (Layer 1)

**Plan:** handoff-cli-tool
**Design reference:** `plans/handoff-cli-tool/outline.md`
**Date:** 2026-03-21

## Files Reviewed

| File | Type | Change |
|------|------|--------|
| `agent-core/skills/handoff/SKILL.md` | Agentic prose | +5/-1 (submodule commit `392e463`) |
| `.claude/settings.local.json` | Configuration | +4/-4 (uncommitted working tree) |

---

## Findings

### 1. SKILL.md — Missing `allowed-tools` entry for `just precommit`

- **Location:** `agent-core/skills/handoff/SKILL.md:4`
- **Axis:** Functional correctness
- **Severity:** Critical

The frontmatter declares `allowed-tools: Read, Write, Edit, Bash(wc:*), Task, Skill`. Step 7 instructs the agent to "Run `just precommit`" — a Bash command. The `Bash(wc:*)` permission restricts Bash to `wc` commands only. The agent executing this skill cannot run `just precommit`.

The commit skill demonstrates the correct pattern at line 4 of its own SKILL.md: `Bash(just precommit)` is explicitly listed.

**Fix:** Add `Bash(just precommit)` to the `allowed-tools` list. Also add `Bash(claudeutils _worktree ls)` since Step 2 instructs the agent to run that command for plan status derivation.

### 2. SKILL.md — Missing `Bash(git diff:*)` for prior-handoff detection

- **Location:** `agent-core/skills/handoff/SKILL.md:27`
- **Axis:** Functional correctness
- **Severity:** Major (pre-existing, not introduced by this deliverable)

Step 1 instructs: "Check `git diff HEAD -- agents/session.md`." This requires `Bash(git diff:*)` which is absent from allowed-tools.

**Note:** Pre-existing issue — not part of the +5/-1 change. Flagged because the new Step 7 makes the allowed-tools gap pattern more visible.

### 3. SKILL.md — Step 7 content is correct

- **Location:** `agent-core/skills/handoff/SKILL.md:147-149`
- **Axis:** All prose axes
- **Severity:** N/A (pass)

The step meets the design requirement ("Handoff skill must add `just precommit` as a pre-handoff gate before calling `_handoff` CLI"):
- Positioned after all writes (Steps 2-6), before STATUS display (Step 8) — correct
- Failure behavior: output result, STOP, agent fixes and retries — correct, deterministic
- Success behavior: continue to STATUS display — correct
- Scope boundary: validates session.md, learnings.md, plan-archive.md — matches the writes in Steps 2-5
- Step numbering: old Step 7 (Display STATUS) renumbered to Step 8 — correct

### 4. settings.local.json — Not a plan deliverable

- **Location:** `.claude/settings.local.json` (entire file)
- **Axis:** Conformance
- **Severity:** Minor

The file is not referenced in the design outline, runbook, or any step file as a deliverable. The uncommitted change (sandbox `false` → `true`, section reorder) duplicates settings already present in `.claude/settings.json:190-198`. The `.local` file's sandbox block is redundant — `settings.json` already has `sandbox.enabled: true` and `autoAllowBashIfSandboxed: true`.

No finding against the plan — this appears to be an incidental environmental change, not a plan deliverable. Whether to commit or discard is a session-level decision.

---

## Summary

| Severity | Count | Details |
|----------|-------|---------|
| Critical | 1 | Missing `Bash(just precommit)` in SKILL.md allowed-tools — Step 7 cannot execute |
| Major | 1 | Pre-existing: missing `Bash(git diff:*)` for Step 1 (not introduced by this change) |
| Minor | 1 | settings.local.json is not a plan deliverable |

**Verdict:** One critical finding blocks the deliverable. The precommit gate (Step 7) is correctly specified but the skill's tool permissions prevent its execution. Fix: add `Bash(just precommit)` to the `allowed-tools` frontmatter.
