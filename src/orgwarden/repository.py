from dataclasses import dataclass


@dataclass
class Repository:
    """
    Represents a GitHub repository.

    Attributes
    __________
    name : str
        Repository name
    url : str
        Repository URL
    org : str
        GitHub organization to which the repo belongs
    cli_flags : str, optional
        Single string containing any CLI flags the user wishes to pass to RepoAuditor for this specific repository
    """

    name: str
    url: str
    org: str
    cli_flags: str | None = None
