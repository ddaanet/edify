# Build skill — merge `/inline` and `/orchestrate` into `/build`

Moderate / agentic-prose. Grounded in `plans/build-skill/inventory.md`
(verified 2026-09-16) and a full read of both SKILL.md bodies.

## Scope

**Affected files** — enumerated from the verified inventory, not from
assumption.

### New skill

**`plugin/skills/build/SKILL.md`** (new, composed; target ~200 lines,
bounded overage acceptable per the `line-caps` rule — this is one cohesive
lifecycle document and fragmenting it costs the reader more than the overage).

Structure: inline's lifecycle spine wrapping orchestrate's item machinery.

1. **Frontmatter** — `name: build`; description names both the runbook entry
   and the no-runbook entry, and does not reuse inline's over-broad
   `run task` trigger. `allowed-tools` takes orchestrate's wider set
   (`Agent, Read, Write, Edit, Bash, Skill, SendMessage, TaskOutput,
   TaskStop`) — inline's narrower set cannot express resume-and-escalate.
2. **§1 Load the work.** Replaces orchestrate §1 and inline §Entry Points.
   Read `plans/<job>/runbook.md` if present; else the proofed `design.md` /
   `outline.md`; else take the task from the invocation. No preflight Read
   that fails — a missing runbook is a fallback, not an error. Keep
   orchestrate's STRICT SEQUENTIAL rule verbatim.
3. **§2 Entry gate.** From inline Phase 1 unchanged in substance:
   `git status --porcelain` non-empty → STOP; `just precommit` failure →
   STOP; baseline captured to a file. **Rename `tmp/inline-baseline` →
   `tmp/build-baseline`**, keeping the "a file, not a shell variable"
   rationale — each Bash call is its own shell.
4. **§3 Pre-work.** From inline Phase 2, now **unconditional**. The
   cold-start-vs-chained `execute` token and its entire justification
   paragraph are deleted: with one entry point there is nothing to
   distinguish. Brief check, recall (the D+B anchor, invoked by path per
   the recall contract), reference loading.
5. **§4 Execute.** Merges orchestrate §2.1 and §2.2 into one section: walk
   the work in order; per item decide **at dispatch time** whether to do it
   directly or delegate, per the batching rule. The phase-type token plays
   no part in that choice. TDD items route to the reference node. Keep
   orchestrate §3 Post-Item Verification (`verify-step.sh`, exit 0/1/2
   taxonomy) intact, with the script's path updated.
6. **§5 Phase boundary.** From orchestrate §4, applying only where the work
   came from a phased runbook; state that it is skipped otherwise.
7. **§6 Review gate.** From inline Phase 4a, carrying the routing table,
   the fix-capable/report-only split, the structural-proof Read and Path B.
   **This is where the open defect is fixed** (below).
8. **§7 Triage feedback.** From inline Phase 4b. `triage-feedback.sh` needs
   no change — it takes a generic `<job-dir> <baseline-commit>` pair and
   contains no `inline` string. Only the baseline filename in the call
   changes.
9. **§8 Completion.** From orchestrate §6: final review, TDD audit, run
   summary, `/deliverable-review plans/<job>` follow-up. Absorbs inline 4c,
   which is the same handoff stated once.
10. **§9 Escalation** — pointer to the reference node.
11. **§Continuation** — the two skills' near-verbatim blocks collapse to one.

### New reference nodes

- **`plugin/skills/build/references/tdd-slice.md`** (new, ~55 lines) —
  orchestrate §2.3 verbatim in substance: the four dispatches (RED, test
  review, GREEN, code review) and the After-the-slice steps (commit the
  review fixes, refactor on signal with the opus-escalation sentence rule,
  list revision). Opt-in: only a tdd item reaches it.
- **`plugin/skills/build/references/escalation.md`** (new, ~25 lines) —
  orchestrate §5: the 2-level model and the five named triggers. Consulted
  on exception, not on the happy path.

### Moved references

- **`plugin/skills/orchestrate/references/dispatch-composition.md`** →
  **`plugin/skills/build/references/dispatch-composition.md`**. Content
  already updated this session (D-42 by artifact kind; `Model:` removed;
  two fixed assignments). One further edit: line 4 names "`/inline`'s
  delegated path" as a second caller — with one skill there is one caller,
  so that clause goes.
- **`plugin/skills/inline/references/review-dispatch-template.md`** →
  **`plugin/skills/build/references/review-dispatch-template.md`**, with
  the open defect fixed (below).
