import argparse
from importlib.metadata import version

from github_rest_cli.handlers import (
    run_create_repo,
    run_delete_repo,
    run_dependabot,
    run_environment_create,
    run_environment_delete,
    run_environment_get,
    run_environment_list,
    run_get_repo,
    run_list_repo,
    run_update_repo,
)


class _HelpFormatter(argparse.HelpFormatter):
    """Widen the option column so flag help stays on one line."""

    def __init__(self, prog: str) -> None:
        super().__init__(prog, max_help_position=40)


def _add_org_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-o", "--org", help="The organization name", required=False, dest="org"
    )


def _add_repo_name_args(
    parser: argparse.ArgumentParser, *, name_required: bool = True
) -> None:
    parser.add_argument(
        "-n",
        "--name",
        help="The repository name",
        required=name_required,
        dest="name",
    )
    _add_org_arg(parser)


def _add_env_name_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-e",
        "--env",
        required=True,
        dest="env",
        help="Deployment environment name",
    )


def _add_pagination_args(
    parser: argparse.ArgumentParser, *, page_help: str = "Page number to fetch"
) -> None:
    parser.add_argument(
        "--per-page",
        required=False,
        default=20,
        type=int,
        dest="per_page",
        help="Number of results per page (max 100)",
    )
    parser.add_argument(
        "-p",
        "--page",
        required=False,
        default=1,
        type=int,
        dest="page",
        help=page_help,
    )


def _add_format_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-f",
        "--format",
        metavar="FORMAT",
        required=False,
        default="table",
        choices=["table", "json"],
        dest="format",
        help="Output format (table or json)",
    )


def _subcommand(
    subparsers: argparse._SubParsersAction,
    name: str,
    *,
    help: str,
) -> argparse.ArgumentParser:
    return subparsers.add_parser(name, help=help, formatter_class=_HelpFormatter)


