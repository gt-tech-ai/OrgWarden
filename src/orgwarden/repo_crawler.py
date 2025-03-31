import json
import subprocess
from orgwarden.repository import Repository


class APIError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def fetch_org_repos(org_name: str, hostname: str) -> list[Repository]:
    """
    Returns a `Repository` list containing the specified organization's public, non-forked repositories.
    Raises an `APIError` if an error occurs while fetching repositories.
    """

    org_repo_entries: list[dict] = []  # unfiltered api response

    res = subprocess.run(
        f"gh api orgs/{org_name}/repos --hostname {hostname} --paginate",
        shell=True,
        capture_output=True,
    )
    if res.stderr:
        raise APIError(f"Error fetching repos for {org_name}: {res.stderr}")

    org_repo_entries = json.loads(res.stdout)
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
