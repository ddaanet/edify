# Outline: /design routing gate and artefact provenance

Two changes to `/design`, batched because both alter what its artefacts
promise a downstream consumer. Agentic prose throughout — no behavioral code.

## Provenance

- **Derived from:** none — this job originates from the task frame, not from a
  deliverable-review.
- **Base:** `926e372d02a0366202b2bb6a684551128d1f2a66` — `HEAD` at outline
  generation. The deliverable-review for this job diffs `<base>..HEAD`.

*(This section is itself Item B's deliverable, written here as its own first
instance.)*

## Requirements

From `.claude/handoff-todo.md` §"/design skill work" — no `requirements.md`;
these two bullets are the requirement.

- **R1 — Remove `/design`'s direct-execution path:** "the Phase B / C.5
  execution-ready branch that bypasses `/runbook` and implements inside the
  design session … Anything coming out of `/design` has requirements, so it
  should be checked by `/edify:deliverable-review`." → **Item A** for the
  branch; **Item B's first-that-exists Prerequisite** for the second clause.
  The agentic-prose route produces only an `outline.md` and
  `deliverable-review` opens `design.md` alone, so nothing coming out of that
  route is reviewable today — which is what ties the two items into one job.
  *What R1 does not ask for:* deleting the `/runbook`-bypassing route itself.
  R1 identifies the path by "implements inside the design session", and D-37
  keeps Simple work routing through `/build` with no runbook. What goes is the
  in-session execution and the name; the route stays.
- **R2 — Design artefacts derived from a deliverable-review record the review
  and the initial commit base**, so a second pass reviews the whole diff from
  the original base rather than the changes since the last commit. → **Item
  B**. R2 scopes this to review-derived artefacts; this outline widens it to
  every artefact, with the rationale under Key decisions.

## Scope

**IN**

- `plugin/skills/design/references/write-outline.md` — the **routing block
  only**, `:206-228`, replaced by a pointer, with `:204`'s trailing clause
  ("On confirmation, assess execution readiness") reworded to name the node.
  The rest of §Outline Sufficiency Gate decides a different question —
  outline-or-design — and stays: the sufficiency criteria (`:197-202`), the
  `**If insufficient**` branch into Phase C (`:230`), `**When to apply:**`
  (`:232`). Nothing in the node holds them.
- `plugin/skills/design/references/write-outline.md` — §Multi-Sub-Problem
  Sufficiency Gate `:185`, "Follow §Continuation (no prepend — dispatch is the
  caller's responsibility)". §Continuation was retired with `/inline` and
  `/orchestrate` (`77a4710d`) and exists nowhere in the skill; this is a third
  routing site and a dangling reference, in an Item A file, of exactly the
  class Item A exists to remove. The line becomes the route each sub-problem's
  readiness names, with dispatch still the caller's.
- `plugin/skills/design/references/write-design.md` — §C.5 `:70-89` replaced
  by a pointer. The heading, the `Read plans/<job>/design.md` grounding line
  (`:66`) and "Design can resolve complexity …" (`:68`) stay — the node
  assumes its caller has already loaded the artefact.
- `plugin/skills/design/references/route-to-execution.md` — new shared node
- `plugin/skills/design/references/design-content-rules.md` — new §Provenance;
  §References' rationale line (`:99`) reworded to stop claiming the word
  "provenance", leaving it a reading list of what informed the design
- `plugin/skills/design/references/research-protocol.md` — §A.5 outline
  content list gains Provenance
- `plugin/skills/design/SKILL.md` — **Item A:** §Downstream Consumers (`:19`),
  §Routing out (`:174-175`), and the Phase 0 resume branches (`:42-43`), which
  name both gates as resume targets. **Item B:** the two per-route step lists
  that enumerate outline content — `:133` (Simple / Moderate agentic-prose,
  "per `references/write-outline.md`") and `:144` (Moderate non-prose,
  "lightweight format (scope, per-file changes, dependencies, IN/OUT
  boundaries)"). The second never reaches `research-protocol.md` §A.5, so
  Provenance is named here or that route's outline never carries one. Hub
  budget: 175 lines against the ~200 `SKILL.md` guideline, so both items'
  additions are line-counted, not free.
- `plugin/agents/outline-corrector.md`, `plugin/agents/design-corrector.md` —
  Provenance criterion
