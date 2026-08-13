# Classification: edify-recall-skill

- **Classification:** Moderate
- **Implementation certainty:** High — approach fully specified in the approved
  design (`docs/superpowers/specs/2026-08-11-edify-recall-skill-design.md`,
  FR1-FR9), itself empirically tested (D7) and iterated through several
  rounds of review this session.
- **Requirement stability:** High — all FRs agreed, each with a concrete
  mechanism; no open questions remain in the design doc.
- **Behavioral code check:** No — the only code file touched
  (`plugin/bin/prepare-runbook.py`) gets a docstring-only edit (no new
  functions, logic paths, or conditional branches); every other change is
  prose (skill/agent markdown, one doc listing).
- **Work type:** Production — delivers a working recall skill and its
  rewiring into the pipeline's agents.
- **Artifact destination:** agentic-prose (`plugin/skills/recall/SKILL.md`
  new; 4 skills + 4 agents under `plugin/skills/`/`plugin/agents/` edited);
  one production-path file (`plugin/bin/prepare-runbook.py`) touched
  non-behaviorally.
- **Evidence:** FR1-FR9 mechanism completeness (design spec); D2/D6 already
  resolve the subagent-index and corpus-dependency questions;
  `agents/decisions/pipeline-contracts.md` T1-T6.5 — `recall` is not an
  author skill with a corrector, and none of the 8 call sites' output
  artifact formats change, so Author-Corrector Coupling has no update to
  make; `memory/workflow-pipeline-revival.md` — this build is the revived
  pipeline's own first end-to-end exercise, flagged there as the outstanding
  "real check"; `memory/feedback-decision-docs-are-living.md` — governs how
  `agents/decisions/*.md` references are treated in the rewire; composite-task
  decomposition considered and not applied: all 8 call-site edits are the
  same homogeneous mechanical rewire (inlined paragraph → skill invocation),
  none carries a behavioral-code trigger, so per-item routing would fragment
  one coherent build without changing any routing outcome.
