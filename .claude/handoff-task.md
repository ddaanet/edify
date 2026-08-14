## Current task

The plan-agent rewire is complete and gated: `prepare-runbook.py` generates no agent definitions, step files open with a `## Context` block naming design, outline and `plans/<name>/common-context.md` and close with an `## Execution Contract`, and `/orchestrate` reads `subagent_type` from the manifest's Phase-Agent Mapping. Nothing is in flight.

The end-to-end pipeline exercise the rewire was blocking is the natural next piece. It matters more than usual here: the new step-file and manifest shapes are verified only by manual runs of the script against three runbook shapes, because `prepare-runbook.py` has no test coverage at all — the suite reaches it only indirectly through `validate-runbook.py`'s imports.

## Open decisions

- pilfer-superpowers Q-1, which blocks FR-13: depend on the installed superpowers plugin and invoke its skills by name, or vendor copies into the edify plugin. The corrector routing fallback added for defect 2 works either way and does not prejudge this.
- Adoption sequencing for pilfer-superpowers: exercise the revived pipeline end-to-end before FR-5/6/7, since they modify orchestration paths that have never been run and an e2e run would also produce the violation transcripts Q-4 needs — or start with the text-only FRs instead.
- Whether the planning-to-execution session boundary should survive now that agent discoverability no longer forces it. It was kept on the model-tier and context-budget grounds in `agents/decisions/orchestration-execution.md`, "When Managing Orchestration Context"; auto-chaining `/runbook` into `/orchestrate` was deliberately not taken as part of the rewire.