import json
import subprocess
from orgwarden.repository import Repository


class APIError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class AuthError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def fetch_org_repos(
    org_name: str, hostname: str, token: str | None
) -> list[Repository]:
    """
    Returns a `Repository` list containing the specified organization's public, non-forked repositories.
    Raises an `APIError` if an error occurs while fetching repositories.
    """

    # authenticate with self-hosted server if token is provided
    if token is not None:
        auth_res = subprocess.run(
            f'echo "{token}" | gh auth login --hostname {hostname} --with-token',
            shell=True,
            capture_output=True,
        )
        if auth_res.stderr:
            raise AuthError(f"Error authenticating with {hostname} : {auth_res.stderr}")

    org_repo_entries: list[dict] = []  # unfiltered api response

    api_res = subprocess.run(
        f"gh api orgs/{org_name}/repos --hostname {hostname} --paginate",
        shell=True,
        capture_output=True,
    )
    if api_res.stderr:
        raise APIError(f"Error fetching repos for {org_name}: {api_res.stderr}")

    org_repo_entries = json.loads(api_res.stdout)
    if not isinstance(org_repo_entries, list):
        raise APIError("API JSON response does not match expected schema")

    # Build filtered list of Repositories
    repositories: list[Repository] = []
    for repo_entry in org_repo_entries:
        if repo_entry["private"]:
            continue  # do not include private repositories (for now?)
        if repo_entry["name"] == ".github":
            continue  # ignore config repo
        if repo_entry["fork"]:
            continue  # ignore forks

        repositories.append(
            Repository(
                name=repo_entry["name"], url=repo_entry["html_url"], org=org_name
            )
        )

    return repositories
