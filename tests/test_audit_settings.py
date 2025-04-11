import typer
from orgwarden.repository import Repository
from orgwarden.audit_settings import (
    RepositorySettings,
    parse_settings_string,
    append_settings,
)
import pytest
from pytest import CaptureFixture


class TestParseSettingsString:
    def test_invalid_settings_strings(self):
        INVALID_STRINGS = [
            "",
            "just_a_key",
            "key_no_value: ",
            ": value_no_key",
            ":",
        ]
        for settings_string in INVALID_STRINGS:
            with pytest.raises(typer.BadParameter):
                _ = parse_settings_string(settings_string)

    def test_valid_settings_strings(self):
        TEST_CASES = [  # input, expected
            ("key: value", RepositorySettings("key", "value")),
            ("key: multiple values", RepositorySettings("key", "multiple values")),
            ("repo: --arg-1 --arg-2", RepositorySettings("repo", "--arg-1 --arg-2")),
            ("repo    :    value", RepositorySettings("repo", "value")),
            ("too: many: colons", RepositorySettings("too", "many: colons")),
            (
                "'quoted_key': 'quoted_val'",
                RepositorySettings("'quoted_key'", "'quoted_val'"),
            ),
            (
                '"quoted_key": "quoted_val"',
                RepositorySettings('"quoted_key"', '"quoted_val"'),
            ),
            (
                "repo: --arg-1     --arg-2",
                RepositorySettings("repo", "--arg-1     --arg-2"),
            ),
        ]
        for settings_string, expected in TEST_CASES:
            actual = parse_settings_string(settings_string)
            assert actual == expected


class TestAppendSettings:
    def test_no_mutation(self):
        REPOS = [
            Repository(name="repo_1", url="url_1", org="org_1"),
            Repository(name="repo_2", url="url_2", org="org_2"),
            Repository(name="repo_3", url="url_3", org="org_3"),
        ]
        new_repos = append_settings(REPOS, [])
        for new_repo, og_repo in zip(new_repos, REPOS):
            assert new_repo is not og_repo

    def test_raises_with_duplicate_repos(self):
        REPOSITORY_SETTINGS = [
            RepositorySettings("repo", "value 1"),
            RepositorySettings("repo", "value 2"),
        ]
        with pytest.raises(ValueError):
            _ = append_settings([], REPOSITORY_SETTINGS)

    def test_with_no_matching_settings(self):
        REPOS = [
            Repository(name="repo_1", url="url_1", org="org_1"),
            Repository(name="repo_2", url="url_2", org="org_2"),
            Repository(name="repo_3", url="url_3", org="org_3"),
        ]
        REPOSITORY_SETTINGS = [
            RepositorySettings("non_matching_repo", "--arg-1 --arg-2")
        ]

        repos_with_settings = append_settings(REPOS, REPOSITORY_SETTINGS)
        for repo in repos_with_settings:
            assert repo.cli_flags is None

    def test_added_settings(self):
        REPOS = [
            Repository(name="repo_1", url="url_1", org="org_1"),
            Repository(name="repo_2", url="url_2", org="org_2"),
            Repository(name="repo_3", url="url_3", org="org_3"),
        ]
        REPOSITORY_SETTINGS = [
            RepositorySettings("repo_1", "--arg-1 --arg-2"),
            RepositorySettings("repo_2", "--arg-3"),
            RepositorySettings("repo_3", "--arg-1 --arg-2 --arg-3"),
        ]
        repos_with_settings = append_settings(REPOS, REPOSITORY_SETTINGS)
        for repo, repo_settings in zip(repos_with_settings, repos_with_settings):
            assert repo.name == repo_settings.name
            assert repo.cli_flags == repo_settings.cli_flags

    def test_empty_flags(self):
        REPOS = [Repository(name="repo", url="url", org="org")]
        REPOSITORY_SETTINGS = [RepositorySettings("repo", "")]
        repos_with_settings = append_settings(REPOS, REPOSITORY_SETTINGS)
        for repo in repos_with_settings:
            assert repo.cli_flags is None

    def test_unused_settings(self, capfd: CaptureFixture):
        REPOSITORY_SETTINGS = [RepositorySettings("repo", "--arg")]
        _ = append_settings([], REPOSITORY_SETTINGS)
        stderr = capfd.readouterr().err
        assert "repository is not being audited" in stderr
