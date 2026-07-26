from github_rest_cli import api
from github_rest_cli.main import cli
from github_rest_cli.parser import build_parser, confirm_delete_repository

GET_HEADERS_FUNCTION = "github_rest_cli.api.get_headers"
FETCH_USER_FUNCTION = "github_rest_cli.api.fetch_user"
REQUEST_HANDLER_FUNCTION = "github_rest_cli.api.request_with_handling"


def test_delete_repo_yes_flag_parses():
    parser = build_parser()
    args = parser.parse_args(["repo", "delete", "--name", "my-repo", "--yes"])

    assert args.command == "repo"
    assert args.repo_command == "delete"
    assert args.name == "my-repo"
    assert args.yes is True


def test_delete_repo_short_yes_flag_parses():
    parser = build_parser()
    args = parser.parse_args(["repo", "delete", "-n", "my-repo", "-y"])

    assert args.yes is True


def test_confirm_delete_skips_prompt_with_yes(mocker):
    prompt = mocker.patch("github_rest_cli.parser.input")

    assert confirm_delete_repository("my-repo", yes=True) is True
    prompt.assert_not_called()


def test_confirm_delete_accepts_yes(mocker):
    mocker.patch("github_rest_cli.parser.input", return_value="y")

    assert confirm_delete_repository("my-repo", org="my-org") is True


def test_confirm_delete_rejects_other_answers(mocker):
    mocker.patch("github_rest_cli.parser.input", return_value="n")

    assert confirm_delete_repository("my-repo") is False


def test_cli_delete_repo_aborts_without_confirmation(mocker, capsys):
    mocker.patch(
        "github_rest_cli.parser.confirm_delete_repository",
        return_value=False,
    )
    delete_mock = mocker.patch("github_rest_cli.parser.delete_repository")
    mocker.patch(
        "sys.argv",
        ["github-rest-cli", "repo", "delete", "--name", "my-repo"],
    )

    cli()

    delete_mock.assert_not_called()
    assert "Aborted." in capsys.readouterr().out


def test_cli_delete_repo_proceeds_with_yes(mocker):
    delete_mock = mocker.patch("github_rest_cli.parser.delete_repository")
    prompt = mocker.patch("github_rest_cli.parser.input")
    mocker.patch(
        "sys.argv",
        ["github-rest-cli", "repo", "delete", "--name", "my-repo", "--yes"],
    )

    cli()

    prompt.assert_not_called()
    delete_mock.assert_called_once_with("my-repo", None)


def test_delete_repository_api(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.delete_repository("my-repo")

    request_mock.assert_called_once()
    assert request_mock.call_args.args[0] == "DELETE"
