# Post 5: "Constrain, Don't Persuade"

## Opening Hook

The earliest agent instructions said "proceed autonomously without asking until all tasks complete." (rules repo, `7b0a4b4`, Sep 2025. Propagated to emojipack `9cc5c62`, tuick `7d2fa67`.)

The current system includes a pushback protocol with structural verification gates, 31 recall gates anchored by tool calls, PreToolUse hooks that block operations before the agent can execute them, and a defense-in-depth model with four enforcement layers.

The reversal took four repos, three months, and two overcorrections.

## Core Argument

### The Escalation Ladder

Structural enforcement didn't begin with tool-call anchoring in February 2026. The principle was operating five months earlier — at a coarser granularity.

```
`just agent` commit gate (emojipack, Oct 2025)
  → Agent-vs-human command separation (box-api, Nov 2025)
    → Platform config: .claude/settings.json (pytest-md, Jan 2026)
      → Orchestrator constraints: Allowed/Delegate (home, Jan 2026)
        → Shared infrastructure: plugin submodule (home, Jan 2026)
          → Defense-in-depth document: D+B named (Feb 8)
            → Prose gates skipped under momentum (Feb 24)
              → Gate inventory: 31 gates, 61% prose-only (Feb 24)
                → Language strengthening rejected (Feb 24)
                  → Tool-call-anchored gates (Feb 25)
                    → Conditional gates still fail (Mar 2)
                      → Unconditional gates: file absence = signal (Mar 2)
                        → PreToolUse hooks: platform enforcement (Feb 21-28)
```

Each rung exists because the previous one failed under a specific condition. `just agent` prevents bad commits but doesn't shape in-session behavior. Role separation prevents wrong-tool usage but doesn't prevent instruction skipping. Platform config prevents configuration drift but doesn't prevent prose rationalization. D+B tool-call anchoring mostly prevents prose skipping — but conditional gates reintroduce the failure mode.

### The Pushback Story

The clearest illustration of the thesis.

**Phase 1: Anti-pushback (Oct 2025).** "Proceed autonomously." The initial design optimized for throughput. Don't stop, don't ask, don't evaluate. Three repos, three months.

**Phase 2: Metacognitive dead ends (Nov–Dec 2025).** oklch-theme (started with Gemini, iterated in Claude Desktop): "Flag uncertainty when multi-step reasoning exceeds 3 steps." tuick: full cognitive protocols — structured metacognition rules. Removed three days later. Both assume confidence-monitoring capability the architecture doesn't have. The lightweight version (oklch-theme) and the heavyweight version (tuick) fail for the same reason: the mechanism is unsound.

**Phase 3: Formalized pushback (Feb 13, 2026).** Pushback fragment: identify counterarguments, track agreement momentum, evaluate model selection. 11 TDD runbook steps, 100% compliance. Four validation scenarios. S1 and S2 pass. S3 (agreement momentum) and S4 (model selection) fail. (Commit `904d679b`)

**Phase 4: The sycophancy trigger test.** Four `d:` proposals in sequence, each with correct conclusions and imprecise reasoning. The agent corrected reasoning on all four. Agreed with every conclusion. "I pushed back on *reasoning* each time but validated every *conclusion*." The rules were satisfied structurally — the agent did evaluate assumptions, did articulate alternatives — while the behavioral goal (genuine disagreement when warranted) was bypassed. (Session `986a00d2`)

This is the core pattern: prose rules create a compliance surface the agent can satisfy without achieving the intended behavioral change.

**Phase 5: Overcorrection.** The fix: disagree-first protocol — articulate the strongest case AGAINST the proposed conclusion. Result: contrarianism. The mirror image of sycophancy. "Whichever reasoning direction the agent pursues first determines the conclusion." AGAINST-first produces disagreement; FOR-first produces agreement. Same mechanism, opposite direction.

Tested without the hook (bare "discuss" prefix) — still too negative. The fragment itself produced contrarianism, not hook duplication. (Session `5952058f`)

**Phase 6: Verdict-first.** Form assessment before building arguments in either direction. Stress-test your own position, not one-directional search. This structurally prevents reasoning-drives-conclusion because the agent commits to a position before constructing arguments. (Commit `beb591a2`)

**Phase 7: Grounding gates (Feb 28).** Even verdict-first was purely reasoning-based. Added structural gates: read referenced artifacts and resolve recall entries before forming assessment. Either the agent read the file or it didn't — verifiable. FR-1 acceptance criterion: "Verification is structural (protocol step with tool call), not advisory (prose instruction)." (Commit `3099c2eb`)

