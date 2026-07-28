"""Argparse handlers that bridge parsed CLI arguments to the API layer."""

from github_rest_cli.handlers.dependabot import run_dependabot
from github_rest_cli.handlers.environments import (
    confirm_delete_environment,
    run_environment_create,
    run_environment_delete,
    run_environment_get,
    run_environment_list,
)
from github_rest_cli.handlers.repos import (
    confirm_delete_repository,
    run_create_repo,
    run_delete_repo,
    run_get_repo,
    run_list_repo,
    run_update_repo,
)

__all__ = [
    "confirm_delete_environment",
    "confirm_delete_repository",
    "run_create_repo",
    "run_delete_repo",
    "run_dependabot",
    "run_environment_create",
    "run_environment_delete",
    "run_environment_get",
    "run_environment_list",
    "run_get_repo",
    "run_list_repo",
    "run_update_repo",
]
