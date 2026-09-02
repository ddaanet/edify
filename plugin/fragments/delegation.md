## Delegation in Orchestration

When executing runbooks via `/orchestrate`, the orchestrator coordinates but does not implement:

1. **Dispatch** each item (or slice) to a standing agent
2. **Monitor** progress and handle exceptions
3. **Synthesize** results between dispatches

### Model Selection

`plugin/skills/orchestrate/references/dispatch-composition.md` §Model assignment
is the authoritative rule. In summary:

- **Type default:** `artisan` and `test-driver` dispatches run sonnet;
  `corrector` dispatches run opus, a tier above the implementers (D-32)
- **Artifact-type override (D-42):** opus for any dispatch editing
  `plugin/skills/`, `plugin/fragments/`, `plugin/agents/` or `docs/design.md`
- **Per-item override:** a `Model:` line on the runbook item overrides both

### Pre-Delegation Checkpoint

Before invoking Agent tool, verify:
- Model matches stated plan (sonnet/opus)
- If changing model, state reason explicitly

### Prompt Composition

The dispatcher composes each prompt per `plugin/skills/orchestrate/references/dispatch-composition.md`: item text inline, design and recall artifact by path. The dispatched agent is a standing one (`edify:artisan`, `edify:test-driver`, `edify:corrector`, `edify:refactor`) — no agents are generated per plan.

### Quiet Execution Pattern

Execution agents report to files, not to orchestrator context.

1. Specify output file path in task prompt
2. Agent writes detailed output to that file
3. Agent returns ONLY: filepath (success) or error message (failure)
4. Use second agent to read report and provide summary if needed

**Output locations:**
- Plan execution: `plans/[plan-name]/reports/`
- Research deliverables: `plans/reports/` — persistent, tracked
- Execution logs, scratch: project-local `tmp/` — ephemeral, gitignored

### Delegate Resume

When a delegate is interrupted, stopped, or returns incomplete results — resume before relaunching.

- Give the agent an explicit `name` at spawn; resuming is `SendMessage` to that name
- **Resume if:** Agent has context for its own issues (dirty tree, incomplete work, lint failures)
- **Fresh launch if:** The resume fails, or the resumed agent returns without making progress on what it was asked to fix

**No message-count cutoff.** Earlier guidance said "skip resume if the agent exchanged >15 messages". The orchestrator cannot observe another agent's message count — no tool reports it — so that rule was unactionable. Resume once; a resumed agent that fails to progress is the observable signal to launch fresh.

**Why:** Stopped agents retain expensive context (files read, reasoning done). Relaunching repeats that work.

### Task Agent Tool Usage

Remind task agents to use specialized tools where they exist:
- **Read** not `cat`/`head`/`tail`
- **Write** not `echo >`, **Edit** not `sed`/`awk`

**Search is the exception.** On native macOS/Linux builds (CC 2.1.117 onward)
there are no `Grep` or `Glob` tools — they are replaced by search embedded in
`Bash`. Windows and npm-installed builds keep them, and `--tools Grep,Glob`
restores them on native builds (CC 2.1.162), so treat their presence as
build-dependent rather than assumed either way.

Search therefore goes through `Bash`: `rg` for content, `rg --files` or `ls`
for discovery. An agent with no `Bash` in its `tools:` list has no search
capability at all on a native build, and must be dispatched with explicit file
paths.

### Recall Artifacts For Sub-Agents

One artifact model: `plans/<job>/recall-artifact.md` — grouped entries with relevance notes, curated by the dispatching skill. The dispatch prompt hands the sub-agent that path, and the sub-agent Reads the artifact then Reads every file it lists. `plugin/skills/orchestrate/references/dispatch-composition.md` §Prompt contents is the authoritative rule. The per-type flat artifacts an earlier model kept for sub-agent injection no longer exist.

**Selection is the parent's job.** A sub-agent has no parent context and cannot judge which entries are relevant, so it resolves all of them. The dispatching skill narrows the artifact to what the work needs; the child does not re-select.

### Multi-Step Verification

**Anti-pattern:** Splitting post-dispatch verification into separate tool calls. First check (git status) returns clean → exit momentum suppresses second check (just lint). The sub-agent "already linted" rationalization makes the skip feel safe.

**Correct pattern:** Single compound command (`git status --porcelain && just lint`). Compound commands can't be partially executed — both run or neither.

### Recall Content In Delegation Prompts

**Reference recall artifact file paths. Do not inline resolved recall content in delegation prompts.** Caller pre-resolving entries and pasting content into the reviewer's prompt is token-wasteful (content duplicated across parent and child context) and potentially stale.

**Correct pattern:** Pass the recall artifact path. Reviewer Reads the listed files itself. Same principle as sub-agent recall: parent curates artifact, child resolves.
