import sys
from typing import Annotated
import typer
from orgwarden.audit import audit_repository
from orgwarden.constants import GITHUB_HOSTNAME
from orgwarden.repository import Repository
from orgwarden.repo_crawler import fetch_org_repos
from orgwarden.url_tools import validate_url

app = typer.Typer()


@app.command()
def list_repos(
    organization: Annotated[
        str,
        typer.Argument(
            help="The name or url of a GitHub organization. Ex: 'gt-tech-ai' OR 'https://github.com/gt-tech-ai'"
        ),
    ],
) -> None:
    """
    Lists all public, non-forked repositories for the specified organization.
    """

    org_name, hostname = organization, GITHUB_HOSTNAME
    try:
        parsed_url = validate_url(organization)
        org_name = parsed_url.org_name
        hostname = parsed_url.hostname
    except ValueError:
        pass

    try:
        repos = fetch_org_repos(org_name, hostname)
    except Exception as e:
        print(e)
        sys.exit(1)

    print(f"~~~~~ Public repositories found for {organization} ~~~~~")
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

    try:
        parsed_url = validate_url(url)
    except ValueError:
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

    if parsed_url.repo_name:  # repository
        repo = Repository(
            name=parsed_url.repo_name,
            url=url,
            org=parsed_url.org_name,
        )
        exit_code, _ = audit_repository(repo)
        sys.exit(exit_code)

    else:  # organization
        try:
            repos = fetch_org_repos(parsed_url.org_name, parsed_url.hostname)
        except Exception as e:
            print(e)
            sys.exit(1)

        final_exit_code = 0  # keep track of highest exit code i.e. worst error -> ensures the command fails if any repo fails audit
        for repo in repos:
            exit_code, _ = audit_repository(repo)
            final_exit_code = max(final_exit_code, exit_code)
        sys.exit(final_exit_code)


if __name__ == "__main__":
    app()  # pragma: no cover
