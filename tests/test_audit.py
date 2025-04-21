from subprocess import CompletedProcess
from orgwarden.audit import audit_repository, KNOWN_MODULES
from pytest import MonkeyPatch
from types import SimpleNamespace

from orgwarden.repository import Repository
from tests.constants import GITHUB_PAT, ORGWARDEN_REPO, ORGWARDEN_URL

# RepoAuditor is run via cli
repo_auditor_IMPORT_PATH = "subprocess.run"


def test_repo_auditor_called_correctly(monkeypatch: MonkeyPatch):
    mock_repo_auditor_called = False

    def mock_repo_auditor(cmd: str, shell: bool, text: bool) -> CompletedProcess[str]:
        nonlocal mock_repo_auditor_called
        mock_repo_auditor_called = True
        assert shell, text
        assert (
            cmd
            == f"uv run repo_auditor --include GitHub --GitHub-url {ORGWARDEN_URL} --GitHub-pat {GITHUB_PAT}"
        )
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(repo_auditor_IMPORT_PATH, mock_repo_auditor)
    exit_code = audit_repository(
        ORGWARDEN_REPO, GITHUB_PAT, audit_settings=None, modules=None
    )
    assert exit_code == 0
    assert mock_repo_auditor_called


def test_specific_modules(monkeypatch: MonkeyPatch):
    MODULES = ["module1", "module2", "module3"]

    def mock_repo_auditor(cmd: str, *args, **kwargs):
        for module in MODULES:
            assert f"--include {module}" in cmd
        # ensure default modules not included
        for module in KNOWN_MODULES:
            assert f"--include {module}" not in cmd
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(repo_auditor_IMPORT_PATH, mock_repo_auditor)
    exit_code = audit_repository(
        ORGWARDEN_REPO, gh_pat=GITHUB_PAT, audit_settings=None, modules=MODULES
    )
    assert exit_code == 0


def test_repo_specifc_cli_flags(monkeypatch: MonkeyPatch):
    REPO = Repository(name="test_repo", url="test_url", org="test_org")
    FLAGS_DICT = {
        "other_repo": "--flag-3",
        "test_repo": "--flag-1 --flag-2",
    }

    def mock_repo_auditor(cmd: str, *args, **kwargs):
        assert " --flag-1 --flag-2" in cmd
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(repo_auditor_IMPORT_PATH, mock_repo_auditor)
    exit_code = audit_repository(
        REPO, gh_pat=GITHUB_PAT, audit_settings=FLAGS_DICT, modules=None
    )
    assert exit_code == 0
