# Brief: Anchor /proof Protocol with Visible State Output

## Context

/proof defines a state machine (entry → loop → terminal actions) but never instructs the agent to communicate state to the user. The agent committed the exact anti-pattern documented in /proof's own §Anti-Patterns: "Does this look right?" → "yes" → proceed.

Root cause: the state machine is invisible. Without visible state output, the agent frames entry as a binary question (yes/no) rather than an open invitation. Bare "y" becomes ambiguous — approval or terminal action? The user had no action menu showing available commands (proceed, learn, suspend, sync).

## Proposed Change

Add visible state + actions output at each /proof transition point. Dual purpose:

1. **Agent protocol anchor (D+B pattern):** The act of emitting state forces the agent to know which state it's in. The output IS the structural anchor — protocol adherence becomes a side effect of generating the output.
2. **User feedback:** The user sees available actions and current state, can participate meaningfully.

### Transition points requiring state output:

- **Entry:** After summary → emit state (reviewing, available actions: feedback text, proceed, learn, suspend, sync)
- **After reword confirmation:** Emit accumulated decisions count + state
- **After sync:** Emit full decision list + state
- **Terminal action:** Emit final state (applying N decisions / no changes)

### Output format (sketch):

```
[proof: reviewing outline.md | decisions: 0 | actions: feedback, proceed, learn, suspend, sync]
```

Compact, machine-readable-ish, serves both anchor and UX purposes.

## Evidence

- Session deviation: /proof loaded, anti-pattern committed anyway. Low context load — not a capacity issue.
- /proof §Anti-Patterns first entry matches observed behavior exactly
- /proof §Terminal Actions defines proceed/learn/suspend/sync but no instruction to display them
- D+B pattern: visible output as structural anchor (established pattern in design skill, recall gates)

## Open Questions

- Exact output format — the sketch above is a starting point. Should it be more or less structured?
- Whether the action list should be full on every transition or abbreviated after first display
