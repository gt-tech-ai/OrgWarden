import subprocess
from orgwarden.repo_crawler import Repository


def audit_repository(
    repo: Repository, pat_token: str | None, capture: bool = False
) -> tuple[int, str | None]:
    """
    Runs RepoAuditor against the specified repository and returns a tuple containing the exit code and the stdout if `capture` is set to True.
    """
    BASE_COMMAND = f"uv run repo_auditor --include GitHub --GitHub-url {repo.url}"
    command = BASE_COMMAND
    if pat_token is not None:
        command = f"{BASE_COMMAND} --GitHub-pat {pat_token}"

    audit_res = subprocess.run(
        command,
        shell=True,
        capture_output=capture,
        text=True,
    )
    return audit_res.returncode, audit_res.stdout if capture else None
