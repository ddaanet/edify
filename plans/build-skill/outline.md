# Build skill — merge `/inline` and `/orchestrate` into `/build`

Moderate / agentic-prose. Grounded in `plans/build-skill/inventory.md`,
whose §0 records the six claims this plan's proof pass found wrong and
corrected in place. Proofed 2026-09-17: all 14 items revised.

This file is an `outline.md` because the `inline-plan.md` artifact kind is
removed by this merge (below) and the agentic-prose route now produces an
outline like every other design route.

At 589 hard-wrapped lines this plan runs over the 400-line soft cap. Split
considered and declined 2026-09-17, after execution: the seam was building
the new skill versus repointing everything that named the old ones, and both
halves are now executed. Splitting a finished plan buys its next reader
nothing and costs the cross-referencing.

## Scope

### New skill

**`plugin/skills/build/SKILL.md`** (new, composed; target ~200 lines per the
SKILL.md hub budget, bounded overage acceptable per `line-caps` — one
cohesive lifecycle document, and fragmenting it costs the reader more than
the overage).

Structure: inline's lifecycle spine wrapping orchestrate's item machinery.

1. **Frontmatter** — `name: build`; description names both the runbook entry
   and the no-runbook entry, and does not reuse inline's over-broad
   `run task` trigger. `allowed-tools` takes orchestrate's wider set
   (`Agent, Read, Write, Edit, Bash, Skill, SendMessage, TaskOutput,
   TaskStop`) — inline's narrower set cannot express resume-and-escalate.
   `Skill` stays for the §3 recall anchor.
2. **§1 Load the work.** Replaces orchestrate §1 and inline §Entry Points.
   In order: `plans/<job>/runbook.md`, else `design.md` / `outline.md`, else
   take the task from the invocation. Existence is tested, not
   Read-and-caught: a missing runbook is a fallback, not an error. Keep
   orchestrate's STRICT SEQUENTIAL rule verbatim.
3. **§2 Entry gate.** From inline Phase 1 unchanged in substance: clean-tree
   check, `just precommit`, baseline captured to a file. **Rename
   `tmp/inline-baseline` → `tmp/build-baseline`**, keeping the "a file, not
   a shell variable" rationale — each Bash call is its own shell. The STOP
   messages name `/build`. The clean-tree check is `verify-step.sh`, not an
   inline `git status` (see §Moved references).
4. **§3 Pre-work.** From inline Phase 2, now **unconditional**. The
   cold-start-vs-chained `execute` token and its justification paragraph are
   deleted — **not** because one entry point removes the distinction (it
   does not; `/design` still chains in with context loaded), but because
   inline's own body records the token failing open and invisibly: a dropped
   token silently re-runs a recall pass, and nothing in the output says so.
   Unconditional pre-work trades one cheap duplicate recall for that whole
   failure class. Brief check, recall (the D+B anchor, invoked by path per
   the recall contract), reference loading.
5. **§4 Execute.** Merges orchestrate §2.1 and §2.2 into one section: walk
   the work in order; per item decide **at dispatch time** whether to do it
   directly or delegate, per the batching rule. The phase-type token plays
   no part in that choice. **Carry orchestrate §2.1's self-review guardrail
   into the direct branch:** an item executed in-session is reviewed by
   `git diff` only when every self-review condition in
   `plugin/fragments/review-requirement.md` holds, otherwise it dispatches
   `edify:corrector` in checkpoint form — the threshold is the fragment's,
   not the executor's judgement. Per-item choice makes that branch more
   common, so the guardrail must not be lost in the collapse. TDD items
   route to the reference node. Keep orchestrate §3 Post-Item Verification
   (`verify-step.sh`, exit 0/1/2 taxonomy) intact, with the script's path
   updated.
6. **§5 Phase boundary.** From orchestrate §4, applying only where the work
   came from a phased runbook; state that it is skipped otherwise. Its
   clean-tree check is `verify-step.sh`.
7. **§6 Review gate.** From inline Phase 4a, carrying the routing table,
   the fix-capable/report-only split, the structural-proof Read and Path B.
   **This is where the carried defect is fixed** (below).
