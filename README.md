![CI](https://github.com/gt-tech-ai/OrgWarden/actions/workflows/CI.yml/badge.svg)

# 👮‍♀️ OrgWarden (Work In Progress)

*OrgWarden* helps ensure your GitHub organization's repositories follow best practices. Under the hood, OrgWarden uses [RepoAuditor](https://github.com/gt-sse-center/RepoAuditor).

## Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/gt-tech-ai/OrgWarden.git

cd OrgWarden
```

#### 2. Sync Project with `uv`
```bash
uv sync
```

## Usage
You can run the tool with `uv`. The available commands are as follows:

### List Repositories
Lists all public, non-forked repositories for the specified GitHub organization. If the provided argument is the name of an organization, OrgWarden will search for said organization on github.com. If the provided argument is a url, OrgWarden will search said organizaiton at that url.
```bash
uv run orgwarden list-repos <github_org_name_or_url>
```

### Audit
Runs [RepoAuditor](https://github.com/gt-sse-center/RepoAuditor) tooling. If the provided url points to a GitHub repository, RepoAuditor will run against said repository. If the provided url points to a GitHub organization, RepoAuditor will run against all public, non-forked repositories within said organization. 
```bash
uv run orgwarden audit <repo_or_org_url>
```


## Development
To manually run tests on this project, run the following command:
```bash
uv run pytest
```