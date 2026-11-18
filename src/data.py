# src/data.py
"""
Projet — langage naturel -> commande git.

Une demande en français -> une STRUCTURE fermée (même format qu'au TP3) :

    <intent> | <slot_type>=<valeur> | ...
    ex :  "pousse la branche main sur origin"  ->  git_push | remote=origin | branch=main

La structure se convertit ensuite mécaniquement en commande (to_command) :

    git_push | remote=origin | branch=main   ->   git push origin main

Corpus rédigé à la main pour ce projet. QUATRE ensembles disjoints :
  • TRAIN (60) : appris (6 phrases par intention).
  • VALIDATION (20) : pour RÉGLER (nombre de pas, prompt...), autant qu'on veut.
  • TEST (20) : SCELLÉ — formulations et valeurs inédites, lu UNE fois pour JUGER.
  • RÉSERVE (20) : un second test, pour la démonstration de l'overfitting adaptatif.
"""
import shlex

from datasets import Dataset

ALLOWED_INTENTS = [
    "git_commit", "git_add", "git_branch_create", "git_branch_delete", "git_checkout",
    "git_merge", "git_push", "git_pull", "git_log", "git_restore",
]
SLOT_TYPES = ["message", "file", "branch", "remote", "count"]


def build_target(intent: str, slots) -> str:
    if not slots:
        return intent
    return intent + " | " + " | ".join(f"{t}={v}" for t, v in slots)


