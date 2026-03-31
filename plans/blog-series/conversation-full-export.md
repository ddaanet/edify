# Conversation Export — Blog Series Planning (plugin)

**Date:** 2026-03-13
**Projet:** claudeutils / plugin

---

## Tour 1

### User

Récupère le contexte du projet sur mon GitHub. Actuellement ça s'appelle claudeutils il y a un sous module qui s'appelle plugin.

### Claude

*(Recherche web "claudeutils plugin GitHub" — pas de résultat pertinent)*

La recherche générique ne trouve pas ton repo spécifique. J'ai besoin d'un peu plus d'info pour le localiser.

Quel est ton nom d'utilisateur GitHub ?

---

## Tour 2

### User

ddaanet, mais il faudrait que je push d'abord

### Claude

Pas de souci, vérifions quand même ce qui est déjà en ligne :

*(Recherche web "github ddaanet claudeutils" → trouve le profil avec le repo claudeutils listé)*

Le repo `claudeutils` existe bien sur ton profil. Voyons ce qu'il contient :

*(Clone https://github.com/ddaanet/claudeutils.git)*

*(Explore la structure du repo — 12M, src/, tests/, agents/, plans/, etc.)*

*(Lit CLAUDE.md — références @plugin/fragments/*, documentation progressive, recipes justfile)*

*(Vérifie le submodule — plugin pointe vers git@github.com:ddaanet/plugin.git, commit 6cafc1d)*

*(Clone plugin via HTTPS — succès)*

*(Explore plugin — skills/, agents/, fragments/, hooks/, bin/, docs/, configs/, templates/)*

*(Lit plugin/README.md — 18 skills, 14 sub-agents, 23 fragments, 4 hooks, pipeline design→handoff)*

*(Lit claudeutils/README.md — CLI commands, agent framework, memory management, development setup)*

*(Lit pyproject.toml — Python 3.14+, dependencies, ruff ALL, mypy strict)*

*(Explore src/claudeutils/ — account/, cli.py, compose.py, discovery.py, extraction.py, filtering.py, markdown*.py, model/, parsing.py, paths.py, recall/, statusline/, tokens.py, validation/, when/, worktree/)*

OK, j'ai tout récupéré et parcouru. Voici le contexte du projet :

**claudeutils** — c'est un outil en deux parties pour travailler avec Claude Code :

**1. CLI Python** (`src/claudeutils/`) — installable via `uv tool install .`, Python 3.14+, avec ces sous-commandes :

- **Feedback pipeline** : `list`, `extract`, `collect`, `analyze`, `rules` — parse les sessions JSONL de Claude Code pour extraire tes retours
- **Markdown cleanup** — corrige les problèmes structurels du markdown généré par Claude (listes emoji, blocs imbriqués, etc.)
- **Token counting** — comptage via l'API Anthropic avec alias modèles (`haiku`/`sonnet`/`opus`)
- **Account/model management** — switch entre providers API/plan, overrides de modèle
- **Compose** — assemble des fichiers markdown modulaires à partir de fragments YAML
- **Validation** — vérifie la cohérence de toute la structure mémoire (memory-index, decisions, jobs, learnings, tasks)
- **Recall analysis** — mesure si les agents consultent vraiment les entrées mémoire pertinentes
- **Statusline** — affichage formaté pour le hook statusline de Claude Code
- **When** — navigation/résolution de fichiers avec fuzzy matching
- **Worktree** — gestion de git worktrees pour exécution parallèle de tâches

Stack : Click, Pydantic, Anthropic SDK, PyYAML. Linting strict avec `ruff ALL` + `mypy strict`. Tests avec pytest (~100+ fichiers de test).

**2. plugin** (sous-module git `plugin/`) — le framework de workflow pour Claude Code :

- **Pipeline structuré** : `/design` → `/runbook` → `[plan-reviewer]` → `/orchestrate` → `[vet-fix-agent]` → `/handoff`
- **18 skills** (slash-commands), **14 sub-agents** (via Task tool en contexte isolé), **23 fragments** d'instruction, **4 hooks**
- **Système mémoire** : `session.md` (handoff), `learnings.md` (append-only), `memory-index.md` (catalogue), `decisions/` (décisions permanentes), `jobs.md` (lifecycle des plans)
- **Modes de session** : `s` (status), `x` (execute), `xc` (execute+commit), `r` (resume), `wt` (worktree)
- En cours de migration vers un plugin Claude Code (`edify-plugin`)

Le `CLAUDE.md` à la racine compose tout avec des `@plugin/fragments/...` references.

Qu'est-ce que tu voulais faire avec ce contexte ? Tu mentionnais vouloir push d'abord — c'est à jour ou il y a des changements locaux que je devrais connaître ?

---

## Tour 3

### User

C'est le contexte du projet initialise la mémoire du projet avec ça

### Claude

*(Vérifie les memory edits existants — aucun)*

*(Ajoute 5 entrées mémoire :)*

1. User is David Allouche (ddaanet on GitHub). Main project: claudeutils — Python CLI + agent framework for Claude Code.
2. claudeutils CLI: click-based, Python 3.14+, uv, pydantic, mypy strict, ruff ALL. Cmds: extract/collect/analyze, markdown, tokens, account, compose, validate, recall, statusline, when, worktree.
3. plugin: git submodule in claudeutils. 18 skills, 14 sub-agents, 23 fragments, 4 hooks. Pipeline: design→runbook→orchestrate→vet→handoff. Migrating to plugin (edify-plugin).
4. plugin memory system: session.md (handoff), learnings.md (append-only), memory-index.md (keyword catalog), decisions/ (permanent), jobs.md (plan lifecycle). Session modes: s/x/xc/r/wt.
5. Repos: github.com/ddaanet/claudeutils (public, Python) and github.com/ddaanet/plugin (public, submodule). Build: hatchling. Tasks: justfile. Tests: pytest (~100+ test files).

C'est fait. 5 entrées mémoire initialisées couvrant l'essentiel : ton identité GitHub, la stack et les commandes du CLI, la structure d'plugin (pipeline, skills, agents, fragments), le système mémoire, et les infos repo/build. Ça sera disponible dans toutes les conversations de ce projet.

---

## Tour 4

### User

Je voudrais générer de l'activité sur LinkedIn pour ça, je projette des créer une série de tickets de blog documentant les patterns clés du système, ça me donnera une bonne vitrine sur ddaa.net et plus de visibilité. En français, et en anglais.

### Claude

Bonne idée. Avant de planifier la série, quelques questions pour cadrer :

*(Widget de questions :)*

**Q : Quel format pour les posts ?**
- Articles longs (1500+ mots) sur ddaa.net + résumé LinkedIn
- Posts LinkedIn natifs (courts, percutants) avec lien vers le repo
- Mix : certains sujets méritent un article, d'autres juste un post LinkedIn

**Q : Quelle audience cible ?**
- Devs qui utilisent déjà Claude Code
- Devs curieux de l'agentic coding en général
- Decision makers / tech leads qui évaluent les outils AI
- Large : tous ces profils

**Q : Quels patterns te semblent les plus forts à mettre en avant ?**
- Pipeline structuré (design→handoff) — pourquoi les agents ont besoin de process
- Mémoire persistante — résoudre l'amnésie entre sessions
- Isolation des sub-agents — scope enforcement structurel
- Vet/review automatique — qualité sans intervention humaine

Et une question ouverte : est-ce que ddaa.net a déjà un blog en place (avec quel moteur — Hugo, Jekyll, autre ?) ou c'est à créer aussi ?

---

## Tour 5

### User

Q : Quel format pour les posts ?
R : Articles longs (1500+ mots) sur ddaa.net + résumé LinkedIn

Q : Quelle audience cible ?
R : Large : tous ces profils

Q : Quels patterns te semblent les plus forts à mettre en avant ?
R : Pipeline structuré (design→handoff) — pourquoi les agents ont besoin de process, Mémoire persistante — résoudre l'amnésie entre sessions, Isolation des sub-agents — scope enforcement structurel et Vet/review automatique — qualité sans intervention humaine

### Claude

Les 4 patterns, c'est parfait — ça fait une série cohérente avec un arc narratif naturel : du problème général (pourquoi structurer) vers les solutions spécifiques.

Tu n'as pas répondu sur ddaa.net — il y a déjà un blog en place, ou c'est à monter ?

En attendant, voici une proposition de plan pour la série. Je pense à 5 articles : un intro qui pose le problème + un par pattern.

**Article 1 — "Pourquoi vos agents AI écrivent du code jetable"**
L'accroche. Le constat que tout le monde vit : ça marche sur le prompt, mais la session suivante c'est le chaos. Pose le problème sans vendre la solution tout de suite. Tease les 4 patterns. C'est l'article qui doit accrocher l'audience large (tech leads, curieux).

**Article 2 — Pipeline structuré : design→handoff**
Premier pattern. Le plus intuitif à comprendre pour les non-utilisateurs de Claude Code. Analogie avec CI/CD — personne ne déploie sans pipeline, pourquoi laisser un agent coder sans process ? Montre le before/after concret.

**Article 3 — Mémoire persistante entre sessions**
Le pattern qui résonne le plus émotionnellement — "l'amnésie" c'est le truc qui frustre tout le monde. session.md, learnings.md, memory-index.md, le système de graduation des connaissances. Concret, démontrable.

**Article 4 — Isolation des sub-agents**
Le plus technique, le plus original. L'idée contre-intuitive que donner *moins* de contexte à un agent améliore les résultats. Scope enforcement structurel plutôt que par instruction prose. C'est l'article qui parle aux devs Claude Code.

**Article 5 — Review automatique sans humain dans la boucle**
Le vet-fix-agent, le cycle review→fix→re-review. Comment on atteint une qualité acceptable sans valider chaque ligne. Ça parle aux tech leads qui se demandent "mais qui vérifie le code de l'IA ?".

Chaque article en FR + EN, avec un post LinkedIn d'accroche qui résume la thèse en 3-4 paragraphes et renvoie vers l'article complet.

Ça te parle comme structure ? Tu voudrais réordonner, fusionner, ou ajouter quelque chose ?

---

## Tour 6

### User

Pas mal. Je pensais au départ plus à une approche didactique, en commençant par le pattern fondamental remember. Il n'est plus utilisé dans le code actuel mais c'est le concept clé avoir une règle pour modifier Claude. MD, ensuite la skill clé qui a tout débloqué: Ground. Suivi de handoff, qui est la base du système de mémoire. Suivi de délivrable-review, qui a été décisif dans l'augmentation de la qualité des délivrer. Suivi des autres sujets.

### Claude

Ça change tout l'angle — c'est une histoire d'évolution, pas un catalogue de features. Beaucoup plus convaincant.

*(Lit skills/remember/SKILL.md, skills/ground/SKILL.md, skills/handoff/SKILL.md, skills/deliverable-review/SKILL.md)*

OK, j'ai lu les 4 skills en détail. Ton angle est bien meilleur — c'est une histoire d'apprentissage progressif, chaque concept débloque le suivant. Voici la série révisée :

**Article 1 — Remember : la règle qui change les règles**

Le pattern fondamental. L'idée que CLAUDE.md n'est pas un fichier statique mais un document vivant que l'agent peut modifier lui-même. Tu commences par un problème universel : l'agent fait une erreur, tu la corriges, il la refait la session suivante. La solution naïve c'est d'ajouter des règles à la main. Le déclic : formaliser ça en skill — l'agent identifie un pattern, le formule en contrainte précise ("Do not" > "avoid"), le place au bon endroit, et vérifie que c'est actionnable. C'est la base de tout le reste : sans ça, aucun apprentissage ne persiste.

**Article 2 — Ground : quand l'agent invente au lieu de chercher**

La skill qui a tout débloqué. Le problème : tu demandes à Claude de créer une méthodologie, un framework, un scoring, et il te sort quelque chose de plausible mais inventé. Ça sonne bien, c'est structuré, et c'est du vent. Ground impose un diverge-converge : une branche interne (brainstorm projet-spécifique via Opus) et une branche externe (recherche web de frameworks nommés existants), puis synthèse avec un label de qualité obligatoire (Strong/Moderate/Thin/None). L'insight clé : ni le raisonnement interne seul ni la recherche seule ne suffisent — c'est le croisement des deux qui produit du contenu ancré.

**Article 3 — Handoff : la mémoire entre les sessions**

La base du système mémoire. Le problème est concret : chaque session Claude Code repart de zéro. Handoff structure ce qui transite : session.md comme working memory (tâches, blockers, contexte), learnings.md comme mémoire sémantique (append-only, anti-patterns, patterns corrects), git comme archive. Les détails qui comptent : les pending tasks sont du carry-forward verbatim (pas de résumé), les learnings ont un format strict (anti-pattern / correct pattern / rationale), et il y a un mécanisme de consolidation automatique quand le fichier grossit. C'est l'article qui fait le lien avec remember — les learnings sont le staging, remember les consolide en documentation permanente.

**Article 4 — Deliverable Review : la qualité sans humain dans la boucle**

Le saut de qualité. Le problème : l'agent produit des artefacts, mais qui vérifie ? Pas juste du linting — une revue structurée avec inventaire des livrables, gap analysis contre le design, axes de revue par type d'artefact (code, test, prose agentique, config), et classification de sévérité (Critical/Major/Minor, grounded dans ISO 25010). Le système à deux couches est l'insight intéressant : Layer 1 déléguée (agents parallèles pour le volume) + Layer 2 interactive obligatoire (cross-cutting que la délégation ne peut pas attraper). C'est ce qui permet de faire confiance au pipeline sans valider chaque ligne.

**Article 5+ — Les sujets suivants**

Pipeline structuré (design→orchestrate), isolation des sub-agents, worktrees pour exécution parallèle, le memory-index comme mécanisme de progressive disclosure... On voit après selon la traction.

Quelques questions ouvertes avant de commencer à écrire :

- Est-ce que ddaa.net a déjà un blog ? Quel moteur ?
- Tu veux que je commence par quel article ? Je partirais sur le 1 (remember) vu que c'est le fondement.
- Pour le bilingue FR/EN : traduction fidèle, ou adaptation du ton pour chaque audience ?

---

## Tour 7

### User

Ddaa.net a un blog maison, basé sur la génération statique de HTML, un partir de markdown .

### Claude

*(Ajoute mémoire #7 : Blog on ddaa.net: static HTML generated from markdown. Content marketing plan: blog series on plugin patterns + LinkedIn promotion in FR and EN.)*

Parfait, donc le livrable c'est du markdown directement. Pas de friction technique.

Restent les deux questions :

*(Widget de questions :)*

**Q : On commence par quoi ?**
- Article 1 (Remember) — le fondement
- Article 2 (Ground) — le plus "wow"
- L'outline complète des 5 d'abord, puis on attaque

**Q : Approche bilingue ?**
- Traduction fidèle FR→EN
- Adaptation : même fond, ton ajusté par audience
- Écrire en FR d'abord, EN ensuite comme version séparée

---

## Tour 8

### User

Q : On commence par quoi ?
R : Il y plein d'autres truc… une protocol de pushback qui marche

Q : Approche bilingue ?
R : Adaptation : même fond, ton ajusté par audience

### Claude

Intéressant, tu veux commencer par le pushback plutôt que la série prévue.

*(Lit fragments/pushback.md, fragments/communication.md, fragments/deslop.md)*

OK, c'est du bon matériel. Le pushback fragment est compact mais il y a un vrai insight dedans — notamment le "agreement momentum" counter (3+ accords consécutifs → auto-réévaluation) et la distinction entre corriger le raisonnement vs contester la conclusion.

Avant que je me lance, je veux clarifier l'angle. Tu as dit "il y a plein d'autres trucs" — est-ce que tu veux :

1. **Commencer la série par le pushback** comme article 1, puis enchaîner remember → ground → handoff → deliverable-review ? Le pushback est une bonne porte d'entrée parce que tout le monde a vécu le problème de la sycophance.

2. **Faire le pushback comme article standalone / teaser**, puis la série des 4 patterns fondamentaux séparément ?

3. **Revoir toute la série** pour inclure pushback, deslop, et les autres fragments comportementaux comme des articles à part entière ?

Et question pratique : le ton que tu veux pour les articles, c'est plutôt dans la veine de ce qu'on fait ici (direct, technique, concret) ou plus narrative / storytelling avec le parcours de découverte ?

---

## Tour 9

### User

Exporte cette conversation en markdown structuré.

### Claude

*(Première tentative : synthèse structurée au lieu d'export verbatim)*

---

## Tour 10

### User

Merci. Ce que je voulais c'est une extraction complète et automatique de la conversation, pas une synthèse.

### Claude

*(Ce fichier)*
