# UserPromptSubmit Hook Exploration

## Summary

The UserPromptSubmit hook is implemented as a Python script (`userpromptsubmit-shortcuts.py`) that expands workflow shortcuts and manages skill continuation chains. It operates in three tiers: command shortcuts (exact match), directive shortcuts (colon prefix), and continuation parsing for multi-skill chains. The hook provides no state tracking between invocations—it is stateless and deterministic.

## Key Findings

### 1. Hook Location and Configuration

**Main hook script:**
- `/Users/david/code/claudeutils-wt/pushback/agent-core/hooks/userpromptsubmit-shortcuts.py`
- Also symlinked to: `/Users/david/code/claudeutils-wt/pushback/.claude/hooks/userpromptsubmit-shortcuts.py`

**Hook registration (`.claude/settings.json`):**
```json
"UserPromptSubmit": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 $CLAUDE_PROJECT_DIR/agent-core/hooks/userpromptsubmit-shortcuts.py",
        "timeout": 5
      }
    ]
  }
]
```

**Key properties:**
- No `matcher` defined (fires on every prompt)
- Timeout: 5 seconds
- No state file or persistence mechanism

### 2. Shortcut Detection Mechanism

Hook operates in three tiers of increasing complexity:

#### Tier 1: Command Shortcuts (Exact Match)

Entire message must match one key exactly. Defined in `COMMANDS` dict (lines 29-57):

| Input | Expansion Output |
|-------|------------------|
| `s` | `[SHORTCUT: #status]` directive |
| `x` | `[SHORTCUT: #execute]` directive |
| `xc` | `[SHORTCUT: #execute --commit]` directive |
| `r` | `[SHORTCUT: #resume]` directive |
| `h` | `[SHORTCUT: /handoff]` directive |
| `hc` | `[SHORTCUT: /handoff --commit]` directive |
| `ci` | `[SHORTCUT: /commit]` directive |
| `?` | `[SHORTCUT: #help]` directive |

**Detection logic (lines 640-650):**
```python
if prompt in COMMANDS:
    expansion = COMMANDS[prompt]
    output = {
        'hookSpecificOutput': {
            'hookEventName': 'UserPromptSubmit',
            'additionalContext': expansion
        },
        'systemMessage': expansion
    }
    print(json.dumps(output))
    return
```

#### Tier 2: Directive Shortcuts (Colon Prefix)

Pattern: `<directive>: <arguments>`
Defined in `DIRECTIVES` dict (lines 60-72):

| Input Pattern | Name | Expansion |
|---------------|------|-----------|
| `d: <text>` | DISCUSS | `[DIRECTIVE: DISCUSS]` + "do not execute" instruction |
| `p: <text>` | PENDING | `[DIRECTIVE: PENDING]` + "append to session.md" instruction |

**Detection logic (lines 652-666):**
```python
match = re.match(r'^(\w+):\s+(.+)', prompt)
if match:
    directive_key = match.group(1)
    if directive_key in DIRECTIVES:
        expansion = DIRECTIVES[directive_key]
        # ... inject as additionalContext and systemMessage
```

Note: The text after colon is captured but NOT passed through the injection—only the directive instruction is sent.

#### Tier 3: Continuation Parsing

Activated when multiple skill references detected (lines 668-686):

**Conditions for activation:**
- Two or more `/skill` references in prompt (line 482)
- Each skill is in the registry (built dynamically from SKILL.md files)
- Single skill invocations pass through silently (Claude handles them)

**Registry building (lines 263-363):**
- Scans `.claude/skills/` for `SKILL.md` files
- Scans enabled plugin skills
- Extracts `continuation.cooperative: true` from YAML frontmatter
- Caches registry in `$TMPDIR/continuation-registry-<hash>.json`
- Cache invalidated if any source file modified (line 231)

**Skill reference detection (lines 432-462):**
```python
def find_skill_references(prompt: str, registry: Dict[str, Dict[str, Any]]) -> List[tuple]:
    references = []
    for match in re.finditer(r'/(\w+)', prompt):
        skill_name = match.group(1)
        if skill_name not in registry:
            continue
        pos = match.start()
        if _should_exclude_reference(prompt, pos, skill_name):
            continue
        references.append((pos, skill_name, match.end()))
    return references
```

