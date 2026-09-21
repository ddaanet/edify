# Independent review — the `docs/design.md` split (10513694)

**Date:** 2026-09-21 **Scope:** the prose move, the hub/index/node structure,
inbound references tree-wide, and `CLAUDE.md` §Design Decisions.
**Baseline:** `git show 10513694^:docs/design.md` (1234 lines), read directly;
the author's `split-report.md` was not used as evidence.

**Verdict:** no content was lost or mutated. Eight findings, none critical: two
major (both routing, not content), six minor. Six further observations are
pre-existing defects the split did not introduce and did not fix.

## 1. Content loss or mutation — mechanical, clean

Method. A normalizer (`$TMPDIR/dsplit/sent.py`) splits a markdown file into
sentence units, joining wrapped prose paragraphs, keeping table rows, list
items, headings and fenced blocks as their own units, and collapsing
whitespace. Run over the pre-split file and over the union of the ten
post-split files, sorted, then `comm`:

```
python3 sent.py old-design.md | sort > old.sent
python3 sent.py docs/design.md docs/decisions.md docs/references/*.md \
  | sort > new.sent
comm -23 old.sent new.sent   # 16 lines
comm -13 old.sent new.sent   # 175 lines
```

The normalizer is character-preserving, which is what makes the comparison
sound rather than indicative:

```
tr -d '[:space:]' < old-design.md | wc -c   # 63330
tr -d '[:space:]' < old.sent      | wc -c   # 63330
cat docs/design.md docs/decisions.md docs/references/*.md \
  | tr -d '[:space:]' | wc -c               # 74345
tr -d '[:space:]' < new.sent      | wc -c   # 74345
```

**Old-only residue: 16 units.** Ten are the `### 6.1`–`### 6.10` headings,
which survive as headings elsewhere (see §2). The other six are
cross-reference repoints, word-diffed with `difflib` against their closest new
match — every one is a single replaced token, the rest of the sentence
byte-identical:

