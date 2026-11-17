---
name: dispatch
description: "Rules for dispatching subagents: what the main thread keeps, agent boundaries and reuse, model tier per task, self-contained prompts, naming, and collecting replies. Use when about to call the Agent tool or write a dispatch prompt, and when a dispatched agent idles or its reply comes back cut."
---

# Dispatch

## The main thread orchestrates

Do on the main thread only what would take more tokens to delegate than to do.
An edit that touches three or more files, or a documentation, changelog or test
sweep of any size, is dispatched, with the grep list and the contract in the
prompt. Editing a document through a Bash heredoc is still an edit: the script
and its echoed result stay in context for the rest of the session. Use the Edit
tool for a change that stays on the main thread.

In a red/green dispatch loop the main thread reads and reviews no implementation
diff: a reviewer subagent does. The main thread orchestrates, starts the gate,
commits and talks to the user. A plan naming the main thread as diff reviewer is
overridden by this.

## Agent boundaries

Choose agent boundaries by batching, not by task. "N tasks" does not mean N
subagents, and it does not mean doing them inline either: the cost a subagent
offsets is context churn in the main session. A repeated mechanical edit does
not disqualify an agent; one agent owning the whole run often makes sense. A
shared mutable file rules out only parallel agents; one sequential agent
handling the batch is fine.

Reviewers batch the same way: one reviewer per stage re-runs every pin or
mutation of that stage and lands one review commit, since each commit pays the
full precommit gate. A reviewer of its own is for a code change, where a review
catches a regression, not for a test-only or prose item. "A reviewer re-checks
each X" in a task file names what is checked, not one agent per X.

In a TDD run, split the work by kind: green and mutation loops on Haiku, tests
and prose on Sonnet, and the reviewer of a red phase a different agent from its
author.

## Reuse agents across slices

A loop keeps its roles (one red author, one red reviewer, one green implementer,
each a different agent), and each slice goes to the same agent by `SendMessage`
to its returned agent id. Respawn only when the agent's context reaches about
150k tokens, judged from the usage its last return reports, or at a plan seam:
the boundary between plans or between a plan's phases. A fresh spawn per slice
re-pays the brief and the orientation reads every time.

## Model tier

Pick the tier by how much the task leaves open. Drafting can be high or low
uncertainty, so the word does not pick the tier.

| Task | Model |
| --- | --- |
| Advice, a second opinion; keep its turns lean and code-free | Fable |
| Name brainstorming (`brainstorm-name`) | Opus |
| High uncertainty | Opus |
| Low uncertainty, prose, tests not fully specified | Sonnet |
| Agentic prose edits | Sonnet at least |
| Fully specified work, TDD green and mutation loops | Haiku |
| Haystack ingestion, well-specified call-intensive work | Haiku |
| A `claude-code-guide` query | Haiku |
| Reviewer | one rung above the implementer, Sonnet at least |
| Refactoring a review flagged | Sonnet; escalate to Opus |

Cheaper agents produce code fine from a prose outline, which is why Fable stays
code-free. Haiku misses subtle issues, hence the reviewer floor.

The refactoring row: the Sonnet run handles a common refactoring (split a
module, simplify a function, reduce nesting), factoring out duplication and dead
code before splitting anything. Its prompt says to stop and reply
`escalated: <reason and scope>` when the refactoring turns architectural (a new
abstraction, multi-module impact). On that reply, re-dispatch on Opus with a
prompt saying that run is the escalation, so it does the work instead of
escalating again.

## Writing the prompt

A directive emitted for a subagent is self-contained: absolute paths, an
explicit `cd "<dir>" &&` where the working directory matters, every `$VAR`
resolved at emit time. A subagent shell inherits neither the environment nor the
working directory. Bats tests with `set -e` and pre-set environment variables
routinely mask a missing one; verify a directive by running it verbatim under
`env -i` from an unrelated directory.

The full suite is the gate's to run, once, before the commit. A dispatched
implementer or reviewer runs the test files it touches and its mutants against
those files, and its prompt says so. A flip in an unrelated suite surfaces at
the gate, at the cost of one extra round; an agent's full-suite run duplicates
minutes the gate repeats on every slice.

Launch a gate near the Bash tool's 10-minute cap with `run_in_background: true`.
The dispatched agent receives its task-notification: tell it to wait for that
and build no watcher.

## Naming

Leave the Agent tool's `name` unset on these dispatches and resume an agent by
`SendMessage` to the agent id its dispatch returned. A named agent becomes an
addressable teammate whose report, idle notices and late summaries each arrive
as a separate message; an unnamed one returns once, as the tool result. A label
the loop needs, such as a slice id, goes in the prompt rather than in `name`.

A delegate that itself dispatches is always unnamed: a named one never receives
its subagents' hand-backs. A custom `name` also replaces the agent type, so an
agent definition's frontmatter `hooks:` register nothing. Elsewhere a named
teammate stays available where addressing a worker mid-flight is the point.

## Collecting the result

Agents report in their reply; git, session logs and agent messages hold the
rest, so no report file is written by default. The exception: a dispatch whose
deliverable is itself a long document keeps a report file, because agent replies
are cut near 4000 characters; the Fable release review's findings file in
`edify:release` is that case.

A reviewer with no `Write` tool gets the report asked for at spawn in parts
under 3500 characters, each part ending with a continuation line and the last
with a fixed end marker such as `END OF REPORT`. Without the marker a truncated
report reads as a complete one.

An idle reply is not evidence the agent died. Check the artifact, `git log` and
the tree before re-dispatching. An executor idle "waiting for the watcher"
already has the verdict: one `SendMessage` telling it to `TaskStop` the watcher,
then read the gates and commit, recovers it. Finish the slice directly only if
that resume returns without progress. Never read a subagent's transcript: it is
the full JSONL conversation and overflows the context window.

## References

- `references/cc-subagent-approval.md`: read when a dispatch must stop for
  approval, an agent idles with no report, or a reply ends in
  `[result truncated`.
- `references/cc-named-delegate-handback-lost.md`: read when a delegate's
  subagent gets
  `Nothing was sent: the agent that spawned you is no longer running.`, or
  before naming an agent that dispatches.
- `references/cc-nested-subagent-spawning.md`: read before handing a dispatching
  skill to a delegate agent.
- `references/cc-async-task-notification-quirks.md`: read before polling a
  running agent, or when a finished task notifies again.
- `references/cc-bash-background-no-duration-cap.md`: read when a gate runs near
  the 10-minute Bash cap, or an agent waits on a background run.
