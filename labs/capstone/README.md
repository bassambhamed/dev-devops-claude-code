# Capstone — une fonctionnalité, de l'idée à la production observée

> **Durée :** 2 h (J4 après-midi) · **Pré-requis :** tous les modules, labs 01 à 11
> · **Format :** binômes **Dev + DevOps** · **Restitution :** 10 min par binôme

---

## 1. Objectif

Livrer **une fonctionnalité réelle** de bout en bout, en n'utilisant que Claude Code et les
briques construites pendant la formation — puis la défendre sous pression lors d'une épreuve
croisée. Ce n'est pas un lab de plus : c'est la preuve que les briques **tiennent ensemble**.

### La fonctionnalité

> **Gérer la marque des produits.** Un produit a une marque (optionnelle). Le catalogue est
> filtrable par marque, dans l'API et dans l'interface. La création de commande expose, en
> télémétrie, le nombre de commandes par marque. Le tout est livré sur le cluster.

Elle touche **toutes** les couches : schéma (migration), API (contrat), tests, front, télémétrie,
image, chart, CI. Le binôme se répartit le travail, pas les responsabilités : chacun relit l'autre.

## 2. Règles du jeu

1. **Tout passe par l'agent**, sauf ce que vos garde-fous vous obligent à faire vous-même — c'est le but.
2. **`/hooks` vérifié en début de session** : tous les garde-fous du poste standard actifs.
3. **Chaque changement passe par une PR**, relue par la CI (`ci.yml`, `claude-review.yml`) **et** par le binôme.
4. **Aucun mot de passe** dans un fichier, un prompt ou une sortie de commande.
5. **Rien de réel** : k3d, PostgreSQL local, comptes de test.

## 3. La chaîne à dérouler

```
  1. Cadrer         /goal, /plan ; découpage en PR                              [Modules 01-02]
  2. Schéma         migration Brand, SQL relu, db-reviewer + MCP catalogdb      [Lab 04]
  3. API & tests    filtre ?brand=, test de contrat, Testcontainers             [Labs 02, 04, 11]
  4. Front          filtre par marque, états, a11y, vérification dans Chrome    [Lab 05]
  5. Télémétrie     tag brand (cardinalité maîtrisée !), test MeterListener     [Lab 10]
  6. Livrer         PR, CI verte, revue Claude, merge par un humain             [Lab 06]
  7. Conteneuriser  images reconstruites, scannées                              [Lab 07]
  8. Déployer       helm upgrade --dry-run relu, puis upgrade par un humain     [Labs 08-09]
  9. Observer       la métrique par marque visible (Aspire ou Grafana)          [Lab 10]
 10. Éprouver       incident injecté par le binôme adverse, post-mortem         [Lab 11]
 11. Capitaliser    une amélioration du plugin d'équipe, version incrémentée    [Module 06]
```

> **Le piège de l'étape 5.** Un tag `brand` sur une métrique est acceptable si le nombre de
> marques reste petit ; un tag `productId` ou `customer` ne l'est jamais (cardinalité, R1).
> Faites-le justifier par l'agent — et par le skill `observability`.

## 4. Déroulé (2 h)

| Temps | Phase | Attendu |
|:---:|---|---|
| 0:00–0:10 | **Cadrage** | `/goal`, `/hooks`, découpage en PR, répartition Dev / DevOps |
| 0:10–0:55 | **Construire** | Étapes 2 à 5 : migration relue, API testée, front vérifié, télémétrie |
| 0:55–1:20 | **Livrer** | Étapes 6 à 9 : CI verte, images, chart, application observée sur le cluster |
| 1:20–1:45 | **Épreuve croisée** | Étape 10 : incident chez vous, injecté par un autre binôme |
| 1:45–2:00 | **Capitaliser & préparer** | Étape 11, plan 30/60/90, restitution |

> **Si vous prenez du retard,** sacrifiez l'étape 8 (le déploiement Helm) et livrez via
> `docker compose`. Ne sacrifiez **jamais** l'étape 10 : l'incident est le cœur du message.

