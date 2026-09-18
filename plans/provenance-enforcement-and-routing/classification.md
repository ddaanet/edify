# Classification: provenance-enforcement-and-routing

**Requirements source:** `plans/provenance-reach-and-sweep/reports/deliverable-review.md`
**Completeness:** Each FR has concrete mechanism: Y — 10 of 11 as written; M-3's
fork settled by my human partner before this block (route by need for the
runbook layer, not by prose). Each NFR has measurable criterion: N/A — no NFRs.
**Routing:** Proceed to triage.

**Multi-item decomposition:** implicit bundling (a deliverable review carrying
11 findings) and explicit bundling (the task frame folds the formatter-gate
item in). Enumerated and checked individually. Nine come out on the same axes;
M-4 and m-5 do not and carry their own blocks.

## M-1, M-2, M-3, M-5, M-6, m-1, m-2, m-3, m-4

- **Classification:** Simple / Moderate agentic-prose (one route)
- **Implementation certainty:** High — each names its file and site
- **Requirement stability:** High — M-3 settled this session
- **Behavioral code check:** Does this task add functions, change logic paths,
  or add conditional branches? **No** — every site is `.md`
- **Work type:** Production
- **Artifact destination:** agentic-prose (`plugin/skills/`, `plugin/agents/`,
  `plugin/fragments/`) plus investigation (`docs/design.md`,
  `docs/changelog.md`)
- **Evidence:** Phase 0 §Classification Criteria; artifact-destination table;
  recall `ddaanet/audit-a-contract-across-its-surfaces`,
  `ddaanet/guard-reveals-singleton` (corrector duplication — deferred to
  pilfer defect 21), `feedback-decision-docs-are-living` (D-80 in place)

## M-4 — review-range script

- **Classification:** Moderate
- **Implementation certainty:** High — verdict table fixed in outline KD-2
- **Requirement stability:** High — my human partner: detect by script, stop
  on conflict
- **Behavioral code check:** **Yes** — a new script with six verdict branches
- **Work type:** Production
- **Artifact destination:** production (`plugin/skills/*/scripts/`) plus
  agentic-prose (the calling step)
- **Evidence:** shared convention "deterministic mechanical work belongs in
  the harness"; `verify-step.sh` as the in-repo precedent

## m-5 — markdown formatter and line guard

- **Classification:** Moderate
- **Implementation certainty:** High — tool and config chosen by measurement
  in `memory/ddaanet/markdown-formatter-choice.md`
- **Requirement stability:** High
- **Behavioral code check:** **Yes** — `scripts/check_line_limits.sh` gains a
  path-picked cap and an allowlist branch; Moderate minimum
- **Work type:** Production
- **Artifact destination:** production (`scripts/`, `plugin/portable.just`)
- **Evidence:** D-38 (per-item check); D-39 (work editing pipeline skills
  leaves the runbook pipeline, TDD per slice from the session); my human
  partner's instruction that this item needs no runbook ceremony

**Route:** one outline, `/proof`, then `/build plans/provenance-enforcement-and-routing`.
M-4 and m-5 ride as the outline's two tdd items rather than routing to
`/runbook`.

**Author-corrector coupling:** Author change: `/design` outline format gains
tdd items (outline KD-4). Coupled corrector: `outline-corrector`. **Update
needed: yes** — one criterion, outline Item 1.7. No mechanical validator.
