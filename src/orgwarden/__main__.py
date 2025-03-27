import sys
from typing import Annotated
from urllib.parse import urlparse
import typer
from orgwarden.audit import audit_repository
from orgwarden.repository import Repository
from orgwarden.repo_crawler import fetch_org_repos

app = typer.Typer()


@app.command()
def list_repos(org_name: str) -> None:
    """
    Lists all public, non-forked repositories for the specified organization.
    """
    repos = fetch_org_repos(org_name)

    print(f"~~~~~ Public repositories found for {org_name} ~~~~~")
    for repo in repos:
        print(f"{repo.org}/{repo.name} - {repo.url}")


@app.command()
def audit(
    url: Annotated[
        str, typer.Argument(help="The url for a GitHub repository or organization.")
    ],
) -> None:
    """
    If the provided <url> is a repository, runs RepoAuditor against the specified repository.
    If the provided <url> is an organization, runs RepoAuditor against all of the organization's public, non-forked repositories.
    """

    def exit_for_invalid_url():
        typer.echo(
            typer.style(
                f"Error: {url} is not a valid GitHub repository or organization.",
                fg=typer.colors.RED,
            )
        )
        typer.echo(
            typer.style(
                "Example: https://github.com/gt-tech-ai/OrgWarden",
                fg=typer.colors.GREEN,
            )
        )
        sys.exit(1)

    # Parse url
    parsed_url = urlparse(url)
    if parsed_url.netloc != "github.com":
        exit_for_invalid_url()
    split_path = parsed_url.path.strip("/").split("/")

    if len(split_path) == 2:  # repository
        repo_owner, repo_name = split_path[0], split_path[1]
        repo = Repository(
            name=repo_name,
            url=f"https://github.com/{repo_owner}/{repo_name}",
            org=repo_owner,
        )
        exit_code, _ = audit_repository(repo)
        sys.exit(exit_code)

    elif len(split_path) == 1:  # organization
        org_name = split_path[0]
        repos = fetch_org_repos(org_name)
        final_exit_code = 0  # keep track of highest exit code i.e. worst error -> ensures the command fails if any repo fails audit
        for repo in repos:
            exit_code, _ = audit_repository(repo)
            final_exit_code = max(final_exit_code, exit_code)
        sys.exit(final_exit_code)

    else:  # invalid url
        exit_for_invalid_url()


if __name__ == "__main__":
    app()  # pragma: no cover