- **`plugin/skills/orchestrate/scripts/verify-step.sh`** →
  **`plugin/skills/build/scripts/verify-step.sh`**. Script content
  unchanged — verified to contain no skill-name or phase-type string.

### The carried defect (must not be dropped by the rewrite)

`.claude/handoff-todo.md` carries this as an open item against files this
merge rewrites. Fixing it here is cheaper than fixing it twice.

- `plugin-dev:skill-reviewer` has **Read, Grep, Glob only**. The template
  tells it to fix issues and write the report; it can do neither. Correct
  the tool list where the template states it, and make the report-only
  variant explicit: the reviewer returns its findings, the **calling
  session** writes them to the report path and applies the fixes.
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

- **`plugin/skills/inline/`** — whole directory.
- **`plugin/skills/orchestrate/`** — whole directory.

Deleted outright, not archived; git history is the archive.

### Phase type `inline` abolished

- **`plugin/skills/runbook/references/runbook-format.md:14`** — header format
  becomes `(type: tdd|general)`. This file also needs the `general` item
  format it has never specified (inventory C1): every content section is
  tdd-shaped, and `general` is the default type.
- **`plugin/skills/runbook/SKILL.md:37,40-41,45`** — the three-type
  vocabulary becomes two; `inline → no dispatch` goes, replaced by the
  statement that delegation is decided at dispatch time.
- **`plugin/fragments/workflows-terminology.md:23`** — phase-type row.
- **`plugin/skills/design/SKILL.md:21`** — per-phase typing guidance.

### Inbound references — the executable ones first

These are mechanism, not documentation. `continuation-passing.md` executes
whatever string is prepended, so a missed one calls a skill that is gone.

- **`plugin/skills/design/SKILL.md:133,137,143-145,185`** — Simple-route
  steps. The Simple route **stops implementing** (decision 5): it produces a
  proofed artifact, commits, and routes to `/build`. The
  `/inline plans/<job> execute` prepend becomes `/build plans/<job>`, with
  the `execute` token dropped everywhere.
- **`plugin/skills/design/references/write-design.md:88`** — same prepend.
- **`plugin/skills/design/references/write-outline.md:210,211,222,226`** —
  same prepend, plus the two `→ inline` work-type routing branches, which
  now name `/build`.
- **`plugin/skills/design/SKILL.md:22`** — the §Downstream Consumers
  Execution line.
- **`plugin/fragments/continuation-passing.md`** — 16 citations. **Claims,
  not just names** (see Dependencies): the default-exit table rows for
  `/inline` and `/orchestrate` collapse to one `/build` row, and the
  commit-compensation rows must be re-derived rather than repointed.

### Inbound references — prose

- `plugin/fragments/delegation.md:3,11,28,75` — the `/orchestrate` framing
  sentence and three hardcoded `dispatch-composition.md` paths.
- `plugin/agents/corrector.md:313` — "`/orchestrate` dispatches this agent
  twice per TDD slice".
- `plugin/skills/runbook/SKILL.md:5,26,149,151` — description, pipeline
  chain, fresh-session note.
- `plugin/skills/runbook/references/runbook-format.md:5,25,35` — the
  `/orchestrate` reader references.
- `plugin/skills/requirements/SKILL.md:266` — triage routing note.
- `plugin/skills/review/SKILL.md:200` — workflow list entry.
- `plugin/README.md:4,27,28,29,30,72-73` — pipeline line, skill table rows
  (two rows become one), `verify-step.sh` path.
- `README.md:41-42`, `CLAUDE.md:183,192-193` — pipeline prose.

### `inline-plan.md` artifact rename

With `/inline` gone the artifact name is orphaned, and leaving it is exactly
the stale-name failure `workflow-pipeline-revival` exists to clean up.

- `plugin/skills/design/references/write-inline-plan.md` →
  `write-build-plan.md`; the artifact it describes becomes
  `plans/<job>/build-plan.md`; its status line
  (`inline-planned → /inline plans/{plan}`) becomes
  `build-planned → /build plans/<job>`.
- `plugin/skills/design/SKILL.md:143` — the generate step.
- `/proof`'s corrector-dispatch table row.
- **This plan file** is itself named `inline-plan.md`; rename with the rest.

### Design record

- **`docs/design.md` D-30** (491-509) — phase types become `tdd`/`general`;
  the paragraph defining when a phase qualifies as `inline` goes.
- **`docs/design.md` D-34** (541-553) — the `/inline`-vs-`/orchestrate`
  route split is the decision this merge reverses. Rewrite as the decision
  to merge, stating what the split cost and why one skill replaces it.
