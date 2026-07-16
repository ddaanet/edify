## Error Handling

**Errors should never pass silently.**

- Do not swallow errors or suppress error output
- Errors provide important diagnostic information
- Report all errors explicitly to the user
- Never use error suppression patterns (e.g., `|| true`, `2>/dev/null`, ignoring exit codes)
- If a command fails, surface the failure - don't hide it

**Exception:** `|| true` is legitimate only where a non-zero exit *encodes a result* rather than a failure — `grep` finding no match, `diff` finding differences. Suppress the exit in exactly those spots; never to silence an error you haven't inspected.

### When Edit Tool Fails Repeatedly

**Do not escape to `sed -i` after Edit tool errors.** sed presents opaque syntax in permission prompts — user sees the command, not a content diff. This degrades the human review gate that Edit provides (old/new content visible).

**Correct pattern:** Stop and report the Edit failure after the second identical error. The stop-on-unexpected rule applies. Edit's permission UX is part of human oversight design — bypassing it with sed is not a neutral tool substitution.
