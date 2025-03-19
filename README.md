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
You can run the tool with `uv`. Currently, this prints all public, non-forked repositories for `gt-sse-center`. In the future, options for specifying a specific organization, as well as running audits on each repository will be implemented.

```bash
uv run orgwarden
```
