from orgwarden.repository import Repository

TECH_AI_URL = "https://github.com/gt-tech-ai"
TECH_AI_ORG_NAME = "gt-tech-ai"


ORGWARDEN_REPO_NAME = "OrgWarden"
ORGWARDEN_URL = "https://github.com/gt-tech-ai/OrgWarden"
ORGWARDEN_REPO = Repository(
    name=ORGWARDEN_REPO_NAME,
    url=f"https://github.com/{TECH_AI_ORG_NAME}/{ORGWARDEN_REPO_NAME}",
    org=TECH_AI_ORG_NAME,
)

GITHUB_HOSTNAME = "github.com"
TECH_AI_KNOWN_REPOS = [ORGWARDEN_REPO_NAME]
