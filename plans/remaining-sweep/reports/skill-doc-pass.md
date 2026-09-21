# Skill and doc pass — A through E

2026-09-21. All five items applied. `just format` then `just precommit` green;
full output at the end. No file I touched appears in the line-limit report, and
no allowlist ceiling moved.

---

## A — scope a GREEN dispatch to its slice

Evidence read first:
`plans/provenance-enforcement-and-routing/reports/tdd-audit.md` §Process
recommendations and §Deviation audits 1–2, plus the two list-revision paragraphs
in that plan's `outline.md` (Item 1.2 after slice 2 and after slice 3; Item 1.10
before slice 1 and the final TDD-audit revision).

The rule now acts in three places, because a rule in only the first two is a
rule the GREEN agent never reads:

- `plugin/skills/build/references/dispatch-composition.md` §Prompt contents,
  item 3 (Scope). Old:
  `OUT — the next items' targets, named explicitly so the executor does not wander into them.`
  New adds: for a GREEN dispatch OUT also names the rest of the item's own
  contract — the `Interfaces:` block goes in for structure, and every part of it
  this slice's tests do not reach is out of scope.
- `plugin/skills/build/references/tdd-slice.md` §(c), new closing paragraph
  **The GREEN prompt carries this slice's behaviour and nothing wider** — GREEN
  implements nothing the slice's tests *do not* demand, and over-implementing
  costs every later slice a mutation proof.
- `plugin/agents/test-driver.md` GREEN mode lead paragraph. Old:
  `Receives the failing batch as its contract and grows the implementation.` New
  adds: the batch is the whole scope; an `Interfaces:` block states the surface
  for structure and any part no test reaches is out of scope here. Placed in the
  section's primacy position rather than as a numbered step, so no step
  renumbered.

The fallback is in `tdd-slice.md` §(a) as its own bolded paragraph,
**Mutation proof — the fallback when the behaviour is already implemented**:
mutate the SUT in place so the behaviour is absent, show each named test red on
its own assertion, restore, verify the restore (`git diff --quiet <sut>` or a
checksum against a copy saved before the first mutation), one mutation per named
test with a restore after each, recorded under a `Mutation proof` heading in the
RED report and as a list revision. Wording marks it a fallback, not a route.

**The three-way reconciliation**, which was the part that needed care:

| Statement | Where | How it now reads |
|---|---|---|
| a passing RED test is vacuous | `test-driver.md` RED step 4 | "…**unless** the behaviour it asserts is already in the SUT" → then the mutation procedure |
| every listed test FAILED | `tdd-slice.md` §(b) first check | a test recorded under `Mutation proof` satisfies the check *by its proof*; the reviewer reproduces it with a **different** mutation. A test with neither a red nor a proof fails the check |
| RED cannot fail → `blocked:` | `test-driver.md` Stop Conditions | now "…and no mutation of the SUT reds it either" |

Also reconciled, which the dispatch did not name but the rule is incoherent
without: `plugin/agents/tdd-auditor.md` per-slice check 1 said "a RED report
showing a passing test with no test-review disposition is a violation". It now
carries **A mutation proof is the one substitute**, counted against named tests
rather than the slice — "one mutation covering a batch leaves every other test
in it unproven, and that is the violation", which is audit recommendation 2.

Deliberately untouched: where a slice's GREEN report is committed (F-1 in
`brief-triage.md`). Nothing in these edits assumes an answer either way.

---

## B — `/recall` loads skills

Verified before acting. Of the `plans/skill-reviews/recall.md` findings, C2 is
already fixed (step 5 carries the store-relative prefix rule) and M2 is still
present (step 2 hardcoded `rg --files memory/` ahead of step 3's corpus
resolution). I did not act on M1, M3, M5 or the m-items — out of scope — but my
step-2 rewrite drops the hardcoded path in favour of the root step 3 resolves,
which is M2's own remedy for the one line I was touching.

**Cache layout verified on this machine**, not assumed:
`~/.claude/plugins/cache/<owner>/<plugin>/<version>/skills/<name>/SKILL.md`
holds. Two corrections to the brief's wording, both measured:

- Several versions coexist (`ddaanet/craft/{0.1.0,0.2.0}`,
  `ddaanet/plugin-craft/{0.1.0,0.1.1,0.1.2}`), so a version must be chosen.
- "Highest version" does not generalise:
  `anthropic-agent-skills/document-skills` has four version directories named by
  content hash (`34040c9c5685`, `3b3fad96af16`, `41bbe19d1a1a`, `53048666b05b`),
  which do not order. So the skill says **newest**, resolved by
  `ls -dt ~/.claude/plugins/cache/*/<plugin>/*/skills/<name>/SKILL.md | head -1`
  — one glob over both varying segments, verified returning
  `.../ddaanet/craft/0.2.0/skills/directive-writing/SKILL.md` and failing
  visibly on a nonexistent plugin. Absent skill: report the name and continue;
  never reconstruct a body from a description.

