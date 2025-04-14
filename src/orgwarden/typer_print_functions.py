import typer


def print_general_error(message: str):
    typer.echo(typer.style(message, fg=typer.colors.RED), err=True)


def print_invalid_url_msg(message: str):
    typer.echo(
        typer.style(
            message,
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


def print_gh_not_installed():
    typer.echo(
        typer.style("The GitHub CLI is not installed.", fg=typer.colors.RED), err=True
    )
    typer.echo(
        typer.style(
            "Please follow the installation instructions here: https://github.com/cli/cli#installation",
            fg=typer.colors.CYAN,
        )
    )


def print_auth_error(hostname: str):
    typer.echo(
        typer.style(
            f"Error: could not authenticate with {hostname}. Please ensure the provided token is valid.",
            fg=typer.colors.RED,
        ),
        err=True,
    )


def print_unused_settings_warning(repo_name: str):
    typer.echo(
        typer.style(
            f"Settings for {repo_name} were provided, but this repository is not being audited.",
            fg=typer.colors.YELLOW,
        ),
        err=True,
    )
