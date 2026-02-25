# Skill Inventory: Prose Quality Audit

**Date:** 2026-02-25
**Skills audited:** 30
**Locations:** `agent-core/skills/*/SKILL.md`

---

## Summary

30 skills inventoried. Quality ranges from A+ (brief, commit, how, when, recall) to C (review, orchestrate, shelve, token-efficient-bash). The dominant failure modes are: (1) `description` frontmatter using "This skill should be used when..." phrasing (18/30 skills), (2) explicit "When to Use" preamble sections that frontload framing before procedures, (3) second-person hedging ("you can", "you need to"), and (4) inflated body length with unnecessary narrative scaffolding. The best skills are thin, imperative, and tool-anchored; the worst read like instructional prose written for a human learner rather than an LLM protocol.

---

## Per-Skill Entries

### brief
**Path:** `/Users/david/code/claudeutils/agent-core/skills/brief/SKILL.md`
**Word count (body):** ~120
**Grade:** A+

**Description frontmatter:** Clean. Third person but factual: `"Transfer context (scope changes, decisions, conclusions) to a worktree task via plans/<plan>/brief.md."` — no "This skill should be used when" phrasing.

**Writing style:** Imperative throughout. "Resolve argument...", "Compose brief...", "Append timestamped H2 entry..."

**Prose quality:** No hedging, no preamble. Steps numbered and dense. Consumer section is pure fact.

**Progressive disclosure:** No references/ subdirectory — body is short enough that this is fine.

**Issues:** None significant.

---

### error-handling
**Path:** `/Users/david/code/claudeutils/agent-core/skills/error-handling/SKILL.md`
**Word count (body):** ~65
**Grade:** B+

**Description frontmatter:** `"This skill should be used when agents execute bash commands and need error handling rules."` — uses "should be used when" anti-pattern.

**Writing style:** Imperative. Bullet list of rules.

**Prose quality:** No hedging in the body. Clean.

**Progressive disclosure:** N/A — body is tiny.

**Issues:**
- Description uses "This skill should be used when..." — fix to factual noun phrase. Example: `"Error handling rules for bash-executing agents. Prevents silent failures and inappropriate error suppression."`

---

### gitmoji
**Path:** `/Users/david/code/claudeutils/agent-core/skills/gitmoji/SKILL.md`
**Word count (body):** ~350
**Grade:** B

**Description frontmatter:** `"This skill should be used when the user asks to 'use gitmoji'..."` — uses anti-pattern.

**Writing style:** Mix. Numbered sections use imperative headers ("Read Gitmoji Index", "Analyze Commit Message"). But "When to Use" section is framing overhead: `"Use when: User requests gitmoji • Integrated into /commit skill..."` — this belongs in the description, not the body.

**Prose quality:**
- "When to Use" section is pure preamble — already in description frontmatter.
- "Integration" section contains second-person-adjacent content: `"Methods: CLAUDE.md: Always-use instruction"` — marginal.
- "Critical Rules" Do/Don't table is clean.
- "Limitations" section at bottom: `"Internet for initial download • Manual updates • jq dependency..."` — dependency list presented as limitations framing.

**Progressive disclosure:** No references/ subdirectory. Index maintenance and integration sections could be extracted, reducing body to ~150 words.

**Issues:**
- Description anti-pattern.
- "When to Use" section is redundant with description — remove or fold into description.
- Word count inflated by narrative scaffolding (Resources, Limitations sections).

---

### token-efficient-bash
**Path:** `/Users/david/code/claudeutils/agent-core/skills/token-efficient-bash/SKILL.md`
**Word count (body):** ~900
**Grade:** C

**Description frontmatter:** `"This skill should be used when writing multi-step bash scripts (3+ sequential commands) to minimize script token cost..."` — uses anti-pattern.

**Writing style:** Mix of imperative and explanatory prose. Heavy tutorial register throughout.

**Prose quality — specific examples:**
- `"Write bash scripts that provide automatic progress diagnostics and fail-fast error handling without manual echo statements or verbose error reporting."` — opening sentence is framing over substance.
- `"**Problem:** Traditional bash scripts require extensive manual instrumentation"` — narrative framing.
- `"**Solution:** Token-efficient pattern (automatic tracing)"` — more framing.
- `"## Token Economy Benefits"` section (40 lines) is a teaching section explaining WHY, not a procedure. Should be in references/, not SKILL.md.
- `"## How It Works"` section (50+ lines) explains each flag in detail — reference material, not protocol.
- `"## Summary"` section at end restates the pattern already given at the top — pure redundancy.
- Multiple `Benefits:` sub-lists after each code example explain what is already visible from the code.

