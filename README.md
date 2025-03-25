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
Lists all public, non-forked repositories for the specified GitHub organization.
```bash
uv run orgwarden ls-repos <github_org_name>
```

### Audit Repository
Runs RepoAuditor on the specified owner's repository.
```bash
uv run orgwarden audit-repo <repository_owner> <repository_name>
```

### Audit Organization
Runs RepoAuditor across all public, non-forked repositories for the specified GitHub organization.
```bash
uv run orgwarden audit-org <github_org_name>
```


## Development
To manually run tests on this project, run the following command:
```bash
uv run pytest
```