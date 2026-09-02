## Brief: migrate edify-specific memories out of the ddaanet tier

2026-09-02

Written from gitlore, where a transcript-corpus analysis of memory reads (`gitlore/plans/2026-09-02-recall-log-analysis.md`, `gitlore/plans/2026-09-02-ddaanet-design-moment-facts.md`) found that the ddaanet tier carries a block of facts whose only worked example is edify's ghmem or ledger work, read by no other repo's sessions in seven weeks. They move into edify's own memory store, merged by design moment.

### Decisions

- Twelve tier facts leave `memory/ddaanet/` and land in `memory/` as edify project facts. Deletion happens here, in edify, so the removal and the new facts ride one memory commit; the other tier consumers take the deletion on their next `/gitlore:merge`.
- Merge by moment rather than copy one-to-one. Target shape, four facts:
  - `scoring-formula-design` ← `ground-formulas-in-data`, `provisional-values-not-provisional-code`, `marginal-weakness-is-not-misweighting`.
  - `data-model-design` ← `optional-means-source-can-omit`, `dont-bake-in-guarantees`, `shape-rules-are-not-duplication`, `no-code-for-impossible-cases`.
  - `review-slices` ← `slice-history-forward-not-by-cherry-pick`, `slice-uncommitted-tree-via-index`.
  - `style-edit-briefs` ← `uncram-prose-shapes`, `prose-voice-does-not-delegate`.
  - `edify-python-standards` moves whole, renamed `python-standards`; the body already names this repo as the reference config.
- Two more tier facts stay in the tier but get an edify twin: `honest-line-count-caps` and `spec-contract-size-predicts-pr-size` carry edify's 400-line PR and file caps. Write the cap-specific content into one edify fact, `line-caps`, and leave the tier copies alone; gitlore's tier-owner pass will generalize them.
- Each merged fact keeps every rule and every worked example of its sources. A merge drops duplication of framing, not content. Where a source has a `**Why:**` grounded in a ghmem or ledger incident, keep that grounding: it is the reason the fact is edify's.
- Index lines follow the recall test: name the moment as an agent meets it ("choosing a weight or threshold for a score", "deciding whether a field is optional"), then the rule. The old lines were decisions without a trigger, which is why nothing recalled them.

### Constraints

- Never commit inside the memory submodule. Edit files, commit the parent, and the pre-commit hook gates memory. This is a memory-only change, so per `ddaanet/gitlore-memory-administration-no-parent-commit` writing the approved summary is enough; no parent content commit is needed to make it land.
- Run `/gitlore:merge` first. edify's tier pin is behind gitlore's, and deleting from a stale tier head produces a conflict at the next merge.
- Delete a tier fact by removing its file under `memory/ddaanet/` and its line from the root `memory/MEMORY.md`. Per `ddaanet/gitlore-tier-merge-direction`, removing the root line propagates to the tier's carrier index in the same pass; do not edit `memory/ddaanet/MEMORY.md` by hand.
- Use the `gitlore:memory-writing` skill for each new fact and its index line. The new lines take a bare path (`memory/scoring-formula-design.md`), not the `ddaanet/` prefix.
- edify's root index is 32.5KB against the ~24,985-byte loader cap. Moving twelve tier lines into project lines is byte-neutral unless merged; the four-fact shape is what buys the reduction. Report the before and after byte count of `grep '^- \[' memory/MEMORY.md | wc -c`.
- Finish with `/gitlore:push` so the tier deletion reaches the other consumers.

### Rejected approaches

- Leaving the facts in the tier with sharper index lines: zero cross-repo reads in seven weeks, and the tier index is itself over the loader cap, so every line spent on an edify-only fact pushes a shared line past the cutoff.
- Deleting from gitlore's side and rewriting in edify separately: two memory commits, and a window where the fact exists nowhere.
- Also moving `reconstructable-two-categories`: it is a handoff-design lesson, not edify's, and goes to the handoff repo in its own pass.

### Additional context

Read counts over the corpus, all repos combined: `no-code-for-impossible-cases` 4, `ground-formulas-in-data` 1, `shape-rules-are-not-duplication` 1, every other fact in the move set 0. `honest-line-count-caps` 6, `spec-contract-size-predicts-pr-size` 2.

The tier-side merges that stay in ddaanet (plan-writing, guard-design, folding singles into hubs) are gitlore's pass and are not part of this brief.
