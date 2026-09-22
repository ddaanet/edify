# Changelog split — report

`docs/changelog.md` was at its 400-line cap. Followed `craft:design-doc-writing`
(specifically its `splitting-an-oversized-doc.md` node, which names the
`docs/changelog/<date>-<title>.md` shape for exactly this case): moved every
dated entry's body verbatim into its own file under `docs/changelog/`, and
reduced `docs/changelog.md` to an index of one bullet per entry (date, title,
link), newest first, in the file's existing order.

## Files created

20 files under `docs/changelog/`, one per dated entry, each an `# <date> —
<title>` heading followed by the entry's body verbatim (heading level bumped
from `##` to `#`, no wording changed):

- `2026-09-21-design-graph-crosslinks-checked-mechanically.md`
- `2026-09-21-tdd-audit-slice-scoped-green-mutation-proof-report-commits.md`
- `2026-09-21-recall-resolves-skills-stops-assuming-index-in-context.md`
- `2026-09-21-ruff-format-check-joins-precommit-gate.md`
- `2026-09-20-living-design-becomes-hub-index-eight-nodes.md`
- `2026-09-20-route-asks-whether-work-needs-runbook.md`
- `2026-09-17-one-routing-node-in-design-artifacts-record-base-commit.md`
- `2026-09-17-inline-and-orchestrate-merge-into-build-continuation-passing-retires.md`
- `2026-09-16-runbook-stops-naming-models.md`
- `2026-09-02-shared-ddaanet-conventions-load-design-record-sheds-situational-state.md`
- `2026-09-01-one-stage-runbook-replaces-two-stage-expansion-pipeline.md`
- `2026-08-14-decision-records-folded-into-one-living-design-doc.md`
- `2026-08-13-per-plan-generated-agents-retired.md`
- `2026-08-10-sub-agent-capability-claims-re-probed.md`
- `2026-08-04-pipeline-revived.md`
- `2026-07-17-bootstrap-reversed-from-stdlib-venv-to-uv.md`
- `2026-07-16-plugin-de-submoduled.md`
- `2026-05-teardown.md`
- `2026-02-pipeline-contracts-and-execution-tiers.md`
- `2026-01-weak-orchestrator-and-tdd-workflow.md`

`docs/changelog.md` itself: 400 lines → 52 lines, now the intro paragraph plus
one linked bullet per entry.

None of the moved entry bodies contained a markdown hyperlink (`](`) — every
cross-reference inside them is a backtick path or bare `D-<n>`/`FR-<n>`
citation, not a link — so no relative-link `../` adjustment was needed inside
the moved files (step 4). Every link in the new index resolves: checked each
`docs/changelog/*.md` target named in `docs/changelog.md` exists on disk (20/20
present).

## References updated

- `CLAUDE.md:314` — was "`docs/changelog.md` carries the dated
  design-significant entries." Now: "`docs/changelog.md` indexes the dated
  design-significant entries, one file per entry under `docs/changelog/`." —
  the old wording implied a single file holding the entries directly.

Checked and left unchanged (already accurate for an index/pointer, no claim
about internal file shape):

- `docs/design.md:339-343` (§10 Changelog) — points at `docs/changelog.md` as
  the design-significant-changes record; doesn't describe its internal shape.
- `docs/references/agent-instructions.md:46` — historical narrative about a
  changelog entry once being mis-dispatched, not about location/shape.
- `plugin/fragments/delegation.md:19` and
  `plugin/skills/build/references/dispatch-composition.md:65` — list
  "changelog entries" as an example of the prose-artifact-type model-assignment
  rule (D-42); not about where the changelog lives.

No `scripts/check_line_limits.sh` or `scripts/check_line_limits.allow` change
was needed: the markdown scope is already `docs/` recursively, so
`docs/changelog.md` and the new `docs/changelog/*.md` files are covered
automatically, and none is over its cap (largest new file is 36 lines).
`scripts/check_design_links.sh` and the `justfile`/`plugin/portable.just`
recipes name `docs/decisions.md` and `docs/references/`, never
`docs/changelog.md` by path, so nothing there needed updating. No test in
`tests/` references `changelog`.

## References deliberately left untouched

