from orgwarden.audit import audit_repository
import pytest
from pytest import CaptureFixture

from orgwarden.repository import Repository
from tests.constants import ORGWARDEN_REPO_NAME, TECH_AI_ORG_NAME


def test_no_repository():
    with pytest.raises(TypeError):
        audit_repository()


def test_invalid_repository(capfd: CaptureFixture):
    exit_code = audit_repository(
        Repository(name="invalid-repo", url="https://example.com", org="invalid-org"),
    )
    assert exit_code != 0
    stdout = capfd.readouterr().out
    assert "not a valid GitHub repository" in stdout


def test_orgwarden_repo(capfd: CaptureFixture):
    repo = Repository(
        name=ORGWARDEN_REPO_NAME,
        url=f"https://github.com/{TECH_AI_ORG_NAME}/{ORGWARDEN_REPO_NAME}",
        org=TECH_AI_ORG_NAME,
    )
    _ = audit_repository(repo)
    # cannot check exit_code, as this is dependent on whether OrgWarden passes audit
    stdout = capfd.readouterr().out
    assert "Results: DONE!" in stdout
    assert repo.url in stdout
    assert "not a valid GitHub repository" not in stdout
