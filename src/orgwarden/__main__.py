import sys
import typer

from orgwarden.audit import audit_repository
from orgwarden.repository import Repository
from .repo_crawler import fetch_org_repos

app = typer.Typer()


@app.command()
def ls_repos(org_name: str) -> None:
    """
    Lists all public, non-forked repositories for the specified <org_name>
    """
    repos = fetch_org_repos(org_name)

    print(f"~~~~~ Public repositories found for {org_name} ~~~~~")
    for repo in repos:
        print(f"{repo.org}/{repo.name} - {repo.url}")

@app.command()
def audit_repo(repo_owner: str, repo_name: str) -> None:
    """
    Runs the RepoAuditor tool against the specified <repo_owner>'s <repo_name>
    """
    repo = Repository(
        name=repo_name,
        url=f"https://github.com/{repo_owner}/{repo_name}",
        org=repo_owner
    )
    exit_code = audit_repository(repo)
    sys.exit(exit_code)

if __name__ == "__main__":
    app()  # pragma: no cover
