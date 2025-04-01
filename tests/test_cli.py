from pytest import MonkeyPatch
from typer.testing import CliRunner
from orgwarden.__main__ import app
from orgwarden.constants import GITHUB_HOSTNAME
from orgwarden.repository import Repository
from tests.constants import (
    ORGWARDEN_REPO_NAME,
    ORGWARDEN_URL,
    TECH_AI_KNOWN_REPOS,
    TECH_AI_ORG_NAME,
    TECH_AI_URL,
)

runner = CliRunner()


class TestListReposCommand:
    COMMAND = "list-repos"

    def test_invalid_orgs(self):
        INVALID_ORGS = ["", "example.com", "https://github.com"]
        for org in INVALID_ORGS:
            res = runner.invoke(app, [self.COMMAND, org])
            assert res.exit_code != 0

    def test_valid_orgs(self):
        VALID_ORGS = [TECH_AI_ORG_NAME, TECH_AI_URL]
        for org in VALID_ORGS:
            res = runner.invoke(app, [self.COMMAND, org])
            assert res.exit_code == 0
            assert all([repo_name in res.stdout for repo_name in TECH_AI_KNOWN_REPOS])


class TestAuditCommand:
    COMMAND = "audit"

    def test_invalid_urls(self):
        INVALID_URLS = [
            "",  # empty url
            "/gt-tech-ai/OrgWarden",  # missing site
            "github.com/gt-tech-ai/OrgWarden",  # missing protocol
            "https://github.com/gt-tech-ai/OrgWarden/extra-bits",  # path too long
        ]
        for url in INVALID_URLS:
            res = runner.invoke(app, [self.COMMAND, url])
            assert res.exit_code != 0
            assert "not a valid GitHub" in res.stdout

    def test_audit_with_repo_url(self, monkeypatch: MonkeyPatch):
        """
        Ensures that `audit` command correctly parses url argument and passes correct `Repository` object to `audit_repository`.
        """
        mock_audit_repository_called = False

        def mock_audit_repository(
            repo: Repository, capture: bool = False
        ) -> tuple[int, str | None]:
            nonlocal mock_audit_repository_called
            mock_audit_repository_called = True
            assert not capture
            assert repo.url == ORGWARDEN_URL
            assert repo.name == ORGWARDEN_REPO_NAME
            assert repo.org == TECH_AI_ORG_NAME
            return 0, None

        monkeypatch.setattr(
            "orgwarden.__main__.audit_repository", mock_audit_repository
        )

        res = runner.invoke(app, [self.COMMAND, ORGWARDEN_URL])
        assert mock_audit_repository_called
        assert res.exit_code == 0

    def test_audit_with_org_url(self, monkeypatch: MonkeyPatch):
        """
        Ensures that `audit` command correctly parses url argument, runs `fetch_org_repos` on the given org, and runs audit `audit_repository` for each returned repository.
        """
        mock_repos = [
            Repository(name="repo1", url="url1", org=TECH_AI_ORG_NAME),
            Repository(name="repo2", url="url2", org=TECH_AI_ORG_NAME),
            Repository(name="repo3", url="url3", org=TECH_AI_ORG_NAME),
        ]

        mock_fetch_org_repos_called = False

        def mock_fetch_org_repos(org_name: str, hostname: str) -> list[Repository]:
            nonlocal mock_fetch_org_repos_called
            mock_fetch_org_repos_called = True
            assert org_name == TECH_AI_ORG_NAME
            assert hostname == GITHUB_HOSTNAME
            return mock_repos

        monkeypatch.setattr("orgwarden.__main__.fetch_org_repos", mock_fetch_org_repos)

        mock_audit_repository_calls = 0

        def mock_audit_repository(
            repo: Repository, capture: bool = False
        ) -> tuple[int, str | None]:
            nonlocal mock_audit_repository_calls
            mock_audit_repository_calls += 1
            assert not capture
            assert repo.org == TECH_AI_ORG_NAME
            return 0, None

        monkeypatch.setattr(
            "orgwarden.__main__.audit_repository", mock_audit_repository
        )

        res = runner.invoke(app, [self.COMMAND, TECH_AI_URL])
        assert mock_fetch_org_repos_called
        assert mock_audit_repository_calls == len(mock_repos)
        assert res.exit_code == 0