- `plugin/skills/deliverable-review/SKILL.md` — Prerequisites (`:23`) take the
  first artefact that exists; Phase 1 step 2 (`:31`) builds the range as
  `<Base>..HEAD` from that artefact's Provenance, asking the user only when
  there is none
- `docs/design.md` — **Item A:** D-35 (`:596`) and L-2 (`:1092`) reworded off
  the `C.5` label and off "execution readiness". **Item B:** a new decision in
  §6.4 Pipeline contracts recording the Provenance clause and its inheritance
  rule — a change to the artefact contract and to a consumer's range, which is
  design-significant and belongs in current truth rather than only in a skill
  body. The same edit settles a standing contradiction: §6.8's D-55 already
  says the review compares "the plan outline's in-scope section" against the
  diff, while `deliverable-review/SKILL.md:23` names `design.md` alone.
- `docs/changelog.md` — dated entry

**OUT**

- `/build`'s own `tmp/build-baseline` (§2) — a per-run gitignored value for
  post-item verification, unrelated to the durable provenance base. Untouched.
- `plugin/skills/build/SKILL.md` §4.1's title, "Direct execution". The phrase
  is live there with a different meaning — inline versus delegated dispatch —
  so the `/design`-local rename does not reach it. Named here because the exit
  condition's grep hits it and a sweep must not "fix" it.
- The complexity-triage thresholds (L-2's file-count figures). Still
  ungrounded, still not this job's problem. L-2 is reworded only where it
  names the `C.5` label.
- `plans/README.md`'s stale `prepare-runbook.py` / `steps/` description —
  known-stale, tracked in the task frame, not in this job's scope.

## Item A — one routing node, renamed to what it decides

### What is actually wrong

The `/build` merge already converted both gate copies' terminal lines from
"direct execution" to "commit, name `/build plans/<job>`, stop". Nothing
implements in the design session any more. What survived the sweep is the
gate's *body*, duplicated and carrying claims nobody re-derived:

1. **Duplication with drift.** The routing block — `write-outline.md:206-228`
   and `write-design.md:70-89` — states one decision twice. (Not the whole of
   either section: `write-outline.md:197-202` and `:230-232` decide
   outline-or-design, a question `write-design.md` has no counterpart for.)
   The two copies already disagree three ways:
   - **Wording.** "No runtime ordering dependencies between files" (`:220`)
     versus "No cross-file coordination requiring sequencing" (`:82`).
   - **A missing qualifier.** `write-outline.md:209` carries "(hard gate —
     file count irrelevant)" on the prose branch; `write-design.md:73` does
     not.
   - **Substance, not wording.** `write-outline.md:217` heads the criteria
     "non-prose paths only — prose path bypasses these"; `write-design.md:79`
     heads them "all must hold for prose/investigation/exploration paths". The
     two copies route differently on the same input. This is what a second
     copy costs, and it has to be resolved rather than inherited.
2. **A false criterion.** "Scope fits single-session capacity (one session,
   one model)" is contradicted by `plugin/skills/build/SKILL.md` §5 ("A run
   spanning several sessions reaches this once, in its last one") and §6's
   `references/resuming.md`. It was true when the branch meant *the design
   session does the work*; it is the direct-execution residue.
3. **A stale name.** "Execution readiness" names a decision that is no longer
   about readiness, and "direct execution" named the in-session path. The
   decision is now narrower and should be named for it. The term is not dead
   tree-wide, though: `/build` §4.1 is itself titled "Direct execution",
   meaning inline-versus-delegated dispatch. The sweep classifies that hit
   **accurate**, not stale — the rename is `/design`-local.

### The change

Extract one node, `references/route-to-execution.md`, read from both sites.
Its question is **does this work need a runbook?** — not whether the session
can execute it.

`/build` cannot make this call itself: its §1 takes whichever artefact exists
and never routes back to `/runbook`. So the decision stays in `/design`.

**Discriminator** (unchanged in substance — work-type-grounded per D-35/D-36):

```
IF all prose edits, no implementation loops        -> /build
ELSE IF work type = Investigation                  -> /build
ELSE IF work type = Exploration                    -> /build
ELSE (work type = Production AND behavioral code)  -> /runbook
```

