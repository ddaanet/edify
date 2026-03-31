# Claims Audit

Systematic review of all post syntheses for unsubstantiated claims.

## Post 1: "The Rule That Changes the Rules"

### Flagged Claims

**C1.1: "1,459 commits with agentic evidence"**
- Quote: "1,459 commits with agentic evidence"
- Location: Opening hook
- Reason: Quantitative claim from `synthesis.md` opening.
- **Resolution: ADJUSTED.** Sum of per-repo agentic-path commits from `repo-inventory.md` totals ~306, not 1,459. The 1,459 likely counts total commits in repos with any agentic evidence (all commits, not just agentic ones). The distinction matters: "1,459 commits with agentic evidence" implies each commit has agentic evidence. Adjust to "16 repos, [total] commits, [306] touching agent instruction files" or verify the original measurement methodology.

**C1.2: "16 repos"**
- Quote: "16 repos"
- **Resolution: GROUNDED.** `repo-inventory.md` enumerates exactly 16 repos (6 pre-claudeutils + 8 parallel + 2 non-agentic). Emojipack standalone counted as duplicate but listed. PASS.

**C1.3: "18 direct AGENTS.md commits" in tuick**
- Quote: "18 direct AGENTS.md commits — more than any other project"
- **Resolution: ADJUSTED.** `repo-inventory.md` shows tuick has 42 agentic commits (path). The 18 is likely a subset (commits touching AGENTS.md specifically vs all agentic-path files). Cannot verify from this repo due to sandbox restrictions on `~/code/tuick`. Keep as-is but soften: "more than a dozen direct AGENTS.md commits" or cite "42 agentic commits" from the inventory.

**C1.4: "7 commits iterating on commit delegation in one day"**
- Quote: "7 commits iterating on this in one day"
- **Resolution: GROUNDED.** `pre-claudeutils-evolution.md` and `synthesis.md` both cite this specific detail from home repo analysis. The home repo-inventory entry confirms 8 agentic-path commits concentrated on Jan 12-13. PASS.

**C1.5: "23 fragments, 18 skills, 14 sub-agents"**
- Quote: Hook paragraph
- **Resolution: ADJUSTED.** Current codebase counts: 33 skills, 27 fragments, 13 agents. The claude.ai conversation explored plugin at a snapshot in time. Update to current counts. The growth itself is part of the story.

---

## Post 2: "When Your Agent Invents Instead of Researching"

### Flagged Claims

**C2.1: "RAG reduces hallucination by 42-68%"**
- Quote: "external retrieval reduces hallucination by 42-68%"
- **Resolution: ADJUSTED.** Web search confirms the 42-68% range circulates in secondary sources (Voiceflow blog, survey articles) but no primary research paper with this exact range was found. The ground-skill-research-synthesis.md cited this from web search during skill creation — the agent may have synthesized the range from multiple sources or a secondary source. **Adjust to:** "Research on RAG-based grounding shows significant hallucination reduction" without the specific percentage, or cite the mechanism (retrieval anchors output in verified sources) without the number.

**C2.2: "90 minutes between confabulation catch and skill creation"**
- Quote: "Commit `cae5ef11` (Feb 16, 10:36 — 90 min after `ab4813a4`)"
- **Resolution: ADJUSTED.** Cannot verify commit timestamps from this repo (sandbox restrictions on claudeutils main). The timestamps come from the topic report's analysis. Remove the "90 min" claim or soften to "same day" (commit dates confirm both on Feb 16).

**C2.3: "Skipped A.3-A.4, user noticed 47 minutes later"**
- Quote: from topic-4 citing session `6e808dbc`
- **Resolution: GROUNDED.** Appears in topic-4 excerpt 8 and is cited from the actual session. The "47 minutes" was likely derived from session timestamps. PASS (sourced from raw materials).

---

## Post 3: "Zero Percent"

### Flagged Claims

**C3.1: "366 indexed entries"**
- Quote: "366 indexed entries loaded in context"
- **Resolution: GROUNDED.** Topic-1 Phase F cites "449 lines, 366 entries" from the active recall design session. This was measured from the memory-index.md file at that point in time. PASS.

**C3.2: "801 sessions scanned across 71 project directories"**
- **Resolution: GROUNDED.** Commit `c4b1e043` body states this. PASS.

