# Formats and Exit

Every shape this skill writes, and every way it leaves the user. Read once, at
the Recall Pass — the recall artifact is written there, and the rest is needed
by steps 3, 4 and 6 of whichever mode procedure is running.

## Recall Artifact

After recall completes, write `plans/<job>/recall-artifact.md`. File paths only
— downstream consumers Read them fresh at consumption time, so the artifact
never goes stale.

The artifact carries planning-stage **curation** into execution. Subagents do
receive the memory index, but nothing is fetched for them automatically —
auto-recall does not run below the main session. The artifact records which
files the planner judged relevant, so no downstream agent has to re-derive that
selection, and it covers corpora the index does not reach.

**Format:**

```markdown
# Recall Artifact: <Job Name>

Read each file listed below — do not rely on inline summaries.

## Entries

memory/<name>.md — <1-line relevance note>
```

**Null artifact (nothing relevant):** Write `null — no relevant entries found`
as the sole entry. Downstream consumers still Read the artifact and find the
null marker, so the gate is anchored without consumer-side empty-section
handling. Augmenting consumers (/design A.1, /runbook §1 Recall and Discovery)
remove the null entry when adding real ones.

**Selection criteria:** Include files that informed requirements or constrain
implementation. Exclude files read but proved irrelevant — the artifact is
curated, not exhaustive.

**Output:** `plans/<job>/recall-artifact.md`

## Gap-Fill Questions

Ask inline, as numbered prose in a single turn. Each question carries a
**proposed answer** drawn from the job name and the conversation, so the user
corrects a draft rather than filling a blank — and silence on a question is
agreement with its proposal.

```
Three gaps in the requirements. Proposed answers below; correct the ones I got
wrong and I'll take the rest as agreed.

1. Functional — the validator parses hook scripts before commit, blocks the
   commit when one is malformed, and reports which hook failed and why.
2. Scope — hook scripts under `.git/hooks/` only; not the hooks Claude Code
   configures in settings.json.
3. Constraints — runs inside the commit path, so it must finish well under a
   second and must not need network.
```

## Standard Format

```markdown
# <Job Name>

## Requirements

### Functional Requirements
**FR-1: <requirement title>**
<description, acceptance criteria>

**FR-2: <requirement title>**
<description, acceptance criteria>

### Non-Functional Requirements
**NFR-1: <requirement title>**
<description>

### Constraints
**C-1: <constraint title>**
<rationale>

### Out of Scope
- <item> — <rationale>

### Dependencies
- <dependency> — <impact on implementation>

### Open Questions
- Q-1: <unresolved item — what needs investigation>

### References
- `plans/<job-name>/reports/explore-<topic>.md` — inherited from prior work;
  this skill does not produce one
- `plans/reports/<topic>-grounding.md` — grounding research synthesis
- [External Paper Title](url) — informed FR-2 scope decision
```

**Section rules:**
- Omit empty sections entirely (don't scaffold structure)
- Number identifiers sequentially within each section (FR-1, FR-2, ... not FR-1,
  FR-3)
- Open Questions captures items conversation didn't resolve → become Design
  Phase A research targets
- Dependencies flags blocking work, prerequisite plans, or external dependencies
- References track provenance — what research, external sources, or project
  artifacts informed the requirements. Include exploration reports, grounding
  research, external papers, prior plan reports. Omit if requirements came
  entirely from conversation.

## Skill Dependency Scanning

After writing artifact, scan requirements text for skill dependency indicators:

| Indicator | Skill to Flag |
|-----------|---------------|
| "sub-agent", "delegate to agent", "agent definition" | `plugin-dev:agent-development` |
| "skill", "invoke skill", "skill preloaded" | `plugin-dev:skill-development` |
| "hook", "PreToolUse", "PostToolUse" | `plugin-dev:hook-development` |
| "plugin", "MCP server" | `plugin-dev:plugin-structure` |

If indicators found, append to artifact:

```markdown
### Skill Dependencies (for /design)
- Load `plugin-dev:hook-development` before design (hooks mentioned in FR-2)
```

**Rationale:** Artifact-scoped scanning reduces A.0 scan time — planner reads
requirements.md first, loads indicated skills immediately rather than scanning
entire codebase.

## Default Exit

Present artifact path and suggest next step based on completeness:

```
Requirements written to: plans/<job>/requirements.md

Next steps (decision criteria):
- 0-2 open questions, all critical sections populated → `/design plans/<job>/`
- 3+ open questions or empty critical sections → stop here; revisit when clearer
- Very clear scope + simple → `/design plans/<job>/` (its triage routes small work straight to `/build`)
- User stated explicit next step → Use that path
```

**Workflow positioning:**
```
/requirements <job> → /design plans/<job>/ (seeds A.0)
/requirements <job> → /handoff:handoff (document intent for later)
/requirements <job> (standalone — capture intent, no immediate follow-up)
```

## STOP Conditions

The artifact is a planning input — `/design` and `/runbook` argue from it, and
`/proof` validates its content, not its preconditions. These conditions abort
before an artifact is written; a wrong or empty requirements.md is worse than
none, because downstream phases treat it as settled.

**STOP and report to the user when:**
- **Gap detection cannot reduce open questions below the count that blocks every
  exit path** (3+ open questions AND empty critical sections). Write what
  exists, mark the artifact incomplete in its header, and stop here rather than
  routing to `/design`.

**Failure handling:** these are user-decision points, not retries. Report the
condition, state what is missing, and wait. Do not fill a gap by inference —
that is the hallucination risk the do-not-infer rule names.

**Review:** `/requirements` has no corrector; `/proof` is the sole gate on
content. That places the burden of a careful read on the user, so do not present
an artifact as validated when it has only been written.
