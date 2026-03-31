# Post 1: "The Rule That Changes the Rules"

## Opening Hook

September 30, 2025. A file called `rules.md` in a git repo. 14 rules in flat markdown: "Commit changes regularly with descriptive messages." "Write fully typed code." Nothing you couldn't find in any style guide.

Six months later: CLAUDE.md with @-references to 27 behavioral fragments, 33 skills the agent invokes as slash commands, 13 sub-agents dispatched for isolated execution, a memory system spanning session handoffs and codified decisions, and a pipeline that routes work through complexity triage → design → planning → orchestration → review. One person, 16 repos.

This is a blog series about what happened in between and what it actually taught me about working with AI coding agents.

## Core Argument

### The Zero State

Two projects before any agent instructions: calendar-cli (Apr 2025, 11 commits — informal paragraphs, no build system) and celebtwin (May–Jul 2025, 256 commits — Claude-assisted with CI and linting, but nothing telling Claude how to behave). Claude helped write code; nothing shaped Claude's behavior.

The gap: Claude Desktop → Claude Code, and the realization that behavioral rules stored in the repo would persist across sessions. (Commit `7b0a4b4`, rules repo, Sep 30, 2025)

### The Template Era

The first AGENTS.md was a template that got copied between projects. rules → emojipack → tuick → jobsearch → box-api. Each project adapted the template — emojipack added TDD rules (`#tdd Follow TDD: Red-Green-Commit-Refactor-Commit`), tuick accumulated 42 agentic commits over three months, box-api introduced agent-vs-human command separation.

Cross-pollination was manual. Commit `791a962` (box-api, Nov 23): "Flesh out AGENTS.md (incorporate relevant rules for tuick)." Copy, adapt, commit. The AGENTS.md files diverged across projects over weeks.

### The naming wasn't settled

Four different migration patterns between AGENTS.md and CLAUDE.md across repos:

| Pattern | Repo | What happened |
|---------|------|---------------|
| Rename | home | `091073f` (Jan 18): "Rename AGENTS.md→CLAUDE.md" |
| Coexistence | tuick | CLAUDE.md as overlay on AGENTS.md |
| Reverse merge | jobsearch | CLAUDE.md merged INTO AGENTS.md (Oct 2025) |
| Replacement | ddaanet | Auto-generated CLAUDE.md replaced by AGENTS.md (Jan 2026) |

Trial and error converging on platform conventions. Not deliberate architecture.

### Dead Ends

tuick, the most-iterated repo (18 AGENTS.md commits), tried "cognitive protocols" — structured metacognition rules — on December 12. Three days later, removed: "Remove epistemic standards" (commit `26c3b5d`). Same day add-and-remove. oklch-theme (started with Gemini, iterated in Claude Desktop) tried "LLM Limitation Awareness" — asking the agent to "flag uncertainty when multi-step reasoning exceeds 3 steps." Both are metacognitive wishful thinking: asking an LLM to monitor confidence it doesn't have.

Not all experimentation survives. The repo history contains the failures alongside the successes.

### The Architectural Leap

home (Jan 12-13, 2026) introduced in two days:
- File organization table separating behavioral direction, session context, design rationale, and artifacts
- Orchestrator constraints: opus operates read-only, delegates all source edits
- Commit delegation protocol (7 commits iterating in one day — each describing what was wrong with the previous version)

Then plugin extraction (Jan 15): shared recipes, configs, fragments, agents across projects. By March, new projects include plugin in their initial commit. Adoption cost approaches zero.

### What Remember Actually Is

The concept behind the (now-deprecated) remember skill: the agent identifies a behavioral pattern, formulates it as a constraint ("Do not" over "avoid"), places it in the right file, and verifies it's actionable. CLAUDE.md isn't a static readme — it's a living spec the agent reads and writes.

This is the foundational concept for the entire series. Every subsequent post describes what happens when you treat LLM behavior as programmable: what the programs can and can't do, how to verify they work, and where the model breaks down.

### The Frame

It's still programming. Process flow, data flow, debugging, verification — the discipline of programming didn't change. The interface changed from syntax to natural language. The conversational fluency is new; the discipline is not.

## Evidence Chain

| Claim | Evidence |
|-------|----------|
| First agent instructions: 14 rules, flat markdown | rules `7b0a4b4` (Sep 30, 2025) |
| Renamed to AGENTS.md two days later | rules `eacf188` (Oct 2, 2025) |
| Template copied across projects | emojipack, tuick, box-api AGENTS.md content similarity |
| Cross-pollination was manual | box-api `791a962`: "incorporate relevant rules for tuick" |
| Cognitive protocols: added and removed in 3 days | tuick `a3e15a1` (Dec 12), `26c3b5d` (Dec 15) |
| oklch-theme: started Gemini, iterated Claude Desktop | oklch-theme `64cbf8f`, AGENTS.md references "Gemini agent" |
| home: architectural leap in 2 days | home commits Jan 12-13 |
| Agent-core extraction | pytest-md/plugin `5783aef` (Jan 15) |
| Zero-cost adoption by March | devddaanet: plugin from initial commit (Mar 5) |
| Four AGENTS.md/CLAUDE.md migration patterns | home `091073f`, tuick coexistence, jobsearch `eec32b4`, ddaanet replacement |

## Transition to Post 2

The rule that changes the rules is: behavior is programmable. But programmable doesn't mean reliable. The next post covers what happens when the agent produces output that looks authoritative, sounds structured, and is entirely fabricated.