8. **§7 Triage feedback.** From inline Phase 4b. `triage-feedback.sh` needs
   no change — it takes a generic `<job-dir> <baseline-commit>` pair and
   contains no `inline` string. Only the baseline filename in the call
   changes.
9. **§8 Completion.** From orchestrate §6: final review, TDD audit, run
   summary, `/deliverable-review plans/<job>` follow-up. Absorbs inline 4c,
   which is the same handoff stated once. **The final review keeps a
   coverage guard, re-derived:** orchestrate gated it on phase-boundary
   checkpoints, which a no-runbook job never reaches. Gate it on §6 instead
   — where §6's review gate already covered the whole diff, §8 does not
   dispatch a second corrector over the same changes. The run summary names
   the follow-up; the skill never writes `.claude/handoff-task.md` itself.
10. **§9 Escalation** — orchestrate §5's 2-level model and its four
    stop-triggers, in the body (see below).
11. **§References** — the index, restored (see below).

**`/build` is not a cooperative skill**: no `continuation:` frontmatter
block, no `## Continuation` section. Agents chain unaided now; the
continuation machinery over-compensated for a failure mode that no longer
exists. Its future is handoff-plugin-driven *handoff-and-continue* and
*precompact-commit-and-continue*, conditioned on context usage — a different
mechanism, so this one is not preserved as an extension point here.

**`/build` is a lean hub.** It reaches for subagent ceremony only where the
work needs it; the simple case stays fast and in-session. That is the
property the removal of `/design`'s direct-execution path depends on
(todo), and it is why this merge does not move that path here.

### New reference nodes

- **`plugin/skills/build/references/tdd-slice.md`** (new, 55 lines measured
  from orchestrate §2.3) — verbatim in substance: the four dispatches (RED,
  test review, GREEN, code review) and the After-the-slice steps (commit the
  review fixes, refactor on signal with the opus-escalation sentence rule,
  list revision). Opt-in with an unmistakable trigger: only a tdd item
  reaches it.
- **`plugin/skills/build/references/resuming.md`** (new, ~10 lines) —
  orchestrate §5's last bullet only: resuming after a context ceiling or
  kill (last checkpoint commit, that checkpoint's verification, inventory of
  remaining work, resume from the next item), carrying its prohibition that
  `just precommit` is a pass/fail gate and not a state-assessment tool. A
  procedure whose trigger is unambiguous, and whose prohibition only bites
  once you are in it.

**Escalation does not become a node.** orchestrate §5's 2-level model and
its four stop-triggers — unexpected result with no error, missing report
file, same error from two dispatches, agent never returns — are prohibitions
against what the executor would otherwise do unprompted (improvise a fix,
proceed past a missing report). An opt-in node is never consulted at the
moment those bite. They stay in the SKILL.md body as §9, ~15 lines, with the
in-band-bound disclaimer and its `escalation-acceptance.md` pointer intact.

**`§References` is restored.** orchestrate carried a §References index;
without it the merged skill would leave four nodes and a script reachable
only from inside prose. It lists `dispatch-composition.md`,
`review-dispatch-template.md`, `tdd-slice.md`, `resuming.md`,
`scripts/verify-step.sh`, `plugin/fragments/delegation.md` and
`plugin/fragments/continuation-passing.md`.

### Moved references

- **`plugin/skills/orchestrate/references/dispatch-composition.md`** →
  **`plugin/skills/build/references/dispatch-composition.md`**. Content
  already updated this session (D-42 by artifact kind; `Model:` removed;
  two fixed assignments). One further edit, line 4: the parenthetical
  "(or from an ad-hoc task in `/inline`'s delegated path)" names a dead
  caller and a live case. **Drop the caller, keep the case** — `/build`
  composes dispatches for no-runbook work, so the file must still say it
  takes a runbook item *or* an ad-hoc task. Line 28's role word
  "orchestrator" stays, per inventory §2b.
