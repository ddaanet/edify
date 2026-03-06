# Agentic Programming Retrospective

## Requirements

### Functional Requirements

**FR-1: Git history evolution tracing**
For each of the five topics, extract the chronological evolution from git history:
- `git log -S` for key terms to find introduction commits
- `git show` of decision files at key commits to capture state at each evolution point
- `git log --follow` on files that were renamed/moved during evolution
- Output: dated event log per topic with commit hashes and brief context

Acceptance criteria: Each topic has a timeline of dated commits showing when key decisions were introduced, modified, or superseded.

**FR-2: Session log scraping for pivotal conversations**
Using the existing session-scraper prototype (`plans/prototypes/session-scraper.py`), identify sessions where topic-relevant decisions were made:
- Use `scan` to inventory available sessions
- Use `correlate` to link sessions to git commits identified in FR-1
- Use `parse` + `tree` to extract conversation segments around pivotal moments (failures discovered, design breakthroughs, RCA findings)
- Output: curated session excerpts with context annotations

Acceptance criteria: Each topic has 3-8 key session excerpts showing the actual conversation where a failure was discovered or a design decision was made.

**FR-3: Five topic evolution narratives**
Produce raw materials organized by topic:

1. **Memory system evolution** — remember rule → memory-index → `/when` + `/how` → recall skill → forced injection hooks. Key inflection: 4.1% metacognitive activation rate.
2. **Pushback protocol** — ambient anti-sycophancy → structured agreement tracking → stress-testing → d: mode grounding gates. Key inflection: prose rules getting rationalized past.
3. **Deliverable-review origins** — statusline-parity failure cascade (385 tests pass, 8 visual issues remain) → ISO 25010 / IEEE 1012 grounded review taxonomy.
4. **Ground skill origins** — confabulated prioritization scoring → diverge-converge external research → WSJF grounding → self-application (circular dependency insight).
5. **Structural enforcement / gating** — prose instructions skipped under momentum → D+B tool-call anchoring → recall gates → PreToolUse hooks. The meta-pattern connecting topics 1-4.

Acceptance criteria: Each topic has a structured evidence bundle containing git timeline, session excerpts, and decision file snapshots at key evolution points.

**FR-4: Cross-topic connection mapping**
Identify and document where topics intersect:
- Which commits/sessions touch multiple topics
- Shared failure patterns that drove evolution across topics
- Chronological co-evolution (what was happening in parallel)

Acceptance criteria: A cross-reference document showing topic intersections with commit/session evidence.

### Non-Functional Requirements

**NFR-1: Evidence-grounded**
Every claim in the raw materials must link to a specific commit hash, session ID, or decision file version. No reconstructed narratives from memory.

**NFR-2: Blog-ready excerpts**
Session excerpts should be trimmed to the relevant exchange (not full session dumps) with enough context to be readable standalone.

### Constraints

**C-1: Use existing session-scraper prototype**
Build on `plans/prototypes/session-scraper.py` for session analysis. If extensions are needed, they require a separate `/requirements` pass before modification.

**C-2: Output to plans/retrospective/reports/**
All raw materials written to the plan's reports directory as markdown files.

### Out of Scope

- Writing the actual blog posts — this produces raw materials only
- Promoting session-scraper prototype to CLI — separate concern
- Renaming D+B gates — pending task on main ("Prose gate terminology"), upstream dependency but not a blocker for evidence gathering
- Quantitative analysis (token costs, session durations) — different kind of retrospective

### Dependencies

- Session JSONL logs accessible at `~/.claude/projects/` — ~980 sessions across ~130 project directories (validated Feb 4, 2026 onward)
- Git history from Dec 16, 2025 (initial commit) — full evolution, not shallow clone
- Session-scraper prototype must handle cross-project scanning (sessions span main project + ~90 worktree project directories, each a separate `~/.claude/projects/` entry)

### References

- `plans/prototypes/session-scraper.py` — existing 4-stage scraping pipeline (scan/parse/tree/correlate)
- `plans/prototypes/explore-sessions.py` — session format exploration script
- `plans/retrospective/recall-artifact.md` — recall entries informing these requirements
- `agents/decisions/workflow-advanced.md` — memory system and recall pattern decisions
- `agents/decisions/defense-in-depth.md` — quality gate and D+B pattern decisions
- `agents/decisions/deliverable-review.md` — review taxonomy and origins
- `agents/decisions/workflow-optimization.md` — ground skill and methodology decisions

### Data Landscape

Session logs span ~130 project directories under `~/.claude/projects/`. Each worktree gets its own project directory (e.g., `-Users-david-code-claudeutils-wt-pushback`). The project directory names encode the evolution timeline — worktree names reflect the feature being built. Key topic-relevant project directories:

- `memory-index-recall` (16 sessions, Feb 10) — memory system design
- `when-recall` (24 sessions, Feb 13) — /when + /how implementation
- `recall-tool-anchoring` (12 sessions, Feb 25) — gate anchoring with tool calls
- `active-recall-system` (13 sessions, Mar 4) — forced injection via hooks
- `pushback` (29 sessions, from wt-pushback) — pushback protocol
- `parity-failures` (7 sessions, Feb 7) — statusline cascade (deliverable-review origin)
- `quality-infra-reform` (13 sessions, Feb 23) — defense-in-depth
- `design-grounding-update` (11 sessions, Feb 27) — ground skill redesign
- `userpromptsubmit-topic` (7 sessions, Feb 28) + `ups-topic-injection` (8 sessions, Mar 1) — topic injection (keyword matching attempt)

Git history covers Dec 16, 2025 – present. Session logs cover Feb 4, 2026 – present. The Dec–Jan gap is pre-topic (project setup, oneshot/TDD workflow) — git history alone suffices for "before" state.
