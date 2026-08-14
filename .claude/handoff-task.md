## Current task

Folding `agents/decisions/*.md` into the living design doc. The content half is
done: `docs/design.md` holds all 23 files' surviving substance in the six-section
format (FR, NFR, architecture, decisions, rejected alternatives, changelog) plus
the state layer, and `docs/changelog.md` carries nine dated design-significant
entries. The source files are still on disk and every reference still points at
them.

What remains is mechanical and needs no knowledge of the corpus:

1. `git rm -r agents/decisions/`
2. Rewire every live reference.
   `grep -rn 'agents/decisions' --include='*.md' --include='*.py' . | grep -v
   '^./scratch/' | grep -v '^./plans/reports/'` finds them. Live sites:
   `CLAUDE.md:207`, `README.md:56`, `agents/README.md`, `agents/ROADMAP.md:11`,
   `agents/learnings.md:5`, the four `.claude/rules/*.md` files (cli-work,
   test-work, workflow-work, design-work — workflow-work points at
   `workflows.md`, which never existed), `plugin/skills/` (deliverable-review ×3
   plus example-report, review-plan, runbook SKILL plus 4 references, design
   SKILL plus design-content-rules ×3), `plugin/bin/prepare-runbook.py:13`,
   `plugin/bin/validate-runbook.py:30`, `plugin/fragments/review-requirement.md:48`
   and `claude-config-layout.md:86`, `plugin/docs/` (tdd-workflow,
   general-workflow ×4, @file-pattern ×3, migration-guide ×8), `plans/README.md`
   ×5, `docs/marketplace.md:17`, `memory/plugin-transition-eval.md:22`,
   `docs/superpowers/design/plugin-transition-evaluation.md:352`. Leave
   `plans/reports/*` and `docs/superpowers/specs/*` alone — historical records.
3. `plans/decision-drift-audit/` is superseded: the drift audit it planned was
   performed as part of the fold. Delete the plan directory.
4. `just precommit`.

`validate-runbook.py:30` needs judgment, not substitution: it matches
`agents/decisions/workflow-[^/]+\.md$` to force opus on edits to those files.
Repointing it at `docs/design.md` widens the rule from four workflow files to
the whole design doc.

## Open decisions

- Three axes of the fold were settled by stated default rather than by asking,
  because `AskUserQuestion` is refused in this session. Each is still open to
  veto and each would mean redoing only that axis: (a) one project-level doc at
  `docs/design.md`, leaving `docs/superpowers/design/` alone as per-subproject
  designs; (b) three-way triage of the rule-shaped content rather than folding
  it verbatim or dropping it; (c) cutting content about torn-down subsystems
  rather than tagging it for a later audit.
- Whether `Now` earns its place in the design-doc format. It overlaps
  `.claude/handoff-task.md`; the distinction drawn is lifetime (project-level and
  persistent vs per-session and transient) and the boundary is soft.