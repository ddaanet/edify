# Plugin Transition — Evaluation

Written 2026-07-15 as an evaluation of five directives: retire hooks, sort out
fragments, adopt `claude-plugin-dev` for release, evaluate merging the `plugin`
submodule into the parent, and reassess `token-efficient-bash`.

**Trimmed 2026-09-21.** Four of the five were executed and are recorded in the
living design; their sections are gone from here rather than kept as a second,
ageing copy:

- **The merge** — done. `plugin/` is a subdirectory, argued as D-10 in
  `docs/references/cli-and-package.md` with the `git add`-inside-a-submodule
  defect that forced it, and dated in
  `docs/changelog/2026-07-16-plugin-de-submoduled.md`. The marketplace
  `git-subdir` route, and the entry that now uses it, are in
  `docs/marketplace.md`; the version-consistency invariant survived the merge
  and `plugin/bin/check-version-consistency.py` still enforces it.
- **Hooks** — `pretooluse-block-tmp.sh` and `posttooluse-autoformat.sh` are
  gone; `plugin/hooks/hooks.json` now registers only the venv bootstrap (D-11).
  The tmp policy they enforced was rewritten rather than relocated and lives in
  `CLAUDE.md` §Temporary Files, which points at the harness scratchpad and a
  project-local `tmp/`. The dangling `plugin/.claude/agents` symlink is deleted.
- **Fragments** — the rule set was inlined into `CLAUDE.md` prose, the third
  option §4 floated, and `memory/operational-rules.md` is retired. The eight
  files left in `plugin/fragments/` are pipeline references, not the behavioural
  rules this section was about.
- **`token-efficient-bash`** — deleted. The `|| true` exception was reworded to
  name the condition rather than the skill, as §5 required, and now reads in
  `CLAUDE.md` §Error Handling: legitimate only where a non-zero exit
  *encodes a result* rather than a failure.

What follows is what is still open, or is recorded nowhere else.

## Release mechanism — recorded

Closed 2026-09-21. The directive to adopt `claude-plugin-dev` for release was
resolved in favour of keeping edify's own `scripts/release.sh`, and the choice
now has a home: **D-87** in `docs/references/cli-and-package.md`, with its three
rejected options — extending the toolkit, un-hybridising edify, and adopting the
toolkit over its own stated exclusion — in that node's rejected-alternatives
section. The node carries the toolkit's two exclusion statements, the structural
gaps, and the reopen gate.

Two claims from the 2026-07-15 measurement did not survive re-checking and are
deliberately absent from D-87: submodule handling stopped being a need when D-10
flattened `plugin/`, and the marketplace side effect stopped being a
differentiator once edify's own `scripts/release.sh` grew the same
`MARKETPLACE_DIR` requirement and the same synthesize-an-entry-if-absent branch.
The dry-run and rollback gaps are real but are the toolkit's own framing of the
exclusion rather than edify's requirement — edify has neither, and offers
`--resume` instead.

## Incidental staleness still live

The 2026-07-15 sweep found thirteen stale sites. Ten have since been fixed or
deleted with the subsystems they named. Three survive:

- `plugin/bin/bump-plugin-version.py:36-52` rewrites `EDIFY_VERSION` in
  `hooks/sessionstart-health.sh`, deleted in the teardown. Guarded by
  `if health_sh.exists()`, so the block silently no-ops and its `sys.exit(1)` is
  unreachable — dead code that reads as live release machinery.
- `plugin/.claude/settings.json` sets `"plansDirectory": "plans/"`; the parent
  `.claude/settings.json` sets `"plans/claude/"`.
- `agents/learnings.md:5` routes consolidation through `/codify`, a deleted
  skill. Its destinations are current (`CLAUDE.md`, `docs/references/` plus the
  `docs/decisions.md` line); the command that performs the move is not.
