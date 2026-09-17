# Outline Review: design-routing-and-provenance

**Artifact**: `plans/design-routing-and-provenance/outline.md`
**Date**: 2026-09-17T16:09:44+02:00
**Mode**: PDR review + fix-all
**Requirements source**: `.claude/handoff-todo.md` §"/design skill work" (two
bullets; no `requirements.md` for this job, by instruction)

## Summary

The outline is technically sound and its two items are genuinely coupled, but
it shipped with one false premise about its own edit target that would have
destroyed an unrelated decision, an exit-condition grep that demonstrably
under-reports, and an unlisted third routing site carrying a dangling
reference to a retired section. Every claim it makes about a file it does not
change was checked against that file; the three the task named
(`build/SKILL.md` §5/§6, `deliverable-review/SKILL.md:31` uniqueness, and
`':!plans'`) all hold. All findings are fixed in the outline.

**Overall Assessment**: Ready (post-fix)

## Claim verification (task-directed)

| Claim in outline | Source checked | Verdict |
|---|---|---|
| `build/SKILL.md` §5 establishes multi-session runs | `plugin/skills/build/SKILL.md:163-166` — "A run spanning several sessions reaches this once, in its last one" | **True** |
| §6 carries `references/resuming.md` | `build/SKILL.md:204-205`; file exists | **True** |
| ⇒ "single-session capacity" is a false criterion | Follows from both | **True** |
| `deliverable-review/SKILL.md:31` is the only site stating the review range | `grep -rn "review range\|git diff --numstat\|':!plans'"` whole tree — one hit in `plugin/`, rest are historical `plans/` reports | **True** |
| The range command excludes `plans/` | `:31` — `git diff --numstat <range> -- . ':!plans' ':!tmp' ':!.claude'` | **True** |
| `/build` §1 takes whichever artefact exists and never routes back to `/runbook` | `build/SKILL.md:25-44` | **True** |
| `:23` Prerequisites name `design.md` only | `deliverable-review/SKILL.md:23` | **True** |
| `design-content-rules.md:99` claims the word "provenance" | `:99` — "Backward-looking provenance (what shaped this design)" | **True** |
| `design-corrector.md:159,173` use the optional-section pattern | Both read "If design includes … section:" | **True** |
| `outline-corrector.md` §3 Review Criteria exists | `:64` | **True** |
| `docs/design.md:596` (D-35) / `:1092` (L-2) carry the stale labels | Both confirmed verbatim | **True** |
| Base `926e372d…` is `HEAD` | `git rev-parse HEAD` | **True** |
| **`write-outline.md:191-232` and `write-design.md:64-89` state the same decision** | `:191-203` and `:230-232` decide outline-or-design; `write-design.md` has no counterpart | **FALSE — Critical 1** |
| **"direct execution" names a path that no longer exists** | `build/SKILL.md:107` — §4.1 is titled "Direct execution", live with a different meaning | **FALSE as stated — Major 2** |

## Requirements Traceability

| Requirement | Outline section | Coverage | Notes |
|---|---|---|---|
| R1 — remove the direct-execution path (Phase B / C.5 branch) | Item A | Complete | Outline correctly re-derives that the *execution* already went in the `/build` merge and the residue is the gate body |
| R1 second clause — "anything coming out of `/design` … checked by `/edify:deliverable-review`" | — → now §Requirements + Item B Consumer | **Was Missing** | Unaddressed and untraced; Item B's first-that-exists Prerequisite is what serves it. Added |
| R1 boundary — "bypasses `/runbook`" does *not* mean delete the route | — → now §Requirements | **Was Missing** | A literal read of R1 says delete the branch; D-37 says keep it. Distinction now stated |
| R2 — record the review and the initial commit base | Item B | Complete | Inheritance rule is the load-bearing part and is stated as such |
| R2 scope widening (every artefact, not only review-derived) | Key decisions D-3 | Complete | Option taken with rationale and accepted tradeoff — PDR-compliant |

