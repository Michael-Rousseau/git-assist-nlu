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
| `train.csv` | 150 | 15 |
| `validation.csv` | 40 | 4 |
| `test.csv` | 40 | 4 |

## Choix

- Tailles conseillées par l'énoncé : 15 phrases par intention pour apprendre, 4
  pour la validation, 4 pour le test.
- Nombre de pas choisi sur la validation uniquement (batch de 2, soit 75 pas par
  époque) :

| pas | époques | val_intent_acc | val_exact | best_val_loss |
|---|---|---|---|---|
| 100 | 1,3 | 72 % | 62 % | 1.60 |
| 200 | 2,7 | 90 % | 88 % | 1.01 |
| **300** | **4** | **100 %** | **100 %** | **0.86** |
| 400 | 5,3 | 95 % | 95 % | 0.83 |
| 500 | 6,7 | 98 % | 98 % | 0.81 |

  Run retenu : 300 pas, meilleur score sur la validation. Au-delà, la perte baisse
  encore un peu mais les scores ne montent plus : l'écart entre 300, 400 et 500
  pas tient à une ou deux phrases sur 40.
- Prompt système : celui généré depuis l'ontologie (`prompts/systeme.txt`). Il n'a
  **pas** été réglé : ni `make prompt-systeme` ni `make prompt-exemples` n'ont été
  mesurés sur la validation.
- Correctif du squelette : `src/generate.py` n'envoyait pas l'entrée sur le device
  du modèle, ce qui plantait sur Mac (MPS). Ajout de `.to(model.device)`.
- Ajouts propres au projet : `src/commande.py` (structure → commande git) et
  `demo.py`.

## Résultat sur le test (40 phrases)

| | LoRA | base | base+prompt |
|---|---|---|---|
| intent_acc | 92 % (37/40) | 0 % | 0 % |
| slot_f1 | 90 % | 12 % | 19 % |
| exact | 88 % (35/40) | 0 % | 0 % |

Porte : PASS (seuil 70 %, marge 30 points, avance mesurée +92 points).

## Lectures du test, et histoire des données

`lectures_test = 1` pour le test livré : une seule lecture, par `make juger`, une
fois données et réglages figés. Rien n'a été modifié ensuite.

Ce compteur ne dit pas tout, voici l'histoire complète :

1. **Premier essai** (squelette du TP3) : train 60, un test de 20 phrases lu une
   fois.
2. **Version 1 du projet** : ce premier test a été versé dans le train (80
   phrases), et un autre test de 20 phrases, jamais lu, a servi à juger. Une
   lecture. Résultat : 90 % d'intentions, 70 % de réponses exactes.
3. **Version 2, livrée ici** : le train de 80 phrases étant au minimum de
   l'énoncé, il a été porté à 150. Le test de la version 1, déjà lu, a été versé
   dans le train, et **un test neuf de 40 phrases a été écrit**, puis lu une seule
   fois. L'expérience MLflow a changé de nom (`projet-nlu-v2`), d'où le compteur
   reparti de zéro.

Aucun réglage n'a donc été choisi en regardant le test qui sert à juger. En
revanche, les erreurs des deux tests précédents étaient connues au moment
d'écrire les nouvelles phrases d'entraînement.

## Limites

- **Colonne base+prompt faible** : le prompt n'a pas été réglé, donc l'avance de
  92 points surestime l'avantage du fine-tuning face à un prompt soigné.
- **Petit test** : 40 phrases, une phrase vaut 2,5 points.
- **Même auteur pour train et test** : le test n'a pas été écrit par quelqu'un
  d'autre, les tournures se ressemblent sûrement. Le test croisé devrait donner
  un score plus bas.
- **Erreurs observées sur le test** (5 sur 40) :
  - intention fausse, et dangereuse : « je retourne sur la branche main » →
    `git_branch_delete | branch=main`, soit `git branch -d main` ;
  - intention fausse : « ramène main depuis origin » → `git_restore | file=main` ;
  - intention fausse et slot inventé en anglais : « prends tous les fichiers
    modifiés pour le prochain commit » → `git_checkout | file=modified` ;
  - slot inventé : `count=1` pour « quels commits ont été faits récemment » ;
  - valeur tronquée : `deploy.sh` au lieu de `scripts/deploy.sh`.
- **Une erreur peut être destructrice** : la structure est toujours bien formée,
  même quand l'intention est fausse. Avant d'exécuter, il faudrait une
  confirmation de l'utilisateur, au moins pour `git_branch_delete` et
  `git_restore`.
- **Demandes hors périmètre** : une demande que l'ontologie ne couvre pas (un
  rebase, par exemple) est rangée de force dans une intention connue.
- Les commandes ne sont pas exécutées : la mesure porte sur la structure, pas sur
  l'effet dans un dépôt. Rendue en commande, la sortie du modèle est identique à
  l'attendu pour 35 phrases sur 40.
