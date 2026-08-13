## Current task

The `edify:recall` rewire is reviewed and closed out — findings and the fixes applied for each are recorded in `plans/edify-recall-skill/reports/deliverable-review.md`. Recall ended up with 15 call sites, not the 9 the design enumerated; the six extra came from grepping the pattern rather than trusting the spec's list.

The open thread is `plans/pilfer-superpowers/`: its requirements capture is written but never user-validated, waiting on `/proof` and then `/design` once the decisions below settle. Comparison analysis and repair backlog are under that plan's `reports/`.

## Open decisions

- Adoption sequencing for pilfer-superpowers: exercise the revived pipeline end-to-end before FR-5/6/7 (they modify orchestration paths that have never been run, and an e2e run would also produce the violation transcripts Q-4 needs), or start with the text-only FRs.
- pilfer-superpowers Q-1, which blocks FR-13: depend on the installed superpowers plugin and invoke its skills by name, or vendor copies into the edify plugin.