| Where now | Old token | New token |
|---|---|---|
| `docs/design.md:27` | `(§5.3, FR-9)` unchanged; `§7.` → | `` `docs/references/pipeline-contracts.md`. `` |
| `docs/design.md:75` | `(§7);` | `` (`docs/references/pipeline-contracts.md`); `` |
| `pipeline-contracts.md:30` | `(§7).` | `(Rejected alternatives, below).` |
| `pipeline-contracts.md:133` | `(§5.3,` | `` (`docs/design.md` §5.3, `` |
| `pipeline-contracts.md:136` | `in §7` | `under Rejected alternatives, below,` |
| `execution-routing.md:27` | `§7:` | `` `docs/references/pipeline-contracts.md`: `` |

No sentence was dropped, and no rewrite changes meaning — all six are
connective repoints made necessary by the move.

**New-only: 175 units, all scaffolding.** Filtering out index lines
(`- **D-nn** — …`), headings, `Argued in …`, the `Part of the docs/design.md
graph` footer and `*Rejected:*` lines leaves 43 units: the eight node preambles
and their "Read this before …" lines, the hub's new §6/§7 pointer prose,
`decisions.md`'s preamble, and the six repointed sentences above. Nothing
substantive was invented.

**Duplication.** `sort | uniq -d` over `new.sent` finds five repeats: two table
header rows (also duplicated in the old file), the shared `Part of the
docs/design.md graph` footer, `## Rejected alternatives`, and
`## CLI and package` — that last one duplicates its own file's H1 (finding 4).
No decision, limitation, non-goal or rejected alternative is stated twice.

## 2. Misfiling and structural invariants — mechanical, clean

**ID sets identical.** `$TMPDIR/dsplit/ids.py` extracts `**D-nn`/`**L-nn`
paragraph leads and `| FR-n |`/`| NFR-n |` table rows:

```
python3 ids.py docs/design.md docs/decisions.md docs/references/*.md
# OLD count: 112  NEW count: 112
# MISSING in new: []   EXTRA in new: []
```

112 = FR-1…18 + NFR-1…7 + D-1…83 + L-2,3,4,6. Every `D-nn` appears exactly
twice — once as an index line, once as its node's argument — and no `FR`, `NFR`
or `L` appears more than once anywhere. So "defined once" holds on the intended
reading, and the index/argument pairing is total in both directions.

**Index conclusions match node lead-ins exactly.** A second pass extracts each
node's `**D-nn — <conclusion>**` and each `decisions.md` line's
`- **D-nn** — <conclusion>`, then compares case-insensitively after stripping a
trailing parenthetical. Result: `in node not indexed: []`,
`indexed not in node: []`, and zero real text mismatches (the seven reported
"mismatches" are my paragraph splitter swallowing the following group header
after a group's last bullet — each index conclusion is a byte-identical prefix
of its node's). Each of the 83 decisions therefore has exactly one index line,
in the group whose node argues it, saying the same thing.

**Un-IDed conclusions are indexed too.** Four bolded paragraph leads in nodes
carry no D-number — `Model tier naming.` and
`No model-tier introspection exists.` (agent-instructions),
`Presentation is not TDD'd.` and
`Conformance work bakes exact strings into assertions.` (testing). All four
appear as bare bullets in their `decisions.md` group. None was lost.

**All 21 rejected alternatives survive, once each, and all 21 are named in the
index.** Extracted per node from each `## Rejected alternatives` section
(multiline-tolerant, since several leads wrap): cli-and-package 10,
pipeline-contracts 5, project-configuration 2, quality-gates 2,
agent-instructions 1, execution-routing 1. The six `*Rejected:*` lines in
`decisions.md` name the same 21 in the same grouping. `testing.md` and
`deliverable-review.md` have no such section and correspondingly no
`*Rejected:*` line.

**All ten old §6 subsection titles survive as headings** — eight as node H1s,
with `6.1 CLI and package` / `6.2 Markdown and token tooling` as H2s inside
`cli-and-package.md` and `6.6 Model selection` / `6.9 Prompt and instruction
structure` as H2s inside `agent-instructions.md`. The merge is the one the
changelog claims.

**By reading:** each node's body is on its stated subject, and the hub's §1, §5,
§8 and §9 cross-citations (D-9, D-12, D-24, D-25, D-26 T5, D-34, D-82, NFR-1,
§5.3, §5.4) all resolve to text that says what the hub says it says. Two
groupings look debatable but are inherited verbatim from the pre-split
subsections, so they are not this commit's doing — see observations O-3 and O-4.

## 3. Dangling references — mechanical sweep, then read

Method. `grep -rn 'docs/design\.md'` over the whole tree excluding `.git`, then
a section-sign sweep `grep -rnE '§\s*(6|7)(\.[0-9]+)?\b'` over the whole tree,
with `plans/*/reports/` (frozen) and `docs/superpowers/plans/` (frozen)
separated out by hand. A python pass over `git ls-files` plus untracked files
printed every line containing `§` for a read-through, so a reference wrapped
across lines could not hide.

Live files still naming a section that moved:

- **`.claude/rules/design-work.md:9`** — finding 1 below.
- **`memory/feedback-decision-docs-are-living.md:28-29`** — finding 3 below.

Everything else resolves. `docs/design.md` §5/§5.1 pointers
(`plugin/skills/design/references/design-content-rules.md:186`,
`docs/marketplace.md:19`, `memory/plugin-transition-eval.md:22`) and the L-6
pointer (`memory/workflow-pipeline-revival.md:39`) all target sections that
stayed in the hub. The four `.claude/rules/` and eleven `plugin/` pointers that
did move are correctly repointed, as is `agents/ROADMAP.md:11`. The hub keeps
§7 as a heading with pointer prose rather than renumbering, so §8/§9/§10
pointers survive — good call.

`docs/changelog.md:221` ("§7 records the rejected two-stage model…") is a dated
2026-09-01 entry describing the state at write time; the changelog is the
write-time record, so it is correct as history, not a stale pointer.

## 4. `CLAUDE.md` routing table — by reading

All eight node names exist and every filename is spelled correctly. The
surrounding claims are both **true**: `docs/decisions.md` does index every
decision as one conclusion line (83 + 4 un-IDed) and does name every rejected
alternative (21/21, verified in §2); `docs/changelog.md` does carry the dated
design-significant entries, including this split's own.

Five of the eight scope lines route their node's whole content. Three do not —
finding 2.

## 5. Optional flag (no fix proposed)

§3 and §4 are tables (`| # | Requirement | Status | Where · pinned by |`) where
`craft:design-doc-writing` prefers a prose lead-in per requirement. Unchanged
by this commit; flagged as asked, not touched.

## Findings

### Major 1 — `.claude/rules/design-work.md` was not repointed

`.claude/rules/design-work.md:9` tells an agent facing an architectural choice
to "resolve using architectural principles from loaded context
(`docs/design.md`, `plugin/fragments/`, plan design documents)". Post-split,
`docs/design.md` no longer holds the decisions — that is exactly the content
this commit moved out. The rule fires on `plans/*/design.md` and
`plans/*/runbook.md`, i.e. precisely when the decisions are needed.

The commit message says inbound references were repointed "including the
path-triggered `.claude/rules` files". `git show --stat 10513694` lists
`cli-work.md`, `test-work.md` and `workflow-work.md` — not `design-work.md`. The
claim over-states by one file.

**Fix** (mechanical, exact):

- file: `.claude/rules/design-work.md`
- old: ``(`docs/design.md`, `plugin/fragments/`, plan design documents)``
- new: ``(`docs/design.md`, `docs/decisions.md` and the `docs/references/` node
  it points at, `plugin/fragments/`, plan design documents)``

### Major 2 — three `CLAUDE.md` scope lines leave node content unroutable

The table's job is to route from what an agent touches to the node it reads
first. Three lines are narrower than their node, so content in those nodes is
unreachable from the table:

| Node | Scope line | Unrouted content |
|---|---|---|
| `pipeline-contracts.md` | "dispatch, review gates, phase types" | D-80 artifact provenance (`## Provenance`, `edify-review-range.sh`); D-25 the planning/execution session boundary |
| `execution-routing.md` | "`/design`, `/runbook`, `/build` routing" | D-35/D-38 classification; D-40 the three escalation tiers |
| `project-configuration.md` | "`.claude/`, agent frontmatter, line caps" | D-72 what a sub-agent actually gets; D-74/D-75 naming; D-76/D-77 the script-versus-delegate split |

D-72 is the sharpest loss: it is the measured platform record (hooks do not fire
in sub-agents, no `max_turns`, nested spawning does not return, resumption is
`SendMessage` by `name`), and nothing in "`.claude/`, agent frontmatter, line
caps" sends an agent there. The hub's own §6 list already names "sub-agent
capabilities", "classification, escalation tiers" and "artifact provenance", so
the information to fix this exists one file away.

A fourth line is weaker but arguable: `quality-gates.md` — "gates, hooks,
validating scripts" does not route D-52 (every skill step opens with a tool
call), D-53 (negative constraints sit beside their positive guidance) or D-54
(four discovery layers), which are skill-authoring rules. An agent writing a
skill is sent to `agent-instructions.md`, whose own preamble says "Read this
before writing a skill", and will not open `quality-gates.md`. Grouping is
pre-existing (O-3); the routing gap is new.

**Fix** (mechanical, exact — `CLAUDE.md` §Design Decisions):

- old: ``- `pipeline-contracts.md` — dispatch, review gates, phase types``
- new: ``- `pipeline-contracts.md` — dispatch, the planning/execution session
  boundary, review gates, phase types, artifact provenance``
- old: ``- `execution-routing.md` — `/design`, `/runbook`, `/build` routing``
- new: ``- `execution-routing.md` — `/design`, `/runbook`, `/build` routing,
  classification, escalation tiers``
- old: ``- `project-configuration.md` — `.claude/`, agent frontmatter, line
  caps``
- new: ``- `project-configuration.md` — `.claude/`, agent frontmatter, line
  caps, what a sub-agent gets, naming, script-versus-delegate``
- old: ``- `quality-gates.md` — gates, hooks, validating scripts``
- new: ``- `quality-gates.md` — gates, hooks, validating scripts, skill step
  and rule placement``

### Minor 3 — stale `§7` pointer in a memory file

`memory/feedback-decision-docs-are-living.md:28-29` records L-5's retirement:
"`§1 Now` and the `§7` rejected-alternative entry keep the mechanism and name
`/gitlore:index-audit` as the pass that acts on it." `§1 Now` still resolves;
`§7` no longer holds entries. The entry in question — "Pruning the memory index
on a size limit" — is now
`docs/references/project-configuration.md` § Rejected alternatives.

**Fix:** `memory/feedback-decision-docs-are-living.md`, old
``the `§7` rejected-alternative entry`` → new ``the "Pruning the memory index on
a size limit" entry in `docs/references/project-configuration.md```. Memory
file: my human partner's call whether a review may touch it.

### Minor 4 — `cli-and-package.md:11` duplicates its own H1

`# CLI and package` (line 1) then `## CLI and package` (line 11). The H2 is the
former `### 6.1` title, mechanically preserved. Six of the eight nodes are flat
bodies; this one reads as if the file had a section about itself.

**Fix:** delete `## CLI and package` and its following blank line, leaving
D-1…D-13 directly under the H1 and `## Markdown and token tooling` as the one
subsection — the shape `pipeline-contracts.md` already has (flat body plus
`## Rejected alternatives`). Renaming instead (e.g. `## Package and bootstrap`)
is a judgement call, listed below.

### Minor 5 — two nodes end with a trailing blank line

`tail -c 2` over the ten files: `docs/references/testing.md` and
`docs/references/deliverable-review.md` end `\n\n`; the other eight end with a
character then `\n`. Two of ten, no pattern.

**Fix:** delete the trailing blank line in
`docs/references/testing.md` and `docs/references/deliverable-review.md`.

### Minor 6 — three divergent copies of the routing table

The eight nodes are described in three places, each with its own wording:
`CLAUDE.md` §Design Decisions (routes by what you touch), `docs/design.md` §6
(describes by content), and `docs/decisions.md`'s group headings plus their
`Argued in …` lines. Renaming, merging or splitting a node now needs three
edits, and nothing checks the three against each other — which is how finding 2
arose in the first place.

Not a defect today; the two prose lists do different jobs. Consolidation is a
judgement call, listed below.

### Minor 7 — `docs/changelog.md:38` undercounts the repoints

"the only tokens that left the moved text are four `§7`/`§5.3` cross-references
that became paths". Four is right for the *moved* text (three sites in
`pipeline-contracts.md`, one in `execution-routing.md`), so the sentence is true
as written — but six sites were repointed in total, the other two being in the
retained hub (`docs/design.md:27` and `:75`). A later auditor grepping for four
will find six and suspect the entry.

