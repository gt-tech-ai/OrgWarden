from dataclasses import dataclass


@dataclass(frozen=True)
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
    """

    name: str
    url: str
    org: str
