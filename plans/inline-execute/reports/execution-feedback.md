# Execution Feedback: Triage Feedback Script

Feedback from first inline task execution, for skill design iteration.

## Issues Encountered

### 1. Hook false positive on path patterns in Task prompts

**pretooluse-recall-check.py** uses `re.search(r"plans/([^/]+)/", prompt)` to extract plan directory from Task prompts. It matches the FIRST occurrence, which may be:
- Template placeholders: `plans/<job>/`, `plans/$job/`
- Test fixture paths: `plans/testjob/reports/`
- Bash variable references in script specs

**Impact:** 4 blocked Task dispatches before workaround found.

**Workaround:** Ensure the real plan directory (`plans/inline-execute/`) appears first in the prompt, before any template paths.

**Fix needed:** Hook should match against `subagent_type`-aware heuristics or check ALL `plans/*/` matches, not just the first. Or: exempt test-fixture paths from the check.

### 2. Recall artifact word-splitting in shell

**tdd-recall-artifact.md** contains multi-word trigger phrases (one per line). The intended invocation `$(cat file)` splits on ALL whitespace, turning 10 phrases into ~60 individual words. Each word fuzzy-matches independently, producing massive duplicates and irrelevant entries.

**Impact:** Sub-agent would have received garbage context if not caught.

**Fix:** Use zsh array expansion to preserve line boundaries:
```zsh
triggers=("${(@f)$(< plans/inline-execute/tdd-recall-artifact.md)}") && agent-core/bin/when-resolve.py "${triggers[@]}"
```

**Pending task:** Fix when-resolve.py to accept recall-artifact on stdin and deduplicate fuzzy matches.

### 3. Sub-agent context isolation not internalized

**Three iterations** before correct pattern established:
1. First attempt: told agent "already resolved in parent context — do not re-resolve" (wrong — sub-agent has no parent context)
2. Second attempt: told agent to run when-resolve.py with specific entries (delegates recall judgment to execution agent)
3. Third attempt: created tdd-recall-artifact.md with mechanical invocation command (correct — no judgment, single command)

**Root cause:** Treating Task agents as context-sharing rather than context-isolated. The parent does cognitive work (selecting relevant entries); the child does mechanical work (resolving them into its own context).

### 4. Design artifact vs requirements artifact for sub-agents

Cycle 2 prompt told sub-agent to "read requirements.md." The outline (design document) has the actual script specification (D-2). Requirements are upstream abstractions. Sub-agents implementing a spec need the spec, not the requirements.

**Fix:** Reference `plans/inline-execute/outline.md` (design) in sub-agent prompts, not requirements.md.

### 5. Piecemeal cycle dispatch

First attempt sent all 7 cycles in a single prompt. Issues:
- Agent loses focus on later cycles
- Full prompt triggers hook false positives on embedded path patterns
- Context overloaded with spec not yet relevant

**Correct pattern:** One cycle per invocation. Resume same agent for subsequent cycles (preserves file reads + implementation context). Fresh agent when context nears 150k.

### 6. TDD agent commit behavior

Initially flagged agent commits as "unauthorized." This was wrong — TDD agents are expected to commit each cycle for audit trail. The per-cycle commit history (7 commits visible in `git log`) provides step-by-step traceability.

## Metrics

- **Cycles:** 7 (planned 5-7)
- **Tests:** 13 passing
- **Script:** 84 lines
- **Test file:** 581 lines (exceeds 400-line soft limit — corrector will flag)
- **Agent context usage:** ~84k tokens across all cycles (well under 150k limit)
- **Wall time:** Cycles 3-7 averaged ~60s each after pattern stabilized. Cycles 1-2 took longer due to iteration on dispatch pattern.
- **Blocked dispatches:** 4 (hook false positives)

## Recommendations for /inline skill design

1. **Recall artifact format:** Include the shell invocation command in the artifact itself (not just entry keys). The artifact should be self-documenting: `# Resolve: triggers=("${(@f)$(< THIS_FILE)}") && when-resolve.py "${triggers[@]}"`

2. **Hook tolerance:** The recall-check hook needs awareness of test-fixture paths vs real plan paths. Pattern: check if the matched directory actually exists on disk AND is a real plan directory (has outline.md or requirements.md).

3. **Sub-agent prompt template:** The /inline skill's corrector template (D-4) should specify "Read outline.md" not "Read requirements.md" for implementation context.

4. **Cycle dispatch protocol:** Document in the skill that TDD execution uses piecemeal dispatch with agent resume. Not a single-prompt pattern.