**Progressive disclosure:** No references/ subdirectory. "How It Works", "Token Economy Benefits", "Examples" (3 full examples with output and benefits commentary), and "Summary" sections should move to references/. Core SKILL.md should be the pattern + caveats only (~100 words).

**Issues:**
- Severe: 900-word body is ~6x the appropriate length for a pattern this simple.
- Description anti-pattern.
- Tutorial register throughout — written for a human learner, not an agent protocol.
- Summary section at end restates what's at the top.
- Three worked examples with annotated output and "Benefits" lists are reference material.

---

### handoff-haiku
**Path:** `/Users/david/code/claudeutils/agent-core/skills/handoff-haiku/SKILL.md`
**Word count (body):** ~420
**Grade:** B

**Description frontmatter:** Clean. Factual: `"Internal skill for Haiku model orchestrators only. Not for Sonnet or Opus — use /handoff instead. Mechanical session context preservation without learnings judgment."`

**Writing style:** Mix. Step headers are imperative. Body has some explanatory prose.

**Prose quality:**
- `"When invoked, update session.md mechanically:"` — clean framing.
- `"## Key Differences from Full Handoff"` section is mostly clean.
- `"## Principles"` section: `"Don't filter or judge importance"`, `"Trust the next agent"` — behavioral directives, not hedging.

**Progressive disclosure:** Body is appropriately sized.

**Issues:**
- Minor: Inline template content (section titles like `## Completed This Session`) embedded in the skill body is not formatted as a code block, making it harder to parse.

---

### next
**Path:** `/Users/david/code/claudeutils/agent-core/skills/next/SKILL.md`
**Word count (body):** ~270
**Grade:** B

**Description frontmatter:** `"This skill should be used when the user asks 'what's next?'..."` — uses anti-pattern.

**Writing style:** Mix. Steps are imperative ("List and read files...", "Read `agents/todo.md`"). But opening preamble and response-format sections add framing.

**Prose quality:**
- `"## When to Use"` section restates the description content: `"1. User asks: 'what's next?'... 2. Check already-loaded context... 3. If work found in context: Report it directly, DO NOT load this skill"` — this pre-execution check belongs in description or a note, not a full section.
- `"## How It Works"` header before the steps — unnecessary framing.
- `"## Response Format"` section provides an example response which is useful, but the header "Response Format" is generic framing.
- `"If actual pending work found: Report it and STOP."` repeated three times verbatim across steps — appropriate as protocol.

**Progressive disclosure:** Body size appropriate.

**Issues:**
- Description anti-pattern.
- "When to Use" section is largely redundant with description.
- "How It Works" header is framing before procedure.

---

### opus-design-question
**Path:** `/Users/david/code/claudeutils/agent-core/skills/opus-design-question/SKILL.md`
**Word count (body):** ~280
**Grade:** A-

**Description frontmatter:** Clean. `"REQUIRED instead of AskUserQuestion for design/architectural decisions."` — direct.

**Writing style:** Numbered steps, imperative. "Recognize when...", "Prepare the decision context", "Use Task tool...", "Read the recommendation".

**Prose quality:**
- Step 1 intro: `"Recognize when you're about to use AskUserQuestion for a design/architectural choice"` — second person "you're" but imperative in effect.
- `"When Opus returns: Read the recommendation / Apply the guidance immediately / No need to confirm with user"` — clean.
- The example section with `AskUserQuestion` contrast is genuinely useful demonstration.

**Progressive disclosure:** Body size appropriate.

**Issues:**
- Minor: Step 2 uses second person: `"Prepare the decision context: 1. Current situation: What are you implementing?"` — "you" could be removed: "Current situation: Implementation context."

---

### release-prep
**Path:** `/Users/david/code/claudeutils/agent-core/skills/release-prep/SKILL.md`
**Word count (body):** ~600
**Grade:** A-

**Description frontmatter:** Clean, factual.

**Writing style:** Numbered steps with imperative verbs. Tool calls anchored in each step. Good D+B structure.

**Prose quality:**
- `"## When to Use"` section (3 bullets): `"Before releasing a package to PyPI, npm, crates.io, etc."` — minor framing section, but brief.
- `"## Post-Report Behavior"` section: `"After displaying the readiness report: If any checks FAILED: stop and wait for user to fix issues..."` — clean imperative protocol.
- `"## Critical Constraints"` section: `"Do NOT run the release command."` — clean.
- Example interaction at end is useful worked example.

**Progressive disclosure:** References section points to references/ subdirectory. Good.

**Issues:**
- "When to Use" section could fold into description.
- Body length (600 words) is on the high end but justified given operational complexity.

---

