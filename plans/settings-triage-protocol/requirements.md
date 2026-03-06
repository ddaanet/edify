# Settings Triage Protocol

## Requirements

### Functional Requirements

**FR-1: Triage step in commit skill**
Add a step to the commit skill (`agent-core/skills/commit/SKILL.md`) that reads `.claude/settings.local.json` during the staging phase and triages each permission entry. Step must follow D+B hybrid pattern — opens with `Read(.claude/settings.local.json)` tool call, not prose judgment.

Acceptance criteria:
- Step reads `settings.local.json` before staging
- Each entry classified as permanent, session-specific, or job-specific
- Step is skipped (no triage needed) only when file is empty `{}` or absent
- Step uses D+B pattern: Read anchor → classify → act

**FR-2: Promote permanent entries to settings.json**
Entries classified as permanent workflow features are moved from `settings.local.json` to `settings.json` via Edit, then cleared from local.

Acceptance criteria:
- Permanent entries added to appropriate section in `settings.json`
- Corresponding entries removed from `settings.local.json`
- Both files staged for commit

**FR-3: Clear session-specific entries**
Entries classified as session-specific (one-time domain grants, temporary permissions) are removed from `settings.local.json`.

Acceptance criteria:
- Session entries removed from `settings.local.json`
- After triage, `settings.local.json` is empty `{}` or contains only job-justified entries

**FR-4: Job-specific entry handling**
Entries classified as job-specific are retained only if justified by handoff context (active worktree needs, in-progress task requirements).

Acceptance criteria:
- Job-specific entries retained with justification visible in commit or handoff context
- Entries without justification treated as session-specific (cleared)

**FR-5: Classification guidance**
The skill step includes guidance for common entry types to reduce misclassification.

Acceptance criteria:
- Permanent examples: `pbcopy`, recurring tool patterns, workflow-essential domains
- Session examples: one-off WebFetch domains, exploratory Bash patterns
- Job examples: worktree sandbox paths (managed by `_worktree` CLI)

### Constraints

**C-1: D+B hybrid pattern required**
Triage step must open with a concrete tool call (Read), not prose judgment. Per "How to Prevent Skill Steps From Being Skipped" — prose-only judgment steps are a structural anti-pattern in skills.

**C-2: Commit skill extension point pattern**
Per "When Treating Commits As Sync Points" — new versioned state types get extension points in the commit skill. This is the `settings.local.json` extension point.

**C-3: Existing step numbering**
Current commit skill steps: 1 (pre-commit validation + discovery), 1b (submodule handling), 2 (draft message), 3 (gitmoji), 4 (stage, commit, verify). Triage step must integrate without breaking existing flow.

**C-4: Allowlist constraint**
Commit skill requires each git/just command as separate Bash call. Triage edits to settings files follow the same pattern — separate Read/Edit calls, no chaining.

### Out of Scope

- Automated classification via script — classification requires judgment (permanent vs session is context-dependent), not scriptable with zero false positives
- Hook-based enforcement — the commit skill IS the chokepoint; adding a hook is redundant layering
- `settings.local.json` management outside commit time — worktree CLI manages it during `_worktree new/rm`
- Changes to `.claude/.gitignore` — `settings.local.json` is already gitignored per discovery

### Open Questions

None — Q-1 (step placement) resolved: step 1c, after submodule handling, before message drafting. Triage mutates files → must precede staging and message drafting. Follows sync-point pattern (1b = submodule, 1c = settings). Precommit doesn't validate JSON config → no re-run needed.

### References

- `plans/settings-triage-protocol/brief.md` — problem statement and observed failures from originating session
- `plans/settings-triage-protocol/recall-artifact.md` — recall entries informing design constraints

### Skill Dependencies (for /design)

- Load `plugin-dev:skill-development` before design (skill modification in FR-1)
