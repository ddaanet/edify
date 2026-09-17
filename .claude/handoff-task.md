## Current task

`plans/design-routing-and-provenance/outline.md` is proofed and corrector-reviewed, ready to execute: it collapses `/design`'s duplicated execution-routing block into one shared `references/route-to-execution.md` node asking "does this work need a runbook?", and adds a `## Provenance` section to every `/design` artefact carrying the deliverable's base commit, so a second design-to-deliverable pass reviews the whole diff from the original base. The outline's scope was narrowed twice during review — the pointer replaces the routing block only (`write-outline.md:206-228`), not the enclosing sufficiency gate, and `build/SKILL.md` §4.1's own "Direct execution" heading is explicitly out of scope so the exit-condition grep does not rewrite it.

This is also the first exercise of the merged `/build`, which no session has run yet.
