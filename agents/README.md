# Agent Instructions and Configuration

This directory contains agent-related configuration and documentation.

## Overview

The `CLAUDE.md` file in the project root provides comprehensive instructions for how agents should behave within this project. It covers communication rules, delegation patterns, tool usage, and role definitions.

## Composition and Generation

`CLAUDE.md` is generated from shared fragments stored in the `plugin` repository. This allows consistent agent instructions to be shared across multiple projects while remaining customizable per project.

### Source Fragments

The `CLAUDE.md` file is composed from fragments stored in `plugin/fragments/`. These fragments provide modular, reusable instruction components that are imported via `@`-references.

Core fragments include communication rules, delegation patterns, tool batching guidelines, and workflow-specific instructions.

### Generation Script

**File**: `agents/compose.sh`

**Purpose**: Concatenates fragments to generate `CLAUDE.md`

**Usage**:
```bash
bash agents/compose.sh
```

**Configuration**:
- Fragment list: `compose.yaml`
- Fragment paths: Hard-coded in `compose.sh` (can evolve to YAML parsing in future)

## Customization

To customize agent instructions for this project:

1. **Add project-specific sections**: Edit `CLAUDE.md` directly for local customization
2. **Modify fragment order**: Update `compose.sh` fragment array and re-run generation
3. **Override shared rules**: Add project-specific rules before the composition step
4. **Document changes**: Keep this README updated with any project-specific patterns

## Integration with Justfile

The generation script can be called from justfile recipes:

```justfile
generate-agents:
    bash agents/compose.sh
```

## Version Control

- **CLAUDE.md**: Tracked in git (generated file, but committed for visibility)
- **compose.yaml**: Tracked in git (composition configuration)
- **compose.sh**: Tracked in git (generation script)
- **plugin/**: Added as git submodule

## Future Enhancements

Potential improvements for future phases:

- YAML parser for compose.yaml in compose.sh
- Template variables for project-specific customization
- Validation schema for generated CLAUDE.md
- CI/CD integration to validate composition on commit
- Fragment composition at import time (eliminating need to regenerate)

## Related Files

- `CLAUDE.md` - Generated agent instructions (project root)
- `compose.yaml` - Composition configuration
- `compose.sh` - Generation script
- `role-*.md` - Specialized role definitions
- `rules-*.md` - Action-triggered rule implementations
- `design-decisions.md` - Architectural rationale
