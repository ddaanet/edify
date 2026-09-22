# Proposal for `../claude-plugins` — edify README section and marketplace description

Written 2026-09-22 from the edify repo. `claude-plugins` is another repository:
this is a proposal, not an edit.

## 1. `README.md` §edify, "Pipeline" bullet (lines 214–216)

Current:

```markdown
- **Pipeline** — `/requirements` → `/design` → `/runbook` → `/orchestrate`
  (or `/inline` for work that needs no runbook), with `/review` as the
  in-progress quality gate.
```

Proposed — `/orchestrate` and `/inline` merged into `/build` on 2026-09-17
(edify `docs/changelog/`):

```markdown
- **Pipeline** — `/requirements` → `/design` → `/runbook` → `/build` (or
  `/design` → `/build` for work that needs no runbook), with `/review` as the
  in-progress quality gate.
```

## 2. `.claude-plugin/marketplace.json`, `edify` entry `description`

Current: `"A lean bundle of framework-agnostic Claude Code skills"`.

Source of truth is `plugin/.claude-plugin/plugin.json` in edify, now:
`"A lean bundle of Claude Code skills and agents built around a requirements →
design → runbook → build planning pipeline"`.

No hand edit needed if the next edify release runs after
`scripts/release.sh` gained description sync for an existing entry (edify
`plans/open-items-sweep/reports/code-batch.md`); the release recipe will
rewrite it. Edit by hand only if a release is not imminent.