**Frozen plans under `plans/`** (historical, not edited per instructions) that
mention `docs/changelog.md`:
`plans/design-routing-and-provenance/outline.md:91`,
`plans/design-routing-and-provenance/classification.md:19`,
`plans/provenance-enforcement-and-routing/outline.md:33,280`,
`plans/provenance-enforcement-and-routing/classification.md:24`,
`plans/skill-reviews/deliverable-review.md:153`,
`plans/provenance-reach-and-sweep/outline.md:91,216`,
`plans/pipeline-simplification/outline.md:293,330,401`,
`plans/pipeline-simplification/recall-artifact.md:21`,
`plans/pipeline-simplification/requirements.md:136`,
`plans/dispatch-model-precedence/brief.md:16,49,65`,
`plans/build-skill/outline.md:371,449,467,516,539,593`,
`plans/build-skill/inventory.md:140,425`.

**`memory/`** (not edited per instructions), stale or soon-to-be-stale
references to the single-file shape:
`memory/ddaanet/claude-plugin-dev.md:37,40` (about the vendored
`claude-plugin-dev` repo's own `docs/changelog.md`, a different repo — not
stale relative to this split),
`memory/workflow-pipeline-revival.md:35,38,42` (cites specific dated entries
in what was a single `docs/changelog.md` — now split across files; the dates
cited still identify the right entry, just not the right file),
`memory/verify-loop-direction.md:55` (generic mention, not location-specific),
`memory/MEMORY.md:25` and `memory/ddaanet/MEMORY.md:38` (about
`claude-plugin-dev`'s changelog, a different repo),
`memory/ddaanet/todo-tool-flag-gated.md:39` (unrelated "unofficial changelog"
mention).

**`inbox/`** — two drafts (`inbox/brief-review-feeds-back-into-design.md:72`,
`inbox/brief-cite-line-context-not-line-numbers.md:68`) mention "a changelog
entry" generically, not `docs/changelog.md`'s location; left as-is.

## Content-preservation check

Command:

```
git show HEAD:docs/changelog.md | sed -n '14,400p' | grep -v '^## ' | grep -v '^$' | sort > orig_lines.txt
cat docs/changelog/*.md | grep -v '^# ' | grep -v '^$' | sort > new_lines.txt
diff orig_lines.txt new_lines.txt
```

Result: `diff` reported no differences — 303 non-heading, non-blank lines on
each side, identical. Run before `just format` reflowed `docs/changelog.md`
(the index, not the entry files, which `just format` did not touch).

## `just precommit` — full output (after `just format` applied rumdl's reflow
of the new index)

`just format` reformatted one file, `docs/changelog.md` — rumdl's 80-column
reflow wrapping the new index's long link lines. No other file changed.

```
[1;36m# version consistency[0m
Version consistent: 0.2.0
Tests cached (inputs unchanged)
[1;36m# line limits[0m
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
oversized-file: plugin/skills/requirements/SKILL.md: 354 lines > 200
oversized-file: plugin/skills/design/SKILL.md: 277 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 218 lines > 200
oversized-file: docs/superpowers/design/plugin-transition-evaluation.md: 403 lines > 400
[1;36m# design links[0m
design-links: 86 decisions indexed, defined once, conclusions match, 8 nodes present
[32m✓[0m Precommit OK
```

The seven `oversized-file` lines are pre-existing allowlisted ceilings
(`scripts/check_line_limits.allow`), unrelated to this change — none is under
`docs/changelog/` and the allowlist file was not touched. Precommit passed
clean.

## Uncertain / worth a second look

- **`memory/workflow-pipeline-revival.md`** cites two specific dates
  (2026-08-04, 2026-09-01) as "the `docs/changelog.md` entry of <date>". Those
  entries now live at `docs/changelog/2026-08-04-pipeline-revived.md` and
  `docs/changelog/2026-09-01-one-stage-runbook-replaces-two-stage-expansion-pipeline.md`.
  Left untouched per instructions (memory is out of scope), but flagging since
  a reader following that memory file to `docs/changelog.md` today lands on
  the index, one hop from the actual entry rather than at it directly — not
  broken, but worth a memory-side follow-up.
- Did not touch `docs/design.md` §10's wording, since it already reads as an
  accurate pointer regardless of internal shape — open to revisiting if my
  human partner wants it explicit there too, matching the `CLAUDE.md` edit.
