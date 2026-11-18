# prompt_lab.py
"""
TP3 — LE LABO DE PROMPT : mesurer le modèle de BASE (sans fine-tuning), guidé
par un prompt système, sur le jeu de son choix. Aucun entraînement : rapide.

  # mesurer un prompt sur un jeu (validation, test ou reserve)
  uv run python prompt_lab.py prompts/systeme.txt validation

  # fabriquer un prompt enrichi d'exemples
  uv run python prompt_lab.py --construire exemples-train   # 1 exemple par intention, pris dans le TRAIN
  uv run python prompt_lab.py --construire triche-test      # les phrases du TEST (interdit !)

Chaque mesure est tracée dans MLflow (expérience tp3-prompt-lab), avec un nom
lisible « <prompt> @ <jeu> ». Lire le test ou la réserve incrémente le compteur
de lectures du projet.
"""
import sys
from pathlib import Path

import mlflow

from src.config import settings
from src.data import SPLIT_NAMES, examples_for_prompt
from src.model import load_base_model
from src.evaluation import evaluate_split, print_split_report, load_prompt, rows_to_text
from src.tracking import log_run, count_sealed_read, warn_sealed_read

BASE_PROMPT = Path("prompts/systeme.txt")
BUILDS = {
    # nom : (jeu source, un exemple par intention ?, fichier produit)
    "exemples-train": ("train", True, Path("prompts/exemples_train.txt")),
    "triche-test": ("test", False, Path("prompts/triche_test.txt")),
}


def build_prompt(kind: str) -> Path:
    source, one_per_intent, out = BUILDS[kind]
    text = BASE_PROMPT.read_text(encoding="utf-8").strip()
    # on n'ajoute pas un exemple déjà présent dans la consigne de base
    pairs = [(u, t) for u, t in examples_for_prompt(source, one_per_intent=one_per_intent)
             if f"{u} -> {t}" not in text]
    text += "\nAutres exemples :\n" + "\n".join(f"{u} -> {t}" for u, t in pairs) + "\n"
    out.write_text(text, encoding="utf-8")
    print(f"Prompt écrit : {out}  ({len(pairs)} exemples tirés du jeu « {source} »)")
    if source == "test":
        print("⚠️  Ce prompt contient les phrases du TEST SCELLÉ : c'est de la triche, "
              "volontaire, pour la démonstration du chapitre 7.")
    return out


def measure(prompt_path: str, split: str) -> None:
    if split not in SPLIT_NAMES or split == "train":
        sys.exit(f"Jeu attendu : validation, test ou reserve (reçu : {split})")
    if not Path(prompt_path).is_file():
        sys.exit(f"Fichier de prompt introuvable : {prompt_path}  (voir le dossier prompts/)")
    prompt = load_prompt(prompt_path)

    settings.configure_environment()
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    if split in ("test", "reserve"):
        warn_sealed_read(split, count_sealed_read(split))
    mlflow.set_experiment(settings.mlflow_prompt_experiment_name)

    model, tokenizer = load_base_model(settings.model_name)   # PAS de LoRA
    metrics, rows = evaluate_split(model, tokenizer, split, system=prompt)
    nom = Path(prompt_path).stem
    print_split_report(f"Modèle de base + prompt « {nom} » sur le jeu « {split} »",
                       metrics, rows)

    with mlflow.start_run(run_name=f"{nom} @ {split}"):
        mlflow.log_params({"prompt": nom, "jeu": split, "model_name": settings.model_name})
        log_run({"intent_acc": metrics["intent_acc"], "slot_f1": metrics["slot_f1"],
                 "exact": metrics["exact"]},
                texts={"prompt.txt": prompt + "\n", f"predictions_{split}.txt": rows_to_text(rows)})
    print(f"\nMesure tracée dans MLflow (expérience {settings.mlflow_prompt_experiment_name}).")


def main(argv):
    if len(argv) == 2 and argv[0] == "--construire" and argv[1] in BUILDS:
        build_prompt(argv[1])
    elif len(argv) == 2 and not argv[0].startswith("--"):
        measure(argv[0], argv[1])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
