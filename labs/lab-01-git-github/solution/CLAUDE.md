# ecommerce-app

Application e-commerce de démonstration (formation Claude Code Dev & DevOps). Données fictives.

## Stack
- .NET 10 / ASP.NET Core, orchestré par .NET Aspire (`src/ECommerce.AppHost`).
- `Catalog.Api`, `Ordering.Api` : minimal APIs + EF Core. `Gateway` : reverse proxy YARP.
  `Web` : Blazor Server. `ServiceDefaults` : OpenTelemetry, health checks, résilience HTTP.
- Ordering appelle Catalog en HTTP synchrone pour valider chaque produit.

## Commandes
```bash
export PATH="/usr/local/share/dotnet:$PATH"
dotnet build ECommerce.slnx                 # toujours la solution, jamais un projet seul
dotnet test ECommerce.slnx
dotnet run --project src/ECommerce.AppHost   # dashboard Aspire : URL + jeton dans la console
```

## Conventions
- Les services s'appellent par NOM via le service discovery Aspire (`https+http://catalog`) :
  jamais d'URL ni de port en dur.
- Toute nouvelle route publique est aussi déclarée dans le Gateway (`appsettings.json`, `ReverseProxy`).
- Branches : `feat/`, `fix/`, `chore/`, `test/`, `ci/` — jamais de travail direct sur `main`.
- Commits : Conventional Commits, en anglais, à l'impératif. Scopes : catalog, ordering, gateway, web, apphost, db, ci.
- Un comportement ajouté ou corrigé = un test d'intégration dans `tests/`.

## Interdits
- Aucune donnée client (nom, e-mail) dans un log, une trace ou un message d'exception.
- Aucun secret dans le code ni dans `appsettings*.json` : `dotnet user-secrets` ou variable d'environnement.
- Ne jamais modifier un test pour faire passer un build : corriger le code.
- Ne jamais merger une PR, ne jamais forcer un push.