### shelve
**Path:** `/Users/david/code/claudeutils/agent-core/skills/shelve/SKILL.md`
**Word count (body):** ~340
**Grade:** B-

**Description frontmatter:** Clean: `"Archive session context to todo list and reset for new work."`

**Writing style:** Mix. Steps have imperative headers but bodies are second-person.

**Prose quality — specific problems:**
- `"## When to Use"` section: `"**Use this skill when:** Switching to unrelated work... / Completing a project phase..."` — unnecessary preamble.
- `"**Ask user for approval before running.**"` — second person imperative, appropriate.
- `"### 1. Gather Input"` → `"Ask user for: **Name/topic**: Natural language description"` — second-person: "Ask user for" could be "Prompt for".
- `"## Example Interaction"` section is pure narrative framing. The example shows the agent saying `"I'll help you shelve the current session context."` — models first-person conversational framing which is exactly the register the project is moving away from.

**Progressive disclosure:** Body size appropriate.

**Issues:**
- "When to Use" section is framing.
- Example interaction models conversational framing ("I'll help you...") — counterproductive.

---

### worktree
**Path:** `/Users/david/code/claudeutils/agent-core/skills/worktree/SKILL.md`
**Word count (body):** ~720
**Grade:** A-

**Description frontmatter:** `"This skill should be used when the user asks to 'create a worktree'..."` — uses anti-pattern.

**Writing style:** Numbered steps, mostly imperative. Operational modes clearly delineated.

**Prose quality:**
- Mode A, B, C are well-structured.
- `"## Usage Notes"` section is clean operational facts.
- `"Emergency '--force' flag: ... Use only as emergency escape hatch when normal workflow is blocked."` — clear.

**Progressive disclosure:** `references/branch-mode.md` referenced for edge case. Good.

**Issues:**
- Description anti-pattern.
- Mode B step 1 calls `"list_plans(Path('plans'))"` — should use CLI: `claudeutils _worktree ls` (per project-tooling rule against ad-hoc Python). This is a **correctness issue**, not just prose.

---

### commit
**Path:** `/Users/david/code/claudeutils/agent-core/skills/commit/SKILL.md`
**Word count (body):** ~390
**Grade:** A+

**Description frontmatter:** Clean, factual. No anti-pattern.

**Writing style:** Dense, imperative throughout. Flag table, step list, example — all precise.

**Prose quality:**
- `"Only commit when explicitly requested."` — direct.
- Gate language: `"Trivial? (≤5 net lines, ≤2 files, additive, no behavioral change) Self-review via git diff HEAD."` — precise criteria.
- `"Gate: precommit fails → STOP."` — direct.

**Progressive disclosure:** References gitmoji-index.txt inline. Body size appropriate.

**Issues:** None significant. Model skill for brevity and density.

---

### doc-writing
**Path:** `/Users/david/code/claudeutils/agent-core/skills/doc-writing/SKILL.md`
**Word count (body):** ~660
**Grade:** B+

**Description frontmatter:** `"This skill should be used when the user asks to 'write a README'..."` — anti-pattern.

**Writing style:** Mix. Steps are imperative but structural principles sections use framing headers.

**Prose quality — specific problems:**
- `"## When to Use"` section (7 lines) — framing overhead.
- `"**Not for:** API reference docs..."` — useful counter-condition, should stay.
- `"### 2. Write"` section: `"Draft the document applying these structural principles:"` — framing before the principles.
- `"**Motivation-first opener.** Lead with the problem the project solves, not a feature list. Reader testing consistently shows feature-list openers leave readers unable to articulate why the project exists."` — the rationale clause ("Reader testing consistently shows...") is narrative framing. The rule stands alone without it.

**Progressive disclosure:** No references/ subdirectory. The worked example in `## Example` (60 lines) could move to references/.

**Issues:**
- Description anti-pattern.
- "When to Use" section is overhead.
- Several rationale clauses in "Write" principles could be trimmed or moved to references/.

---

### plugin-dev-validation
**Path:** `/Users/david/code/claudeutils/agent-core/skills/plugin-dev-validation/SKILL.md`
**Word count (body):** ~1400
**Grade:** B-

**Description frontmatter:** Clean: `"Domain validation criteria for plugin components. Consumed by corrector during artifact review."` — factual.

**Writing style:** Mix. Review criteria sections are structured tables and imperative bullets. But framing sections are heavy.

**Prose quality — specific problems:**
- `"**Rationale:**"` sub-bullets throughout every criterion: `"Rationale: Frontmatter enables skill discovery and invocation"`, `"Rationale: Direct commands reduce ambiguity"` — explanatory noise. The criterion is the rule; the rationale should be in a reference file or omitted if self-evident.
- `"**What 'correct' means for each artifact type:**"` — framing before the list.
- `"## Usage Notes"` section: `"**For planners:** Reference this skill..."`, `"**For corrector:** Read this skill when task prompt references it..."`, `"**For users:** This skill is NOT user-invocable..."` — second-person, framing-heavy.

