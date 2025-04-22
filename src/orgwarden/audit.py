import subprocess
from orgwarden.repo_crawler import Repository

KNOWN_MODULES = ["GitHub"]


def audit_repository(
    repo: Repository,
    gh_pat: str,
    audit_settings: dict[str, str] | None,
    modules: list[str] | None,
) -> int:
    """
    Runs RepoAuditor against the specified repository and returns the resulting exit code.
    """
    if not modules:
        modules = KNOWN_MODULES

    command = f"uv run repo_auditor {' '.join(f'--include {module}' for module in modules)} --GitHub-url {repo.url} --GitHub-pat {gh_pat}"

    if audit_settings and repo.name in audit_settings:
        command += f" {audit_settings[repo.name]}"

    audit_res = subprocess.run(
        command,
        shell=True,
        text=True,
    )
    return audit_res.returncode
