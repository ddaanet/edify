# Blog Series Structure

## Series Title: "Agentic Programming: What Six Months of Trial and Error Actually Taught Me"

## Ordering Rationale

The claude.ai conversation proposed: Remember → Ground → Handoff → Deliverable Review → Pipeline. The user wanted a didactic arc where each concept builds on the previous. Pushback mentioned as potential standalone.

**Challenge to the proposed ordering:**

1. **Remember is foundational but not a strong opener.** "You can write rules in CLAUDE.md" is well-known to the target audience. The concept matters (behavior is programmable), but it doesn't hook readers.

2. **One-article-per-skill fragments the meta-pattern.** The cross-topic analysis shows all five topics hit the same wall: LLMs optimize for linguistic consistency, not correctness. Prose instructions get rationalized past. Structural enforcement is the common fix. Skill-per-article obscures this.

3. **The strongest content is the failures, not the solutions.** 385 tests pass with 8 visual bugs. 0% spontaneous recall. Confabulated scoring. Disagree-first producing contrarianism. These are visceral, surprising, and differentiate this series from generic "how I use AI" posts.

**Final structure:** Didactic ordering preserved (concepts build on each other), but organized by insight rather than by skill. Each post is anchored by a concrete failure and the insight it produced. Pushback integrated into Post 5 as the strongest example of the thesis.

---

## Post 1: "The Rule That Changes the Rules"

**Thesis:** LLM behavior is programmable — not through prompting, but through the same discipline as any other programming. CLAUDE.md is a living spec, not a static readme.

**Scope:**
- T1 pre-history: rules.md (Sep 2025) → AGENTS.md → oklch-theme "Agent Memory" with self-update → structured file taxonomy (home, Jan 2026)
- The remember concept: agent identifies pattern, formulates constraint, places it
- User framing: "it's still programming — process flow, data flow, debugging. The only new thing is conversational fluency at the interface"
- User framing: "AGENTS.md → CLAUDE.md migration wasn't deliberate architecture — trial and error converging on platform conventions"

**Hook:** Open with the Sep 2025 rules.md — 14 rules, flat markdown. End with CLAUDE.md + 23 fragments + 18 skills + 14 sub-agents. Six months, one person, trial and error.

**Evidence sources:**
- `pre-edify-evolution.md` — rules → emojipack → tuick → home arc
- `synthesis.md` §Phase 1, §Phase 2
- `topic-1-memory-system.md` §Phase 0
- `cross-repo-patterns.md` §Agent Instruction Evolution Arc
- `appendix-underlying-model.md` §What's Actually New

**Target length:** 1500-2000 words

---

## Post 2: "When Your Agent Invents Instead of Researching"

**Thesis:** LLMs confabulate methodology with full confidence. Internal reasoning alone produces plausible-but-invented output. External research is the structural break.

**Scope:**
- T4: confabulated scoring exposed → WSJF grounding → diverge-converge pattern
- The ground skill: parallel internal brainstorm + external web search → synthesis
- Self-application: grounding the design skill, bootstrapping paradox
- User framing: "LLMs don't reason — they pattern-match for logically consistent language"

**Hook:** "Establish grounded methodology" → agent produces scoring with subjective weights and no external anchoring → user catches it → same-day fix produces diverge-converge pattern.

**Evidence sources:**
- `topic-4-ground-skill.md` — full timeline + all excerpts
- `appendix-underlying-model.md` §LLMs Don't Reason, §What The Five Topics Show (T4)
- `cross-topic-connections.md` §Pattern 2 (Reasoning drives conclusion)

**Target length:** 1500-2000 words

---

## Post 3: "Zero Percent"

**Thesis:** Agents never spontaneously consult reference material — not at 4.1%, not at 0.2%, at zero. Context without procedural activation is dead weight. The memory problem is a recognition problem.

**Scope:**
- T1: memory-index creation → /when skill → 4.1% measurement → 0% spontaneous recall confirmed
- Handoff as the solution that actually works: session.md, learnings.md, structured carry-forward
- The recognition bottleneck: `/commit` (action trigger) succeeds, `/when` (metacognitive trigger) fails
- Forced injection: moving recognition from agent to script

**Hook:** 129 recall tool invocations across 69 sessions. Zero spontaneous. Every single one was either mandated by a skill step or initiated by the user.

**Evidence sources:**
- `topic-1-memory-system.md` — full arc from Phase A through Phase G
- `appendix-underlying-model.md` §What The Five Topics Show (T1)
- `cross-topic-connections.md` §Pattern 3 (Measurement reveals wrong assumptions), §Arc 2

**Target length:** 2000-2500 words (richest evidence base, multiple measurements)

