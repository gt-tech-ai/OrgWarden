![CI](https://github.com/gt-tech-ai/OrgWarden/actions/workflows/CI.yml/badge.svg)

# 👮‍♀️ OrgWarden (Work In Progress)

*OrgWarden* is a tool for auditing an oganization's repositories.

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
You can run the tool with `uv`. Currently, this prints all public, non-forked repositories for the specified github organization. In the future, the ability to run audits on each repository will be implemented.

```bash
uv run orgwarden <github-org-name>
```

## Development
To manually run tests on this project, run the following command:
```bash
uv run pytest
```