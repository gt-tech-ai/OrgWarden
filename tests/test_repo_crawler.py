import json
from subprocess import CompletedProcess
import pytest
from pytest import MonkeyPatch
from orgwarden.repo_crawler import APIError, AuthError, fetch_org_repos
from orgwarden.repository import Repository
from tests.constants import (
    SELF_HOSTED_HOSTNAME,
    TECH_AI_KNOWN_REPOS,
    TECH_AI_ORG_NAME,
    GITHUB_HOSTNAME,
)


def test_no_org_name():
    with pytest.raises(TypeError):
        fetch_org_repos()


def test_missing_org():
    with pytest.raises(APIError):
        fetch_org_repos(org_name="", hostname=GITHUB_HOSTNAME)


def test_missing_hostname():
    with pytest.raises(APIError):
        fetch_org_repos(org_name=TECH_AI_ORG_NAME, hostname="")


def test_gh_not_installed(monkeypatch: MonkeyPatch):
    mock_which_called = False

    def mock_which(cmd: str) -> str | None:
        nonlocal mock_which_called
        mock_which_called = True
        assert cmd == "gh"
        return None

    monkeypatch.setattr("shutil.which", mock_which)
    with pytest.raises(FileNotFoundError):
        fetch_org_repos(TECH_AI_ORG_NAME, GITHUB_HOSTNAME)
    assert mock_which_called


def test_self_hosted_invalid_auth():
    with pytest.raises(AuthError):
        fetch_org_repos(org_name=TECH_AI_ORG_NAME, hostname=SELF_HOSTED_HOSTNAME)


def test_invalid_json_response(monkeypatch: MonkeyPatch):
    mock_json_loads_called = False

    def mock_json_loads(_: str):
        nonlocal mock_json_loads_called
        mock_json_loads_called = True
        return {}

    monkeypatch.setattr("json.loads", mock_json_loads)
    with pytest.raises(APIError) as e:
        fetch_org_repos(TECH_AI_ORG_NAME, GITHUB_HOSTNAME)
        assert "JSON response does not match" in e.message
        assert mock_json_loads_called


def test_github_hosted_orgs():
    repos = fetch_org_repos(TECH_AI_ORG_NAME, GITHUB_HOSTNAME)
    validate_response(TECH_AI_KNOWN_REPOS, repos)


def test_self_hosted_org(monkeypatch: MonkeyPatch):
    REPO_NAME = "test-repo"
    REPO_URL = "https://test-url.com"
    REPO_ORG = "test-org"
    mock_gh_called = False

    def mock_gh(cmd: str, shell: bool, capture_output: bool) -> CompletedProcess[str]:
        nonlocal mock_gh_called
        mock_gh_called = True
        assert shell, capture_output
        assert SELF_HOSTED_HOSTNAME in cmd
        json_res = json.dumps(
            [
                {
                    "name": REPO_NAME,
                    "html_url": REPO_URL,
                    "org": REPO_ORG,
                    "private": False,
                    "fork": False,
                }
            ]
        )
        return CompletedProcess(args=None, returncode=0, stdout=json_res)

    monkeypatch.setattr("subprocess.run", mock_gh)

    repos = fetch_org_repos(REPO_ORG, SELF_HOSTED_HOSTNAME)
    assert len(repos) == 1
    repo = repos[0]
    assert repo.name == REPO_NAME
    assert repo.url == REPO_URL
    assert repo.org == REPO_ORG


def validate_response(known: list[str], actual: list[Repository]):
    # check for duplicates
    unique = []
    for repo in actual:
        assert repo not in unique
        unique.append(repo)

    # ensure response includes known repositories
    actual_names = []
    for repo in actual:
        actual_names.append(repo.name)
    for repo in known:
        assert repo in actual_names

    # ensure response excludes .github
    assert ".github" not in actual_names

    # ensure response excludes forks
    # cannot check currently as gt-tech-ai currently has no public forks