**Progressive disclosure:** Good/Bad Examples for each artifact type, Verification Procedures, and Fix Procedures should move to references/. This skill is ~3x appropriate size.

**Issues:**
- Rationale sub-bullets throughout — redundant if criteria are self-explanatory.
- "Usage Notes" section is second-person framing.
- Word count ~3x appropriate size — significant content should move to references/.

---

### project-conventions
**Path:** `/Users/david/code/claudeutils/agent-core/skills/project-conventions/SKILL.md`
**Word count (body):** ~100
**Grade:** A+

**Description frontmatter:** Clean: `"Project prose and output conventions for sub-agents. Injected via skills: frontmatter — not user-invocable. Bundles deslop (prose quality), token economy, and tmp-directory rules."`

**Writing style:** Bullet lists under section headers. Imperative where applicable.

**Prose quality:** Dense, no hedging, no framing. Opening note is clean.

**Progressive disclosure:** N/A — body is intentionally minimal.

**Issues:** None.

---

### requirements
**Path:** `/Users/david/code/claudeutils/agent-core/skills/requirements/SKILL.md`
**Word count (body):** ~850
**Grade:** A-

**Description frontmatter:** Clean, factual. No anti-pattern.

**Writing style:** Numbered procedures with imperative steps. Well-structured.

**Prose quality:**
- `"Dual-mode requirements capture: extract from conversation or elicit through semi-structured questions."` — clean opener.
- `"**Opus required.** Extract mode requires synthesizing nuanced conversation context; sonnet misses implicit requirements."` — direct constraint.
- `"**Critical rule:** Extract from what was said, do NOT infer unstated requirements. Hallucination risk..."` — good.
- `"## Key Principles"` table: Rationale column in table is fine (structured reference).

**Progressive disclosure:** References `references/empirical-grounding.md`. Good.

**Issues:**
- Body length (850 words) is high but justified by genuine complexity (two modes, format spec, skill dependency scanning).
- `"## Integration Notes"` section at end contains meta-commentary: `"No changes to /design or /runbook needed"` — stale coordination note, should be removed.

---

### memory-index
**Path:** `/Users/david/code/claudeutils/agent-core/skills/memory-index/SKILL.md`
**Word count (body):** ~550 (mostly index content)
**Grade:** A

**Description frontmatter:** `"This skill should be used when sub-agents need memory recall capabilities."` — uses anti-pattern.

**Writing style:** Index body is pure data (triggers and file paths). Protocol section is imperative.

**Prose quality:** The skill is mostly an index — prose quality barely applies. Protocol section is clean.

**Progressive disclosure:** N/A — the index IS the body.

**Issues:**
- Description anti-pattern.

---

### review
**Path:** `/Users/david/code/claudeutils/agent-core/skills/review/SKILL.md`
**Word count (body):** ~1100
**Grade:** C

**Description frontmatter:** Clean: `"Review in-progress changes for quality and correctness"` — factual.

**Writing style:** Heavy second-person and preamble throughout.

**Prose quality — specific problems:**
- `"## When to Use"` section (12 lines): `"**Use this skill when:** Ready to review changes before committing / Want to check recent commits for issues..."` — pure framing.
- `"**Distinction:** This skill reviews work-in-progress. The built-in /review is for PR-focused reviews."` — meta-commentary.
- `"**Ask user what to review:**"` — second person.
- `"**Be constructive, not critical"` in Tone section — hedging language.
- `"**Acknowledge good practices"` — instructional hedging.
- `"## Common Scenarios"` section (60+ lines) — all narrative framing and examples.
- `"## Integration with General Workflow"` section — meta-commentary.
- `"## Example Execution"` — 60-line worked example with role-play agent monologue.

**Progressive disclosure:** No references/ subdirectory. 60% of body could move to references/.

**Issues:**
- Severe: "Common Scenarios", "Example Execution", and "When to Use" sections are pure narrative overhead.
- Second-person framing throughout.
- "Be constructive, not critical" is hedging.
- Word count ~2.5x appropriate size.

---

### codify
**Path:** `/Users/david/code/claudeutils/agent-core/skills/codify/SKILL.md`
**Word count (body):** ~650
**Grade:** A-

**Description frontmatter:** `"This skill should be used when the user asks to 'remember this'..."` — uses anti-pattern.

**Writing style:** Steps are numbered, mostly imperative. Good structure.

