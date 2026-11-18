# src/commande.py
"""
Dernière étape de l'assistant : la structure produite par le modèle devient une
commande git.

    git_push | remote=origin | branch=main   ->   git push origin main

La conversion est mécanique et ne fait confiance à rien : une intention hors
ontologie ou un slot obligatoire manquant donne None, pour ne jamais exécuter
une commande que le modèle aurait inventée.
"""
import shlex

from src.data import parse_target


def to_command(target: str) -> str | None:
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