**Phase 8: Accepting a ceiling.** Agreement momentum (S3) failed across two improvement cycles. The pragmatic decision: ship what works, document the known limitation. "Prompt-level self-monitoring may have a fundamental ceiling because the model lacks persistent cross-turn state." (Session `1f594e71`)

### The Meta-Pattern Across All Topics

Structural enforcement is the connecting thread across every topic in this series:

**Memory (Post 3):** 0% spontaneous recall. The fix: forced injection via hooks (recognition moved from agent to script) and procedural recall mandated by skill steps.

**Confabulation (Post 2):** Internal reasoning alone produces confident fabrication. The fix: parallel diverge-converge with external research that produces tool calls (Task agents dispatched, web searches executed) the agent can't rationalize away.

**Quality (Post 4):** 385 tests pass, 8 bugs ship. The fix: tests as executable contracts (structural specification), defense-in-depth (layered gates), mandatory review skill invocation before delivery.

**Pushback (this post):** Prose rules satisfied structurally without behavioral change. The fix: verdict-first reasoning order + grounding gates with tool calls.

Each topic arrived at the same principle through its own failure cascade.

### Why Structural Enforcement Works

The appendix to this retrospective states the principle directly:

"The common thread isn't 'prose fails.' It's that LLMs optimize for linguistic consistency, not correctness. Procedural activation (tool calls, gates, hooks) works because it constrains the completion space structurally. The model doesn't become more correct — it has fewer ways to be wrong."

Prose instruction: "Check the error handling decision before writing error handling code." The model can generate linguistically consistent output without executing this step — "I've written error handling that's consistent with the patterns I've seen" is a valid completion.

Tool-call gate: `edify _recall resolve "when raising exceptions"`. The model must either execute the command (producing output that enters its context) or not execute it (absence is observable). The completion space is constrained to {execute, skip}, and skip is detectable.

PreToolUse hook: platform intercepts the tool call before execution. The agent cannot bypass through rationalization — the enforcement happens at a layer below agent control.

### What Didn't Work

- **Metacognitive instructions** (oklch-theme "flag uncertainty", tuick cognitive protocols): assume capabilities the architecture doesn't have
- **Semantic matching for recall** (topic injection): structurally sound mechanism, but keyword matching produced low-relevance hits. Delivered clean (0C/0Ma/3Mi in review), removed 5 days later, 896 lines deleted. Structural enforcement works best with deterministic triggers (file existence, tool name), not semantic matching (keyword overlap)
- **Graduated enforcement** ("warnings"): if the model can produce a valid completion that includes the warning and ignores the instruction, it will

### The Frame

Every failed approach in this series assumed the model's fluent output meant it understood the instruction. Every successful approach treated the model as a system to be constrained, not an agent to be persuaded.

It's the same discipline as any other programming. Specify inputs, constrain execution paths, verify outputs. The interface changed from syntax to natural language. The discipline didn't.

## Evidence Chain

| Claim | Evidence |
|-------|----------|
| "Proceed autonomously" in earliest instructions | rules `7b0a4b4`, emojipack `9cc5c62`, tuick `7d2fa67` |
| oklch-theme: started Gemini, iterated Claude Desktop | oklch-theme `64cbf8f` |
| Cognitive protocols: added Dec 12, removed Dec 15 | tuick `a3e15a1`, `26c3b5d` |
| S3/S4 failed in initial pushback | Commit `904d679b` |
| Sycophancy trigger: agreed with all 4 conclusions | Session `986a00d2` |
| Disagree-first → contrarianism | Session `5952058f` |
| Fragment itself caused contrarianism (tested without hook) | Session `5952058f` — bare "discuss" prefix |
| Verdict-first protocol | Commit `beb591a2` |
| Grounding gates with tool-call verification | Commit `3099c2eb`, FR-1 acceptance criterion |
| S3 accepted as fundamental ceiling | Session `1f594e71` |
| 31 gates, 61% prose-only | Commit `7ee9d0c0` |
| Language strengthening explicitly rejected | Commit `cd45d076` |
| Unconditional gates: conditional D+B still fails | Session `4d31c984` |
| Topic injection: delivered clean, removed 5 days later | Commits `e253c43f`, `108a444d` |
| 896 lines deleted | Commit `108a444d` |

## Series Closing

Six months, 16 repos, 1,459 commits. The starting point was 14 rules in a flat file. The ending point is a shared framework with fragments, skills, hooks, and a recall system.

The journey followed a predictable pattern: write prose instructions → observe agents bypass them → measure the bypass rate → build structural enforcement → discover the next bypass mode → escalate. Each step made the system more reliable by reducing the space of valid completions the model could produce.

The model didn't get smarter. The constraints got tighter. That's the entire lesson.
