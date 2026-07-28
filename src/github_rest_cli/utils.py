import json

from rich import print as rprint

REPO_SUMMARY_COLUMNS = ["name", "owner", "url", "visibility"]

REPO_DETAIL_FIELDS = [
    "name",
    "full_name",
    "owner",
    "description",
    "visibility",
    "default_branch",
    "language",
    "topics",
    "html_url",
    "created_at",
    "updated_at",
    "pushed_at",
    "fork",
    "archived",
    "disabled",
    "is_template",
]

ENVIRONMENT_SUMMARY_COLUMNS = [
    "name",
    "id",
    "protection_rules",
    "created_at",
    "updated_at",
]

ENVIRONMENT_DETAIL_FIELDS = [
    "name",
    "id",
    "node_id",
    "url",
    "html_url",
    "created_at",
    "updated_at",
    "protection_rules",
    "deployment_branch_policy",
]


def to_json(data) -> str:
    return json.dumps(data, indent=2)


def to_table(rows, *, columns, title):
    from prettytable import PrettyTable

    table = PrettyTable()
    table.title = title
    table.header_style = "upper"
    table.field_names = columns
    table.align = "l"

    for row in rows:
        table.add_row(row)

    return table


def to_key_value_table(pairs, *, title):
    return to_table(pairs, columns=["field", "value"], title=title)


def _stringify(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def project_repo_summary(repo: dict) -> dict:
    return {
        "name": repo.get("name"),
        "owner": repo.get("owner", {}).get("login"),
        "url": repo.get("html_url"),
        "visibility": repo.get("visibility"),
    }


def project_repo_detail(repo: dict) -> list[tuple[str, str]]:
    topics = repo.get("topics") or []
    values = {
        "name": repo.get("name"),
        "full_name": repo.get("full_name"),
        "owner": repo.get("owner", {}).get("login"),
        "description": repo.get("description") or "",
        "visibility": repo.get("visibility"),
        "default_branch": repo.get("default_branch"),
        "language": repo.get("language"),
        "topics": ", ".join(topics),
        "html_url": repo.get("html_url"),
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
        "pushed_at": repo.get("pushed_at"),
        "fork": repo.get("fork"),
        "archived": repo.get("archived"),
        "disabled": repo.get("disabled"),
        "is_template": repo.get("is_template"),
    }
    return [(field, _stringify(values[field])) for field in REPO_DETAIL_FIELDS]


def _describe_protection_rules(rules) -> str:
    return ", ".join(rule.get("type", "") for rule in rules or [])


def _describe_branch_policy(policy) -> str:
    """Summarise the deployment_branch_policy object as its enabled keys."""
    if not policy:
        return ""
    enabled = [
        key
        for key in ("protected_branches", "custom_branch_policies")
        if policy.get(key)
    ]
    return ", ".join(enabled)


def project_environment_summary(environment: dict) -> dict:
    return {
        "name": environment.get("name"),
        "id": environment.get("id"),
        "protection_rules": _describe_protection_rules(
            environment.get("protection_rules")
        ),
        "created_at": environment.get("created_at"),
        "updated_at": environment.get("updated_at"),
    }


def project_environment_detail(environment: dict) -> list[tuple[str, str]]:
    values = {
        "name": environment.get("name"),
        "id": environment.get("id"),
        "node_id": environment.get("node_id"),
        "url": environment.get("url"),
        "html_url": environment.get("html_url"),
        "created_at": environment.get("created_at"),
        "updated_at": environment.get("updated_at"),
        "protection_rules": _describe_protection_rules(
            environment.get("protection_rules")
        ),
        "deployment_branch_policy": _describe_branch_policy(
            environment.get("deployment_branch_policy")
        ),
    }
    return [(field, _stringify(values[field])) for field in ENVIRONMENT_DETAIL_FIELDS]


def format_repo_list(repos, output_format: str = "table"):
    summaries = [project_repo_summary(repo) for repo in repos]

    if output_format == "json":
        return to_json({"repositories": summaries})

    rows = [[s[column] for column in REPO_SUMMARY_COLUMNS] for s in summaries]
    return to_table(rows, columns=REPO_SUMMARY_COLUMNS, title="GitHub Repositories")


def format_repo_get(repo, output_format: str = "table"):
    if output_format == "json":
        return to_json(repo)

    pairs = project_repo_detail(repo)
    return to_key_value_table(pairs, title="GitHub Repository")


def format_environment_list(payload, output_format: str = "table"):
    if output_format == "json":
        return to_json(payload)

    environments = payload.get("environments") or []
    summaries = [project_environment_summary(env) for env in environments]
    rows = [
        [_stringify(s[column]) for column in ENVIRONMENT_SUMMARY_COLUMNS]
        for s in summaries
    ]
    return to_table(
        rows, columns=ENVIRONMENT_SUMMARY_COLUMNS, title="GitHub Environments"
    )


def format_environment_get(environment, output_format: str = "table"):
    if output_format == "json":
        return to_json(environment)

    pairs = project_environment_detail(environment)
    return to_key_value_table(pairs, title="GitHub Environment")


def rich_output(message: str, format_str: str = "bold green"):
    return rprint(f"[{format_str}]{message}[/{format_str}]")
