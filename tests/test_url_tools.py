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
    for url, hostname, org in [
        ("https://github.com/gt-tech-ai", "github.com", "gt-tech-ai"),
        ("https://github.gatech.edu/gt-tech-ai", "github.gatech.edu", "gt-tech-ai"),
    ]:
        parsed_url = validate_url(url)
        assert parsed_url.hostname == hostname
        assert parsed_url.org_name == org
        assert parsed_url.repo_name is None


def test_repo_urls():
    for url, hostname, org, repo in [
        (
            "https://github.com/gt-tech-ai/OrgWarden",
            "github.com",
            "gt-tech-ai",
            "OrgWarden",
        ),
        (
            "https://github.gatech.edu/gt-tech-ai/OrgWarden",
            "github.gatech.edu",
            "gt-tech-ai",
            "OrgWarden",
        ),
    ]:
        parsed_url = validate_url(url)
        assert parsed_url.hostname == hostname
        assert parsed_url.org_name == org
        assert parsed_url.repo_name == repo