- **`docs/design.md` D-37** (569) — "Simple classification still routes
  through `/inline`" becomes the `/build` route, paired with decision 5's
  "design stops at a proofed artifact and commits".
- **`docs/design.md` FR-8/FR-10/FR-11** (59,61,62) — the requirement-to-path
  table maps to `skills/design/`, `skills/orchestrate/`, `skills/inline/`.
  Nothing tests documentation-to-code path correctness, so this goes
  silently wrong without a deliberate pass.
- **`docs/changelog.md`** — one new dated entry. Existing entries are
  historically accurate as written and are not rewritten.

### Memory

- **`memory/workflow-pipeline-revival.md`** — the canonical stale-name map.
  Add `/inline`, `/orchestrate` → `/build`. This is the file a future
  session consults when it meets the old names in a frozen plan, so the
  merge is incomplete without it.

## Boundaries

**IN**

- The merged skill, its reference nodes, the moved script.
- Deletion of both source skill directories.
- Phase type `inline` removed from every definition and consumer.
- The `general` item format `runbook-format.md` has never specified.
- Every executable prepend and every prose reference listed above.
- The report-only reviewer defect, carried from the todo.
- `tmp/inline-baseline` → `tmp/build-baseline` (5 call sites, 2 files).
- `inline-plan.md` → `build-plan.md` and its format reference.
- `docs/design.md` D-30 / D-34 / D-37 and the FR path table; one changelog
  entry; the `workflow-pipeline-revival` memory entry.

**OUT**

- **Frozen plan artifacts** — `plans/pipeline-simplification/**`,
  `plans/pilfer-superpowers/**`, `plans/edify-recall-skill/**`,
  `plans/blog-series/**`, `plans/reports/**`. Dated records of what was
  done; the stale-name map is how a reader resolves them.
- **`docs/superpowers/**`** — predates the current shape entirely; one file
  explicitly describes the torn-down pipeline.
- **`agents/learnings.md`** — accurate history of past defects. Its
  `:71-72` pointer to "the inline skill's template" will dangle; that is
  what a learnings log is.
- **Existing `docs/changelog.md` entries** — only a new entry is added.
- **`plans/README.md`'s `prepare-runbook.py` reference** — already stale
  before this merge, per the inventory. Separate cleanup.
- **The four resolved conflicts** — entry gate, review routing scope, commit
  ownership, escalation taxonomy are settled (richer of the two wins in each
  case) and are not reopened during execution.
- **Skill-body length targets per class** (FR-12 remainder) — no
  calibration data, tracked separately.
- **`/recall` loading skills** — deferred, `inbox/recall-skill.md`.

## Dependencies

1. **Claims, not just paths** (`feedback-stale-claims-survive-reference-sweeps`).
   `continuation-passing.md:131-132` asserts that delegated `/inline`
   execution commits per dispatch — "compensation impractical" — while
   direct execution does not. Once delegation is a **dispatch-time**
   decision rather than a skill-level property, that distinction no longer
   partitions by skill and the rows' claims are wrong, not merely
   misnamed. Re-derive from what `/build` actually does before rewriting.

2. **Audit exit condition** (`reference-audit-after-a-move`). Completion is
   **not** "the diff looks right". It is a whole-tree grep for `/inline`,
   `/orchestrate`, `edify:inline`, `edify:orchestrate`, `skills/inline`,
   `skills/orchestrate`, `inline-baseline` and `inline-plan`, with **every
   hit classified** accurate-or-stale against where things live now. Expect
   the count to exceed the inventory's; that is the audit working, not a
   defect in the inventory. "The rest are fine" is where misses hide.
   Generic-English "inline" and role-word "orchestrator" hits are catalogued
   in inventory §2b and stay.

3. **Verification needs a restart.** A skill listing resolves at startup, so
   `/build` is not invocable in the session that creates it and the deleted
   skills stay resolvable. Nothing errors either way. Verify via
   `handoff:restart`, which preserves the conversation, before claiming the
   skill works.

4. **No mechanical coupling to discharge.** Verified: no manifest enumerates
   skills (auto-discovery from `plugin/skills/*/SKILL.md`), no test touches
   `plugin/skills/`, no script parses a phase type, and
   `scripts/check_line_limits.sh` does not scan `plugin/skills/` — so
   nothing will flag an oversized `SKILL.md`. Measure it by hand, after
   hard-wrapping, per `line-caps`.

5. **Commit shape** (`commit-bundling`). The source change, the design
   record, the changelog entry and the memory edit correspond to one
   another and ride one parent-repo commit, including the memory gitlink
   bump. Never commit inside the memory submodule.
