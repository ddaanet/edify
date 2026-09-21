# Project configuration

Decisions about the platform this project runs on and the conventions it
follows: rules files, sub-agent capabilities, agent frontmatter, naming, line
caps and the script-versus-agent split. Read this before changing `.claude/`
configuration, an agent's frontmatter, or a checking script.

Part of the `docs/design.md` graph; conclusions are indexed in
`docs/decisions.md`.

**D-67 — `.claude/rules/` with `paths` frontmatter injects domain context.**
Documentation-only enforcement through tables in always-loaded context relies on
model attention and is unreliable; hooks cannot detect skill-loading state
because they see tool inputs, not conversation context. Rules files are passive
reminders, not enforcement — models can ignore them — but they beat
always-loaded bloat. Rules fire in the main session only; sub-agents never
receive them, so domain context must be carried explicitly into a delegation
prompt.

**D-68 — `CLAUDE.md` is the project-root marker for scripts.** Not `agents/`:
subdirectories carry their own `agents/` folders (`plugin/agents/`), so a script
walking upward stops at the wrong level.

**D-69 — A file's line cap is picked from its path, enforced by precommit.** 400
lines for a Python module and for prose, 200 for a `SKILL.md` hub, which is paid
on every invocation while a reference node is opt-in. Review effectiveness drops
faster than linearly past ~400 LOC — reviews under 300 lines get architectural
feedback, past 600 only style comments
([Baldawa 2024](https://rishi.baldawa.com/posts/pr-throughput/cognitive-load-cliff/));
the AI-assisted sweet spot is 150-500 lines
([Faherty 2025](https://medium.com/@eamonn.faherty_58176/right-sizing-your-python-files-the-150-500-line-sweet-spot-for-ai-code-editors-340d550dcea4));
PyLint's default of 1000 is too permissive for an agent's context. The limit
provides backpressure against slop.

The check covers prose as well as Python — `plugin/`, `docs/` and the root
`*.md`, the frozen `docs/superpowers/` trees excluded. A count is honest only
once a hard-wrapping formatter has run, so `just precommit` runs a non-fixing
`rumdl fmt --check` (MD013, reflow at 80 columns) ahead of the guard. Files
already over their cap are carried in an allowlist sidecar recording each one's
ceiling and the job that retires it: still reported, failing only above the
ceiling, which ratchets down only. That ratchet is what makes the check
enforceable from the day it lands — a hard gate is red on its first run, and a
warn-only gate never turns red at all.

The sidecar's entry format is argued only where it is implemented — the header
comment of `scripts/check_line_limits.sh`, restated in the sidecar's own header:
one `<path><TAB><ceiling><TAB><note>` per line, the path root-relative and
matched exactly, no globbing and no basename comparison. A carriage return
anywhere in an entry is a failure to run (exit 2), not a silently unmatched
path, because a CRLF sidecar would make every entry miss while the gate still
reported success.

When a file hits the limit, look for code-quality improvements first — redundant
calls, dead code, extraction candidates. Compressing user-facing output strings
or splitting to a new file to satisfy the counter degrades output clarity or
module cohesion without addressing the cause. Splitting a module by functional
responsibility is mechanical, so `refactor` (sonnet) may do it without opus
escalation. Runbook planning should project file growth and insert split points
rather than react per slice.

**D-70 — Fix the design problem a lint rule points at.** "No hardcoded exception
messages" answered by `msg = "..."; raise ValueError(msg)` preserves the real
problem — using `ValueError` for a domain error — while removing the signal.
"Function too long" is answered by extracting helpers, not compressing strings.

**D-71 — Agents compose behavior through `skills:` frontmatter.** Wrapping
shared guidance as a skill and referencing it from an agent definition injects
the content as prompt with no build step, so it stays current automatically.

**D-72 — What a sub-agent actually gets (measured 2026-08-10).** Sub-agents
receive `CLAUDE.md` and `memory/MEMORY.md` natively, under the same
`Contents of <path>` label the main session gets. They have the `Skill` tool,
are given the full skill listing, and resolve project-local plugin skills as
well as marketplace ones. They can spawn sub-agents through `Agent` — there is
no `Task` tool at any level.

What they lack is the automatic memory *fetch*: recall does not run below the
main session, so a body arrives only if the agent Reads it. Never instruct an
agent to Read the index — it already has it; instruct it to Read the files the
index names.

Hooks do not fire in sub-agents. Nested spawning is asynchronous and its result
does not reach the parent: the tool result is a launch acknowledgement, and the
grandchild's completion surfaces in the main session while the parent goes idle.
Never design a sub-agent to consume a grandchild's return value. `Agent`
parameters are `description`, `prompt`, `subagent_type`, `name`, `model`,
`isolation` — no `max_turns`, no `run_in_background`, no `resume`. Resumption is
`SendMessage` addressed to the agent's `name`, which is why naming at spawn time
matters.

**D-73 — Agent frontmatter uses block scalars for descriptions with examples.**
YAML parsers treat unindented content after `description:` as a new field, and
invalid YAML prevents agent registration. `description: |` makes the examples
part of the value.

**D-74 — Names are chosen for discoverability first.** The word a user thinks of
when they need the capability should be the handle: "I need to ground this" →
`/ground`, not `/found`. Then recall — short common words beat etymologically
precise ones. Thematic alignment is nice and never worth a discoverability cost.
Check CLI built-ins before naming a skill (`/help`, `/plan`, `/review`,
`/model`, `/clear`, `/compact`).

**D-75 — Title-words beat kebab-case for identifiers in prose.** Measured
kebab-case at +31% drift penalty against title-words at +17% when agents get
verbose; hyphens often tokenize separately while spaces do not add overhead.

**D-76 — Script the deterministic, delegate the cognitive.** If a solution is
non-cognitive — deterministic, pattern-based — script it and auto-fix. Reserve
agent invocations for design, review and ambiguous decisions. A script that
validates metadata presence while expecting an agent to generate it has the
split backwards: deterministic standard metadata gets injected during assembly.

**D-77 — Delegate for exploration you have not done, not for context you already
hold.** If the files are already in context, executing directly beats delegating
to an agent that re-reads everything. Assess complexity once — an entry-point
skill that triages and then routes to a planning skill that re-assesses under
different labels is pure duplication.

## Rejected alternatives

**Pruning the memory index on a size limit** — rejected in favour of append-only
growth. Each entry is a keyword-rich discovery surface, consolidation into
domain summaries kills keyword matching, and soft limits get treated as hard
caps and provoke aggressive pruning. (Superseded in mechanism: gitlore now owns
the memory store, and its index budget is a real loader cutoff rather than a
soft limit, so retiring and relocating entries is a periodic pass —
`/gitlore:index-audit` — rather than a rejected idea.)

**Skill-description optimization for this project** — matters only where
automatic triggering operates. Every skill here is invoked explicitly, so
descriptions serve as documentation.
