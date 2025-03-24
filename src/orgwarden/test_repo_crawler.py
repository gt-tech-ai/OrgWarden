import pytest
import requests
from .repo_crawler import Repository, fetch_org_repos

class TestFetchOrgRepos():
    def test_no_org_name(self):
        with pytest.raises(TypeError):
            fetch_org_repos()

    def test_non_existing_org(self):
        with pytest.raises(requests.RequestException):
            fetch_org_repos("")

    def test_gt_sse_center(self):
        SSEC = "gt-sse-center"
        KNOWN_REPOS = [
            "RepoAuditor",
            "PatientX.AI",
            "PythonProjectBootstrapper"
        ]
        repos = fetch_org_repos(SSEC)
        assert no_duplicates(repos)
        assert includes_known_repos(repos, KNOWN_REPOS)
        # ensure repos excludes .github and forks
        assert not includes_known_repos(repos, [".github"])
        assert not includes_known_repos(repos, ["LIReC"])

    def test_gt_tech_ai(self):
        TECH_AI = "gt-tech-ai"
        KNOWN_REPOS = [] # currently no public repos
        repos = fetch_org_repos(TECH_AI)
        assert no_duplicates(repos)
        assert includes_known_repos(repos, KNOWN_REPOS)


def no_duplicates(repos: list[Repository]) -> bool:
    unique = []
    for repo in repos:
        if repo in unique:
            return False
        unique.append(repo)
    return True

def test_no_duplicates():
    assert no_duplicates([
        Repository("test_repo_1", "https://example.com/test1", "test_org_1"),
        Repository("test_repo_2", "https://example.com/test2", "test_org_2")
    ])
    assert not no_duplicates([
        Repository("test_repo_1", "https://example.com/test1", "test_org_1"),
        Repository("test_repo_1", "https://example.com/test1", "test_org_1")
    ])

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
        ["test_repo_1"]
    )
    assert not includes_known_repos(
        [Repository("test_repo_1", "https://example.com/test1", "test_org_1")],
        ["test_repo_2"]
    )

