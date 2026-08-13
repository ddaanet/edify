# Review: edify:recall skill + 5 call-site rewires

Baseline: `ce4d03d4`. Scope: `plugin/skills/recall/SKILL.md` (new) and the
rewired paragraphs in `requirements`, `design`, `orchestrate`, `review-plan`,
`proof` SKILL.md files. Agents, `agents/decisions/*.md`, `prepare-runbook.py`,
`CLAUDE.md`, `plugin/README.md` out of scope (reviewed separately).

## Verdict

New skill correctly implements FR1-FR8. All 6 call-site edits replace the old
inlined procedure with an `edify:recall` invocation, no leftover procedure
text. One real defect found: **two of the five rewired skills invoke the
`Skill` tool without declaring it in `allowed-tools`.**

## Findings

### Critical — `Skill` tool not declared in two rewired skills' frontmatter

- `plugin/skills/requirements/SKILL.md` frontmatter: `allowed-tools: Read,
  Write, Bash, AskUserQuestion` — no `Skill`. Body now calls
  `Skill(skill: "edify:recall", args: ...)` twice (Recall Pass process,
  Post-Explore Recall Gate).
- `plugin/skills/proof/SKILL.md` frontmatter: `allowed-tools: Read, Write,
  Edit, Bash, Agent, AskUserQuestion` — no `Skill`. Body now calls
  `Skill(skill: "edify:recall", args: "<topic>")` per item (line 100).

By contrast `design/SKILL.md` already listed `Skill` in `allowed-tools`
pre-change (unrelated prior use), and `orchestrate`/`review-plan` declare no
`allowed-tools` at all (unrestricted), so they're unaffected. `requirements`
and `proof` are the two skills whose rewire introduces a `Skill` tool call
that their own frontmatter does not authorize. Add `Skill` to both
`allowed-tools` lists.

## FR-by-FR check of `plugin/skills/recall/SKILL.md`

- **FR1** — met. Single skill owns select-then-Read; explicitly disclaims
  artifact ownership ("callers... own that artifact themselves").
- **FR2** — met. Step 1: invocation arg is topic; absent arg → select
  against "what the conversation is actually doing," explicitly "not a
  literal string."
- **FR3** — met. Step 2: "injected at session start and is never Read."
- **FR4** — met. Step 2 degrade clause: `rg --files memory/` at project
  root, keyed on "structurally absent" (feature off / no store configured),
  matching the design doc's phrasing almost verbatim.
- **FR5** — met. Step 3 resolves corpus from "this session's own context,"
  not a fixed path, names `memory/` as this project's resolution, includes
  tier subdirectories, excludes everything else.
- **FR6** — met. Step 4: cap 5, certainty-gated ("unsure means exclude"),
  empty selection legitimate, thematic match not keyword overlap, no
  re-selecting a body already pulled this conversation.
- **FR7** — met. Step 5: "Issue every selected Read in a single message."
- **FR8** — met. Step 6 + intro: skill writes nothing, caller owns the
  artifact.
- **D2** (subagent non-invocation) — carried into the skill body almost
  verbatim: "A subagent that lacks the index should not invoke this skill."
- **D3** (picker distinguishability from `gitlore:recall`) — description
  leads with "for the edify pipeline" in the first sentence and triggers on
  "a pipeline skill or agent reaches its recall checkpoint" — distinct from
  `gitlore:recall`'s "half-recognise but cannot act on" framing. Adequate.
- **Frontmatter** — `allowed-tools: Read, Bash`, `user-invocable: true`,
  matches the design doc's Procedure section exactly and the convention used
  by `proof`/`ground` (name/description/allowed-tools/user-invocable shape).

## Call-site rewires (FR9, D4, D6)

All five sites replace their inlined index-selection paragraph with an
`edify:recall` invocation; no old procedure text survives:

- `requirements/SKILL.md`: Recall Pass process paragraph → `Invoke
  Skill(skill: "edify:recall", args: "<topic derived from job name and
  conversation>")`. Post-Explore Recall Gate → `Skill(skill: "edify:recall")`
  (no-topic form, correct per FR2's trigger-based branch). Artifact format
  example dropped the `agents/decisions/<name>.md` line.
- `design/SKILL.md`: Triage Recall's inline "load triage-relevant decisions
  … Read those bodies, plus any `agents/decisions/*.md`" paragraph deleted
  outright; the no-artifact branch now reads "the anchor is invoking
  `Skill(skill: "edify:recall", args: "<topic>")`."
- `orchestrate/SKILL.md`: the corrector-dispatch template's "Review recall"
  line's if-absent branch → `Skill(skill: "edify:recall", args: "<topic
  derived from phase scope>")`, replacing the old "index is already in your
  context … `memory/*.md` and `agents/decisions/*.md`" text.
- `review-plan/SKILL.md`: item 3 (artifact-absent branch) →
  `Skill(skill: "edify:recall", args: "<topic covering quality patterns,
  failure modes, testing conventions>")`.
- `proof/SKILL.md`: "Per-item recall (FR-3)" line → `invoke Skill(skill:
  "edify:recall", args: "<topic>")`, per D4.

## D6 — `agents/decisions/*.md` out of the recall corpus

Grepped all six files for `agents/decisions`. Three residual hits, all
unrelated to recall (confirmed by reading context, not just grep):

- `design/SKILL.md:98` — artifact-destination table entry for
  "investigation" output paths (`plans/reports/`, `agents/decisions/`), not
  a recall corpus reference.
- `design/SKILL.md:167` — Author-Corrector Coupling step, references
  `agents/decisions/pipeline-contracts.md` for the T1-T6.5 transformation
  table, not recall.
- `review-plan/SKILL.md:291` — Model Assignment Review advisory check,
  flags edits to `agents/decisions/workflow-*.md` needing opus, not recall.

No `agents/decisions` reference remains inside any recall-related paragraph
in the six files. D6 satisfied for this scope.

## Consistency across call sites

Topic-argument phrasing is uniform: every site uses `Skill(skill:
"edify:recall", args: "<topic ...>")` with a bracketed description of what
the topic should cover, except the two intentional no-topic invocations
(`review-plan`... actually all sites but the Post-Explore Recall Gate supply
a topic). No site left a residual `memory/MEMORY.md`-inline-index
paragraph — grep for `MEMORY.md` / `do not Read` / `already in your context`
across all six files returns zero matches outside `recall/SKILL.md` itself.
