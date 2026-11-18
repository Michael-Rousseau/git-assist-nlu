# Notes — assistant git (langage naturel → commande git)

## Sujet

Une demande en français devient une structure fermée, convertible mécaniquement
en commande git :

```
« pousse la branche main sur origin »  ->  git_push | remote=origin | branch=main  ->  git push origin main
```

10 intentions (`git_commit`, `git_add`, `git_branch_create`, `git_branch_delete`,
`git_checkout`, `git_merge`, `git_push`, `git_pull`, `git_log`, `git_restore`) et
5 types de slots (`message`, `file`, `branch`, `remote`, `count`).

## Source des données et licence

Toutes les phrases ont été rédigées pour ce projet, avec l'aide d'un assistant IA
(Claude), puis vérifiées par `make valider` (0 erreur, 0 avertissement). Aucun jeu
de données externe, aucune donnée personnelle ni donnée d'entreprise. Pas de
licence tierce à citer.

| Fichier | Phrases | Par intention |
|---|---|---|
| `train.csv` | 80 | 8 |
| `validation.csv` | 20 | 2 |
| `test.csv` | 20 | 2 |

## Choix

- Train au minimum demandé (8 par intention), pas aux 15 conseillés.
- Nombre de pas choisi sur la validation uniquement :

| pas | val_intent_acc | val_exact | best_val_loss |
|---|---|---|---|
| 60 | 45 % | 40 % | 2.22 |
| 100 | 85 % | 70 % | 1.42 |
| 150 | 95 % | 95 % | 1.05 |
| **200** | **95 %** | **95 %** | **0.90** |
| 300 | 95 % | 90 % | 0.81 |

  Run retenu : 200 pas (égalité avec 150 sur les scores, départagée par la perte
  de validation, règle de `juger.py`).
- Prompt système : celui généré depuis l'ontologie (`prompts/systeme.txt`). Il n'a
  **pas** été réglé : ni `make prompt-systeme` ni `make prompt-exemples` n'ont été
  mesurés sur la validation.
- Correctif du squelette : `src/generate.py` n'envoyait pas l'entrée sur le device
  du modèle, ce qui plantait sur Mac (MPS). Ajout de `.to(model.device)`. Cinq runs
  en échec, sans mesure, restent dans MLflow pour cette raison.

## Résultat sur le test (20 phrases)

| | LoRA | base | base+prompt |
|---|---|---|---|
| intent_acc | 90 % | 0 % | 0 % |
| slot_f1 | 82 % | 10 % | 10 % |
| exact | 70 % | 0 % | 0 % |

Porte : PASS (seuil 70 %, marge 30 points, avance mesurée +90 points).

## Lectures du test

`lectures_test = 1` : une seule lecture, par `make juger`, une fois données et
réglages figés. Aucune modification des données ni des réglages ensuite.

À savoir sur l'origine de ces 20 phrases : un premier essai du même sujet a été
fait dans le squelette du TP3, avec un autre test de 20 phrases, lu une fois. Ce
premier test a ensuite été versé dans le train, et le test actuel est l'ancienne
« réserve » de cet essai, jamais lue avant ce jugement.

## Limites

- **Colonne base+prompt faible** : le prompt n'a pas été réglé, donc l'avance de
  90 points surestime l'avantage du fine-tuning face à un prompt soigné.
- **Petit test** : 20 phrases, une phrase vaut 5 points.
- **Même auteur pour train et test** : le test n'a pas été écrit par quelqu'un
  d'autre, les tournures se ressemblent sûrement. Le test croisé devrait donner
  un score plus bas.
- **Erreurs observées sur le test** (6 sur 20) :
  - intention inventée, hors ontologie : `git_integration` pour « intègre
    perf-tests dans ma branche » ;
  - intention fausse : `git_restore` pour « envoie tout sur origin » ;
  - slots inventés, hors ontologie : `summary=…`, `user=git` ;
  - slot oublié : la branche dans « tire perf-tests depuis origin » ;
  - valeur tronquée : `pyproject.tom` ;
  - « tout » pris pour un fichier : `file=change` pour « ajoute tout ce qui a changé ».
- **Sortie non contrainte** : rien n'empêche le modèle de sortir une étiquette
  hors ontologie. Un filtre sur la liste fermée serait nécessaire avant d'exécuter
  une commande.
- Les commandes ne sont pas exécutées : la mesure porte sur la structure, pas sur
  l'effet dans un dépôt.
