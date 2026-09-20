# docs/design.md split — report

2026-09-20. `docs/design.md` went from 1234 lines to a hub of 288, a decision
index of 175 and eight nodes under `docs/references/`, largest 224. Nothing
committed; nothing under `memory/` or `.claude/` was edited.

## Layout, and why this cut

`craft:design-doc-writing` names one lever at the hub's floor: the
`## Decisions` heading is itself a section boundary, so the conclusions move
whole into `docs/decisions.md` and the two sections above it become pointer
stubs.

The measurement says that lever was needed rather than optional. Keeping §6 in
the hub as one conclusion line per decision would have put the hub at roughly
460 lines (201 lines of §1–§5, ~176 of conclusions, ~25 of rejected names, 57
of §8–§10) — over the 400 cap before any growth. With §6 and §7 moved out the
hub measures 288.

**Node boundaries are need-time**, which is what the skill asks for. The repo
already carried evidence of where those boundaries fall: `.claude/rules/`
routes CLI work to §6.1, test work to §6.3, and workflow work to §6.4 plus
§6.5. Seven nodes are one former subsection each. One merge: §6.6 "Model
selection" and §6.9 "Prompt and instruction structure" became
`agent-instructions.md`, because a reader writing a skill, a fragment or a
dispatch prompt needs both (D-63 bridges them), and — checked before merging —
neither section was cited from anywhere outside the doc, so the merge cost no
repoint. §6.4 and §6.5 were *not* merged despite `workflow-work.md` naming them
together: at 181 + 128 lines they would sit near the cap, and both are the
active-growth areas (D-80 to D-83 are the newest entries) against a policy that
never raises a ceiling.

The 21 rejected alternatives moved to the node whose decisions they protect,
under that node's own `## Rejected alternatives` heading, and are named in the
index on a `*Rejected:*` line per group — the fold the skill prescribes, rather
than a separate index.

Two files carry the loading instruction, since nothing in Claude Code opens a
node on its own: the hub's opening states the shape, and `CLAUDE.md` §Design
Decisions now carries a routing table from what an agent touches to the node it
reads first, plus the commit rule (hub conclusion and node argument change
together).

## Line counts

| File | Lines |
|---|---|
| `docs/design.md` (hub) | 288 |
| `docs/decisions.md` (index) | 175 |
| `docs/references/pipeline-contracts.md` | 224 |
| `docs/references/cli-and-package.md` | 186 |
| `docs/references/agent-instructions.md` | 143 |
| `docs/references/execution-routing.md` | 143 |
| `docs/references/project-configuration.md` | 123 |
| `docs/references/quality-gates.md` | 100 |
| `docs/references/deliverable-review.md` | 68 |
| `docs/references/testing.md` | 60 |

Counted after `just format` (rumdl, MD013 reflow at 80 columns). Cap is 400 for
every one of them. Also touched and still under cap: `CLAUDE.md` 311,
`docs/changelog.md` 328.

The `docs/design.md` entry was deleted from
`scripts/check_line_limits.allow`. No entry was added. `just precommit` no
longer reports `docs/design.md` as oversized.

## ID-set diff

Every identifier definition present before is present exactly once after.

```sh
cd /Users/david/code/edify
git show HEAD:docs/design.md \
  | grep -oE '^\| (FR|NFR)-[0-9]+ |^\*\*(D|L)-[0-9]+ ' \
  | tr -d '|*' | tr -d ' ' | sort -V > /tmp/ids-before.txt
grep -hoE '^\| (FR|NFR)-[0-9]+ |^\*\*(D|L)-[0-9]+ ' \
  docs/design.md docs/decisions.md docs/references/*.md \
  | tr -d '|*' | tr -d ' ' | sort -V > /tmp/ids-after.txt
wc -l /tmp/ids-before.txt /tmp/ids-after.txt
diff /tmp/ids-before.txt /tmp/ids-after.txt && echo IDENTICAL
sort /tmp/ids-after.txt | uniq -d   # no output = no id defined twice
```

Result: 112 definitions before, 112 after, `diff` silent (`IDENTICAL`),
`uniq -d` empty. The set is D-1…D-83 (83), FR-1…FR-18 (18), NFR-1…NFR-7 (7),
L-2, L-3, L-4, L-6 (4). The retired ids stay retired and un-reused: FR-19,
FR-20 and L-1 keep their retirement notes in the hub; D-31 is superseded but
present.