**Prose quality:**
- `"## When to Use"` section: `"**Use when:** Workflow improvement discovered..."` — framing. Brief (5 bullets), but still preamble.
- `"**Skip when:** Trivial update..."` — useful counter-condition.
- `"**Prerequisite:** Execute in a clean session (fresh start)."` — clean constraint.
- `"## Common Patterns"` and `"## Additional Resources"` sections point to references/ — good progressive disclosure.

**Progressive disclosure:** Good — heavy content deferred to references/.

**Issues:**
- Description anti-pattern.
- "When to Use" section (10 lines) is preamble — could fold into description.

---

### ground
**Path:** `/Users/david/code/claudeutils/agent-core/skills/ground/SKILL.md`
**Word count (body):** ~500
**Grade:** A

**Description frontmatter:** `"This skill should be used when producing output that contains methodological claims..."` — uses anti-pattern.

**Writing style:** Numbered phases with imperative verbs. Dense.

**Prose quality:**
- `"**Core principle:** Internal reasoning alone confabulates plausible structures. External research alone produces generic frameworks."` — rationale statement. Compact, acceptable here.
- `"**Framing rule — general first:**"` with ❌/✅ examples — clean.
- `"## Integration Points"` section: `"**Not needed for:** Applying an already-grounded framework..."` — useful counter-condition.

**Progressive disclosure:** References `references/grounding-criteria.md`. Good.

**Issues:**
- Description anti-pattern.
- Opening rationale paragraph could move to references/ but is compact enough to justify.

---

### how
**Path:** `/Users/david/code/claudeutils/agent-core/skills/how/SKILL.md`
**Word count (body):** ~130
**Grade:** A+

**Description frontmatter:** `"This skill should be used when the agent needs to recall procedural knowledge..."` — uses anti-pattern.

**Writing style:** Pure imperative. Three resolution modes, each with a bash command. When to Use / When NOT to Use are terse.

**Prose quality:** Minimal, no hedging, no narrative. Output Format section is factual.

**Progressive disclosure:** N/A — body is intentionally small.

**Issues:**
- Description anti-pattern only (body is exemplary).

---

### when
**Path:** `/Users/david/code/claudeutils/agent-core/skills/when/SKILL.md`
**Word count (body):** ~130
**Grade:** A+

**Description frontmatter:** `"This skill should be used when the agent needs to recall behavioral knowledge..."` — uses anti-pattern.

**Writing style:** Identical structure to `how`. Pure imperative, terse, tool-anchored.

**Prose quality:** Exemplary — minimal, no filler.

**Progressive disclosure:** N/A.

**Issues:**
- Description anti-pattern only (body is exemplary).

---

### recall
**Path:** `/Users/david/code/claudeutils/agent-core/skills/recall/SKILL.md`
**Word count (body):** ~500
**Grade:** A

**Description frontmatter:** `"This skill should be used when the user asks to 'recall'..."` — anti-pattern.

**Writing style:** Numbered passes with imperative steps. Mode definitions are dense and precise.

**Prose quality:**
- `"## Why This Exists"` section: `"Agents self-retrieve at ~3% rate. The pipeline injects recall at fixed points, but interactive sessions bypass it."` — rationale, not hedging. Acceptable here.
- Pass 1-3 descriptions are clean imperative.
- Mode definitions (`/recall deep`, `/recall broad`, etc.) are precise.
- `"## Relationship to /when and /how"` table — useful, clean.

**Progressive disclosure:** N/A — body size appropriate to complexity.

**Issues:**
- Description anti-pattern.
- "Why This Exists" section is design rationale — could move to references/ but is compact.

---

### prioritize
**Path:** `/Users/david/code/claudeutils/agent-core/skills/prioritize/SKILL.md`
**Word count (body):** ~400
**Grade:** A

**Description frontmatter:** `"This skill should be used when the user asks to 'prioritize tasks'..."` — anti-pattern.

**Writing style:** Numbered steps, imperative. Formula at top is clear.

**Prose quality:**
- `"**Evidence-based scoring:** Use observable evidence, not intuition..."` — clean constraint.
- `"## Tiebreaking"` section: clean ordered rules.
- `"## When to Re-Score"` section: `"Re-run prioritization when:"` — clean conditional.

**Progressive disclosure:** References `references/scoring-tables.md`. Good.

**Issues:**
- Description anti-pattern.
- `"## Additional Resources"` at end is framing for one bullet.

---

### handoff
**Path:** `/Users/david/code/claudeutils/agent-core/skills/handoff/SKILL.md`
**Word count (body):** ~560
**Grade:** A-

