# Validating: deliverable-review finds Critical/Major defects across multiple rounds

Claim under test: deliverable-review has a tendency of finding Critical and
Major defects over multiple rounds on the same job, so a round-N review must
cover the complete change including the fix commits produced after earlier
rounds.

## 1. Every deliverable-review report in the repo

| Report | Job | Date | Range (as stated) | Critical | Major | Minor |
|---|---|---|---|---|---|---|
| `plans/edify-recall-skill/reports/deliverable-review.md` | edify-recall-skill | 2026-08-13 | commit `6108f610` (single commit, already on `main`) | 1 | 3 | 3 |
| `plans/reports/deliverable-review-prioritize.md` | prioritize skill | 2026-02-16 | not stated (three named artifacts) | 0 | 0 | 4 |
| `plans/reports/deliverable-review-blocker-merge.md` | wt-blocker-merge-fix | 2026-02-21 | not stated (session.md baseline) | 0 | 0 | 5 |
| `plans/skill-reviews/deliverable-review.md` | deliverable-review skill itself | 2026-09-16 | working tree at that date (skill-reviewer agent, no Write tool) | 3 | 7 | 9 |
| `plans/skill-reviews/reports/verify-deliverable-review.md` | verification of the above, against 2026-09-21 tree | 2026-09-21 | n/a — status check per finding, not a fresh review | n/a (3 open) | n/a (7 open) | n/a (7 open) |
| `plans/pipeline-simplification/reports/deliverable-review-agentic-prose.md` | pipeline-simplification, Layer 1 (agentic prose) | 2026-09-02 | `f3f1015b..HEAD` | 1 | 7 | 12 |
| `plans/pipeline-simplification/reports/deliverable-review-docs.md` | pipeline-simplification, Layer 1 (docs/config) | 2026-09-02 | `f3f1015b..HEAD` (`993b23b7`) | 1 | 5 | 9 |
| `plans/pipeline-simplification/reports/deliverable-review.md` | pipeline-simplification, Layer 2 (merged) | 2026-09-02 | `f3f1015b..993b23b7` | 3 (1 pre-existing) | 13 (3 pre-existing) | 24 (6 pre-existing) |
| `plans/design-routing-and-provenance/reports/deliverable-review.md` | design-routing-and-provenance (round 1) | 2026-09-17 | `926e372d..HEAD` | 0 | 4 | 3 |
| `plans/provenance-reach-and-sweep/reports/deliverable-review.md` | provenance-reach-and-sweep (round 2) | 2026-09-18 | `926e372d..HEAD` (same base) | 0 | 6 | 5 |
| `plans/provenance-enforcement-and-routing/reports/deliverable-review-code-tests.md` | provenance-enforcement-and-routing, Layer 1 (code/tests partition) | 2026-09-21 | same job's range | 0 | 3 | 8 |
| `plans/provenance-enforcement-and-routing/reports/deliverable-review.md` | provenance-enforcement-and-routing (round 3, merged) | 2026-09-21 | `926e372d..HEAD` (same base) | 0 | 6 | 15 |

Counts are read from each report's own `## Critical` / `## Major` / `## Minor`
(or `Findings`) sections and, where present, an explicit summary line — not
inferred. `verify-deliverable-review.md` is not a fresh review; it is a
resolution-status audit of the 2026-09-16 report's 19 findings against a later
tree, so it has no independent severity counts and is excluded from the
"rounds" analysis below.

## 2. Chains reconstructed from `## Provenance` / `Derived from:`

Only one chain exists in the repo: the three `/design`-provenance jobs. Their
outlines carry matching `## Provenance` sections with `Derived from:` naming
the prior job's deliverable-review report, and all three inherit the same
`Base:` (`926e372d02a0366202b2bb6a684551128d1f2a66`), copied verbatim rather
than recomputed each time — confirmed at
`plans/provenance-reach-and-sweep/outline.md:9-16` and
`plans/provenance-enforcement-and-routing/outline.md:12-17`. Because the base
never moves and the range is always `<base>..HEAD`, each round's review range
is a strict superset of the previous round's: it includes the original
deliverable, all of round 1's fixes, all of round 2's fixes, and so on.

No other chain exists: `plans/pipeline-simplification/`,
`plans/edify-recall-skill/`, `plans/reports/deliverable-review-prioritize.md`
and `plans/reports/deliverable-review-blocker-merge.md` have no `Derived
from:` referencing a prior deliverable-review report — each is a single round
(pipeline-simplification's three reports are Layer 1 / Layer 2 of *one*
round, not sequential rounds).

### The provenance chain, round by round

| Round | Job | Report | Critical | Major | Minor |
|---|---|---|---|---|---|
| 1 | design-routing-and-provenance | `plans/design-routing-and-provenance/reports/deliverable-review.md` | 0 | 4 | 3 |
| 2 | provenance-reach-and-sweep | `plans/provenance-reach-and-sweep/reports/deliverable-review.md` | 0 | 6 | 5 |
| 3 | provenance-enforcement-and-routing | `plans/provenance-enforcement-and-routing/reports/deliverable-review.md` | 0 | 6 | 15 |

