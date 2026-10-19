# Déroulé — quelle source, à quel moment

Toutes les sources du dépôt, dans l'ordre où on les utilise, de la préparation à la clôture. Pour
chacune : ce qu'on projette, ce qu'on fait dérouler, ce qu'on exécute et ce qu'on garde pour soi.
Le programme et ses justifications sont dans le [README](README.md) : ils ne sont pas répétés ici.

**Colonne « Usage »** — **Lire** : préparation personnelle · **Projeter** : deck PDF ·
**Faire dérouler** : énoncé Markdown suivi par les participants · **Montrer** : fichier de
référence ouvert à l'écran · **Exécuter** : commande à lancer soi-même ·
**Ne pas distribuer** : script d'injection d'incident.

Les pages citées sont celles des PDF de [`slides/`](slides/).

---

## Le geste répété — module et lab

**Un module** (deck 02 + `modules/NN-*/README.md`) :
1. Projeter la section du deck 02 : la limite, puis le concept.
2. Faire dérouler le **mini-lab** (§ 4 du README), dans `~/lab-ecommerce`.
3. Conclure sur la **checklist de sortie** (§ 6) et **la limite suivante** (§ 7), qui annonce l'étape d'après.

**Un lab** (deck 03 + `labs/lab-NN-*/README.md`) :
1. Projeter la diapo de lancement du deck 03 : objectif, briques, livrable, garde-fous.
2. Faire dérouler le **déroulé pas-à-pas** (§ 4), puis vérifier le **livrable** (§ 5).
3. Conclure sur **la limite révélée** (§ 8).
4. Le corrigé (`solution/`) ne s'applique **qu'après avoir essayé**, avec la commande de la
   section « Corrigé » en fin d'énoncé.

Tout au long de la formation : [`docs/choisir-sa-brique.md`](docs/choisir-sa-brique.md) se relit
à chaque transition de brique.

---

## Avant la session — J-7 à J-1

| # | Source | Usage | Repères |
|:---:|---|---|---|
| 1 | [`README.md`](README.md) | Lire | Programme 4 jours, compétences visées, structure du dépôt |
| 2 | [`slides/README.md`](slides/README.md) | Lire | Les quatre decks et leur moment. En cas d'écart avec un énoncé, **le Markdown fait foi** |
| 3 | [`docs/prerequis.md`](docs/prerequis.md) | Envoyer à J-7 | Installation par jour, comptes à préparer. Poste verrouillé : demande au catalogue logiciel **une semaine avant** |
| 4 | [`docs/check-prereqs.sh`](docs/check-prereqs.sh) | Envoyer avec le 3 | **Vérifie seulement, n'installe rien.** `MANQ` = bloquant (code 1), `ABS` = optionnel |
| 5 | [`CLAUDE.md`](CLAUDE.md) § Vérifier | Exécuter | Build de l'application, `claude plugin validate` (×3), `helm lint`. Ensuite, supprimer les `bin/`, `obj/` et `TestResults/` produits |
| 6 | [Lab 08](labs/lab-08-kubernetes/), [Lab 10](labs/lab-10-observabilite/), [Lab 11 B](labs/lab-11-incident-postmortem/) | Répéter à blanc | Ces corrigés n'ont **pas** été exécutés pendant la rédaction : manifestes jamais appliqués sur un cluster, MCP Aspire et `grafana-mcp` jamais lancés, scénario B jamais joué |
| 7 | Comptes et accès | Préparer | Compte GitHub **de test** (labs 01, 06) ; clé d'API Anthropic **de test** pour la revue headless ([Lab 06](labs/lab-06-ci-cd/), pré-requis) ; extension *Claude in Chrome* ([Lab 05](labs/lab-05-frontend/)) |
| 8 | [`docs/choisir-sa-brique.md`](docs/choisir-sa-brique.md) · [`docs/garde-fous.md`](docs/garde-fous.md) | Lire | Le fil rouge des transitions ; les six règles R1–R6 et la configuration de référence |

---

## J1 matin — Ouverture et fondations

