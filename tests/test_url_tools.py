import pytest
from orgwarden.url_tools import validate_url


def test_invalid_urls():
    INVALID_URLS = [
        "",  # empty url
        "github.com/gt-tech-ai/OrgWarden",  # missing protocol
        "https://gt-tech-ai/OrgWarden"  # missing top-level domain
        "/gt-tech-ai/OrgWarden",  # missing site and protocol
        "https://github.com/gt-tech-ai/OrgWarden/extra-bits",  # path too long
        "https://github.com",  # no path
    ]
    for url in INVALID_URLS:
        with pytest.raises(ValueError, match="not a valid URL"):
            _ = validate_url(url)


def test_org_urls():
    TEST_CASES = [  # url, hostname, org_name
        ("https://github.com/gt-tech-ai", "github.com", "gt-tech-ai"),
        ("https://github.gatech.edu/gt-tech-ai", "github.gatech.edu", "gt-tech-ai"),
    ]
    for url, hostname, org in TEST_CASES:
        parsed_url = validate_url(url)
        assert parsed_url.hostname == hostname
        assert parsed_url.org_name == org
        assert parsed_url.repo_name is None


def test_repo_urls():
    TEST_CASES = [  # url, hostname, org_name, repo_name
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
    ]
    for url, hostname, org, repo in TEST_CASES:
        parsed_url = validate_url(url)
        assert parsed_url.hostname == hostname
        assert parsed_url.org_name == org
        assert parsed_url.repo_name == repo
