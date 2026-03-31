# README / Documentation Skill Research

Research conducted during edify README rewrite session.

## Sources Evaluated

### Anthropic `doc-coauthoring` (best)
- **Source:** https://github.com/anthropics/skills/blob/main/skills/doc-coauthoring/SKILL.md
- 3-stage workflow: Context Gathering → Refinement & Structure → Reader Testing
- **Reader Testing (steal this):** Spawn fresh sub-agent with zero prior context, feed it
  only the finished document, ask predicted reader questions. If fresh-Claude
  misinterprets, the doc has gaps. Works via Task tool in Claude Code.
- Section-by-section brainstorming → curation → drafting loop (overkill for READMEs)
- Context gathering stage redundant when you already know the project

### ComposioHQ `content-research-writer`
- **Source:** https://github.com/ComposioHQ/awesome-claude-skills/blob/master/content-research-writer/SKILL.md
- Research + citations, hook improvement, voice preservation
- Voice preservation implementation is thin: "read samples, ask 'does this sound like you?'"
- No actual style extraction or modeling — corpus as direct reference is sufficient

### `readme-ai` (eli64s)
- **Source:** https://github.com/eli64s/readme-ai
- Standalone Python CLI, not a Claude skill
- Analyzes codebases, generates READMEs via multiple LLM backends
- Templates, badges, SEO — more about generation than quality

### Skill Directories
- https://github.com/anthropics/skills — official Anthropic skills
- https://github.com/ComposioHQ/awesome-claude-skills — community curated
- https://github.com/VoltAgent/awesome-agent-skills — 300+ cross-platform
- https://awesome-skills.com/ — visual marketplace
- https://github.com/daymade/claude-code-skills — production-ready skills

## Techniques Worth Reusing

### 1. Reader Testing (from doc-coauthoring)
Spawn a Task agent with ONLY the document content. Ask 5-10 predicted reader
questions. Check what the agent understood, what was unclear, what it guessed.
Fix gaps identified. One Task call at the end of writing, not a dependency.

**Implementation:** Single Task call with prompt containing the document text
and numbered questions. Agent returns per-question assessment.

### 2. Style Corpus as Direct Reference
Load writing samples into context as reference material. No extraction step
needed — the model matches voice from examples without explicit style rules.

**Implementation:** Keep corpus file (e.g., `tmp/STYLE_CORPUS.md`), reference it
in the writing prompt. Works for any content type.

### 3. Motivation-First Opening
Reader test consistently flagged feature-list openers as insufficient. Lead with
the problem being solved, not a list of capabilities. "X stores Y but gives you
no tools" beats "toolset for X that does A, B, C."

## What NOT to Reuse

- Full doc-coauthoring workflow — too heavy for READMEs/project docs
- Voice preservation skill machinery — corpus reference is sufficient
- Section-by-section brainstorm/curate/draft loop — overkill except for long specs
- Plugin dependencies on external skill repos — patterns are simple enough to inline

## Session Application

Applied to edify README rewrite:
- Reader-tested with 9 questions, fixed 6 gaps
- Style-matched to `tmp/STYLE_CORPUS.md` corpus
- Motivation opener: "Claude Code stores conversations as JSONL, but gives you
  no tools to work with them"
- Result: 261-line stale doc → 214-line comprehensive README
