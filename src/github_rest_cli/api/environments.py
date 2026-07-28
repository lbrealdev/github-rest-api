from github_rest_cli.api import base
from github_rest_cli.utils import format_environment_get, format_environment_list


def deployment_environment(name: str, env: str, org: str | None = None):
    owner = org if org else base.fetch_user()
    headers = base.get_headers()
    url = base.build_url("repos", owner, name, "environments", env)

    return base.request_with_handling(
        "PUT",
        url,
        headers=headers,
        success_msg=f"Environment {env} has been created successfully in {owner}/{name}.",
        error_msg={422: f"Failed to create repository environment {owner}/{name}."},
    )


def list_environments(
    name: str,
    org: str | None = None,
    output_format: str = "table",
    per_page: int = 20,
    page: int = 1,
    fetch_all: bool = False,
):
    owner = org if org else base.fetch_user()
    headers = base.get_headers()
    url = base.build_url("repos", owner, name, "environments")
    start_page = 1 if fetch_all else page
    params = {"per_page": per_page, "page": start_page}
    error_msg = {
        401: "Unauthorized access. Please check your token or credentials.",
        404: "The requested repository does not exist.",
    }

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
        return format_environment_list(response.json(), output_format)

    environments = []
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

        payload = response.json()
        environments.extend(payload.get("environments") or [])
        next_url = response.links.get("next", {}).get("url")
        next_params = None

    return format_environment_list(
        {"total_count": len(environments), "environments": environments},
        output_format,
    )


def get_environment(
    name: str, env: str, org: str | None = None, output_format: str = "table"
):
    owner = org if org else base.fetch_user()
    headers = base.get_headers()
    url = base.build_url("repos", owner, name, "environments", env)

    response = base.request_with_handling(
        "GET",
        url,
        headers=headers,
        error_msg={
            401: "Unauthorized access. Please check your token or credentials.",
            404: f"The environment {env} does not exist in {owner}/{name}.",
        },
    )

    if not response:
        return None

    return format_environment_get(response.json(), output_format)


def delete_environment(name: str, env: str, org: str | None = None):
    owner = org if org else base.fetch_user()
    headers = base.get_headers()
    url = base.build_url("repos", owner, name, "environments", env)

    return base.request_with_handling(
        "DELETE",
        url,
        headers=headers,
        success_msg=f"Environment {env} has been deleted successfully in {owner}/{name}.",
        error_msg={
            401: "Unauthorized access. Please check your token or credentials.",
            404: f"The environment {env} does not exist in {owner}/{name}.",
        },
    )
