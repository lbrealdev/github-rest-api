from argparse import Namespace

from github_rest_cli.api import (
    delete_environment,
    deployment_environment,
    get_environment,
    list_environments,
)


def run_environment_create(args: Namespace) -> None:
    deployment_environment(args.name, args.env, args.org)


def run_environment_list(args: Namespace) -> None:
    environments = list_environments(
        args.name,
        args.org,
        args.format,
        per_page=args.per_page,
        page=args.page,
    )
    if environments is not None:
        print(environments)  # noqa: T201


def run_environment_get(args: Namespace) -> None:
    environment = get_environment(args.name, args.env, args.org, args.format)
    if environment is not None:
        print(environment)  # noqa: T201


def run_environment_delete(args: Namespace) -> None:
    if not confirm_delete_environment(args.name, args.env, args.org, yes=args.yes):
        print("Aborted.")  # noqa: T201
        return
    delete_environment(args.name, args.env, args.org)


def confirm_delete_environment(
    name: str, env: str, org: str | None = None, *, yes: bool = False
) -> bool:
    """Return True if deletion should proceed."""
    if yes:
        return True

    target = f"{org}/{name}" if org else name
    answer = input(
        f"Delete environment '{env}' in {target}? This cannot be undone. [y/N] "
    )
    return answer.strip().lower() in {"y", "yes"}
