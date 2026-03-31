# Step 6.2

**Plan**: `plans/plugin-migration/runbook-phase-6.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Execute after plugin verified working. Irreversible within session.

---

---

## Step 6.2: Update fragments and documentation

**Objective**: Remove `sync-to-parent` references and symlink documentation from fragments.

**Prerequisites**:
- Step 6.1 complete (symlinks removed, sync-to-parent deleted)
- Read each fragment before editing:
  - `plugin/fragments/project-tooling.md`
  - `plugin/fragments/claude-config-layout.md`
  - `plugin/fragments/sandbox-exemptions.md`
  - `plugin/fragments/delegation.md` (outline specified as target — verify for any `sync-to-parent` references; currently none found, but confirm before skipping)

**Implementation**:
1. `project-tooling.md`: remove `sync-to-parent` references (recipe no longer exists), remove anti-pattern example using `ln -sf` to create symlinks
2. `claude-config-layout.md`: remove the "Symlinks in .claude/:" subsection (lines referencing `.claude/agents/`, `.claude/skills/`, `.claude/hooks/` symlinks and `just sync-to-parent`)
3. `sandbox-exemptions.md`: remove `sync-to-parent` subsection entirely (recipe deleted)
4. `delegation.md`: check for `sync-to-parent` references; skip if none found (currently clean)

**Expected Outcome**:
- No references to `sync-to-parent` in any fragment
- No symlink documentation in `claude-config-layout.md`
- All fragments valid markdown

**Error Conditions**:
- If fragment has other references to symlinks beyond the targeted sections → investigate scope
- If removing a section leaves orphan cross-references → fix or note

**Validation**:
- `grep -r 'sync-to-parent' plugin/fragments/` returns no matches
- `grep 'sync-to-parent\|Symlinks in .claude' plugin/fragments/claude-config-layout.md` returns no matches

---
