# Edify — Living Design

Edify is a Claude Code plugin of working-discipline skills for an orchestrating
agent: how to release, how to review each commit, how to dispatch subagents, and
two small tools for agent-written files. Everything it ships is prose or a
standard-library script; there is no installed package, no daemon and no hook.
History is git's; this document states what is true now.

## 1. Functional requirements

- FR-1: A release cascade from `dev` onto `main` that runs the simplify pass,
  the parallel release reviews, triaged fixes and a medium loop until only low
  findings remain, then push, preflight and the release recipe (skill
  `release`).
- FR-2: A per-commit review loop: a delegated medium review of each commit that
  adds, changes or deletes content, triage of its findings, and fix commits
  reviewed the same way (skill `review`).
- FR-3: Rules for dispatching subagents: what the main thread keeps, agent
  boundaries and reuse, a model tier per task, self-contained prompts, naming,
  and collecting replies (skill `dispatch`).
- FR-4: Repair the recurring structural defects of agent-written markdown in
  place (skill `markdown`, script `bin/edify-markdown`).
- FR-5: Count the tokens of files with the Anthropic `count_tokens` endpoint
  (skill `token-counting`, script `bin/edify-count-tokens`).
- FR-6: Ground a claim with external research before asserting methodology
  (skill `ground`), and brainstorm names in a clean context (agent
  `brainstorm-name`).

## 2. Non-functional requirements

- NFR-1: Scripts use the Python standard library only, so a plugin install needs
  no virtual environment and no dependency resolution.
- NFR-2: A skill's `description` states the moment it applies and what it is not
  for; a skill hub stays small and moves reference material into `references/`
  nodes loaded on demand.
- NFR-3: A skill states rules and the reason each holds, and does not narrate a
  project's history.

## 3. Architecture

The plugin holds skills, one agent and two scripts, laid out at the repository
root: `.claude-plugin/plugin.json`, `skills/`, `agents/`, and `bin/` with the
`lib/` package the markdown fixer imports.

- Skill `release` is the release cascade. It owns the branch switches the
  cascade needs and the boundary between a release and ordinary work.
- Skill `review` is the per-commit loop. It states where a fix goes: back to the
  reviewer by message while that reviewer's context is under about 150k tokens,
  otherwise to a fresh agent; a release fix goes to fresh agents partitioned by
  file, since the release reviewers cannot take a fix. A review fix is its own
  commit, never an amend.
- Skill `dispatch` holds the dispatch rules, a decision table for model tiering,
  and `references/` nodes with facts about Claude Code's subagent and
  background-task behaviour (approval, nested spawning, handback of named
  agents, notification quirks, the absence of a duration cap on a background
  shell).
- Skill `markdown` names the moment (agent-produced markdown with keyword lists
  lacking bullets, mis-quoted backticks or fence markers) and runs
  `edify-markdown` by name (the plugin's `bin/` is on PATH) on the files just
  written. The script reads paths on stdin and rewrites in place.
- Skill `token-counting` documents `bin/edify-count-tokens`, which posts to the
  `count_tokens` endpoint and reads the key from the environment or
  `~/.config/edify/config.toml`.
- Skill `ground` and its `references/` carry the grounding criteria.
- Agent `brainstorm-name` delegates name brainstorming to a clean context to
  avoid anchoring.

## 4. Design decisions

- D-1: The plugin is a set of disciplines for the orchestrator, not a pipeline.
  A planning pipeline of staged skills and correctors cost more prose and
  dispatches than the work it governed, so it was removed whole; the rules that
  survived are the ones that change what an orchestrator does by default.
- D-2: Model tiering is a decision table in the `dispatch` skill, chosen by how
  much the task leaves open. Agents carry no `model:` frontmatter, because the
  right tier depends on the task, not on the agent that receives it.
- D-3: Dispatched agents return their report in the reply by default. A dispatch
  whose deliverable is itself a long document names an output file, because a
  reply is cut near 4000 characters. A reviewer with no `Write` tool returns its
  report in parts under that size with a fixed end marker.
- D-4: Scripts are single files with the standard library only; the token
  counter keeps no cache, since a count is one request and a stale count is
  worse than none.
- D-5: Skills that wrap a script name the moment and run the script by name, the
  plugin's `bin/` being on PATH; nothing runs implicitly.
- D-6: Facts about Claude Code's behaviour live in the skill that acts on them,
  as `references/` nodes written in the skill's voice, not as repository memory.

## 5. Rejected alternatives

- A `decide-model` script: tiering is a judgement about uncertainty, which a
  table states and a script cannot read from a task.
- `model:` in agent frontmatter: it binds a tier to the agent, so one task that
  needs a higher tier needs a second agent.
- Report files for every dispatch: they cost a write and a read per dispatch to
  carry what the reply already holds; D-3 keeps them for long documents.
- A dependency-bearing package for the scripts (`pydantic`, `icontract`,
  SQLAlchemy): the scripts do small, closed jobs and an environment bootstrap
  outweighs them (NFR-1).
- A token-count cache: not worth the schema and invalidation for a
  single-request count (D-4).
- A hook for the markdown fixer: it would rewrite files the agent has not
  finished writing; the skill names the moment instead (D-5).
- Keeping the staged requirements, design, runbook and build skills with their
  correctors: removed under D-1; its reasoning is in git history.
