from typer.testing import CliRunner
from orgwarden.__main__ import app
from .test_repo_crawler import TECH_AI_ORG_NAME, TECH_AI_KNOWN_REPOS

runner = CliRunner()

class TestApp():
    def test_invalid_org(self):
        res = runner.invoke(app, [""])
        assert res.exit_code != 0
    
    def test_tech_ai(self):
        res = runner.invoke(app, [TECH_AI_ORG_NAME])
        assert res.exit_code == 0
        assert includes_known_repos(res.stdout, TECH_AI_KNOWN_REPOS)


def includes_known_repos(stdout: str, repo_names: list[str]) -> bool:
    for repo_name in repo_names:
        if repo_name not in stdout:
            return False
    return True