**Traceability Assessment**: Gaps identified and fixed. A `## Requirements`
section now stands between §Provenance and §Scope, quoting both bullets and
mapping each to an item.

## Scope-to-Component Traceability

| Scope IN item | Item | Notes |
|---|---|---|
| `write-outline.md` routing block | A | Was stated as the whole §Outline Sufficiency Gate — **Critical 1**, fixed |
| `write-outline.md:185` §Continuation | A | **Was absent from IN and OUT — Critical 3**, added |
| `write-design.md` §C.5 | A | Range narrowed to `:70-89`; grounding lines preserved |
| `route-to-execution.md` (new node) | A | Direct |
| `design-content-rules.md` §Provenance + `:99` | B | Covers `design.md` only — now stated |
| `research-protocol.md` §A.5 | B | Covers the outline paths reached via `write-outline.md:103` |
| `design/SKILL.md` "the two per-route step lists" | ? | **Was unresolvable — Major 8**; now split by item, with line numbers and purpose |
| `outline-corrector.md`, `design-corrector.md` | B | Direct |
| `deliverable-review/SKILL.md` `:23`, `:31` | B | Range endpoint was unspecified — **Major 7**, fixed |
| `docs/design.md` D-35, L-2 | A | Direct |
| `docs/design.md` decision for Provenance | B | **Was orphan — Major 6**, added to §6.4 |
| `docs/changelog.md` | A+B | Direct |

**Scope Assessment**: Orphans found and fixed. Every IN item now names an
item, a line range, and what changes there.

## Cross-component interface check

- **`route-to-execution.md` → its two callers.** The node assumes the caller
  has loaded the artefact. `write-design.md:66` holds that `Read` line and the
  original scope would have deleted it with the section. Fixed by preserving
  `:66` and `:68`.
- **Provenance producer → `deliverable-review` consumer.** Producer writes
  `Base: <sha>`; consumer needs a *range*. `:31` currently says only "the
  plan's commits" and the outline said the consumer "reads the base" — a
  scalar handed to something expecting an interval. Fixed: `<Base>..HEAD`
  stated on both sides.
- **Provenance spec node → producing paths.** `design-content-rules.md` is
  reachable only from `write-design.md:13` (Phase C.1, `design.md`). Four
  paths produce artefacts; that node covers one. Fixed by naming the outline
  side explicitly (`research-protocol.md` §A.5 via `write-outline.md:103`) and
  by pinning `SKILL.md:144`, the one route that reaches neither.

## Review Findings

### Critical Issues

1. **Scope IN destroyed the outline-or-design decision, on a false premise**
   - Location: §Scope IN bullet 1; Item A "What is actually wrong" item 1
   - Problem: "§Outline Sufficiency Gate replaced by a pointer", justified by
     "`write-outline.md:191-232` and `write-design.md:64-89` state the same
     decision". They do not. `:197-202` are the *sufficiency* criteria
     (outline-or-design), `:230` is the branch into Phase C, `:232` is "When
     to apply". None has a counterpart in `write-design.md`, and nothing in
     the new routing node holds them. Executing the scope as written deletes a
     live decision that this job never examined.
   - Fix: scope narrowed to `:206-228` plus a reword of `:204`'s trailing
     clause, with the surviving lines enumerated; the duplication claim
     restated as `write-outline.md:206-228` ≡ `write-design.md:70-89`, with
     the non-overlap called out in parentheses.
   - **Status**: FIXED

2. **The two copies disagree substantively, not just in wording, and the
   outline inherited the disagreement silently**
   - Location: Item A item 1; §Criteria, reclassified
   - Problem: `write-outline.md:217` heads the criteria "non-prose paths only
     — prose path bypasses these"; `write-design.md:79` heads them "all must
     hold for prose/investigation/exploration paths". The copies route
     differently on the same input. The outline listed only the wording drift
     and then wrote preconditions that "apply to routing at all" — picking
     `write-design.md`'s side without saying so. That is an undeclared
     behaviour change to the Phase B path.
   - Fix: third drift instance added and labelled "substance, not wording";
     an explicit paragraph binds both preconditions to every branch including
     prose, with the reason; a fifth Key decision records the choice and its
     accepted tradeoff.
   - **Status**: FIXED