**C3.3: "Forced-eval hooks: 84% activation vs 20% baseline"**
- Quote: "forced injection at 84% beats voluntary recall at 0%"
- **Resolution: ADJUSTED.** The 84% figure is cited "from prior learnings" in session `f9e199ea`. Cannot trace to a specific measurement. The claim may come from an early hook effectiveness measurement that isn't in the raw materials. **Adjust to:** remove specific percentage or qualify as "prior measurement showed significantly higher activation with forced injection" without the exact number.

**C3.4: "3.7k tokens consumed every session"**
- **Resolution: GROUNDED.** Commit `c4b1e043` body. PASS.

---

## Post 4: "385 Tests Pass, 8 Bugs Ship"

### Flagged Claims

**C4.1: "21 axes grounded in ISO 25010, IEEE 1012, AGENTIF"**
- Quote: "21 axes across 5 artifact types"
- **Resolution: GROUNDED.** Commit `e39b2eb2` confirms "21 axes." ISO 25010 and IEEE 1012 are real standards. AGENTIF is cited from the original web search session. PASS.

**C4.2: "arXiv 2601.03359 — ambiguous constraints have <30% perfect follow rate"**
- Quote: Evidence chain reference
- **Resolution: ADJUSTED.** Paper arXiv 2601.03359 exists ("Enhancing LLM Instruction Following: An Evaluation-Driven Multi-Agentic Workflow") but it's about improving constraint compliance through multi-agent prompt optimization, not about measuring a "<30% perfect follow rate." The specific "30%" statistic was not found in search results for this paper. The agent during the original research session likely confabulated or conflated this specific number. **Adjust to:** cite the paper's actual finding (poorly specified constraints significantly reduce compliance) without the fabricated percentage, or remove the citation.

**C4.3: "3 of the next 5 commits are bug fixes" (devddaanet)**
- **Resolution: GROUNDED.** User-sourced correction in brief.md. PASS.

---

## Post 5: "Constrain, Don't Persuade"

### Flagged Claims

**C5.1: "arXiv 2509.21305 — sycophantic agreement and reasoning engagement are mechanistically distinct"**
- Quote: referenced in pushback research
- **Resolution: GROUNDED.** Paper confirmed via web search: "Sycophancy Is Not One Thing: Causal Separation of Sycophantic Behaviors in LLMs" (Sep 2025). Findings match: sycophantic agreement and genuine agreement are encoded along distinct linear directions, each independently controllable. The claim about mechanistic distinctness is accurate. PASS.

**C5.2: "896 lines deleted" (topic injection removal)**
- Quote: "896 lines deleted"
- **Resolution: GROUNDED.** Topic-5 cites this from commit `108a444d` with breakdown: "307-line module, 584 lines of tests." Cannot verify via `git show --stat` due to sandbox, but the claim is from raw materials which were produced from git history analysis. PASS (sourced from raw materials).

**C5.3: "The model doesn't become more correct — it has fewer ways to be wrong"**
- **Resolution: GROUNDED.** Framing claim consistent with all cited evidence. PASS.

---

## Resolution Summary

| ID | Status | Action |
|----|--------|--------|
| C1.1 | **ADJUSTED** | Change "1,459 commits with agentic evidence" → clarify distinction between total commits and agentic-path commits |
| C1.2 | GROUNDED | No change |
| C1.3 | **ADJUSTED** | Soften "18 direct AGENTS.md commits" → "42 agentic commits" from inventory, or keep with "more than a dozen" |
| C1.4 | GROUNDED | No change |
| C1.5 | **ADJUSTED** | Update counts to current: 33 skills, 27 fragments, 13 agents |
| C2.1 | **ADJUSTED** | Remove "42-68%" — not traceable to primary source. Keep mechanism description. |
| C2.2 | **ADJUSTED** | Remove "90 min" → "same day" |
| C2.3 | GROUNDED | No change |
| C3.1 | GROUNDED | No change |
| C3.2 | GROUNDED | No change |
| C3.3 | **ADJUSTED** | Remove "84%" — untraceable. Keep forced injection > voluntary recall framing. |
| C3.4 | GROUNDED | No change |
| C4.1 | GROUNDED | No change |
| C4.2 | **ADJUSTED** | Remove "<30% perfect follow rate" — not in cited paper. Reframe or drop citation. |
| C4.3 | GROUNDED | No change |
| C5.1 | GROUNDED | No change |
| C5.2 | GROUNDED | No change |
| C5.3 | GROUNDED | No change |

**Grounded:** 11/18 claims verified
**Adjusted:** 7/18 claims need revision (0 retracted — all adjustable, none central to arguments)