# (phrase, intent, [(slot_type, valeur)])
_TRAIN = [
    ("commit avec le message fix du parser", "git_commit", [("message", "fix du parser")]),
    ("enregistre mes changements avec le message ajout des tests", "git_commit", [("message", "ajout des tests")]),
    ("fais un commit intitulé mise à jour du readme", "git_commit", [("message", "mise à jour du readme")]),
    ("valide le travail avec comme message correction du login", "git_commit", [("message", "correction du login")]),
    ("commite ça avec le message nettoyage du code", "git_commit", [("message", "nettoyage du code")]),
    ("crée un commit nommé première version", "git_commit", [("message", "première version")]),
    ("ajoute main.py à l'index", "git_add", [("file", "main.py")]),
    ("stage le fichier config.yaml", "git_add", [("file", "config.yaml")]),
    ("prépare readme.md pour le prochain commit", "git_add", [("file", "readme.md")]),
    ("ajoute tous les fichiers", "git_add", []),
    ("mets src/app.py dans la zone de staging", "git_add", [("file", "src/app.py")]),
    ("indexe le fichier tests/test_api.py", "git_add", [("file", "tests/test_api.py")]),
    ("crée une branche feature-login", "git_branch_create", [("branch", "feature-login")]),
    ("nouvelle branche appelée hotfix-paiement", "git_branch_create", [("branch", "hotfix-paiement")]),
    ("ouvre une branche dev", "git_branch_create", [("branch", "dev")]),
    ("fais-moi une branche nommée refonte-ui", "git_branch_create", [("branch", "refonte-ui")]),
    ("démarre une nouvelle branche experimental", "git_branch_create", [("branch", "experimental")]),
    ("crée la branche release-2", "git_branch_create", [("branch", "release-2")]),
    ("supprime la branche feature-login", "git_branch_delete", [("branch", "feature-login")]),
    ("efface la branche test-vieux", "git_branch_delete", [("branch", "test-vieux")]),
    ("enlève la branche hotfix-paiement", "git_branch_delete", [("branch", "hotfix-paiement")]),
    ("détruis la branche brouillon", "git_branch_delete", [("branch", "brouillon")]),
    ("vire la branche dev", "git_branch_delete", [("branch", "dev")]),
    ("retire la branche release-1", "git_branch_delete", [("branch", "release-1")]),
    ("va sur la branche main", "git_checkout", [("branch", "main")]),
    ("bascule sur dev", "git_checkout", [("branch", "dev")]),
    ("passe sur la branche feature-login", "git_checkout", [("branch", "feature-login")]),
    ("change de branche pour release-2", "git_checkout", [("branch", "release-2")]),
    ("retourne sur main", "git_checkout", [("branch", "main")]),
    ("place-toi sur la branche hotfix-paiement", "git_checkout", [("branch", "hotfix-paiement")]),
    ("fusionne la branche dev", "git_merge", [("branch", "dev")]),
    ("merge feature-login dans la branche courante", "git_merge", [("branch", "feature-login")]),
    ("intègre la branche hotfix-paiement", "git_merge", [("branch", "hotfix-paiement")]),
    ("fusionne release-2 ici", "git_merge", [("branch", "release-2")]),
    ("fais un merge de refonte-ui", "git_merge", [("branch", "refonte-ui")]),
    ("incorpore la branche experimental", "git_merge", [("branch", "experimental")]),
    ("pousse sur origin", "git_push", [("remote", "origin")]),
    ("envoie la branche main sur origin", "git_push", [("remote", "origin"), ("branch", "main")]),
    ("pousse mes commits", "git_push", []),
    ("publie dev sur upstream", "git_push", [("remote", "upstream"), ("branch", "dev")]),
    ("push la branche feature-login vers origin", "git_push", [("remote", "origin"), ("branch", "feature-login")]),
    ("envoie mon travail sur le dépôt upstream", "git_push", [("remote", "upstream")]),
    ("récupère les changements de origin", "git_pull", [("remote", "origin")]),
    ("tire la branche main depuis origin", "git_pull", [("remote", "origin"), ("branch", "main")]),
    ("mets à jour mon dépôt local", "git_pull", []),
    ("pull dev depuis upstream", "git_pull", [("remote", "upstream"), ("branch", "dev")]),
    ("ramène les derniers commits de upstream", "git_pull", [("remote", "upstream")]),
    ("récupère la branche release-2 de origin", "git_pull", [("remote", "origin"), ("branch", "release-2")]),
    ("montre l'historique", "git_log", []),
    ("affiche les 5 derniers commits", "git_log", [("count", "5")]),
    ("montre l'historique du fichier main.py", "git_log", [("file", "main.py")]),
    ("liste les 10 derniers commits", "git_log", [("count", "10")]),
    ("quels sont les 3 derniers commits sur readme.md", "git_log", [("count", "3"), ("file", "readme.md")]),
    ("affiche le journal des commits", "git_log", []),
    ("annule mes modifications sur main.py", "git_restore", [("file", "main.py")]),
    ("restaure le fichier config.yaml", "git_restore", [("file", "config.yaml")]),
    ("abandonne tous mes changements locaux", "git_restore", []),
    ("remets readme.md dans son état d'origine", "git_restore", [("file", "readme.md")]),
    ("jette les modifs de src/app.py", "git_restore", [("file", "src/app.py")]),
    ("annule les changements non commités", "git_restore", []),
]
_VAL = [
    ("fais un commit avec le message refonte du menu", "git_commit", [("message", "refonte du menu")]),
    ("enregistre ça sous le message correction des typos", "git_commit", [("message", "correction des typos")]),
    ("ajoute utils.py à l'index", "git_add", [("file", "utils.py")]),
    ("stage tout", "git_add", []),
    ("crée une branche bugfix-cache", "git_branch_create", [("branch", "bugfix-cache")]),
    ("nouvelle branche nommée essai", "git_branch_create", [("branch", "essai")]),
    ("supprime la branche essai", "git_branch_delete", [("branch", "essai")]),
    ("efface la branche bugfix-cache", "git_branch_delete", [("branch", "bugfix-cache")]),
    ("bascule sur la branche release-1", "git_checkout", [("branch", "release-1")]),
    ("va sur experimental", "git_checkout", [("branch", "experimental")]),
    ("fusionne la branche bugfix-cache", "git_merge", [("branch", "bugfix-cache")]),
    ("merge main ici", "git_merge", [("branch", "main")]),
    ("pousse la branche dev sur origin", "git_push", [("remote", "origin"), ("branch", "dev")]),
    ("envoie mes commits sur upstream", "git_push", [("remote", "upstream")]),
    ("tire les changements depuis upstream", "git_pull", [("remote", "upstream")]),
    ("récupère la branche dev de origin", "git_pull", [("remote", "origin"), ("branch", "dev")]),
    ("affiche les 2 derniers commits", "git_log", [("count", "2")]),
    ("montre l'historique de config.yaml", "git_log", [("file", "config.yaml")]),
    ("annule mes modifications sur utils.py", "git_restore", [("file", "utils.py")]),
    ("abandonne mes changements", "git_restore", []),
]
# TEST SCELLÉ : formulations et valeurs inédites (test de généralisation)
_TEST = [
    ("sauvegarde mon travail dans un commit qui s'appelle ajout du cache", "git_commit", [("message", "ajout du cache")]),
    ("commit rapide, message : suppression des logs", "git_commit", [("message", "suppression des logs")]),
    ("inclus docker-compose.yml dans le prochain commit", "git_add", [("file", "docker-compose.yml")]),
    ("ajoute le dossier docs à la zone de staging", "git_add", [("file", "docs")]),
    ("j'ai besoin d'une nouvelle branche api-v2", "git_branch_create", [("branch", "api-v2")]),
    ("prépare une branche qui s'appelle migration-db", "git_branch_create", [("branch", "migration-db")]),
    ("débarrasse-moi de la branche api-v1", "git_branch_delete", [("branch", "api-v1")]),
    ("la branche migration-db ne sert plus, supprime-la", "git_branch_delete", [("branch", "migration-db")]),
    ("je veux travailler sur la branche api-v2", "git_checkout", [("branch", "api-v2")]),
    ("reviens sur la branche staging", "git_checkout", [("branch", "staging")]),
    ("ramène le contenu de api-v2 dans ma branche par un merge", "git_merge", [("branch", "api-v2")]),
    ("fusionne staging avec la branche actuelle", "git_merge", [("branch", "staging")]),
    ("envoie api-v2 vers le remote origin", "git_push", [("remote", "origin"), ("branch", "api-v2")]),
    ("publie mon travail", "git_push", []),
    ("synchronise-moi avec origin", "git_pull", [("remote", "origin")]),
    ("va chercher la branche staging sur upstream", "git_pull", [("remote", "upstream"), ("branch", "staging")]),
    ("qu'est-ce qui a été commité récemment", "git_log", []),
    ("donne-moi les 7 derniers commits de makefile", "git_log", [("count", "7"), ("file", "makefile")]),
    ("défais ce que j'ai changé dans docker-compose.yml", "git_restore", [("file", "docker-compose.yml")]),
    ("remets tout comme au dernier commit", "git_restore", []),
]
# RÉSERVE : un second test, jamais consulté avant la démonstration finale
_RESERVE = [
    ("valide tout ça, message : passage à python 3.12", "git_commit", [("message", "passage à python 3.12")]),
    ("fais un commit appelé ajout du dockerfile", "git_commit", [("message", "ajout du dockerfile")]),
    ("mets pyproject.toml dans l'index", "git_add", [("file", "pyproject.toml")]),
    ("ajoute tout ce qui a changé", "git_add", []),
    ("il me faut une branche perf-tests", "git_branch_create", [("branch", "perf-tests")]),
    ("crée-moi la branche docs-fr", "git_branch_create", [("branch", "docs-fr")]),
    ("la branche docs-fr est inutile, enlève-la", "git_branch_delete", [("branch", "docs-fr")]),
    ("fais disparaître la branche perf-tests", "git_branch_delete", [("branch", "perf-tests")]),
    ("rends-toi sur la branche docs-fr", "git_checkout", [("branch", "docs-fr")]),
    ("je passe sur perf-tests", "git_checkout", [("branch", "perf-tests")]),
    ("intègre perf-tests dans ma branche", "git_merge", [("branch", "perf-tests")]),
    ("fais la fusion de la branche docs-fr", "git_merge", [("branch", "docs-fr")]),
    ("pousse docs-fr sur upstream", "git_push", [("remote", "upstream"), ("branch", "docs-fr")]),
    ("envoie tout sur origin", "git_push", [("remote", "origin")]),
    ("récupère ce qu'il y a de nouveau", "git_pull", []),
    ("tire perf-tests depuis origin", "git_pull", [("remote", "origin"), ("branch", "perf-tests")]),
    ("montre-moi les 4 derniers commits", "git_log", [("count", "4")]),
    ("qui a modifié pyproject.toml dernièrement", "git_log", [("file", "pyproject.toml")]),
    ("oublie mes modifs sur pyproject.toml", "git_restore", [("file", "pyproject.toml")]),
    ("reviens à la version propre de src/model.py", "git_restore", [("file", "src/model.py")]),
]

