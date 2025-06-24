import subprocess
from orgwarden.repo_crawler import Repository

KNOWN_MODULES = ["GitHub", "GitHubRulesets", "GitHubCommunityStandards"]


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

    command = "uv run repo_auditor"
    for module in modules:
        command += (
            f" --include {module} --{module}-url {repo.url} --{module}-pat {gh_pat}"
        )

    if audit_settings and repo.name in audit_settings:
        command += f" {audit_settings[repo.name]}"

    audit_res = subprocess.run(
        command,
        shell=True,
        text=True,
    )
    return audit_res.returncode
