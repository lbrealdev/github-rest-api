import requests
import argparse
import json
from github_rest_api.config import settings
from rich.console import Console
from rich import print as rprint
from rich.text import Text


GITHUB_URL = f"{settings.API_URL}"
GITHUB_USER = f"{settings.USER}"
GITHUB_TOKEN = f"{settings.AUTH_TOKEN}"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Authorization": f"token {GITHUB_TOKEN}",
}


def rich_output(input_str: str, format_str: str):
    console = Console()
    text = Text(input_str)
    text.stylize(format_str)
    console.print(text)


def get_repository(name: str, org: str):
    url = f"{GITHUB_URL}/repos/{org if org else GITHUB_USER}/{name}"

    try:
        req = requests.get(url, headers=HEADERS)
        req.raise_for_status()
        source_repo = json.loads(req.text)
        rprint(source_repo)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            rich_output(
                "Unauthorized access. Please check your token or credentials.",
                format_str="blink bold red",
            )
        elif e.response.status_code == 404:
            rich_output(
                "The requested repository does not exist!", format_str="blink bold red"
            )
        else:
            rich_output(
                f"Failed to get repository {name}\n"
                + f"Status code: {str(e.response.status_code)}",
                format_str="blink bold red",
            )


def create_repository(name: str, visibility: str, org: str):
    data = {
        "name": name,
        "auto_init": "true",
        "visibility": visibility,
    }

    if visibility == "private":
        data["private"] = True

    try:
        url = f"{GITHUB_URL}/orgs/{org}/repos" if org else f"{GITHUB_URL}/user/repos"
        req = requests.post(url, headers=HEADERS, json=data)
        req.raise_for_status()
        rich_output(
            f"Repository successfully created in {org or GITHUB_USER}/{name}",
            format_str="blink bold green",
        )
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            rich_output(
                "Unauthorized access. Please check your token or credentials.",
                format_str="blink bold red",
            )
        elif e.response.status_code == 422:
            rich_output(
                "Repository name already exists on this account or organization!",
                format_str="blink bold red",
            )
        else:
            rich_output(
                f"Failed to create repository {name}\
                    Status code: {e.response.status_code}",
                format_str="blink bold red",
            )


def delete_repository(name: str, org: str):
    url = f"{GITHUB_URL}/repos/{org if org else GITHUB_USER}/{name}"

    try:
        req = requests.delete(url, headers=HEADERS)
        req.raise_for_status()
        rich_output(
            f"Repository sucessfully deleted in {org or GITHUB_USER}/{name}",
            format_str="blink bold green",
        )
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            rich_output(
                "You are not an admin of this repository!",
                format_str="blink bold red",
            )
        elif e.response.status_code == 404:
            rich_output(
                "The requested repository was not found!",
                format_str="blink bold red",
            )
        else:
            rich_output(
                f"Failed to delete repository {name}\
                    with status code {e.response.status_code}",
                format_str="blink bold red",
            )


def list_repositories(page: int, property: str, role: str, org: str):
    params = {"per_page": page, "sort": property, "type": role}

    if org:
        if role in ["private", "forks", "sources", "member"]:
            params["type"] = role
        else:
            params["type"] = "all"

    try:
        url = f"{GITHUB_URL}/orgs/{org}/repos" if org else f"{GITHUB_URL}/user/repos"
        req = requests.get(url, headers=HEADERS, params=params)
        req.raise_for_status()
        repositories = json.loads(req.text)
        repository_full_name = [repo["full_name"] for repo in repositories]
        rich_output(
            "\n".join([f"- {repos}" for repos in repository_full_name]),
            format_str="blink bold green",
        )
        rich_output(
            f"\nTotal repositories: {len(repository_full_name)}",
            format_str="blink bold green",
        )
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            rich_output(
                "Unauthorized access. Please check your token or credentials.",
                format_str="blink bold red",
            )
        else:
            rich_output(
                f"Failed to list repositories for {org or GITHUB_USER}"
                + f"Status code: {e.response.status_code}",
                format_str="blink bold red",
            )


def dependabot_security(name: str, org: str, enabled: bool):
    is_enabled = bool(enabled)

    url = f"{GITHUB_URL}/repos/{org if org else GITHUB_USER}/{name}"
    dependabot_endpoints = ["vulnerability-alerts", "automated-security-fixes"]

    try:
        if is_enabled:
            for endpoint in dependabot_endpoints:
                req = requests.put(f"{url}/{endpoint}", headers=HEADERS)
                req.raise_for_status()
            rich_output(
                f"Dependabot has been activated on repository {org or GITHUB_USER}/{name}",
                format_str="blink bold green",
            )
        else:
            req = requests.delete(f"{url}/vulnerability-alerts", headers=HEADERS)
            req.raise_for_status()
            rich_output(
                f"Dependabot has been disabled on repository {org or GITHUB_USER}/{name}",
                format_str="blink bold green",
            )
    except requests.exceptions.RequestException as e:
        rprint(f"Error: {e}")