_SPLITS = {"train": _TRAIN, "validation": _VAL, "test": _TEST, "reserve": _RESERVE}
SPLIT_NAMES = tuple(_SPLITS)


def _to_dataset(rows) -> Dataset:
    return Dataset.from_dict({
        "instruction": [u for (u, _i, _s) in rows],
        "response": [build_target(i, s) for (_u, i, s) in rows],
    })


def get_train_dataset() -> Dataset:
    return _to_dataset(_TRAIN)


def get_validation_dataset() -> Dataset:
    return _to_dataset(_VAL)


def get_test_dataset() -> Dataset:
    return _to_dataset(_TEST)


def get_reserve_dataset() -> Dataset:
    return _to_dataset(_RESERVE)


def get_split(name: str) -> Dataset:
    """Un jeu par son nom : train, validation, test ou reserve."""
    if name not in _SPLITS:
        raise ValueError(f"Jeu inconnu : {name} (attendu : {', '.join(SPLIT_NAMES)})")
    return _to_dataset(_SPLITS[name])


def examples_for_prompt(name: str, one_per_intent: bool = False):
    """Paires (phrase, cible) d'un jeu, pour les écrire dans un prompt."""
    pairs, seen = [], set()
    for u, i, s in _SPLITS[name]:
        if one_per_intent and i in seen:
            continue
        seen.add(i)
        pairs.append((u, build_target(i, s)))
    return pairs


