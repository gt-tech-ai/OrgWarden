import json
import subprocess
from orgwarden.repository import Repository


def fetch_org_repos(org_name: str) -> list[Repository]:
    """
    Returns a `Repository` list containing the specified organization's public, non-forked repositories.
    """

    org_repo_entries: list[dict] = []  # unfiltered api response

    res = subprocess.run(
        f"gh api orgs/{org_name}/repos --paginate", shell=True, capture_output=True
    )
    if res.stderr:
        raise ConnectionError(f"Error fetching repos for {org_name}: {res.stderr}")
    try:
        org_repo_entries = json.loads(res.stdout)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Could not decode API response: {e}")

    # Build filtered list of Repositories
    repositories: list[Repository] = []
    for repo_entry in org_repo_entries:
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
