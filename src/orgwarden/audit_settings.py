import re
import typer
from dataclasses import dataclass


@dataclass(frozen=True)
class RepoAuditSettings:
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


def parse_settings_string(value: str) -> RepoAuditSettings:
    match = SETTINGS_REGEX.match(value)
    ERROR = typer.BadParameter(
        f'Your input: "{value}" does not match expected pattern. Example: "repo_name: --flag-1 --flag-2"',
        param_hint="settings string",
    )
    if not match:
        raise ERROR
    key, val = match["key"].strip(), match["val"].strip()
    if not key or not val:
        raise ERROR

    return RepoAuditSettings(key, val)


def get_audit_settings(settings_sequence: list[RepoAuditSettings]) -> dict[str, str]:
    """
    Returns a dictionary of `repo_name`: `cli_flags`.
    """

    audit_settings: dict[str, str] = {}

    for repo_settings in settings_sequence:
        repo_name, cli_flags = repo_settings.repo_name, repo_settings.cli_flags
        if repo_name in audit_settings:
            raise ValueError(
                f"Repository settings sequence contains multiple entries for {repo_name}."
            )
        if cli_flags:  # skip empty string
            audit_settings[repo_name] = cli_flags

    return audit_settings