- **`plugin/skills/inline/references/review-dispatch-template.md`** →
  **`plugin/skills/build/references/review-dispatch-template.md`**, with
  four edits:
  1. The carried defect (below).
  2. Line 3 — delegation "from /inline Phase 4a" becomes `/build` §6.
  3. Field Rules / Baseline — `tmp/inline-baseline` → `tmp/build-baseline`,
     "/inline Phase 1" → `/build` §2. This is the 5th rename call site.
  4. Field Rules / Baseline — "When `/inline execute` follows /design,
     baseline excludes design-phase artifacts" is **re-derived, not
     repointed**: the `execute` token is gone and `/design` commits before
     routing, so the exclusion is now unconditional. State it as a property
     of the baseline, not as a conditional on a dead token.
- **`plugin/skills/orchestrate/scripts/verify-step.sh`** →
  **`plugin/skills/build/scripts/verify-step.sh`**, **and promoted**.
  Verified by direct read: 32 lines, no skill-name or phase-type string, the
  only literal name is ` M memory`.

  It becomes **the skill's single definition of a clean tree**, called from
  §2, §4 and §5. Today three sites answer "is the tree clean" three
  different ways — the entry gate's bare `git status --porcelain` with no
  exemptions, this script's one-line ` M memory` exemption, and the phase
  boundary's `just precommit` with no status check at all — so a run that
  writes a memory file trips the entry gate on a state the post-item gate is
  documented to tolerate. Merging the skills puts all three in one file,
  which is when that becomes indefensible. This also makes `docs/design.md`
  D-49 true: the script is the mechanical/blocking half of the split it is
  already cited as exemplifying.

  One content change: `exec 2>&1` with `set -xeuo pipefail` dumps a full
  shell trace on every call, and tripling the call sites triples the noise
  (`plans/skill-reviews/orchestrate.md:125`). Keep `set -euo pipefail`, drop
  the trace.

**Inbound path references to the moved files**, beyond the `plugin/README.md`
entry in the prose list:

- `docs/design.md:150` — hardcoded `skills/orchestrate/references/dispatch-composition.md`.
- `docs/design.md:157` — hardcoded `skills/orchestrate/scripts/verify-step.sh`.
- `docs/design.md:160` — `triage-feedback.sh` described as "the inline
  route's post-execution gate"; the route name does not survive.

These sit in the architecture prose, not in a numbered decision, so the
design-record item's D-numbered list does not reach them. It absorbs them.
`docs/design.md:708` names `verify-step.sh` without a path and needs nothing.

### The carried defect (must not be dropped by the rewrite)

`.claude/handoff-todo.md` carries this as an open item against files this
merge rewrites. Fixing it here is cheaper than fixing it twice.

- `plugin-dev:skill-reviewer` has **Read, Grep, Glob** — no Write, no Edit,
  no Bash, no Skill. The template's prompt body tells it to fix all issues
  and write the report; it can do neither.
- **Extend the accommodation that already exists, do not add a second one.**
  The Field Rules already carve out report-only reviewers for the *recall*
  line ("which have Read but no `Skill` tool"). Fold the fix-and-write
  problem into that same carve-out so there is one report-only variant, not
  a recall exception beside an unrelated write exception.
- **Two live sites describe the tool list wrongly, in different ways** —
  inline Phase 4a says "Read plus Bash `rg` only" (there is no Bash), and
  the Field Rules say "Read but no `Skill` tool" (omitting the Write/Edit
  absence that is the actual defect). Both are corrected to the real list.
  `Grep` and `Glob` are tools, not `rg`; a prompt instructing `rg` fails.
- The report-only variant is explicit: the reviewer **returns** its findings,
  and the **calling session** writes them to the report path and applies the
  fixes.
- The structural-proof Read then finds a file that exists, so the gate stops
  blocking for skill definitions.
- The template carries the **chunked-return instruction up front** — a reply
  is cut at roughly 4000 characters, confirmed four times out of four, and a
  chunk instruction given at spawn worked every time. Each part ends with a
  continuation line, the last with a fixed end marker; without the marker a
  truncated report reads as complete.
- Report path: one rule. `plans/<job>/reports/review-<group>.md`, and the
  structural proof reads the path it actually dispatched.

### Deletions

