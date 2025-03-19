from orgwarden import repo_crawler


def main() -> None:
    org_name = "gt-sse-center" # hard-coded for now
    repos = repo_crawler.fetch_org_repos(org_name)

    print(f"~~~~~ Public repositories found for {org_name} ~~~~~")
    for repo in repos:
        print(f"{repo.org}/{repo.name} - {repo.url}")
