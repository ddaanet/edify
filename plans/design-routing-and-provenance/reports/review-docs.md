# Human Docs Review: design-routing-and-provenance

**Reviewer:** delegated docs reviewer (opus)
**Baseline:** `a533a842573459032e7816271b3b55849fe37890`
**Date:** 2026-09-17
**Mode:** review-and-fix; all findings below are applied in the working tree

## Group

- `docs/design.md`
- `docs/changelog.md`

Axes: accuracy, consistency, completeness, usability. Sources of truth read for
accuracy: `plugin/skills/design/references/route-to-execution.md`,
`plugin/skills/design/references/design-content-rules.md` §Provenance Section,
`plugin/skills/design/references/write-outline.md`,
`plugin/skills/design/references/write-design.md`,
`plugin/skills/design/SKILL.md`, `plugin/skills/deliverable-review/SKILL.md`,
`plugin/skills/build/SKILL.md`, `plugin/agents/outline-corrector.md`,
`plugin/agents/design-corrector.md`.

## Verdict

Both requirements' docs work is present and, after the fixes below, accurate
against the shipped files. Six findings — two Critical, three Major, one Minor
— all fixed. One observation left unfixed and reported.

## Findings

### C-1 (Critical) — D-80 misstated the consumer's fallback

`docs/design.md` D-80 said `/edify:deliverable-review` "asks the user only when
the section is absent". The shipped `deliverable-review/SKILL.md:31` asks the
user in **two** cases: no Provenance section, *and* `git rev-parse
<Base>^{commit}` not resolving. The word "only" made the design record state a
narrower contract than the skill implements — exactly the drift D-80 exists to
close. The corrector amendment that added the unresolvable-base case landed
after D-80 was written.

**Fixed:** D-80 now reads "asks the user for the range when the section is
absent and when `<Base>` does not resolve to a commit", and labels the clause
*Consumer:* in the italic-label idiom §6.4 already uses.

### C-2 (Critical) — D-80 misdescribed corrector enforcement

D-80 said the clause is "enforced by the outline- and design-correctors only
after the artifact is written". True as far as it goes, but it omits the
load-bearing half of the shipped criterion: both correctors are barred from
supplying a `Base:` themselves and repair a missing or unverifiable one with a
`TODO` placeholder (`outline-corrector.md:117`, `design-corrector.md:171`). A
reader taking D-80 at face value would expect the gate to close the hole, when
in fact it can only mark it. That difference is what keeps a
corrector-computed base from becoming the silent recomputation the decision
forbids.

**Fixed:** the tradeoff clause now states that the correctors check after the
fact and cannot repair — "a base they supplied would be the same
recomputation, so they leave a `TODO` for the author instead".

### M-1 (Major) — D-35's "both sufficiency gates" was wrong twice over

The reworded D-35 said the node is read by "both sufficiency gates". Two
errors: `write-design.md`'s C.5 is not a sufficiency gate (it is C.5. Execution
Route and Handoff), and there are three call sites, not two —
`write-outline.md`'s Multi-Sub-Problem Sufficiency Gate (`:185`), its Outline
Sufficiency Gate (`:204`) and `write-design.md:70`. The sentence also inherited
the original's incompleteness: it implied every route decides its route at the
node, when `/design` Phase 0 triage fixes the route outright for Simple
(`/build`), Moderate agentic-prose (`/build`) and Moderate non-prose
(`/runbook`) — only Complex work reaches a gate at all.

**Fixed:** D-35 now says complexity and work type are decided at Phase 0,
"which also fixes the route for Simple and Moderate work; Complex work decides
its route later, at whichever gate confirms its terminal artifact — both of
`write-outline.md`'s sufficiency gates and `write-design.md`'s C.5 read
`references/route-to-execution.md`."

### M-2 (Major) — D-37 still carried the retired "Direct execution" label

D-37 opened with a scare-quoted **"Direct execution"** naming the in-session
path R1 retires. With the `/design`-local name gone, the only live definition
of that phrase in the tree is `/build` §4.1, where it means inline rather than
delegated dispatch — so a reader resolving D-37's term against the tree now
lands on a decision that says inline dispatch bypasses the integration-test
gate, review dispatch and the deliverable-review chain, which is false. This is
the wrapped `docs/design.md` hit Item A's exit condition predicted the
word-level grep would surface; it had been left unclassified.

