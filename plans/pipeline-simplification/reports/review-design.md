# Review — design record (task 7, D11)

**Scope:** `docs/design.md` in full, `docs/changelog.md` 2026-09-01 entry.
**Baseline:** `a4aad0c8`; changes reviewed at `06a431ec`.
**Verdict:** requirements met. 9 issues found, all fixed in the working tree.
No `UNFIXABLE`. Nothing committed.

## Method

Recall resolved through `plans/pipeline-simplification/recall-artifact.md`;
four entries read for this scope (`design-doc-writing`,
`feedback-decision-docs-are-living`,
`feedback-stale-claims-survive-reference-sweeps`,
`spec-enumerations-need-rederiving`).

Per `spec-enumerations-need-rederiving`, the retired-machinery sweep ran as an
`rg` over both docs *before* reading the task's list of rewired sections, so the
task list could not anchor it. Every file path, `D-N`, `L-N` and `FR-N` the
record names was resolved against the tree. Live claims were checked against
`plugin/skills/orchestrate/SKILL.md`, `references/dispatch-composition.md`,
`plugin/skills/runbook/SKILL.md`, `references/runbook-format.md`,
`plugin/agents/*.md` frontmatter, `plugin/fragments/review-requirement.md` and
`plugin/skills/design/SKILL.md`.

## Requirements verdict

**FR-7 acceptance — no present-tense claim describes the retired machinery.**
Holds. The sweep matched 21 lines across both docs; every survivor is
past-tense rationale (D-24's 2026-08-13-to-2026-09-01 step-file paragraph,
D-31's superseding pointer, the L-1 closure note), a §7 rejected alternative,
or an unrelated sense of the word ("marketplace manifest", "dependency
cycles", D-63's "expansion ranges", "glob expansion").

**FR-7 sections.** §1, §5.1, §5.3, D-24, D-26, D-30 to D-35, D-39, D-49,
D-69, §7 (four new entries), L-1, L-2, L-6 all rewired. D-26 T2 names
`runbook-corrector`; the table has five rows and no expansion row. Gate models
in the table match agent frontmatter: `design-corrector`, `runbook-corrector`,
`runbook-simplifier` and `corrector` are all `model: opus`.

**FR-1 to FR-6 as design facts.** All stated. One-stage terminal runbook (§5.3,
FR-9), expansion machinery deleted (§5.1 drops `docs/` from the plugin
listing; §7 and the changelog record the deletion), the corrector rename
(§5.3, D-26 T2), live prompt composition (FR-10, D-24), four dispatches per
slice with list revision (D-30, D-24), prose plus `Interfaces:` and never code
(§5.3, D-32).

**NFR-1.** The five distinguishers are all stated: requirement IDs on runbook
items (§5.3), pinned model tiers (§6.6 and the D-26 gate column), the `/proof`
human gate (§5.3, D-33, FR-16), fix-all correctors (D-27), tester/implementer
separation (D-24 consequences, D-30). §7 states plainly that deterministic
validation does not survive, citing D-51.

**NFR-2.** The changelog's only count, 7,029 lines / 97,724 tokens, matches
`reports/measurements.md` exactly. No estimate is presented as fact. Two stale
measured figures found (see below).

## Findings

### Major

**1. Stale verification stamp.** The header read `Verified against: 0eb3cdc2
(2026-08-14)` while the state layer had been rewritten for the 2026-09-01
tree. Every state claim in the document anchors to that commit, so a reader
checking for drift would diff the wrong range and see the whole simplification
as unexplained drift. *Fixed:* stamped `06a431ec` (2026-09-01), the commit
reviewed. The `Status:` line now names the 2026-09 simplification alongside
the 2026-08 revival, matching §1 and L-6.

**2. §5.1 named the wrong version.** "`plugin.json` version ==
`pyproject.toml` version — currently `0.0.3`". Both files hold `0.1.1`.
*Fixed.*

**3. §5.3 misstated when `verify-step.sh` runs.** It said "clean tree +
precommit after each dispatch". `/orchestrate` §3 runs it after GREEN, code
review and general items, and explicitly not after RED or test review, where
uncommitted tests are the designed state — a clean-tree gate there would fail
by construction. *Fixed:* the parenthetical now names the committing
dispatches and the RED exception.

**4. D-28 contradicted the shipped orchestrator.** "The orchestrator delegates
all reviews" is false for `inline` items, which D-30 says the orchestrator
executes itself; `/orchestrate` §2.1 routes that one path through the
proportionality rule in `plugin/fragments/review-requirement.md` and names it
as the exception. *Fixed:* D-28 gains a paragraph stating the exception and
its bound, so the decision survives with the real boundary rather than an
absolute that the code does not honour.

**5. The changelog dropped a rationale that stopped being true.** The
2026-08-13 entry records the planning/execution session boundary as kept "on
model-tier and context-budget grounds". D-25 now rests on context budget
alone, because orchestration no longer runs a tier below planning — but D-25
was missing from the rewired-decision list and nothing recorded the loss. A
future reader comparing the two entries would find the change unexplained.
*Fixed:* the list reads `D-24 to D-26`, and a short paragraph records which
ground was lost and why.

### Minor

**6. D-31's superseding pointer cited the wrong decision.** It attributed "the
runbook is terminal" to D-34, which decides execution *routes* and never
states terminality. *Fixed:* repointed to §5.3 and FR-9, where the claim
actually lives.

**7. §1 attributed live prompt composition to D-34.** That is D-24's decision;
D-34 carries the retired three-tier structure. *Fixed:* the bullet now cites
§5.3 and FR-9 for terminality, D-24 for composition, D-34 for the structure it
replaced.

**8. `Status:` line** — folded into finding 1.

**9. §5.2's module enumeration omitted `tokens_cli`,** though FR-4 pins the
CLI requirement to `tokens_cli.py`. *Fixed.*

## Verified, no defect

- Every path the record names exists: `verify-step.sh`,
  `dispatch-composition.md`, `runbook-format.md`, `triage-feedback.sh`,
  `escalation-acceptance.md`, `check_line_limits.sh`,
  `check-version-consistency.py`, `bootstrap-venv.sh`, `hooks.json`,
  `bootstrap-venv.bats`, `plans/reports/triage-feedback-log.md`.
- §5.3's agent roster is exactly the eleven files in `plugin/agents/`.
- D-34 and D-35 cite `/design` Phase 0 and Phase C.5; both labels exist in
  `plugin/skills/design/SKILL.md`.
- D-33's ordering (corrector → simplifier → `/proof`) matches
  `/runbook` steps 5, 6 and 7.
- L-6's claim that `tdd-auditor` detects the implementation-shortcut risk is
  supported: its per-slice check 3 ("GREEN modified no reviewed test") names
  that shortcut as the one the audit exists to catch.
- The changelog entry is dated, design-significant throughout, and consistent
  with the record.

## Not flagged — scope

`memory/` and its consolidation are out of scope, so **L-5's figure was left
alone**: it says `memory/MEMORY.md` is "~28.9 KB against a 24.4 KB limit", and
`wc -c` now returns 32,346 bytes (31.6 KB). The limitation still holds and its
direction is unchanged; the number is stale, and updating it belongs with the
consolidation item (§1 Next). Flagging it here for the lead to route.

Also left untouched per the scope list: the plugin files themselves, the
design-outline stage and `outline-corrector`, `docs/superpowers/`, `CLAUDE.md`,
`README.md`, and the size of `docs/design.md`.