`git show HEAD:docs/design.md` is the right baseline — the file was clean at
HEAD when the split started (verified by diffing it against the working copy
taken before any edit).

Index coverage — every decision argued in a node has a conclusion line in the
index, and no index line points at an argument that does not exist:

```sh
grep -oE '\*\*D-[0-9]+\*\*' docs/decisions.md | tr -d '*' | sort -V > /tmp/idx.txt
grep -hoE '^\*\*D-[0-9]+ ' docs/references/*.md | tr -d '|*' | tr -d ' ' | sort -V > /tmp/nodedefs.txt
diff /tmp/idx.txt /tmp/nodedefs.txt && echo IDENTICAL
```

Result: 83 and 83, `diff` silent.

Rejected alternatives — 21 before (not 19: a `grep '^\*\*[^*]+\*\*'` misses the
two entries whose names contain a `*` inside backticks,
`` `"Bash(rm:*/index.lock)"` `` and the PreToolUse advisory), 21 after, same
names verbatim:

```sh
git show HEAD:docs/design.md | awk 'NR>=1075 && NR<=1178' | grep -E '^\*\*' \
  | sed 's/\(\*\*.*\*\*\).*/\1/' | sort > /tmp/rej-before.txt
for f in docs/references/*.md; do
  awk '/^## Rejected alternatives/{f=1;next} /^## /{f=0} f && /^\*\*/' "$f"
done | sed 's/\(\*\*.*\*\*\).*/\1/' | sort > /tmp/rej-after.txt
diff /tmp/rej-before.txt /tmp/rej-after.txt && echo IDENTICAL
```

Result: `IDENTICAL`. Distribution: cli-and-package 10, pipeline-contracts 5,
quality-gates 2, project-configuration 2, agent-instructions 1,
execution-routing 1.

### Content-loss check

Because every block moved as an exact line range, a token set-difference proves
nothing but the four deliberate repoints left the moved text:

```sh
git show HEAD:docs/design.md | awk 'NR>=202 && NR<=1178' | grep -v '^#' \
  | tr -s ' \t' '\n\n' | sed '/^$/d' | sort -u > /tmp/set-before.txt
cat docs/references/*.md | grep -v '^#' \
  | tr -s ' \t' '\n\n' | sed '/^$/d' | sort -u > /tmp/set-after.txt
comm -23 /tmp/set-before.txt /tmp/set-after.txt
```

Result, the complete output: `(§5.3,`, `(§7).`, `§7`, `§7:` — the four
cross-references rewritten to paths (see below). Nothing else left. The same
check over the hub's own sections (lines 1–201 and 1179–1235 against
`docs/design.md`) returns `(§7);` and `§7.` and nothing else.

### Cross-references rewritten inside the moved text

Four, all because the section they named is no longer where the reader is:

- hub §3, "dropped 2026-09-01 with the two-stage runbook (§7)" →
  `` `docs/references/pipeline-contracts.md` ``
- hub §1 "Do not re-litigate", "rejected in §7" → same node
- `pipeline-contracts.md` D-24 "(§7)" and D-31 "recorded in §7" → "Rejected
  alternatives, below" (same file)
- `pipeline-contracts.md` D-31 "(§5.3, FR-9)" →
  "(`docs/design.md` §5.3, FR-9)"
- `execution-routing.md` D-34 "rejected in §7" →
  `` `docs/references/pipeline-contracts.md` ``

Left alone because they still resolve: hub-internal §5.3 / §5.4;
`pipeline-contracts.md` "§Provenance" (a section of a design artifact, not of
this doc); `execution-routing.md` "§4", "§4.1", "§4.3" (sections of
`plugin/skills/build/SKILL.md`).

## Inbound-reference classification

Whole-tree grep for `docs/design.md` and `design.md#`, excluding `plans/`
(frozen records), `memory/` (off-limits) and `.git/`:

```sh
grep -rn 'docs/design\.md\|design\.md#' --include='*' . \
  | grep -vE '^(\.git|plans|memory)/'
```

No hit anywhere in the tree used the `design.md#anchor` form.

### Repointed (17 hits, 13 files)