**Fixed:** the phrase is replaced by what it denoted ("Doing the work in the
design session instead"), and D-37 now states the disambiguation explicitly —
the path is retired and so is its name, with `/build` §4.1 keeping the phrase
for the other meaning. This is the doc-side counterpart of the OUT item in
`outline.md` §Scope that protects `/build` §4.1 from the sweep.

### M-3 (Major) — duplicate decision id `D-79` (pre-existing)

`docs/design.md` carried **two** D-79 decisions: "Three planning artifacts, two
design routes, one execution skill" (§6.5) and "Two dispatches are fixed, and a
runbook item carries no model" (§6.6). The citation at D-37's tail, `(D-79)`,
was therefore ambiguous. Pre-existing — both landed before this job — but in
scope under cross-reference integrity, and newly consequential because D-80 was
allocated as the next free id from a sequence whose maximum was already taken
twice.

**Fixed:** the §6.6 decision (2026-09-16, the older of the two) keeps `D-79`;
the §6.5 decision (2026-09-17) is renumbered `D-81`, and D-37's citation
repointed. A repo-wide grep for `D-79` found no other citation in `docs/`,
`plugin/`, `plans/` or `.claude/`, so the renumber breaks nothing. Ids are now
unique; verified by `grep -o '^\*\*[DL]-[0-9]*' docs/design.md | sort | uniq
-d` returning empty.

### m-1 (Minor) — hard-wrap breakage in D-55 and the changelog

The reworded D-55 left a 22-column orphan line mid-paragraph ("them is findings
—"), and the changelog entry had one 83-column line. `docs/` is not covered by
`scripts/check_line_limits.sh`, so nothing catches these; the file's own
convention is ~78–80 columns.

**Fixed:** both paragraphs reflowed. No line in either changed region now
exceeds 80 columns.

## Consistency sweep

Grepped `docs/` case-insensitively for `execution.read`, `direct.execution`,
`C\.5`, plus separate `readiness`, `outline`, `deliverable-review` and
`baseline` passes. Every surviving hit classified:

| Hit | Classification |
|---|---|
| `changelog.md:17` — "`write-design.md`'s C.5" | accurate — narrates the pre-change state |
| `changelog.md:24` — "Execution readiness" / "direct execution" | accurate — names the retired terms as retired |
| `design.md:620` — "`write-design.md`'s C.5" | accurate — C.5 is a live heading |
| `design.md:500` — "readiness rules to all" | accurate — runbook item quality, unrelated |
| `design.md:855` — D-59 "merge-readiness" | accurate — review reporting, unrelated |
| `design.md:630-631` — "direct execution" in `/build` §4.1 | accurate — added by M-2's fix, correctly scoped |
| `design.md:625` — D-36 "direct implementation" | accurate — different term, describes prototypes |

Neighbouring decisions checked against D-35, D-80 and D-55 as reworded, and
found consistent without edits: **D-26** (T5 "Design/Outline → Implementation
(no runbook)" already names both artifact kinds), **D-27** (fix-all and
escalate — the correctors' `TODO` repair is an escalation to the author, within
the pattern), **D-34** (`/build` takes `runbook.md`, or `design.md` /
`outline.md` with no runbook), **D-36** (ceremony by artifact destination),
**D-81** (`outline.md` keeps both consumers), **D-60** (findings route to
`/design`). §5.3 enumerates skills, agents and scripts but not `/design`'s
`references/` nodes, so the new node needs no listing there.

## Cross-reference integrity

Every path, section and skill name in the changed text resolves:
`plugin/skills/design/references/route-to-execution.md`, `write-outline.md`,
`write-design.md` §C.5, both of `write-outline.md`'s sufficiency gates
(`:165`, `:191`), `/build` §4.1 (`build/SKILL.md:110`) and §5
(`build/SKILL.md:166`), `## Provenance`, `Derived from:`, `Base:`,
`/edify:deliverable-review`. Section numbering `6.1`–`6.10` is contiguous and
in order; D-80 sits at the end of §6.4 Pipeline contracts, which is where the
outline scoped it.

## Changelog entry

Dated 2026-09-17, design-significant, in the file's established voice (what
broke, what it cost, what replaced it). Three changes applied:

- **Ungrounded history claim.** "had been false since `/build` gained
  multi-session runs" asserts a moment I cannot verify — `/build` itself is one
  day old, and the criterion predates it under `/inline` and `/orchestrate`.
  Replaced with the grounded form: it "contradicted `/build` §5, which provides
  for a run spanning several sessions … true only while the design session did
  the work".
- **Verbatim echo of the design doc.** "a too-narrow diff reads as a clean
  review" appeared in D-80, in `design-content-rules.md` and in both
  correctors; the changelog repeated it word for word. One telling per
  artifact — the changelog now states the consequence in its own words and
  leaves the standing-rule phrasing to D-80.
- **Unclear sentence, plus a missing signpost.** "the `/design`-local name goes
  with the duplication" did not parse cleanly. Rewritten, and extended to name
  the two retired terms and to record that `/build` §4.1 keeps "direct
  execution" for inline-versus-delegated dispatch — the fact a future reader
  greps for. The corrector bar on supplying a base is also now recorded.

No estimates, figures or thresholds are asserted anywhere in the changed text;
the only quantity is "two lines and one `git rev-parse`" in D-80's tradeoffs,
which counts the shipped `## Provenance` block in
`design-content-rules.md:102-107`.

## Reported, not fixed

`docs/design.md:7` — **Verified against:** `f50ed025` (2026-09-02). Two weeks
and several design-significant changes stale. Left alone deliberately: the line
asserts that someone checked the *whole* document against a tree state, and
this pass checked two decisions and their neighbourhood. Advancing it would be
a claim I did not earn. My human partner may want to refresh it on the next
full read-through.
