# Classification: Runbook Warnings

- **Classification:** Moderate
- **Implementation certainty:** High — approach known: collect file-creation declarations from all steps, build "will-exist" set, subtract from validation targets
- **Requirement stability:** High — single FR with concrete mechanism direction
- **Behavioral code check:** Yes — adds new logic paths to `validate_file_references`
- **Work type:** Production
- **Artifact destination:** production (`plugin/bin/`)
- **Evidence:** Single function (~60 lines) needs modification. Existing suppression heuristics are ad-hoc — need systematic replacement. Recall: "When step file inventory misses codebase references" confirms grep-based discovery approach.