| # | Source | Usage | Repères |
|:---:|---|---|---|
| 9 | [`slides/00-plan-formation.pdf`](slides/00-plan-formation.pdf) p. 1–14 | Projeter | Objectifs, publics, progression, les 9 modules et 11 labs, programme, application fil rouge |
| 10 | `slides/00-plan-formation.pdf` p. 15–18 · [`docs/garde-fous.md`](docs/garde-fous.md) | Projeter, puis montrer | Le principe, les six règles, ce qu'on ne fait pas (§ 4 du document) |
| 11 | `slides/00-plan-formation.pdf` p. 19–20 | Projeter | « Vérifier son poste — maintenant » |
| 12 | [`docs/check-prereqs.sh`](docs/check-prereqs.sh) | Faire exécuter | `./docs/check-prereqs.sh`. Une ligne `MANQ` : renvoyer vers l'étape 13. Une ligne `ABS` : les labs concernés se suivent en observation |
| 13 | [`docs/prerequis.md`](docs/prerequis.md) § 1–2, § 5 | Faire dérouler | Installer ce qui manque. Le poste est prêt quand le build passe et que le dashboard Aspire s'ouvre (§ 5) |
| 14 | `slides/00-plan-formation.pdf` p. 21–22 | Projeter | Livrables de la formation, transition vers les fondations |
| 15 | [`slides/01-fondations-ia-dev-devops.pdf`](slides/01-fondations-ia-dev-devops.pdf) p. 1–15 | Projeter | LLM, erreurs typiques, agents, prompt structuré, avant/après Dev et DevOps |
| 16 | `slides/01-fondations-ia-dev-devops.pdf` p. 16–21 · [`tp/README.md`](tp/README.md) | Projeter | Présenter le TP. Il se fait **dans l'application Claude** (claude.ai ou Desktop), une conversation par exercice, données synthétiques |
| 17 | [`tp/TP_Prompt_Engineering_Dev_DevOps.md`](tp/TP_Prompt_Engineering_Dev_DevOps.md) | Faire dérouler | 13 techniques (≈ 2 h 10) puis le livrable § 14 (20 min) : **cinq prompts par binôme**, réutilisés en J2. Sélectionner des techniques si le temps manque |
| 18 | `slides/01-fondations-ia-dev-devops.pdf` p. 22–26 | Projeter | Risques en banque, règles d'hygiène, à retenir, transition vers l'outil |

---

## J1 après-midi — Modules 00 à 03

| # | Source | Usage | Repères |
|:---:|---|---|---|
| 19 | [`README.md`](README.md) § Démarrage rapide · [`modules/README.md`](modules/README.md) § Où travailler | Faire exécuter | `export FORMATION="$PWD"`, puis `cp -r ecommerce-app ~/lab-ecommerce`. **Tout se fait dans la copie**, jamais dans `ecommerce-app/` |
| 20 | [`ecommerce-app/README.md`](ecommerce-app/README.md) | Montrer | Les cinq projets de l'application fil rouge et le lancement par Aspire |
| 21 | [`docs/cheatsheet.md`](docs/cheatsheet.md) · [`docs/glossaire.md`](docs/glossaire.md) | Distribuer | À garder ouverts toute la formation |
| 22 | [`slides/02-claude-code-briques.pdf`](slides/02-claude-code-briques.pdf) p. 1–2 · [`docs/choisir-sa-brique.md`](docs/choisir-sa-brique.md) § 1 | Projeter | Le fil conducteur : la chaîne des briques |
| 23 | `slides/02` p. 3–6 → [`modules/00-prise-en-main/`](modules/00-prise-en-main/) | Module | 45 min, mini-lab 15 min |
| 24 | `slides/02` p. 7–10 → [`modules/01-commandes-natives/`](modules/01-commandes-natives/) | Module | 45 min, mini-lab 20 min |
| 25 | `slides/02` p. 11–15 → [`modules/02-contexte-et-memoire/`](modules/02-contexte-et-memoire/) | Module | 40 min, mini-lab 20 min |
| 26 | `slides/02` p. 16–19 → [`modules/03-commandes-personnalisees/`](modules/03-commandes-personnalisees/) | Module | 30 min, mini-lab 15 min |

---

## J2 — Imposer et capitaliser

