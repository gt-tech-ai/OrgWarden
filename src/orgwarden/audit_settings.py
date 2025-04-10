from copy import deepcopy
import re
import typer
from orgwarden.repository import Repository
from dataclasses import dataclass


@dataclass(frozen=True)
class RepositorySettings:
    repo_name: str
    cli_flags: str


SETTINGS_PATTERN = """
^           # beginning of string
(?P<key>    # Capture group 'key'
    [^:]+?) # One or more non-colon characters
:           # colon separates key & val
(?P<val>    # Capture group 'val'
    .+)     # One or more of any character
$           # end of string
"""
SETTINGS_REGEX = re.compile(SETTINGS_PATTERN, re.VERBOSE)


def parse_settings_string(value: str) -> RepositorySettings:
    match = SETTINGS_REGEX.match(value)
    ERROR = typer.BadParameter(
        f'Your input: "{value}" does not match pattern expected pattern. Example: "repo_name: --flag-1 --flag-2"',
        param_hint="settings string",
    )
    if not match:
        raise ERROR
    key, val = match["key"].strip(), match["val"].strip()
    if not key or not val:
        raise ERROR

    return RepositorySettings(key, val)


def append_settings(
    repos: list[Repository], settings: list[RepositorySettings]
) -> list[Repository]:
    """
    Returns a copy of provided `repos` list with `cli_flags` settings appended.
    """
    flags_dict: dict[str, str] = {}

    for repo_settings in settings:
        repo_name, cli_flags = repo_settings.repo_name, repo_settings.cli_flags
        if repo_name in flags_dict:
            raise ValueError(
                f"Repository settings sequence contains multiple entries for {repo_name}."
            )
        flags_dict[repo_name] = cli_flags

    copied_repos = deepcopy(repos)
    for repo in copied_repos:
        if repo.name in flags_dict:
            flags = flags_dict[repo.name]
            if flags:  # skip empty string
                repo.cli_flags = flags

    # check for unused settings & warn user
    for repo in copied_repos:
        if repo.name in flags_dict:
            del flags_dict[repo.name]
    if len(flags_dict) != 0:
        for repo_name in flags_dict.keys():
            typer.echo(
                typer.style(
                    f"Settings for {repo_name} were provided, but this repository is not being audited.",
                    fg=typer.colors.YELLOW,
                ),
                err=True,
            )

    return copied_repos
