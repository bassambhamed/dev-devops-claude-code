# Lab 02 — Tests automatisés

> **Durée :** 60 min · **Modules requis :** [04](../../modules/04-hooks/), [05](../../modules/05-skills/)
> · **Outils :** `dotnet`, `jq` · **Corrigé :** [`solution/`](solution/)

---

## 1. Objectif

Doter l'application d'une suite de tests d'intégration **utile** — endpoints du catalogue, logique
de commande avec un faux service Catalog —, et rendre deux règles **inévitables** :

1. chaque fichier C# écrit par l'agent est formaté ;
2. l'agent **ne peut pas conclure** une tâche si du code a changé et que les tests sont rouges.

> **« Je suis DevOps, pourquoi des tests ? »** Parce que la question que vous posez chaque jour est
> *« est-ce que je peux déployer ça ? »*. Une suite de tests est la réponse automatisable — et
> c'est elle que la CI du [Lab 06](../lab-06-ci-cd/) exécutera.

## 2. Pré-requis

- [Lab 01](../lab-01-git-github/) terminé (dépôt initialisé, correctif de quantité appliqué).
- Les hooks `guard-destructive` et `secret-scan` du [module 04](../../modules/04-hooks/) actifs.
- Le skill `gen-tests` du [module 05](../../modules/05-skills/).

## 3. Briques mobilisées — et pourquoi chacune

| Brique | Rôle | Pourquoi celle-ci et pas une autre |
|---|---|---|
| **Skill** `gen-tests` | La doctrine de test de l'équipe | Écrire un test demande du **jugement** (quel niveau, quels cas) : c'est un savoir-faire, pas une règle |
| **Hook** `PostToolUse` `format-cs` | Formater chaque `.cs` écrit | Doit s'appliquer **à chaque fois**, sans que personne y pense |
| **Hook** `Stop` `tests-must-pass` | Interdire de conclure sur des tests rouges | « Ne conclus pas si c'est rouge » dans `CLAUDE.md` serait une consigne ; ici c'est un **contrôle** |
| **Commande** `/review-diff` | Relire avant commit | Déclenchée par vous, au moment de livrer |

---

## 4. Déroulé pas-à-pas

### Étape 1 — Comprendre avant de tester (10 min)

```bash
cd ~/lab-ecommerce && git switch -c test/integration-suite && claude
```
```text
> Liste les comportements observables de CatalogEndpoints.cs et de OrderingEndpoints.cs :
  entrées, sorties, codes HTTP, cas d'erreur, appels à d'autres services.
  Ne génère aucun test pour l'instant.
```

**Cette étape n'est pas facultative.** Des tests écrits sans comprendre le comportement attendu
valident le code tel qu'il est — bugs compris.

### Étape 2 — Le hook de formatage (5 min)

Si ce n'est pas fait au module 04 :

```bash
cp "$FORMATION/labs/lab-02-tests/solution/.claude/hooks/format-cs.sh" .claude/hooks/
chmod +x .claude/hooks/format-cs.sh
```

Ajoutez-le en `PostToolUse` (matcher `Write|Edit|MultiEdit`) dans `.claude/settings.json`.

### Étape 3 — Les tests du catalogue (15 min)

```text
> Crée le projet tests/ECommerce.Catalog.Tests (xUnit), ajoute-le à ECommerce.slnx, et écris
  des tests d'intégration des endpoints du catalogue : liste, lecture par id, id inexistant,
  id non entier, création puis relecture, et /health.
```

Le skill `gen-tests` doit se déclencher seul. **Le point de friction attendu :** les *top-level
statements* génèrent une classe `Program` **interne** ; `WebApplicationFactory<Program>` ne la
voit pas. L'agent doit ajouter `public partial class Program { }` à la fin de `Program.cs` — s'il
ne le fait pas, donnez-lui l'erreur de compilation : la boucle *agir → observer → corriger*.

```bash
dotnet test ECommerce.slnx
```

### Étape 4 — La logique de commande, avec un faux Catalog (15 min)

C'est le test que la revue du Lab 01 a réclamé :

```text
> Crée tests/ECommerce.Ordering.Tests : teste la création de commande sans démarrer Catalog,
  en remplaçant le handler HTTP du client typé CatalogServiceClient par un faux catalogue.
  Couvre : le total avec plusieurs quantités, une commande vide, une quantité nulle ou
  négative, un produit inconnu.
```

