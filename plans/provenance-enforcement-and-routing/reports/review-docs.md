# Review gate — design documents (Items 1.3, 1.8)

Baseline `1f54633b8bf3425a2c3cbd30bc9482049c216522`. Scope: `docs/design.md`,
`docs/changelog.md`. Reviewed as `edify:corrector` under living-doc criteria
(`craft:design-doc-writing` 0.2.0), since `edify:design-corrector` is scoped to
`plans/<job>/design.md`.

## Findings

### C-1 (Critical, fixed) — the validation gate's new behaviour was unrecorded

KD-7 and KD-8 change a contract the living design records in three places, and
Item 1.3 touched none of them.

- `docs/design.md` NFR-1 cited `MAX_LINES=400`, a variable the shipped
  `scripts/check_line_limits.sh` no longer has, and stated the requirement as
  "No source module exceeds 400 lines" — now false in both directions: the
  check covers markdown, and a `SKILL.md` hub's cap is 200.
- D-69's heading asserted "400 lines is a hard per-module limit", which the
  path-picked cap and the allowlist ceiling both contradict.
- D-46 enumerated `just precommit` as "line limits, lint, tests" — the
  non-fixing `rumdl fmt --check` that now runs ahead of the guard was missing.

Fixed in place: NFR-1 restated with the path-picked caps and repointed at the
script, its allowlist sidecar and `tests/test_line_limits.py`; D-69's heading
rewritten and one paragraph added recording the markdown scope, the
formatter-before-guard ordering and the allowlist ratchet with its rationale
(a hard gate is red on its first run, a warn-only gate never turns red); D-46's
list gained "formatting". No new section was added, and no allowlist contents
or line counts were written into the doc — per the skill's
no-measurement-of-mutable-state rule, only the mechanism is recorded.

### C-2 (Major, fixed) — L-2 stated a superseded parameter set as current truth

L-2 read "The file-count and component-count figures `/design` uses to triage
complexity **and decide whether work needs a runbook** have no empirical
calibration". After D-82 the runbook decision carries no figures at all — its
second discriminator is judgement with no item count behind it. Corrected to
split the two claims and cite D-82 alongside D-34 for the route structure.

### C-3 (Minor, fixed) — dangling reference in D-80

"`git log`, `git merge-base` and `HEAD` are all the recomputation **the Critical
case names**" — "the Critical case" has no antecedent in `docs/design.md`; it is
the corrector's report severity from KD-1's table, which the living design does
not carry. Reworded to "all recompute what the rule says to inherit".

### Accepted without change

- **D-82/D-83 citation form.** They cite `build/references/phase-boundary.md`,
  `build/references/tdd-slice.md` and `runbook/references/runbook-format.md`.
  §6.5's pre-existing form is the bare `references/route-to-execution.md`; §5
  and other §6 entries use the full `plugin/skills/...`. The skill-qualified
  form is a third shape, but the bare form would be ambiguous across skills and
  the full form is not §6.5's convention. Left as shipped.
- **D-82's closing rejected-alternative sentence** ("Routing on the material
  instead — …") reads as contrast, not as history, and the doc's decision
  entries carry that shape elsewhere. Not narration.

## Verification against what shipped

Compared to `plugin/skills/design/references/route-to-execution.md`,
`plugin/skills/build/SKILL.md` §4.3, `plugin/skills/build/references/tdd-slice.md`
and `plugin/skills/design/references/write-outline.md`:

- **D-80** names `edify-review-range.sh`, invoked by bare name from the plugin's
  `bin/`; states stop-on-conflict with the "neither value substituted" ground
  and the one-hop rule; narrows "no mechanical validator" to the write side;
  states KD-1's copy/`TODO` split and drops "cannot repair it". Matches KD-1 and
  KD-2.
- **D-35** and the `outline.md`-consumers passage say four callers and that
  Phase 0 fixes the route only for Simple and Moderate agentic-prose. The four
  callers are verified in the tree: `write-outline.md:256` (multi-sub-problem
  gate), `write-outline.md:294` (Outline Sufficiency Gate), `write-design.md:92`
  (C.5), `design/SKILL.md:234` (Phase 0 Moderate non-prose, step 4 after
  `/proof`). Matches KD-5.
- **D-39** keeps stale-instruction risk as its own ground — the runbook step
  that edits the runbook skill — and cites D-82 only in its closing
  generalisation. As specified.
- **D-82** matches `route-to-execution.md` as shipped: three branches in the
  stated order, two discriminators either sufficient, the second marked
  **ungrounded** with no threshold, commutativity relocated under the first.
