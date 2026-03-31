# Interactive Review: Grounding Report

**Grounding:** Strong — 4 established frameworks (Fagan, IEEE 1028, Gerrit, Phabricator) + cognitive load research (Cisco/SmartBear, Microsoft) + internal codebase patterns (/proof, corrector agents, deliverable-review). Per-item verdict gap validated across all surveyed tools.

---

## Framework Mapping

### External Frameworks Surveyed

| Framework | Relevance | Key Contribution |
|-----------|-----------|-----------------|
| Fagan Inspection (1976) | High | Reader-paraphrase, detection-not-resolution, per-item defect logging |
| IEEE 1028 (2008) | Moderate | Review type taxonomy, formality spectrum |
| GitHub PR Reviews | Low | Review-level verdicts only; inline comments without per-item verdicts |
| Gerrit Code Review | High | 5-point numeric scale, opinion-vs-decision distinction (+1/-1 vs +2/-2) |
| Phabricator Differential | High | Rich state machine, draft-then-submit, "Accepted Prior Diff" staleness |
| Cognitive Load Research | High | Segmentation principle, 60-90min ceiling, forced-verdict engagement |

### Internal Patterns Mapped

| Internal Pattern | External Analog | Mapping Tightness |
|-----------------|-----------------|-------------------|
| /proof reword-accumulate-sync | Fagan reader-paraphrase + defect logging | Loose — /proof validates user input, not agent findings |
| Corrector severity (critical/major/minor) | IEEE 1028 + industry 3-level | Tight — same taxonomy |
| Corrector status (FIXED/DEFERRED/OUT-OF-SCOPE/UNFIXABLE) | Phabricator revision states | Moderate — status is orthogonal to severity in both |
| Fix-all policy (correctors apply all fixes) | Fagan rework phase (author fixes all) | Tight — same principle, different actor |
| No merge-readiness language | Fagan detection-not-resolution | Tight — reviewer reports, user decides |

---

## Adaptations

### 1. Verdict Vocabulary: 5 Per-Item Verdicts

**General principle:** Structured inspection research converges on a 3-state model (pass / conditional / block) across all frameworks. Modern tools add skip/defer for reviewer workflow. Per-item verdicts force engagement — cognitive load research shows passive scanning misses defects.

**Project adaptation:** Map to existing corrector severity taxonomy + reviewer workflow actions.

| Verdict | Shortcut | Meaning | Corrector Status Mapping |
|---------|----------|---------|------------------------|
| **approve** | `a` | Item correct, no issues | — (no finding) |
| **revise** | `r` | Issue found, user states fix | FIXED (after edit applied) |
| **kill** | `k` | Item should be removed | — (item deleted) |
| **discuss** | `d` | Need to explore before deciding | — (enters sub-loop) |
| **skip** | `s` | Defer judgment to later | DEFERRED |

**What changed from requirements FR-4:** Removed `absorb` as a top-level verdict. Absorption is a specific type of kill (kill + transfer content). Handle as a sub-action within `kill` ("where should this content go?") rather than a separate verdict. This follows the convergence finding: all frameworks converge on 3-5 states, not 6+.

**Grounding:** Fagan uses 2 per-item states (defect/no-defect). Gerrit uses 5 numeric levels. GitHub/Phabricator have 3 review-level actions. The 5-verdict vocabulary sits at the intersection: richer than Fagan's binary (supports reviewer workflow), simpler than Gerrit's numeric scale (avoids training cost), and per-item where modern tools are per-review.

### 2. Detection vs Resolution: Reviewer Decides, Agent Doesn't Rationalize

**General principle:** Fagan inspection strictly separates detection (meeting) from resolution (rework). The author clarifies but cannot defend. This prevents premature closure — debating fixes during detection reduces defect capture rate.

**Project adaptation:** The `revise` verdict lets the reviewer state the fix (detection + direction), but the agent doesn't argue. The `discuss` verdict is the escape valve for items needing exploration. The corrector's existing "no merge-readiness language" rule is this same principle in artifact form.

**Inverse of /proof:** In /proof, the user proposes changes and the agent validates understanding (reword). In interactive review, the agent presents items and the user provides verdicts. The reword step inverts: agent restates the user's verdict before applying (not the user's change request).

### 3. Orientation Before Iteration: Preamble + TOC + Checkpoint

**General principle:** Fagan inspection has an Overview phase before the Inspection Meeting. IEEE 1028 inspection requires an overview session. Cognitive load research shows segmentation works best with advance organizers (schema activation before detail processing).

**Project adaptation (from dogfooding feedback):**
1. **Preamble:** What's being reviewed, item count, overall summary
2. **TOC:** Numbered list with per-item title + short summary (not table — brief feedback)
3. **Checkpoint:** Pause for user feedback before first item. User may reorder, skip sections, adjust scope.

**Grounding:** All formal inspection methods include orientation before item review. The dogfooding session confirmed the gap — jumping to Item 1 without context was disorienting.

### 4. Draft-Then-Submit: Accumulate Verdicts, Apply on Request

**General principle:** GitHub, Gerrit, and Phabricator all use batch submission — draft comments accumulated, then submitted together. This reduces noise and lets reviewers build a complete picture before committing.

