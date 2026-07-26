from github_rest_cli import api

GET_HEADERS_FUNCTION = "github_rest_cli.api.get_headers"
FETCH_USER_FUNCTION = "github_rest_cli.api.fetch_user"
REQUEST_HANDLER_FUNCTION = "github_rest_cli.api.request_with_handling"


def test_delete_repository(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.delete_repository("my-repo")

    request_mock.assert_called_once()
    assert request_mock.call_args.args[0] == "DELETE"
    assert "test-user/my-repo" in request_mock.call_args.args[1]


def test_delete_repository_org(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.delete_repository("my-repo", org="my-org")

    assert "my-org/my-repo" in request_mock.call_args.args[1]


def test_dependabot_security_enable(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.dependabot_security("my-repo", True)

    assert request_mock.call_count == 2
    assert all(call.args[0] == "PUT" for call in request_mock.call_args_list)


def test_dependabot_security_disable(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.dependabot_security("my-repo", False)

    assert request_mock.call_count == 1
    assert request_mock.call_args.args[0] == "DELETE"


def test_deployment_environment(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.deployment_environment("my-repo", "production")

    request_mock.assert_called_once()
    assert request_mock.call_args.args[0] == "PUT"
    assert request_mock.call_args.args[1].endswith(
        "/repos/test-user/my-repo/environments/production"
    )


def test_deployment_environment_org(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.deployment_environment("my-repo", "staging", org="my-org")

    assert request_mock.call_args.args[1].endswith(
        "/repos/my-org/my-repo/environments/staging"
    )


def test_update_repository(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.update_repository(
        "my-repo",
        description="Updated",
        homepage="https://example.com",
        visibility="private",
        default_branch="main",
        archived=True,
    )

    request_mock.assert_called_once()
    assert request_mock.call_args.args[0] == "PATCH"
    assert request_mock.call_args.args[1].endswith("/repos/test-user/my-repo")
    assert request_mock.call_args.kwargs["json"] == {
        "description": "Updated",
        "homepage": "https://example.com",
        "visibility": "private",
        "private": True,
        "default_branch": "main",
        "archived": True,
    }


def test_update_repository_org(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.update_repository("my-repo", org="my-org", visibility="public", archived=False)

    assert request_mock.call_args.args[1].endswith("/repos/my-org/my-repo")
    assert request_mock.call_args.kwargs["json"] == {
        "visibility": "public",
        "private": False,
        "archived": False,
    }


def test_update_repository_requires_changes(mocker):
    output = mocker.patch("github_rest_cli.api.rich_output")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION)

    result = api.update_repository("my-repo")

    assert result is None
    request_mock.assert_not_called()
    output.assert_called_once()
    assert "No updates specified" in output.call_args.args[0]


def test_update_repository_rename(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.update_repository("old-repo", new_name="new-repo")

    request_mock.assert_called_once()
    assert request_mock.call_args.args[0] == "PATCH"
    assert request_mock.call_args.args[1].endswith("/repos/test-user/old-repo")
    assert request_mock.call_args.kwargs["json"] == {"name": "new-repo"}
    assert (
        request_mock.call_args.kwargs["success_msg"]
        == "Repository successfully updated in test-user/new-repo."
    )


def test_update_repository_as_template(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.update_repository("my-repo", is_template=True)

    assert request_mock.call_args.kwargs["json"] == {"is_template": True}


def test_update_repository_no_template(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.update_repository("my-repo", is_template=False)

    assert request_mock.call_args.kwargs["json"] == {"is_template": False}


def test_create_repository_from_template(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    mocker.patch(FETCH_USER_FUNCTION, return_value="test-user")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.create_repository(
        "my-app",
        "private",
        template="octo/template",
        include_all_branches=True,
    )

    request_mock.assert_called_once()
    assert request_mock.call_args.args[0] == "POST"
    assert request_mock.call_args.args[1].endswith("/repos/octo/template/generate")
    assert request_mock.call_args.kwargs["json"] == {
        "name": "my-app",
        "owner": "test-user",
        "private": True,
        "include_all_branches": True,
    }


def test_create_repository_from_template_org(mocker):
    mocker.patch(GET_HEADERS_FUNCTION, return_value={"Authorization": "token fake"})
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION, return_value=None)

    api.create_repository(
        "my-app",
        "public",
        org="my-org",
        template="octo/template",
    )

    assert request_mock.call_args.kwargs["json"]["owner"] == "my-org"
    assert request_mock.call_args.kwargs["json"]["private"] is False


def test_create_repository_template_rejects_empty(mocker):
    output = mocker.patch("github_rest_cli.api.rich_output")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION)

    result = api.create_repository(
        "my-app",
        "public",
        empty=True,
        template="octo/template",
    )

    assert result is None
    request_mock.assert_not_called()
    assert "--template" in output.call_args.args[0]
    assert "--empty" in output.call_args.args[0]


def test_create_repository_template_rejects_internal(mocker):
    output = mocker.patch("github_rest_cli.api.rich_output")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION)

    result = api.create_repository(
        "my-app",
        "internal",
        template="octo/template",
    )

    assert result is None
    request_mock.assert_not_called()
    assert "--internal" in output.call_args.args[0]


def test_create_repository_template_invalid_ref(mocker):
    output = mocker.patch("github_rest_cli.api.rich_output")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION)

    result = api.create_repository("my-app", "public", template="not-a-ref")

    assert result is None
    request_mock.assert_not_called()
    assert "OWNER/REPO" in output.call_args.args[0]


def test_create_repository_include_all_branches_requires_template(mocker):
    output = mocker.patch("github_rest_cli.api.rich_output")
    request_mock = mocker.patch(REQUEST_HANDLER_FUNCTION)

    result = api.create_repository(
        "my-app",
        "public",
        include_all_branches=True,
    )

    assert result is None
    request_mock.assert_not_called()
    assert "--include-all-branches" in output.call_args.args[0]