- **D-83** matches `build/SKILL.md` §4.3 ("When the item carries `Slices:` it
  carries nothing else to execute") and `tdd-slice.md:3-7` ("An item carrying
  `Slices:` … reaches here from a runbook, or from an outline or design routed
  to `/build`"). `Slices:` is the trigger in any artifact, as specified.

## KD-to-decision coverage

| KD | Contract | Recorded at | State |
|---|---|---|---|
| KD-1 | Corrector's Provenance repair is a table, not a ban | D-80 *Accepted tradeoffs* | Shipped by Item 1.3 |
| KD-2 | Script establishes the review range, stops on conflict | D-80 *Consumer* | Shipped by Item 1.3 |
| KD-3 | Route asks whether the work needs the runbook layer | D-82 (new), D-39 closing | Shipped by Item 1.3 |
| KD-4 | An outline carries a TDD change as a `tdd` item | D-83 (new) | Shipped by Item 1.3 |
| KD-5 | Phase 0's Moderate non-prose route reads the node | D-35, §6.5 artifact-consumers passage | Shipped by Item 1.3 |
| KD-6 | A not-routable sub-problem reopens only its own entry | **No home** — the living design records no multi-sub-problem gate detail (`rg 'sub-problem' docs/design.md` is empty). Gate-internal branch, not a recorded contract. Carried by the changelog entry only. | Correctly absent |
| KD-7 | Markdown guard: path-picked cap, allowlist, ceiling | NFR-1, D-69 | **Missing — added by this review (C-1)** |
| KD-8 | rumdl MD013 reflow, non-fixing check in precommit | D-69, D-46 | **Missing — added by this review (C-1)** |

## Contradiction check

`rg` over D-26, D-30, D-34, D-36, D-37, D-39, D-42 and §7/§8 for routing claims
D-82 or D-83 may contradict:

- **D-26** T5 ("Design/Outline → Implementation (no runbook)") — consistent; the
  gate row makes no routing claim.
- **D-30** — the phase-attribute `tdd`/`general` type is a runbook property;
  D-83 cites D-30 explicitly for that and keys `/build` on `Slices:` instead. No
  contradiction.
- **D-34** — one execution skill whatever the work arrived as. Consistent.
- **D-36** — ceremony by artifact destination; says nothing about the route.
- **D-37** — "Simple therefore gets the same four steps as Moderate
  agentic-prose — outline, proof, commit, route to `/build`" agrees with D-35's
  corrected text.
- **D-42** — model tier only.
- **§7 Rejected alternatives** — no routing claim touched by this job.
- **§8 L-2** — contradicted D-82; fixed (C-2).

## Changelog

The 2026-09-20 entry is accurate against what shipped: the three-branch route,
the two surviving discriminators with the second marked ungrounded, the
commutativity definition relocated under the first, `Slices:` as `/build`'s
trigger, the three-to-four caller count, and KD-6's branch — verified against
`write-outline.md:259-269`, which matches the entry clause for clause. Its third
paragraph names the 2026-09-17 entry and narrows its "preconditions, which bind
every branch including prose" to the first precondition, stating that the second
binds the `/build` branches only. As required.

`git diff 1f54633b -- docs/changelog.md` shows the new entry added above the
2026-09-17 entry, which is otherwise changed only by the 80-column reflow
(`f375c9d9`) — every hunk in it is a re-wrap with identical words. Older entries
likewise reflow-only. No edit to the write-time record.

## Reflow damage

`rg -n '\*\*$|`$' docs/design.md docs/changelog.md` returns 39 hits; every one
is a line ending on the *closing* backtick of a complete code span or the
closing `**` of a complete bold run. Confirmed mechanically by an awk pass
counting backticks per line outside fenced blocks — no line has an odd count, so
no span is split across a wrap. No defects.

## Line count — unresolved, needs a call

`docs/design.md` was 1221 lines, its allowlist ceiling. The three fixes above
put it at **1234**, 13 over. The additions were compressed to the minimum that
still states the mechanism and its ground; trimming existing prose purely to
satisfy the counter is the anti-pattern D-69 itself names, and splitting an
allowlisted file is out of this job's scope ("Each is its retiring job's work").

`scripts/check_line_limits.sh` is therefore red:

```
oversized-file: docs/design.md: 1234 lines > 400
```

This is the first-growth red the outline's Risks section predicted ("until the
file is trimmed or the ceiling raised by hand. By design; the first red is not a
regression"). Two resolutions, neither taken here: raise the
`docs/design.md` ceiling in `scripts/check_line_limits.allow` to 1234, or open
the trim job the entry's "no job yet" note anticipates. Raising a ceiling on its
first growth defeats the ratchet, so it is my human partner's call rather than
this review's.

`rumdl fmt --check -q --no-cache docs/design.md docs/changelog.md` exits 0.

## git diff --stat

```
 docs/design.md                       | 51 ++++++++++++++++++++++--------------
 plans/reports/triage-feedback-log.md |  1 +
 2 files changed, 33 insertions(+), 19 deletions(-)
```

`plans/reports/triage-feedback-log.md` is **not this review's change** — it is an
appended `2026-09-20 | provenance-enforcement-and-routing` row from another
agent's `triage-feedback.sh` run, uncommitted in the working tree. Reported, not
touched.
