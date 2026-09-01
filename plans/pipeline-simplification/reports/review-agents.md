# Review — agent definitions (pipeline-simplification)

## Summary

- Critical: 0
- Major: 0
- Minor: 2 (both OPEN, fixable in place)
- Out-of-scope observations: 2 (pre-existing, belong to pilfer defect 21 —
  corrector-skeleton compression/deduplication — already excluded from this
  job's scope)

**Verdict: READY.** All nine agent files match their assigned design
decisions (D2, D3, D4, D5, D6, D9, D13, D14; D12 struck). No stale C-4
vocabulary, no dangling references, no wrong-agent redirects. Model tiers
match NFR-1 (artisan/test-driver `sonnet`; corrector/runbook-corrector/
design-corrector `opus`). Two minor tools/text-consistency issues found,
neither blocking.

## Findings

### 1. `artisan.md` declares an unused `Skill` tool

**Problem:** Frontmatter `tools:` includes `"Skill"`, but the body never
invokes `Skill(...)` anywhere, and per `dispatch-composition.md` / D4,
`artisan` resolves recall by directly reading the recall artifact and the
files it lists — not by calling `edify:recall` as a skill. This predates the
job (unchanged in the `a7d9a1ce` diff) but fails the "tools minimal and
sufficient" criterion as the file now stands.

**Fix:**
- file: `plugin/agents/artisan.md:6`
- old: `tools: ["Read", "Write", "Edit", "Bash", "Skill"]`
- new: `tools: ["Read", "Write", "Edit", "Bash"]`

**Status:** FIXED (applied by the calling session)

### 2. `refactor.md`'s opus-escalation text contradicts its own Return Protocol

**Problem:** Two places describe an internal round-trip to opus that the
agent cannot actually perform and that the rest of the file does not
support:

- Lines ~52–57 ("If architectural refactoring (new abstraction,
  multi-module):"): `Escalate to opus with context` → `Opus designs
  approach` → `Execute opus-designed refactoring` → `Verify and return`.
- Lines ~88–93 ("For architectural refactoring (opus):"): `Escalate to
  opus` → `Await opus design` → `Execute opus-designed approach`.

`refactor.md`'s declared tools are `["Read", "Write", "Edit", "Bash"]` — no
`Agent` or `Skill` tool to invoke an opus sub-agent — and its own Return
Protocol treats escalation as terminal: `Escalation to opus: escalated:
[brief reason and scope]`. `plugin/skills/orchestrate/SKILL.md` §2.3
confirms the orchestrator's actual handling is `On escalated → note the
opus follow-up in the run summary`, not a synchronous opus round-trip inside
this dispatch. This text predates the job (unchanged in the `a7d9a1ce`
diff, which only removed tier language) — D3 kept "the opus escalation"
without redesigning its mechanism, so the underlying behavior is intentional
but the prose overstates what happens inside one dispatch.

**Fix (two edits):**
- file: `plugin/agents/refactor.md` (Refactoring Evaluation section)
- old:
```
**If architectural refactoring (new abstraction, multi-module):**
- Document the architectural need
- Escalate to opus with context
- Opus designs approach
- Execute opus-designed refactoring
- Verify and return
```
- new:
```
**If architectural refactoring (new abstraction, multi-module):**
- Document the architectural need and scope
- Return `escalated: <reason and scope>` — the orchestrator notes the opus
  follow-up in the run summary; this dispatch does not wait for or execute
  an opus-designed change
```

- file: `plugin/agents/refactor.md` (Step 2: Design Refactoring section)
- old:
```
**For architectural refactoring (opus):**
- Document architectural need
- Provide context (design doc, current state, warnings)
- Escalate to opus
- Await opus design
- Execute opus-designed approach
```
- new:
```
**For architectural refactoring (opus):**
- Document architectural need
- Provide context (design doc, current state, warnings) in the return
- Return `escalated: <reason and scope>` and stop — no in-dispatch opus
  round-trip
```

**Status:** FIXED (applied by the calling session)

### 3. `corrector.md` — dead "when reviewing runbooks/plans" criteria

**Problem:** Lines 293–304 ("Runbook File References" and "Self-referential
modification", both headed "when reviewing runbooks/plans") are unreachable:
Step 0 of the same file ("Runbook rejection") makes the agent refuse and
redirect to `runbook-corrector` the moment the task prompt names
`runbook.md` or the file content shows runbook markers. These two criteria
blocks can therefore never fire.

**Investigation:**
1. Scope OUT check: not explicitly listed by path, but matches "OUT:
   corrector-skeleton compression / deduplication across correctors (pilfer
   defect 21, separate work)" — this dead block is shared skeleton content,
   not something FR-3/FR-5/FR-6/D2/D5/D9 asked this job to touch.
2. Confirmed pre-existing: identical text present at baseline `a4aad0c8`
   (before this job's first commit), and the `a7d9a1ce`/`06a431ec` diffs
   that did touch `corrector.md` only reworded "steps/cycles" → "items" and
   the marker anchor — they did not add or restructure this block.
3. Codebase pattern: the three sibling correctors
   (`design-corrector.md`, `outline-corrector.md`, `runbook-corrector.md`)
   each have their own artifact-type gate and do not carry this dead block —
   `corrector.md` is the outlier, consistent with it being unrefactored
   skeleton.

**Status:** OUT-OF-SCOPE (belongs to pilfer defect 21; no fix applied)

### 4. Corrector family's recall step doesn't match the sub-agent recall contract

**Problem:** `corrector.md` (§1.5), `design-corrector.md` (§1.5),
`runbook-corrector.md` (§2 item 4), and `outline-corrector.md` (§2 item 4,
out of scope on its own but sharing the same text) each resolve recall with
`Skill(skill: "edify:recall", args: "plans/<job> — ...")` — the selective,
judgment-based "pipeline" recall model. But:

- `plugin/fragments/delegation.md` §"Recall Artifacts For Sub-Agents"
  (rewired by this job's task 6, commit `a8d0c3d2`) states: "Sub-agents have
  no parent context — they can't judge which entries are relevant, making
  selective resolution circular... Correct pattern: Flat list for sub-agent
  injection. Delegation prompt says 'resolve ALL entries.' Pipeline model
  for skills/orchestrators that have topic context for selection."
- `plugin/skills/recall/SKILL.md` itself states: "A subagent that lacks the
  index should not invoke this skill."
- `dispatch-composition.md` (D4) composes every dispatch prompt with
  "`Read plans/<job>/recall-artifact.md, then Read each file it lists`" —
  the flat-list model — for every standing agent it names, `corrector`
  included.

When `corrector`/`runbook-corrector`/`design-corrector` run as dispatched
sub-agents (slice reviews, checkpoints, `/runbook`'s gate, `/design`'s
gate), their own §1.5/§2-item-4 step reaches for the selective Skill call
instead of the flat-list Read the dispatch prompt already told them to do
per D4. This is identical text duplicated across all four corrector-family
files.

**Investigation:**
1. Scope OUT check: matches "OUT: corrector-skeleton compression /
   deduplication across correctors (pilfer defect 21, separate work)" — one
   recall-step fix would need to land identically in four files, which is
   exactly the compression/deduplication pilfer defect 21 covers.
2. Confirmed pre-existing in `corrector.md`/`design-corrector.md` (unchanged
   by this job's diffs); `runbook-corrector.md` inherited it unchanged from
   the old `runbook-outline-corrector.md` at the task-2 rename.

**Status:** OUT-OF-SCOPE (belongs to pilfer defect 21; no fix applied)

### 5. `tdd-auditor.md` — FR-5's literal acceptance wording vs. D14 (observation, no fix needed)

**Problem:** FR-5's acceptance text (`requirements.md`) says `tdd-auditor`
checks "RED-before-GREEN per slice and test-at-a-time from the commit
sequence." D5(c) makes GREEN commit once per slice
(`feat: Item N.M/k — <title>`), so there is no per-test commit granularity
left to derive "test-at-a-time" from. D14 (the outline's own rewrite of the
tdd-auditor criteria) supersedes this: it audits "GREEN modified no
reviewed test" by diffing the slice commit's test files against the RED
report's test list, not by inspecting a commit sequence for one-test-per-commit.
`tdd-auditor.md` correctly implements D14 (Per-Slice Check 3), which is the
authoritative, later decision — this is not a defect in the agent file, just
a place where FR-5's original wording was overtaken by D14 during design.
No fix applied; noted for Scope completeness below.

**Status:** N/A (no defect; design (D14) legitimately supersedes requirements
wording)

## Reference resolution

| Path | Referenced from | Exists |
|---|---|---|
| `plugin/skills/runbook/references/runbook-format.md` | `runbook-corrector.md:60` | Yes |
| `docs/design.md` | `refactor.md:139`, `design-corrector.md` (implicit path convention) | Yes |
| `CLAUDE.md` | `refactor.md:147` | Yes |
| `memory/MEMORY.md` | `design-corrector.md:135,354` | Yes |
| `plugin/skills/orchestrate/scripts/verify-step.sh` (cited by `/orchestrate`, consumed by dispatched agents' done-criteria, not named inside the 9 files directly) | — | Yes |
| `plugin/skills/orchestrate/scripts/verify-red.sh` | not referenced anywhere in the 9 files | Correctly absent (deleted) |
| `plugin/fragments/review-requirement.md`, `escalation-acceptance.md`, `continuation-passing.md`, `delegation.md` | cross-checked for consistency, not cited inside the 9 files | All exist |
| `plans/<job>/runbook.md`, `design.md`, `outline.md`, `requirements.md`, `reports/*.md` | throughout all nine files | Template paths (`<job>` placeholder) — valid by construction |
| No occurrence of `runbook-outline.md`, `runbook-outline-corrector`, `prepare-runbook.py`, `validate-runbook.py`, `assemble-runbook.py`, `verify-red.sh`, `review-plan`, `steps/`, `common-context.md`, `orchestrator-plan.md`, `## Step`/`## Cycle` markers, `Tier 1/2/3`, or `expansion` (tier sense) in any of the nine files | C-4 sweep | Confirmed clean via `grep` |

## Scope completeness

| Scope IN item | Deliverable | Status |
|---|---|---|
| `test-driver.md` rewrite: RED/GREEN modes, `model: sonnet`, no-mode-named defect | Present — RED mode (stub-then-red, no commit, stop), GREEN mode (one-test-at-a-time, never edits tests, one `feat:` commit) | Matches D2, D4, FR-5 |
| `artisan.md`: `model: sonnet`, context handling (prompt carries task text + artifact paths) | Present | Matches D2, D4 — minor: unused `Skill` tool (Finding 1) |
| `refactor.md`: dispatched on code-review signal, own `refactor:` commit on clean tree | Present — Step 6 commits `refactor:` on a clean tree, no amend | Matches D3 — minor: escalation-text mismatch (Finding 2) |
| `tdd-auditor.md`: rewritten per-slice/cross-slice checks, process metrics | Present — Per-Slice Checks 1–4, Cross-Slice Checks, Process Metrics section | Matches D14 |
| `corrector.md`: `model: opus`, markers `## Phase N:`/`Item N.M:`, new §3.5 TDD Slice Reviews (vacuous-green catalogue, mutated-SUT run, `REFACTOR-NEEDED:` flag) | Present — §3.5 test review + code review, matches `/orchestrate` §2.3(b)/(d) exactly | Matches D2, D5 — dead pre-existing code and recall-step mismatch noted OUT-OF-SCOPE (Findings 3, 4) |
| `runbook-corrector.md`: renamed from `runbook-outline-corrector`, reviews `runbook.md`, §4 Item Format Rules, `model: opus` | Present — Step 0 rejects non-`runbook.md`, §4 has all four FR-6/D9 rules (code-block violation, missing-Interfaces gap, crammed-contract violation, tdd-slice defects) | Matches FR-3, FR-6, D9 |
| `runbook-simplifier.md`: description purpose-first, input `runbook.md`, "before `/proof`" framing | Present — description leads with what it does, no "Phase 0.85"/"expansion" language, examples say "before `/proof`" | Matches D9 |
| `design-corrector.md`: runbook-marker anchor lines ~53–56, ~65, ~144 rewired | Present — anchor uses `## Phase N:`/`Item N.M:`, redirect names `runbook-corrector`, near-miss example uses live `outline-corrector`/`runbook-corrector` pair | Matches D9, C-4 sweep |
| `outline-corrector.md`: line ~143 rewired only | Present — cross-component interface example now uses a generic glob-vs-single-artifact case, no `runbook-phase-*.md` | Matches C-4 sweep; rest of file correctly untouched (out of scope) |

All Scope IN items have a corresponding deliverable; no gaps.
