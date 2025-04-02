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
Lists all public, non-forked repositories for the specified GitHub organization. The `enterprise-token` option is required when making requests to a self-hosted GitHub instance.
```bash
uv run orgwarden list-repos <org_url> --enterprise-token [gh_enterprise_token]
```

### Audit
Runs [RepoAuditor](https://github.com/gt-sse-center/RepoAuditor) tooling. If the provided url points to a GitHub repository, RepoAuditor will run against said repository. If the provided url points to a GitHub organization, RepoAuditor will run against all public, non-forked repositories within said organization. The `pat-token` option is a GitHub Personal Access Token (PAT) that is used by RepoAuditor for increased functionality. The `enterprise-token` option is required if auditing a self-hosted GitHub instance.
```bash
uv run orgwarden audit <repo_or_org_url> --pat-token [gh_pat] --enterprise-token [gh_enterprise_token]
```


## Development
To manually run tests on this project, run the following command:
```bash
uv run pytest
```