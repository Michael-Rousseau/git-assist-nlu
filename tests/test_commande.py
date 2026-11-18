# tests/test_commande.py  —  lancer avec :  make test
import pytest

from src.commande import to_command
from src.data import read_csv


@pytest.mark.parametrize("target, command", [
    ("git_push | remote=origin | branch=main", "git push origin main"),
    ("git_push", "git push"),
    ("git_pull | branch=dev", "git pull origin dev"),
    ("git_commit | message=fix du parser", "git commit -m 'fix du parser'"),
    ("git_add", "git add -A"),
    ("git_branch_create | branch=api-v2", "git branch api-v2"),
    ("git_branch_delete | branch=api-v2", "git branch -d api-v2"),
    ("git_checkout | branch=main", "git switch main"),
    ("git_log | count=3 | file=readme.md", "git log -n 3 -- readme.md"),
    ("git_restore", "git restore ."),
])
def test_renders_the_git_command(target, command):
    assert to_command(target) == command


@pytest.mark.parametrize("target", ["git_merge", "git_commit", "git_rebase | branch=main", ""])
def test_refuses_what_cannot_be_executed(target):
    assert to_command(target) is None


@pytest.mark.parametrize("split", ["train", "validation", "test"])
def test_every_expected_answer_of_the_corpus_renders_a_command(split):
    for phrase, reponse in read_csv(f"donnees/{split}.csv"):
        assert to_command(reponse) is not None, phrase