3. **A third routing site, carrying a dangling reference to a retired
   section, was in neither IN nor OUT**
   - Location: §Scope
   - Problem: `write-outline.md:165-187` (Multi-Sub-Problem Sufficiency Gate)
     routes sub-problems and ends at `:185` with "Follow §Continuation (no
     prepend — dispatch is the caller's responsibility)". §Continuation was
     retired with `/inline` and `/orchestrate` (`77a4710d`) and exists nowhere
     in the design skill — verified by whole-tree grep. This is residue of the
     exact class Item A exists to remove, in an Item A file, and the outline's
     exit-condition grep would never surface it (the string contains none of
     its patterns).
   - Fix: added as a Scope IN bullet with the replacement stated (route by the
     sub-problem's readiness; dispatch stays the caller's).
   - **Status**: FIXED

### Major Issues

1. **The exit-condition grep under-reports — demonstrated, not suspected**
   - Location: Item A §Exit condition
   - Problem: `execution.read|direct.execution|C\.5` is case-sensitive.
     Running it against `plugin/` and `docs/` returns 18 hits; `-i` returns
     23. The five it misses are `plugin/agents/runbook-corrector.md:112`,
     `plugin/skills/build/SKILL.md:107`, `write-design.md:79`,
     `write-design.md:86` and `write-outline.md:217` — two of them inside the
     sections being rewritten. Separately, line-based grep cannot match
     `docs/design.md` D-37, where the hard wrap puts "Direct" and "execution"
     on different lines. An exit condition that certifies a sweep it did not
     perform is worse than none, and this is precisely the failure
     `reference-audit-after-a-move` warns about.
   - Fix: exit condition rewritten — case-insensitive form mandated, the five
     missed hits named, a word-level (`readiness`, `direct`) pass added for
     wrapped phrases, D-37 flagged for hand-checking, and "expect the count to
     exceed what this outline lists" stated.
   - **Status**: FIXED

2. **"direct execution names a path that no longer exists" is false tree-wide**
   - Location: Item A item 3
   - Problem: `build/SKILL.md:107` — §4.1 is titled "Direct execution",
     meaning inline-versus-delegated dispatch. The term is live with a
     different referent. Left as written, the sweep classifies a correct hit
     as stale and renames it.
   - Fix: claim narrowed to the `/design`-local decision; the `/build` §4.1
     hit named and pre-classified **accurate**; added to Scope OUT so a sweep
     does not "fix" it.
   - **Status**: FIXED

3. **The Exploration-conjunct rationale contradicts itself**
   - Location: Item A §Discriminator
   - Problem: "the precondition below already guarantees it, and read
     literally it would bounce every spike back to design". Both cannot hold.
     The precondition is explicitly *weaker* than "design resolved all
     questions" — the outline itself says so two paragraphs later ("This is
     not 'no open questions'"). The conjunct is replaced, not made redundant.
   - Fix: reworded to "replaced by the first precondition, not made redundant
     by it", with the asymmetry stated.
   - **Status**: FIXED

4. **`SKILL.md:42-43` missing from the inbound-reference repoint list**
   - Location: Item A §Inbound references
   - Problem: the Phase 0 resume branches say "skip to outline sufficiency
     gate" and "skip to multi-sub-problem sufficiency gate" — both name
     sections this job rewrites, and neither was listed.
   - Fix: added to the repoint list with their text quoted.
   - **Status**: FIXED

