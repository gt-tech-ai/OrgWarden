import pytest
from orgwarden.url_tools import validate_url


def test_no_url():
    with pytest.raises(TypeError):
        validate_url()


def test_invalid_urls():
    for url in [
        "",  # empty url
        "github.com/gt-tech-ai/OrgWarden",  # missing protocol
        "https://gt-tech-ai/OrgWarden"  # missing site
        "/gt-tech-ai/OrgWarden",  # missing site and protocol
        "https://github.com/gt-tech-ai/OrgWarden/extra-bits",  # path too long
    ]:
        with pytest.raises(ValueError):
            validate_url(url)


def test_org_urls():
    for url, org in [
        ("https://github.com/gt-tech-ai", "gt-tech-ai"),
        ("https://github.gatech.edu/gt-tech-ai", "gt-tech-ai"),
    ]:
        repo_owner, repo_name = validate_url(url)
        assert repo_name is None
        assert repo_owner == org


def test_repo_urls():
    for url, org, repo in [
        ("https://github.com/gt-tech-ai/OrgWarden", "gt-tech-ai", "OrgWarden"),
        ("https://github.gatech.edu/gt-tech-ai/OrgWarden", "gt-tech-ai", "OrgWarden"),
    ]:
        repo_owner, repo_name = validate_url(url)
        assert repo_owner == org
        assert repo_name == repo
