# Settings.local.json Triage Protocol

Brief from devddaanet session (2026-03-06). Agent repeatedly skipped or mishandled `settings.local.json` changes across 4 commit rounds until corrected.

## Problem

`settings.local.json` accumulates permission grants during a session (WebFetch domains, Bash patterns). At commit time, each entry needs triage:

- **Permanent workflow feature** → promote to `settings.json`, clear from local
- **Session-specific** → drop, clear from local
- **Job-specific** → keep in local only if justified by handoff context

The agent's default behavior was to either ignore the file ("unrelated local settings") or commit it as-is without triage. Both are wrong.

## Observed Failures

1. First commit: skipped `settings.local.json` entirely as "unrelated" — user corrected
2. Second round: included it but didn't triage entries — user corrected
3. Dropped `pbcopy` as "session convenience" when it's a permanent workflow feature — user corrected
4. Subsequent rounds: agent learned within session, but this knowledge doesn't persist

## Proposed Change

Add settings.local.json triage as a step in the commit skill. During the staging phase:

1. Read `settings.local.json` — if non-empty, triage each entry
2. For each permission entry: classify as permanent/session/job-specific
3. Permanent → promote to `settings.json` via Edit, clear from local
4. Session-specific → clear from local
5. Job-specific → keep only if handoff justifies it
6. After triage, `settings.local.json` should be empty `{}` or contain only job-justified entries
7. Stage both files

## Artifacts to Modify

1. **Commit skill** (`.claude/skills/commit/SKILL.md` or equivalent) — add triage step after staging, before commit
2. Possibly a **learning/decision entry** so recall surfaces it during commit workflows

## Key Principle

`settings.local.json` is versioned specifically so changes can be reviewed and incorporated. It is NOT a throwaway file. Empty local = clean state.
