import json
from subprocess import CompletedProcess
from types import SimpleNamespace
import pytest
from pytest import MonkeyPatch
from orgwarden.repo_crawler import APIError, AuthError, fetch_org_repos
from orgwarden.repository import Repository
from tests.constants import (
    TECH_AI_ORG_NAME,
    GITHUB_HOSTNAME,
)

# gh is run via cli
gh_IMPORT_PATH = "subprocess.run"


def test_missing_org():
    with pytest.raises(ValueError, match="empty string"):
        _ = fetch_org_repos(org_name="", hostname="host")


def test_missing_hostname():
    with pytest.raises(ValueError, match="empty string"):
        _ = fetch_org_repos(org_name="org", hostname="")


def test_gh_not_installed(monkeypatch: MonkeyPatch):
    mock_which_called = False

    def mock_which(cmd: str) -> str | None:
        nonlocal mock_which_called
        mock_which_called = True
        assert cmd == "gh"
        return None

    monkeypatch.setattr("shutil.which", mock_which)
    with pytest.raises(FileNotFoundError, match="GitHub CLI is not installed"):
        _ = fetch_org_repos("org", "host")
    assert mock_which_called


def test_gh_called_correctly(monkeypatch: MonkeyPatch):
    mock_gh_called = False

    def mock_gh(cmd: str, shell: bool, capture_output: bool) -> CompletedProcess[str]:
        nonlocal mock_gh_called
        mock_gh_called = True
        assert shell, capture_output
        assert TECH_AI_ORG_NAME in cmd, GITHUB_HOSTNAME in cmd
        return SimpleNamespace(stderr=None, stdout="[]")

    monkeypatch.setattr(gh_IMPORT_PATH, mock_gh)

    _ = fetch_org_repos(TECH_AI_ORG_NAME, GITHUB_HOSTNAME)
    assert mock_gh_called


def test_invalid_auth(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(
        gh_IMPORT_PATH,
        lambda *args, **kwargs: SimpleNamespace(stderr="Must authenticate"),
    )
    with pytest.raises(AuthError, match="Must authenticate"):
        _ = fetch_org_repos("org", "host")


def test_generic_api_error(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(
        gh_IMPORT_PATH,
        lambda *args, **kwargs: SimpleNamespace(stderr="Some general API error"),
    )
    with pytest.raises(APIError, match="Some general API error"):
        _ = fetch_org_repos("org", "host")


def test_invalid_json_response(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(
        gh_IMPORT_PATH, lambda *args, **kwargs: SimpleNamespace(stderr="", stdout="{}")
    )
    with pytest.raises(APIError, match="JSON response does not match"):
        _ = fetch_org_repos(TECH_AI_ORG_NAME, GITHUB_HOSTNAME)


def test_api_response_parsing(monkeypatch: MonkeyPatch):
    JSON_OUTPUT = [
        {
            "name": "repo1",
            "html_url": "url1",
            "private": False,
            "fork": False,
        },
        {
            "name": "repo2",
            "html_url": "url2",
            "private": False,
            "fork": False,
        },
        {
            "name": "repo3",
            "html_url": "url3",
            "private": False,
            "fork": False,
        },
    ]
    EXPECTED_REPOS = [
        Repository("repo1", "url1", TECH_AI_ORG_NAME),
        Repository("repo2", "url2", TECH_AI_ORG_NAME),
        Repository("repo3", "url3", TECH_AI_ORG_NAME),
    ]
    monkeypatch.setattr(
        gh_IMPORT_PATH,
        lambda *args, **kwargs: SimpleNamespace(
            stderr="", stdout=json.dumps(JSON_OUTPUT)
        ),
    )
    repos = fetch_org_repos(TECH_AI_ORG_NAME, GITHUB_HOSTNAME)
    for actual, expected in zip(repos, EXPECTED_REPOS):
        assert actual == expected


def test_skips_private_forks_dotgithub(monkeypatch: MonkeyPatch):
    JSON_OUTPUT = [
        {
            "name": ".github",
            "html_url": "url",
            "private": False,
            "fork": False,
        },
        {
            "name": "private_repo",
            "html_url": "url",
            "private": True,
            "fork": False,
        },
        {
            "name": "forked_repo",
            "html_url": "url",
            "private": False,
            "fork": True,
        },
    ]
    monkeypatch.setattr(
        gh_IMPORT_PATH,
        lambda *args, **kwargs: SimpleNamespace(
            stderr="", stdout=json.dumps(JSON_OUTPUT)
        ),
    )
    repos = fetch_org_repos("org", "host")
    assert len(repos) == 0
