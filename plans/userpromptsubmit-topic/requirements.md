# UserPromptSubmit Topic Injection

## Requirements

### Functional Requirements

**FR-1: Parse memory-index into keyword lookup table**
Build a keyword lookup structure from `agents/memory-index.md` trigger phrases. Each entry maps extracted keywords to the entry's trigger phrase and source decision file. Reuse existing infrastructure: `src/claudeutils/recall/index_parser.py` provides `_extract_keywords()` (tokenization + stopword removal) and `parse_memory_index()` returning `IndexEntry` with `keywords: set[str]`.

Acceptance criteria:
- Parses all 200+ memory-index entries into keyword-indexed structure
- Keywords extracted from trigger phrase AND pipe-delimited extras (e.g., `/when hook commands use relative paths | cwd drift non-blocking error CLAUDE_PROJECT_DIR absolute`)
- Structure supports fast keyword-to-entries lookup (inverted index: keyword → list of entries)

**FR-2: Match user prompt against keyword table**
Tokenize user prompt text, match tokens against keyword lookup table, rank entries by match quality. Score reflects how many of an entry's keywords appear in the prompt.

Acceptance criteria:
- Tokenizes prompt using same rules as `_extract_keywords()` (stopword removal, lowercase, punctuation split)
- Produces ranked list of matching entries sorted by relevance score
- Entries with zero keyword overlap excluded
- Matching operates on the full prompt text (not just first line)

**FR-3: Resolve and inject matched entry content via additionalContext**
For top-ranked matches, resolve the decision section content and inject via `additionalContext` (agent-only channel — no user output). Content is the full decision section text from the referenced decision file.

Acceptance criteria:
- Resolves entry trigger to decision file section content (reuse resolver infrastructure from `src/claudeutils/when/resolver.py`)
- Injects via `additionalContext` in UserPromptSubmit hook output
- Resolution failures (missing file, missing section) silently skip — no error output, no hook failure
- Injected content includes entry heading and source file for agent provenance

**FR-4: Cache keyword table for performance**
Cache the parsed keyword table between hook invocations. Invalidate when `agents/memory-index.md` is modified (mtime check). Follow existing caching pattern from continuation registry in `userpromptsubmit-shortcuts.py`.

Acceptance criteria:
- Cache stored in `$TMPDIR` (sandbox-compatible)
- Cache invalidated on source file modification (mtime comparison)
- Cold build (cache miss) completes within hook timeout budget
- Cache hit path avoids re-parsing and re-indexing

**FR-5: Integrate as new tier in existing UserPromptSubmit hook**
Add topic matching as a new tier in `agent-core/hooks/userpromptsubmit-shortcuts.py`. Additive with existing tiers — topic injection combines with Tier 2.5 pattern guards and Tier 3 continuation parsing. Dual-channel output: `additionalContext` for agent, `systemMessage` for user transparency.

Acceptance criteria:
- Fires after Tier 2 directives (directives change interaction mode — topic injection not appropriate on `d:` or `p:` prompts that already have custom behavior)
- Additive with Tier 2.5 and Tier 3 (combined via `context_parts` and `system_parts` lists)
- Silent pass-through when no entries match (no output, exit 0)
- Does not fire on Tier 1 exact-match commands (s, x, r, etc. — already return early)

**FR-7: User-visible match feedback via systemMessage**
Show matched memory-index lines in `systemMessage` so the user can audit what context the agent received. Follows the established pattern: Tier 2 shows directive summaries, Tier 2.5 shows guard triggers.

Acceptance criteria:
- `systemMessage` contains full memory-index trigger lines (trigger phrase + pipe-delimited extras)
- Multiple matches newline-separated
- Header includes injected content line count: `"topic (N lines):"`
- Extras preserved — they show keyword overlap explaining *why* the match fired
- `/when` or `/how` prefix stripped (redundant for user display)

**FR-6: Token budget control**
Limit total injected content to prevent context bloat. Match threshold and token cap are design-phase decisions requiring empirical measurement — requirements capture the constraint, not the threshold.

