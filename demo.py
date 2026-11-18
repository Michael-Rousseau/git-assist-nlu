# demo.py
"""
Essayer l'assistant : une phrase -> la structure du modèle -> la commande git.

  uv run python demo.py "pousse la branche main sur origin"
  uv run python demo.py                      # mode interactif
  uv run python demo.py --livrable autre.zip "crée une branche dev"

Le modèle est reconstruit à partir du LIVRABLE (modèle de base public +
adaptateur LoRA du zip), sans MLflow ni Docker. Rien n'est exécuté : la
commande est seulement affichée.
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

from evaluer_livrable import charger, extraire
from src.commande import to_command
from src.generate import generate_answer


def default_deliverable() -> Path:
    archives = sorted(Path("livrables").glob("livrable_*.zip"))
    if len(archives) != 1:
        sys.exit("Précise le livrable :  uv run python demo.py --livrable livrables/<fichier>.zip")
    return archives[0]


def answer(model, tokenizer, phrase: str) -> None:
    structure = generate_answer(model, tokenizer, phrase)
    command = to_command(structure) or "(aucune : sortie hors ontologie ou incomplète)"
    print(f"phrase    : {phrase}\nstructure : {structure}\ncommande  : {command}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("phrases", nargs="*")
    parser.add_argument("--livrable", type=Path)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        racine = extraire(args.livrable or default_deliverable(), Path(tmp))
        rapport = json.loads((racine / "rapport.json").read_text(encoding="utf-8"))
        model, tokenizer = charger(racine, rapport)

    for phrase in args.phrases:
        answer(model, tokenizer, phrase)
    if args.phrases:
        return
    print("Tape une demande (Entrée vide pour quitter).")
    while (phrase := input("> ").strip()):
        answer(model, tokenizer, phrase)


if __name__ == "__main__":
    main()