**Description frontmatter:** `"This skill should be used when the user asks to 'handoff'..."` — anti-pattern.

**Writing style:** Numbered steps, mostly imperative. Dense.

**Prose quality:**
- `"**NEVER reference commits as pending** in session.md"` — strong, appropriate.
- `"### 3. Context Preservation"` section: `"**Preserve:** commit hashes, file paths..."` / `"**Omit:** execution logs..."` — clean.
- `"## Principles"` section: `"**session.md = working memory.**"` — clean.

**Progressive disclosure:** References `examples/good-handoff.md` and `references/learnings.md`. Good.

**Issues:**
- Description anti-pattern.

---

### deliverable-review
**Path:** `/Users/david/code/claudeutils/agent-core/skills/deliverable-review/SKILL.md`
**Word count (body):** ~600
**Grade:** A-

**Description frontmatter:** `"This skill should be used when the user asks to 'review deliverables'..."` — anti-pattern.

**Writing style:** Numbered phases, imperative. Phase structure clear.

**Prose quality:**
- `"## When to Use"` section (5 lines) — framing, brief.
- Phase descriptions are imperative.
- `"**Why interactive is mandatory:** Delegated agents lack cross-project context..."` — rationale clause, appropriate for a constraint this non-obvious.
- `"Report severity counts only. No merge-readiness language — user reads severity counts, user decides."` — direct.

**Progressive disclosure:** References decision file and example report. Good.

**Issues:**
- Description anti-pattern.
- "When to Use" section is 5-line framing — fold into description.

---

### orchestrate
**Path:** `/Users/david/code/claudeutils/agent-core/skills/orchestrate/SKILL.md`
**Word count (body):** ~1500
**Grade:** C

**Description frontmatter:** Clean: `"Execute prepared runbooks with weak orchestrator pattern"` — factual.

**Writing style:** Numbered steps, imperative — but body is massively bloated with narrative sections.

**Prose quality — specific problems:**
- `"## When to Use"` section (10 lines): `"**Use this skill when:**", "**Do NOT use when:**"` — pure framing.
- `"## Weak Orchestrator Pattern"` section (50+ lines): narrative explanation of the pattern principle: `"**Delegate, don't decide:** Orchestrator does NOT make judgment calls"`, `"**Trust agents:** If agent reports success, trust it"` — this is teaching prose, not protocol. Should be in references/ or removed.
- `"## Example Execution"` section (80+ lines): a full worked example with role-play agent monologue (agent says "Verifying artifacts...", "Reading orchestrator plan...", "Escalating to sonnet...") — narrative framing that models conversational register.
- `"## Handling Common Scenarios"` section (60+ lines): 5 scenarios each with action + reason — reference material.
- `"## References"` section contains absolute paths `/Users/david/code/claudeutils/...` — debugging artifacts in a shared skill.

**Progressive disclosure:** No systematic references/ subdirectory used. ~600 words of reference material in body.

**Issues:**
- Severe: "When to Use", "Weak Orchestrator Pattern", "Example Execution", and "Handling Common Scenarios" sections (~600 words) are narrative overhead.
- "Example Execution" models conversational agent framing which is against project style.
- Body ~3x appropriate length.
- References section has hardcoded absolute paths.

---

### reflect
**Path:** `/Users/david/code/claudeutils/agent-core/skills/reflect/SKILL.md`
**Word count (body):** ~1100
**Grade:** B-

**Description frontmatter:** `"This skill should be used when the user asks to 'reflect'..."` — anti-pattern.

**Writing style:** Numbered phases, mostly imperative. Phase 1 framing block is designed.

**Prose quality — specific problems:**
- `"## When to Use"` section (10 lines) — framing.
- `"**Model expectation:** Designed for opus model. User switches to opus before invoking."` — second person "User switches" should be imperative: "Switch to opus before invoking."
- `"## Key Design Decisions"` section (100+ lines): `"### Session-Local Diagnosis"`, `"### Opus Expected, Not Enforced"`, `"### Framing Block is Mandatory"` etc. — pure design rationale. Should move to references/.

**Progressive disclosure:** References `references/patterns.md` and `references/rca-template.md`. Good. But "Key Design Decisions" section in body should also move to references/.

**Issues:**
- Description anti-pattern.
- "When to Use" framing section.
- "Key Design Decisions" section (~150 words of design rationale) inflates body — move to references/.
- Second person in model expectation.

---

### review-plan
**Path:** `/Users/david/code/claudeutils/agent-core/skills/review-plan/SKILL.md`
**Word count (body):** ~1600
**Grade:** B+

**Description frontmatter:** Multi-line, factual. No anti-pattern. Clean.