**Project adaptation:** Two modes, reviewer's choice:
- **Immediate apply** (default, from FR-5): Each verdict applied as the reviewer gives it. File on disk always current. Matches FR-5's interruption-safety requirement.
- **Batch apply** (reviewer request): Accumulate verdicts, apply all at once. Matches draft-then-submit pattern.

**Tension with FR-5:** FR-5 requires immediate application for interruption safety. The batch pattern from external research conflicts. Resolution: immediate apply is default (FR-5 satisfied), batch is opt-in for reviewers who prefer the draft workflow.

### 5. Segmentation: One Item at a Time, Forced Verdict

**General principle:** Cognitive load research (Cisco 2006, 2,500 reviews) shows segmenting review into focused sub-tasks improves defect detection. Forced verdicts prevent passive scanning — reviewers who must decide on each item catch more issues than those who scan freely.

**Project adaptation:** Linear presentation with forced verdict before advancing. Skip is the escape valve (not silence). No random-access navigation during iteration — linear forces engagement with every item.

**Deliberate exclusion:** Random access (jump to item N, reorder) excluded despite being available in GitHub/Phabricator. Research shows linear presentation prevents skip-ahead bias. Allow revisiting completed items (change verdict on item 3 after reaching item 7) but not preview of upcoming items.

### 6. Session Boundaries: Time-Boxing Not Required, But Item Count Visible

**General principle:** Review effectiveness degrades after 60-90 minutes (Cisco 2006). Fagan inspection limits meetings to 2-3 hours with rate limits (150-500 LOC/hour for code, 4-6 pages/hour for documents).

**Project adaptation:** Don't enforce time limits (CLI can't track wall time reliably). Instead: show progress ("Item 3 of 12") so reviewer self-regulates. The skip verdict is the "come back later" mechanism. Session handoff captures progress naturally (from requirements Out of Scope).

**Deliberately excluded:** Automatic checkpoints after N items, time-based interruptions, re-inspection triggers. These add complexity for marginal benefit in an interactive CLI context where the user controls pacing.

---

## Grounding Assessment

**Quality label:** Strong

**Evidence basis:**
- 4 established named frameworks with documented procedures (Fagan, IEEE 1028, Gerrit, Phabricator)
- Empirical research with sample sizes (Cisco: 2,500 reviews; Microsoft: 1.5M comments; LinearB: elite teams)
- Internal codebase has 7 review-adjacent patterns mapped to external analogs
- Dogfooding evidence from this project (brief.md) confirms 3 of the external findings independently

**Gap analysis:**
- No external framework combines per-item verdicts with modern interactive UX — this design fills that gap
- Cognitive load thresholds (200-400 LOC, 60-90 min) are for code review; artifact review rates may differ. No direct research found for document-item review rates.
- Fagan's re-inspection trigger (>5% rework) has no direct analog in the design. Could inform when to re-review after revisions, but not included (complexity cost).

**Searches performed:**
- "Fagan inspection" methodology process steps roles
- "IEEE 1028" software review standard
- GitHub pull request review UX patterns
- Gerrit code review workflow vote label
- Phabricator Differential inline comment review
- "code review checklist" structured inspection
- "cognitive load" code review effectiveness

---

## Sources

### Primary Sources (Framework Originators)

- **Fagan, M.E.** (1976). "Design and Code Inspections to Reduce Errors in Program Development." IBM Systems Journal, 15(3). Foundational structured inspection method. Retrieved via: Grokipedia, en-academic.com, ProfessionalQA, iSixSigma.
- **IEEE 1028-2008.** "Standard for Software Reviews and Audits." IEEE Standards Association. Five review types with procedures. Retrieved via: IEEE Xplore, Wikipedia.
- **Gerrit Code Review.** Label configuration and review mechanics. Retrieved via: gerrit-review.googlesource.com, Graphite guides.
- **Phabricator Differential.** Code review application with state machine. Retrieved via: secure.phabricator.com, Graphite guides, Mozilla documentation.

### Secondary Sources (Research, Summaries)

- **Cisco/SmartBear** (2006). Code review study (2,500 reviews). Cognitive load cliff at 450 LOC/hr, 200-400 LOC batch size. Retrieved via: Rishi Baldawa's analysis.
- **Springer** (2022). "Do explicit review strategies improve code review performance?" Checklist effectiveness, segmentation. Retrieved via: link.springer.com.
- **Springer** (2018). "Associating working memory capacity and code change ordering." Cognitive factors in review. Retrieved via: link.springer.com.
- **LinearB** (2025). Elite team PR size metrics (<219 LOC). Retrieved via: Rishi Baldawa's analysis.
- **Microsoft** (1.5M comment study). Proportion of useful review comments decreases with changeset size. Retrieved via: Rishi Baldawa's analysis.

### Internal Sources

- `plugin/skills/proof/SKILL.md` — reword-accumulate-sync protocol
- `plugin/agents/corrector.md` — severity taxonomy, status taxonomy, investigation gates
- `plugin/skills/deliverable-review/SKILL.md` — two-layer review, severity classification
- `plans/interactive-review/brief.md` — dogfooding feedback (presentation, research gap)
- `plans/interactive-review/requirements.md` — FR-1 through FR-7, constraints

### Branch Artifacts (Audit Evidence)

- `plans/reports/interactive-review-internal-codebase.md` — internal codebase exploration
- `plans/reports/interactive-review-external-research.md` — external framework research