The Exploration branch loses its `AND design resolved all questions` conjunct
— **replaced by the first precondition, not made redundant by it.** Read
literally the conjunct bounces every spike back to design, since a spike
exists to answer a question. The precondition is deliberately weaker: it asks
only that the *executor* face no unresolved decision, which is the property
routing actually needs.

**Criteria, reclassified.** The surviving four split into two kinds, which the
single list conflated:

*Preconditions for routing at all* — failing these sends the work back to
design, not to a different route:

- Every decision **the executor would otherwise have to make** is resolved.
  This is not "no open questions": an Exploration job exists to answer one,
  and that question is its deliverable, not a blocker.
- Edit targets are named (section-level or line-level). With no runbook the
  artefact **is** the item list, so `/build` walks what the artefact names.

**Both preconditions bind every branch, prose included.** This settles item
1's substantive drift in `write-design.md`'s favour, and it is a behaviour
change for the Phase B copy, which exempted the prose path. Named edit targets
are what the prose path needs most, for the reason just given: with no runbook
the artefact is the item list, and a prose job that names no targets gives
`/build` nothing to walk.

*Runbook discriminators* — failing these means `/runbook`, not `/build`:

- Cross-file coordination requiring sequencing. Phases exist for this.
- Implementation loops (test/build feedback). `tdd` slices exist for this.

Dropped: single-session capacity (item 2 above). The prose-path rationale
paragraph in `write-outline.md` moves into the node intact — it is the
justification for the first discriminator branch and currently exists in only
one of the two copies.

