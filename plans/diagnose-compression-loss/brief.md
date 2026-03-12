**⚠ UNREVIEWED — Agent-drafted from session.md task descriptions. Validate before design.**

# Diagnose Compression Loss

## Problem

Session handoff compression quality degraded at commit `0418cedb`. Handoff output became more verbose, less information-dense. Root cause unknown.

## Investigation Scope

- Diff commit `0418cedb` against its parent — identify what changed
- Check handoff skill, session.md format rules, prose quality fragments
- Determine if regression is in skill content, fragment content, or model behavior shift
- Assess whether the change was intentional (feature) or accidental (regression)

## Success Criteria

- Root cause identified with evidence (specific file change or behavioral shift)
- If regression: fix applied or fix plan documented
- If intentional: rationale documented in decisions/
