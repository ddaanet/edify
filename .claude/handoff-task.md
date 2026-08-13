/inline just executed the edify-recall-skill plan: new `plugin/skills/recall/SKILL.md` plus rewires across `requirements`, `design`, `orchestrate`, `review-plan`, `proof` skills and the four corrector agents (per `docs/superpowers/specs/2026-08-11-edify-recall-skill-design.md` FR1-FR9). All three group reviews (skill-reviewer, agent-creator, corrector) passed; one gap (`Skill` missing from `allowed-tools` in `requirements`/`proof`) was fixed inline. Ready for `/deliverable-review plans/edify-recall-skill`, then commit.

Separately, the pilfer-superpowers capture (plans/pilfer-superpowers/requirements.md) is written but not user-validated — /proof it, then /design once its open questions settle. The comparison analysis and repair backlog live in plans/pilfer-superpowers/reports/.

## Open decisions

- Adoption sequencing: run the pipeline end-to-end exercise before pilfer-superpowers FR-5/6/7 (they modify never-exercised orchestration paths), or start with the text-only FRs — the e2e run would also produce the violation transcripts Q-4 needs.
- pilfer-superpowers Q-1: depend on the installed superpowers plugin (invoke its skills by name) vs vendor copies into the edify plugin — blocks FR-13.