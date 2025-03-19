from .repo_crawler import fetch_org_repos


def main() -> None:
    org_name = "gt-sse-center" # hard-coded for now
    repos = fetch_org_repos(org_name)

    print(f"~~~~~ Public repositories found for {org_name} ~~~~~")
    for repo in repos:
        print(f"{repo.org}/{repo.name} - {repo.url}")

if __name__ == "__main__":
    main()