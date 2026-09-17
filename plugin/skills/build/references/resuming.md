# Resuming After a Context Ceiling or a Kill

A run that hit a context ceiling, or whose session was killed, resumes from
committed state rather than from memory of what it was doing.

1. Find the last checkpoint commit in `git log`.
2. Run that checkpoint's verification.
3. Build the inventory of remaining work from its output.
4. Resume from the next item.

**Do not use `just precommit` as a state-assessment tool.** It is a pass/fail
gate, not a diagnostic: a green run says the tree is valid, never which items
already landed, and a red one says nothing about where the run stopped.