def build_parser() -> argparse.ArgumentParser:
    """
    Create parsers and subparsers for CLI arguments
    """
    parser = argparse.ArgumentParser(
        description="Python CLI for GitHub REST API",
        formatter_class=_HelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {version('github-rest-cli')}",
    )

    subparsers = parser.add_subparsers(help="GitHub REST API commands", dest="command")

    # repo {get,list,create,update,delete}
    repo_parser = _subcommand(subparsers, "repo", help="Manage repositories")
    repo_subparsers = repo_parser.add_subparsers(
        help="Repository commands", dest="repo_command"
    )
    repo_subparsers.required = True

    get_repo_parser = _subcommand(
        repo_subparsers, "get", help="Get a repository's details"
    )
    _add_repo_name_args(get_repo_parser)
    _add_format_arg(get_repo_parser)
    get_repo_parser.set_defaults(func=run_get_repo)

    list_repo_parser = _subcommand(
        repo_subparsers,
        "list",
        help="List your repositories",
    )
    _add_org_arg(list_repo_parser)
    list_repo_parser.add_argument(
        "-r",
        "--role",
        required=False,
        dest="role",
        help="List repositories by role",
    )
    _add_pagination_args(
        list_repo_parser, page_help="Page number to fetch (ignored with --all)"
    )
    list_repo_parser.add_argument(
        "--all",
        action="store_true",
        dest="fetch_all",
        help="Fetch all pages (follows Link headers)",
    )
    list_repo_parser.add_argument(
        "-s",
        "--sort",
        required=False,
        default="pushed",
        dest="sort",
        help="List repositories sorted by",
    )
    _add_format_arg(list_repo_parser)
    list_repo_parser.set_defaults(func=run_list_repo)

    create_repo_parser = _subcommand(
        repo_subparsers,
        "create",
        help="Create a new repository",
    )
    _add_repo_name_args(create_repo_parser)
    visibility = create_repo_parser.add_mutually_exclusive_group()
    visibility.add_argument(
        "--public",
        action="store_const",
        const="public",
        dest="visibility",
        help="Make the repository public (default)",
    )
    visibility.add_argument(
        "--private",
        action="store_const",
        const="private",
        dest="visibility",
        help="Make the repository private",
    )
    visibility.add_argument(
        "--internal",
        action="store_const",
        const="internal",
        dest="visibility",
        help="Make the repository internal",
    )
    create_repo_parser.add_argument(
        "-e",
        "--empty",
        required=False,
        action="store_true",
        dest="empty",
        help="Create an empty repository",
    )
    create_repo_parser.add_argument(
        "--template",
        metavar="OWNER/REPO",
        required=False,
        default=None,
        dest="template",
        help="Create from a template repository (OWNER/REPO)",
    )
    create_repo_parser.add_argument(
        "--include-all-branches",
        required=False,
        action="store_true",
        dest="include_all_branches",
        help="Include all branches from the template repository",
    )
    create_repo_parser.set_defaults(visibility="public", func=run_create_repo)

    update_repo_parser = _subcommand(
        repo_subparsers,
        "update",
        help="Update an existing repository",
    )
    _add_repo_name_args(update_repo_parser)
    update_repo_parser.add_argument(
        "--new-name",
        required=False,
        default=None,
        dest="new_name",
        help="Rename the repository",
    )
    update_repo_parser.add_argument(
        "--description",
        required=False,
        default=None,
        dest="description",
        help="Short description of the repository",
    )
    update_repo_parser.add_argument(
        "--homepage",
        required=False,
        default=None,
        dest="homepage",
        help="Homepage URL for the repository",
    )
    update_visibility = update_repo_parser.add_mutually_exclusive_group()
    update_visibility.add_argument(
        "--public",
        action="store_const",
        const="public",
        dest="visibility",
        help="Make the repository public",
    )
    update_visibility.add_argument(
        "--private",
        action="store_const",
        const="private",
        dest="visibility",
        help="Make the repository private",
    )
    update_visibility.add_argument(
        "--internal",
        action="store_const",
        const="internal",
        dest="visibility",
        help="Make the repository internal",
    )
    update_repo_parser.add_argument(
        "--default-branch",
        required=False,
        default=None,
        dest="default_branch",
        help="Default branch name",
    )
    update_archived = update_repo_parser.add_mutually_exclusive_group()
    update_archived.add_argument(
        "--archived",
        action="store_const",
        const=True,
        dest="archived",
        help="Archive the repository",
    )
    update_archived.add_argument(
        "--unarchived",
        action="store_const",
        const=False,
        dest="archived",
        help="Unarchive the repository",
    )
    update_template = update_repo_parser.add_mutually_exclusive_group()
    update_template.add_argument(
        "--as-template",
        action="store_const",
        const=True,
        dest="is_template",
        help="Mark the repository as a template",
    )
    update_template.add_argument(
        "--no-template",
        action="store_const",
        const=False,
        dest="is_template",
        help="Unmark the repository as a template",
    )
    update_repo_parser.set_defaults(
        visibility=None, archived=None, is_template=None, func=run_update_repo
    )

    delete_repo_parser = _subcommand(
        repo_subparsers,
        "delete",
        help="Delete an existing repository",
    )
    _add_repo_name_args(delete_repo_parser)
    delete_repo_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        dest="yes",
        help="Skip the confirmation prompt and delete immediately",
    )
    delete_repo_parser.set_defaults(func=run_delete_repo)

    # dependabot {enable,disable}
    dependabot_parser = _subcommand(
        subparsers,
        "dependabot",
        help="Manage Dependabot settings",
    )
    dependabot_subparsers = dependabot_parser.add_subparsers(
        help="Dependabot commands", dest="dependabot_command"
    )
    dependabot_subparsers.required = True

    dependabot_enable_parser = _subcommand(
        dependabot_subparsers,
        "enable",
        help="Enable Dependabot security updates",
    )
    _add_repo_name_args(dependabot_enable_parser)
    dependabot_enable_parser.set_defaults(func=run_dependabot, control=True)

    dependabot_disable_parser = _subcommand(
        dependabot_subparsers,
        "disable",
        help="Disable Dependabot security updates",
    )
    _add_repo_name_args(dependabot_disable_parser)
    dependabot_disable_parser.set_defaults(func=run_dependabot, control=False)

    # environment {create,list,get,delete}
    environment_parser = _subcommand(
        subparsers,
        "environment",
        help="Manage deployment environments",
    )
    environment_subparsers = environment_parser.add_subparsers(
        help="Environment commands", dest="environment_command"
    )
    environment_subparsers.required = True

    environment_create_parser = _subcommand(
        environment_subparsers,
        "create",
        help="Create a deployment environment",
    )
    _add_repo_name_args(environment_create_parser)
    _add_env_name_arg(environment_create_parser)
    environment_create_parser.set_defaults(func=run_environment_create)

    environment_list_parser = _subcommand(
        environment_subparsers,
        "list",
        help="List deployment environments",
    )
    _add_repo_name_args(environment_list_parser)
    _add_pagination_args(
        environment_list_parser, page_help="Page number to fetch (ignored with --all)"
    )
    environment_list_parser.add_argument(
        "--all",
        action="store_true",
        dest="fetch_all",
        help="Fetch all pages (follows Link headers)",
    )
    _add_format_arg(environment_list_parser)
    environment_list_parser.set_defaults(func=run_environment_list)

    environment_get_parser = _subcommand(
        environment_subparsers,
        "get",
        help="Get a deployment environment's details",
    )
    _add_repo_name_args(environment_get_parser)
    _add_env_name_arg(environment_get_parser)
    _add_format_arg(environment_get_parser)
    environment_get_parser.set_defaults(func=run_environment_get)

    environment_delete_parser = _subcommand(
        environment_subparsers,
        "delete",
        help="Delete a deployment environment",
    )
    _add_repo_name_args(environment_delete_parser)
    _add_env_name_arg(environment_delete_parser)
    environment_delete_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        dest="yes",
        help="Skip the confirmation prompt and delete immediately",
    )
    environment_delete_parser.set_defaults(func=run_environment_delete)

    return parser
