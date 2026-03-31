# Runbook Outline: Agentic Programming Retrospective

## Requirements Mapping

| Requirement | Phase |
|-------------|-------|
| FR-1: Git history evolution tracing | Phase 2 (per-topic) |
| FR-2: Session log scraping for pivotal conversations | Phase 1 (extensions) + Phase 2 (per-topic) |
| FR-3: Five topic evolution narratives | Phase 2 (per-topic assembly) |
| FR-4: Cross-topic connection mapping | Phase 3 |
| NFR-1: Evidence-grounded | All phases (commit hashes, session IDs in all output) |
| NFR-2: Blog-ready excerpts | Phase 2 (excerpt extraction per topic) |
| C-1: Use existing session-scraper prototype | Phase 1 (extend), Phase 2 (use) |
| C-2: Output to plans/retrospective/reports/ | All phases |

## Key Decisions

- Session-scraper extensions are exploration-weight (prototype, no tests, general steps)
- Per-topic evidence gathering combines FR-1 + FR-2 + FR-3 into single per-topic steps (avoids artificial phase boundaries)
- 5 topics are independent — parallel execution in Phase 2
- Git history tracing uses git log -S with topic-specific key terms per requirements
- Session scraping uses scan (all projects) + parse/tree for topic-relevant project directories
- Cross-topic mapping (Phase 3) depends on all Phase 2 outputs

## Phase Structure

### Phase 1: Session-scraper extensions (type: general)

Prerequisite: Assess prototype gaps against FR-1/FR-2 needs. The prototype has scan/parse/tree/correlate but lacks content-based search across sessions and excerpt extraction.

- Step 1.1: Assess scraper capabilities against requirements
  - Run each scraper stage against a topic-relevant project directory (e.g., pushback, 29 sessions)
  - Document what works, what's missing, what needs extension
  - Output: `plans/retrospective/reports/scraper-assessment.md`

- Step 1.2: Implement content search extension
  - Add `search` command: given a list of project directories and keyword list, find sessions containing those keywords
  - Returns session IDs + project dirs + matching entry refs for downstream parse/tree
  - Exploration artifact: modify `plans/prototypes/session-scraper.py`

- Step 1.3: Implement excerpt extraction extension
  - Add `excerpt` command: given session ID + project dir + entry ref(s), extract conversation window (N entries before/after) as markdown
  - Trims to relevant exchange per NFR-2
  - Exploration artifact: modify `plans/prototypes/session-scraper.py`

- Step 1.4: Verify extensions against one topic
  - Run search + excerpt pipeline against pushback topic (29 sessions, well-defined keywords)
  - Validate output format matches FR-2 acceptance criteria
  - Output: `plans/retrospective/reports/extension-validation.md`

### Phase 2: Per-topic evidence gathering (type: general)

5 parallel steps — one per topic. Each step combines FR-1 (git history), FR-2 (session excerpts), and FR-3 (evidence bundle assembly).

- Step 2.1: Memory system evolution
  - Git: `git log -S` for "memory-index", "recall", "when_trigger", "metacognitive"
  - Git: `git log --follow` on `agents/memory-index.md`, `plugin/skills/recall/`
  - Sessions: Project dirs `memory-index-recall` (16), `when-recall` (24), `recall-tool-anchoring` (12), `active-recall-system` (14), `recall-cli-integration` (9), `recall-tool-consolidation` (3), `recall-pass-requirements` (8), `recall-fix` (1), `runbook-recall-expansion` (4), `review-recall-null` (1), `when-recall-evaluation` (1)
  - Key inflection: 4.1% metacognitive activation rate discovery
  - Output: `plans/retrospective/reports/topic-1-memory-system.md`

- Step 2.2: Pushback protocol
  - Git: `git log -S` for "pushback", "sycophancy", "agreement_momentum", "stress-test"
  - Git: `git log --follow` on `plugin/fragments/pushback.md`
  - Sessions: Project dirs `pushback` (29), `pushback-grounding` (1)
  - Key inflection: prose rules rationalized past → structural enforcement
  - Output: `plans/retrospective/reports/topic-2-pushback.md`

