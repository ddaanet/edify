---
name: release
description: "Releases `dev` onto `main` through the full cascade: /simplify, the Fable and Codex astra release reviews, triage and parallel fixes, a medium loop until only lows remain, then push, preflight and `just release`. Use when the user runs /edify:release or asks for a release, and when a continuation resumes one. Not for the per-commit review, which is edify:review."
---

# Release

Run `just precommit` before every commit below. Switch branches only where
section 6 says to.

## 1. Where the ritual stands

A frame whose task or todo opens with "resume `/edify:release` at step N":
resume at that step with the state the frame records. Otherwise the delta is
`git log --oneline main..dev`; an empty delta ends the ritual with that report.

## 2. Simplify

Run `/simplify` over `main...dev`. Commit its edits with a `refactor:` prefix.
No review of that commit on its own.

## 3. Release reviews, in parallel

All review `main...dev` as it now stands. Dispatch them together and wait for
all of them.

- **Code review on Fable.** Dispatch an agent with `model: fable` whose task is
  `/code-review high main...dev`, writing its findings to
  `.claude/review-<sha>.md` (severity and a one-line reason per finding) and
  replying with one line pointing at it. Read the file.
- **Adversarial review on Codex astra.** Write the focus to
  `.claude/review-focus.md`: what the delta is for, what is settled and not up
  for challenge, the sources to verify claims against, and the finding format
  (file, line, severity, reason). Then run, unsandboxed and in a background Bash
  call:

  ```bash
  companion="$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs | sort -V | tail -n 1)"
  model="$(jq -r '.models[] | .slug // .id' ~/.codex/models_cache.json | grep astra | head -n 1)"
  node "$companion" adversarial-review --wait --base main --model "$model" "$(cat .claude/review-focus.md)"
  ```

  Its findings arrive in the background task's output.
- **In a plugin repo, `plugin-dev:skill-reviewer` and
  `plugin-dev:plugin-validator`.** Neither has `Write`, and a reply is cut at
  about 4000 characters: ask for the report in parts under 3500 characters, each
  but the last ending with a continuation line and the last with
  `END OF REPORT`.

## 4. Triage high and medium findings, fix in parallel

Read every report. Assign severity at triage, not from the reviewer: a finding
is high or medium when a reader following the text would do the wrong thing — a
command that fails, a claim a probe or primary source contradicts, two places
prescribing opposite actions. Phrasing, wrapping, placement and redundancy are
low, and so is a guard for a state nothing produces. Verify a finding against
its source before accepting it. List the lows as declined in the reply; never
dispatch them.

Partition the high and medium findings by the files they touch, one fix agent
per partition, dispatched together; no two agents share a file. Each agent fixes
its findings, runs the gate, commits with a `fix:` prefix, and replies with its
commit and a one-line summary.

## 5. Medium loop

Run `/code-review medium` over the fix commits of the previous round
(`<sha before the round>..dev`). Triage as in step 4, fix the high and medium
findings in parallel agents, commit. Repeat over the new fix commits until a
pass returns only lows.

## 6. Ship

In claude-plugin-dev and in a plugin whose `plugin-dev/VERSION` is 0.16.0 or
later, every step runs on `dev`: skip item 2 of the list below, and the checkout
and merge of its item 5 (the push of `dev` in item 5 still runs). The release
moves `main` itself.

1. Push `dev` when `git ls-remote --heads origin dev` prints a line.
2. `git checkout main && git merge --ff-only dev`.
3. `/ddaa:preflight`. ` M memory` in the status is not a block; any other dirty
   path is one.
4. Pick the bump from the delta and say which in the reply: `minor` when a
   user-visible capability lands or an installed setup changes (a file path or
   shape, a hook or command name); `patch` otherwise; `major` only when the user
   named it. Then `just release <bump>`, alone in its Bash call, with no `cd`
   prefix and no `MARKETPLACE_DIR=` prefix.
5. `git checkout dev && git merge --ff-only main`. Then push `dev` under item
   1's condition.

## Boundaries

A boundary is a triage done (step 4, before its fixes are dispatched) or a fix
pass done (step 4's, and each round of step 5). At each one, run
`~/.claude/bin/context-usage`. Then:

- Past 150k with no agents running: `/autodrive-handoff:handoff` with `clear`
  and `continue`. Its task text opens with "resume `/edify:release` at step N"
  and records what each review found, what is fixed and what is still open.
- Past 200k with agents running: `/autodrive-handoff:precompact` with
  `compact: true` and `continue`. Its todo opens with the same resume line and
  lists each running agent's id and what it owns.
