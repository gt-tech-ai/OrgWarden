from typer.testing import CliRunner
from orgwarden.__main__ import app
from tests.constants import (
    ORGWARDEN_REPO_NAME,
    ORGWARDEN_URL,
    TECH_AI_KNOWN_REPOS,
    TECH_AI_ORG_NAME,
    TECH_AI_URL,
    TESTING_FLAG,
)

runner = CliRunner()


class TestListRepos:
    COMMAND = "list-repos"

    def test_invalid_org(self):
        res = runner.invoke(app, [self.COMMAND, ""])
        assert res.exit_code != 0

    def test_tech_ai(self):
        res = runner.invoke(app, [self.COMMAND, TECH_AI_ORG_NAME])
        assert res.exit_code == 0
        assert includes_known_repos(res.stdout, TECH_AI_KNOWN_REPOS)


class TestAudit:
    COMMAND = "audit"

    def test_missing_url(self):
        res = runner.invoke(app, [self.COMMAND, ""])
        assert res.exit_code != 0
        assert "not a valid GitHub" in res.stdout

    def test_missing_site(self):
        res = runner.invoke(app, [self.COMMAND, "/gt-tech-ai/OrgWarden"])
        assert res.exit_code != 0
        assert "not a valid GitHub" in res.stdout

    def test_path_too_long(self):
        res = runner.invoke(
            app, [self.COMMAND, "https://github.com/gt-tech-ai/OrgWarden/extra-bits"]
        )
        assert res.exit_code != 0
        assert "not a valid GitHub" in res.stdout

    def test_audit_repo_orgwarden(self):
        res = runner.invoke(app, [self.COMMAND, ORGWARDEN_URL, TESTING_FLAG])
        # cannot check exit code, as this will vary depending on whether OrgWarden passes audit
        assert includes_known_repos(res.stdout, [ORGWARDEN_REPO_NAME])
        assert repo_auditor_ran(res.stdout)

    def test_audit_org_tech_ai(self):
        res = runner.invoke(app, [self.COMMAND, TECH_AI_URL, TESTING_FLAG])
        # cannot check exit code, as this will vary depending on whether all gt-tech-ai repos pass audit
        assert includes_known_repos(res.stdout, TECH_AI_KNOWN_REPOS)
        assert repo_auditor_ran(res.stdout)


def includes_known_repos(stdout: str, repo_names: list[str]) -> bool:
    for repo_name in repo_names:
        if repo_name not in stdout:
            return False
    return True


def repo_auditor_ran(stdout: str) -> bool:
    return "Results: DONE!" in stdout
