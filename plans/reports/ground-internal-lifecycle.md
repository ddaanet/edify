# Internal Lifecycle Naming: Project-Specific Brainstorm

Dimensions, constraints, and desiderata for naming post-execution plan states. All analysis is specific to this project's agent architecture, marker file system, and operational patterns.

---

## 1. LLM Agent Naming Constraints

### How state names are consumed

State names appear in three contexts, each with different constraints:

- **`#status` display** — Agent reads `Plan: hook-batch [ready] → /orchestrate hook-batch`. The `[status]` string is a decision input. The agent uses it to determine what to suggest, whether to skip, and how to describe the plan to the user.
- **`_derive_next_action` match arms** — The status string is a Python `match/case` target. Agent-facing only indirectly (through the derived action), but the name must be a valid Python identifier-like string (lowercase, hyphens or underscores).
- **`_determine_status` priority chain** — The docstring reads `Status priority: ready > planned > designed > requirements`. Adding 4 more states doubles the cognitive load of this priority chain.

### Properties that make a name LLM-friendly

- **Unambiguous polarity.** An LLM must immediately know if a state is "good" (proceed) or "bad" (stop/fix). "Completed" is unambiguously good. "Review-pending" is neutral-to-good (waiting, not broken). "Defective" is unambiguously bad. Clear polarity prevents agents from treating blocked states as actionable.
- **Action-suggestive.** The name should hint at what to do. "Review-pending" suggests "run the review." "Defective" suggests "fix something." "Delivered" suggests "nothing more." The existing names do this well: "requirements" → write design, "designed" → write runbook.
- **Non-overlapping with task status vocabulary.** Task notation uses `completed` (`[x]`), `blocked` (`[!]`), `failed` (`[✗]`). If plan status uses the same words with different semantics, agents will conflate them. "Completed" already exists in both domains — the plan-level meaning (review passed, ready to deliver) differs from task-level (work done).
- **Consistent grammatical form.** Existing states are past participles (`designed`, `planned`) or bare nouns (`requirements`, `ready`). New states should match. `review-pending` is adjectival (matches `ready`). `completed` and `delivered` are past participles (match `designed`, `planned`). `defective` is adjectival (matches `ready`).

### LLM confusion risk: "completed" vs "delivered"

Both sound terminal. An agent reading `[completed]` will likely treat it as done-done. The distinction (review passed vs. merged to main) is subtle. A haiku agent in particular will not reliably distinguish these without additional prompt context.

**Mitigation options:**
- Rename `completed` to something that implies "approved but not yet shipped" — e.g., `reviewed`, `approved`, `accepted`
- Keep `completed` but ensure `_derive_next_action` returns an explicit action (merge command) so the agent sees actionability
- Accept the ambiguity — the gap between completed and delivered is typically one command (`_worktree merge`), and the agent executing it already knows the context

### LLM confusion risk: "defective"

"Defective" implies a manufacturing defect — something intrinsically wrong with the product. In our system, the deliverables may be fixable (and usually are — most review findings are major, not critical). An agent reading "defective" might:
- Treat the plan as unsalvageable (over-interpretation)
- Hesitate to re-enter the plan (negative connotation stronger than intended)
- Conflate with task `[✗]` failed status (terminal vs. reworkable)

Alternative candidates and their connotations for LLM consumers:
- `needs-rework` — Most action-suggestive. Tells the agent exactly what to do. Two words, hyphenated.
- `rejected` — Clear polarity but implies a human decision. Our reviewer is an agent.
- `failed-review` — Explicit about what happened. Compound name.
- `rework` — Bare noun, like `requirements`. Shortest.
- `defective` — Strong negative. Industrial quality terminology.

---

## 2. Marker File Semantics

### The name IS the filename

Each state is detected by `(plan_dir / "state-name.md").exists()`. This creates hard constraints:

- **Filesystem-safe characters only.** No spaces, no special characters. Hyphens work (we already use them: `runbook-phase-1.md`). Underscores would break convention.
- **Lowercase.** All existing artifacts are lowercase (`requirements.md`, `design.md`, `orchestrator-plan.md`).
- **Colloquially parseable as a filename.** `review-pending.md` reads naturally. `needs-rework.md` reads naturally. `defective.md` reads naturally.
- **No collision with existing artifacts.** Current files: `requirements.md`, `design.md`, `outline.md`, `problem.md`, `orchestrator-plan.md`, `runbook-phase-N.md`, `brief.md`. None of the proposed names collide.

