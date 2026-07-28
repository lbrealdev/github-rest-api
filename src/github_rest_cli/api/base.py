import requests

from github_rest_cli.globals import get_api_url, get_headers
from github_rest_cli.utils import rich_output


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
