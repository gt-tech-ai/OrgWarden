from types import SimpleNamespace
from pytest import CaptureFixture, MonkeyPatch
import pytest
from typer import BadParameter
from typer.testing import CliRunner
from orgwarden.__main__ import app, reject_empty_string
from orgwarden.audit_settings import RepoAuditSettings, get_audit_settings
from orgwarden.repository import Repository
from tests.constants import (
    GITHUB_PAT,
    ORGWARDEN_URL,
    TECH_AI_KNOWN_REPOS,
    TECH_AI_ORG_NAME,
    TECH_AI_URL,
)

validate_url_IMPORT_PATH = "orgwarden.__main__.validate_url"
fetch_org_repos_IMPORT_PATH = "orgwarden.__main__.fetch_org_repos"
get_audit_settings_IMPORT_PATH = "orgwarden.__main__.get_audit_settings"
audit_repository_IMPORT_PATH = "orgwarden.__main__.audit_repository"
requests_get_IMPORT_PATH = "requests.get"

runner = CliRunner()


def test_reject_empty_string():
    with pytest.raises(BadParameter, match="empty string"):
        _ = reject_empty_string("")

    val = reject_empty_string("not empty")
    assert val == "not empty"


class TestSharedFunctionality:
    """
    Tests code pathways followed by both the `list-repos` and `audit` commands.
    """

    COMMANDS = ["list-repos", "audit"]

    def test_handles_invalid_url(self):
        for command in self.COMMANDS:
            res = runner.invoke(app, [command, "bad-url", "pat"])
            assert res.exit_code != 0
            assert "not a valid URL" in res.stdout
            assert "Example: " in res.stdout

    def test_handles_api_auth_error(self, monkeypatch: MonkeyPatch):
        for command in self.COMMANDS:
            monkeypatch.setattr(
                requests_get_IMPORT_PATH,
                lambda *args, **kwargs: SimpleNamespace(
                    status_code=403, json=lambda: {"message": "could not authenticate"}
                ),
            )
            res = runner.invoke(app, [command, TECH_AI_URL, "pat"])
            assert res.exit_code != 0
            assert "could not authenticate" in res.stdout

    def test_handles_general_api_error(self, monkeypatch: MonkeyPatch):
        for command in self.COMMANDS:
            monkeypatch.setattr(
                requests_get_IMPORT_PATH,
                lambda *args, **kwargs: SimpleNamespace(
                    status_code=400, json=lambda: {"message": "some general api error"}
                ),
            )
            res = runner.invoke(app, [command, TECH_AI_URL, "pat"])
            assert res.exit_code != 0
            assert "Error fetching repos" in res.stdout


class TestListReposCommand:
    COMMAND = "list-repos"

    def test_happy_path(self):
        res = runner.invoke(app, [self.COMMAND, TECH_AI_URL, GITHUB_PAT])
        assert res.exit_code == 0
        for repo_name in TECH_AI_KNOWN_REPOS:
            assert repo_name in res.stdout


class TestAuditCommand:
    COMMAND = "audit"

    def test_happy_paths(self, capfd: CaptureFixture):
        """
        Run happy path for auditing a repository and auditing an org.
        """
        for url in [ORGWARDEN_URL, TECH_AI_URL]:
            _ = runner.invoke(app, [self.COMMAND, url, GITHUB_PAT])
            stdout = capfd.readouterr().out
            assert "DONE" in stdout
            assert url in stdout

    def test_handles_unused_settings_entries(
        self, monkeypatch: MonkeyPatch, capfd: CaptureFixture
    ):
        REPOS = [Repository("repo_one", "url", "org")]
        SETTINGS_SEQUENCE = ["repo_one: --flag-1", "extra_repo: --flag-1 --flag-2"]
        monkeypatch.setattr(fetch_org_repos_IMPORT_PATH, lambda *args, **kwargs: REPOS)
        res = runner.invoke(
            app, [self.COMMAND, TECH_AI_URL, GITHUB_PAT, *SETTINGS_SEQUENCE]
        )
        assert "this repository is not being audited" in res.stdout

        _ = capfd.readouterr()  # prevents error output from RepoAuditor
        # due to invalid flags from polluting test output

    def test_handles_duplicate_settings_entries(self):
        SETTINGS_SEQUENCE = ["repo: --flag-1", "repo: --flag-1 --flag-2"]
        res = runner.invoke(
            app, [self.COMMAND, TECH_AI_URL, GITHUB_PAT, *SETTINGS_SEQUENCE]
        )
        assert res.exit_code != 0
        assert "contains multiple entries" in res.stdout

    # not needed for coverage, but worth explicitly testing
    def test_repository_settings_passed_correctly(self, monkeypatch: MonkeyPatch):
        REPOS = [
            Repository(name="repo1", url="url1", org=TECH_AI_ORG_NAME),
            Repository(name="repo2", url="url2", org=TECH_AI_ORG_NAME),
            Repository(name="repo3", url="url3", org=TECH_AI_ORG_NAME),
        ]
        SETTINGS_SEQUENCE = ["repo1: --arg-1 --arg-2", "repo3: --arg-1 --arg-2 --arg-3"]
        EXPECTED_REPO_SETTINGS = [
            RepoAuditSettings("repo1", "--arg-1 --arg-2"),
            RepoAuditSettings("repo3", "--arg-1 --arg-2 --arg-3"),
        ]
        EXPECTED_AUDIT_SETTINGS = {
            "repo1": "--arg-1 --arg-2",
            "repo3": "--arg-1 --arg-2 --arg-3",
        }
        monkeypatch.setattr(fetch_org_repos_IMPORT_PATH, lambda *args, **kwargs: REPOS)
        mock_get_audit_settings_called = False

        def mock_get_audit_settings(settings_sequence: list[RepoAuditSettings]):
            nonlocal mock_get_audit_settings_called
            mock_get_audit_settings_called = True
            assert settings_sequence == EXPECTED_REPO_SETTINGS
            actual_audit_settings = get_audit_settings(settings_sequence)
            assert actual_audit_settings == EXPECTED_AUDIT_SETTINGS
            return actual_audit_settings

        monkeypatch.setattr(get_audit_settings_IMPORT_PATH, mock_get_audit_settings)

        def mock_audit(_repo: Repository, _gh_pat: str, audit_settings: dict[str, str]):
            assert audit_settings == EXPECTED_AUDIT_SETTINGS
            return 0

        monkeypatch.setattr(audit_repository_IMPORT_PATH, mock_audit)
        res = runner.invoke(
            app, [self.COMMAND, TECH_AI_URL, GITHUB_PAT, *SETTINGS_SEQUENCE]
        )
        assert mock_get_audit_settings_called
        assert res.exit_code == 0
