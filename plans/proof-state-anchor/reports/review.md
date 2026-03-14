# Skill Review: proof State Output (D+B anchor)

## Findings: 0 Critical, 0 Major, 3 Minor

### M-1: Terminal format undocumented as variant
Terminal emissions use self-contained sentence form (`applying N decisions to <artifact>`) rather than the pipe-separated general format. Emission rules table captures this correctly, but format section only shows the general template.
**Status:** FIXED — added terminal format examples to format section.

### M-2: "feedback" as pseudo-action
"feedback" in action list is the default mode, not a discrete command. Including it makes the default explicit to users. No handler needed.
**Status:** DEFERRED — intentional UX choice, no fix needed.

### M-3: D+B anchor label inconsistency
Entry emission labeled `(D+B anchor)`, subsequent emissions not. Section header at line 29 already establishes context for all emissions.
**Status:** DEFERRED — cosmetic, section header carries semantic weight.
