from dataclasses import dataclass
import sys
import requests


@dataclass
class Repository:
    name: str
    url: str
    org: str

def fetch_org_repos(org_name: str) -> list[Repository]:
    """
    Returns a `Repository` list containing the specified organization's public, non-forked repositories.
    """

    repositories: list[Repository] = []
    page_num = 1
    while True:
        response = requests.get(
            url=f"https://api.github.com/orgs/{org_name}/repos",
            headers={
                "Accept": "application/vnd.github+json"
            },
            params={
                "per_page": 100, # max repos per page
                "page": page_num
            }
        )
        if not response.ok:
            sys.exit(f"Error fetching repos for organization: {org_name} -> {response.json()}")
        
        json_data: list[dict] = response.json()
        page_num += 1  # Go to the next page
        if not json_data:
            break  # No more repos

        for repo in json_data:
            if repo["name"] == ".github":
                continue # ignore config repo
            if repo["fork"]:
                continue # ignore forks

            repositories.append(Repository(
                name=repo["name"],
                url=repo["html_url"],
                org=org_name
            ))

    return repositories
