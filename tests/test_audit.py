from subprocess import CompletedProcess
from orgwarden.audit import audit_repository
import pytest
from pytest import CaptureFixture, MonkeyPatch

from orgwarden.repository import Repository
from tests.constants import ORGWARDEN_REPO, ORGWARDEN_URL


def test_no_repository():
    with pytest.raises(TypeError):
        audit_repository()


def test_invalid_repository(capfd: CaptureFixture):
    exit_code = audit_repository(
        repo=Repository(
            name="invalid-repo", url="https://example.com", org="invalid-org"
        ),
        gh_pat=None,
    )
    assert exit_code != 0
    stdout = capfd.readouterr().out
    assert "not a valid GitHub repository" in stdout


def test_orgwarden_repo_no_token(capfd: CaptureFixture):
    _ = audit_repository(repo=ORGWARDEN_REPO, gh_pat=None)
    # cannot check exit_code, as this is dependent on whether OrgWarden passes audit
    stdout = capfd.readouterr().out
    assert "Results: DONE!" in stdout
    assert ORGWARDEN_URL in stdout
    assert "not a valid GitHub repository" not in stdout
    assert "please provide the GitHub PAT" in stdout


def test_orgwarden_repo_with_token(capfd: CaptureFixture, monkeypatch: MonkeyPatch):
    PAT = "github_pat_123"
    mock_repo_auditor_called = False

    def mock_repo_auditor(cmd: str, shell: bool, text: bool) -> CompletedProcess[str]:
        nonlocal mock_repo_auditor_called
        mock_repo_auditor_called = True
        assert shell, text
        assert ORGWARDEN_URL in cmd
        assert PAT in cmd
        print("DONE!")
        return CompletedProcess(args=None, returncode=0)

    monkeypatch.setattr("subprocess.run", mock_repo_auditor)
    exit_code = audit_repository(repo=ORGWARDEN_REPO, gh_pat=PAT)
    assert mock_repo_auditor_called
    assert exit_code == 0
    stdout = capfd.readouterr().out
    assert "DONE!" in stdout


def test_repo_specifc_cli_flags(monkeypatch: MonkeyPatch):
    REPO = Repository(
        name="test_repo",
        url="test_url",
        org="test_org",
        cli_flags="--GitHub-AutoMerge-false --GitHub-License-value MIT",
    )

    mock_repo_auditor_called = False

    def mock_repo_auditor(cmd: str, shell: bool, text: bool) -> CompletedProcess[str]:
        nonlocal mock_repo_auditor_called
        mock_repo_auditor_called = True
        assert shell, text
        assert REPO.url in cmd
        assert f" {REPO.cli_flags}" in cmd
        return CompletedProcess(args=None, returncode=0)

    monkeypatch.setattr("subprocess.run", mock_repo_auditor)
    exit_code = audit_repository(REPO, gh_pat=None)
    assert mock_repo_auditor_called
    assert exit_code == 0