Le skill doit consulter sa [doctrine](solution/.claude/skills/gen-tests/doctrine.md) pour le faux
handler. Si le test échoue sur la résolution de `catalog`, donnez l'indice : le service discovery
attend `services:catalog:http:0` dans la configuration de test.

### Étape 5 — Le hook qui interdit de conclure sur du rouge (10 min)

```bash
cp "$FORMATION/labs/lab-02-tests/solution/.claude/hooks/tests-must-pass.sh" .claude/hooks/
chmod +x .claude/hooks/tests-must-pass.sh
```

Câblez-le sur l'événement `Stop` (voir [`solution/.claude/settings.json`](solution/.claude/settings.json)),
relancez `claude`, vérifiez `/hooks`. Puis provoquez la situation :

```text
> Simplifie la création de commande : pas besoin de gérer les quantités, mets Quantity = 1
  partout. Dis-moi quand c'est fini.
```

L'agent modifie, veut conclure… et le hook refuse : le test du total est rouge. L'agent **reprend
la main** avec le message du hook. Deux issues correctes : il revient sur la modification, ou il
vous explique que la demande contredit un comportement testé. Une issue **incorrecte** : il
modifie le test. Si c'est le cas, rappelez la règle et inscrivez-la :

```text
> # ne jamais modifier un test pour faire passer un build : corriger le code
```

> Lisez le script : il ne s'exécute que si des `.cs`, `.csproj` ou `.razor` ont changé, et il
> laisse conclure au second passage (`stop_hook_active`) pour éviter une boucle infinie.

### Étape 6 — Livrer (5 min)

```text
> /review-diff
> /ship suite de tests d'intégration Catalog et Ordering
```

---

## 5. Livrable

```
tests/
├── ECommerce.Catalog.Tests/          # 5 tests d'intégration
└── ECommerce.Ordering.Tests/         # 4 tests, faux Catalog
ECommerce.slnx                        # référence les deux projets
.claude/skills/gen-tests/             # SKILL.md + doctrine.md
.claude/hooks/format-cs.sh            # PostToolUse
.claude/hooks/tests-must-pass.sh      # Stop
.claude/settings.json                 # câblage
```

## 6. Garde-fous

| Règle | Mécanisme | Garantie |
|---|---|---|
| Le code écrit est formaté | Hook `PostToolUse` | Contrôle |
| Pas de conclusion sur tests rouges | Hook `Stop` | Contrôle |
| Ne jamais affaiblir un test | `gen-tests` + `CLAUDE.md` | Consigne (le hook `Stop` la rend visible) |
| Aucune donnée réelle dans les tests | Doctrine du skill | Consigne |

## 7. Pour aller plus loin

- Ajoutez au hook `Stop` un `dotnet build` des seuls projets touchés, pour gagner du temps.
- Mesurez la couverture : `dotnet test --collect:"XPlat Code Coverage"` — et discutez de ce que le
  chiffre **ne dit pas**.
- Essayez le plugin officiel `hookify` : décrivez une règle en français, il en fait un hook.

## 8. La limite révélée

Votre `.claude/` contient maintenant trois commandes, quatre hooks, deux skills. Deux constats :

- **Ils ne servent qu'à vous.** Vos collègues n'en ont aucun ; et si vous corrigez un hook, il
  faut le recopier dans chaque dépôt.
- **Le retour est tardif.** Le hook `Stop` vous apprend une erreur de type après un
  `dotnet test` complet. Un serveur de langage C# la signalerait juste après l'édition — et il
  existe déjà, maintenu par d'autres.

> **→ [Module 06 — Plugins](../../modules/06-plugins/) :** consommer ce qui existe (`csharp-lsp`),
> packager ce qui vous est propre, distribuer en une commande.

## Corrigé

```bash
cp -r "$FORMATION/labs/lab-02-tests/solution/tests" ~/lab-ecommerce/
cp -r "$FORMATION/labs/lab-02-tests/solution/.claude/skills/gen-tests" ~/lab-ecommerce/.claude/skills/
cp "$FORMATION/labs/lab-02-tests/solution/.claude/hooks/"*.sh ~/lab-ecommerce/.claude/hooks/
# settings.json : fusionnez avec le vôtre plutôt que d'écraser — voir solution/.claude/settings.json
```

Voir [`solution/tests/README.md`](solution/tests/README.md) pour la mise en place (`public partial
class Program`, ajout à la solution). Corrigé **vérifié** : 9 tests verts, hook `Stop` testé
sur les cas rouge, vert et anti-boucle.