Ordering: **the three moves in §Moved references run first**, as `git mv`,
then the directories are removed. Both directories are named as deletion
targets while three of their five files are move sources; deleting first
destroys the sources. `git mv` keeps history attached — the exit condition
is a grep audit rather than a diff read, so nothing downstream would catch a
move recorded as delete-plus-add.

After the moves, the deletion is **two files**:

- **`plugin/skills/inline/SKILL.md`** (174 lines) — absorbed into
  `build/SKILL.md`.
- **`plugin/skills/orchestrate/SKILL.md`** (202 lines) — absorbed into
  `build/SKILL.md` and the `tdd-slice.md` / `resuming.md` nodes.

Then `plugin/skills/inline/` and `plugin/skills/orchestrate/` are removed,
including the now-empty `references/` and `scripts/` subdirectories.

Deleted outright, not archived; git history is the archive. Diff arithmetic
for review: five files leave, three reappear under `plugin/skills/build/`,
two are gone.

### Phase type `inline` abolished

- **`plugin/skills/runbook/references/runbook-format.md:14`** — header format
  becomes `(type: tdd|general)`.

  While this file is open, fix its signposting. The general item format is
  **not** missing — §Structure specifies it as the base item shape, and
  `### tdd items: Slices` adds `Slices:` on top (inventory §0). Do not write
  a new format section; that would duplicate §Structure and drift. What is
  missing is ~10 lines:
  - A short worked example under a heading reading
    `## Phase N: <title> (type: general)`. The file's only general item
    (Example, Item 2.2) currently sits under a `(type: tdd)` heading, so no
    general phase is visible anywhere.
  - Marking the tdd-only sections as tdd-only: §Assertion quality,
    §Ordering, and the four test-specific §Item-level rules (no presentation
    tests, no weak assertions, no unit-only coverage, no mocked subprocess).
    Unlabelled they read as binding on general items, which have no tests.
    §No split prose edits is the rule that *is* general-specific; say so.
- **`plugin/skills/runbook/SKILL.md:37,40-41,45`** — the three-type
  vocabulary becomes two. On :45, `inline → no dispatch` goes and
  `general → one dispatch` is replaced by the statement that delegation is
  decided at dispatch time. `tdd → four dispatches per slice` stays: type
  still determines item format and tdd's dispatch structure, and no longer
  determines whether delegation happens.
- **`plugin/fragments/workflows-terminology.md`** — the Phase type row; the
  "and dispatch" clause narrows with :45.
- **`plugin/skills/design/SKILL.md:21`** — per-phase typing guidance; the
  "prose/config the orchestrator applies itself" clause goes with the type.

`docs/design.md:144` names the three types in architecture prose, outside
D-30. The design-record item absorbs it, with `:150`, `:157` and `:160`.

### Inbound references — the executable ones first

These are mechanism, not documentation. A missed prepend routes to a skill
that is gone.

**Routes to `/build` do not tail-call.** `/build` is not a cooperative skill,
so a prepend-and-tail-call hands it a continuation remainder it will never
consume, silently orphaning `/handoff:handoff` and `/commit-commands:commit`.
Where `/design` routes to `/build`, it names the next command and ends. The
`/runbook` branch at `:185` keeps its prepend — `/runbook` is still
cooperative.

**The Simple route produces an `outline.md`**, proofs it, commits, and routes
to `/build` — the same four steps as the Moderate agentic-prose route, which
now produces the same artifact. **The two routes collapse into one.** Say so
in `design/SKILL.md` rather than leaving two identical branches.

- **`plugin/skills/design/SKILL.md:133,137,143-145`** — the Simple and
  Moderate-agentic-prose route steps, collapsed to one route generating
  `outline.md`. The `execute` token is dropped everywhere.
- **`plugin/skills/design/SKILL.md:185`** — the step-2 prepend table. The
  Simple / agentic-prose / execution-ready row stops being a prepend and
  becomes "route to `/build plans/<job>`, no tail-call".
- **`plugin/skills/design/SKILL.md:22`** — §Downstream Consumers Execution
  line names `/build`.
