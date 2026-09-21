# Verification of `plans/skill-reviews/ground.md` — 2026-09-21

Checked against the working tree: `plugin/skills/ground/SKILL.md` (107 lines)
and `plugin/skills/ground/references/grounding-criteria.md` (160 lines). Neither
file is modified in today's working tree, so HEAD and the tree agree here.

Review tally: 0 critical, 6 major, 8 minor = 14 findings. My table carries 14.

| ID | Sev | Status | Evidence |
|---|---|---|---|
| 1 | Major | open-mechanical | SKILL.md:42 "Execute two branches as parallel **Task agents**"; same at :46, :50, :55. `allowed-tools` (:8) still lists `Agent`. |
| 2 | Major | open-mechanical | SKILL.md:32 still "consult `references/grounding-criteria.md` for guidance"; :46-49 codebase bullet says only "Surface existing codebase patterns"; the mandatory rule is still only at grounding-criteria.md:94-96, :122-126. |
| 3 | Major | open-design | grounding-criteria.md:52 (question shape) and :122 (topic class) still select scope with no stated precedence. |
| 4 | Major | open-mechanical | SKILL.md:91 still `plans/reports/<topic>.md`; `ls plans/reports` shows 31 files on the `-grounding.md` / `-external-research.md` / `-internal-codebase.md` pattern, and memory/feedback-grounding-reports-are-reusable.md:19-20 keys the non-deletable set to exactly those three globs. |
| 5 | Major | open-mechanical | SKILL.md:66 "Both agents write reports and return filepath only (quiet execution pattern)" — no path; the definition is `plugin/fragments/delegation.md` §Quiet Execution Pattern (:39-51). |
| 6 | Major | open-mechanical | grounding-criteria.md:100-101 still "This is the highest-signal internal source for process grounding", unsourced, inside the doc whose :16-21 classifies that shape as needing grounding. |
| 7 | Minor | open-mechanical | SKILL.md:7 still closes "Parallel diverge-converge research preventing confabulated structures." |
| 8 | Minor | open-design | Description (:3-7) still has no exclusion clause; grounding-criteria.md:25-30 defines four. Pairs with 7 — one rewrite, but what to exclude is an authoring call. |
| 9 | Minor | disputed | SKILL.md:5 lists `"ground"` among five triggers. The claim that a bare common word auto-fires is not grounded in any measurement of description matching; the reviewers offer none. Ungrounded — needs validation before acting. |
| 10 | Minor | open-design | SKILL.md:5-6 still carries "design a methodology"; design/SKILL.md:7 still "planning requests". Which wins is a routing decision. |
| 11 | Minor | open-mechanical | SKILL.md:94-99 lists the grounding label third of four required sections; grounding-criteria.md:43-44 says "Attach at the top of the output document, immediately after the title." |
| 12 | Minor | open-mechanical | grounding-criteria.md:115 still shows `edify list \| extract <prefix> \| collect`; `src/edify/cli.py:56,:69,:86` are three independent `@cli.command`s and `extract` takes `session_prefix` as an argument (`:70`), not stdin. |
| 13 | Minor | open-design | grounding-criteria.md:110 still cites `agents/learnings.md`; that file is 195 lines against its own "Soft limit: 80 lines" (:5) and still routes consolidation to `/codify`, which no longer exists. |
| 14 | Minor | open-mechanical | grounding-criteria.md:104-120 still omits `memory/MEMORY.md`; `ground/SKILL.md` still has no `edify:recall` checkpoint (no `Skill(` call anywhere in it). |

## Cross-file links

- Finding 12 is the same defect as the `CLAUDE.md` copy the reviewer noted; the
  project `CLAUDE.md` line is outside this skill and outside this sweep.
- Finding 5 is the same class as recall M3 and deliverable-review M6: a skill
  leaning on a fragment without naming its path.

## Exact edits for `open-mechanical`

### `plugin/skills/ground/SKILL.md`

Finding 1, four sites:

- :42 `Execute two branches as parallel Task agents. Launch both in a single message.`
  → `Execute two branches as parallel Agent dispatches. Launch both in a single message.`
- :46 `- **Codebase scope:** Delegate to a Task agent (subagent_type: general-purpose,`
  → `- **Codebase scope:** Delegate via the Agent tool (subagent_type: general-purpose,`
- :50 `- **Conceptual scope:** Delegate to Task agent (subagent_type: general-purpose,`
  → `- **Conceptual scope:** Delegate via the Agent tool (subagent_type: general-purpose,`
- :55 `**Branch B — External research:** Delegate to Task agent (subagent_type:`
  → `**Branch B — External research:** Delegate via the Agent tool (subagent_type:`

Finding 2, :32 and the codebase bullet:

- :32 `- Select parameters (consult `references/grounding-criteria.md` for guidance):`
  → `- Select parameters — Read `references/grounding-criteria.md` and select by it:`
- :47 `  Surface existing codebase patterns, prior decisions, current`
  → `  Surface existing codebase patterns, prior decisions, current` (unchanged)
  and append after :48 `  Write to ...`:
  `  Where the topic is a process skill, grounding-criteria.md §Process Skill`
  `  Internal Sources binds: git history mining and session-log scraping are`
  `  required alongside file inspection.`

Finding 4, :91:

- `Write the grounded reference document to `plans/reports/<topic>.md` (persistent,`
  → `Write the grounded reference document to `plans/reports/<topic>-grounding.md`
  (persistent,`

Finding 5, :66:

- `Both agents write reports and return filepath only (quiet execution pattern).`
  → `Both agents write reports and return filepath only — the quiet execution
  pattern at `plugin/fragments/delegation.md` §Quiet Execution Pattern.`

Finding 7, :7:

- `  practices". Parallel diverge-converge research preventing confabulated structures.`
  → `  practices".`
  (Finding 8 would replace it with an exclusion clause; that wording is the
  open-design half.)

Finding 11, :94-99 — move the label to first position:

- reorder the `Required sections:` list so `Grounding quality label with evidence
  basis` is the first bullet, matching grounding-criteria.md:43-44.

### `plugin/skills/ground/references/grounding-criteria.md`

Finding 6, :100-101:

- `Git history surfaces what current files cannot: failure patterns, correction`
  `cycles, and behavioral deviations that motivated rule additions. This is the`
  `highest-signal internal source for process grounding — external frameworks`
  `describe how processes *should* work, git history documents how *this* process`
  `actually fails.`
  → drop the ranking clause:
  `Git history surfaces what current files cannot: failure patterns, correction`
  `cycles, and behavioral deviations that motivated rule additions. External`
  `frameworks describe how processes *should* work; git history documents how`
  `*this* process actually fails.`

Finding 12, :115:

- `- Session scraper (`edify list | extract <prefix> | collect`) — mine session`
  → `- Session scraper (`edify list`, then `edify extract <session-prefix>`, or
  `edify collect`) — mine session`

Finding 14, after :109 (`- `agents/learnings.md` ...`):

- insert `- `memory/MEMORY.md` and the memory files it indexes — the live recall
  surface; route through `edify:recall` rather than reading the index directly`
