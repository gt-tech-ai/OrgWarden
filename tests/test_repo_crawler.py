import pytest
from orgwarden.repo_crawler import fetch_org_repos
from orgwarden.repository import Repository
from tests.constants import TECH_AI_KNOWN_REPOS, TECH_AI_ORG_NAME


class TestFetchOrgRepos:
    def test_no_org_name(self):
        with pytest.raises(TypeError):
            fetch_org_repos()

    def test_non_existing_org(self):
        with pytest.raises(ConnectionError):
            fetch_org_repos("")

    def test_gt_tech_ai(self):
        repos = fetch_org_repos(TECH_AI_ORG_NAME)
        assert no_duplicates(repos)
        assert includes_known_repos(repos, TECH_AI_KNOWN_REPOS)
        # ensure repos excludes .github
        assert not includes_known_repos(repos, [".github"])
        # ensure repos excludes forks - gt-tech-ai currently has no public forks, ignore for now
        # assert not includes_known_repos(repos, [""])


def no_duplicates(repos: list[Repository]) -> bool:
    unique = []
    for repo in repos:
        if repo in unique:
            return False
        unique.append(repo)
    return True


def test_no_duplicates():
    assert no_duplicates(
        [
            Repository("test_repo_1", "https://example.com/test1", "test_org_1"),
            Repository("test_repo_2", "https://example.com/test2", "test_org_2"),
        ]
    )
    assert not no_duplicates(
        [
            Repository("test_repo_1", "https://example.com/test1", "test_org_1"),
            Repository("test_repo_1", "https://example.com/test1", "test_org_1"),
        ]
    )


def includes_known_repos(repos: list[Repository], known_repos_names: list[str]) -> bool:
    actual_names = []
    for repo in repos:
        actual_names.append(repo.name)
    for known_name in known_repos_names:
        if known_name not in actual_names:
            return False
    return True


def test_includes_known_repos():
    assert includes_known_repos(
        [Repository("test_repo_1", "https://example.com/test1", "test_org_1")],
        ["test_repo_1"],
    )
    assert not includes_known_repos(
        [Repository("test_repo_1", "https://example.com/test1", "test_org_1")],
        ["test_repo_2"],
    )
