# 2026-09-21 — The release mechanism is recorded as a decision

Edify runs its own `scripts/release.sh` rather than the shared
`claude-plugin-dev` toolkit every other ddaanet plugin repo vendors. The call
was taken on 2026-07-16 but written down only in an evaluation page and a memory
note, so the living design had nothing to say about why the odd one out is odd.
It is now **D-87** in `docs/references/cli-and-package.md`.

The reason is not preference: `claude-plugin-dev` excludes this repo's shape in
its own record, as a repo non-goal and as a stated limitation, both naming
edify. Its recipe drives one manifest at the repo root, has no PyPI step and no
`pyproject.toml` awareness; edify's manifest sits a directory down and its two
version files move in lockstep (NFR-4). Adoption would therefore mean reversing
another project's decision, not configuring a tool — which is why "reconsider
the exclusion" is D-87's reopen gate rather than an available route.

Re-checking the 2026-07-15 evaluation against the tree dropped two of its
frictions. Submodule handling stopped being a need when D-10 flattened
`plugin/`. The marketplace side effect stopped distinguishing the two recipes
once edify's own script grew the same `MARKETPLACE_DIR` requirement and the same
synthesize-an-entry-if-absent branch. The evaluation page was left holding a
pointer to D-87 and those two corrections; it was deleted on 2026-09-22 once its
last staleness items were fixed, and the corrections moved into D-87's own
argument.
