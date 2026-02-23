# Remember Skill Update

## Requirements

### Functional Requirements

**FR-1: Titles use When/How prefix**
Every learning title in `agents/learnings.md` must start with "When" or "How to" — matching the decision file heading convention and `/when`/`/how` operator format.

Acceptance criteria:
- Title starts with `## When ` or `## How to `
- Title reads naturally as a trigger: `/when <rest of title>` or `/how <rest of title>`
- Title describes the **situation an agent encounters**, not root cause or jargon

Examples from existing decision files:
- `### When Placing Deliverable Artifacts`
- `### When Launching Task Agents In Parallel`
- `### How to End Workflow With Handoff And Commit`

**FR-2: Titles comply with validation rules**
Titles must pass existing learnings.py validation and be compatible with planned validation:

- Max 5 words (enforced, includes "When"/"How to")
- Unique (enforced)
- Min 2 words (planned — Workstream 1 Phase 1)
- ~~No special characters beyond alphanumeric + spaces~~ **Resolved:** hyphens allowed (memory-index already uses hyphens in 30+ triggers; SKILL.md "no hyphens" was unenforced and contradicted by practice). Special character restriction dropped from scope.

**FR-3: Structural validation enforced at precommit**
learnings.py updated with:
- Min 2 words check
- When/How prefix check
- Existing checks preserved (max 5 words, uniqueness, H2 format)

**FR-4: Consolidation pipeline is mechanical**
Consolidation pipeline: `## When X` → `### When X` (decision heading, title case) → `/when x` (index trigger, lowercased). No agent rephrasing step. Remember skill Step 4a updated to derive triggers directly from title.

**FR-5: Semantic guidance in skill and handoff docs**
Update remember SKILL.md and handoff skill with:
- Title must start with "When" or "How to"
- Anti-pattern/correct-pattern examples
- Reject jargon/root-cause titles with suggested rephrase

**FR-6: Frozen-domain recall analysis**
Evaluate alternatives to rule files for proactive knowledge recall:
- Options: status quo, PreToolUse hook, inline code comments, UserPromptSubmit topic detection
- Criteria: agent-independence, token cost, false positive rate, maintenance burden
- Output: analysis with recommendation (not implementation)

~~**FR-7: Migrate existing learning titles**~~
**Resolved — already done.** All 54 current titles already use `When` prefix format. No migration needed.

### Constraints

**C-1: Title IS the trigger — no rephrasing during consolidation**
The learning title must be directly usable as a memory-index trigger without agent judgment at consolidation time.

**C-2: Word count includes prefix**
"When" and "How to" count toward the 5-word max. Effective content words: 4 (for When) or 3 (for How to).

~~**C-3: Migration preserves body content**~~
**Resolved — FR-7 already done.** No migration needed.

**FR-8: Inline execution in clean session — remove remember-task delegation**
The `/remember` skill executes consolidation inline in the calling session rather than delegating to `remember-task` agent. Requires a clean session (fresh start) to keep context manageable — CLAUDE.md + files being edited, not accumulated conversation history. Delegation throws away loaded context and adds agent startup overhead; inline execution in a bloated session is equally wrong.

Acceptance criteria:
- `/remember` skill steps 1-5 execute in the calling session without Task tool delegation
- Invocation requires clean session (skill documents this as a prerequisite)
- `remember-task` agent is deleted
- Handoff skill consolidation step invokes `/remember` skill inline (no agent)

**FR-9: Inline file splitting — remove memory-refactor delegation**
When a target documentation file exceeds 400 lines during consolidation, the skill splits it inline before proceeding. No delegation to `memory-refactor` agent.

Acceptance criteria:
- After each Write/Edit to a decision file, check line count
- If >400 lines: split by H2/H3 boundaries into 100-300 line sections inline
- Run `validate-memory-index.py --fix` after split
- `memory-refactor` agent is deleted

**FR-10: Rename skill to `/codify`**
Rename `/remember` skill to `/codify`. Update all references (~30 files): skill directory, SKILL.md, agent definitions, handoff skill + references, session.md, memory-index triggers, agent-core docs, plan files. Requires restart after rename.

Acceptance criteria:
- Skill directory renamed `remember` → `codify`
- All references updated across codebase
- `just sync-to-parent` run, symlinks verified
- Restart required flag noted

**FR-11: Agent routing for learnings**
When consolidating learnings actionable for sub-agents, route to agent templates as additional consolidation targets. All agents are eligible except plan-specific agents (generated per-runbook).

Acceptance criteria:
- Consolidation pipeline identifies agent-relevant learnings
- Relevant entries propagated to matching agent files

**FR-12: Recall CLI simplification**
Replace two-argument call convention (`when-resolve.py when <query>`) with one-argument-by-recall syntax (`when-resolve.py "when <query>"`). Add batched recall support.

Acceptance criteria:
- Operator parsed from query string prefix (when/how)
- Batched recall: `when-resolve.py "when X" "how Y" "when Z"`
- `/when` and `/how` skill docs updated with new invocation syntax
- Backward compatibility not required (agents are sole callers)

**FR-13: Remove memory-index from always-loaded context**
Remove `@agents/memory-index.md` reference from CLAUDE.md. ~5000 tokens for 2.9% recall rate.

Acceptance criteria:
- `@agents/memory-index.md` removed from CLAUDE.md
- `agents/memory-index.md` file remains (used by when-resolve.py)
- `/when` and `/how` skills continue to work via CLI resolution

### Out of Scope

- Memory index validation pipeline changes
- Hook implementation for frozen-domain (separate task if recommended by FR-6)
- `agent-core/bin/compress-key.py` changes

### Dependencies

- Phase 1 (validation) should precede Phase 2 (documentation) — docs reference validation constraints
- Phase 3 depends on Phase 2 (routing targets defined after pipeline simplification)
- Phase 4 is independent (CLI fix)
- Phase 5 depends on Phase 2-3 (rename after content changes settle)
- Phase 6 is independent (frozen-domain analysis)

### Open Questions

~~Q-1: Hyphen handling~~ **Resolved:** allow hyphens. Memory-index already uses hyphens in 30+ triggers.