| File:line | Was | Now |
|---|---|---|
| `CLAUDE.md:293` | "the living design record (requirements, architecture, decisions, rejected alternatives)" | hub/index/nodes shape plus an eight-row routing table and the commit rule |
| `plugin/skills/deliverable-review/SKILL.md:64` | `docs/design.md` §6.8 | `docs/references/deliverable-review.md` |
| `plugin/skills/deliverable-review/SKILL.md:135` | `docs/design.md` §6.8 (report template field) | `docs/references/deliverable-review.md` |
| `plugin/skills/deliverable-review/SKILL.md:172` | `docs/design.md` §6.8 (References) | `docs/references/deliverable-review.md` |
| `plugin/skills/deliverable-review/references/example-report.md:3` | `docs/design.md` §6.8 | `docs/references/deliverable-review.md` |
| `plugin/skills/runbook/SKILL.md:22` | `docs/design.md` §6.4 | `docs/references/pipeline-contracts.md` |
| `plugin/skills/runbook/SKILL.md:113` | `docs/design.md` D-39 | `docs/references/execution-routing.md` D-39 |
| `plugin/skills/design/SKILL.md:256` | `docs/design.md` §6.4 | `docs/references/pipeline-contracts.md` |
| `plugin/skills/design/references/design-content-rules.md:193` | `docs/design.md` §6.4 | `docs/references/pipeline-contracts.md` |
| `plugin/skills/design/references/design-content-rules.md:218` | "the living design (`docs/design.md`)" in the opus-required directive | gained `docs/decisions.md` and `docs/references/` — the directive decides who may edit design prose, and that prose now lives in the nodes |
| `plugin/skills/build/references/finishing.md:35` | `docs/design.md` §6.4 D-26 | `docs/references/pipeline-contracts.md` D-26 |
| `plugin/skills/build/references/review-dispatch-template.md:101` | `docs/design.md` §6.4 D-26 | `docs/references/pipeline-contracts.md` D-26 |
| `plugin/fragments/claude-config-layout.md:91` | `docs/design.md` §6.10 | `docs/references/project-configuration.md` |
| `plugin/fragments/review-requirement.md:68` | `docs/design.md` §6.4 | `docs/references/pipeline-contracts.md` |
| `agents/ROADMAP.md:11` | `docs/design.md` §6.2 | `docs/references/cli-and-package.md` "Markdown and token tooling" |
| `tests/test_review_range.py:25` | `(docs/design.md D-21)` in a docstring | `(docs/references/testing.md D-21)` |
| `scripts/check_line_limits.allow:15` | the `docs/design.md 1234` ceiling | entry deleted |

### Still accurate, left alone (15 hits)

- `README.md:60` — "Design is recorded in `docs/design.md`." The hub is the
  entry point and its opening states the shape.
- `docs/marketplace.md:19` — `docs/design.md` §5.1 "One tree, two products".
  §5 stayed in the hub.
- `docs/changelog.md:9` and `:11` — bare references to the hub as the
  present-tense record. Still true.
- `plugin/skills/design/references/design-content-rules.md:186` —
  `docs/design.md` §5 "Architecture". §5 stayed in the hub.
- `plugin/skills/design/SKILL.md:137` — `docs/design.md` in a table of
  investigation-output locations. Bare reference.
- `plugin/skills/build/references/dispatch-composition.md:53` — "the living
  design (`docs/design.md`), changelog entries and decision nodes" as examples
  of opus-work prose. It already said "decision nodes"; still accurate.
- `plugin/skills/build/references/review-dispatch-template.md:122` —
  `docs/design.md` inside a worked example's Scope OUT list. Example content.
- `plugin/agents/refactor.md:155` — "**Design record** - `docs/design.md`, only
  if the refactored symbols are named there". Bare; symbols named in a node are
  reached via the hub's routing.
- `agents/learnings.md:5` and `agents/README.md:9` — learnings graduate into
  `docs/design.md`. Bare reference to the entry point; one hop to the right
  file via the hub's shape statement.
- `.claude/rules/design-work.md:9` — lists `docs/design.md` among the sources
  of architectural principle. Bare reference, still true, so the no-edit
  constraint costs nothing here.
- `.claude/handoff-todo.md:3`, `:14`, `:20` — session task notes naming the
  file and this job. Nothing to repoint.

### Needs a repoint, NOT applied — `.claude/` is no-edit

The brief listed `.claude/rules/*.md` among the files to fix and also said not
to edit anything under `.claude/`. I took the prohibition as binding and
messaged team-lead. These three are stale as of this split; each is a
one-line change:

