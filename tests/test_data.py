# tests/test_data.py  —  lancer avec :  make test
import pytest

from src.data import (
    ALLOWED_INTENTS, SLOT_TYPES, SPLIT_NAMES,
    get_train_dataset, get_validation_dataset, get_test_dataset, get_reserve_dataset,
    get_split, assert_disjoint, score, examples_for_prompt, parse_target, to_command,
)


def test_sizes_and_disjoint():
    assert len(get_train_dataset()) == 60
    assert len(get_validation_dataset()) == 20
    assert len(get_test_dataset()) == 20
    assert len(get_reserve_dataset()) == 20
    assert_disjoint()


def test_get_split():
    assert len(get_split("reserve")) == 20
    with pytest.raises(ValueError):
        get_split("inconnu")


@pytest.mark.parametrize("split", SPLIT_NAMES)
def test_every_target_respects_the_ontology_and_renders_a_command(split):
    intents_seen = set()
    for example in get_split(split):
        intent, slots = parse_target(example["response"])
        intents_seen.add(intent)
        assert intent in ALLOWED_INTENTS, example
        assert all(slot_type in SLOT_TYPES for slot_type, _ in slots), example
        assert to_command(example["response"]) is not None, example
    assert intents_seen == set(ALLOWED_INTENTS)


def test_scoring_exact_and_intent():
    assert score("git_push | remote=origin", "git_push | remote=origin") == (True, 1.0, True)
    # bonne intention, slot de mauvais TYPE -> intention ok mais pas exact
    intent_ok, _f1, exact = score("git_checkout | file=main", "git_checkout | branch=main")
    assert intent_ok is True and exact is False


def test_to_command():
    assert to_command("git_push | remote=origin | branch=main") == "git push origin main"
    assert to_command("git_pull | branch=dev") == "git pull origin dev"
    assert to_command("git_commit | message=fix du parser") == "git commit -m 'fix du parser'"
    assert to_command("git_log | count=3 | file=readme.md") == "git log -n 3 -- readme.md"
    assert to_command("git_restore") == "git restore ."
    # slot obligatoire manquant, ou intention hors ontologie : rien d'exécutable
    assert to_command("git_merge") is None
    assert to_command("git_rebase | branch=main") is None


def test_prompt_examples():
    pairs = examples_for_prompt("train", one_per_intent=True)
    assert len(pairs) == 10
    assert pairs[0] == ("commit avec le message fix du parser",
                        "git_commit | message=fix du parser")
    assert len(examples_for_prompt("test")) == 20