## 5. L'épreuve croisée

À 1:20, échangez les postes. L'autre binôme injecte **une** panne de son choix, sans vous dire
laquelle — un contrat cassé, une migration piégée, un Secret désaligné, une limite mémoire, une
donnée personnelle glissée dans un log. Vous avez 25 minutes pour :

1. **Détecter** — par la télémétrie, pas parce qu'on vous a prévenus.
2. **Diagnostiquer** — avec `incident-analyst`, en lecture seule.
3. **Rétablir** — en respectant vos propres garde-fous.
4. **Empêcher la récurrence** — un test, un hook, ou un skill, committé.
5. **Écrire** le post-mortem avec le skill `postmortem`.

**Ce qui est évalué :** votre outillage vous a-t-il servi sous pression, ou gêné ? Les deux
réponses sont instructives — la seconde vous dit quoi corriger lundi.

## 6. Livrables

```
<votre-dépôt>/
├── CLAUDE.md · .claude/settings.json · .mcp.json      # contexte, plugins d'équipe, MCP sans secret
├── src/ … Migrations/…_AddProductBrand.cs             # la fonctionnalité
├── tests/                                             # dont le test de contrat et le test de métrique
├── .github/workflows/                                 # ci, cd (gate), claude-review, security, images
├── helm/ecommerce/                                    # version du chart incrémentée
├── docs/
│   ├── decisions.md                                   # les choix et leur justification
│   └── postmortems/                                   # le post-mortem de l'épreuve
└── (marketplace) le plugin d'équipe, version incrémentée
```

## 7. Restitution — 10 minutes par binôme

1. **La chaîne** (3 min) — en direct : une PR jusqu'au cluster, la métrique visible.
2. **Les garde-fous** (3 min) — **montrez** un blocage réel, pas un slide. Pourquoi ce contrôle
   est-il au bon niveau (hook, permission, plateforme) ?
3. **L'incident** (2 min) — la panne, la preuve, le MTTR, l'action qui empêche la récurrence.
4. **Le plan** (2 min) — vos trois cas d'usage prioritaires et votre plan 30/60/90.

## 8. Grille d'évaluation

| Critère | Poids | Ce qu'on regarde |
|---|:---:|---|
| La fonctionnalité fonctionne de bout en bout | 25 % | Filtre par marque dans l'API et l'interface, sur le cluster |
| Garde-fous actifs et **démontrés** | 25 % | Un blocage réel ; aucun secret nulle part |
| Qualité des artefacts | 20 % | Migration relue, tests de contrat, rendu Helm relu, a11y |
| Incident et post-mortem | 15 % | Preuve citée, action de récurrence vérifiable, blameless |
| Capitalisation | 15 % | Plugin amélioré, versionné, installable |

> Un binôme qui livre une chaîne **partielle mais correctement cadrée** passe devant un binôme qui
> livre tout sans garde-fou. C'est le message central de la formation.

## 9. Le plan 30/60/90 jours

| Horizon | Attendu | Exemple |
|---|---|---|
| **30 jours** | Un `CLAUDE.md` et le poste standard sur **un** dépôt réel ; les hooks de garde actifs | « Notre dépôt API a ses conventions, son anti-secret, son audit » |
| **60 jours** | Le plugin d'équipe publié sur un marketplace interne ; MCP base en lecture seule | « Les 12 développeurs ont la même configuration » |
| **90 jours** | La revue headless dans la CI ; indicateurs mesurés (délai de revue, MTTR) | « On sait chiffrer ce que ça nous a apporté » |

**Les trois questions à traiter :**

1. Quel est votre cas d'usage n° 1 — celui qui vous coûte le plus de temps aujourd'hui ?
2. Quel garde-fou doit être en place **avant** de le lancer sur un dépôt réel ?
3. Qui est propriétaire du `CLAUDE.md`, du plugin d'équipe, et de la revue de ce que l'agent produit ?