**Continuation patterns supported (two modes):**

**Mode 3 - Multi-line list:** (lines 489-522)
```
/skill1 args
and
- /skill2 args
- /skill3 args
```

**Mode 2 - Inline prose:** (lines 524-569)
```
/skill1 args, /skill2 args and /skill3 args
```

Delimiters recognized: `, /`, ` and /`, ` then /`, ` finally /`

### 3. Context Injection via additionalContext

Hook outputs to Claude in two channels:

**Output structure (lines 641-666):**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "<injected text>"
  },
  "systemMessage": "<same text>"
}
```

**Injection content by tier:**

**Tier 1 (Commands):**
Example for `s`:
```
[SHORTCUT: #status] List pending tasks with metadata from session.md.
Display in STATUS format. Wait for instruction.
```

**Tier 2 (Directives):**
Example for `d:`:
```
[DIRECTIVE: DISCUSS] Discussion mode. Analyze and discuss only —
do not execute, implement, or invoke workflow skills.
The user's topic follows in their message.
```

**Tier 3 (Continuation):**
Formatted by `format_continuation_context()` (lines 572-630):
```
[CONTINUATION-PASSING]
Current: /design <args>
Continuation: /handoff --commit, /commit

After completing the current skill, invoke the NEXT continuation entry via Skill tool:
  Skill(skill: "handoff", args: "--commit [CONTINUATION: /commit]")

Do NOT include continuation metadata in Task tool prompts.
```

### 4. Extension Pattern

To add new shortcuts, modify the appropriate dictionary:

#### Adding Tier 1 Command (e.g., `wt` for worktree setup):

Edit `COMMANDS` dict (lines 29-57):
```python
COMMANDS = {
    # ... existing ...
    'wt': (
        '[SHORTCUT: wt] Set up git worktrees for parallel execution. '
        'Invoke `/worktree-setup` skill.'
    )
}
```

The hook then:
1. Matches entire message `wt`
2. Injects expansion as additionalContext + systemMessage
3. Claude reads injected instruction and invokes the skill

#### Adding Tier 2 Directive (e.g., `note:` for meta-notes):

Edit `DIRECTIVES` dict (lines 60-72):
```python
DIRECTIVES = {
    # ... existing ...
    'note': (
        '[DIRECTIVE: NOTE] Record a note for context recovery. '
        'Do not process it as a task.'
    )
}
```

Detection remains automatic via regex `^(\w+):\s+(.+)`.

#### Adding Skill to Continuation Registry:

Create `SKILL.md` with YAML frontmatter in `.claude/skills/<skill-name>/`:
```yaml
---
name: skill-name
continuation:
  cooperative: true
  default-exit: ["/handoff --commit", "/commit"]
---
```

Registry builder (line 318-336) automatically:
1. Scans for the file
2. Extracts frontmatter
3. Checks `continuation.cooperative`
4. Adds to registry if true
5. Caches the registry

### 5. State Tracking Between Invocations

**No persistent state tracking exists.** Hook is stateless and deterministic:

**Why stateless design:**
- Hooks fire on EVERY prompt (line 409: "fires on every prompt, no matcher")
- No session scope or agent context preservation across invocations
- Each invocation is independent—same input produces same output
- Cache is ONLY for skill registry, not user state

**Cache details (lines 177-261):**
- Path: `$TMPDIR/continuation-registry-<sha256-hash-of-paths>.json`
- Content: Skill registry (metadata, not user context)
- Invalidation: File modification timestamp (checked at line 231)
- Fallback: Graceful degradation to uncached operation if save fails (line 259)

**Consequence for conversation history:**
- Hook cannot detect "same user as last invocation" or "previous shortcut was X"
- Each shortcut expansion is independent
- State is carried via Claude's context (session.md references, prior messages)
- Hook's role is MECHANICAL expansion only

### 6. Discussion Mode Detection (`d:`)

**Current implementation:**
- Directive defined in `DIRECTIVES` dict (lines 61-65)
- Pattern: `d: <text>` (colon prefix)
- Detection: Regex match `^(\w+):\s+(.+)` → directive_key = "d" → found in DIRECTIVES
- Injection: "[DIRECTIVE: DISCUSS] ... do not execute, implement, or invoke workflow skills."

**Limitation:**
- Only the instruction is injected, NOT the user's text
- User must still type their discussion topic AFTER the directive marker
- Hook does NOT capture the text argument—regex match discards it (line 655)

**No ambient detection:**
- Hook does NOT infer discussion intent from natural language
- No pattern matching on "thoughts on", "what if", "analyze" without explicit `d:` prefix
- Pure marker-based approach

## Patterns and Conventions

### Naming
- Command shortcuts: Single letters or letter pairs (`s`, `x`, `xc`, `r`, `h`, `hc`, `ci`, `?`)
- Directive prefixes: Single letters with colon (`d:`, `p:`)
- Skill names in registry: Underscores only (regex `/(\w+)` doesn't match hyphens, line 4 comment in test file)

### Output Format
- Both `additionalContext` and `systemMessage` populated with same text (dual channel)
- Prefix pattern: `[SHORTCUT: ...]` or `[DIRECTIVE: ...]` for visibility
- Actual instructions follow the marker

### Registry Caching
- Hash-based path: Deterministic, survives hook restarts
- File modification detection: Ensures cache freshness
- Graceful failure: Continues without cache if save fails

### Multi-skill Continuation
- Skill must have `continuation.cooperative: true` in frontmatter
- Default-exit chain stored per skill (for potential future use)
- Continuation context INCLUDES metadata to guide next skill invocation
- "Do NOT include continuation metadata in Task tool prompts" (line 621) — prevents recursion

## Gaps and Unresolved

### Q1: Can `d:` detect partial text?
Current implementation requires full `d: <text>` pattern. Regex `^(\w+):\s+(.+)` would fail on `d:` alone (no text after colon). Not tested.

### Q2: How does hook behave with ambient context injection?
Hook outputs both `additionalContext` (injected) and `systemMessage` (visible to user). Scope of visibility unclear—does user see systemMessage in transcript?

### Q3: Recovery from malformed skill frontmatter
If YAML parsing fails (line 104), file is skipped silently. No error logging—operators may not notice corrupted SKILL.md files.

### Q4: Continuation parsing with path arguments
Hook excludes `/path-like/` patterns (line 421-422) but `/skill-name` with hyphens in skill name will NOT be detected (regex limitation). Workaround: use underscores in skill names.

### Q5: Extension point for custom directives?
Design supports adding new directives easily to `DIRECTIVES` dict, but no mechanism to inject directives from plugins or project-local sources. All directives are hardcoded in hook script.

## Files Reference

| File | Lines | Purpose |
|------|-------|---------|
| `/Users/david/code/claudeutils-wt/pushback/agent-core/hooks/userpromptsubmit-shortcuts.py` | 1-693 | Main hook implementation |
| `/Users/david/code/claudeutils-wt/pushback/.claude/hooks/userpromptsubmit-shortcuts.py` | Symlink | Project-local reference |
| `/Users/david/code/claudeutils-wt/pushback/.claude/settings.json` | 67-77 | Hook registration |
| `/Users/david/code/claudeutils-wt/pushback/agent-core/docs/shortcuts.md` | 1-59 | User-facing reference |
| `/Users/david/code/claudeutils-wt/pushback/tests/test_continuation_parser.py` | Full | Continuation parsing tests |

## Code Snippets for Extension

### Adding a new Tier 1 command:
```python
# In COMMANDS dict (lines 29-57)
'wt': (
    '[SHORTCUT: wt] Create git worktrees. '
    'Invokes /worktree-setup skill.'
),
```

### Adding a new Tier 2 directive:
```python
# In DIRECTIVES dict (lines 60-72)
'note': (
    '[DIRECTIVE: NOTE] Record a meta-note. '
    'Do not execute or process as task.'
),
```

### Adding a cooperative skill:
```yaml
# In .claude/skills/my-skill/SKILL.md frontmatter
---
name: my-skill
continuation:
  cooperative: true
  default-exit: ["/handoff --commit"]
---
```

Then hook automatically discovers it on next invocation (cache cleared when file added).
