# Pushback Design Outline

## Research Grounding

**Model-level baseline:** Claude 4.5 is 70-85% less sycophantic than 4.1 (Anthropic's Petri evaluation). Our intervention amplifies existing capability, not fighting the model.

**Validated prompt-level techniques (converging across multiple sources):**
- Counterfactual prompting ("What would need to be true for this to fail?") > generic risk identification
- Context/motivation for WHY behavior matters (Anthropic docs: Claude generalizes better with motivation)
- Evaluator role framing > devil's advocate (DA produces performative disagreement, evaluator produces genuine analysis)
- Confidence calibration ("State your confidence and what would change your assessment")
- Non-leading question design (frame for evaluation, not validation)

**Fundamental limitation (validates Q-2):** LLMs lack persistent world models for principled disagreement. Prompt-level sycophancy mitigation is amplification of model capability, not a cure. Success is empirical.

**Sources:**
- [Reducing LLM Sycophancy: 69% Improvement Strategies](https://sparkco.ai/blog/reducing-llm-sycophancy-69-improvement-strategies) — prompt engineering techniques, counterfactual prompting
- [Anthropic: Protecting Well-Being of Users](https://www.anthropic.com/news/protecting-well-being-of-users) — Petri evaluation, 70-85% model-level improvement, system prompt approach
- [Claude 4 Prompting Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) — context/motivation improves generalization
- [The "Yes Sir" Problem](https://danialamin.com/pages/articles/2025-06-29-yes-man.html) — root cause analysis, world model limitations
- [Structured Sycophancy Mitigation (ICLR 2025)](https://proceedings.iclr.cc/paper_files/paper/2025/file/a52b0d191b619477cc798d544f4f0e4b-Paper-Conference.pdf) — causal model disentanglement (training-level, context only)
- [10 Prompts That Force AI to Challenge Your Worst Ideas](https://www.aiprompthackers.com/p/10-prompts-that-force-ai-to-challenge) — practitioner patterns
- [Stop Letting AI Be Your Yes Man](https://windowsforum.com/threads/stop-letting-ai-be-your-yes-man-prompt-disagreement-and-show-your-work.384169/) — counterargument demand patterns

## Approach

Two-layer mechanism: ambient fragment (always-loaded behavioral rules) + enhanced hook injection (targeted reinforcement during discussion mode).

**Why two layers:** Fragment gives 100% recall (Vercel study: ambient 100% vs invoked 79%). Hook provides targeted reinforcement when discussion mode is active. Neither alone is sufficient — fragment lacks salience at decision point, hook lacks ambient presence outside `d:` mode.

**Why NOT adversary agent:** Requirements explicitly exclude handoff review agent on cost/benefit. Second-agent approaches violate NFR-2 (lightweight). Out of scope.

**Why NOT pure enforcement:** "Enforcement cannot fix judgment errors" (validated learning). Structural checks (precommit, counters) can be satisfied with wrong content. Pushback requires judgment, not compliance.

## Key Decisions

**D-1: Fragment over skill for ambient rules.**
Skills are invoked (79% trigger rate). Fragment is ambient (100%). Pushback must be available in ALL conversation modes, not just when explicitly invoked. Fragment loaded via CLAUDE.md @-reference.

**D-2: Enhance existing `d:` hook directive, don't create new hook event.**
`userpromptsubmit-shortcuts.py` already detects `d:` and injects context. Extending the injection text is zero-infrastructure cost — no new hook scripts, no new settings.json entries.

**D-5: Add long-form directive aliases.**
Rename `d:` → `discuss:` and `p:` → `pending:` (long forms). Keep short forms as aliases. Both map to same expansion. Self-documenting for new users, muscle memory preserved for existing.

**D-6: Match directives on any line, not just first line.**
Current hook uses `re.match()` (anchored to start). Change to scan all lines for directive patterns. Tier 1 commands (exact full-message match) unchanged. Exclude lines inside fenced code blocks and inline code spans.

**D-7: Code-aware directive detection (dependency).**
Fenced block detection: reuse existing markdown preprocessor code (refactoring opportunity to shared utility). Inline code span detection: depends on pending markdown parser task — not yet available. Initial implementation: fenced block awareness + line-start matching. Full inline code awareness added when parser lands.

**D-3: Self-monitoring for agreement momentum over external state tracking.**
Hook is stateless (no cross-invocation memory). Adding state files adds complexity and failure modes. Fragment rule instructs agent to self-monitor agreement runs. If this proves unreliable empirically, external state is a future escalation.

**D-4: Model selection guidance as fragment rule, not hook-injected.**
FR-3 (model selection) applies when creating pending tasks, not specifically in discussion mode. Fragment rule is always available. The `p:` directive hook could be enhanced later if needed.

## Artifacts

- **New fragment:** `agent-core/fragments/pushback.md` — behavioral rules with motivation (WHY sycophancy is harmful), counterfactual evaluation structure, confidence calibration, agreement momentum self-monitoring, model selection evaluation
- **Modified hook:** `agent-core/hooks/userpromptsubmit-shortcuts.py` — enhanced `d:`/`discuss:` directive expansion with evaluation structure, long-form aliases, any-line matching, fenced code block exclusion
- **Modified CLAUDE.md:** Add `@agent-core/fragments/pushback.md` reference
- **Modified symlink:** `just sync-to-parent` after hook changes (hook lives in agent-core, symlinked to .claude/hooks)

## Design Principles (from requirements)

- **NFR-1 (genuine, not reflexive):** Rules emphasize articulating costs/risks/alternatives AND articulating why good ideas are good. Not devil's advocate theater. (→ FR-1, NFR-1)
- **NFR-2 (lightweight):** Fragment already loaded (zero per-turn cost). Hook enhancement is string modification (no latency change). (→ NFR-2)
- **FR-1 (structural pushback):** Hook injects counterfactual evaluation structure: "What assumptions does this make? What would need to be true for this to fail? What alternatives exist?" — research-validated framing over generic "identify risks." (→ FR-1)
- **FR-2 (agreement momentum):** Fragment rule: self-monitor for consecutive agreements, flag explicitly when detected. (→ FR-2)
- **FR-3 (model selection):** Fragment rule: evaluate cognitive requirements when creating pending tasks. (→ FR-3)

## Open Questions

- **Q-1 (Where does pushback live?):** RESOLVED — Fragment (ambient rules) + hook (targeted reinforcement in `d:` mode). See Approach and Key Decisions D-1/D-2.
- **Q-2 (Can LLM self-correct sycophancy?):** This design is the lightest viable intervention. Success is empirical — test and observe. Fragment + hook is low-cost enough that failure leads to "try harder" (structural approaches) without wasted investment.
- **Q-3 (Agreement momentum detection):** Self-monitoring first. The rule makes the concern salient, which is the mechanism by which fragments work (ambient awareness).
- **Q-4 (Genuine vs sycophantic agreement):** The rule "articulate WHY specifically" forces evaluation depth. Sycophantic agreement is characteristically vague.

## Phase Structure

- **Phase 1 (general):** Create pushback fragment with behavioral rules
- **Phase 2 (general):** Enhance hook `d:` directive expansion
- **Phase 3 (general):** Wire fragment into CLAUDE.md, sync symlinks
- **Phase 4 (general):** Manual validation — test `d:` discussions for pushback behavior with scenarios: (1) propose good idea, verify agent articulates WHY it's good specifically; (2) propose flawed idea, verify agent identifies costs/risks/alternatives before agreeing; (3) agree to 3+ consecutive proposals in `d:` mode, verify agent flags agreement momentum; (4) create pending task requiring opus-level reasoning, verify agent evaluates model tier against cognitive requirements

## Scope Boundaries

**In scope:**
- Pushback behavioral rules (fragment)
- Hook enhancement for discussion mode (evaluation structure, any-line matching, fenced code exclusion)
- Long-form directive aliases (`discuss:`, `pending:`)
- Agreement momentum self-monitoring
- Model selection guidance

**Out of scope:**
- Adversary agent / second-opinion pattern
- External state tracking for agreement momentum
- Precommit enforcement of model selection
- Mechanical validation of judgment quality
- Inline code span detection (depends on pending markdown parser task)

**Dependencies:**
- Fenced block detection: existing markdown preprocessor code (refactoring to shared utility)
- Inline code span detection: pending markdown parser task (deferred — added when parser lands)