**Writing style:** Numbered sections with imperative rules. Structured criteria with Grep patterns. Dense.

**Prose quality:**
- `"## Purpose"` section: clean — `"Review agent behavior: Write review (audit trail) → Fix ALL issues → Escalate unfixable"`.
- Review criteria sections use **Violation:** / **Correct approach:** / **Check:** framing — appropriate for a validation skill.
- `"*Grounding: LLMs produce 'syntactically correct but irrelevant' code at 13.6–31.7% rate...*"` — cited evidence, not hedging.
- `"## Key Principles"` section (10 numbered rules) — clean.
- `"## Sources"` section with links — appropriate.

**Progressive disclosure:** Body is long (~1600 words) but this is a validation criteria reference, not a procedure. Much of the content is necessarily detailed criteria.

**Issues:**
- Body length is on the high end but justified by the validation criteria role.
- `"**Why this is wrong:**"` framing in violation sections is slightly redundant — the correct approach could stand alone without the framing header. Minor.

---

### runbook
**Path:** `/Users/david/code/claudeutils/agent-core/skills/runbook/SKILL.md`
**Word count (body):** ~2000+ (read truncated at 100 lines)
**Grade:** B

**Description frontmatter:** `"This skill should be used when the user asks to '/runbook'..."` — anti-pattern.

**Writing style:** Mix. Complex skill with multiple sections — some dense, some padded.

**Prose quality (from first 100 lines):**
- `"**Usage:** /runbook plans/<job-name>/design.md"` — clean opener.
- `"**Workflow context:** Part of implementation workflow..."` — useful context.
- Per-Phase Type Model section is dense and clear.
- `"## When to Use"` section (10 lines) — framing overhead.
- Three-Tier Assessment section is procedural and clean.

**Progressive disclosure:** Given the skill's complexity, length may be partially justified, but "When to Use" and likely several example/scenario sections could move to references/.

**Issues:**
- Description anti-pattern.
- "When to Use" section present.
- Body is very long — full assessment requires reading beyond the truncation point.

---

### design
**Path:** `/Users/david/code/claudeutils/agent-core/skills/design/SKILL.md`
**Word count (body):** ~1800
**Grade:** B+

**Description frontmatter:** `"This skill should be used when the user asks to 'design'..."` — anti-pattern.

**Writing style:** Numbered phases, mostly imperative. Phase sections have inline rationale that inflates length.

**Prose quality — specific observations:**
- `"## Downstream Consumer"` — clean two-line note.
- `"### 0. Complexity Triage"` with D+B anchor — exemplary structure.
- Classification Gate produces explicit output block — good.
- `"**Anti-pattern:** Deferring skill loading to A.1 judgment..."` / `"**Correct pattern:** Scan requirements..."` — anti-pattern/correct-pattern blocks appear throughout and are appropriate.
- `"**Rationale:** Designer has deepest understanding of what knowledge the task requires. Encoding this explicitly prevents planner from either under-reading..."` — rationale clause in body. Appropriate for design clarity but inflates length.

**Progressive disclosure:** References `references/grounding-criteria.md` and other files. Good use of progressive disclosure.

**Issues:**
- Description anti-pattern.
- Body length (~1800 words) is high. Rationale clauses throughout add ~200 words that could move to references/ or be trimmed.
- `"## Constraints"` section at end is only 3 bullets — could fold inline.

---

## Patterns Across All Skills

### Anti-Pattern 1: Description Frontmatter (18/30 skills)

The most pervasive problem. 18 of 30 skills use `"This skill should be used when..."` in their description field. This phrasing is verbose, passive, and redundant with triggers already encoded in the body.

**Skills using the anti-pattern:**
error-handling, gitmoji, token-efficient-bash, next, when, how, recall, ground, codify, handoff, prioritize, worktree, doc-writing, deliverable-review, memory-index, reflect, runbook, design

**Fix:** Replace with factual noun phrase describing the skill's purpose and triggers. Example:
- Current: `"This skill should be used when the user asks to '/runbook'..."`
- Better: `"Create execution runbooks from design documents. Triggered by /runbook, 'create a runbook', 'plan the implementation'."`

### Anti-Pattern 2: "When to Use" Preamble Sections (15/30 skills)

Approximately half the skills have a `## When to Use` section at the top that restates what's already in the description. Counter-conditions ("Do NOT use when...") are useful; positive conditions are redundant.

**Skills with this section:** gitmoji, release-prep, shelve, worktree, orchestrate, review, codify, reflect, runbook, design, deliverable-review, next, doc-writing, handoff-haiku, handoff

**Fix:** Remove positive "Use when" bullets. Keep only counter-conditions. If counter-conditions are important, fold into description frontmatter.

