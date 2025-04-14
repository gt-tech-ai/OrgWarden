import subprocess
from orgwarden.repo_crawler import Repository


def audit_repository(
    repo: Repository,
    audit_settings: dict[str, str] | None,
    gh_pat: str | None,
) -> int:
    """
    Runs RepoAuditor against the specified repository and returns the resulting exit code.
    """

    command = f"uv run repo_auditor --include GitHub --GitHub-url {repo.url}"
    if gh_pat is not None:
        command += f" --GitHub-pat {gh_pat}"

    if audit_settings and repo.name in audit_settings:
        command += f" {audit_settings[repo.name]}"

    audit_res = subprocess.run(
        command,
        shell=True,
        text=True,
    )
    return audit_res.returncode
