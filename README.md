# github-rest-cli

[![PyPI](https://img.shields.io/pypi/v/github-rest-cli.svg)](https://pypi.org/project/github-rest-cli/)
[![Python CI](https://github.com/lbrealdev/github-rest-cli/actions/workflows/python-ci.yml/badge.svg)](https://github.com/lbrealdev/github-rest-cli/actions/workflows/python-ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Python CLI for common [GitHub REST API](https://docs.github.com/en/rest) operations—list and inspect repositories, create, update, or delete them, manage Dependabot security settings, and create deployment environments.

## Installation

With `pip`:

```shell
pip install github-rest-cli
```

With `uv`:

```shell
uv pip install github-rest-cli
```

Requires Python 3.11.5 or newer.

## Authentication

See [Authentication](docs/authentication.md) for PAT scopes and how to set `GITHUB_AUTH_TOKEN` (or `.secrets.toml`).

For API URL overrides, settings files, and Dynaconf environments, see [Configuration](docs/configuration.md).

## Quick start

```shell
github-rest-cli --version
github-rest-cli --help
```

```shell
github-rest-cli repo list
github-rest-cli repo get --name my-repo
github-rest-cli repo create --name my-new-repo --private
github-rest-cli repo create --name my-app --template owner/template-repo
github-rest-cli repo update --name my-repo --description "Updated"
github-rest-cli repo update --name my-repo --new-name renamed-repo
github-rest-cli repo update --name my-repo --as-template
```

## Commands

Full command reference: [CLI guide](docs/cli.md).

```shell
github-rest-cli repo --help
github-rest-cli dependabot --help
github-rest-cli environment --help
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for local development, testing, linting, and Dynaconf tooling.

## Links

- [PyPI](https://pypi.org/project/github-rest-cli/)
- [Source](https://github.com/lbrealdev/github-rest-cli)
- [Issues](https://github.com/lbrealdev/github-rest-cli/issues)
- [License](LICENSE)