- **`plugin/skills/design/references/write-design.md:88`** — execution-ready
  branch; no tail-call, names `/build`.
- **`plugin/skills/design/references/write-outline.md`** — **seven sites**
  (inventory §0): 209 the prose hard gate, 210 and 211 the Investigation and
  Exploration branches, 217 the `**Inline criteria**` heading, 224
  `Inline execution bypasses /runbook`, 226 the execution-ready route. All
  name `/build`.
- **Generic-English hits that stop being generic:**
  `write-outline.md:222` and `write-design.md:84` — "Scope fits inline
  capacity (single session, single model)". Inventory §2b leaves
  generic-English `inline` alone, but 222 sits under the heading renamed at
  217, leaving "inline capacity" as a dangling term of art. Both become
  "single-session capacity", which is what each parenthetical already says.
- **`plugin/fragments/continuation-passing.md`** — deletions only. `/build`
  never enters this file:
  - §Cooperative Skills — drop the `/inline` and `/orchestrate` rows. No
    `/build` row is added.
  - §Pivot Transactions — drop the `/inline (delegated)`, `/inline (direct)`
    and `/orchestrate` rows. No re-derivation: it would only have existed to
    repartition a claim for `/build`, and `/build` is not described here.
  - §How It Works, §Worked Examples, §Transport Format, §Orphaned
    Continuation Recovery — repoint the `/orchestrate` illustrations to
    `/runbook`, which is still cooperative.
  The fragment then describes exactly `/design` and `/runbook` — the surface
  the retirement todo removes next.

### Inbound references — prose

**Cite by string, not by line** (inventory §0 records why). Each entry names
the text to match.

- `plugin/fragments/delegation.md` — the `/orchestrate` framing sentence
  ("When executing runbooks via `/orchestrate`…") and **three** hardcoded
  `plugin/skills/orchestrate/references/dispatch-composition.md` paths
  (§Model assignment, §the dispatcher composes, §One artifact model).
- `plugin/fragments/workflows-terminology.md` — **two rows, not one.** The
  Runbook row ("Phased implementation plan `/orchestrate` dispatches from")
  and the Phase type row, which is the phase-type item's.
- `plugin/fragments/workflows-terminology.md` — **add an Orchestrator row.**
  About thirty sites across `plugin/agents/` and `plugin/fragments/` use
  "the orchestrator" as a role word and stay per inventory §2b, but with
  `/orchestrate` gone the word has no defined referent. One row defining it
  as the role the executing skill plays — decoupled from any skill name —
  resolves all thirty without editing them.
- `plugin/agents/corrector.md` — "`/orchestrate` dispatches this agent twice
  per TDD slice". Its other three hits are role words and stay.
- `plugin/skills/runbook/SKILL.md` — description line, the
  `→ /proof → /orchestrate` pipeline chain, and the §Continuation
  fresh-session note ("orchestration runs in a fresh session",
  "the orchestrator needs its own"), which are role words whose claim stays
  true for `/build`.
- `plugin/skills/runbook/references/runbook-format.md` — the opening
  "`/orchestrate` reads it and composes each dispatch prompt from it live",
  and "the id `/orchestrate` uses in dispatch names and slice commit
  subjects". Also repoint the bare `dispatch-composition.md` filename in the
  no-model paragraph to its new full path — it does not resolve today
  either.
- `plugin/skills/requirements/SKILL.md` — triage routing note
  ("its triage routes small work to `/inline`").
- `plugin/skills/review/SKILL.md` — workflow list entry
  ("`/orchestrate` — Executes runbook").
- `plugin/README.md` — the pipeline line in the opening paragraph, the two
  skill-table rows that become one, the `/design` row's "routes simple work
  straight to `/inline`", and the `verify-step.sh` path with its
  "`/orchestrate` runs after each committing dispatch" sentence.
