import subprocess
from orgwarden.repo_crawler import Repository


def audit_repository(repo: Repository) -> int:
    """
    Runs RepoAuditor against the specified repository and returns a tuple containing the exit code and the stdout if `capture` is set to True.
    """
    audit_res = subprocess.run(
        f"uv run repo_auditor --include GitHub --GitHub-url {repo.url}",
        shell=True,
        text=True,
    )
    return audit_res.returncode
