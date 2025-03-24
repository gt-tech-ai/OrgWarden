import typer
from .repo_crawler import fetch_org_repos

app = typer.Typer()

@app.command()
def main(org_name: str) -> None:
    repos = fetch_org_repos(org_name)

    print(f"~~~~~ Public repositories found for {org_name} ~~~~~")
    for repo in repos:
        print(f"{repo.org}/{repo.name} - {repo.url}")

if __name__ == "__main__":
    app() # pragma: no cover
    