**Fix:** `docs/changelog.md`, old ``are four `§7`/`§5.3` cross-references that
became paths`` → new ``are four `§7`/`§5.3` cross-references that became paths,
with two more repointed in the retained hub``.

### Minor 8 — two "graduates into `docs/design.md`" pointers now under-specify

`agents/README.md:9` ("older entries graduate into `docs/design.md`") and
`agents/learnings.md:5` ("technical details → `docs/design.md`") both name only
the hub. A learning that becomes a decision now needs a node argument *and* an
index line. Both paths resolve, so this is wording, not a dangling reference.

**Fix:** `agents/learnings.md`, old ``technical details → `docs/design.md``` →
new ``technical details → `docs/design.md`, a decision → a `docs/references/`
node plus its `docs/decisions.md` line``. Same substitution shape for
`agents/README.md:9`.

## Pre-existing, not introduced by this commit

- **O-1** `.gitlore/bin/claude:4` cites `docs/design.md "Memory Redirect
  Launcher" (D10)`. `grep 'Memory Redirect'` over the pre-split file returns
  nothing, so the section never existed here. Already recorded in
  `.claude/handoff-todo.md`.
- **O-2** `.claude/rules/cli-work.md` fires on `src/cli/**` and `bin/**`. The
  CLI source is `src/edify/` and the bootstrap is `plugin/bin/`, so the rule
  matches nothing and its (correctly repointed) node is never reached by it.
