import requests

from github_rest_cli.globals import get_api_url, get_headers
from github_rest_cli.utils import format_repo_get, format_repo_list, rich_output


def request_with_handling(
    method, url, success_msg: str | None = None, error_msg: str | None = None, **kwargs
):
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        if success_msg:
            rich_output(success_msg)
        else:
            return response
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if error_msg and status in error_msg:
            rich_output(error_msg[status], format_str="bold red")
        else:
            rich_output(f"Request failed: status code {status}", format_str="bold red")
        return None
    except requests.exceptions.RequestException as e:
        rich_output(f"Request error: {e}", format_str="bold red")
        return None


def build_url(*segments: str) -> str:
    """
    Build an GitHub REST API endpoint

    Example:
      build_url("repos", "org", "repo", "environments", "prod")

    Result:
      https://api.github.com/repos/org/repo/environments/prod
    """
    base = get_api_url()
    path = "/".join(segment.strip("/") for segment in segments)
    return f"{base}/{path}"


def fetch_user() -> str:
    headers = get_headers()
    url = build_url("user")
    response = request_with_handling("GET", url, headers=headers)
    if response:
        data = response.json()
        return data.get("login")
    return None


def get_repository(name: str, org: str | None = None, output_format: str = "table"):
    owner = org if org else fetch_user()
    headers = get_headers()
    url = build_url("repos", owner, name)

    response = request_with_handling(
        "GET",
        url,
        headers=headers,
        error_msg={
            401: "Unauthorized access. Please check your token or credentials.",
            404: "The requested repository does not exist.",
        },
    )

    if not response:
        return None

    return format_repo_get(response.json(), output_format)


def list_repositories(
    per_page: int,
    page: int,
    property: str,
    role: str,
    output_format: str,
    fetch_all: bool = False,
):
    headers = get_headers()
    url = build_url("user", "repos")
    start_page = 1 if fetch_all else page
    params = {"per_page": per_page, "page": start_page, "sort": property}
    if role:
        params["type"] = role

    if not fetch_all:
        response = request_with_handling(
            "GET",
            url,
            params=params,
            headers=headers,
            error_msg={
                401: "Unauthorized access. Please check your token or credentials."
            },
        )
        if not response:
            return None
        return format_repo_list(response.json(), output_format)

    repos = []
    next_url = url
    next_params = params

    while next_url:
        response = request_with_handling(
            "GET",
            next_url,
            params=next_params,
            headers=headers,
            error_msg={
                401: "Unauthorized access. Please check your token or credentials."
            },
        )
        if not response:
            return None

        repos.extend(response.json())
        next_url = response.links.get("next", {}).get("url")
        next_params = None

    return format_repo_list(repos, output_format)


def _parse_template_ref(template: str) -> tuple[str, str] | None:
    """Parse OWNER/REPO template reference. Returns None if invalid."""
    if not template or "/" not in template:
        return None
    template_owner, template_repo = template.split("/", 1)
    if not template_owner or not template_repo or "/" in template_repo:
        return None
    return template_owner, template_repo


def create_repository(
    name: str,
    visibility: str,
    org: str | None = None,
    empty: bool = False,
    template: str | None = None,
    include_all_branches: bool = False,
):
    if template and empty:
        rich_output(
            "Cannot use --template together with --empty.",
            format_str="bold red",
        )
        return None

    if include_all_branches and not template:
        rich_output(
            "--include-all-branches requires --template.",
            format_str="bold red",
        )
        return None

    if template:
        return _create_repository_from_template(
            name,
            visibility,
            org=org,
            template=template,
            include_all_branches=include_all_branches,
        )

    payload = {
        "name": name,
        "visibility": visibility,
        "auto_init": True,
    }

    if visibility == "private":
        payload["private"] = True

    if empty:
        payload["auto_init"] = False

    owner = org if org else fetch_user()
    headers = get_headers()
    url = build_url("orgs", owner, "repos") if org else build_url("user", "repos")

    return request_with_handling(
        "POST",
        url,
        headers=headers,
        json=payload,
        success_msg=f"Repository successfully created in {owner}/{name}.",
        error_msg={
            401: "Unauthorized access. Please check your token or credentials.",
            422: "Repository name already exists on this account or organization.",
        },
    )