**Inbound references** repointed: `SKILL.md:19` ("Phase B sufficiency gate,
Phase C.5 execution readiness"), `SKILL.md:42-43` (the Phase 0 resume
branches, "skip to outline sufficiency gate" / "skip to multi-sub-problem
sufficiency gate" — both name a section this job rewrites),
`SKILL.md:174-175` ("execution-ready (B gate or C.5)" / "Not
execution-ready"), `write-design.md:53` ("Proceed to C.5"),
`docs/design.md:596` (D-35, "route at `/design` C.5") and `docs/design.md:1092`
(L-2, "decide execution readiness").

**Exit condition** (per `reference-audit-after-a-move`): a whole-tree grep with
**every** hit classified accurate or stale and the classification stated per
hit. Not a reading of the diff. Two properties of the grep are load-bearing,
both established by running it:

- **Case-insensitive.** `grep -rn 'execution.read|direct.execution|C\.5'`
  misses five live hits that `grep -rni` finds —
  `plugin/agents/runbook-corrector.md:112`, `plugin/skills/build/SKILL.md:107`,
  `write-design.md:79` and `:86`, `write-outline.md:217`. Two of those are
  inside the sections being rewritten.
- **Word-level as well as phrase-level.** Line-based grep cannot match a
  phrase the hard wrap splits: `docs/design.md` D-37 carries "Direct" at the
  end of one line and "execution" at the start of the next, and no
  phrase pattern finds it. Separate `readiness` and `direct` passes run too.

Expect the count to exceed what this outline lists, and treat that as the
audit working.

## Item B — artefacts record their base

### What is wrong

`plugin/skills/deliverable-review/SKILL.md:31` establishes the review range
from context "or asked of the user". Nothing durable records it. So a second
design-to-deliverable pass, triggered by a review of the first, reviews only
the fixes — it cannot judge whether the whole deliverable meets its
requirements, because the original base is gone from context by then.

### The change

A `## Provenance` section on every `/design` artefact — `outline.md` and
`design.md` alike, since the agentic-prose route produces only an outline.
Two fields:

- **Derived from:** the review report that motivated this design **and the
  artefact it supersedes**, or `none`. Naming both is what makes the base
  copyable — a second pass in a new job directory has no other way to find it.
- **Base:** the commit the deliverable started from.

**The inheritance rule is the whole point.** A first-pass artefact takes
`git rev-parse HEAD` at generation time. A second-pass artefact copies `Base:`
verbatim from the artefact named in `Derived from:`, and never recomputes it.
Recomputing is exactly the bug: a fresh `HEAD` makes pass 2's range start after
pass 1's work, which is the narrow diff the current behaviour already produces.

Taking `HEAD` at artefact-generation time is correct: `plans/` is excluded
from the review diff (`':!plans' ':!tmp' ':!.claude'` in the range command at
`deliverable-review/SKILL.md:31`), so the design artefact's own commit cannot
pollute the range it defines.

*Residual:* commits landing between artefact generation and the work — an
unrelated fix, a merge — fall inside the range and surface as unspecified
deliverables. Bounded and visible: Phase 2 reports them as excess. A narrower
base would be worse, since it would start after the job's own first commit.

Distinct from §References, which is a reading list. Provenance carries a git
ref a later command substitutes into `git diff`.

**Where it is specified:** two nodes, because two paths produce artefacts.
`design-content-rules.md` is read only from `write-design.md:13` and governs
Phase C.1's `design.md`. The outline side is `research-protocol.md` §A.5's
content list (currently: approach summary, key decisions, open questions,
scope boundaries), reached from `write-outline.md:103` on every
outline-producing route but the Moderate non-prose one — which is why
`SKILL.md:144` is in scope. Neither node covers the other; one edit is not
enough.

**Consumer:** `deliverable-review` Prerequisites take the first that exists —
`plans/<plan>/design.md`, else `plans/<plan>/outline.md`, matching `/build`
§1 — and Phase 1 step 2 builds the range as `<Base>..HEAD` from that
artefact's `Base:`, falling back to asking the user only when no Provenance
section exists. Both endpoints are part of the change: `:31` says only "the
plan's commits", and a base alone does not close a range. `:31` is the single
site in `plugin/` that states the range — verified by whole-tree grep for the
`git diff --numstat` command — so this is one edit, not a family. Without the
first-that-exists rule, Provenance on a prose job's outline is written to a
file this consumer never opens, which is R1's second clause left unserved.

**Correctors:** both gain a conditional criterion in the pattern each already
uses for optional sections — `outline-corrector.md` §3 Review Criteria,
`design-corrector.md:159,173`. Without it the new section ships unreviewed.

## Key decisions

- **D — The gate stays in `/design`.** `/build` §1 has no path back to
  `/runbook`, so routing cannot move downstream. *Accepted tradeoff:* `/design`
  keeps a responsibility that looks like execution's, and the node must be
  re-read on every complex job.
- **D — One shared node, not a pointer from one copy to the other.** Both
  call sites are peers (Phase B and Phase C.5 reach it from different
  ceremony levels); making one the definition would imply a precedence that
  does not exist. *Accepted tradeoff:* a third file in `references/`.
- **D — Provenance on every artefact, not only review-derived ones.** The
  alternative — record the base only when a review triggered the design —
  fails at pass 2, because pass 1 left nothing to inherit. *Accepted
  tradeoff:* one `git rev-parse` and two lines on every design artefact,
  including the many that no deliverable-review ever reads.
- **D — Routing criteria split into preconditions and discriminators.** The
  flat five-item list conflated "this work isn't ready to route" with "this
  work needs phases", which is how a false criterion survived in it unnoticed.
  *Accepted tradeoff:* two lists to check instead of one, and the reader must
  know which kind of failure sends work back to design rather than to
  `/runbook`.
- **D — Preconditions bind the prose path too.** The two copies disagreed on
  this (item 1), so the node cannot inherit both readings. *Accepted
  tradeoff:* a prose job with unnamed edit targets now goes back to design
  instead of straight to `/build`, which the Phase B copy would have waved
  through.

## Risks and open questions

**Open questions:** none. Both mechanisms are settled, and every claim this
outline makes about a file it does not change has been checked against that
file.

**Risks:**

- **The sweep under-reports.** Item A's exit condition is the only thing
  between this job and a repeat of the residue it exists to remove, and the
  first form of that grep missed five live hits plus a wrapped one. Mitigated
  by the case and word-level properties stated above; residual risk is a hit
  phrased in words none of the patterns carry.
- **Provenance goes unwritten.** It is a prose contract with four producing
  paths, no mechanical validator, and correctors as the only enforcement —
  which catches it after the artefact is written, not during. First-pass
  evidence that the contract is writable is this outline's own §Provenance.
- **The inheritance rule inverts under a careless second pass.** `Base:` is
  the one field an agent's instinct is to recompute, and the failure is
  silent: a too-narrow diff reads as a clean review. Stated in the node and in
  both correctors' criteria; nothing detects a violation mechanically.

## Next steps

Load `plugin-dev:skill-development` and `plugin-dev:agent-development` before
executing. Workflow/skill/agent edits: opus required.
