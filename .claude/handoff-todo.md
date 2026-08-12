## Remaining

- Review the committed `edify:recall` spec, then write its implementation plan.
- Build `plugin/skills/recall/` and rewire the eight call sites the spec names.
- Fold the local corpus, `agents/decisions/*.md` included, into a living design document.
- Exercise the revived pipeline end to end: `Agent` dispatch, name-based `SendMessage` resume, and the plan-specific agents `prepare-runbook.py` generates.
- Consolidate `memory/MEMORY.md` — it is over its 24.4KB read budget (28.6KB), silently dropping entries past the cutoff; last consolidated 2026-07-16.