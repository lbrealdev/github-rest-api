# github-rest-cli

[![PyPI](https://img.shields.io/pypi/v/github-rest-cli.svg)](https://pypi.org/project/github-rest-cli/)
[![Python CI](https://github.com/lbrealdev/github-rest-cli/actions/workflows/python-ci.yml/badge.svg)](https://github.com/lbrealdev/github-rest-cli/actions/workflows/python-ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Python CLI for common [GitHub REST API](https://docs.github.com/en/rest) operations: list and inspect repositories for a user or an organization, create, update, or delete them, manage Dependabot security settings, and manage deployment environments.

[Features](#features) · [Installation](#installation) · [Authentication](#authentication) · [Quick start](#quick-start) · [Usage](#usage) · [Documentation](#documentation)

## Features

- Manage repositories for the authenticated user or an organization: get, list, create, update, delete.
- Create repositories from templates, with optional inclusion of all branches.
- Enable or disable Dependabot security updates.
- Create, list, inspect, and delete deployment environments.
- Table or JSON output (`--format table|json`) on all read commands.
- Pagination with `--per-page` and `--page`, full traversal with `--all`, sorting with `--sort` on `repo list`.

## Installation

With `pip`:

```shell
pip install github-rest-cli
```

With `uv`:

```shell
uv pip install github-rest-cli
```

Or install it as a uv tool:

```shell
uv tool install github-rest-cli
```

Requires Python 3.11.5 or newer.

## Authentication

The CLI authenticates with a GitHub personal access token. The quickest setup:

```shell
export GITHUB_AUTH_TOKEN="<github-auth-token>"
```

> [!NOTE]
> A classic token with the `repo` scope covers most operations. Fine-grained tokens need repository access with Contents, Administration, Environments, and Dependabot permissions as needed. See [Authentication](docs/authentication.md) for the full scope table and the `.secrets.toml` alternative.

For API URL overrides, settings files, and Dynaconf environments, see [Configuration](docs/configuration.md).

## Quick start

```shell
github-rest-cli repo list
github-rest-cli repo get --name my-repo
github-rest-cli repo create --name my-new-repo --private
github-rest-cli dependabot enable --name my-repo
github-rest-cli environment list --name my-repo
```

## Usage

Commands are nested: `github-rest-cli <command> <subcommand> [options]`. Every level supports `--help`.

| Group | Subcommands | Purpose |
| --- | --- | --- |
| `repo` | `get`, `list`, `create`, `update`, `delete` | Manage repositories |
| `dependabot` | `enable`, `disable` | Manage Dependabot security updates |
| `environment` | `create`, `list`, `get`, `delete` | Manage deployment environments |

```shell
github-rest-cli repo list --org my-org --all --format json
github-rest-cli repo create --name my-app --template owner/template-repo --private
github-rest-cli repo update --name my-repo --description "Updated description"
github-rest-cli repo delete --name my-repo
```

> [!WARNING]
> `repo delete` and `environment delete` are destructive. Both ask for confirmation; pass `--yes` to skip the prompt.

```shell
github-rest-cli dependabot enable --name my-repo
github-rest-cli dependabot disable --name my-repo
```

```shell
github-rest-cli environment create --name my-repo --env production
github-rest-cli environment get --name my-repo --env production
github-rest-cli environment delete --name my-repo --env staging --yes
```

The full flag reference, including pagination, sorting, and visibility rules, is in the [CLI guide](docs/cli.md).

## Output formats

Read commands (`repo get`, `repo list`, `environment get`, `environment list`) accept `--format table` (default) or `--format json`.

Example output of `repo list` in table mode:

```text
+-----------------------------------------------------------------------------+
|                             GitHub Repositories                             |
+-----------+-----------+----------------------------------------+------------+
| NAME      | OWNER     | URL                                    | VISIBILITY |
+-----------+-----------+----------------------------------------+------------+
| test-repo | test-user | https://github.com/test-user/test-repo | public     |
| dotfiles  | test-user | https://github.com/test-user/dotfiles  | private    |
+-----------+-----------+----------------------------------------+------------+
```

JSON mode returns the same summary fields as `{"repositories": [...]}` for `repo list`, and full raw API payloads for `get` commands.

## Documentation

- [CLI guide](docs/cli.md): full command and flag reference
- [Authentication](docs/authentication.md): token creation and scopes
- [Configuration](docs/configuration.md): environment variables, settings files, Dynaconf
- [Contributing](CONTRIBUTING.md): local development, testing, linting

## Links

- [PyPI](https://pypi.org/project/github-rest-cli/)
- [Source](https://github.com/lbrealdev/github-rest-cli)
- [Issues](https://github.com/lbrealdev/github-rest-cli/issues)
- [License](LICENSE)
