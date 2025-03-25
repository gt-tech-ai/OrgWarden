import subprocess
from orgwarden.repo_crawler import Repository


def audit_repository(repo: Repository, capture: bool = False) -> tuple[int, str | None]:
    """
    Runs RepoAuditor against the specified repository and returns a tuple containing the exit code and the stdout if `capture` is set to True.
    """
    audit_res = subprocess.run(
        f"uv run repo_auditor --include GitHub --GitHub-url {repo.url}",
        shell=True,
        capture_output=capture,
        text=True,
    )
    return audit_res.returncode, audit_res.stdout if capture else None
