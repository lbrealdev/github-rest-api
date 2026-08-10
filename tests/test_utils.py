from github_rest_cli.utils import (
    format_environment_get,
    format_environment_list,
    format_repo_get,
    format_repo_list,
    project_environment_detail,
    project_environment_summary,
    project_repo_detail,
    project_repo_summary,
)

SAMPLE_REPO = {
    "name": "test-repo",
    "full_name": "test-user/test-repo",
    "owner": {"login": "test-user", "id": 1},
    "description": "A test repository",
    "html_url": "https://github.com/test-user/test-repo",
    "visibility": "public",
    "default_branch": "main",
    "language": "Python",
    "topics": ["cli", "github"],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-06-01T00:00:00Z",
    "pushed_at": "2024-06-02T00:00:00Z",
    "fork": False,
    "archived": False,
    "disabled": False,
    "is_template": True,
}


def test_project_repo_summary():
    assert project_repo_summary(SAMPLE_REPO) == {
        "name": "test-repo",
        "owner": "test-user",
        "url": "https://github.com/test-user/test-repo",
        "visibility": "public",
    }


def test_project_repo_detail_ordered_fields():
    pairs = project_repo_detail(SAMPLE_REPO)
    fields = [field for field, _ in pairs]

    assert fields == [
        "name",
        "full_name",
        "owner",
        "description",
        "visibility",
        "default_branch",
        "language",
        "topics",
        "html_url",
        "created_at",
        "updated_at",
        "pushed_at",
        "fork",
        "archived",
        "disabled",
        "is_template",
    ]
    assert dict(pairs)["topics"] == "cli, github"
    assert dict(pairs)["fork"] == "false"
    assert dict(pairs)["is_template"] == "true"


def test_project_repo_detail_null_and_missing_fields():
    repo = {
        "name": "sparse-repo",
        "owner": {},
        "description": None,
        "topics": None,
    }

    values = dict(project_repo_detail(repo))

    assert values["name"] == "sparse-repo"
    assert values["owner"] == ""
    assert values["description"] == ""
    assert values["topics"] == ""
    assert values["full_name"] == ""
    assert values["language"] == ""
    assert values["fork"] == ""


def test_project_repo_detail_empty_topics():
    repo = {**SAMPLE_REPO, "topics": []}
    values = dict(project_repo_detail(repo))
    assert values["topics"] == ""


def test_format_repo_get_json_is_raw():
    result = format_repo_get(SAMPLE_REPO, "json")
    assert '"login": "test-user"' in result
    assert '"id": 1' in result
    assert '"repositories"' not in result


def test_format_repo_get_table_is_key_value():
    table_text = str(format_repo_get(SAMPLE_REPO, "table"))
    assert "GITHUB REPOSITORY" in table_text.upper()
    assert "FIELD" in table_text.upper()
    assert "VALUE" in table_text.upper()
    assert "default_branch" in table_text
    assert "main" in table_text


def test_format_repo_list_json_is_projected():
    result = format_repo_list([SAMPLE_REPO], "json")
    assert '"repositories"' in result
    assert '"owner": "test-user"' in result
    assert '"login"' not in result


def test_format_repo_list_empty_table_message():
    assert format_repo_list([], "table") == "No repositories found."


def test_format_repo_list_empty_json_unchanged():
    assert format_repo_list([], "json") == '{\n  "repositories": []\n}'


SAMPLE_ENVIRONMENT = {
    "id": 161088068,
    "node_id": "MDExOkVudmlyb25tZW50",
    "name": "production",
    "url": "https://api.github.com/repos/test-user/test-repo/environments/production",
    "html_url": "https://github.com/test-user/test-repo/deployments",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-06-01T00:00:00Z",
    "protection_rules": [{"type": "wait_timer"}, {"type": "required_reviewers"}],
    "deployment_branch_policy": {
        "protected_branches": True,
        "custom_branch_policies": False,
    },
}


def test_project_environment_summary():
    assert project_environment_summary(SAMPLE_ENVIRONMENT) == {
        "name": "production",
        "id": 161088068,
        "protection_rules": "wait_timer, required_reviewers",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-06-01T00:00:00Z",
    }


def test_project_environment_detail_ordered_fields():
    pairs = project_environment_detail(SAMPLE_ENVIRONMENT)
    fields = [field for field, _ in pairs]

    assert fields == [
        "name",
        "id",
        "node_id",
        "url",
        "html_url",
        "created_at",
        "updated_at",
        "protection_rules",
        "deployment_branch_policy",
    ]
    assert dict(pairs)["deployment_branch_policy"] == "protected_branches"
    assert dict(pairs)["id"] == "161088068"


def test_project_environment_detail_null_and_missing_fields():
    values = dict(project_environment_detail({"name": "staging"}))

    assert values["name"] == "staging"
    assert values["protection_rules"] == ""
    assert values["deployment_branch_policy"] == ""
    assert values["html_url"] == ""


def test_format_environment_list_json_is_raw():
    result = format_environment_list(
        {"total_count": 1, "environments": [SAMPLE_ENVIRONMENT]}, "json"
    )
    assert '"total_count": 1' in result
    assert '"node_id"' in result


def test_format_environment_list_table_is_summary():
    table_text = str(
        format_environment_list(
            {"total_count": 1, "environments": [SAMPLE_ENVIRONMENT]}
        )
    )
    assert "GITHUB ENVIRONMENTS" in table_text.upper()
    assert "production" in table_text
    assert "node_id" not in table_text


def test_format_environment_list_empty_table_message():
    assert (
        format_environment_list({"total_count": 0, "environments": []}, "table")
        == "No environments found."
    )


def test_format_environment_list_empty_json_unchanged():
    payload = {"total_count": 0, "environments": []}
    assert format_environment_list(payload, "json") == (
        '{\n  "total_count": 0,\n  "environments": []\n}'
    )


def test_format_environment_get_table_is_key_value():
    table_text = str(format_environment_get(SAMPLE_ENVIRONMENT))
    assert "GITHUB ENVIRONMENT" in table_text.upper()
    assert "FIELD" in table_text.upper()
    assert "VALUE" in table_text.upper()
    assert "node_id" in table_text
