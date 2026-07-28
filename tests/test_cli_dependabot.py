import pytest

from github_rest_cli import api
from github_rest_cli.parser import build_parser

GET_HEADERS_FUNCTION = "github_rest_cli.api.base.get_headers"
FETCH_USER_FUNCTION = "github_rest_cli.api.base.fetch_user"
REQUEST_HANDLER_FUNCTION = "github_rest_cli.api.base.request_with_handling"


def test_dependabot_enable_subcommand():
    parser = build_parser()
    args = parser.parse_args(["dependabot", "enable", "--name", "my-repo"])

    assert args.command == "dependabot"
    assert args.dependabot_command == "enable"
    assert args.name == "my-repo"
    assert args.control is True
    assert args.org is None


def test_dependabot_disable_subcommand():
    parser = build_parser()
    args = parser.parse_args(
        ["dependabot", "disable", "--name", "my-repo", "--org", "my-org"]
    )

    assert args.command == "dependabot"
    assert args.dependabot_command == "disable"
    assert args.name == "my-repo"
    assert args.org == "my-org"
    assert args.control is False


def test_dependabot_missing_subcommand_errors(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["dependabot", "--name", "my-repo"])

    assert exc_info.value.code == 2


def test_dependabot_security_enable(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.dependabot_security("my-repo", True)

    assert request_mock.call_count == 2
    methods = [call.args[0] for call in request_mock.call_args_list]
    assert methods == ["PUT", "PUT"]


def test_dependabot_security_disable(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.dependabot_security("my-repo", False)

    assert request_mock.call_count == 1
    assert request_mock.call_args.args[0] == "DELETE"