def _create_repository_from_template(
    name: str,
    visibility: str,
    *,
    org: str | None = None,
    template: str,
    include_all_branches: bool = False,
):
    if visibility == "internal":
        rich_output(
            "Template create does not support --internal; use --public or --private.",
            format_str="bold red",
        )
        return None

    parsed = _parse_template_ref(template)
    if not parsed:
        rich_output(
            "--template must be in OWNER/REPO format.",
            format_str="bold red",
        )
        return None

    template_owner, template_repo = parsed
    owner = org if org else fetch_user()
    if not owner:
        return None

    payload = {
        "name": name,
        "owner": owner,
        "private": visibility == "private",
        "include_all_branches": include_all_branches,
    }

    headers = get_headers()
    url = build_url("repos", template_owner, template_repo, "generate")

    return request_with_handling(
        "POST",
        url,
        headers=headers,
        json=payload,
        success_msg=(
            f"Repository successfully created in {owner}/{name} "
            f"from template {template_owner}/{template_repo}."
        ),
        error_msg={
            401: "Unauthorized access. Please check your token or credentials.",
            404: "Template repository not found or is not marked as a template.",
            422: "Repository name already exists or template generate failed.",
        },
    )


def update_repository(
    name: str,
    org: str | None = None,
    *,
    new_name: str | None = None,
    description: str | None = None,
    homepage: str | None = None,
    visibility: str | None = None,
    default_branch: str | None = None,
    archived: bool | None = None,
    is_template: bool | None = None,
):
    payload = {}
    if new_name is not None:
        payload["name"] = new_name
    if description is not None:
        payload["description"] = description
    if homepage is not None:
        payload["homepage"] = homepage
    if visibility is not None:
        payload["visibility"] = visibility
        if visibility == "private":
            payload["private"] = True
        elif visibility == "public":
            payload["private"] = False
    if default_branch is not None:
        payload["default_branch"] = default_branch
    if archived is not None:
        payload["archived"] = archived
    if is_template is not None:
        payload["is_template"] = is_template

    if not payload:
        rich_output(
            "No updates specified. Pass at least one option to change.",
            format_str="bold red",
        )
        return None

    owner = org if org else fetch_user()
    if not owner:
        return None

    headers = get_headers()
    url = build_url("repos", owner, name)
    result_name = new_name if new_name is not None else name

    return request_with_handling(
        "PATCH",
        url,
        headers=headers,
        json=payload,
        success_msg=f"Repository successfully updated in {owner}/{result_name}.",
        error_msg={
            401: "Unauthorized access. Please check your token or credentials.",
            404: "The requested repository does not exist.",
            422: "Invalid repository update request.",
        },
    )


def delete_repository(name: str, org: str | None = None):
    owner = org if org else fetch_user()
    headers = get_headers()
    url = build_url("repos", owner, name)

    return request_with_handling(
        "DELETE",
        url,
        headers=headers,
        success_msg=f"Repository successfully deleted in {owner}/{name}.",
        error_msg={
            403: "The authenticated user does not have sufficient permissions to delete this repository.",
            404: "The requested repository does not exist.",
        },
    )


def dependabot_security(name: str, enabled: bool, org: str | None = None):
    is_enabled = bool(enabled)

    owner = org if org else fetch_user()
    headers = get_headers()
    url = build_url("repos", owner, name)
    security_urls = ["vulnerability-alerts", "automated-security-fixes"]

    if is_enabled:
        for endpoint in security_urls:
            full_url = f"{url}/{endpoint}"
            request_with_handling(
                "PUT",
                url=full_url,
                headers=headers,
                success_msg=f"Enabled {endpoint}",
                error_msg={
                    401: "Unauthorized. Please check your credentials.",
                },
            )
    else:
        full_url = f"{url}/{security_urls[0]}"
        request_with_handling(
            "DELETE",
            url=full_url,
            headers=headers,
            success_msg=f"Dependabot has been disabled on repository {owner}/{name}.",
            error_msg={401: "Unauthorized. Please check your credentials."},
        )


def deployment_environment(name: str, env: str, org: str | None = None):
    owner = org if org else fetch_user()
    headers = get_headers()
    url = build_url("repos", owner, name, "environments", env)

    return request_with_handling(
        "PUT",
        url,
        headers=headers,
        success_msg=f"Environment {env} has been created successfully in {owner}/{name}.",
        error_msg={422: f"Failed to create repository environment {owner}/{name}."},
    )
