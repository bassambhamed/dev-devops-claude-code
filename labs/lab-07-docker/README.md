# Lab 07 — Conteneurisation

> **Durée :** 45 min · **Modules requis :** [04](../../modules/04-hooks/), [05](../../modules/05-skills/)
> · **Outils :** Docker, `trivy` · **Corrigé :** [`solution/`](solution/) (vérifié)

---

## 1. Objectif

Conteneuriser les quatre services avec des images **petites, non-root, sans secret et scannées**,
et lancer toute la pile — **PostgreSQL compris** — avec `docker compose`, sans Aspire. Ce sont ces
images que le cluster du [Lab 08](../lab-08-kubernetes/) exécutera.

## 2. Pré-requis

```bash
docker info >/dev/null && trivy --version
dotnet build ECommerce.slnx      # la solution compile (labs 04 et 05 appliqués)
```

> **Port 8080 occupé ?** Le frontend compose est publié sur `8080`. Si un autre outil l'utilise,
> changez le port publié dans `docker-compose.yml` (`"18080:8080"`).

## 3. Briques mobilisées — et pourquoi chacune

| Brique | Rôle | Pourquoi celle-ci |
|---|---|---|
| **Skill** `containerize` | La doctrine d'image : multi-stage, chiselée, non-root, cache du restore | Une procédure avec des pièges connus : un savoir-faire |
| **Hook** `scan-image` (`PostToolUse`) | Scanner chaque image construite par l'agent | Personne ne pense à scanner à chaque build ; le harnais, si |
| **Hook** `guard-destructive` (plugin) | Bloquer `docker system prune`, `docker compose down -v` | Une base locale effacée ne se récupère pas |
| **CI** `images.yml` | Bloquer une image vulnérable ou root avant fusion | Le contrôle de dernier recours, hors de portée de l'agent |

---

## 4. Déroulé pas-à-pas

### Étape 1 — Le premier Dockerfile (10 min)

```bash
cd ~/lab-ecommerce && git switch -c build/containers && claude
```
```text
> /plan Écris src/ECommerce.Catalog.Api/Dockerfile : build multi-étapes .NET 10, image finale
  aspnet:10.0-noble-chiseled non-root, port 8080, contexte de build = racine du dépôt.
  Aucune chaîne de connexion dans l'image. Ajoute le .dockerignore qui va avec.
```

Le skill `containerize` se déclenche. Faites expliquer **pourquoi** le `.dockerignore` exclut
`bin/` et `obj/` (un `restore` du poste copié dans l'image fait échouer `--no-restore` avec
`NETSDK1064`).

```bash
docker build -t ecommerce-catalog:dev -f src/ECommerce.Catalog.Api/Dockerfile .
docker inspect --format '{{.Config.User}}' ecommerce-catalog:dev      # un UID (1654), jamais vide ni 0
```

> **Piège vérifié :** `docker run --rm <image> id` ne marche **pas** sur une image chiselée — il
> n'y a ni shell ni commande `id` (`exec: "sh": executable file not found`). C'est précisément
> l'intérêt de l'image. On vérifie l'utilisateur avec `docker inspect`, ou `docker top` sur un
> conteneur lancé.

### Étape 2 — Le scan automatique (10 min)

```bash
cp "$FORMATION/labs/lab-07-docker/solution/.claude/hooks/scan-image.sh" .claude/hooks/
chmod +x .claude/hooks/scan-image.sh
```

Câblez-le en `PostToolUse` sur `Bash`, avec `timeout: 180` (voir
[`solution/.claude/settings.json`](solution/.claude/settings.json)). Puis faites reconstruire
l'image par l'agent. Sans vulnérabilité *CRITICAL*, le hook reste silencieux ; sinon, il renvoie
le résumé à l'agent :

```text
> Pour chaque vulnérabilité remontée : est-elle exploitable dans notre contexte (image sans
  shell, pas de réseau entrant direct, service interne derrière le gateway) ? Classe par
  criticité RÉELLE et propose la remédiation minimale.
```

> Un scanner produit du volume ; la valeur de l'agent est de **qualifier**. Et le `timeout` n'est
> pas un détail : un moteur Docker en mauvais état peut faire attendre un hook indéfiniment.

### Étape 3 — Généraliser (5 min)

```text
> Applique la même doctrine à Ordering.Api, Gateway et Web. Pour Web, tiens compte des assets
  statiques de wwwroot.
```

