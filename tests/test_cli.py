from typer.testing import CliRunner
from orgwarden.__main__ import app
from tests.constants import ORGWARDEN_REPO_NAME, TECH_AI_KNOWN_REPOS, TECH_AI_ORG_NAME, TESTING_FLAG

runner = CliRunner()


class TestLsRepos:
    COMMAND = "ls-repos"

    def test_invalid_org(self):
        res = runner.invoke(app, [self.COMMAND, ""])
        assert res.exit_code != 0

    def test_tech_ai(self):
        res = runner.invoke(app, [self.COMMAND, TECH_AI_ORG_NAME])
        assert res.exit_code == 0
        assert includes_known_repos(res.stdout, TECH_AI_KNOWN_REPOS)


class TestAuditRepo:
    COMMAND = "audit-repo"

    def test_invalid_repo(self):
        res = runner.invoke(app, [self.COMMAND, "", ""])
        assert res.exit_code != 0

    def test_orgwarden(self):
        res = runner.invoke(
            app, [self.COMMAND, TECH_AI_ORG_NAME, ORGWARDEN_REPO_NAME, TESTING_FLAG]
        )
        # cannot check exit code, as this will vary depending on whether OrgWarden passes audit
        assert includes_known_repos(res.stdout, [ORGWARDEN_REPO_NAME])
        assert repo_auditor_ran(res.stdout)


class TestAuditOrg:
    COMMAND = "audit-org"

    def test_invalid_org(self):
        res = runner.invoke(app, [self.COMMAND, ""])
        assert res.exit_code != 0

    def test_tech_ai(self):
        res = runner.invoke(app, [self.COMMAND, TECH_AI_ORG_NAME, TESTING_FLAG])
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
