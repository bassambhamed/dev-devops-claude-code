# Supports de présentation

Les **PDF** distribués aux participants. Les sources Beamer vivent à côté du dépôt, dans
[`../dev-devops-claude-code_latex/`](../../dev-devops-claude-code_latex/) (`make all` les recompile et
les publie ici).

| Support | Pages | Contenu | Quand |
|---|:---:|---|---|
| [`00-plan-formation.pdf`](00-plan-formation.pdf) | 22 | Objectifs, publics Dev & DevOps, progression justifiée par les cas d'usage, programme 4 jours, application fil rouge, garde-fous R1–R6 | Ouverture J1 |
| [`01-fondations-ia-dev-devops.pdf`](01-fondations-ia-dev-devops.pdf) | 26 | LLM, agents, prompt structuré (exemples .NET et Kubernetes), les 13 techniques du [TP](../tp/TP_Prompt_Engineering_Dev_DevOps.md), risques en banque | J1 matin |
| [`02-claude-code-briques.pdf`](02-claude-code-briques.pdf) | 61 | Les briques des modules 00 à 08, dans l'ordre du parcours — chaque section s'ouvre sur **la limite** et ses cas Dev / DevOps ; plugins et MCP approfondis ; l'annexe hors chaîne (l'agent sans terminal) ; arbre de décision | J1 après-midi → J3 |
| [`03-labs-dev-devops.pdf`](03-labs-dev-devops.pdf) | 27 | Lancement de chaque lab (objectif, briques, livrable, garde-fous, limite révélée), parcours Dev / DevOps des labs 10 et 11, capstone | À chaque lab |

Le deck 02 suit les modules un pour un ; le deck 03 suit les énoncés de [`labs/`](../labs/). En cas
d'écart, **les Markdown font foi** : corrigez-les d'abord, puis la source LaTeX.
