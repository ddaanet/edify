## 2026-03-23: RCA — inline recall keywords in corrector prompt

**Deviation:** /inline Phase 4a corrector dispatch inlined recall keywords instead of referencing artifact path. Violated `delegation.md` "Recall Content In Delegation Prompts" rule.

**Root cause:** Pattern entrainment. Six test-driver dispatches (Phase 3) used inline keywords per runbook cycle specs. Corrector dispatch (Phase 4a) reused the same template instead of switching to artifact-path-only pattern. The inline skill correctly specifies `Recall artifact: plans/<job>/recall-artifact.md (reviewer resolves entries)` at line 141, but the transition from Phase 3 to Phase 4a didn't trigger re-reading the dispatch instructions.

**Classification:** Insufficient context at decision point + unanchored gate.

**Fix:** `references/review-dispatch-template.md` is referenced at inline SKILL.md line 132 but may not exist or may not enforce the recall pattern. Verify template exists, add recall artifact-path-only constraint if missing. The template is the structural anchor — freeform prompt composition allows the entrainment pattern.

**Secondary:** The pretooluse-recall-check hook's regex `plans/([^/]+)/` matches across newlines, capturing prose text between `plans/` and the next `/` anywhere in the prompt. Three blocked dispatches resulted from `plans/handoff-cli-tool rework` and `plans/*/reports/` matching before the actual plan path. Hook regex should use `\S+` (no whitespace) instead of `[^/]+`.
