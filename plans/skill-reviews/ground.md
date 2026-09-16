# plugin-dev:skill-reviewer on plugin/skills/ground (2026-09-16)

Saved by the calling session (the reviewer has no Write tool). Line cites are the
reviewer's and are unverified here. **Partial — remainder requested; report was cut
mid-sentence inside Major finding 4.**

Files: `SKILL.md` (82 lines, 586 words), `references/grounding-criteria.md` (126
lines, 892 words). SKILL.md links no fragment, which the reviewer counts as Major 5;
it read `delegation.md` and `token-economy.md` as the two whose content the skill
restates or should route to.

Reviewer's summary: no critical findings, six major, eight minor. Procedure and
progressive-disclosure shape are sound; the defects are stale tool naming, a
mandatory rule stranded in the reference, and an output-path convention that
diverges from every artifact the repo has produced.

## Major

**1. The dispatch tool is named wrongly, and the wrong name collides with a real,
different feature.** SKILL.md:35, :39, :40, :43 say "Task agent"; the tool is
`Agent`, and the `Task*` tools are the unrelated background-task feature. The same
correction is already recorded at `plugin/fragments/escalation-acceptance.md:50`,
and the skill's own `allowed-tools` (SKILL.md:8) lists `Agent`, so the body
contradicts its frontmatter. Every other skill says "Agent tool"
(`design/references/write-design.md:27`, `inline/references/review-dispatch-template.md:7`,
`design/references/write-outline.md:79`). An agent reading "parallel Task agents"
has `TaskStop` and `TaskOutput` visible and may reach for them.

**2. The mandatory process-skill rule lives only in the reference, and SKILL.md
frames the reference as optional.** `grounding-criteria.md:86` says the internal
codebase branch **must** include git history mining alongside file inspection, and
:98 gives a hard selector: process skill → codebase scope with git history mining
plus session log scraping. Neither appears in SKILL.md; Phase 1 says only "consult
`references/grounding-criteria.md` for guidance" (:27), and Phase 2's codebase
bullet (:39) describes plain file inspection. Grounding process skills is ground's
most common use in this repo, so the common path loses the mandatory step.

**3. The reference carries two scope selectors with no stated precedence.**
`grounding-criteria.md:47` selects by question shape (descriptive → codebase,
generative → conceptual); :98 selects by topic class (process skill → codebase). A
generative question about a process skill satisfies both with opposite answers.
SKILL.md:28 reproduces only the first, so the conflict is invisible from the body.

**4. The prescribed output path breaks the convention every real artifact follows,
and drops the report out of its protective glob.** SKILL.md:69 writes to
`plans/reports/<topic>.md`, but every grounding output in the repo uses a
`-grounding.md` suffix (seventeen of them in `plans/reports/`). The memory file
`memory/feedback-grounding-reports-are-reusable.md` identifies non-deletable research
artifacts by exactly that glob (`plans/reports/*-grounding.md`, `*-external-research.md`,
`*-internal-codebase.md`), so a report at `<topic>.md` falls outside all three and
becomes a deletion candidate at the next purge. The branch artifact paths
(SKILL.md:39, :40, :49) do match; only the synthesis path does not.

**5. SKILL.md:51 names the quiet execution pattern without a path to its definition.**
"Both agents write reports and return filepath only (quiet execution pattern)" — the
pattern is defined at `plugin/fragments/delegation.md:30-42`, including the four-step
contract and the output-location table that independently confirms `plans/reports/`.
Every other skill leaning on a fragment names the path (`orchestrate/SKILL.md:201`,
`review/SKILL.md:206`, `inline/SKILL.md:108`). The shared conventions call the
output-file contract load-bearing.

**6. The reference asserts an unsourced superlative inside the document that forbids
them.** `grounding-criteria.md:88` says git history "is the highest-signal internal
source for process grounding" with no evidence or comparison — the exact shape
:14 classifies as a methodological claim requiring grounding, and what the No
Confabulation rule prohibits. It is load-bearing: it is the sole justification for
the mandatory mining step in finding 2. The sentence that follows it stands on its
own without the ranking claim.

## Minor

**7. The description's closing sentence is mechanics** (SKILL.md:7, "Parallel
diverge-converge research preventing confabulated structures"), which the house
standard says to cut; descriptions are injected at session start in every repo where
the plugin is enabled.

**8. The description has no exclusion clause, though the reference defines one**
(`grounding-criteria.md:21-26` lists four cases where grounding is not required), so
the skill cannot suppress itself. `recall`'s description does this correctly.
Trading the mechanics sentence for an exclusion clause is token-neutral.

