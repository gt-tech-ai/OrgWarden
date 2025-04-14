from typing import Annotated
import typer
from orgwarden import typer_print_functions as tpf
from orgwarden.audit import audit_repository
from orgwarden.audit_settings import (
    RepoAuditSettings,
    get_audit_settings,
    parse_settings_string,
)
from orgwarden.repository import Repository
from orgwarden.repo_crawler import AuthError, fetch_org_repos
from orgwarden.url_tools import validate_url

app = typer.Typer(rich_markup_mode="markdown")


@app.command()
def list_repos(
    url: Annotated[
        str,
        typer.Argument(
            help="The url of a GitHub organization. Ex: 'https://github.com/gt-tech-ai'",
            show_default=False,
        ),
    ],
) -> None:
    """
    Lists all public, non-forked repositories for the specified organization.
    """

    try:
        parsed_url = validate_url(url)
    except ValueError as e:
        tpf.print_invalid_url_msg(e)
        raise typer.Exit(1)

    try:
        repos = fetch_org_repos(parsed_url.org_name, parsed_url.hostname)
    except FileNotFoundError:
        tpf.print_gh_not_installed()
        raise typer.Exit(1)
    except AuthError as e:
        tpf.print_auth_error(e.hostname)
        raise typer.Exit(1)
    except Exception as e:
        tpf.print_general_error(e)
        raise typer.Exit(1)

    print(f"~~~~~ Public repositories found for {url} ~~~~~")
    for repo in repos:
        print(f"{repo.org}/{repo.name} - {repo.url}")


@app.command()
def audit(
    url: Annotated[
        str,
        typer.Argument(
            help="The url for a GitHub repository or organization. "
            "If the provided <url> points to a repository, RepoAuditor runs against that repository. "
            "If the provided <url> points to an organization, RepoAuditor runs against all of that organization's public, non-forked repositories.",
            show_default=False,
        ),
    ],
    settings_sequence: Annotated[
        list[RepoAuditSettings] | None,
        typer.Argument(
            parser=parse_settings_string,
            help="Control which CLI flags are passed to RepoAuditor for specific repositories. "
            'Each settings string should follow the format: "repo_name: cli_flags". '
            'You can provide a string for each repository: "repo_one: --flag-1" "repo_two: --flag-1 --flag-2". '
            "See [OrgWarden docs](https://github.com/gt-tech-ai/OrgWarden#repository-specific-settings) for further details. "
            "See [RepoAuditor docs](https://github.com/gt-sse-center/RepoAuditor) for available CLI arguments.",
            show_default=False,
        ),
    ] = None,
    gh_pat: Annotated[
        str | None,
        typer.Option(
            help="GitHub Personal Access Token (PAT) - must have access to the specified repository or organization. "
            "RepoAuditor's full functionality will not be available if a PAT is not provided. "
            "See [OrgWarden docs](https://github.com/gt-tech-ai/OrgWarden#setting-up-a-personal-access-token) for help setting up a PAT.",
            show_default=False,
        ),
    ] = None,
) -> None:
    """
    Runs RepoAuditor against the specified organization or repository.
    """

    if not gh_pat:
        typer.echo(
            typer.style(
                "Running RepoAuditor with limited functionality. Please provide a GitHub PAT for full functionality.",
                fg=typer.colors.CYAN,
            )
        )

    try:
        parsed_url = validate_url(url)
    except ValueError as e:
        tpf.print_invalid_url_msg(e)
        raise typer.Exit(1)

    repos: list[Repository] = []

    if parsed_url.repo_name:  # repository
        repos = [
            Repository(
                name=parsed_url.repo_name,
                url=url,
                org=parsed_url.org_name,
            )
        ]

    else:  # organization
        try:
            repos = fetch_org_repos(parsed_url.org_name, parsed_url.hostname)
        except FileNotFoundError:
            tpf.print_gh_not_installed()
            raise typer.Exit(1)
        except AuthError as e:
            tpf.print_auth_error(e.hostname)
            raise typer.Exit(1)
        except Exception as e:
            tpf.print_general_error(e)
            raise typer.Exit(1)

    # Add Repository-Specific Settings
    audit_settings = None
    if settings_sequence:
        try:
            audit_settings = get_audit_settings(settings_sequence)
            # check for unused settings & warn user
            all_repo_names = {repo.name for repo in repos}
            for repo_name in audit_settings.keys():
                if repo_name not in all_repo_names:
                    tpf.print_unused_settings_warning(repo_name)
        except Exception as e:
            tpf.print_general_error(e)
            raise typer.Exit(1)

    # Audit repositories
    final_exit_code = 0  # keep track of highest exit code i.e. worst error -> ensures the command fails if any repo fails audit
    for repo in repos:
        typer.echo(typer.style(f"Now Auditing: {repo.url}", fg=typer.colors.CYAN))

        exit_code = audit_repository(repo, audit_settings, gh_pat)
        final_exit_code = max(final_exit_code, exit_code)
    raise typer.Exit(final_exit_code)


if __name__ == "__main__":
    app()  # pragma: no cover
