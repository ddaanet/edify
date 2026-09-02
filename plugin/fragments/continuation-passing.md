# Continuation Passing Protocol

Skills chain through continuation passing — composable chains that replace hardcoded tail-calls.

## How It Works

A continuation reaches a skill from one of two places, never from a hook. No hook parses input or injects continuation context.

- **The invoking prompt** — a `[CONTINUATION: ...]` suffix in the user's message, or in the `args` a calling skill passes on its tail-call.
- **The task frame** (`.claude/handoff-task.md`) — a chain a prior session's `/handoff:handoff` recorded, read back when the work resumes.

```
User: "/design plans/foo [CONTINUATION: /runbook, /orchestrate]"
  → /design executes, peels /runbook, tail-calls with remainder
  → /runbook executes, peels /orchestrate, tail-calls with remainder
  → /orchestrate executes, no continuation → uses own default-exit
```

**Single skills** pass through unchanged — a skill invoked with no continuation manages its own default-exit behavior.

## Frontmatter Schema

Cooperative skills declare continuation support in YAML frontmatter. "Cooperative" means the skill implements the consumption protocol (reads continuation, peels first entry, tail-calls remainder).

```yaml
continuation:
  cooperative: true
  default-exit: ["/handoff:handoff", "/commit-commands:commit"]
```

- `cooperative: true` — Skill understands continuation protocol
- `default-exit` — Tail-call chain used when standalone or last in continuation chain. Empty `[]` for terminal skills.

## Consumption Protocol

This is the protocol itself, not a template to copy. A cooperative skill's own
`## Continuation` section points here and states only its site-specific
prepend rule (step 2); everything else below is the same for every skill.

As the **final action** of a cooperative skill:

1. Read the continuation from the `[CONTINUATION: ...]` suffix in the invoking
   prompt or Skill args, or from the task frame if the invocation resumed one
2. If the skill needs a subroutine before continuing: prepend entries to continuation
   - Existing entries remain in original order (append-only invariant)
   - Prepend only — never remove, reorder, or modify existing entries
   - Skills that don't need subroutines skip this step
3. If continuation present: peel first entry from (possibly modified) continuation, tail-call with remainder
4. If no continuation: use the `continuation.default-exit` chain from the
   skill's own YAML frontmatter (standalone / last-in-chain). Invoke its first
   entry, passing the remainder as that skill's continuation.

**CRITICAL:** Do NOT include continuation metadata in Agent tool prompts.

### Worked Examples

Incoming: `/orchestrate myplan [CONTINUATION: /commit-commands:commit]`
- Complete the skill's work
- Peel first entry: `/commit-commands:commit`
- No remainder, so invoke: `Skill(/commit-commands:commit)`

Incoming: `/orchestrate myplan [CONTINUATION: /handoff:handoff, /commit-commands:commit]`
- Peel first: `/handoff:handoff`; remainder: `/commit-commands:commit`
- Invoke: `Skill(/handoff:handoff args="[CONTINUATION: /commit-commands:commit]")`

Incoming: `/orchestrate myplan` (no continuation)
- Use frontmatter default-exit: `["/handoff:handoff", "/commit-commands:commit"]`
- Invoke: `Skill(/handoff:handoff args="[CONTINUATION: /commit-commands:commit]")`

Prepend (subroutine call). Incoming: `/orchestrate myplan [CONTINUATION: /handoff:handoff, /commit-commands:commit]`
- A `/commit-commands:commit` checkpoint is needed before the chain resumes
- Prepend: `[/commit-commands:commit, /handoff:handoff, /commit-commands:commit]`
- Peel first: `/commit-commands:commit`; remainder: `/handoff:handoff, /commit-commands:commit`
- Invoke: `Skill(/commit-commands:commit args="[CONTINUATION: /handoff:handoff, /commit-commands:commit]")`
- After it completes, the original chain resumes

## Transport Format

One format throughout, whether the continuation arrives in a user message, in
the task frame, or in a Skill `args` parameter on a tail-call:
```
[CONTINUATION: /runbook, /orchestrate, /handoff:handoff, /commit-commands:commit]
```

Bracket-delimited, comma-separated entries. Each entry: `/skill optional-args`.

## Sub-Agent Isolation

Continuation metadata must never reach sub-agents:
- Do NOT include `[CONTINUATION: ...]` in Agent tool prompts
- Continuation lives in main conversation context only
- Skills construct Agent prompts explicitly — no accidental inclusion path