def deployment_environment(name: str, env: str, org: str):
    url = f"{GITHUB_URL}/repos/{org if org else GITHUB_USER}/{name}/environments/{env}"

    try:
        req = requests.put(url, headers=HEADERS)
        req.raise_for_status()
        rich_output(
            f"Environment '{env.upper()}' created.\n"
            + f"Repository: {org or GITHUB_USER}/{name}",
            format_str="blink bold green",
        )
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            rich_output(
                f"Failed to create environment {env.upper()}",
                format_str="blink bold red",
            )
        else:
            rprint(f"Error: {e}")


def cli():
    """
    Create parsers and subparsers for CLI arguments
    """
    global_parser = argparse.ArgumentParser(
        description="Python CLI to GitHub REST API",
    )
    subparsers = global_parser.add_subparsers(
        help="Python GitHub REST API commands", dest="command"
    )

    # Subparser for "get-repository" function
    get_repo_parser = subparsers.add_parser(
        "get-repo", help="Get repository information"
    )
    get_repo_parser.add_argument(
        "-n",
        "--name",
        help="The repository name",
        required=True,
        dest="name",
    )
    get_repo_parser.add_argument(
        "-o", "--org", help="The organization name", required=False, dest="org"
    )

    # Subparser for "list-repository" function
    list_repo_parser = subparsers.add_parser(
        "list-repo",
        help="List repositories for authenticated user",
    )
    list_repo_parser.add_argument(
        "-r",
        "--role",
        required=False,
        default="owner",
        dest="role",
        help="List repositories by role",
    )
    list_repo_parser.add_argument(
        "-p",
        "--page",
        required=False,
        default=30,
        type=int,
        dest="page",
        help="The number of results",
    )
    list_repo_parser.add_argument(
        "-s",
        "--sort",
        required=False,
        default="pushed",
        dest="sort",
        help="List repositories sorted by",
    )
    list_repo_parser.add_argument(
        "-o", "--org", help="The organization name", required=False, dest="org"
    )

    # Subparser for "create-repository" function
    create_repo_parser = subparsers.add_parser(
        "create-repo",
        help="Create a new repository",
    )
    create_repo_parser.add_argument(
        "-n",
        "--name",
        required=True,
        dest="name",
        help="The repository name",
    )
    create_repo_parser.add_argument(
        "-v",
        "--visibility",
        required=False,
        default="public",
        dest="visibility",
        help="The visibility of the repository",
    )
    create_repo_parser.add_argument(
        "-o",
        "--org",
        required=False,
        dest="org",
        help="The organization name",
    )

    # Subparser for "delete-repository" function
    delete_repo_parser = subparsers.add_parser(
        "delete-repo",
        help="Delete a repository",
    )
    delete_repo_parser.add_argument(
        "-n",
        "--name",
        required=True,
        dest="name",
        help="The repository name",
    )
    delete_repo_parser.add_argument(
        "-o",
        "--org",
        required=False,
        dest="org",
        help="The organization name",
    )

    # Subparser for "delete-repository" function
    dependabot_parser = subparsers.add_parser(
        "dependabot",
        help="Github Dependabot security updates",
    )
    dependabot_parser.add_argument(
        "-n",
        "--name",
        required=True,
        dest="name",
        help="The repository name",
    )
    dependabot_parser.add_argument(
        "-o",
        "--org",
        dest="org",
        help="The organization name",
    )
    dependabot_parser.add_argument(
        "--enable",
        required=False,
        action="store_true",
        dest="control",
        help="Enable dependabot security updates",
    )
    dependabot_parser.add_argument(
        "--disable",
        required=False,
        action="store_false",
        dest="control",
        help="Disable dependabot security updates",
    )

    # Subparser for "deployment-environments" function
    deploy_env_parser = subparsers.add_parser(
        "environment",
        help="Github Deployment environments",
    )
    deploy_env_parser.add_argument(
        "-n",
        "--name",
        required=True,
        dest="name",
        help="The repository name",
    )
    deploy_env_parser.add_argument(
        "-e",
        "--env",
        required=True,
        dest="env",
        help="Deployment environment name",
    )
    deploy_env_parser.add_argument(
        "-o",
        "--org",
        required=False,
        dest="org",
        help="The organization name",
    )

    # guard clause pattern
    args = global_parser.parse_args()
    command = args.command

    if command == "get-repo":
        return get_repository(args.name, args.org)
    if command == "list-repo":
        return list_repositories(args.page, args.sort, args.role, args.org)
    if command == "create-repo":
        return create_repository(args.name, args.visibility, args.org)
    if command == "delete-repo":
        return delete_repository(args.name, args.org)
    if command == "dependabot":
        return dependabot_security(args.name, args.org, args.control)
    if command == "environment":
        return deployment_environment(args.name, args.env, args.org)
    return False


if __name__ == "__main__":
    cli()
