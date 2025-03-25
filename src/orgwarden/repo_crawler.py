import requests

from orgwarden.repository import Repository


def fetch_org_repos(org_name: str) -> list[Repository]:
    """
    Returns a `Repository` list containing the specified organization's public, non-forked repositories.
    """

    org_repo_entries: list[dict] = []  # unfiltered api response
    page_num = 1
    while True:
        response = requests.get(
            url=f"https://api.github.com/orgs/{org_name}/repos",
            headers={"Accept": "application/vnd.github+json"},
            params={
                "per_page": 100,  # max repos per page
                "page": page_num,
            },
        )
        if not response or response.status_code != 200:
            raise requests.HTTPError(
                f"Error fetching repos for organization: {org_name}", response=response
            )

        json_data: list[dict] = response.json()
        if not json_data:
            break  # No more repos
        org_repo_entries += json_data
        page_num += 1  # Go to the next page

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