5. **Item B had no decision record in `docs/design.md`**
   - Location: §Scope IN, `docs/design.md` bullet
   - Problem: the bullet allocated D-35 and L-2, both Item A. Provenance is a
     new artefact-contract clause with an inheritance rule and a changed
     consumer behaviour — design-significant, and `docs/design.md` is current
     truth per `feedback-decision-docs-are-living`. Nothing would have
     recorded it outside a skill body. Compounding this: §6.8's D-55 already
     says the review compares "the plan outline's in-scope section" against
     the diff, contradicting `deliverable-review/SKILL.md:23`'s
     `design.md`-only Prerequisite — an existing inconsistency this job
     resolves and should record.
   - Fix: `docs/design.md` bullet split by item; a new §6.4 Pipeline contracts
     decision added for Provenance, with the D-55 contradiction named.
   - **Status**: FIXED

6. **The review range's far endpoint was unspecified**
   - Location: Item B §Consumer; §Scope IN
   - Problem: "Phase 1 step 2 reads that artefact's `Base:` for the range".
     `:31` currently says "the plan's commits"; a base is a point, not a
     range. The consumer edit would land ambiguous.
   - Fix: `<Base>..HEAD` stated in both the Consumer paragraph and the Scope
     bullet, with the reason `:31`'s current wording does not suffice.
   - **Status**: FIXED

7. **"the two per-route step lists" was unresolvable, and one of them is the
   only path Provenance would otherwise miss**
   - Location: §Scope IN, `design/SKILL.md` bullet
   - Problem: the bullet grouped an unnamed pair of step lists with two Item A
     sections, stating no line numbers and no change. `SKILL.md` has two
     per-route step lists (`:131-137` Simple/Moderate-agentic-prose,
     `:139-145` Moderate non-prose); neither consults the routing gate, so the
     Item A reading is vacuous. Under the Item B reading it matters
     critically: `:144`'s "lightweight format (scope, per-file changes,
     dependencies, IN/OUT boundaries)" is generated inline and never reaches
     `research-protocol.md` §A.5, so that route's outline would carry no
     Provenance at all.
   - Fix: bullet split by item with line numbers, the purpose of each edit
     stated, and the `:144` gap spelled out.
   - **Status**: FIXED

### Minor Issues

1. **Third drift instance unlisted** — `write-outline.md:209` carries "(hard
   gate — file count irrelevant)"; `write-design.md:73` does not. Fix: added
   to the drift list. **Status**: FIXED
