## Scope

**Design reference:** `docs/superpowers/specs/2026-08-11-edify-recall-skill-design.md` (FR1-FR9, D1-D7)

**Affected files:**

1. `plugin/skills/recall/SKILL.md` — new
2. `plugin/skills/requirements/SKILL.md`
3. `plugin/skills/design/SKILL.md`
4. `plugin/skills/orchestrate/SKILL.md`
5. `plugin/skills/review-plan/SKILL.md`
6. `plugin/agents/corrector.md`
7. `plugin/agents/design-corrector.md`
8. `plugin/agents/outline-corrector.md`
9. `plugin/agents/runbook-outline-corrector.md`
10. `plugin/skills/proof/SKILL.md`
11. `plugin/bin/prepare-runbook.py`
12. `CLAUDE.md`
13. `plugin/README.md`

**Changes:**

1. **`plugin/skills/recall/SKILL.md`** (new) — body is FR1-FR9 and the
   Procedure section of the design spec, transcribed as the skill's
   frontmatter + instructions: `allowed-tools: Read, Bash`,
   `user-invocable: true`, description per D3 (names the edify pipeline so
   the picker resolves against `gitlore:recall`). Procedure: establish topic
   (FR2) → treat index as in-context, never Read (FR3) → degrade to
   `rg --files memory/` only where structurally absent (FR4) → corpus is the
   memory store named in this session's own auto-memory context, not a fixed
   path (FR5) → select at most 5, certainty-gated (FR6) → batch-Read in one
   message (FR7) → writes nothing (FR8).

2. **`plugin/skills/requirements/SKILL.md`** — under `## Recall Pass` →
   `### Process` (currently the paragraph starting "The memory index
   `memory/MEMORY.md` is already in your context..." through "Re-read the
   index only if it was edited this session or a compaction dropped it."):
   replace with an invocation, `Skill(skill: "edify:recall", args:
   "<topic derived from job name and conversation>")`. Keep the "Gate anchor"
   and "Boundaries" bullets that follow — those govern the recall *artifact*
   write (D1 plan plumbing), not the process being replaced. Also, in
   `### Recall Artifact` → `**Format:**` code block, drop the
   `agents/decisions/<name>.md — <1-line relevance note>` example line (keep
   the `memory/<name>.md` line). Also convert `### Post-Explore Recall Gate`:
   replace its "Discovery via `rg --files`/`rg`... Re-scan the in-context
   index..." procedure paragraph with `Skill(skill: "edify:recall")` (no
   topic — FR2's trigger-based branch). Keep the "Gate anchor" bullets ("New
   entries found: Read the matching files, then add their paths to the recall
   artifact" / "No new entries: state that explicitly") unchanged — the
   artifact write stays a caller responsibility per D1.

3. **`plugin/skills/design/SKILL.md`** (this file) — under `#### Triage
   Recall (D+B anchor)`: drop the lead sentence "Load triage-relevant
   decisions before classifying..." and the paragraph "The memory index
   `memory/MEMORY.md` is already in your context... plus any
   `agents/decisions/*.md` covering the task's domain." Keep the
   `Read plans/<job>/recall-artifact.md` code block and its first bullet
   unchanged (D1 plumbing). In the "No artifact" bullet, replace "the anchor
   is the Read of the files you selected from the index" with "the anchor is
   invoking `Skill(skill: "edify:recall", args: "<topic>")`" — keep the
   trailing "If nothing matches, state that explicitly" sentence.

4. **`plugin/skills/orchestrate/SKILL.md`** — in the §3.5 Phase Boundary
   corrector-dispatch prompt template, the `**Review recall:**` line: keep
   the first sentence (Read `recall-artifact.md` when present), replace "If
   absent: the `memory/MEMORY.md` index is already in your context (do not
   Read it) — identify review-relevant entries and Read the matching
   `memory/*.md` and `agents/decisions/*.md` files." with "If absent: invoke
   `Skill(skill: "edify:recall", args: "<topic derived from phase scope>")`."

5. **`plugin/skills/review-plan/SKILL.md`** — under `## Recall Context`,
   item 3 ("If the artifact is absent: do lightweight recall..."): replace
   with "invoke `Skill(skill: "edify:recall", args: "<topic covering
   quality patterns, failure modes, testing conventions>")`." Items 1-2
   unchanged.

6. **`plugin/agents/corrector.md`** — under `### 1.5. Load Recall Context`,
   the "If the artifact is absent" sentence: replace with "invoke
   `Skill(skill: "edify:recall", args: "<topic covering quality patterns,
   failure modes>")`." Keep the "Derive job name" bullet and the "When the
   artifact exists" sentence unchanged.

7. **`plugin/agents/design-corrector.md`** — under `### 1.5. Load Recall
   Context`, same edit as corrector.md (topic: architectural conventions,
   quality patterns).

8. **`plugin/agents/outline-corrector.md`** — under `### 2. Load Context`,
   item 4 (single-line "If the artifact is absent: do lightweight recall...
   Read the matching `memory/*.md` and `agents/decisions/*.md` files."):
   same edit, folded into the existing single line.

9. **`plugin/agents/runbook-outline-corrector.md`** — under `### 2. Load
   Context`, item 4: same edit as outline-corrector.md.

10. **`plugin/skills/proof/SKILL.md`** — under `### Item Iteration`, rewrite
    the `**Per-item recall (FR-3):**` line: replace its inline procedure with
    an invocation, `Skill(skill: "edify:recall", args: "<topic>")` (D4 — keep
    per-item recall; the original justification for deleting it was
    circular, since the mature `proof` sibling that lacks it was itself
    produced by stripping memory content from a copy of this same skill).

11. **`plugin/bin/prepare-runbook.py`** — `resolve_recall_entries` docstring,
    first line: "Read the memory and decision files named in the recall
    artifact." → "Read the memory files named in the recall artifact." No
    code change — `resolve_recall_entries` resolves whatever repo-relative
    paths the artifact names, so dropping a corpus needs no logic change.

12. **`CLAUDE.md`** — `## Skills` → Standalone list: append `recall` —
    "`proof`, `ground`, `deliverable-review`, `formalize`" →
    "`proof`, `ground`, `deliverable-review`, `formalize`, `recall`".

13. **`plugin/README.md`** — Skills → Standalone table: add a row
    `| /recall | Select and Read relevant memory-index entries for the
    current task or a given topic |`.

## Boundaries

**IN:**
- Creating `plugin/skills/recall/SKILL.md`
- Swapping the inlined recall paragraph for an `edify:recall` invocation in
  the 4 skills + 4 agents listed above (items 2-9)
- Converting `plugin/skills/requirements/SKILL.md`'s
  `### Post-Explore Recall Gate` to invoke `edify:recall` (no topic —
  trigger-based)
- The 4 peripheral edits: proof directive rewired to invoke `edify:recall`
  (not deleted), prepare-runbook.py docstring, requirements artifact-format
  example line, CLAUDE.md/README listing

**OUT:**
- Any change to `agents/decisions/*.md` content itself — D6 only removes the
  recall skill's *dependency* on that corpus; folding those files into a
  living design doc is separate, already-tracked work.
- Exercising the revived `design → runbook → orchestrate` pipeline
  end-to-end — per the design's own §7 Verification, that would confound
  this build's result with the pipeline's.
- Consolidating `memory/MEMORY.md`'s over-budget size — pre-existing,
  unrelated, separately tracked.

## Dependencies

- Every call-site edit depends on `plugin/skills/recall/SKILL.md` existing
  first (item 1 before items 2-9).
- No cross-file ordering dependency among items 2-13 beyond that — each is
  an independent, self-contained edit.
