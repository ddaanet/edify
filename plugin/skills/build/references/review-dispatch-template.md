# Review Dispatch Template

Prompt template for reviewer delegation from `/build` §6. Reviewer selection
happens upstream (§6 routing logic) — this template structures the prompt for
the selected reviewer.

Two variants. Use §Template for a fix-capable reviewer, §Report-only variant
for a reviewer that can neither write nor edit.

## Template

Delegate to selected reviewer agent (Agent tool, `subagent_type` per routing table):

```
Review implementation changes against design specification.

**Baseline:** <baseline commit hash>

**Changed files:** `git diff --name-only <baseline commit hash>`

**Requirements:**
<FR/NFR items relevant to this execution, from outline or design>

**Scope:**
- IN: <implementation targets from design>
- OUT: <explicitly excluded from design scope>

**Design reference:** plans/<job>/outline.md (or design.md if present)

**Recall context:** `Skill(skill: "edify:recall", args: "plans/<job> — quality patterns, failure modes for this scope")`

**Review criteria:**
- Implementation matches design decisions
- Scope completeness: every Scope IN item has a corresponding deliverable (not just components/decisions — standalone scope items too)
- Test quality (if behavioral code): behavior-focused, meaningful assertions
- Code quality: clarity, patterns, no duplication
- Integration: consistency with existing patterns

Fix all issues (critical, major, minor). Write report to: plans/<job>/reports/review-<group>.md

Return filepath on success, or "UNFIXABLE: [description]" on failure.
```

## Report-only variant

For a reviewer that has no Write, Edit or Bash tool — `plugin-dev:skill-reviewer`
holds **Read, Grep and Glob, and nothing else**. Its prompt is the §Template
body with the closing three lines and the recall line replaced by:

```
**Return your findings in parts.** A reply is cut at roughly 4000 characters.
Split the report into parts under that size. End every part but the last with
the line `CONTINUED`, and end the last part with the line `END OF REPORT`.
Without the end marker a truncated report reads as a complete one.

**Recall context:** Read `plans/<job>/recall-artifact.md` and Read each file
it lists — that is all the recall available to you.

Do not apply fixes and do not write a file — you have neither tool. Report
every issue (critical, major, minor) with its file, its location and the
change you would make. Mark a blocker "UNFIXABLE: [description]".
```

The **calling session** then writes the returned findings to
`plans/<job>/reports/review-<group>.md` and applies the fixes itself. The
structural-proof Read in `/build` §6 then finds a file that exists, so the
gate stops blocking on skill-definition groups.

## Field Rules

- **Baseline:** substitute the hash itself, read back from `tmp/build-baseline` (written at `/build` §2 by `git rev-parse HEAD` before edits) — the reviewer's shell is not the dispatcher's, so no variable survives into the prompt. The baseline is taken after the entry gate has confirmed a clean tree, so it excludes design-phase artifacts unconditionally: whatever `/design` produced is already committed, and only execution edits are in the diff it defines.
- **Design context:** Always `outline.md` or `design.md` — never `requirements.md`. Requirements are upstream abstractions; design/outline contains the implementation-level decisions the reviewer needs.
- **Recall context:** Pass the plan directory only. The reviewer resolves entries itself — do not pre-resolve and paste recall content into the prompt. Token economy: reference, never repeat. A report-only reviewer (`plugin-dev:skill-reviewer`) has **Read, Grep and Glob only** — no Write, no Edit, no Bash, no `Skill` — so it takes the §Report-only variant, which resolves recall by path and moves writing and fixing to the caller. `Grep` and `Glob` are its search tools; a prompt instructing it to run `rg` fails.
- **Report path:** one rule — `plans/<job>/reports/review-<group>.md`, `<group>` being the artifact group §6 routed. The structural proof reads the path actually dispatched, so the prompt and the proof must name the same file.
- **Scope IN/OUT:** From design or outline, not invented. Prevents reviewer from flagging work explicitly deferred.
- **Scope completeness:** Reviewer must mechanically diff every Scope IN item against deliverables. Design scope items that aren't mapped to named components are the gap — component+decision validation alone misses standalone scope items (e.g., planstate specified in Scope IN but not part of any C1-C4 component).
- **Constraint:** This template is for implementation changes only. Planning artifacts route by artifact per `docs/design.md` §6.4 D-26: `design.md` → `edify:design-corrector`, `outline.md` → `edify:outline-corrector`, `runbook.md` → `edify:runbook-corrector`. `runbook-corrector` rejects anything that is not `runbook.md`.

## Example: Skill Creation Task

```
Review implementation changes against design specification.

**Baseline:** abc1234

**Changed files:** `git diff --name-only abc1234`

**Requirements:**
- FR-8: One execution skill covering runbook and runbook-less work
- FR-10: Runbook execution lifecycle
- FR-11: Runbook-less execution lifecycle

**Scope:**
- IN: plugin/skills/build/SKILL.md, references/tdd-slice.md, references/resuming.md, references/dispatch-composition.md, references/review-dispatch-template.md, scripts/verify-step.sh
- OUT: the reference sweep across /design, /runbook and the fragments; `docs/design.md`; `memory/MEMORY.md`

**Design reference:** plans/build-skill/outline.md

**Recall context:** `Skill(skill: "edify:recall", args: "plans/build-skill — quality patterns, failure modes for this scope")`

**Review criteria:**
- Implementation matches design decisions
- Scope completeness: every Scope IN item has a corresponding deliverable
- Skill structure follows D+B convention (tool call anchors per phase)
- Delegation protocol complete and accurate

Fix all issues. Write report to: plans/build-skill/reports/review-skill.md

Return filepath on success, or "UNFIXABLE: [description]" on failure.
```
