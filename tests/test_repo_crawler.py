import pytest
from pytest import MonkeyPatch
from orgwarden.repo_crawler import APIError, fetch_org_repos
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
        fetch_org_repos(org_name="", hostname=GITHUB_HOSTNAME, token=None)


def test_missing_hostname():
    with pytest.raises(APIError):
        fetch_org_repos(org_name=TECH_AI_ORG_NAME, hostname="", token=None)


def test_invalid_json_response(monkeypatch: MonkeyPatch):
    mock_json_loads_called = False

    def mock_json_loads(_: str):
        nonlocal mock_json_loads_called
        mock_json_loads_called = True
        return {}

    monkeypatch.setattr("json.loads", mock_json_loads)
    with pytest.raises(APIError) as e:
        fetch_org_repos(TECH_AI_ORG_NAME, GITHUB_HOSTNAME, token=None)
        assert "JSON response does not match" in e.message
        assert mock_json_loads_called


def test_github_hosted_orgs():
    repos = fetch_org_repos(TECH_AI_ORG_NAME, GITHUB_HOSTNAME, token=None)
    validate_response(TECH_AI_KNOWN_REPOS, repos)


@pytest.mark.xfail(reason="Need to setup testing Auth token for self-hosted server")
def test_self_hosted_org():
    TOKEN = "todo"
    repos = fetch_org_repos(TECH_AI_ORG_NAME, SELF_HOSTED_HOSTNAME, TOKEN)
    validate_response([], repos)


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