- `README.md` — pipeline prose ("`/design` → `/inline` for work that needs
  no runbook").
- `CLAUDE.md` — the Workflow pipeline bullet, and the hardcoded
  `plugin/skills/orchestrate/references/dispatch-composition.md` path in the
  delegates-by-reference paragraph.

`docs/changelog.md`'s `/orchestrate` mentions are historical entries and stay
per Boundaries OUT; they will appear in the audit and classify as accurate.

### `inline-plan.md` artifact kind removed

Not renamed. `inline-plan.md` is an `outline.md` with the architecture
section left empty — every field it has (affected files, per-file changes,
IN/OUT boundaries, dependencies), a sufficient outline has, and
`write-outline.md:203` already says "The outline IS the design" when its
sufficiency criteria hold. The artifact has no identity of its own, only a
consumer, which is exactly why it ended up named after one. Renaming it
`build-plan.md` would carry that defect forward under a cleaner name.

- **`plugin/skills/design/references/write-inline-plan.md` is deleted.** Its
  two contributions not already in `write-outline.md` — read the affected
  files before writing, and record what changes rather than why the approach
  was chosen — fold in as a note on the agentic-prose branch.
- **`plugin/skills/design/SKILL.md:143,144`** — the generate step and the
  `/proof` invocation directly below it both name `outline.md`. The
  agentic-prose branch stops being a separate artifact path.
- **Two lines die with the file rather than moving:**
  - `:31`'s citation of a "/proof Corrector Dispatch table" row. No such
    table exists (`plans/skill-reviews/proof.md:19`, verified against
    `plugin/skills/proof/`).
  - `:32`'s status line `inline-planned → /inline plans/{plan}` (parallel to
    `planned` → `/orchestrate`). Neither token appears anywhere else in the
    repo (`plans/skill-reviews/design.md:112`): no reader, no writer.

The artifact map after this merge:

| Artifact | Means | Goes to |
|---|---|---|
| `design.md` | architecture was uncertain and needed full resolution | `/runbook` |
| `outline.md` | architecture known, or resolved within the outline | `/runbook` or `/build` |
| `runbook.md` | decomposed into typed phases | `/build` |

`outline.md` keeps both consumers: the Moderate non-prose route sends it to
`/runbook`, the agentic-prose and Simple routes to `/build`.

### Design record

- **`docs/design.md` §1 Now** (13-16, 22-25) — the focus line names the
  pipeline as `/design` → `/runbook` → `/orchestrate`. §1 is the
  current-state layer and the first thing a reader sees; it goes stale
  first.
- **`docs/design.md` D-28** (473-477) — the bounded-review paragraph: "when
  the orchestrator executes an `inline` item itself… review follows the
  proportionality rule". **Re-derive, do not repoint.** The `inline` item
  type is abolished, but the rule survives and widens: it now binds whenever
  the executor does an item directly, which §4 of the new skill makes a
  per-item decision. This is the design record of the guardrail §4 carries.
- **`docs/design.md` D-30** (491-509) — phase types become `tdd`/`general`;
  the paragraph defining when a phase qualifies as `inline` goes.
- **`docs/design.md` D-34** (541-553) — the route split is the decision this
  merge reverses. Rewrite as the decision to merge, stating what the split
  cost and why one skill replaces it. **Carry forward its closing sentence**
  — "the inline-versus-delegated distinction survives … as an
  execution-level choice, not a route" — which the merge completes rather
  than contradicts, and which is the principle the merged §4 is built on.
- **`docs/design.md` D-37** (569) — "Simple classification still routes
  through `/inline`" becomes the `/build` route, paired with the Simple
  route producing an `outline.md` and committing. Its own point —
  classification determines design ceremony, not execution ceremony —
  survives unchanged.
- **`docs/design.md` FR-8/FR-10/FR-11** (59,61,62) — FR-8's **requirement
  text** names `/inline`, not just its Where column. FR-10 and FR-11 both
  come to point at `skills/build/`; **keep them as two requirements**. They
  are two obligations one component now serves, and merging them would drop
  the runbook-less lifecycle, which is the obligation the no-runbook path
  exists to honour.
- **A new decision records the artifact map** above: three artifacts, two
  design routes, one execution skill, and `inline-plan.md` removed as a kind
  rather than renamed.
