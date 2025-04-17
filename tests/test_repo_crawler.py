from subprocess import CompletedProcess
from types import SimpleNamespace
import pytest
from pytest import MonkeyPatch
from orgwarden.repo_crawler import APIError, AuthError, fetch_org_repos
from orgwarden.repository import Repository
from tests.constants import TECH_AI_ORG_NAME, GITHUB_HOSTNAME, GITHUB_PAT

requests_get_IMPORT_PATH = "requests.get"


def test_missing_org():
    with pytest.raises(ValueError, match="empty string"):
        _ = fetch_org_repos(org_name="", hostname="host", gh_pat="pat")


def test_missing_hostname():
    with pytest.raises(ValueError, match="empty string"):
        _ = fetch_org_repos(org_name="org", hostname="", gh_pat="pat")


def test_requests_get_called_correctly(monkeypatch: MonkeyPatch):
    mock_get_called = False

    def mock_get(url: str, params: dict, headers: dict) -> CompletedProcess[str]:
        nonlocal mock_get_called
        mock_get_called = True
        assert params, headers
        assert TECH_AI_ORG_NAME in url, GITHUB_HOSTNAME in url
        assert GITHUB_PAT in headers["Authorization"]
        return SimpleNamespace(status_code=200, json=lambda: [])

    monkeypatch.setattr(requests_get_IMPORT_PATH, mock_get)
    _ = fetch_org_repos(TECH_AI_ORG_NAME, GITHUB_HOSTNAME, GITHUB_PAT)
    assert mock_get_called


def test_invalid_auth(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(
        requests_get_IMPORT_PATH,
        lambda *args, **kwargs: SimpleNamespace(
            status_code=401, json=lambda: {"message": "Must authenticate"}
        ),
    )
    with pytest.raises(AuthError, match="Must authenticate"):
        _ = fetch_org_repos("org", "host", "pat")


def test_generic_api_error(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(
        requests_get_IMPORT_PATH,
        lambda *args, **kwargs: SimpleNamespace(
            status_code=400, json=lambda: {"message": "Some general API error"}
        ),
    )
    with pytest.raises(APIError, match="Some general API error"):
        _ = fetch_org_repos("org", "host", "pat")


def test_invalid_json_response(monkeypatch: MonkeyPatch):
    INVALID_RESPONSES = [
        {},
        ["string"],
        [{"object": "with no name, fork, or private properties"}],
    ]
    for json_resp in INVALID_RESPONSES:
        monkeypatch.setattr(
            requests_get_IMPORT_PATH,
            lambda *args, **kwargs: SimpleNamespace(
                status_code=200,
                json=lambda: json_resp if kwargs["params"]["page"] == 1 else [],
            ),
        )
        with pytest.raises(
            APIError, match="response does not match expected JSON schema"
        ):
            _ = fetch_org_repos("org", "host", "pat")


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
        requests_get_IMPORT_PATH,
        lambda *args, **kwargs: SimpleNamespace(
            status_code=200,
            json=lambda: JSON_OUTPUT if kwargs["params"]["page"] == 1 else [],
        ),
    )
    repos = fetch_org_repos(TECH_AI_ORG_NAME, "host", "pat")
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
        requests_get_IMPORT_PATH,
        lambda *args, **kwargs: SimpleNamespace(
            status_code=200,
            json=lambda: JSON_OUTPUT if kwargs["params"]["page"] == 1 else [],
        ),
    )
    repos = fetch_org_repos("org", "host", "pat")
    assert len(repos) == 0