- **O-3** D-52/D-53/D-54 are skill-authoring rules filed under quality gates —
  the grouping of the old §6.7, preserved.
- **O-4** D-32 ("Runbook review runs at opus") is a model-choice decision filed
  under pipeline contracts rather than agent instructions — the grouping of the
  old §6.4, preserved.
- **O-5** `plugin/skills/deliverable-review/SKILL.md:64,135,173` and
  `references/example-report.md:3` cite `docs/references/deliverable-review.md`,
  but the plugin root is `plugin/` and `docs/` is not shipped, so the citation
  is unresolvable for an installed plugin. Pre-existing in form: it pointed at
  the same unshipped file's §6.8 before.
- **O-6** `docs/design.md:28-29` attributes the three-tier retirement to D-34.
  D-34 is the 2026-09-17 `/build` merge; the three tiers went on 2026-09-01 and
  D-34 *carries that forward*, as `execution-routing.md:25` says. The sentence
  is byte-identical to the pre-split text apart from the `§7` repoint.

Also verified while checking the changelog's claims, all true: the
`docs/design.md` allowlist entry is gone from
`scripts/check_line_limits.allow`; the hub is 288 lines, the index 175, the
largest node 224, all under the 400 cap; and no prose line in any of the ten
files exceeds 80 *characters* — the only over-80 lines are table rows and bare
URLs, which MD013 reflow cannot break. (Byte-length tools report false
positives here: em dashes and arrows are three bytes each.)