Files changed:

- `plugin/skills/recall/SKILL.md` — `description:` now says "its memory files
  and the skills it lists"; `allowed-tools: Read, Bash` → `Read, Bash, Skill`;
  skills-loading folded into **step 1** (same artifact, same act, no
  renumbering). Step 2 retitled **Match the topic against the index**: old text
  said the index "is injected at session start and is never Read", degrading
  only where it is "structurally absent". New text confirms its lines are in
  context before matching and Reads `MEMORY.md` under the corpus root otherwise
  — "its absence is ordinary, not impossible: one prior session found it missing
  at every recall checkpoint". The closing paragraph "A subagent that lacks the
  index should not invoke this skill" was replaced: it directly contradicted the
  new step 2 and the Skill-tool fallback.
- `plugin/skills/design/references/write-outline.md` §Artifact format — the
  format block now carries `## Skills to load before executing` with a
  `<plugin>:<name> — <note>` line, marked optional, plus the rule that a fact
  migrated into a skill is listed there rather than as a memory entry.
  **This was the only place the artifact format is specified**; the format block
  had no skills section, so nothing produced one on purpose.
- `plugin/agents/test-driver.md` and `plugin/agents/artisan.md` §Context
  Handling — both resolve a recall artifact *without* invoking the skill and
  neither holds `Skill`, so the read path is inline in each definition. This is
  the reach the rule needed: a rule only in the recall skill would never have
  been seen by either.
- `plugin/fragments/delegation.md` §Recall Artifacts For Sub-Agents — one
  clause, for the dispatcher's benefit.

Grep for `Skills to load` across the tree (excluding `.git`) returned exactly
two hits before this pass: `.claude/handoff-todo.md:22` and
`plans/provenance-reach-and-sweep/recall-artifact.md:27`. The four correctors
that invoke `Skill(skill: "edify:recall", …)` all hold `Skill`, so they need no
per-agent clause.

---

## C — three small skill fixes

**M1** — `plugin/skills/runbook/SKILL.md`. Old:
`- **Code-fix items enumerate affected call sites** (file:function or file:line).`
New: by file and enclosing symbol, plus a quoted distinctive fragment where the
symbol holds more than one site; no line numbers, "the edits the item prescribes
invalidate them, and the reader who needs them is reading after the edit".

**`plugin/fragments/token-economy.md` — judged, and fixed.** The finding holds
on inspection: `(path:line or path)` licenses the exact form M1 removes, with no
write-time-record distinction. Two facts against each other — no file under
`plugin/` or `docs/` routes to this fragment (`grep -rn token-economy` hits only
`docs/superpowers/design/plugin-transition-evaluation.md:254`, a frozen
evaluation), so it licenses nothing to an in-repo reader *today*; but it ships
in `plugin/fragments/` and a consumer's skill can route to it, and the fix is
one clause. Fixed: a path, or the path plus the enclosing symbol; `path:line`
only in a dated write-time record. **Separately worth a decision:** this
fragment is otherwise an orphan in the tree. Retiring it is a deletion I did not
take on my own authority.

**M8** — `plugin/skills/build/references/finishing.md` §3 step 2. Old: "with the
session's `subagents/` transcripts as fallback where a report is missing". New:
"Where a report is missing, resume the agent named for that dispatch and get it
(`references/dispatch-composition.md` §Naming and resumption)." The transcript
route is **withheld rather than forbidden** — naming it to prohibit it hands a
fresh agent the string, and no other source in that context supplies it.

**`CLEAN` prose.** `grep -rn CLEAN` over
`plugin/ docs/ scripts/ tests/ src/ justfile README.md` found three live hits:
the script itself (`verify-step.sh:33`, already `echo "CLEAN: $checks"`) and
`build/SKILL.md:52` and `:141`, both `- Exit 0 (CLEAN) → proceed.` Those two are
now `- Exit 0 (`CLEAN:` and the checks that passed) → proceed.` The replacement
is shorter than 80 columns, so `build/SKILL.md` is still exactly 218 lines — its
allowlist ceiling, unmoved. No test references `CLEAN` or `verify-step.sh`.

---

## D — design-doc-split mechanical fixes

