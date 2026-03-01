# Classification: Fix Recall-Expansion (Deliverable Review Findings)

- **Classification:** Moderate
- **Implementation certainty:** High — each finding specifies exact location, problem, and expected fix
- **Requirement stability:** High — findings concrete and mechanism-specified by deliverable review
- **Behavioral code check:** Yes — exception handling adds logic path, test restructuring adds behavioral assertions → Moderate minimum
- **Work type:** Production — delivers test coverage and robustness to existing feature
- **Artifact destination:** production (`tests/test_prepare_runbook_recall.py`, `agent-core/bin/prepare-runbook.py`)
- **Evidence:** All fixes have concrete locations/expected outcomes. No architectural decisions. Stacey: both axes high. Behavioral code prevents Simple. Three findings: Major-1 (e2e test for phase recall → step files), Minor-1 (e2e tests call main() not replicate wiring), Minor-2 (subprocess exception handling).
