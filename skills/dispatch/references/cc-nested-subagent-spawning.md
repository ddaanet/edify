# Nested subagent spawning

Verified against the Claude Code docs and a live probe on CC 2.1.278: an
`Agent`-tool subagent can itself call `Agent`, to a depth set by
`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` (three layers below the main conversation
worked), and background subagents keep the `Agent` tool.

Running a dispatching skill inside a delegate rather than the main session keeps
the main context free for review and audit: main session, then a
`general-purpose` delegate invoking the skill, then per-item agents.

Constraints on the delegating layer:

- **Its type must be `general-purpose`.** An agent definition that enumerates
  its tools without `Agent` cannot dispatch. The `claude` type carries a
  background-job narration protocol that gets in the way of a skill running its
  own dispatch loop.
- **One Opus delegate carries about one heavy phase** of a multi-phase
  orchestration before its context fills. Hand the work over in phase-sized
  units, and make the skill's phase-boundary resume block the handoff: the next
  delegate starts from it, not from the previous one's transcript.
- **The brief sets a hard context stop at about 200k tokens.** Past it the
  delegate finishes only the dispatch or commit in flight, writes and commits a
  Resume section (last commit, exact step, decisions given, what remains) and
  stops. A delegate does not stop on its own, and a teammate's idle notices
  carry no token count: one briefed without a cap ran to about 330k before
  anyone noticed.
- **A skill's approval gate comes back as the delegate's final message.** The
  delegate stops there; the answer goes back by `SendMessage` to the same agent,
  which continues with its context intact. A new `Agent` call restarts the skill
  from nothing.
- **Launch it without `name`.** A named delegate is a teammate, and its
  dispatches' `SubagentHandback` never reaches it: see
  `cc-named-delegate-handback-lost.md`.
- The delegate's Bash runs in the main session's sandbox, so a dispatch that has
  to fetch names its hosts in `allowed_domains` up front.
- A delegate that runs `git stash` to compare two states takes the parent's
  staged files with it. The dispatch prompt rules out `git stash`, `git reset`
  and blanket `git add`, and names any pre-staged files.
