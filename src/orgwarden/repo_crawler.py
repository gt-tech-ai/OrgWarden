import requests
from orgwarden.repository import Repository


class APIError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


JSON_SCHEMA_ERROR = APIError(
    "The GitHub API response does not match expected JSON schema."
)


class AuthError(Exception):
    def __init__(self, hostname: str, message: str):
        self.hostname = hostname
        self.message = message
        super().__init__(hostname, message)


def fetch_org_repos(org_name: str, hostname: str, gh_pat: str) -> list[Repository]:
    """
    Returns a `Repository` list containing the specified organization's public, non-forked repositories.
    Raises an `AuthError` if OrgWarden lacks authorization with GitHub API.
    Raises an `APIError` if an other error occurs while fetching repositories, or the JSON response does not match expected schema.
    """

    if not org_name:
        raise ValueError("org_name is an empty string.")
    if not hostname:
        raise ValueError("hostname is an empty string.")

    BASE_URL = (
        "https://api.github.com"
        if "github.com" in hostname or "www.github.com" in hostname
        else f"https://{hostname}/api/v3"
    )
    HEADERS = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {gh_pat}",
    }

    org_repo_entries: list[dict] = []  # unfiltered api response

    page_num = 1
    while True:
        res = requests.get(
            f"{BASE_URL}/orgs/{org_name}/repos",
            params={
                "page": page_num,
                "per_page": 100,  # max value
            },
            headers=HEADERS,
        )

        if res.status_code == 401 or res.status_code == 403:
            raise AuthError(hostname, message=res.json())
        if res.status_code != 200:
            raise APIError(f"Error fetching repos for {org_name}: {res.json()}")

        data = res.json()
        if not isinstance(data, list):
            raise JSON_SCHEMA_ERROR
        if not data:  # end of paginated results
            break

        page_num += 1
        org_repo_entries += data

    # Build filtered list of Repositories
    repositories: list[Repository] = []
    for repo_entry in org_repo_entries:
        if not isinstance(repo_entry, dict):
            raise JSON_SCHEMA_ERROR
        try:
            if repo_entry["private"]:
                continue  # do not include private repositories (for now?)
            if repo_entry["name"] == ".github":
                continue  # ignore config repo
            if repo_entry["fork"]:
                continue  # ignore forks
        except KeyError:
            raise JSON_SCHEMA_ERROR

        repositories.append(
            Repository(
                name=repo_entry["name"], url=repo_entry["html_url"], org=org_name
            )
        )

    return repositories
