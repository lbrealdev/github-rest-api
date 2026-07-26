from github_rest_cli.utils import (
    format_repo_get,
    format_repo_list,
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
