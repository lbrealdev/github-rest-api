from github_rest_cli.api import base
from github_rest_cli.utils import format_repo_get, format_repo_list, rich_output


def get_repository(name: str, org: str | None = None, output_format: str = "table"):
    owner = org if org else base.fetch_user()
    headers = base.get_headers()
    url = base.build_url("repos", owner, name)

    response = base.request_with_handling(
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
    sort: str,
    role: str,
    output_format: str,
    fetch_all: bool = False,
    org: str | None = None,
):
    headers = base.get_headers()
    url = (
        base.build_url("orgs", org, "repos") if org else base.build_url("user", "repos")
    )
    start_page = 1 if fetch_all else page
    params = {"per_page": per_page, "page": start_page, "sort": sort}
    if role:
        params["type"] = role

    error_msg = {401: "Unauthorized access. Please check your token or credentials."}
    if org:
        error_msg[404] = "The requested organization does not exist."

    if not fetch_all:
        response = base.request_with_handling(
            "GET",
            url,
            params=params,
            headers=headers,
            error_msg=error_msg,
        )
        if not response:
            return None
        return format_repo_list(response.json(), output_format)

    repos = []
    next_url = url
    next_params = params

    while next_url:
        response = base.request_with_handling(
            "GET",
            next_url,
            params=next_params,
            headers=headers,
            error_msg=error_msg,
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

    owner = org if org else base.fetch_user()
    headers = base.get_headers()
    url = (
        base.build_url("orgs", owner, "repos")
        if org
        else base.build_url("user", "repos")
    )

    return base.request_with_handling(
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
    owner = org if org else base.fetch_user()
    if not owner:
        return None

    payload = {
        "name": name,
        "owner": owner,
        "private": visibility == "private",
        "include_all_branches": include_all_branches,
    }

    headers = base.get_headers()
    url = base.build_url("repos", template_owner, template_repo, "generate")

    return base.request_with_handling(
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

    owner = org if org else base.fetch_user()
    if not owner:
        return None

    headers = base.get_headers()
    url = base.build_url("repos", owner, name)
    result_name = new_name if new_name is not None else name

    return base.request_with_handling(
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
    owner = org if org else base.fetch_user()
    headers = base.get_headers()
    url = base.build_url("repos", owner, name)

    return base.request_with_handling(
        "DELETE",
        url,
        headers=headers,
        success_msg=f"Repository successfully deleted in {owner}/{name}.",
        error_msg={
            403: "The authenticated user does not have sufficient permissions to delete this repository.",
            404: "The requested repository does not exist.",
        },
    )