Applied 1, 2, 4, 5, 6, 7, 8. **Not 3** (`cli-and-package.md`'s duplicate H2), as
instructed — it is open question 2 in that report. Every old string was verified
present before replacement; none required a second attempt.

| # | File | Old → new |
|---|---|---|
| 1 | `.claude/rules/design-work.md` | `(`docs/design.md`, `plugin/fragments/`, …)` → adds `` `docs/decisions.md` and the `docs/references/` node it points at `` |
| 2 | `CLAUDE.md` §Design Decisions | four scope lines widened per Major 2 — pipeline-contracts gains the session boundary and artifact provenance; execution-routing gains classification and escalation tiers; quality-gates gains skill step and rule placement; project-configuration gains what a sub-agent gets, naming, script-versus-delegate |
| 4 | `docs/references/testing.md` | trailing blank line removed (`tail -c 3` was `. \n \n`, now `e . \n`) |
| 5 | `docs/references/deliverable-review.md` | same, verified the same way |
| 6 | `docs/changelog.md` | `…cross-references that became paths` → `…, with two more repointed in the retained hub` |
| 7 | `agents/learnings.md` | `technical details → `docs/design.md`` → adds `a decision → a `docs/references/` node plus its `docs/decisions.md` line` |
| 8 | `agents/README.md` | `older entries graduate into `docs/design.md`` → adds `, or into a `docs/references/` node plus its `docs/decisions.md` line` |

Neither `.claude/rules/design-work.md` nor `CLAUDE.md` was write-protected in
this sandbox; both edits landed, so no hand-off was needed. Nothing from the
report's "Needs my human partner's call" list was acted on.

---

## E — docs coupling, and the FR/NFR tables

### Reference nodes

- `docs/references/quality-gates.md` D-46 — the automated-checks layer now reads
  `` `just precommit` — `ruff format --check`, a non-fixing markdown reflow check, line limits, lint, tests ``.
  Closes `small-defects.md` item 5's docs note, which said to record it "once
  item 5 is resolved either way".
- `quality-gates.md` D-49 — adds: the script's success line names the checks
  that passed, `CLEAN: tree clean, just precommit passed`, "because a bare
  `CLEAN` is indistinguishable from a check that never ran".
- `quality-gates.md` D-48 — required for B. Old: "The index is already in
  context (D-72), so instructing a Read of it buys a redundant tool call". New:
  *normally* in context, an *unconditional* Read is the redundant one, "normally
  is not always", the Read is conditional and "never becomes the anchor". D-48's
  conclusion line is unchanged, so `decisions.md` needed no edit for it.
- `docs/references/project-configuration.md` D-69 — new paragraph on the
  allowlist. **Where the format is argued:** only where it is implemented — the
  header comment of `scripts/check_line_limits.sh`, restated in the sidecar's
  own header. No node argued it. The paragraph names that, states the
  `<path><TAB><ceiling><TAB><note>` shape and exact root-relative matching, and
  records the carriage-return rejection as exit 2 rather than a silently
  unmatched path, "because a CRLF sidecar would make every entry miss while the
  gate still reported success".
- `docs/references/pipeline-contracts.md` — two new decisions, appended after
  D-80 to match how D-80 itself sits. **D-84** (GREEN scoped to its slice; a
  slice already implemented is proven by mutation) carries the grounding, the
  fallback, the per-named-test rule and the three-way reconciliation. **D-85**
  (the recall checkpoint resolves skills, and Reads the index when it is not in
  context) carries the cache path, the glob and the false premise.
- `docs/decisions.md` — two index lines added to the Pipeline contracts group,
  IDs continuing the sequence past D-83. Every conclusion line is a byte-prefix
  of its node's bolded lead, the invariant the split review measured.

### Changelog

Three dated 2026-09-21 entries, newest-first above the 2026-09-20 split entry:
the GREEN scoping and mutation fallback; recall resolving skills; and
`ruff format --check` joining the gate (with the `verify-step.sh` sign-off in
the same entry, since both are the same gate's output).

One thing to flag. My three entries pushed `docs/changelog.md` to
**exactly 400 lines**, its cap — passing, but a file parked at its cap has
stopped emitting the signal, and the next entry turns the gate red. I tightened
the entries to 389 rather than leave it there. The real fix is the per-date
split `craft:design-doc-writing` describes (`docs/changelog/<date>-<title>.md`
beside an index), which is a structural change and a decision, not something to
take mid-pass.
**Open: the changelog needs that split before it takes many more entries.**

### The FR and NFR tables — converted

`craft:design-doc-writing` does prescribe it, explicitly and not by inference.
`references/writing-style.md` §Prose over tables:
"**FR and NFR rows usually are not** [tabular]: a requirement stated as a
sentence is neither short nor uniform, so those sections take the same bolded
lead-in prose as decisions, each carrying its id, the statement, the status and
the `Where · pinned by` pin inline. Numbering survives the move."

So `docs/design.md` §3.1, §3.2 and §4 are now bolded lead-in prose, one
paragraph per requirement. §2's status legend stays a table — its cells are
short and uniform, which is the skill's own test.

Verification that nothing was lost:

- **ID multiset identical.** `grep -oE '\b(FR|NFR)-[0-9]+' | sort | uniq -c`
  before and after: `diff` empty, including the two ids that legitimately appear
  twice (FR-9, NFR-1) and the retired FR-19/FR-20 mentions.
- **Token multiset diff against `git show HEAD:docs/design.md`**, punctuation
  and table scaffolding normalised away. Only-in-before: `#`×3, `---`×12,
  `Requirement`×3, `Status`×3, `Where`×3, `pinned`×3, `by`×3 — the three table
  header rows and nothing else. Only-in-after: **empty**. So no requirement
  text, no status, no `Where · pinned by` target and no cross-reference was
  dropped.
- NFR-2's `\|\| true` lost its table-mandated backslashes and is now `|| true`.
  Rendered output is unchanged; the escaping was a table artifact.
- The header row's column labels are the one thing that went, so §3 gains a
  two-line lead-in stating the form, and each entry keeps the `·` before what
  pins it.
- No live file cites design.md §3 or §4 — `grep -rnE '§\s*[34]\b'` over the tree
  hits only `plugin/skills/build/SKILL.md`'s own §4.x sections and frozen
  `plans/` reports.

`docs/design.md` went 288 → 339 lines, well inside its 400 cap and off the
allowlist as the split left it.

**One unrelated staleness fixed in passing.** `docs/design.md` §5.1 said the
version-consistency check requires equal versions "— currently `0.1.1`"; the
tree is at `0.2.0`. That clause is a measurement of mutable state, which the
design-doc skill rules out of a living doc, and it was already false. Clause
deleted rather than refreshed, per that rule.

---

## What I deliberately left

- **Where a slice's GREEN report is committed** (F-1). Named as an open fork in
  the changelog entry and untouched in the skills.
- **`brief-triage.md` M2–M7, M9–M11.** Not in this dispatch; several land in the
  same files and M4/M5/M9 are job (b)'s single pass over `tdd-slice.md`.
- **`independent-review.md` fix 3** and its whole "Needs my human partner's
  call" list, including the `memory/` edit (finding 3) — `memory/` is a gitlore
  submodule.
- **`plans/skill-reviews/recall.md` M1** (the `gitlore:recall` duplication and
  trigger collision), M3, M5 and the m-items. M1 is the largest structural
  change in that review and is a fork about how much of gitlore's body edify
  keeps.
- **`run-lint-checks`** (used by `check`/`lint`/`green`/`red-lint`) still has no
  `ruff format --check`; `format-fix.md` flagged it as a scope call for whoever
  owns `check`.

## Open questions

1. **The changelog split.** Above. Needs a decision before the next entry.
2. **Retiring `plugin/fragments/token-economy.md`.** Nothing in the tree routes
   to it. Fixed in place rather than deleted.
3. **`docs/design.md` §6's node list vs `CLAUDE.md`'s routing table.** Fix 2
   widened only the `CLAUDE.md` copy, which is what the report specified. The
   two surfaces are now worded differently on purpose — that is finding 6, the
   consolidation question, left open.

## Observable state note

`git status --porcelain` shows five untracked `.claude/` paths that were not in
the session-start snapshot: `launch.json`, `loop.md`, `output-styles/`,
`routines/`, `workflows/`. They are harness-managed (my earlier grep could not
read them), not written by me, and I left them alone.

---

## `just format` then `just precommit` — full output

`just format`, final run:

```
**Reformatted files:**
  - docs/references/pipeline-contracts.md
  - plugin/skills/build/references/tdd-slice.md
  - plugin/skills/recall/SKILL.md
```

`UV_CACHE_DIR="$TMPDIR/uv-cache" just precommit`, untruncated:

```
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
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

All nine `oversized-file:` lines are pre-existing allowlist entries at their
exact recorded ceilings — disclosure, not failure, and byte-identical to the
list in `format-fix.md` and `small-defects.md`. `docs/design.md` is absent from
it, as it has been since the split. Not one file this pass touched is reported.

**On `Tests cached`:** the sentinel hashes
`git ls-files src/ tests/ plugin/hooks/ plugin/bin/` plus `pyproject.toml` and
the Python version (`justfile` `run-pytest`). This pass changed none of those —
every edit is markdown plus `CLAUDE.md` and `.claude/rules/` — so the cache is
valid and these changes cannot reach the suite. The last real run in this
session (`format-fix.md`) recorded 336 passed, 1 xfail.

Checks that passed in the run above: version consistency, the cached test suite,
`ruff check`, `ruff format --check`, `docformatter -c`, `mypy`, `rumdl` and line
limits.
