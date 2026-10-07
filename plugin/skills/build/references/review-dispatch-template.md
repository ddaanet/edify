# Review Dispatch Template

Prompt template for reviewer delegation from `finishing.md` §1. Reviewer
selection happens upstream (`finishing.md` §1 routing) — this template
structures the prompt for the selected reviewer.

Two variants. Use §Template for a fix-capable reviewer, §Report-only variant for
a reviewer that can neither write nor edit.

## Template

Delegate to selected reviewer agent (Agent tool, `subagent_type` per routing
table):

```
Review implementation changes against design specification.

**Baseline:** <baseline commit hash>

**Changed files:**
- <one line per file in this artifact group — its share of `finishing.md` §1 step 1's list>

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
- <agent-definition group only: the `plugin-dev:agent-development` criteria — frontmatter validity, trigger description quality, tool access minimality, system-prompt structure; where `plugin-dev` is not installed, review against the existing agent definitions and say so in the report>
- <design-graph group only: the `craft:design-doc-writing` criteria — graph structure, hub/node agreement, decision records; where `craft` is not installed, say so in the report>

**Constraints:**
- Do NOT flag items outside the provided scope (Scope OUT above)

Fix all issues (critical, major, minor). Write report to: <report path, per `dispatch-composition.md` §Prompt contents>

<return contract, per `dispatch-composition.md` §Prompt contents, plus the UNFIXABLE marking as §Example words it>
```

## Report-only variant

For a reviewer that has no Write, Edit or Bash tool —
`plugin-dev:skill-reviewer` holds **Read, Grep and Glob, and nothing else**. Its
prompt is the §Template body with the closing three lines and the recall line
replaced by:

```
**Return your findings in parts.** A reply is cut at roughly 4000 characters.
Split the report into parts under that size. End every part but the last with
the line `CONTINUED`, and end the last part with the line `END OF REPORT`.
Without the end marker a truncated report reads as a complete one.

**Recall context:** Read `plans/<job>/recall-artifact.md` and Read each file
it lists — that is all the recall available to you.

Do not apply fixes and do not write a file — you have neither tool. Report
every issue (critical, major, minor) with its file, its location and the
change you would make.

Mark an issue that has no fix path "UNFIXABLE" with its subcategory code:
U-REQ (requirements ambiguous or in conflict), U-ARCH (the fix would break an
architectural invariant or a documented design decision) or U-DESIGN (several
valid approaches with non-trivial downstream consequences). Follow it with an
investigation summary of the three gates you checked — Scope OUT, design
deferral, codebase patterns — and your conclusion. An issue in Scope OUT or
deferred by the design is DEFERRED, not UNFIXABLE.

If you cannot review at all, reply `blocked: <reason>` instead of findings.
```

The **calling session** then collects the parts (`dispatch-composition.md`
§Prompt contents item 5), writes them to the group's report path (§Field Rules)
and applies the fixes itself. The structural-proof Read in `finishing.md` §1
then finds a file that exists, so the gate stops blocking on skill-definition
groups. An UNFIXABLE that fails validation there goes back to this reviewer,
`review-<group>`, resumed by `SendMessage` for reclassification; its reply comes
in parts as before, and the session rewrites the report from it. A
`blocked: <reason>` reply carries no findings and leaves no report for the
structural proof to Read: STOP and report the reason to the user, as
`references/escalation.md` §Escalation's "Unexpected result" bullet does.

## Field Rules

- **Baseline:** substitute the hash itself — the `BASE:` that
  `plugin/skills/build/scripts/changed-files.sh <job>` prints, the one
  `finishing.md` §1 step 1 took. The reviewer's shell is not the dispatcher's,
  so no variable survives into the prompt. That base is the parent of the run's
  first item-report commit, so whatever `/design` produced and committed before
  execution lies outside the diff it defines.
- **Design context:** Always `outline.md` or `design.md` — never
  `requirements.md`. Requirements are upstream abstractions; design/outline
  contains the implementation-level decisions the reviewer needs.
- **Recall context:** Pass the plan directory only. The reviewer resolves
  entries itself — do not pre-resolve and paste recall content into the prompt.
  Token economy: reference, never repeat. A report-only reviewer
  (`plugin-dev:skill-reviewer`) has **Read, Grep and Glob only** — no Write, no
  Edit, no Bash, no `Skill` — so it takes the §Report-only variant, which
  resolves recall by path and moves writing and fixing to the caller. `Grep` and
  `Glob` are its search tools; a prompt instructing it to run `rg` fails.
- **Report path and return contract:** `dispatch-composition.md` §Prompt
  contents is the one rule for both, under the dispatch name `review-<group>`
  that `dispatch-composition.md` §Naming and resumption defines. The structural
  proof reads the path actually dispatched, so the prompt and the proof must
  name the same file.
- **Scope IN/OUT:** From design or outline, not invented. Prevents reviewer from
  flagging work explicitly deferred.
- **Scope completeness:** Reviewer must mechanically diff every Scope IN item
  against deliverables. Design scope items that aren't mapped to named
  components are the gap — component+decision validation alone misses standalone
  scope items (e.g., planstate specified in Scope IN but not part of any C1-C4
  component).
- **Constraints:** keep the template's scope-OUT bullet as written; add any
  constraint the design names.
- **Implementation only:** planning artifacts route as `finishing.md` §1 says,
  not through this template.

## Example: Skill Creation Task

The example shows the fix-capable §Template for a skill-definition group, which
is what that group takes when `plugin-dev` is not installed and the routing
table's skill row falls back to `edify:corrector`. With `plugin-dev` installed,
the group goes to `plugin-dev:skill-reviewer` with the §Report-only variant.

```
Review implementation changes against design specification.

**Baseline:** abc1234

**Changed files:**
- plugin/skills/build/SKILL.md
- plugin/skills/build/references/tdd-slice.md
- plugin/skills/build/references/escalation.md
- plugin/skills/build/references/dispatch-composition.md
- plugin/skills/build/references/review-dispatch-template.md

**Requirements:**
- FR-8: One execution skill covering runbook and runbook-less work
- FR-10: Runbook execution lifecycle
- FR-11: Runbook-less execution lifecycle

**Scope:**
- IN: plugin/skills/build/SKILL.md, references/tdd-slice.md, references/escalation.md, references/dispatch-composition.md, references/review-dispatch-template.md, scripts/verify-step.sh
- OUT: the reference sweep across /design, /runbook and the fragments; `docs/design.md`; `memory/MEMORY.md`

**Design reference:** plans/build-skill/outline.md

**Recall context:** `Skill(skill: "edify:recall", args: "plans/build-skill — quality patterns, failure modes for this scope")`

**Review criteria:**
- Implementation matches design decisions
- Scope completeness: every Scope IN item has a corresponding deliverable
- Skill structure follows D+B convention (tool call anchors per phase)
- Delegation protocol complete and accurate

**Constraints:**
- Do NOT flag items outside the provided scope (Scope OUT above)

Fix all issues. Write report to: plans/build-skill/reports/review-skill.md

Return the report path on success, or `blocked: <reason>`. Inside the report,
mark an issue that has no fix path "UNFIXABLE" with its subcategory code:
U-REQ (requirements ambiguous or in conflict), U-ARCH (the fix would break an
architectural invariant or a documented design decision) or U-DESIGN (several
valid approaches with non-trivial downstream consequences). Follow it with an
investigation summary of the three gates you checked — Scope OUT, design
deferral, codebase patterns — and your conclusion. An issue in Scope OUT or
deferred by the design is DEFERRED, not UNFIXABLE.
```