| # | Source | Usage | Repères |
|:---:|---|---|---|
| 27 | [`slides/03-labs-dev-devops.pdf`](slides/03-labs-dev-devops.pdf) p. 1–4 | Projeter | **Une seule fois**, avant le premier lab : modules vs labs, quelle brique pour quel lab, la chaîne critique 04 → 07 → 08 |
| 28 | `slides/03` p. 5–6 → [`labs/lab-01-git-github/`](labs/lab-01-git-github/) | Lab | 60 min. Dépôt GitHub de test. Livrable : un correctif livré en PR par `/ship` |
| 29 | `slides/02` p. 20–25 → [`modules/04-hooks/`](modules/04-hooks/) | Module | 50 min. Montrer les hooks de référence dans [`plugins/oddo-dev-toolkit/hooks/`](plugins/oddo-dev-toolkit/hooks/) |
| 30 | `slides/02` p. 26–30 → [`modules/05-skills/`](modules/05-skills/) | Module | 45 min. Montrer [`skills/ef-migration/`](plugins/oddo-dev-toolkit/skills/ef-migration/) (anatomie, p. 29) |
| 31 | `slides/03` p. 7 → [`labs/lab-02-tests/`](labs/lab-02-tests/) | Lab | 60 min. Mise en place des tests : [`solution/tests/README.md`](labs/lab-02-tests/solution/tests/README.md) |
| 32 | `slides/02` p. 31–38 → [`modules/06-plugins/`](modules/06-plugins/) | Module | 60 min. Montrer [`plugins/oddo-dev-toolkit/`](plugins/oddo-dev-toolkit/), [`plugins/oddo-dev-standard/`](plugins/oddo-dev-standard/) et [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json). Le mini-lab ajoute le marketplace : `claude plugin marketplace add "$FORMATION"` |
| 33 | `slides/03` p. 8 → [`labs/lab-03-securite-secrets/`](labs/lab-03-securite-secrets/) | Lab | 60 min. L'étape 8 installe le poste standard (`oddo-dev-standard`) |

---

## J3 — Déléguer, connecter

| # | Source | Usage | Repères |
|:---:|---|---|---|
| 34 | `slides/02` p. 39–43 → [`modules/07-sous-agents/`](modules/07-sous-agents/) | Module | 45 min. Montrer les six sous-agents de [`plugins/oddo-dev-toolkit/agents/`](plugins/oddo-dev-toolkit/agents/) (p. 43) |
| 35 | `slides/02` p. 44–50 → [`modules/08-mcp/`](modules/08-mcp/) | Module | 60 min. Partie C du mini-lab : jeton GitHub *fine-grained* en lecture seule. Montrer [`exemple-serveur-mcp-csharp/`](modules/08-mcp/exemple-serveur-mcp-csharp/) avec l'inspecteur MCP (p. 50). **En fin de journée : désinstaller le plugin et supprimer le jeton** |
| 36 | `slides/03` p. 9–11 → [`labs/lab-04-postgresql/`](labs/lab-04-postgresql/) | Lab | 90 min. Début de la chaîne critique : sans base, les labs 05, 10 et 11 A n'ont pas de données |
| 37 | `slides/03` p. 12 → [`labs/lab-05-frontend/`](labs/lab-05-frontend/) | Lab | 75 min. `/chrome` doit afficher *Enabled*. À l'étape 3, comparer avec la maquette [`solution/mockup/catalog-mockup.html`](labs/lab-05-frontend/solution/mockup/catalog-mockup.html) |
| 38 | `slides/02` p. 51–55 → [`modules/annexe-agent-sans-terminal/`](modules/annexe-agent-sans-terminal/) | Module | 40 min. Insister : **un mode d'exécution, pas une brique** |
| 39 | `slides/02` p. 56–61 · [`docs/choisir-sa-brique.md`](docs/choisir-sa-brique.md) § 3–5 | Projeter | Synthèse des briques : arbre de décision, confusions qui coûtent cher, niveau de garantie |
| 40 | `slides/03` p. 13–14 → [`labs/lab-06-ci-cd/`](labs/lab-06-ci-cd/) | Lab | 60 min. La clé d'API de test est ajoutée **comme secret du dépôt** (`gh secret set`), jamais dans un fichier |

---

## J4 — Livrer et exploiter