Acceptance criteria:
- Total injection bounded by a configurable cap (token count or entry count)
- Cap prevents adherence degradation from excessive context (reference: ~150 user rule budget before degradation)
- When matches exceed cap, highest-ranked entries win

### Non-Functional Requirements

**NFR-1: Hook execution within 5s timeout**
UserPromptSubmit hooks have a 5s timeout (configured in settings.json). Topic matching must complete within this budget, shared with existing tiers (Tier 1-3 already consume some budget).

**NFR-2: No degradation of existing hook behavior**
Adding topic matching must not break or slow existing shortcut expansion, directive handling, pattern guards, or continuation parsing.

### Constraints

**C-1: Single hook script architecture**
UserPromptSubmit fires a single hook command. Topic matching integrates into `userpromptsubmit-shortcuts.py`, not as a separate hook (Claude Code runs hooks serially — separate script would add latency and complicate output merging).

**C-2: Dual-channel output matching existing tier pattern**
All existing tiers (Tier 2 directives, Tier 2.5 pattern guards, Tier 3 continuations) use both `additionalContext` (agent) and `systemMessage` (user). Topic injection follows the same pattern:
- `additionalContext`: resolved decision section content (agent-only)
- `systemMessage`: full matched memory-index lines (trigger + pipe extras), newline-separated, with injected line count header. Extras show *why* the entry matched (keyword overlap), not just *which* entry matched.
- No `permissionDecision` — this is advisory, not blocking
- Token count replaces line count when token count caching infrastructure lands

**C-3: Match threshold deferred to design**
Matching threshold (how many entries to inject, minimum score cutoff) is a design-phase decision. No-confabulation rule: thresholds require empirical data, not invented heuristics. Requirements specify the mechanism, design specifies the calibration.

### Out of Scope

- Sub-agent recall injection — hooks don't fire in sub-agents (separate mechanism needed)
- Memory-index generation/maintenance — separate task ("Generate memory index")
- Deep recall pipeline integration — `/recall` skill handles multi-pass saturation; this is the cheap first layer
- Replacement of `/recall` — complementary, not competitive. `/recall` does deep saturation; hook does ambient injection
- Decision file content authoring — the hook consumes existing content, doesn't create it

### Dependencies

- `src/claudeutils/recall/index_parser.py` — keyword extraction and index parsing
- `src/claudeutils/when/resolver.py` — section resolution from decision files
- `agents/memory-index.md` — source data (200+ entries, ~5k tokens)
- `agent-core/hooks/userpromptsubmit-shortcuts.py` — integration target

### Open Questions

- Q-1: Should topic injection fire on multi-line prompts containing code blocks? Code block content might produce false-positive keyword matches. The existing `is_line_in_fence()` utility could filter fenced content.
- Q-2: How should matches interact with Tier 2.5 pattern guards that already inject domain-specific context? If CCG_PATTERN fires AND topic matching finds hook-related entries, is that redundant or reinforcing?

### References

- `plans/reports/prioritization-2026-02-27.md` — WSJF score 2.4, CRR=8 ("highest-impact recall improvement")
- `plans/reports/recall-pass-internal-brainstorm.md` — open question on hook/recall complementarity
- `agents/decisions/operational-practices.md` — "evaluating recall system effectiveness" (4.1% voluntary, forced injection bypasses recognition)
- `agents/decisions/hook-patterns.md` — UserPromptSubmit filtering, output channel mapping

### Skill Dependencies (for /design)

- Load `plugin-dev:hook-development` before design (hook modification in FR-5)

### Design Research Notes

- **Ground scoring algorithm during A.1** — `/ground` FR-2's keyword matching approach (keyword overlap vs TF-IDF vs BM25). 5s timeout constraint and "cheap first layer" goal may favor simple approaches, but grounding validates this rather than assuming it. Existing `_extract_keywords()` provides a starting point, not a ceiling.
