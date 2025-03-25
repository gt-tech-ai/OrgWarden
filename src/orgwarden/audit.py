import subprocess


from .repo_crawler import Repository

def audit_repository(repo: Repository) -> int:
    """
    Runs RepoAuditor against the specified repository and returns the results exit code.
    """
    audit_res = subprocess.run(
        f"uv run repo_auditor --include GitHub --GitHub-url {repo.url}",
        shell=True,
        capture_output=False,
        text=True
    )
    return audit_res.returncode
