import pytest

from github_rest_cli import api
from github_rest_cli.handlers.environments import confirm_delete_environment
from github_rest_cli.main import cli
from github_rest_cli.parser import build_parser

GET_HEADERS_FUNCTION = "github_rest_cli.api.base.get_headers"
FETCH_USER_FUNCTION = "github_rest_cli.api.base.fetch_user"
REQUEST_HANDLER_FUNCTION = "github_rest_cli.api.base.request_with_handling"

SAMPLE_ENVIRONMENT = {
    "id": 161088068,
    "node_id": "MDExOkVudmlyb25tZW50MTYxMDg4MDY4",
    "name": "production",
    "url": "https://api.github.com/repos/test-user/my-repo/environments/production",
    "html_url": "https://github.com/test-user/my-repo/deployments/activity_log?environments_filter=production",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-06-01T00:00:00Z",
    "protection_rules": [
        {"id": 1, "type": "wait_timer", "wait_timer": 30},
        {"id": 2, "type": "required_reviewers"},
    ],
    "deployment_branch_policy": {
        "protected_branches": True,
        "custom_branch_policies": False,
    },
}

SAMPLE_ENVIRONMENT_LIST = {
    "total_count": 1,
    "environments": [SAMPLE_ENVIRONMENT],
}


def _mock_environment_response(mocker, payload):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = payload
    return mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=mock_response)


def test_list_environments_table_format(mocker):
    request_mock = _mock_environment_response(mocker, SAMPLE_ENVIRONMENT_LIST)

    result = api.list_environments("my-repo")

    assert request_mock.call_args.args[0] == "GET"
    assert request_mock.call_args.args[1].endswith(
        "/repos/test-user/my-repo/environments"
    )
    table_text = str(result)
    assert "GITHUB ENVIRONMENTS" in table_text.upper()
    assert "production" in table_text
    assert "wait_timer, required_reviewers" in table_text


def test_list_environments_json_format(mocker):
    _mock_environment_response(mocker, SAMPLE_ENVIRONMENT_LIST)

    result = api.list_environments("my-repo", output_format="json")

    assert '"total_count": 1' in result
    assert '"name": "production"' in result
    assert '"node_id"' in result


def test_list_environments_pagination_params(mocker):
    request_mock = _mock_environment_response(mocker, SAMPLE_ENVIRONMENT_LIST)

    api.list_environments("my-repo", per_page=50, page=2)

    assert request_mock.call_args.kwargs["params"] == {"per_page": 50, "page": 2}


def test_list_environments_org(mocker):
    request_mock = _mock_environment_response(mocker, SAMPLE_ENVIRONMENT_LIST)

    api.list_environments("my-repo", org="my-org")

    assert request_mock.call_args.args[1].endswith("/repos/my-org/my-repo/environments")


