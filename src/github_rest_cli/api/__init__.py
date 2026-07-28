"""GitHub REST API wrappers, grouped by resource.

Every public function is re-exported here so that
``from github_rest_cli.api import <function>`` keeps working.
"""

from github_rest_cli.api.base import build_url, fetch_user, request_with_handling
from github_rest_cli.api.dependabot import dependabot_security
from github_rest_cli.api.environments import (
    delete_environment,
    deployment_environment,
    get_environment,
    list_environments,
)
from github_rest_cli.api.repos import (
    create_repository,
    delete_repository,
    get_repository,
    list_repositories,
    update_repository,
)

__all__ = [
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
