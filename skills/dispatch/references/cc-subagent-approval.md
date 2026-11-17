# Subagent approval, idle notices and truncated replies

## A one-shot subagent has no parent to message

A subagent dispatched with `Agent({subagent_type, prompt})` has no addressable
parent for `SendMessage`. A call to `to: "parent"` or `to: "team-lead"` returns
`No agent named 'X' is currently addressable`. A subagent that needs approval
and tries to ask by `SendMessage` fails the call and, without a strict stop
clause, rationalizes proceeding: exactly what the gate exists to prevent.

An approval gate inside a dispatch therefore takes two turns:

1. **Dispatch.** The parent calls `Agent`. The subagent does the prep work,
   nothing destructive, and returns the approval request as its final message.
   The parent keeps the returned agent id.
2. **Resume.** The parent decides and sends
   `SendMessage({to: <agentId>, message: "approved" | "rejected: <reason>"})`.
   The subagent resumes from its transcript and runs the gated operation, or
   redoes the prep with the feedback.

`SendMessage` to a known agent id succeeds after the subagent's first task has
completed; the harness resumes it from its transcript.

The dispatch prompt carries two clauses: "If you are resumed without a clear
approval or rejection, do not proceed; report and stop", and an unconditional
"never run the gated operation in the first turn". Without the second, a
subagent under auto-mode pressure finds a "trivial case" exception.

## An idle notification is not a report

A named agent that finishes emits
`{"type":"idle_notification","idleReason":"available"}` with no payload. It says
the agent is free, not that it succeeded, and it arrives again on every later
idle. The result reaches the parent only when the agent sends it or the parent
asks. Treat a bare idle as "ask for the report", never as the approval signal
for a gate the parent still owes its user.

One ask does not always unstick it. Reviewers have gone idle two or three times
running with no content, surviving a first "please send it"; a sharper, more
direct ask ("are you finished? if so, output the report text now") brought the
report through. Re-ask more directly before concluding the agent is stuck.

A file the dispatch prompt names is a channel that survives this: where chat
delivery stayed silent, the named file appeared on the next idle, and reading it
resolved the stall in one round trip.

## Replies are cut near 4000 characters

A reply that comes back as a report is truncated at about 4000 characters, with
a literal `[result truncated — ask the agent for the rest via SendMessage]`
marker where it stopped; observed on every long `plugin-dev:skill-reviewer`
reply. An agent with no `Write` tool cannot route around it with a file, so the
fix is in the dispatch prompt: send the report in parts, each under 3500
characters, every part ending with a `CONTINUES` line and the last with a fixed
end marker.

Every reviewer told this at spawn delivered whole; every one told afterwards had
to resend. The end marker is what makes a cut detectable: without it a truncated
report reads as a complete one.