### Anti-Pattern 3: Rationale Clauses Inline (common in medium/large skills)

Many skills embed `"**Rationale:**"` or `"**Why this is correct:**"` sub-bullets alongside every criterion. This inflates length and slows down an LLM reading the protocol. Rationale belongs in references/ or design decisions docs, not inline.

**Most affected:** plugin-dev-validation, review-plan, orchestrate, reflect

### Anti-Pattern 4: Example/Scenario Sections in Body (review, orchestrate, shelve, gitmoji)

These sections model conversational or narrative interaction patterns. `review` has a 60-line worked example where the agent says `"Reviewing uncommitted changes..."`. `orchestrate` has 80 lines of role-play monologue. `shelve` models `"I'll help you shelve the current session context."` These sections:
- Inflate body length significantly
- Model conversational register the project is moving away from ("I'll help you...")
- Should move to references/examples/

### Anti-Pattern 5: Second-Person Language

Lower frequency than the other patterns but present in several skills. Examples:
- `"User switches to opus before invoking."` (reflect) → `"Switch to opus before invoking."`
- `"Ask user for:"` (shelve) → `"Prompt for:"`
- `"Recognize when you're about to use AskUserQuestion..."` (opus-design-question) — borderline acceptable as a pattern-recognition cue

---

## Grade Summary

| Skill | Grade | Body Words | Primary Issues |
|-------|-------|-----------|----------------|
| brief | A+ | ~120 | None |
| commit | A+ | ~390 | None |
| how | A+ | ~130 | Description anti-pattern only |
| when | A+ | ~130 | Description anti-pattern only |
| project-conventions | A+ | ~100 | None |
| recall | A | ~500 | Description anti-pattern, minor rationale |
| ground | A | ~500 | Description anti-pattern |
| memory-index | A | ~550 | Description anti-pattern |
| prioritize | A | ~400 | Description anti-pattern |
| opus-design-question | A- | ~280 | Minor second-person |
| release-prep | A- | ~600 | Minor "When to Use" |
| requirements | A- | ~850 | Description anti-pattern, stale note |
| handoff | A- | ~560 | Description anti-pattern |
| deliverable-review | A- | ~600 | Description anti-pattern, "When to Use" |
| worktree | A- | ~720 | Description anti-pattern, correctness issue |
| codify | A- | ~650 | Description anti-pattern, "When to Use" |
| design | B+ | ~1800 | Description anti-pattern, rationale inflation |
| review-plan | B+ | ~1600 | Minor framing, length justified |
| doc-writing | B+ | ~660 | Description anti-pattern, "When to Use" |
| error-handling | B+ | ~65 | Description anti-pattern |
| handoff-haiku | B | ~420 | Minor structural issue |
| next | B | ~270 | Description anti-pattern, "When to Use" |
| gitmoji | B | ~350 | Description anti-pattern, "When to Use", padded |
| runbook | B | ~2000+ | Description anti-pattern, "When to Use", long |
| reflect | B- | ~1100 | Description anti-pattern, design rationale in body |
| shelve | B- | ~340 | "When to Use", models conversational register |
| plugin-dev-validation | B- | ~1400 | Rationale inflation, "Usage Notes" framing |
| review | C | ~1100 | Second-person, "Common Scenarios", example monologue |
| orchestrate | C | ~1500 | Teaching prose, example monologue, hardcoded paths |
| token-efficient-bash | C | ~900 | Tutorial register throughout, Summary redundancy |

---

## Priority Fix List

**High impact, low effort (description field only):**
All 18 skills with "This skill should be used when..." description — mechanical find-and-replace with factual noun phrases.

**Medium impact (body surgery needed):**
1. `token-efficient-bash` — extract "How It Works", "Token Economy Benefits", examples, Summary to references/
2. `orchestrate` — extract "Weak Orchestrator Pattern", "Example Execution", "Handling Common Scenarios" to references/; fix hardcoded absolute paths in References section
3. `review` — extract "Common Scenarios", "Example Execution", trim "When to Use", remove "Be constructive" hedging
4. `plugin-dev-validation` — extract Rationale sub-bullets, "Verification Procedures", "Fix Procedures", "Good/Bad Examples" to references/
5. `reflect` — extract "Key Design Decisions" to references/, remove "When to Use"
6. `shelve` — replace "Example Interaction" with terse note, remove "When to Use"

**Low priority (minor cleanup):**
- Remove "When to Use" preamble sections from: gitmoji, next, doc-writing, deliverable-review, handoff
- Remove stale "Integration Notes" from requirements
- Fix `list_plans()` reference in worktree Mode B (correctness issue — use `claudeutils _worktree ls`)
