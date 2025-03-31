from urllib.parse import urlparse


def validate_url(url: str) -> tuple[str, str | None]:
    """
    Validates the provided url. Returns a tuple containing the `repo_owner` and `repo_name` if included.
    Raises a ValueError if the url is invalid.
    """
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError()

    split_path = parsed_url.path.strip("/").split("/")
    if len(split_path) == 1:
        return split_path[0], None
    elif len(split_path) == 2:
        return split_path[0], split_path[1]
    else:
        raise ValueError()
