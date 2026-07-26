import pytest

from github_rest_cli.main import __version__, cli
from github_rest_cli.parser import build_parser


def test_version_flag(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--version"])

    assert exc_info.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_help_flag(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--help"])

    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert "repo" in out
    assert "dependabot" in out
    assert "environment" in out


def test_no_command_prints_help(mocker, capsys):
    mocker.patch("sys.argv", ["github-rest-cli"])

    cli()

    out = capsys.readouterr().out
    assert "GitHub REST API" in out or "usage:" in out.lower()


def test_repo_help_lists_subcommands(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["repo", "--help"])

    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert "get" in out
    assert "list" in out
    assert "create" in out
    assert "update" in out
    assert "delete" in out


def test_repo_get_subcommand_help(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["repo", "get", "--help"])

    assert exc_info.value.code == 0
    assert "--name" in capsys.readouterr().out


def test_repo_create_defaults_to_public():
    parser = build_parser()
    args = parser.parse_args(["repo", "create", "--name", "my-repo"])

    assert args.visibility == "public"
    assert args.template is None
    assert args.include_all_branches is False


def test_repo_create_private_flag():
    parser = build_parser()
    args = parser.parse_args(["repo", "create", "--name", "my-repo", "--private"])

    assert args.visibility == "private"


def test_repo_create_template_flags():
    parser = build_parser()
    args = parser.parse_args(
        [
            "repo",
            "create",
            "--name",
            "my-app",
            "--template",
            "owner/template",
            "--include-all-branches",
            "--private",
        ]
    )

    assert args.template == "owner/template"
    assert args.include_all_branches is True
    assert args.visibility == "private"


def test_repo_update_parses_options():
    parser = build_parser()
    args = parser.parse_args(
        [
            "repo",
            "update",
            "--name",
            "my-repo",
            "--new-name",
            "renamed-repo",
            "--description",
            "Updated",
            "--homepage",
            "https://example.com",
            "--private",
            "--default-branch",
            "main",
            "--archived",
        ]
    )

    assert args.repo_command == "update"
    assert args.new_name == "renamed-repo"
    assert args.description == "Updated"
    assert args.homepage == "https://example.com"
    assert args.visibility == "private"
    assert args.default_branch == "main"
    assert args.archived is True


def test_repo_update_defaults_leave_fields_unset():
    parser = build_parser()
    args = parser.parse_args(["repo", "update", "--name", "my-repo"])

    assert args.visibility is None
    assert args.archived is None
    assert args.description is None
    assert args.new_name is None
    assert args.is_template is None


def test_repo_update_new_name_flag():
    parser = build_parser()
    args = parser.parse_args(
        ["repo", "update", "--name", "old-repo", "--new-name", "new-repo"]
    )

    assert args.name == "old-repo"
    assert args.new_name == "new-repo"


def test_repo_update_as_template_flag():
    parser = build_parser()
    args = parser.parse_args(["repo", "update", "--name", "my-repo", "--as-template"])

    assert args.is_template is True


def test_repo_update_no_template_flag():
    parser = build_parser()
    args = parser.parse_args(["repo", "update", "--name", "my-repo", "--no-template"])

    assert args.is_template is False


def test_repo_update_archived_conflict(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(
            ["repo", "update", "--name", "my-repo", "--archived", "--unarchived"]
        )

    assert exc_info.value.code == 2


def test_repo_update_template_conflict(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(
            ["repo", "update", "--name", "my-repo", "--as-template", "--no-template"]
        )

    assert exc_info.value.code == 2


def test_repo_create_public_and_private_conflict(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(
            ["repo", "create", "--name", "my-repo", "--public", "--private"]
        )

    assert exc_info.value.code == 2


def test_repo_list_pagination_defaults():
    parser = build_parser()
    args = parser.parse_args(["repo", "list"])

    assert args.per_page == 20
    assert args.page == 1
    assert args.fetch_all is False


def test_repo_list_pagination_flags():
    parser = build_parser()
    args = parser.parse_args(
        ["repo", "list", "--per-page", "50", "--page", "3", "--all"]
    )

    assert args.per_page == 50
    assert args.page == 3
    assert args.fetch_all is True
