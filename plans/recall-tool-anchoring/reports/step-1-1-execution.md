# Step 1.1 Execution Report

**Step:** 1.1 — Write recall-check.sh
**Status:** Complete

## Output

Created: `agent-core/bin/recall-check.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: recall-check.sh <job-name>" >&2
  exit 1
fi

JOB="$1"
ARTIFACT="plans/${JOB}/recall-artifact.md"

if [[ ! -f "$ARTIFACT" ]]; then
  echo "recall-artifact.md missing for ${JOB}" >&2
  exit 1
fi

if [[ ! -s "$ARTIFACT" ]]; then
  echo "recall-artifact.md empty for ${JOB}" >&2
  exit 1
fi
```

## Validation Results

- Existing artifact (`recall-tool-anchoring`): exit 0, no output (pass)
- Nonexistent job (`nonexistent-job`): exit 1, stderr `recall-artifact.md missing for nonexistent-job` (pass)

## Commits

- Submodule: `1f16000` — Add recall-check.sh existence/non-empty validator script
- Parent: `6fd29c08` — Update agent-core submodule: add recall-check.sh (step 1.1)