- **`docs/design.md` architecture prose** — absorbed from the moved-reference
  and phase-type items: `:144` (the three phase types), `:149-150`
  (hardcoded `skills/orchestrate/references/dispatch-composition.md`),
  `:157` (hardcoded `skills/orchestrate/scripts/verify-step.sh`), `:160`
  (`triage-feedback.sh` as "the inline route's post-execution gate").
- **`docs/changelog.md`** — one new entry dated 2026-09-17. Existing entries
  are historically accurate as written and are not rewritten.

### Memory

`memory/workflow-pipeline-revival.md` is the canonical stale-name map — the
file a future session consults when it meets an old name in a frozen plan,
and the frozen `plans/` trees are full of these names.

**Three surfaces, not one.** The body is read only after the hook matched.

1. **Body** — add four rows to the stale-name map:
   - `/inline`, `/orchestrate` → `/build`
   - phase type `inline` → removed; delegation is decided at dispatch time
   - `inline-plan.md` → removed as a kind; the artifact is `outline.md`
   - `skills/inline/`, `skills/orchestrate/` → `skills/build/`
   These qualify under the file's own "names no other artifact maps" rule:
   no single artifact states all four. Add the pointer sentence naming the
   `docs/changelog.md` 2026-09-17 entry, matching how the 2026-08 and
   2026-09-01 rewirings are handled.
2. **Frontmatter `description`** — add `/inline`, `/orchestrate` to the name
   list. This is half the routing hook.
3. **`memory/MEMORY.md`** — the same addition to this entry's index line.

**Keep both hook additions to the bare names.** Measured 2026-09-17:
`MEMORY.md` is 26661 bytes against a 25600-byte loader cap; the cutoff falls
at line 86 of 88, so two entries are dropped today. This entry's line is at
byte 20665 and loads fine, but ~60 further bytes puts line 85 at risk as
well. The `/gitlore:index-audit` pass on the Remaining list is the fix; this
item must not make it worse than it has to.

## Boundaries

**IN**

- The merged skill `plugin/skills/build/SKILL.md`, **not cooperative** and a
  lean hub: no `continuation:` frontmatter, no `## Continuation` section,
  subagent ceremony only where the work needs it.
- Its reference nodes — `tdd-slice.md`, `resuming.md`, and the moved
  `dispatch-composition.md` and `review-dispatch-template.md` — plus a
  restored `§References` index. Escalation's 2-level model and four
  stop-triggers stay in the body as §9, not a node.
- `verify-step.sh` moved **and promoted**: the skill's single definition of a
  clean tree, called from §2, §4 and §5, replacing three divergent inline
  checks. Shell trace dropped.
- Deletion of both source skill directories — after the three `git mv`s, two
  `SKILL.md` files.
- Phase type `inline` removed from every definition and consumer.
- `runbook-format.md` signposting: a `(type: general)` example, and the
  tdd-only sections marked as such. **Not** a new general-item format
  section — §Structure already specifies it.
- Every executable prepend and prose reference listed above, cited by string
  rather than line. Routes to `/build` name the next command and do not
  tail-call.
- `continuation-passing.md` reduced by deletion only; `/build` never enters
  it.
- An Orchestrator row in `workflows-terminology.md`, giving ~30 surviving
  role-word sites a referent.
- The report-only reviewer defect, carried from the todo, folded into the
  existing report-only carve-out.
- `tmp/inline-baseline` → `tmp/build-baseline` (5 call sites, 2 files —
  count verified).
- **`inline-plan.md` removed as an artifact kind**, `write-inline-plan.md`
  deleted, and the Simple and Moderate-agentic-prose routes collapsed into
  one route producing `outline.md`.
- `docs/design.md` §1 Now, D-28, D-30, D-34, D-37, the FR-8/10/11 rows, a
  new artifact-map decision, and the architecture prose at `:144`,
  `:149-150`, `:157`, `:160`; one changelog entry dated 2026-09-17; the
  `workflow-pipeline-revival` memory entry across all three of its surfaces.

**OUT**

