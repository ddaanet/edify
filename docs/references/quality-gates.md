# Quality gates

Decisions governing how a gate is built so it cannot be skipped: layering,
chokepoint placement, tool-call anchoring, and the structural fixes that work
where stronger wording does not. Read this before designing or changing a gate,
a hook or a validating script.

Part of the `docs/design.md` graph; conclusions are indexed in
`docs/decisions.md`.

**D-46 — Quality gates are layered; no single gate is trusted alone.** Four
layers, outer to inner: execution flow (the gate is anchored by a tool call so
it cannot be optimized away as prose), automated checks (`just precommit` —
formatting, line limits, lint, tests), semantic review (a corrector catches
logic, integration and design-deviation issues), and conformance (comparison
against an external reference). Each prevents a distinct failure mode.
*Grounding:* a parity failure cascade where unit tests passed 385/385 while 8
visual parity issues survived, the review missed systemic conformance gaps
because its mandate excluded reference comparison, and the 400-line constraint
was bypassed — each layer failed independently.

Checklist when designing a new gate: is there an outer execution-flow defense, a
middle automated check, an inner semantic review, and — for external-reference
work — a conformance comparison? Do the layers have *different* failure modes?
Can any single layer's failure cause total failure?

**D-47 — Gate at the chokepoint, not with ambient rules.** Ambient rules in
always-loaded context telling agents to review artifacts are unenforceable:
agents rationalize skipping under momentum, and sub-agents never see them. A
scripted check at the commit chokepoint blocks mechanically with no judgment at
the gate. *Grounding:* ~100 lines of always-loaded context eliminated for no
behavioral loss.

**D-48 — Anchor a gate with a tool call that proves work happened.** "Read X
(skip if already in context)" is not a gate — the escape hatch *is* the failure
mode, and the agent rationalizes the skip without verifying. The canonical
anchor is the recall pass, and its anchoring call is the Read of
`<plan-dir>/recall-artifact.md` followed by Reads of the files selected from the
index — *not* a Read of the index itself. The index is already in context
(D-72), so instructing a Read of it buys a redundant tool call rather than
evidence of selection. The artifact Read is unskippable and the per-file Reads
require knowing which entries matter, so the pair proves selection happened. One
anchor suffices — passphrase and proof-of-Read mechanisms are redundant when the
anchor proves both. The negative path must cost the same: a null recall artifact
still gets Read, so the gate is provably reached whether or not anything was
found.

Verify that the anchor tool's preconditions match the gate's runtime state. A
recall-diff keyed on `git log --since=mtime` needs intervening commits; at a
post-explore gate the exploration reports are uncommitted and the check finds
nothing.

**D-49 — Split validation into mechanical and semantic.** A script handles
deterministic checks — blocking, zero false positives. An agent enriches an
existing review for semantic checks — advisory. `verify-step.sh` (clean tree,
precommit — blocking) beside `corrector` (semantic review — fix-all, flagging
what it cannot fix) is the split; bundling both in one agent pass loses both
properties.

**D-50 — Fix the environment, not the prose.** Strengthening language ("no
exceptions", "MUST", scenario-specific warnings) in a rule the agent already saw
and rationalized past does not work: if the rule was clear and the agent
overrode it, clarity was not the problem. Structural fixes — resolve conflicting
directives, anchor gates with tool calls, add hooks or scripts, ensure
sufficient context at the decision point.

**D-51 — Either fail the build or do not check.** Validators that print warnings
without failing normalize deviance and create a false sense of compliance.
*Trade-off:* hard limits force immediate resolution and may need tuning.

**D-52 — Every skill step opens with a concrete tool call.** Steps carrying only
prose judgment get skipped: execution-mode cognition optimizes for "next tool
call", so a step without one registers as commentary. The D+B fix eliminates
standalone prose gates by merging each into its adjacent action step, anchors
each gate's first instruction with a Read or Bash call providing the data to
evaluate, and makes control flow explicit with if/then branch targets.

**D-53 — Negative constraints sit beside the positive guidance they qualify.** A
"don't write X" rule placed in a later cleanup phase fires after the violation
is already written. Any rule about what *not* to produce is co-located with the
instructions for what to produce.

**D-54 — A skill needs four discovery layers, not good internal documentation.**
Always-loaded context, a path-triggered `.claude/rules/` entry, in-workflow
reminders in related skills, and a directive description. Agents see only skill
listing descriptions and always-loaded context; internal skill docs are
invisible until invoked. *Grounding:* a skill with 248 lines of documentation
and zero external visibility — agents asked the user instead of consulting it.

## Rejected alternatives

**A `"Bash(rm:*/index.lock)"` permission deny entry** — never fires, because
`rm` runs inside the sandbox without needing explicit permission. A PreToolUse
hook inspecting `tool_input.command` fires unconditionally.

**A PreToolUse advisory (exit 0 + `additionalContext`) as a pre-delegation
gate** — no model turn runs between the hook and tool execution on exit 0, so
the spawn dispatches, runs and completes before the agent reads the advisory.
The gate would be post-delegation. Blocking with `permissionDecision: deny` is
the mechanism.
