# Phase 10: Remember Skill Update

**Type:** General
**Model:** haiku
**Dependencies:** Phase 9 (format must be proven stable)
**Files:** `agent-core/skills/remember/SKILL.md`

**Design reference:** `/remember` Skill Update section

**Prior state:** Phase 9 completed migration. Index now uses `/when` and `/how` format. Validator enforces new format. Compress-key tool available for uniqueness verification.

---

## Step 10.1: Update entry generation to produce `/when` format

**Prerequisite:** Read `agent-core/skills/remember/SKILL.md` — understand current entry generation instructions

**Objective:** Update the `/remember` skill to generate `/when` or `/how` format entries instead of `Key — description` format.

**Implementation:**
- Find the section in SKILL.md that instructs how to generate index entries
- Replace em-dash format instruction with `/when trigger | extra triggers` format
- Include operator selection guidance:
  - `/when` for behavioral knowledge (when to do X, when X applies)
  - `/how` for procedural knowledge (how to do X, technique for X)

**Expected Outcome:** Skill instructions produce new format entries when invoked.

**Error Conditions:** None expected (content update only).

**Validation:** Read updated SKILL.md — verify entry format instructions match design spec.

---

## Step 10.2: Add trigger naming guidelines

**Objective:** Add guidelines for creating effective trigger phrases.

**Implementation:**
- Add trigger naming guidelines to SKILL.md:
  - Plain prose, no hyphens or special characters
  - 2-5 words typical
  - Optimize for discovery: "what would an agent type when facing this problem?"
  - Keep concise but specific enough for unique fuzzy matching
  - Use operator prefix to disambiguate when/how

**Expected Outcome:** Guidelines section added to skill, clear examples provided.

**Error Conditions:** None expected.

**Validation:** Read guidelines section — verify specificity and examples.

---

## Step 10.3: Reference compress-key tool for uniqueness verification

**Objective:** Add instruction to verify trigger uniqueness using compress-key tool.

**Implementation:**
- Add step in entry creation workflow: "Verify trigger uniqueness"
- Note that compress-key tool (`agent-core/bin/compress-key.py`, available after Phase 7) can suggest minimal unique trigger
- Alternatively, verify manual trigger against corpus using fuzzy matching
- Reference that the validator will catch collisions at precommit

**Expected Outcome:** Skill workflow includes uniqueness verification step.

**Error Conditions:** None expected.

**Validation:** Read updated workflow — verify uniqueness verification step present with tool reference and manual alternative.