Each round's outline states explicitly that it exists to work the prior
round's findings: round 2's outline opens "Second pass on
design-routing-and-provenance, working its deliverable review's 4 major and 3
minor findings" (`plans/provenance-reach-and-sweep/outline.md:3-4`, matching
round 1's own count); round 3's opens "Third pass in the
design-routing-and-provenance line, working the 6 major and 5 minor findings
of provenance-reach-and-sweep's deliverable review"
(`plans/provenance-enforcement-and-routing/outline.md:4-5`, matching round
2's own count). Critical stayed at 0 throughout; Major held at 4 → 6 → 6;
Minor rose 3 → 5 → 15.

### Did later rounds find defects in earlier rounds' fix commits?

Yes, traced through `git log`. Round 1's own commits were `6a98c5fb`
(18:39:59) — introduces the `## Provenance` contract and the corrector
criteria — and `fb542dc2` (18:55:31) — applies round 1's own Layer-1
skill-review findings to `plugin/skills/design/SKILL.md`,
`plugin/skills/deliverable-review/SKILL.md`,
`design-content-rules.md`, `research-protocol.md`,
`route-to-execution.md`. The next commit, `6639cc92` (19:02:50, "correctors
verify provenance without fabricating a base"), adds the "Never fill in
`Base:` yourself" directive to both `outline-corrector.md` and
`design-corrector.md` in direct response to round 1's M-1/M-2 findings about
the inheritance rule's enforceability.

Round 2's own review (`provenance-reach-and-sweep/reports/deliverable-review.md`)
then finds, as its own M-1 and M-2, two Major defects **inside that exact
directive**: M-1 ("The corrector repair directive destroys a correct `Derived
from:`") and M-2 ("The blanket ban blocks the one repair that is not a
recomputation") both cite `plugin/agents/outline-corrector.md:117` and
`plugin/agents/design-corrector.md:175` — the lines `6639cc92` wrote. This is
a later round's review finding Major defects in a fix commit that was itself
produced to close an earlier round's findings, inside the same growing range.
Round 2's M-4 ("The consumer never checks the inheritance rule it depends on")
similarly cites `plugin/skills/deliverable-review/SKILL.md:31`, a file
`fb542dc2` (round 1) touched.

Round 3's review contains one finding of the same shape but from outside the
chain: F-4 ("The trailing sweep commit reintroduced M-6, the defect form this
job eliminated") reports that a commit from a **different, unrelated job**
(`5594a753`, the `remaining-sweep` plan) reintroduced the exact pattern round
3's own Item 1.9 had just eliminated. Round 3's own F-6 names this explicitly
as a property of the unbounded-range mechanism: "nothing bounds commits
landing *after* the work, and `..HEAD` grows without limit until the review
runs." So F-4 is evidence for the general "review the complete range"
principle, but not evidence of a defect specifically in *this chain's own*
fix commits — F-1, F-2, F-3 (the three Majors that are in-scope for round 3's
own job) are new defects in round 3's own new code (the two scripts), not
regressions of round 1's or round 2's fixes.

## 3. Session-log counts

Session transcripts: `/Users/david/.claude/projects/-Users-david-code-edify/*.jsonl`
(161 files total).

- `grep -l 'deliverable-review' *.jsonl` → **76 sessions** contain the string
  somewhere.
- `grep -o 'edify:deliverable-review' *.jsonl | wc -l` → **629** raw
  occurrences across **41** sessions.
- `grep -o '"skill":"edify:deliverable-review"' *.jsonl | wc -l` → **4**
  occurrences, in exactly **2** sessions
  (`2a5f3ca7-51ba...jsonl`, `f875be65-...jsonl`).
- `grep -c '"text":"/deliverable-review' *.jsonl` → **0** (no slash-command
  invocation recorded in that literal form).

**These counts are unreliable as a "number of review runs" measure and I am
not treating them as such.** Reasons:

- Claude Code's JSONL transcript format re-serializes prior conversation
  state into later entries (tool results, system-reminder injections that
  repeat the full skill-description listing every turn), so a raw substring
  count like the 629 figure counts re-transmissions of the same text, not
  events. It does not correspond to 629 reviews — only 12 deliverable-review
  report files exist in the repo (§1).
- Narrowing to the literal Skill-tool invocation JSON field
  (`"skill":"edify:deliverable-review"`) drops the count to 4, in 2 sessions
  — undercounting relative to the 12 reports found on disk, because several
  of those reviews (e.g. the 2026-02 ones, predating the current Skill-tool
  plumbing; and delegated Layer-1 sub-reviews dispatched as `Agent` calls
  rather than a top-level `Skill` call) would not appear under that exact
  field/value pair.
- I did not find a single grep pattern that reliably counts "one review
  actually ran" across the whole history; the two figures (76 sessions /
  4 tool-invocations) bracket the true number without pinning it, and no
  further narrowing was attempted since it would not change the verdict
  below, which rests on the report files themselves.

## Verdict

**The evidence supports the claim, for the one chain in the repo where it is
testable.** The three-round `/design`-provenance chain
(design-routing-and-provenance → provenance-reach-and-sweep →
provenance-enforcement-and-routing) shows Major findings at every round (4,
then 6, then 6) and rising Minor findings (3, 5, 15), with Critical at 0
throughout. Critically, round 2's review (`provenance-reach-and-sweep`) found
two Major defects (M-1, M-2) squarely inside the fix commit
(`6639cc92`) that round 1's own findings had produced — a direct instance of
"a later round found Critical/Major defects in an earlier round's fix
commit." That is only detectable because the range stayed `<base>..HEAD` with
`Base:` inherited verbatim rather than recomputed per round (D-80), so round
2's review necessarily covered round 1's fix commits along with round 1's
original deliverable. Round 3 adds a different but related data point (F-4,
F-6): the same unbounded-range mechanism also pulled in an unrelated job's
regression of a round-3 fix, which the job's own outline (F-6) reads as
evidence for, not against, keeping the range wide rather than narrowing it to
"just this round's new commits." No other job in the repo has more than one
deliverable-review round, so the claim is unverified — not contradicted —
outside this one chain.