def test_list_environments_returns_none_on_error(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    assert api.list_environments("my-repo") is None


def test_list_environments_empty_payload(mocker):
    _mock_environment_response(mocker, {"total_count": 0, "environments": []})

    table_text = str(api.list_environments("my-repo"))

    assert "GITHUB ENVIRONMENTS" in table_text.upper()


def test_get_environment_table_format(mocker):
    request_mock = _mock_environment_response(mocker, SAMPLE_ENVIRONMENT)

    result = api.get_environment("my-repo", "production")

    assert request_mock.call_args.args[0] == "GET"
    assert request_mock.call_args.args[1].endswith(
        "/repos/test-user/my-repo/environments/production"
    )
    table_text = str(result)
    assert "GITHUB ENVIRONMENT" in table_text.upper()
    assert "FIELD" in table_text.upper()
    assert "production" in table_text
    assert "protected_branches" in table_text


def test_get_environment_json_format(mocker):
    _mock_environment_response(mocker, SAMPLE_ENVIRONMENT)

    result = api.get_environment("my-repo", "production", output_format="json")

    assert '"name": "production"' in result
    assert '"wait_timer": 30' in result


def test_get_environment_org(mocker):
    request_mock = _mock_environment_response(mocker, SAMPLE_ENVIRONMENT)

    api.get_environment("my-repo", "staging", org="my-org")

    assert request_mock.call_args.args[1].endswith(
        "/repos/my-org/my-repo/environments/staging"
    )


def test_get_environment_returns_none_on_error(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    assert api.get_environment("my-repo", "production") is None


def test_delete_environment(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.delete_environment("my-repo", "production")

    request_mock.assert_called_once()
    assert request_mock.call_args.args[0] == "DELETE"
    assert request_mock.call_args.args[1].endswith(
        "/repos/test-user/my-repo/environments/production"
    )
    assert request_mock.call_args.kwargs["success_msg"] == (
        "Environment production has been deleted successfully in test-user/my-repo."
    )


def test_delete_environment_org(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.delete_environment("my-repo", "staging", org="my-org")

    assert request_mock.call_args.args[1].endswith(
        "/repos/my-org/my-repo/environments/staging"
    )


def test_environment_list_subcommand_parses():
    parser = build_parser()
    args = parser.parse_args(
        ["environment", "list", "--name", "my-repo", "--org", "my-org"]
    )

    assert args.command == "environment"
    assert args.environment_command == "list"
    assert args.name == "my-repo"
    assert args.org == "my-org"
    assert args.per_page == 20
    assert args.page == 1
    assert args.format == "table"


def test_environment_list_requires_name():
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["environment", "list"])

    assert exc_info.value.code == 2


def test_environment_get_subcommand_parses():
    parser = build_parser()
    args = parser.parse_args(
        ["environment", "get", "--name", "my-repo", "--env", "production", "-f", "json"]
    )

    assert args.environment_command == "get"
    assert args.env == "production"
    assert args.format == "json"


def test_environment_get_requires_env():
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["environment", "get", "--name", "my-repo"])

    assert exc_info.value.code == 2


def test_environment_delete_subcommand_parses():
    parser = build_parser()
    args = parser.parse_args(
        ["environment", "delete", "-n", "my-repo", "-e", "production", "-y"]
    )

    assert args.environment_command == "delete"
    assert args.env == "production"
    assert args.yes is True


def test_confirm_delete_environment_skips_prompt_with_yes(mocker):
    prompt = mocker.patch("github_rest_cli.handlers.environments.input")

    assert confirm_delete_environment("my-repo", "production", yes=True) is True
    prompt.assert_not_called()


def test_confirm_delete_environment_accepts_yes(mocker):
    prompt = mocker.patch(
        "github_rest_cli.handlers.environments.input", return_value="y"
    )

    assert confirm_delete_environment("my-repo", "production", org="my-org") is True
    assert (
        "Delete environment 'production' in my-org/my-repo?" in prompt.call_args.args[0]
    )


def test_confirm_delete_environment_rejects_other_answers(mocker):
    mocker.patch("github_rest_cli.handlers.environments.input", return_value="n")

    assert confirm_delete_environment("my-repo", "production") is False


def test_cli_environment_delete_aborts_without_confirmation(mocker, capsys):
    mocker.patch(
        "github_rest_cli.handlers.environments.confirm_delete_environment",
        return_value=False,
    )
    delete_mock = mocker.patch(
        "github_rest_cli.handlers.environments.delete_environment"
    )
    mocker.patch(
        "sys.argv",
        ["github-rest-cli", "environment", "delete", "-n", "my-repo", "-e", "prod"],
    )

    cli()

    delete_mock.assert_not_called()
    assert "Aborted." in capsys.readouterr().out


def test_cli_environment_delete_proceeds_with_yes(mocker):
    delete_mock = mocker.patch(
        "github_rest_cli.handlers.environments.delete_environment"
    )
    prompt = mocker.patch("github_rest_cli.handlers.environments.input")
    mocker.patch(
        "sys.argv",
        [
            "github-rest-cli",
            "environment",
            "delete",
            "-n",
            "my-repo",
            "-e",
            "prod",
            "--yes",
        ],
    )

    cli()

    prompt.assert_not_called()
    delete_mock.assert_called_once_with("my-repo", "prod", None)


def test_cli_environment_list_prints_result(mocker, capsys):
    mocker.patch(
        "github_rest_cli.handlers.environments.list_environments",
        return_value="ENV TABLE",
    )
    mocker.patch(
        "sys.argv",
        ["github-rest-cli", "environment", "list", "--name", "my-repo"],
    )

    cli()

    assert "ENV TABLE" in capsys.readouterr().out


def test_cli_environment_get_prints_result(mocker, capsys):
    get_mock = mocker.patch(
        "github_rest_cli.handlers.environments.get_environment",
        return_value="ENV DETAIL",
    )
    mocker.patch(
        "sys.argv",
        ["github-rest-cli", "environment", "get", "-n", "my-repo", "-e", "prod"],
    )

    cli()

    get_mock.assert_called_once_with("my-repo", "prod", None, "table")
    assert "ENV DETAIL" in capsys.readouterr().out