**9. The bare token "ground" is a weak trigger** (SKILL.md:4). The word is common in
unrelated technical English ("ground truth" in the memory index; "grounds" as
justification in `docs/design.md`). The `/ground` command path is unaffected; the
risk is auto-invocation. The other four triggers are specific.

**10. "design a methodology" overlaps the `design` skill's trigger surface**
(SKILL.md:5 vs design's "architecture or implementation planning requests"), with
nothing saying which wins.

**11. Phase 4's required-sections list contradicts the reference on label placement**:
SKILL.md:71-76 lists the grounding-quality label third of four;
`grounding-criteria.md:39` says to attach it at the top, immediately after the title.

**12. The session-scraper invocation is not runnable as written.**
`grounding-criteria.md:96` shows `edify list | extract <prefix> | collect`, but these
are three independent Click subcommands (`src/edify/cli.py:56`, `:69`, `:86`);
`extract` takes a `session_prefix` argument and does not read stdin, so the pipeline
fails. The prose after the backticks spells out the correct forms. The same
non-runnable form appears in `CLAUDE.md`.

**13. `agents/learnings.md` is cited as an internal source but is self-declared
stale** (`grounding-criteria.md:94`): 195 lines against its own 80-line soft limit,
with a consolidation instruction pointing at `/codify`, a skill recorded as deleted.

**14. The internal-source list predates the memory migration and omits
`memory/MEMORY.md`** (`grounding-criteria.md:90-96`), which CLAUDE.md identifies as
the live recall surface. Two indexed entries are directly on topic for a Branch A
dispatch. `ground` also has no recall checkpoint anywhere in SKILL.md, unlike the
pipeline skills routing through `edify:recall`.

## Notes that are not findings

- **Search templates hardcode a year window** (`grounding-criteria.md:72`). Current
  as of 2026-09-16 but rots silently; :80 already instructs refinement, so relative
  phrasing would keep the intent.
- **Provenance sentence points at a departed skill** (SKILL.md:14, "proven during
  prioritization skill creation"). Only the plan directory survives. Historically
  true, costs one line.
- **`WebSearch` and `WebFetch` are unused by the body** — both research branches are
  delegated (SKILL.md:39-43). `allowed-tools` grants rather than restricts, so this
  only misdescribes the skill.
- **Branch A's two-bullet layout could read as two dispatches** (SKILL.md:35, :38).
  One sentence naming the selection would remove the ambiguity.
- **`subagent_type: general-purpose` skips a purpose-built agent.** `edify:scout`
  (`plugin/agents/scout.md:3-6`) targets exactly Branch A's codebase case, but
  defaults to haiku (below the skill's sonnet floor) with tools `Read, Bash, Write`.
  Branch B genuinely needs `general-purpose` for web access. Worth a deliberate call.
- **Model guidance in the body is legitimate here**: ground is the dispatcher and
  sets `model` as an `Agent` parameter, which it can enforce. The house rule targets
  a skill declaring its own tier.
- **The ❌/✅ markers are a minority convention** (SKILL.md:64-65); the house form is
  `**Anti-pattern:**` / `**Correct pattern:**`. Cosmetic.
- **The reference's foundation line has no inline links** (`grounding-criteria.md:5`)
  while :34 requires citation links for a Strong label. It routes to
  `plans/reports/ground-skill-research-synthesis.md`, which the reviewer confirmed
  carries real URLs for all three frameworks.

## Verified clean

No imperative-form violations (a word-boundary grep for you/your/yours returns
nothing); the one non-imperative construction is the passive at SKILL.md:77, same
shape at :51. Size and progressive disclosure are correct: 82 lines, 586 words, four
phases, one reference routed at four decision points (:27, :45, :59, :60) plus a
References section at :81. `plans/reports/` is the right directory per
`delegation.md:41`; only the suffix is wrong. Every path the reference cites exists.
Frontmatter is valid and matches the bundle, and the absent `continuation` block
matches the other standalone skills. The description opens with what the skill does.
The dispatch contract names an output file at :39, :40, :49 and requires a
filepath-only return at :51.

## Suggested fix order

1. Findings 1 and 4 — mechanical, clearest consequences: replace "Task agent" with
   "Agent tool" at four sites; change SKILL.md:69 to
   `plans/reports/<topic>-grounding.md`.
2. Finding 2 — a sentence in Phase 2's codebase bullet naming git history and session
   scraping, plus hardening SKILL.md:27 from "consult for guidance" to a directive.
3. Finding 3 — a precedence sentence in `grounding-criteria.md`; an author judgement.
4. Findings 7 and 8 — one description rewrite swapping the mechanics tail for an
   exclusion clause.
