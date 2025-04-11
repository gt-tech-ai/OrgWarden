import subprocess
from orgwarden.repo_crawler import Repository


def audit_repository(
    repo: Repository,
    gh_pat: str | None,
) -> int:
    """
    Runs RepoAuditor against the specified repository and returns the resulting exit code.
    """

    command = f"uv run repo_auditor --include GitHub --GitHub-url {repo.url}"
    if gh_pat is not None:
        command += f" --GitHub-pat {gh_pat}"

    if repo.cli_flags:
        command += f" {repo.cli_flags}"

    audit_res = subprocess.run(
        command,
        shell=True,
        text=True,
    )
    return audit_res.returncode
