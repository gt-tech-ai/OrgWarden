from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class ParsedURL:
    hostname: str
    org_name: str
    repo_name: str | None


def validate_url(url: str) -> ParsedURL:
    """
    Validates the provided url.
    Returns a `ParsedURL` object if the url is valid.
    Raises a ValueError if the url is invalid.
    """

    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError()

    split_path = parsed_url.path.strip("/").split("/")
    if len(split_path) != 1 and len(split_path) != 2:
        raise ValueError()

    return ParsedURL(
        hostname=parsed_url.netloc,
        org_name=split_path[0],
        repo_name=split_path[1] if len(split_path) == 2 else None,
    )