| # | Source | Usage | Repères |
|:---:|---|---|---|
| 41 | `slides/03` p. 15 → [`labs/lab-07-docker/`](labs/lab-07-docker/) | Lab | 45 min. Produit les images `ecommerce-*:dev` exigées par le lab 08 |
| 42 | `slides/03` p. 16 → [`labs/lab-08-kubernetes/`](labs/lab-08-kubernetes/) | Lab | 60 min. Le Secret est créé **par le participant, hors session** (étape 2). Première passe sur cluster **accompagnée** (cf. étape 6) |
| 43 | `slides/03` p. 17 → [`labs/lab-09-helm/`](labs/lab-09-helm/) | Lab | 30–45 min. **Variable d'ajustement** de J4 |
| 44 | `slides/03` p. 18–19 → [`labs/lab-10-observabilite/`](labs/lab-10-observabilite/) | Lab | 60 min. Les Dev suivent le parcours 4A (35 min), les DevOps le 4B (25 min, **variable d'ajustement**) |
| 45 | `slides/03` p. 20 → [`labs/lab-11-incident-postmortem/`](labs/lab-11-incident-postmortem/) | Lab | 45–60 min. Vérifier que le hook d'audit est actif (`/hooks`) **avant** l'injection. Ne pas dire quel scénario est injecté |
| 46 | [`solution/trainer/inject-contract-break.sh`](labs/lab-11-incident-postmortem/solution/trainer/inject-contract-break.sh) | Ne pas distribuer | Scénario A (Dev), voir le détail ci-dessous |
| 47 | [`solution/trainer/inject-secret-rotation.sh`](labs/lab-11-incident-postmortem/solution/trainer/inject-secret-rotation.sh) | Ne pas distribuer | Scénario B (DevOps), voir le détail ci-dessous |
| 48 | `slides/03` p. 21–26 → [`labs/capstone/`](labs/capstone/) | Lab | 2 h, en binômes Dev + DevOps. Épreuve croisée à 1:20 ; restitution de 10 min par binôme ; grille d'évaluation (§ 8) |
| 49 | `slides/03` p. 27 · [`docs/garde-fous.md`](docs/garde-fous.md) § 5 | Projeter, puis montrer | Clôture : la grille d'auto-contrôle avant d'utiliser l'agent sur un vrai dépôt, et le plan 30/60/90 |

### Lab 11 — injecter les incidents

Les deux scripts refusent de s'exécuter hors de leur cadre. Ils ne s'utilisent que sur un
environnement de lab.

| | Scénario A — Dev | Scénario B — DevOps |
|---|---|---|
| Pré-requis | Lab 04 et Lab 10 parcours Dev ; dépôt du participant **propre** (le script refuse sinon) | Lab 08 ou 09 ; contexte kubectl `k3d-ecom-dev` (le script refuse sinon) |
| Commande | `"$FORMATION/labs/lab-11-incident-postmortem/solution/trainer/inject-contract-break.sh" <dépôt-du-participant>` | `"$FORMATION/labs/lab-11-incident-postmortem/solution/trainer/inject-secret-rotation.sh"`, sur le poste du participant |
| Effet | Quatre commits locaux, la régression noyée au deuxième. L'énoncé commence par `git pull` : si l'injection se fait dans un clone, **pousser** ensuite | Le Secret `catalog-db` est remplacé sans changer le mot de passe PostgreSQL, puis les pods Catalog sont recréés |
| Symptôme à annoncer | « Des commandes sont enregistrées à 0,00 € » | « Le catalogue est vide et les commandes échouent » |

---

## Pendant les quatre jours

**Un participant en retard.** Les corrigés sont **cumulatifs** : appliquer, dans l'ordre, la
section « Corrigé » de chaque lab manquant. Dépendances à respecter (détail dans
[`labs/README.md`](labs/README.md)) :

- tout lab suppose le Lab 01 (dépôt GitHub) ;
- 05, 10 et 11 A supposent le 04 (la base) ;
- 08 suppose le 07 (les images) ;
- 09, 10 B et 11 B supposent le 08 (le cluster).

**Le groupe prend du retard.** Dans l'ordre, sacrifier : le Lab 09, le parcours 4B du Lab 10,
puis l'étape 8 du capstone (livrer par `docker compose`). Ne jamais sacrifier l'étape 10 du
capstone : l'incident est le cœur du message.

**Un terme accroche** → [`docs/glossaire.md`](docs/glossaire.md). **Une commande oubliée** →
[`docs/cheatsheet.md`](docs/cheatsheet.md). **Une panne de poste** → le tableau de dépannage du
[README](README.md#dépannage).

---

## Après la session — maintenance du dépôt

- Rappeler aux participants de **supprimer leurs jetons** (GitHub, clé d'API de test).
- Un énoncé à corriger : modifier le Markdown d'abord, puis reporter la correction dans le deck
  correspondant (02 pour un module, 03 pour un lab). Les sources Beamer sont dans
  `../dev-devops-claude-code_latex/` (`make all`). Ne jamais éditer un PDF.
- Un fichier de corrigé modifié : vérifier les labs suivants qui fournissent le même fichier
  (corrigés cumulatifs).
- Relancer les vérifications de [`CLAUDE.md`](CLAUDE.md) § Vérifier, puis supprimer `bin/`, `obj/`
  et `TestResults/`.