- `.claude/rules/cli-work.md:7` — `` `docs/design.md` §6.1 "CLI and package" ``
  → `` `docs/references/cli-and-package.md` ``
- `.claude/rules/test-work.md:7` — `` `docs/design.md` §6.3 "Testing" `` →
  `` `docs/references/testing.md` ``
- `.claude/rules/workflow-work.md:6` —
  `` `docs/design.md` §6.4 "Pipeline contracts" and §6.5 "Execution routing" ``
  → `` `docs/references/pipeline-contracts.md` and
  `docs/references/execution-routing.md` ``

These matter more than most: they are the path-triggered routing D-67
describes, and the split's whole payoff depends on an agent opening the node.

### Pre-existing staleness, not caused by this split, not fixed

- `.gitlore/bin/claude:4` — `# see docs/design.md "Memory Redirect Launcher"
  (D10)`. No such section and no such decision existed in `docs/design.md`
  before the split either; it points at some other repo's design doc. Left
  alone — `.gitlore/` is gitlore infrastructure, and fixing it is not this
  job's scope.
- `memory/ddaanet/harden-human-gates.md:13` cites
  `docs/references/evals-operations.md` §10.4 — another repo's node, not one of
  ours. Excluded tree, mentioned so a future path-resolution sweep does not
  flag it.

## `just precommit`

Full, untruncated output:

```
# version consistency
Version consistent: 0.2.0
# Test Report

**Summary:** 331/332 passed, 1 xfail
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
oversized-file: plugin/skills/review/SKILL.md: 231 lines > 200
oversized-file: plugin/skills/requirements/SKILL.md: 357 lines > 200
oversized-file: plugin/skills/design/SKILL.md: 285 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 218 lines > 200
oversized-file: plugin/skills/proof/SKILL.md: 203 lines > 200
oversized-file: docs/superpowers/design/plugin-transition-evaluation.md: 403 lines > 400
✓ Precommit OK
```

Green. Every `oversized-file:` line is an allowlisted file that was already
over its cap before this job — reported by design, failing nothing.
`docs/design.md` is no longer among them, which is the gate's own confirmation
that the split landed.

## Changelog

`docs/changelog.md` gained a dated entry at the top — the split is
design-significant (a subsystem restructured) and a future reader asking "why
is the design in three places" needs it. It records the measurement that made
the cut necessary, the need-time boundary, the one merge and the one
non-merge, and the open question about whether an always-on instruction
reliably causes the node read.

## Things I was unsure about

1. **The `.claude/rules/` conflict**, above. Default taken: do not edit,
   report. One message sent to team-lead; not waited on.
2. **§6.4 + §6.5 left unmerged.** `workflow-work.md` names them together,
   which is real need-time evidence for merging. I did not, because 309 lines
   plus framing against a 400 cap in the project's fastest-growing area, under
   a never-raise-the-ceiling policy, buys a re-split soon. Cheap to reverse if
   you disagree.
3. **FR/NFR stayed as tables.** The skill says FR and NFR rows usually are not
   tabular and should take bolded lead-in prose. Converting them would grow the
   hub and is a style change rather than a split; I left it. Worth its own
   pass.
4. **No crosslink checker exists.** The skill describes one — a gate failing on
   a decision with no index line or a pointer that stops resolving. This repo
   has the line-limit gate but nothing checking the graph's shape, so the
   invariants proved above are proved once, by hand, not pinned. The checks in
   this report are all one-liners and would make a reasonable script.
5. **`docs/decisions.md` at 175 lines** is the file that grows fastest from
   here: every new decision adds a line, and it cannot be split without losing
   the read-whole property that is the reason it exists. Worth watching rather
   than acting on.

## Working-tree state at the time of writing

Two paths are dirty that this job did not touch, reported rather than filtered:

- `.claude/handoff-todo.md` — staged (`M ` in the index), not by me.
- `plans/provenance-enforcement-and-routing/outline.md` — modified, not by me.
- `.claude/autodrive.exited` — untracked, present before this job started.

Everything else in `git status --porcelain` is this job: the 12 repointed
files, the allowlist, `docs/changelog.md`, `docs/design.md`, and the new
`docs/decisions.md` and `docs/references/`. Nothing was committed and no branch
was created.
