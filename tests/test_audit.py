from orgwarden.audit import audit_repository
import pytest

from orgwarden.repository import Repository
from tests.constants import ORGWARDEN_REPO_NAME, ORGWARDEN_URL, TECH_AI_ORG_NAME


def test_no_repository():
    with pytest.raises(TypeError):
        audit_repository()


def test_invalid_repository():
    exit_code, stdout = audit_repository(
        repo=Repository(
            name="invalid-repo", url="https://example.com", org="invalid-org"
        ),
        token=None,
        capture=True,
    )
    assert exit_code != 0
    assert "not a valid GitHub repository" in stdout


ORGWARDEN_REPO = Repository(
    name=ORGWARDEN_REPO_NAME,
    url=f"https://github.com/{TECH_AI_ORG_NAME}/{ORGWARDEN_REPO_NAME}",
    org=TECH_AI_ORG_NAME,
)


def test_orgwarden_repo_no_token():
    _, stdout = audit_repository(repo=ORGWARDEN_REPO, token=None, capture=True)
    # cannot check exit_code, as this is dependent on whether OrgWarden passes audit
    assert "Results: DONE!" in stdout
    assert ORGWARDEN_URL in stdout
    assert "not a valid GitHub repository" not in stdout
    assert "please provide the GitHub PAT" in stdout


@pytest.mark.xfail(reason="Need to setup a PAT for testing.")
def test_orgwarden_repo_with_token():
    PAT = "todo"
    _, stdout = audit_repository(repo=ORGWARDEN_REPO, token=PAT, capture=True)
    assert "Results: DONE!" in stdout
    assert ORGWARDEN_URL in stdout
    assert "not a valid GitHub repository" not in stdout
    assert "please provide the GitHub PAT" not in stdout
