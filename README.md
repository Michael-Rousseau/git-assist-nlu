# Assistant git — langage naturel → commande git (LoRA sur Qwen3-0.6B)

Projet NLU : une demande en français devient une structure fermée, convertible
en commande git.

```
« pousse la branche main sur origin »
 -> git_push | remote=origin | branch=main
 -> git push origin main
```

- 10 intentions : `git_commit`, `git_add`, `git_branch_create`, `git_branch_delete`,
  `git_checkout`, `git_merge`, `git_push`, `git_pull`, `git_log`, `git_restore`.
- 5 types de slots : `message`, `file`, `branch`, `remote`, `count`.
- Données rédigées pour le projet : train 80, validation 20, test 20.

## Organisation du dépôt

| Dossier | Contenu |
|---|---|
| `exercice-projet-nlu/` | **le projet rendu** : données (`donnees/`), code, livrable (`livrables/`) |
| racine (`main.py`, `src/`, …) | premier essai, dans le squelette du TP3 (données dans `src/data.py`, avec `to_command()` qui rend la commande git) |

## Résultats (`exercice-projet-nlu/`)

Réglage sur la validation :

| pas | val_intent_acc | val_exact | best_val_loss |
|---|---|---|---|
| 60 | 45 % | 40 % | 2.22 |
| 100 | 85 % | 70 % | 1.42 |
| 150 | 95 % | 95 % | 1.05 |
| **200** | **95 %** | **95 %** | **0.90** |
| 300 | 95 % | 90 % | 0.81 |

Jugement sur le test (20 phrases, lu une fois) : **PASS**.

| | LoRA | base | base+prompt |
|---|---|---|---|
| intent_acc | 90 % | 0 % | 0 % |
| slot_f1 | 82 % | 10 % | 10 % |
| exact | 70 % | 0 % | 0 % |

Choix, limites et erreurs détaillés : `exercice-projet-nlu/donnees/NOTES.md`.

## Livrable

`exercice-projet-nlu/livrables/livrable_groupe-michael-rousseau.zip` (2,1 Mo) :
adaptateur LoRA, données, prompt, notes, rapport.

## Refaire le cycle

```
cd exercice-projet-nlu
cp .env.example .env
make setup      # MLflow + RustFS (Docker)
uv sync
make valider    # vérifier les données
make run        # régler : entraîner + mesurer sur la validation
make juger      # juger : porte de qualité sur le test
make livrer     # fabriquer le livrable
make evaluer    # le réévaluer sans MLflow ni Docker
```

Énoncé : `exercice-projet-nlu/EXERCICE_PROJET_NLU.md`.
