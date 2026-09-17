# Open items

## Open decisions

- **`plugin/agents/design-corrector.md` is now 401 lines**, one over the 400 soft cap, pushed there by Item B's 7-line Provenance criterion. Per `memory/line-caps.md` a file parked at its cap has stopped signalling and prose must not be shaved to fit — so this is a split-or-accept call, not a trim. Not acted on.
- **Scope deviation in Item A, applied and needing confirmation.** The outline's §Scope said `write-design.md`'s C.5 heading and lines :66/:68 "stay", while Item A's §3 said the name "execution readiness" is stale and should be renamed. Read the scope line's rationale as being about *retention* (the node does not carry those lines), the heading became "C.5. Execution Route and Handoff" and :66/:68 were reworded off "execution-readiness". The `C.5` label itself was kept — it is a phase id in a C.1–C.5 sequence and `write-design.md:53` depends on it.
- **`design/SKILL.md:133` was left unchanged**, though the outline listed it alongside :139 for Item B. That route says "per `references/write-outline.md`", which reaches `research-protocol.md` §A.5, so Provenance arrives transitively; the outline's own stated reason for touching SKILL.md applied only to :139, and the hub is at 175 lines against a ~200 guideline.

## Remaining

- `/proof`'s verdict prompting is too formal. Replace the `(a)pprove (r)evise (k)ill (s)kip` prompt in `plugin/skills/proof/SKILL.md` §Item Iteration with: propose a verdict conversationally, show the amended item, capture the verdict from the reply. Couples to `references/item-review.md`; route through `/design`.
- deliverable-review follow-up (skill-review decision 2, second half): Criticals route to a fresh design-to-deliverable round, Majors and Minors to a direct /build flow. Depends on /build accepting work with no runbook. `inbox/brief-review-feeds-back-into-design.md` (arrived 2026-09-17 from the handoff plugin repo) is a brief on this same seam and should be read first.
- The remaining `plans/skill-reviews/` findings beyond the five settled decisions — 24 critical / 74 major / 91 minor across eleven skills, none actioned. The proof pass found at least one already fixed in source, so verify each against the file before acting.
- Pilfer defect 21 (corrector-skeleton dedup), carrying: the unreachable 'when reviewing runbooks/plans' criteria in `corrector.md` ~293-304; the corrector family's `Skill(edify:recall)` (`corrector.md:184`, `runbook-corrector.md:59`) against the by-path recall rule; `review-requirement.md`'s routing table still routing 'plans' to `edify:corrector` with no outline/runbook rows (defers to D-26).
- FR-12 remainder beyond defect 21: per-class skill-body length targets, which have no calibration data.
- `/design plans/pilfer-superpowers/` once Q-1 and Q-3 settle.
- Extend /recall to load skills (`craft`, `plugin-craft`, `sandbox-lies`) as well as memory files; the recall artifact format must allow naming them. Rationale in `inbox/recall-skill.md`.