- Step 2.3: Deliverable-review origins
  - Git: `git log -S` for "deliverable-review", "statusline-parity", "ISO 25010", "IEEE 1012"
  - Git: `git log --follow` on `plugin/skills/deliverable-review/`, `agents/decisions/deliverable-review.md`
  - Sessions: Project dirs `parity-failures` (7), `quality-infra-reform` (13), `design-quality-gates` (1)
  - Key inflection: 385 tests pass, 8 visual issues remain (statusline-parity)
  - Output: `plans/retrospective/reports/topic-3-deliverable-review.md`

- Step 2.4: Ground skill origins
  - Git: `git log -S` for "ground", "confabulated", "WSJF", "diverge-converge"
  - Git: `git log --follow` on `plugin/skills/ground/`, `agents/decisions/workflow-optimization.md`
  - Sessions: Project dirs `design-grounding-update` (11), `update-grounding-skill` (1)
  - Key inflection: confabulated prioritization scoring caught → external research mandate
  - Output: `plans/retrospective/reports/topic-4-ground-skill.md`

- Step 2.5: Structural enforcement / gating
  - Git: `git log -S` for "D+B", "tool-call anchor", "PreToolUse", "gate_anchor", "structural enforcement"
  - Git: `git log --follow` on `plugin/fragments/pushback.md`, `agents/decisions/defense-in-depth.md`
  - Sessions: Project dirs `recall-tool-anchoring` (12), `userpromptsubmit-topic` (7), `ups-topic-injection` (8 → mapped to project dir), `fix-ups-topic-findings` (1), `rm-ups-topic` (1)
  - Key inflection: prose instructions skipped under momentum → tool-call anchoring
  - Output: `plans/retrospective/reports/topic-5-structural-enforcement.md`

### Phase 3: Cross-topic connection mapping (type: general)

Depends on: all Phase 2 steps complete.

- Step 3.1: Cross-topic connections — FR-4
  - Read all 5 topic reports
  - Identify commits/sessions touching multiple topics (git hash intersection)
  - Map shared failure patterns across topics
  - Map chronological co-evolution (parallel timelines)
  - Output: `plans/retrospective/reports/cross-topic-connections.md`

## Execution Model

**Agents:**
- `retrospective-scraper-task`: Sonnet agent for Phase 1 (scraper extensions). Context: session-scraper.py source, requirements FR-1/FR-2, exploration conventions.
- `retrospective-topic-task`: Sonnet agent for Phase 2 steps (per-topic evidence gathering). Context: requirements, extended scraper tools, topic-specific search terms and project directories.
- `retrospective-synthesis-task`: Sonnet agent for Phase 3 (cross-topic). Context: all 5 topic reports, FR-4, NFR-1.

**Dispatch protocol:**
1. Phase 1: Sequential steps 1.1-1.4 via `retrospective-scraper-task`
2. Phase 2: 5 parallel tasks via `retrospective-topic-task` (one per topic)
3. Phase 3: Sequential step 3.1 via `retrospective-synthesis-task` (after all Phase 2 complete)

**Recall injection:**
- Resolve all entries from `plans/retrospective/recall-artifact.md` in each agent prompt
- Per-topic agents also get topic-specific recall entries (memory decisions for topic 1, pushback decisions for topic 2, etc.)

**Checkpoints:**
- After Phase 1: Verify scraper extensions work (step 1.4 validation report)
- After Phase 2: Verify all 5 topic reports exist with required structure (git timeline + session excerpts + evidence bundle)
- After Phase 3: Verify cross-reference document links back to topic reports with commit/session evidence

**Model:** Sonnet for all phases (investigation/exploration work, no architectural decisions).

**Report locations:** `plans/retrospective/reports/`

**Success criteria:** Each of 5 topics has evidence bundle (FR-3 acceptance criteria) + cross-reference document (FR-4 acceptance criteria). Every claim links to commit hash or session ID (NFR-1).

## Expansion Guidance

- Phase 1 steps are sequential — each depends on prior. Step 1.1 assessment informs 1.2-1.3 implementation scope. If assessment shows existing tools are sufficient (no extensions needed), skip steps 1.2-1.3.
- Phase 2 steps are identical in structure, varying only in topic-specific parameters (search terms, project directories, key inflections). Template one step, parametrize the rest.
- Phase 3 is a single synthesis step — no expansion needed.
- All output is markdown to `plans/retrospective/reports/` per C-2.