### Étape 4 — La pile complète, PostgreSQL compris (15 min)

```text
> /plan Écris docker-compose.yml : postgres:17-alpine avec healthcheck pg_isready et volume ;
  catalog qui attend postgres « healthy » et reçoit ConnectionStrings__catalogdb ; ordering,
  gateway, web, avec le service discovery recâblé par les variables services__<nom>__http__0.
  Le mot de passe vient de .env (non versionné) : compose doit REFUSER de démarrer sans lui.
  Seul web publie un port.
```

```bash
echo "CATALOG_DB_PASSWORD=$(openssl rand -hex 24)" > .env      # hexadécimal : sans ; ni =
git check-ignore .env && echo ".env bien ignoré"
docker compose up -d --build
docker compose ps                                               # postgres (healthy), 4 services Up
curl -s http://localhost:8080/products | grep -o 'All categories\|in stock' | sort | uniq -c
```

Attendu (vérifié) : la page catalogue affiche les données **lues dans PostgreSQL** via le gateway.
Testez le garde-fou de compose : `mv .env .env.bak && docker compose config` → refus explicite ;
`mv .env.bak .env`.

### Étape 5 — Ce que l'agent ne fera pas (5 min)

```text
> Repars de zéro : arrête tout et supprime les volumes avec docker compose down -v.
```

**Refusé** par `guard-destructive`. Si vous voulez vraiment repartir de zéro, c'est votre
décision : `docker compose down -v`, vous-même.

### Étape 6 — Le contrôle en CI (optionnel, 5 min)

```bash
cp "$FORMATION/labs/lab-07-docker/solution/.github/workflows/images.yml" .github/workflows/
```

Chaque PR qui touche `src/` construit les quatre images, **échoue** si l'une tourne en root, et
**échoue** sur une vulnérabilité *CRITICAL* corrigeable.

---

## 5. Livrable

```
src/ECommerce.{Catalog.Api,Ordering.Api,Gateway,Web}/Dockerfile
.dockerignore · docker-compose.yml · .env.example        # .env : local, ignoré par Git
.claude/hooks/scan-image.sh                              # + câblage PostToolUse
.github/workflows/images.yml                             # build, non-root, Trivy — bloquant
```

## 6. Garde-fous

| Règle | Mécanisme | Garantie |
|---|---|---|
| Aucun conteneur root | `USER $APP_UID` + vérification `docker inspect` + CI | Contrôle (CI) |
| Aucun secret dans une image | Doctrine du skill ; injection au démarrage | Consigne + revue |
| Mot de passe de base hors dépôt | `.env` ignoré ; `${VAR:?…}` fait échouer compose | Contrôle |
| Toute image est scannée | Hook `scan-image` (poste) + `images.yml` (CI) | Contrôle |
| Pas de suppression de volume par l'agent (R2) | Hook `guard-destructive` | Contrôle |

## 7. Pour aller plus loin

- Comparez la taille de `aspnet:10.0` et `aspnet:10.0-noble-chiseled` ; faites expliquer l'écart.
- Générez un SBOM (`trivy image --format cyclonedx`) et faites-le analyser.
- Épinglez les images de base **par digest** (`@sha256:…`) et discutez du coût de mise à jour.

## 8. La limite révélée

Compose lance la pile sur **un** poste, sans redémarrage automatique, sans montée en charge, sans
contrôle de santé de la plateforme. Et le mot de passe de base y circule dans une variable d'un
fichier `.env` : acceptable sur un poste, pas sur un environnement partagé.

> **→ [Lab 08 — Kubernetes](../lab-08-kubernetes/)**

## Corrigé

```bash
S="$FORMATION/labs/lab-07-docker/solution"
for svc in Catalog.Api Ordering.Api Gateway Web; do cp "$S/src/ECommerce.$svc/Dockerfile" ~/lab-ecommerce/src/ECommerce.$svc/; done
cp "$S/"{docker-compose.yml,.dockerignore,.env.example} ~/lab-ecommerce/
cp "$S/.claude/hooks/scan-image.sh" ~/lab-ecommerce/.claude/hooks/
```

Vérifications faites : les quatre images construites ; utilisateur `1654` (non-root) ; pile
compose démarrée avec PostgreSQL *healthy* et page catalogue servie depuis la base ; refus de
compose sans `.env` ; extraction du tag par le hook testée sur `-t` et `--tag=`.
