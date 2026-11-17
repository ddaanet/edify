# Background Bash has no duration cap

The Bash tool's `timeout` (default 120000 ms, max 600000 ms) bounds how long a
command is awaited in the foreground. A task launched with
`run_in_background: true` has no duration cap: the timeout is computed and never
applied as a wait, the task is registered, and the tool returns.

A foreground command that hits its timeout is moved to the background when the
harness classifies it as backgroundable, not killed. So "run it in the
foreground" cannot be promised for a gate near the cap; a nine-minute gate
crosses it with any slack. A background task ends only by exiting, by a turn
abort, or, for a subagent, when the agent gives its final response, since that
ends the subagent's context.

Verified against CC 2.1.261 by decompiling the Bun-embedded bundle, then
operationally: a nine-minute gate launched in the background survived the main
agent ending its turn, completed, and recorded its pass.

## A subagent receives the notification

The completion notification does reach a subagent (CC 2.1.282, read from the
sidechain JSONL): a `queued_command` attachment with
`commandMode: task-notification`, routed through the main session's queue. The
parent transcript's `queue-operation` entries are routing, not delivery.

What stalls a subagent is a watcher it builds instead: an `until` loop over gate
mtimes whose start postdated the first gates, or a Monitor, idled on with the
notification already in hand. One message recovers it when it names the act that
ends the wait: `TaskStop` the watcher, then read the gates and commit. A message
that only says "read the gates" leaves the agent reasoning that it must not
duplicate the run, still waiting. A fresh Bash call can neither see nor kill the
agent's tasks, so the resume is the only lever.

## Reading a verdict

`ps` in a fresh Bash call cannot see another background task's processes, and a
runner that buffers into a log file prints nothing until the end, so neither
settles whether a run is alive.

Read the verdict from the durable artifact the gate writes on a pass (a
sentinel, a cache marker, a report) and say the verdict came from there. Its
validity is the gate's own freshness rule, not the filesystem's: a sentinel
holding a content hash of the recipe's declared inputs is valid when re-hashing
those inputs reproduces it, and an mtime comparison is a guess at a question the
recorded hash answers exactly. A killed multi-recipe gate keeps whatever
finished, so only the missing recipes rerun. A gate with no such artifact gives
a waiting agent nothing; add one.

## How to apply

A gate longer than ten minutes is not a reason to split it into per-recipe calls
or to skip recording its pass. Launch it in the background and wait for the
notification; arm a Monitor only when the result must be acted on inside the
same turn. Split calls remain the fallback when the run genuinely dies, and then
say the pass was not recorded.