def assert_disjoint() -> None:
    """Garde-fou : aucune phrase commune entre deux jeux."""
    sets = {n: {u for (u, *_r) in rows} for n, rows in _SPLITS.items()}
    names = list(sets)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            commun = sets[names[a]] & sets[names[b]]
            assert not commun, f"Fuite de données entre {names[a]} et {names[b]} : {commun}"


# ── Parsing + scoring de la sortie ─────────────────────────────────────
_ARTICLES = {"le", "la", "les", "un", "une", "des"}


def _norm_value(v: str) -> str:
    """minuscules + retrait d'un article en tête (la valeur ; pas le type)."""
    v = v.strip().lower()
    if v.startswith("l'"):
        v = v[2:].strip()
    toks = v.split()
    if toks and toks[0] in _ARTICLES:
        v = " ".join(toks[1:])
    return v.strip()


def parse_target(text: str):
    """Ligne -> (intent, set[(type,valeur)]) normalisés."""
    line = text.strip().splitlines()[0] if text.strip() else ""
    parts = [p.strip() for p in line.split("|")]
    intent = parts[0].strip().lower() if parts else ""
    slots = set()
    for p in parts[1:]:
        if "=" in p:
            t, v = p.split("=", 1)
            slots.add((t.strip().lower(), _norm_value(v)))
    return intent, slots


def score(pred: str, gold: str):
    """(intent_ok, slot_f1, exact_match)."""
    pi, ps = parse_target(pred)
    gi, gs = parse_target(gold)
    intent_ok = (pi == gi)
    tp = len(ps & gs)
    prec = tp / len(ps) if ps else (1.0 if not gs else 0.0)
    rec = tp / len(gs) if gs else 1.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else (1.0 if not gs and not ps else 0.0)
    exact = intent_ok and (ps == gs)
    return intent_ok, f1, exact


def to_command(target: str) -> str | None:
    """Structure -> commande git. None si la structure n'est pas exécutable
    (intention inconnue, ou slot obligatoire manquant)."""
    intent, slot_set = parse_target(target)
    slots = dict(slot_set)
    branch, file = slots.get("branch"), slots.get("file")
    args = None
    if intent == "git_commit" and slots.get("message"):
        args = ["commit", "-m", slots["message"]]
    elif intent == "git_add":
        args = ["add", file] if file else ["add", "-A"]
    elif intent == "git_branch_create" and branch:
        args = ["branch", branch]
    elif intent == "git_branch_delete" and branch:
        args = ["branch", "-d", branch]
    elif intent == "git_checkout" and branch:
        args = ["switch", branch]
    elif intent == "git_merge" and branch:
        args = ["merge", branch]
    elif intent in ("git_push", "git_pull"):
        # git exige le remote dès qu'une branche est précisée
        remote = slots.get("remote") or ("origin" if branch else None)
        args = [intent.removeprefix("git_")] + [a for a in (remote, branch) if a]
    elif intent == "git_log":
        args = ["log"]
        if slots.get("count", "").isdigit():
            args += ["-n", slots["count"]]
        if file:
            args += ["--", file]
    elif intent == "git_restore":
        args = ["restore", file or "."]
    return shlex.join(["git"] + args) if args else None


def format_chat(example, tokenizer) -> str:
    """Met un exemple au format conversation (renvoie une chaîne)."""
    messages = [
        {"role": "user", "content": example["instruction"]},
        {"role": "assistant", "content": example["response"]},
    ]
    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=False, enable_thinking=False
    )
