# A named delegate loses its dispatches' hand-backs

A delegate launched with the `Agent` tool's `name` parameter is a teammate. Its
spawn result reads "will receive instructions via mailbox". It has no
`SubagentHandback`, and it sends and receives only by `SendMessage`. A delegate
launched without `name` is a plain background agent ("Async agent launched"). It
has `SubagentHandback`, and its subagents' hand-backs come back as their `Agent`
results.

That difference decides how a delegate's own dispatches can report (auto mode,
CC 2.1.281, each row probed):

| Delegate | The subagent reports by                | It arrives                                |
| -------- | -------------------------------------- | ----------------------------------------- |
| unnamed  | `SubagentHandback`                     | as the `Agent` result, in the same turn   |
| named    | `SendMessage` to the delegate's name   | once the delegate goes idle, resuming it  |
| either   | a named output file                    | when the delegate reads it                |

Under a named delegate the harness still offers `SubagentHandback` and tells the
subagent that only that call reaches its caller. Every call returns
`Nothing was sent: the agent that spawned you is no longer running.`, while the
delegate is alive and blocked on the call. The delegate's `Agent` result then
reads `The subagent ended without delivering a report through SubagentHandback`
and suggests `SendMessage`. Following that advice sends the resumed run's
`[Subagent hand-back]` to the main session.

On CC 2.1.283 the same dispatch's `SubagentHandback` reached the main session
instead of failing, and the delegate saw only an idle "waiting for ...". Either
way the delegate never receives it: route the report through a named file, or
have the main session relay it by `SendMessage`.

A subagent's `SendMessage` to the delegate's name does reach it. It stayed
queued through the delegate's next five tool calls and arrived as a
`<teammate-message>` the moment the delegate went idle, resuming it within the
same user turn.

- **A delegate that dispatches is launched without `name`.** Address it by the
  agent id from its spawn result, for gate answers and resumes alike.
- A named delegate's dispatch either writes a file, or is told the delegate's
  name and reports by `SendMessage`. In the second case the delegate goes idle
  after the dispatch returns, and the report resumes it. An agent type whose
  tool list lacks both `Write` and `SendMessage` (for example
  `plugin-dev:skill-reviewer`) has no channel at all.
- Never resume a named delegate's subagent to collect a report.

The documentation says a launcher receives its nested subagents' results and
does not mention the named case. anthropics/claude-code#96225 reports the same
hand-back error for an agent-team teammate's subagent on 2.1.280. Re-probe on a
newer CC version.