## Fixes safe to apply mechanically

1. `.claude/rules/design-work.md` — ``(`docs/design.md`, `plugin/fragments/`,
   plan design documents)`` → ``(`docs/design.md`, `docs/decisions.md` and the
   `docs/references/` node it points at, `plugin/fragments/`, plan design
   documents)``
2. `CLAUDE.md` — the four scope-line substitutions given under Major 2.
3. `docs/references/cli-and-package.md` — delete line 11
   `## CLI and package` and the blank line after it.
4. `docs/references/testing.md` — delete the trailing blank line.
5. `docs/references/deliverable-review.md` — delete the trailing blank line.
6. `docs/changelog.md` — ``are four `§7`/`§5.3` cross-references that became
   paths`` → ``are four `§7`/`§5.3` cross-references that became paths, with two
   more repointed in the retained hub``
7. `agents/learnings.md` — ``technical details → `docs/design.md``` →
   ``technical details → `docs/design.md`, a decision → a `docs/references/`
   node plus its `docs/decisions.md` line``
8. `agents/README.md` — ``older entries graduate into `docs/design.md``` →
   ``older entries graduate into `docs/design.md`, or into a
   `docs/references/` node plus its `docs/decisions.md` line``

## Needs my human partner's call

1. **The memory-file edit (finding 3).** `memory/` is a gitlore submodule and
   the fix is a content change to a fact, not a path repoint. Say whether a
   review may edit it directly or should route through the memory-writing skill.
2. **Whether to rename `cli-and-package.md`'s first H2 instead of deleting it.**
   Deleting leaves an asymmetric file (flat body + one named subsection).
   Renaming to something like `## Output, errors and packaging` keeps the
   symmetry and costs one invented heading name.
3. **Whether to consolidate the three routing surfaces (finding 6).** One
   option: cut `docs/design.md` §6's eight-line list to a pointer at
   `docs/decisions.md`, leaving `CLAUDE.md` as the only routing table and
   `decisions.md`'s `Argued in …` lines as the only per-group scope statement.
   That removes the drift that produced Major 2, at the cost of a hub section
   that no longer states the shape on its own.
4. **Whether the `quality-gates.md` skill-authoring rules (O-3) should move to
   `agent-instructions.md`.** Major 2's fourth substitution patches the routing
   without moving anything; moving D-52/D-53/D-54 would fix the grouping but
   re-opens a boundary this commit deliberately preserved.
5. **O-5, the unshipped-`docs/` citations from a shipped skill.** Real for any
   installed plugin, out of scope for a split review, and the fix is a design
   question (ship the node, inline the axes, or accept the dogfood-only limit).