## Cooperative Skills

| Skill | Default Exit | Notes |
|-------|-------------|-------|
| `/design` | `["/handoff:handoff", "/commit-commands:commit"]` | Planning entry point |
| `/runbook` | `["/handoff:handoff", "/commit-commands:commit"]` | Runbook planning (unified) |
| `/inline` | `["/handoff:handoff", "/commit-commands:commit"]` | Inline execution lifecycle (no runbook) |
| `/orchestrate` | `["/handoff:handoff", "/commit-commands:commit"]` | Runbook execution |
| `/handoff:handoff` | `[]` | Context preservation (terminal) |
| `/superpowers:using-git-worktrees` | `[]` | Terminal skill (parallel task setup) |
| `/commit-commands:commit` | `[]` | Terminal skill |

**Note**: Default Exit column documents each skill's standalone behavior, implemented by the skill itself. Nothing enforces it from outside.

## Error Propagation

Four skills declare `cooperative: true` and chain via tail-calls with zero implicit error handling. A failure mid-chain orphans the remaining continuation.

### Default Behavior: Abort and Report

When a skill fails during a CPS chain:
1. **Abort remaining continuation** — do not invoke the next skill in the chain
2. **Report the failure to the user** — which skill failed, error category (from `error-classification.md`), retryable/non-retryable classification, and the remaining continuation that was orphaned. No pipeline skill writes the task frame; the next `/handoff:handoff` carries the report into it from context
3. **Manual resume** — user resolves the blocker, then re-invokes the failed skill with the remaining continuation in its args

**No automatic retry.** 0 retries by default. Add targeted retry for specific failure types only if they prove common in practice. The retryable/non-retryable classification informs the recorded error context (helping the user decide how to resume), not the immediate response.

**Recovery operations must be idempotent** — a resumed skill may re-execute work that partially completed before failure. Skills should tolerate re-application (e.g., Edit that matches current content, Write that overwrites).

### Pivot Transactions

Points of no return in the chain where compensation is impractical (Saga pattern concept):

| Chain Position | Pivot? | Reason |
|---------------|--------|--------|
| `/design` completes | No | Outline/design is additive, can be revised |
| `/runbook` completes | No | Runbook artifacts can be regenerated |
| `/inline` completes (delegated) | **Yes** | Sub-agents commit per dispatch — multiple commits, compensation impractical |
| `/inline` completes (direct) | No | No intermediate commits — single session, revertible |
| `/orchestrate` completes execution | **Yes** | Multiple commits, file changes, reports — compensating transactions impractical |
| `/handoff:handoff` completes | **Yes** | Session state updated, learnings written — reversion loses institutional knowledge |
| `/commit-commands:commit` completes | **Yes** | Git history modified, push may have occurred |

After a pivot transaction, the chain records the point-of-no-return. Recovery proceeds forward (fix and continue) rather than backward (undo and retry).

### Orphaned Continuation Recovery

When a chain aborts, the failure report names the orphaned continuation:

```markdown
**Orphaned CPS continuation:**
- Chain: `/design → /runbook → /orchestrate → /handoff:handoff → /commit-commands:commit`
- Failed at: `/orchestrate` (EXECUTION_ERROR, retryable: timeout)
- Remaining: `/handoff:handoff → /commit-commands:commit`
- Resume: fix the orchestration issue, then `/orchestrate plans/<name> [CONTINUATION: /handoff:handoff → /commit-commands:commit]`
```

### Skill-Level Error Handling

Each cooperative skill should handle errors by:
- Catching failures from its own operations (Agent tool errors, Read/Write failures)
- Classifying per `error-classification.md` taxonomy (5 categories, retryable/non-retryable)
- If the error is within the skill's scope to fix: fix and continue
- If not: abort, report the failure and the orphaned continuation, do NOT invoke continuation tail-call

**Anti-pattern:** Skill catches error, records it, then proceeds to invoke next skill in chain. The chain must stop at the failure point.

## Adding Continuation to a New Skill

1. Add `continuation:` block to YAML frontmatter
2. Add `Skill` to `allowed-tools` if not present (needed for tail-call)
3. Replace hardcoded tail-call with consumption protocol section
4. Ensure Agent tool prompts exclude continuation metadata
5. Add error handling: on failure, abort continuation and report the orphaned remainder
