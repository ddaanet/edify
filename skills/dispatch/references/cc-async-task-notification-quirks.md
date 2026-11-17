# Background task notification quirks

`TaskOutput(task_id, block=false)` on a still-running `local_agent` task can
return the raw JSONL transcript tail (tool calls, diffs, full file bodies) in
the tool result itself, not just a status line, despite the tool's own guidance
against reading a `local_agent`'s `.output` file directly. Checking on a running
agent this way risks the same context blowup that guidance warns against. Wait
for the `<task-notification>` instead of polling.

A `<task-notification>` can refire for the same task id well after it first
reported `completed`, carrying content unrelated to the original task. The
cause: a background agent's own session is independently interactive. The user
can message it directly, outside the parent conversation, and that resume
produces a new notification answering whatever was asked there, not the
delegated task. Treat as authoritative only what the agent sent for its
delegated task, in its reply or by `SendMessage`; a later notification on an
already-reported task id may be answering something else.
