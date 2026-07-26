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


def rich_output(message: str, format_str: str = "bold green"):
    return rprint(f"[{format_str}]{message}[/{format_str}]")
