# Item 2.1 — `plugin/skills/build/SKILL.md`

Status: **blocked — classifier refused `plugin/skills/build/SKILL.md`.** Every
Edit on the target returned "The server-side auto mode classifier gave no
verdict (it skipped this action)". Nothing was applied; the target is unchanged
and nothing is committed for this item. Per the dispatch rules, no retry and no
sed, Bash or Write fallback was attempted.

The exact edits prepared, old → new, one per bullet:

## Frontmatter — orch M1, m7 (KD-4)

- old: `allowed-tools: Agent, Read, Write, Edit, Bash, Skill, SendMessage, TaskOutput, TaskStop`
- new: `allowed-tools: Agent, Read, Write, Edit, Bash, Skill, SendMessage`

## §1 — orch C2 (KD-6)

- old:

  ```
  ## 1. Load the work

  ```bash
  ```

- new:

  ```
  ## 1. Load the work

  `<job>` is the `plans/<job>` path the invocation names. A run resumed in a fresh
  session is re-invoked with the same path; nothing infers it.

  ```bash
  ```

## §2 DIRTY bullet — orch m5 (KD-7)

- old: `- Exit 1 with `DIRTY:` → STOP: "Dirty tree. Commit or stash before /build."`
- new:

  ```
  - Exit 1 with `DIRTY:` → STOP: "Dirty tree. Commit or stash before /build."
    Any change is dirt, untracked files included, except three paths dirty by
    convention: `memory` (the gitlore submodule), `.claude/handoff-*.md` and
    `inbox/*.md`. A listing the `sandbox-lies` hook annotates as sandbox masks is
    re-run instead, per `references/escalation.md` §Post-item remediation.
  ```

  The pointer lands only once Item 2.6 adds the mask re-run at the head of that
  section's exit-1 bullet.

## §3.2 — inline m9

- old: `Patterns for implementing this, not for classifying it.`
- new: `Select patterns for implementing this task, not for classifying it.`

## §4.1 — orch m3

- old:

  ```
  §Proportionality holds; otherwise dispatch `edify:corrector` in its checkpoint
  form. This is
  ```

- new:

  ```
  §Proportionality holds; otherwise dispatch `edify:corrector` scoped to this
  item's changes. This is
  ```

## §4.2 — orch M4

- old (last line of §4.2): `the mechanical work, since subagents have no parent context.`
- new:

  ```
  the mechanical work, since subagents have no parent context.

  Where the item is a review, the corrector commits nothing: commit its report,
  with the fixes it applied where there are any, before §4.4. Stage those paths by
  name and commit with `git commit -- <paths>`.
  ```

  Judgement: the `git commit -- <paths>` clause applies KD-7's pathspec commit
  to the orchestrator's own commit, since a `/handoff` in this session can leave
  `.claude/handoff-task.md` staged. Drop it if KD-7 is meant for dispatches only.

## §4.4 — orch M4

- old: `review once its commit lands, and any general or directly executed item. Not`
- new:

  ```
  review once its commit lands, a review item once §4.2's commit lands, and any
  general or directly executed item. Not
  ```
