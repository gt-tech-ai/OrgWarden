import typer


def print_centered_message(message_with_spaces: str):
    REPO_AUDITOR_OUTPUT_LENGTH = 180
    BAR_CHAR = "─"
    message_with_spaces = f" {message_with_spaces} "
    side_bar_length = (REPO_AUDITOR_OUTPUT_LENGTH - len(message_with_spaces)) // 2
    typer.echo(
        typer.style(
            f"{BAR_CHAR * side_bar_length}{message_with_spaces}{BAR_CHAR * side_bar_length}",
            fg=typer.colors.CYAN,
        )
    )


def print_general_error(err: Exception):
    typer.echo(typer.style(err, fg=typer.colors.RED), err=True)


def print_invalid_url_msg(err: Exception):
    typer.echo(
        typer.style(
            err,
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
