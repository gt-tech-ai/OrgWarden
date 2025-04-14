import typer
from orgwarden.audit_settings import (
    RepoAuditSettings,
    parse_settings_string,
    get_audit_settings,
)
import pytest


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
            with pytest.raises(
                typer.BadParameter, match="does not match expected pattern"
            ):
                _ = parse_settings_string(settings_string)

    def test_valid_settings_strings(self):
        TEST_CASES = [  # input, expected
            ("key: value", RepoAuditSettings("key", "value")),
            ("key: multiple values", RepoAuditSettings("key", "multiple values")),
            ("repo: --arg-1 --arg-2", RepoAuditSettings("repo", "--arg-1 --arg-2")),
            ("repo    :    value", RepoAuditSettings("repo", "value")),
            ("too: many: colons", RepoAuditSettings("too", "many: colons")),
            (
                "'quoted_key': 'quoted_val'",
                RepoAuditSettings("'quoted_key'", "'quoted_val'"),
            ),
            (
                '"quoted_key": "quoted_val"',
                RepoAuditSettings('"quoted_key"', '"quoted_val"'),
            ),
            (
                "repo: --arg-1     --arg-2",
                RepoAuditSettings("repo", "--arg-1     --arg-2"),
            ),
        ]
        for settings_string, expected in TEST_CASES:
            actual = parse_settings_string(settings_string)
            assert actual == expected


class TestGetAuditSettings:
    def test_raises_with_duplicate_repos(self):
        REPOSITORY_SETTINGS = [
            RepoAuditSettings("repo", "value 1"),
            RepoAuditSettings("repo", "value 2"),
        ]
        with pytest.raises(ValueError, match="multiple entries for"):
            _ = get_audit_settings(REPOSITORY_SETTINGS)

    def test_empty_flags(self):
        REPOSITORY_SETTINGS = [RepoAuditSettings("repo", "")]
        audit_settings = get_audit_settings(REPOSITORY_SETTINGS)
        assert len(audit_settings) == 0

    def test_dict_built_correctly(self):
        REPO_AUDIT_SETTINGS = [
            RepoAuditSettings("repo_1", "--arg-1 --arg-2"),
            RepoAuditSettings("repo_2", "--arg-3"),
            RepoAuditSettings("repo_3", "--arg-1 --arg-2 --arg-3"),
        ]
        audit_settings = get_audit_settings(REPO_AUDIT_SETTINGS)
        for setting in REPO_AUDIT_SETTINGS:
            assert setting.repo_name in audit_settings
            assert audit_settings[setting.repo_name] == setting.cli_flags
