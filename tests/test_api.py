from github_rest_cli import api

BACKWARD_COMPATIBLE_EXPORTS = [
    "build_url",
    "create_repository",
    "delete_environment",
    "delete_repository",
    "dependabot_security",
    "deployment_environment",
    "fetch_user",
    "get_environment",
    "get_repository",
    "list_environments",
    "list_repositories",
    "request_with_handling",
    "update_repository",
]

GET_HEADERS_FUNCTION = "github_rest_cli.api.base.get_headers"
FETCH_USER_FUNCTION = "github_rest_cli.api.base.fetch_user"
REQUEST_HANDLER_FUNCTION = "github_rest_cli.api.base.request_with_handling"


def test_api_package_reexports_public_functions():
    """The api package split must keep `from github_rest_cli.api import X` working."""
    for name in BACKWARD_COMPATIBLE_EXPORTS:
        assert callable(getattr(api, name)), name


def test_fetch_user(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"login": "test-user"}
    mock_response.raise_for_status = lambda: None

    mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=mock_response)

    result = api.fetch_user()

    assert result == "test-user"


def test_create_repository_user(mocker):
    expected_message = "Repository successfully created in test-user/test-repo."

    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=expected_message)

    result = api.create_repository("test-repo", "public")

    assert result == expected_message


def test_create_repository_org(mocker):
    expected_message = "Repository successfully created in test-org/test-repo."

    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=expected_message)

    result = api.create_repository("test-repo", "public", "test-org")

    assert result == expected_message


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
    "is_template": False,
}


def _mock_repo_response(mocker, payload):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = payload
    mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=mock_response)


def test_get_repository_json_format(mocker):
    _mock_repo_response(mocker, SAMPLE_REPO)

    result = api.get_repository("test-repo", output_format="json")

    assert isinstance(result, str)
    assert '"name": "test-repo"' in result
    assert '"visibility": "public"' in result
    assert '"login": "test-user"' in result
    assert '"id": 1' in result


def test_get_repository_table_format(mocker):
    _mock_repo_response(mocker, SAMPLE_REPO)

    result = api.get_repository("test-repo", output_format="table")

    table_text = str(result)
    assert "GITHUB REPOSITORY" in table_text.upper()
    assert "FIELD" in table_text.upper()
    assert "VALUE" in table_text.upper()
    assert "test-repo" in table_text
    assert "test-user" in table_text
    assert "default_branch" in table_text
    assert "main" in table_text
    assert "is_template" in table_text
    assert not table_text.strip().startswith("{")


def test_list_repositories_json_format(mocker):
    _mock_repo_response(mocker, [SAMPLE_REPO])

    result = api.list_repositories(20, 1, "pushed", None, "json")

    assert isinstance(result, str)
    assert '"repositories"' in result
    assert '"name": "test-repo"' in result
    assert '"owner": "test-user"' in result
    assert '"login"' not in result


def test_list_repositories_table_format(mocker):
    _mock_repo_response(mocker, [SAMPLE_REPO])

    result = api.list_repositories(20, 1, "pushed", None, "table")

    table_text = str(result)
    assert "test-repo" in table_text
    assert "GITHUB REPOSITORIES" in table_text.upper()


def test_list_repositories_passes_page_params(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [SAMPLE_REPO]
    mock_response.links = {}
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=mock_response)

    api.list_repositories(30, 2, "updated", "owner", "json")

    assert request_mock.call_count == 1
    _, kwargs = request_mock.call_args
    assert kwargs["params"] == {
        "per_page": 30,
        "page": 2,
        "sort": "updated",
        "type": "owner",
    }


def test_list_repositories_uses_org_endpoint(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    fetch_user = mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [SAMPLE_REPO]
    mock_response.links = {}
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=mock_response)

    api.list_repositories(20, 1, "pushed", None, "json", org="my-org")

    fetch_user.assert_not_called()
    assert request_mock.call_args.args[1].endswith("/orgs/my-org/repos")
    assert request_mock.call_args.kwargs["error_msg"][404] == (
        "The requested organization does not exist."
    )


def test_list_repositories_without_org_uses_user_endpoint(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [SAMPLE_REPO]
    mock_response.links = {}
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=mock_response)

    api.list_repositories(20, 1, "pushed", None, "json")

    assert request_mock.call_args.args[1].endswith("/user/repos")
    assert 404 not in request_mock.call_args.kwargs["error_msg"]


def test_list_repositories_org_fetch_all_follows_link_headers(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})

    first = mocker.Mock()
    first.status_code = 200
    first.json.return_value = [SAMPLE_REPO]
    first.links = {"next": {"url": "https://api.github.com/orgs/my-org/repos?page=2"}}

    second = mocker.Mock()
    second.status_code = 200
    second.json.return_value = []
    second.links = {}

    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, side_effect=[first, second])

    api.list_repositories(20, 1, "pushed", None, "json", fetch_all=True, org="my-org")

    assert request_mock.call_count == 2
    assert request_mock.call_args_list[0].args[1].endswith("/orgs/my-org/repos")
    assert (
        request_mock.call_args_list[1].args[1]
        == "https://api.github.com/orgs/my-org/repos?page=2"
    )


def test_list_repositories_fetch_all_follows_link_headers(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})

    page1 = {
        "name": "repo-one",
        "owner": {"login": "test-user"},
        "html_url": "https://github.com/test-user/repo-one",
        "visibility": "public",
    }
    page2 = {
        "name": "repo-two",
        "owner": {"login": "test-user"},
        "html_url": "https://github.com/test-user/repo-two",
        "visibility": "private",
    }

    first = mocker.Mock()
    first.status_code = 200
    first.json.return_value = [page1]
    first.links = {"next": {"url": "https://api.github.com/user/repos?page=2"}}

    second = mocker.Mock()
    second.status_code = 200
    second.json.return_value = [page2]
    second.links = {}

    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, side_effect=[first, second])

    result = api.list_repositories(20, 5, "pushed", None, "json", fetch_all=True)

    assert request_mock.call_count == 2
    _, first_kwargs = request_mock.call_args_list[0]
    assert first_kwargs["params"]["page"] == 1
    assert first_kwargs["params"]["per_page"] == 20

    second_args, second_kwargs = request_mock.call_args_list[1]
    assert second_args[1] == "https://api.github.com/user/repos?page=2"
    assert second_kwargs["params"] is None

    assert '"name": "repo-one"' in result
    assert '"name": "repo-two"' in result