---

## Post 4: "385 Tests Pass, 8 Bugs Ship"

**Thesis:** Automated quality gates pass individually while the system fails collectively. Defense-in-depth and structurally grounded review catch what tests miss.

**Scope:**
- T3: statusline-parity failure cascade → RCA → defense-in-depth → ISO/IEEE grounded review taxonomy
- The two-layer model: delegated per-file + mandatory interactive cross-cutting
- "Tests are executable contracts" and "warnings do not work" as design principles
- External validation: devddaanet full review cycle (but post-delivery: 3 of 5 commits are bug fixes)

**Hook:** 14 TDD cycles. 28 commits. 385/385 tests passing. Agent declares "visual parity validated against shell reference." Human opens the terminal. Eight discrepancies.

**Evidence sources:**
- `topic-3-deliverable-review.md` — full timeline + all excerpts
- `appendix-underlying-model.md` §What The Five Topics Show (T3)
- `synthesis.md` §devddaanet section
- `cross-topic-connections.md` §Pattern 3

**Target length:** 1500-2000 words

---

## Post 5: "Constrain, Don't Persuade"

**Thesis:** Every successful approach in this series treated the agent as a system to be constrained, not a colleague to be persuaded. Structural enforcement is the meta-pattern.

**Scope:**
- T5: the escalation ladder from `just agent` (Oct 2025) to PreToolUse hooks (Feb 2026)
- T2 (pushback) as the primary example: anti-pushback → metacognitive dead ends → disagree-first overcorrects → verdict-first → grounding gates. The full reversal arc.
- The meta-pattern validated across all topics (cross-topic connections §The Meta-Pattern)
- What didn't work: metacognitive instructions (oklch-theme, tuick cognitive protocols), semantic matching (topic injection removed after 5 days)
- The fundamental ceiling: S3 agreement momentum — accepted as unsolvable at prompt level
- Closing: the thesis from appendix-underlying-model.md — the model doesn't become more correct, it has fewer ways to be wrong

**Hook:** The earliest agent instructions said "proceed autonomously without asking." The current system includes a pushback protocol with structural verification gates. The reversal took four repos, three months, and two overcorrections.

**Evidence sources:**
- `topic-5-structural-enforcement.md` — full timeline + enforcement ladder
- `topic-2-pushback.md` — full arc (most compelling example of the thesis)
- `cross-topic-connections.md` §The Meta-Pattern, §Arc 1, §Arc 5
- `appendix-underlying-model.md` — full document (series capstone)

**Target length:** 2000-2500 words (series capstone, synthesizes all topics)

---

## Material Mapping

| Source File | Post 1 | Post 2 | Post 3 | Post 4 | Post 5 |
|-------------|--------|--------|--------|--------|--------|
| topic-1-memory-system.md | Phase 0 | | Main | | |
| topic-2-pushback.md | | | | | Main |
| topic-3-deliverable-review.md | | | | Main | |
| topic-4-ground-skill.md | | Main | | | |
| topic-5-structural-enforcement.md | | | | | Main |
| synthesis.md | Phase 1-2 | | | devddaanet | |
| cross-topic-connections.md | | Pattern 2 | Pattern 3, Arc 2 | Pattern 3 | Meta-Pattern, Arc 1, Arc 5 |
| appendix-underlying-model.md | §New | §T4 | §T1 | §T3 | Full (capstone) |
| pre-edify-evolution.md | Main | | | | Pre-history |
| cross-repo-patterns.md | Evolution arc | | | | |
| pre-agentic-baseline.md | Contrast | | | | |
| parallel-projects.md | | | | | |
| repo-inventory.md | Reference | | | | |
| topic-cross-reference.md | | | | | |

## Series Arc

```
Post 1: Here's what I built (introduction, scope, the journey)
Post 2: Here's the first thing that broke (confabulation, the "wow")
Post 3: Here's the measurement that changed everything (0%, recognition)
Post 4: Here's what tests can't catch (quality, defense-in-depth)
Post 5: Here's the principle that ties it all together (structural enforcement)
```

Each post is self-contained (reader can enter at any post) but builds toward the thesis in Post 5. Posts 2-4 provide the evidence; Post 5 names the pattern.

## Corrections Applied

All post syntheses must use corrected framings from brief.md:
- oklch-theme: "started with Gemini, iterated in Claude Desktop" (not "Gemini project")
- LLM Limitation Awareness and cognitive protocols: "metacognitive dead end / wishful thinking" (not "proto-pushback")
- scratch/ repos: tooling workaround (drop prefix from narrative)
- devddaanet review: "ensures review happens, not that it's comprehensive" (3 of 5 post-delivery commits are bug fixes)
