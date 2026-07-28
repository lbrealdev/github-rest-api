from github_rest_cli.api import base


def dependabot_security(name: str, enabled: bool, org: str | None = None):
    is_enabled = bool(enabled)

    owner = org if org else base.fetch_user()
    headers = base.get_headers()
    url = base.build_url("repos", owner, name)
    security_urls = ["vulnerability-alerts", "automated-security-fixes"]

    if is_enabled:
        for endpoint in security_urls:
            full_url = f"{url}/{endpoint}"
            base.request_with_handling(
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
        base.request_with_handling(
            "DELETE",
            url=full_url,
            headers=headers,
            success_msg=f"Dependabot has been disabled on repository {owner}/{name}.",
            error_msg={401: "Unauthorized. Please check your credentials."},
        )