### Marker file content

D-3 says "Marker files with minimal content (date, source). Not empty. Content for humans, not parsed." This means:
- The filename carries the entire semantic load for detection
- File content is purely diagnostic (when was it created, by whom/what)
- No risk of content-based parsing complexity

### Priority chain extension

Current detection: `ready > planned > designed > requirements`
Proposed: `delivered > completed > defective > review-pending > ready > planned > designed > requirements`

The priority chain is a waterfall: highest-priority marker file wins. This means:
- A plan with both `completed.md` and `defective.md` is `completed` (the defective was fixed)
- A plan with both `delivered.md` and everything else is `delivered` (terminal)
- A plan with `review-pending.md` and `ready` artifacts is `review-pending` (execution done, trumps planning artifacts)

**Potential issue:** The `defective ↔ review-pending` loop. After rework fixes the defects, a new `review-pending.md` is created. Does `defective.md` get deleted? Or does the priority chain handle it (review-pending > defective)? If both exist simultaneously, priority says `defective` wins — which is wrong after rework.

**Resolution options:**
- Delete `defective.md` when re-entering review — requires active file management
- Reverse priority: `review-pending > defective` — then review-pending always wins when present, defective only shows when review-pending is absent (which means review hasn't been re-triggered)
- Use a single file with content-based state — contradicts the "existence detection" model

This is a genuine design constraint the naming decision must address. The priority between `defective` and `review-pending` determines whether file deletion is required in the loop.

### File accumulation

Marker files accumulate. A delivered plan has: `requirements.md`, `design.md`, `outline.md`, `runbook-phase-*.md`, `steps/`, `orchestrator-plan.md`, `review-pending.md`, `completed.md`, `delivered.md` — potentially also `defective.md` from a prior review cycle. That's 4 new files minimum for the post-execution lifecycle. The plan directory grows from ~5-8 files to ~9-12 files.

This is acceptable — plan directories already accumulate `reports/` subdirectories with multiple files. The marker files are small.

---

## 3. Review Loop Semantics

### The unusual pattern

Most lifecycle models have a linear post-execution path: done → reviewed → shipped. Our loop allows:

```
review-pending → (review fails) → defective → (rework) → review-pending → (review passes) → completed
```

This can cycle N times. Each cycle involves:
1. Deliverable review agent runs, finds issues
2. Fix agent (or manual intervention) resolves issues
3. Review re-runs

### Naming for loop clarity

The loop has two transition types:
- **Forward:** review-pending → completed (pass) or review-pending → defective (fail)
- **Backward:** defective → review-pending (re-submit for review)

Names should make the direction clear:
- `review-pending` → "I'm waiting for review" (entry point and re-entry point)
- `defective` → "Review found problems" (exit-to-rework)

The re-entry from defective back to review-pending is the tricky transition. Does "review-pending" mean "first review" or "re-review after fixes"? For the state machine, it doesn't matter — the state is the same regardless of how many times you've entered it. For human/agent comprehension, the marker file content could record the cycle count.

### Alternative: explicit review-cycle naming

Instead of reusing `review-pending` for re-review, could use:
- `review-pending.md` for first review
- `review-N.md` for Nth re-review

This breaks the simple existence-check model. Not worth it. The single `review-pending` state with content tracking cycle count is cleaner.

---

## 4. Transition Ambiguity Analysis

### Where an LLM agent could trigger the wrong transition

**review-pending → defective vs. review-pending → completed:**
The transition is determined by the deliverable review outcome, not by the agent's choice. The review skill/agent writes the marker. Low ambiguity — the agent doesn't choose.

**defective → review-pending:**
After rework, who creates the new `review-pending.md`? The rework agent? The orchestrator? Manual? If it's automatic after commit, the agent doesn't choose. If it requires explicit re-submission, an agent must know to trigger it. `_derive_next_action` for `defective` should return the re-review command.

**completed → delivered:**
In worktree context, this happens at `_worktree merge`. In main-branch context (no worktree), this could happen immediately after review passes. The agent needs to know whether to merge or whether completed IS the terminal state in-context.

**ready → review-pending:**
This transition happens after orchestration completes. The orchestrator (or a post-orchestration hook) creates `review-pending.md`. An agent looking at a `ready` plan should not be confused about whether to create `review-pending.md` directly vs. running orchestration first. `_derive_next_action` for `ready` returns `/orchestrate` — the review-pending marker is a side effect of successful orchestration.

### "Defective" vs "failed" vs "rejected"

| Term | Implies | LLM risk |
|------|---------|----------|
| `defective` | Inherent flaw, QA terminology | Agent may treat as unsalvageable |
| `failed` | Terminal outcome, test failure | Collides with task `[✗]` failed (terminal) |
| `rejected` | Human judgment, PR review | Implies authority/decision, not automated finding |
| `needs-rework` | Action required, fixable | Most action-suggestive, clear next step |
| `rework` | Bare noun, like `requirements` | Matches existing naming pattern |

**Strongest candidate: `rework`**
- Matches the bare-noun pattern of `requirements`
- Implies action without implying terminality
- No collision with task status vocabulary
- `rework.md` as filename reads naturally
- `_derive_next_action("rework")` → re-review command (clear)

**Runner-up: `needs-rework`**
- More explicit but breaks the single-word pattern

**Weakest: `failed`**
- Direct collision with `[✗]` task status (terminal)
- Agent could treat plan as abandoned rather than reworkable

---

## 5. "Delivered" vs "Deployed"

### Our definition

"Delivered" = merged into main branch via `_worktree merge`. This is the terminal state. The plan's work exists on the main branch and is available to all sessions.

### Potential confusion

In CI/CD terminology:
- "Delivered" (Continuous Delivery) = artifact built and tested, ready for production deployment
- "Deployed" (Continuous Deployment) = running in production

In kanban:
- "Done" = accepted by customer
- "Delivered" = varies by team

### Why "delivered" is correct for us

Our "main branch" IS production. There's no staging environment, no deployment pipeline, no production server. When code merges to main, it's immediately available — every new Claude Code session on main uses the new code.

"Deployed" would imply infrastructure we don't have. "Released" implies versioning/packaging we don't do.

"Delivered" correctly captures: the plan's deliverables have been transported from the worktree (development) to main (production).

### Edge case: in-main execution

When a plan is executed directly on main (no worktree), there's no merge event. The transitions completed → delivered happen in immediate succession. D-2 notes: "In-main: completed and delivered in sequence (no merge gap)." The `delivered.md` marker is created by the completion process itself, not by a merge.

This means "delivered" has two creation paths:
1. Worktree: `_worktree merge` creates it
2. In-main: completion process creates it

The naming holds for both paths — "delivered to main" is accurate whether by merge or by direct commit.

---

## 6. Terminal State Clarity

### The problem

`completed` and `delivered` are both terminal-sounding. In English:
- "The project is completed" = done, nothing left
- "The project is delivered" = shipped to recipient

Both imply finality. But in our system, `completed` still has one action remaining (merge/deliver).

### Naming alternatives for `completed`

| Term | Implication | Distinguishes from `delivered`? |
|------|-------------|-------------------------------|
| `completed` | All work done | Weakly — "done" vs "shipped" is subtle |
| `reviewed` | Review passed | Yes — describes what happened, not finality |
| `approved` | Accepted for delivery | Yes — implies a gate passed, delivery pending |
| `accepted` | Quality accepted | Similar to approved |
| `verified` | Verification complete | Technical, accurate |
| `ready-to-deliver` | Explicit pre-delivery | Very clear but verbose as filename |
| `mergeable` | Can be merged | Context-specific, clear for worktree users |

**Strongest candidate: `reviewed`**
- Past participle (matches `designed`, `planned`, `delivered`)
- Describes the transition that just happened (review passed)
- Does NOT sound terminal — "reviewed" implies something follows
- `reviewed.md` as filename is natural
- Status display: `Plan: hook-batch [reviewed] → _worktree merge hook-batch`

**Runner-up: `approved`**
- Implies a gate/authority, which is accurate (deliverable review is a gate)
- Slightly more formal than the existing vocabulary

**Weakest: `completed`**
- Sounds terminal, conflates with task `[x]` completed
- An agent seeing `[completed]` may not look for `_derive_next_action`

### The lifecycle with naming alternatives

Original: `requirements → designed → planned → ready → review-pending → [defective ↔ review-pending] → completed → delivered`

Alternative A (strongest): `requirements → designed → planned → ready → review-pending → [rework ↔ review-pending] → reviewed → delivered`

Alternative B: `requirements → designed → planned → ready → review-pending → [defective ↔ review-pending] → approved → delivered`

---

## 7. Plan States vs Task States

### Current mappings

| Task status | Notation | Plan equivalent |
|-------------|----------|-----------------|
| Pending | `[ ]` | requirements, designed, planned, ready |
| In-progress | `[>]` | (during orchestration — no marker) |
| Completed | `[x]` | delivered |
| Blocked | `[!]` | (gate stale — vet chain) |
| Failed | `[✗]` | (no equivalent today) |
| Canceled | `[–]` | (no equivalent today) |

### Where new states map

- `review-pending` → Task is still in-progress (`[>]`). The plan executed but the task isn't done until delivery.
- `defective` / `rework` → Closest to task `[!]` blocked. Work can't proceed until issues are fixed. But it's self-unblocking (fix and re-review), unlike task-blocked which waits for external signal.
- `completed` / `reviewed` → Task is still in-progress. Deliverables are good but not yet on main.
- `delivered` → Task `[x]` completed. The plan's contribution to the task is done.

### The "defective" ≈ "[!] blocked" question

Task `[!]` means "waiting on signal — see `task-failure-lifecycle.md`." Plan `defective`/`rework` means "deliverable review found issues, fix them." The key difference:
- Task blocked: external dependency, can't self-resolve
- Plan rework: internal quality issue, self-resolvable

Using "defective" for a self-resolvable state is misleading if agents associate it with the blocked/failed family. "Rework" better captures the self-resolvable nature — it names what to do, not what's wrong.

### Cross-domain naming collision analysis

- `completed` in task domain = terminal. `completed` in plan domain = pre-terminal. **Collision risk: HIGH.**
- `reviewed` in task domain = not used. `reviewed` in plan domain = pre-terminal. **Collision risk: NONE.**
- `delivered` in task domain = not used. `delivered` in plan domain = terminal. **Collision risk: NONE.**
- `rework` in task domain = not used. `rework` in plan domain = needs fixes. **Collision risk: NONE.**

This strongly favors `reviewed` over `completed` for the pre-terminal state.

---

## Summary of Recommendations

| Proposed | Alternative | Rationale |
|----------|-------------|-----------|
| `review-pending` | (keep) | Clear, action-suggestive, no collision |
| `defective` | `rework` | Action-suggestive, non-terminal connotation, matches bare-noun pattern, avoids task-status collision |
| `completed` | `reviewed` | Past-participle consistency, non-terminal connotation, no cross-domain collision |
| `delivered` | (keep) | Correct for our deployment model (main = production) |

### Open design question: priority ordering in the review loop

Must resolve: when both `rework.md` and `review-pending.md` exist, which wins? Two options:
1. `rework > review-pending` (current proposal in D-4) — requires deleting `rework.md` when re-submitting
2. `review-pending > rework` — review-pending presence means "currently in review," rework presence means "was in rework but re-submitted"

Option 2 avoids file deletion in the loop. The latest marker always wins. Sequence: orchestration creates `review-pending.md` → review fails, creates `rework.md` (rework > review-pending → status is rework) → fixes applied, new `review-pending.md` created (but it already exists... needs touch/overwrite to update mtime? Or priority based on mtime?).

This reveals a limitation of pure existence-based detection for cyclic states. The priority chain works for linear progressions but creates ambiguity in loops. Options:
- Accept file deletion as the loop mechanism (delete rework.md on re-review)
- Use mtime comparison instead of existence for loop states
- Merge rework and review-pending into a single state with content-based sub-state

This is a design constraint that the design phase should resolve. Flagged here for the grounding output.