2. **`write-design.md` §C.5's grounding lines would have been deleted** —
   `:66` (`Read plans/<job>/design.md`) and `:68` ("Design can resolve
   complexity …") are not part of the routing decision. Fix: replacement range
   narrowed to `:70-89`, survivors named. **Status**: FIXED
3. **Where Provenance is specified was implicit** — `design-content-rules.md`
   is read only from `write-design.md:13` and scoped to Phase C.1; a reader
   would assume the one new §Provenance covers outlines too. Fix: a "Where it
   is specified" paragraph names both nodes and their reach. **Status**: FIXED
4. **`plans/`-exclusion argument cited the wrong precision** — the range
   command excludes `':!plans' ':!tmp' ':!.claude'`, and the site was not
   cited. Fix: full exclusion list and `:31` cited. **Status**: FIXED
5. **Base drift unstated** — unrelated commits landing between artefact
   generation and the work fall inside `<base>..HEAD`. Fix: a *Residual*
   paragraph states the bound and why a narrower base is worse.
   **Status**: FIXED
6. **No line-budget note despite `line-caps` being in the recall artifact** —
   `design/SKILL.md` is 175 lines against the ~200 hub guideline and both
   items add to it. Fix: budget stated in the scope bullet. (The three
   reference nodes are far from the 400 cap: 232 → ~205, 96 → ~75, new node
   ~50.) **Status**: FIXED
7. **"Open questions: None" with no risks** — PDR wants risks identified, and
   "consumers verified against source" was an overclaim given Criticals 1–3.
   Fix: section retitled "Risks and open questions"; three risks added (sweep
   under-reporting, Provenance going unwritten, inheritance-rule inversion),
   each with its mitigation and residual. **Status**: FIXED
8. **L-2's OUT boundary imprecise** — L-2 is both an OUT item (its thresholds)
   and an IN item (its `C.5` label). Fix: OUT bullet now says L-2 is reworded
   only where it names the label. **Status**: FIXED

## Fixes Applied

- §Provenance→§Scope — new `## Requirements` section: both task-frame bullets
  quoted, mapped to items, with R1's second clause and R1's boundary
  ("bypasses `/runbook`" ≠ "delete the route") traced
- §Scope IN `write-outline.md` — narrowed to `:206-228`; surviving lines
  enumerated
- §Scope IN — new bullet for `write-outline.md:185` §Continuation
- §Scope IN `write-design.md` — narrowed to `:70-89`; `:66`/`:68` preserved
- §Scope IN `design/SKILL.md` — split by item, line numbers, purpose,
  `:144` gap, hub line budget
- §Scope IN `docs/design.md` — split by item; §6.4 decision for Provenance;
  D-55 contradiction named
- §Scope IN `deliverable-review/SKILL.md` — `<Base>..HEAD` and the
  no-Provenance fallback
- §Scope OUT — new bullet for `build/SKILL.md` §4.1 "Direct execution";
  L-2 boundary sharpened
- Item A item 1 — line ranges corrected, non-overlap stated, three drift
  instances enumerated with the substantive one labelled
- Item A item 3 — claim narrowed; `/build` §4.1 pre-classified accurate
- Item A §Discriminator — Exploration-conjunct rationale corrected
- Item A §Criteria — preconditions bound to every branch including prose,
  with reason
- Item A §Inbound references — `SKILL.md:42-43` added
- Item A §Exit condition — rewritten: case-insensitivity mandated with the
  five missed hits named, word-level pass for wrapped phrases, D-37 flagged,
  expectation that the count grows
- Item B §The change — full exclusion list and `:31` citation; *Residual*
  paragraph on base drift; "Where it is specified" paragraph
- Item B §Consumer — `<Base>..HEAD`, uniqueness of `:31` stated as verified,
  R1 second clause tied in
- §Key decisions — fifth decision on prose-path preconditions
- §Open questions → §Risks and open questions — three risks with mitigations

Outline grew 200 → 340 lines. All lines wrap under 79 characters, matching the
author's existing column.

## Positive Observations

- The two items are genuinely one job, and the outline's instinct to batch
  them is right — Item B's first-that-exists Prerequisite is what makes Item
  A's prose route reviewable at all. (The outline did not *say* this; the fix
  made the link explicit rather than inventing it.)
- Item A's central re-derivation is correct and non-obvious: the removal R1
  asks for already happened in the `/build` merge, and what is left is the
  gate's body carrying claims nobody re-checked. That is exactly the
  `feedback-stale-claims-survive-reference-sweeps` pattern, correctly applied
  to the job's own premise.
- The false criterion is correctly identified and correctly sourced.
- Item B's inheritance rule is the sharp part of the design and is presented
  as such, with the failure mode named ("Recomputing is exactly the bug").
- §Provenance instantiates its own contract in the artefact that proposes it —
  first-pass evidence the contract is writable.
- Every Key decision carries an accepted tradeoff, per
  `design-content-rules.md`.

## Recommendations

- **The sweep is the risk, not the design.** The exit condition is now
  specific enough to execute, but it is a prose instruction with no validator.
  Consider having the executor paste the classified hit list into the commit
  or the review report rather than asserting it ran.
- **Worth a user decision:** binding the preconditions to the prose path
  (Key decision 5) is a real behaviour change — a prose job that names no edit
  targets now returns to design. It is the correct resolution of an existing
  contradiction, but it is a resolution, not a restatement.
- **Also worth a user decision:** the `docs/design.md` §6.4 decision for
  Provenance needs a D-number and phrasing; whether the D-55 contradiction is
  settled in the same entry or a separate one is the author's call.
- The `plans/README.md` staleness and the `memory/MEMORY.md` over-cap issue
  remain correctly OUT; no reason to pull either in.

---

**Ready for user presentation**: Yes. No ESCALATION — every finding was
fixable within the outline.
