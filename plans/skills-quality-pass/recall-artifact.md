# Recall Artifact: Skills Quality Pass

## How to Prevent Skill Steps From Being Skipped

**Source:** `agents/decisions/implementation-notes.md`
**Relevance:** Core pattern being applied — D+B hybrid anchors every skill step with a tool call.

Every skill step must open with a concrete tool call (Read/Bash/Glob). Prose-only judgment steps are a structural anti-pattern. Fix: merge gate into adjacent action step, anchor with tool call, explicit control flow with if/then branch targets.

## When Placing DO NOT Rules In Skills

**Source:** `agents/decisions/implementation-notes.md`
**Relevance:** Negative constraints must be co-located with positive content guidance, not deferred to cleanup phases.

Place "don't write X" rules alongside instructions for WHAT to produce, where decisions are made. By cleanup phase, the violation is already written.

## When Selecting Model For Prose Artifact Edits

**Source:** `agents/decisions/pipeline-contracts.md`
**Relevance:** All edits in this task are to LLM-consumed instruction files — opus required.

Skills, fragments, agent definitions, design documents → opus. Code implementation, test writing → model by complexity. Mechanical execution → haiku.

## When Refactoring Agents Need Quality Directives

**Source:** `agents/decisions/operational-practices.md`
**Relevance:** Deslop factorization must be explicit in refactor prompts.

Include explicit code quality and factorization directives in refactor prompts. Refactor agents focus on warnings, don't proactively optimize for token efficiency.

## When Loading Context Before Skill Edits

**Source:** `agents/decisions/operational-practices.md`
**Relevance:** Load skill-development guide before editing any skill file.

Load `/plugin-dev:skill-development` before editing any skill file. Guide mandates "This skill should be used when..." third-person with trigger phrases. H1 heading is what Claude Code displays in skill picker.

## How to Make Skills Discoverable

**Source:** `agents/decisions/project-config.md`
**Relevance:** Description field is one of 4 discovery layers — quality directly impacts skill activation.

Skills require 4 discovery layers: (1) CLAUDE.md fragment, (2) path-triggered rules, (3) in-workflow reminders, (4) directive skill description. Internal docs invisible until invoked.

## When Formatting Rules For Adherence

**Source:** `agents/decisions/prompt-structure-research.md`
**Relevance:** Bullet points outperform prose for discrete task adherence — informs deslop direction.

Discrete rules → bullets. Connected concepts → prose paragraphs. Critical rules → visually salient markers. Examples → code blocks.

## When Writing Rules For Different Models

**Source:** `agents/decisions/prompt-structure-research.md`
**Relevance:** Skills consumed by haiku need explicit steps and markers; opus skills can trust inference.

Opus: concise prose, trust inference. Sonnet: clear bullets with context. Haiku: explicit steps, markers, DO NOT examples.

## When Designing Quality Gates

**Source:** `agents/decisions/defense-in-depth.md`
**Relevance:** D+B is Layer 1 (outer defense) — ensures gates execute via tool call, not skipped as prose.

Layer 1 (D+B): execution flow defense. Layer 2: automated precommit checks. Layer 3: semantic review. Layer 4: conformance tests. Each layer prevents different failure modes.

## When Bootstrapping Self-Referential Improvements

**Source:** `agents/decisions/workflow-planning.md`
**Relevance:** Fix corrector agents before skills that delegate to them — ordering constraint.

Apply each improvement before using that tool in subsequent steps. Phase ordering follows tool-usage dependency graph, not logical grouping.

## Design Skill Fast Path Regression

**Source:** Session discussion (2026-02-25), prior deslop pass evidence
**Relevance:** Critical review constraint — verify control flow AND user reporting after restructuring.

Previous deslop pass on design skill combined two fast paths, causing regression in user-visible messages. When restructuring conditional branches: enumerate all paths before editing, verify each path's user-visible output after.

## When Reviewing Skill Deliverable

**Source:** `agents/decisions/pipeline-contracts.md`
**Relevance:** Skill review needs cross-project context (other skills' patterns, fragment conventions).

Route to skill-reviewer agent or review interactively. Delegated agents lack cross-project context needed to compare against project-wide patterns.