- **Every `plans/` directory except `plans/build-skill/`.** Frozen, dated
  records; the stale-name map is how a reader resolves them. Stated as a
  rule, not a list — see inventory §0 for why, and for the measured baseline
  of 380 stale-name hits across 9 directories. `plans/README.md` is a living
  index, not frozen; its stale `prepare-runbook.py` reference is separate
  cleanup.
- **Removing `/design`'s direct-execution path** — the Phase B / C.5
  execution-ready branch that bypasses `/runbook` and implements in the
  design session. Decided, recorded as a todo with the other `/design` work.
  This merge only makes it possible by giving `/build` a fast simple path.
- **Retiring continuation-passing from `/design` and `/runbook`** — the
  frontmatter blocks, the `## Continuation` sections and the fragment
  itself. Recorded as a todo. This merge only stops `/build` participating
  and deletes the rows naming the two dead skills.
- **`docs/superpowers/**`** — predates the current shape entirely.
- **`agents/learnings.md`** — accurate history of past defects. Its
  `:71-72` pointer to "the inline skill's template" will dangle; that is
  what a learnings log is.
- **Existing `docs/changelog.md` entries** — only a new entry is added.
- **The ~30 "orchestrator" role-word sites** in `plugin/agents/` and
  `plugin/fragments/` — they stay per inventory §2b, given a referent by the
  new `workflows-terminology.md` row rather than by 30 edits.
- **The four resolved conflicts** — entry gate, review routing scope, commit
  ownership, escalation taxonomy are settled (richer of the two wins in each
  case) and are not reopened during execution.
- **Skill-body length targets per class** (FR-12 remainder) — no
  calibration data, tracked separately.
- **`/recall` loading skills** — deferred, `inbox/recall-skill.md`.

## Dependencies

1. **Claims, not just paths** (`feedback-stale-claims-survive-reference-sweeps`).
   Before rewriting any reference, ask whether the sentence's *claim* still
   partitions the world the way it did. Four instances in this plan alone:
   the `execute`-token justification (the token distinguished cold start
   from loaded context, which was never skill-keyed);
   `dispatch-composition.md:4`'s parenthetical (a dead caller and a live
   case in one clause); `review-dispatch-template.md`'s baseline rule
   (conditional on a token being removed, so the condition becomes
   unconditional); and `docs/design.md` D-28 (triggers on a type being
   abolished, while its rule must survive and widen).

2. **Audit exit condition** (`reference-audit-after-a-move`). Completion is
   **not** "the diff looks right". It is a whole-tree grep for `/inline`,
   `/orchestrate`, `edify:inline`, `edify:orchestrate`, `skills/inline`,
   `skills/orchestrate`, `inline-baseline`, `inline-plan`, `inline-planned`
   and `build-plan`, with **every hit classified** accurate-or-stale.
   Inventory §0 records where its own cites were wrong and by how much —
   read it before trusting a line number, and cite by string. Generic-English
   "inline" and role-word "orchestrator" hits are catalogued in inventory
   §2b and stay, except `write-outline.md:222` and `write-design.md:84`,
   which become "single-session capacity".

   Report claims are not evidence either: verify each finding against the
   file before acting on it (inventory §0 has an instance that was already
   fixed in source).

3. **Verification needs a restart.** A skill listing resolves at startup, so
   `/build` is not invocable in the session that creates it and the deleted
   skills stay resolvable. Nothing errors either way. Verify via
   `handoff:restart`, which preserves the conversation, before claiming the
   skill works.

4. **No mechanical coupling to discharge.** Verified by direct read: no
   manifest enumerates skills (auto-discovery from
   `plugin/skills/*/SKILL.md`), nothing under `tests/` or `src/` mentions
   `plugin/skills`, no script parses a phase type, and
   `scripts/check_line_limits.sh` scans only `src`/`tests` for `*.py` and
   `agents/decisions` for `*.md` — so nothing will flag an oversized
   `SKILL.md`. Measure it by hand, after hard-wrapping, per `line-caps`.

5. **Commit shape** (`commit-bundling`). The source change, the design
   record, the changelog entry and the memory edit correspond to one
   another and ride one parent-repo commit, including the memory gitlink
   bump. Never commit inside the memory submodule.
