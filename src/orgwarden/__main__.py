from typing import Annotated
import typer
from orgwarden.audit import audit_repository
from orgwarden.repository import Repository
from orgwarden.repo_crawler import AuthError, fetch_org_repos
from orgwarden.url_tools import validate_url

app = typer.Typer()


@app.command()
def list_repos(
    url: Annotated[
        str,
        typer.Argument(
            help="The url of a GitHub organization. Ex: 'https://github.com/gt-tech-ai'",
            show_default=False,
        ),
    ],
    token: Annotated[
        str | None,
        typer.Option(
            help="GitHub Personal Access Token (PAT) - required for self-hosted GitHub instances",
            show_default=False,
        ),
    ] = None,
) -> None:
    """
    Lists all public, non-forked repositories for the specified organization.
    """

    try:
        parsed_url = validate_url(url)
    except ValueError:
        print_invalid_url_msg(url)
        raise typer.Exit(1)

    try:
        repos = fetch_org_repos(parsed_url.org_name, parsed_url.hostname, token)
    except AuthError as e:
        print_auth_error(e.hostname)
        raise typer.Exit(1)
    except Exception as e:
        print_general_error(e)
        raise typer.Exit(1)

    print(f"~~~~~ Public repositories found for {url} ~~~~~")
    for repo in repos:
        print(f"{repo.org}/{repo.name} - {repo.url}")


@app.command()
def audit(
    url: Annotated[
        str,
        typer.Argument(
            help="The url for a GitHub repository or organization.", show_default=False
        ),
    ],
    token: Annotated[
        str | None,
        typer.Option(
            help="GitHub Personal Access Token (PAT) - must have access to the specified repository or organization. "
            "RepoAuditor's full functionality will not be available if a PAT is not provided.",
            show_default=False,
        ),
    ] = None,
) -> None:
    """
    If the provided <url> is a repository, runs RepoAuditor against the specified repository.
    If the provided <url> is an organization, runs RepoAuditor against all of the organization's public, non-forked repositories.
    """

    if token is None:
        typer.echo(
            typer.style(
                "Running RepoAuditor with limited functionality. Please provide a GitHub PAT for full functionality.",
                fg=typer.colors.CYAN,
            )
        )

    try:
        parsed_url = validate_url(url)
    except ValueError:
        print_invalid_url_msg(url)
        raise typer.Exit(1)

    if parsed_url.repo_name:  # repository
        repo = Repository(
            name=parsed_url.repo_name,
            url=url,
            org=parsed_url.org_name,
        )
        exit_code, _ = audit_repository(repo, token)
        raise typer.Exit(exit_code)

    else:  # organization
        try:
            repos = fetch_org_repos(parsed_url.org_name, parsed_url.hostname, token)
        except AuthError as e:
            print_auth_error(e.hostname)
            raise typer.Exit(1)
        except Exception as e:
            print_general_error(e)
            raise typer.Exit(1)

        final_exit_code = 0  # keep track of highest exit code i.e. worst error -> ensures the command fails if any repo fails audit
        for repo in repos:
            exit_code, _ = audit_repository(repo, token)
            final_exit_code = max(final_exit_code, exit_code)
        raise typer.Exit(final_exit_code)


# pragma: no cover
def print_invalid_url_msg(url: str):
    typer.echo(
        typer.style(
            f"Error: {url} is invalid.",
            fg=typer.colors.RED,
        ),
        err=True,
    )
    typer.echo(
        typer.style(
            "Example: https://github.com/gt-tech-ai/OrgWarden",
            fg=typer.colors.GREEN,
        ),
        err=True,
    )


# pragma: no cover
def print_general_error(message: str):
    typer.echo(typer.style(message, fg=typer.colors.RED), err=True)


# pragma: no cover
def print_auth_error(hostname: str):
    typer.echo(
        typer.style(
            f"Error: could not authenticate with {hostname}. Please ensure the provided token is valid.",
            fg=typer.colors.RED,
        ),
        err=True,
    )
    typer.echo(
        typer.style(
            "Please",
            fg=typer.colors.CYAN
        )
    )


if __name__ == "__main__":
    app()  # pragma: no cover
