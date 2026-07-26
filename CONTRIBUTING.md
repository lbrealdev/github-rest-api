# Contributing

Thanks for helping improve `github-rest-cli`. This guide covers local development, configuration, and quality tooling.

## Prerequisites

- Python 3.11.5+
- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just) (optional, wraps common tasks)
- [Ruff](https://docs.astral.sh/ruff/)
- [pre-commit](https://pre-commit.com/) (optional)

## Setup

Clone the repository, sync dependencies, and activate the virtualenv:

```shell
git clone https://github.com/lbrealdev/github-rest-cli.git
cd github-rest-cli
uv sync
source .venv/bin/activate
```

Install pre-commit hooks and Ruff (via just, if available):

```shell
just setup-pre-commit
just setup-ruff
```

Or install them yourself:

```shell
pre-commit install
uv tool install ruff
```

List installed packages:

```shell
uv pip list
```

## Authentication for local runs

See [docs/authentication.md](docs/authentication.md) for PAT scopes and how to provide the token (`GITHUB_AUTH_TOKEN` or `.secrets.toml`).

Run the CLI entrypoint:

```shell
github-rest-cli --version
github-rest-cli --help
```

You can also profile a command:

```shell
just profile --help
# or with arguments, e.g.:
just profile repo list --format json
```

## Configuration

See [docs/configuration.md](docs/configuration.md) for environment variables, optional settings files, and Dynaconf tooling (`just dl` / `just dv`).

CLI usage for end users: [docs/cli.md](docs/cli.md).

## Lint and format

```shell
just lint
just fmt
```

Equivalent:

```shell
ruff check .
ruff format .
```

## Tests

```shell
just test
# equivalent: pytest -v
```

## Build and publish (maintainers)

Local dry-run:

```shell
just build-local
just publish-local   # requires PYPI_TOKEN
```

Clean the uv cache:

```shell
just cache
```

### Release process

Publishing to PyPI is triggered by creating a GitHub Release. The workflow is [`.github/workflows/release.yml`](.github/workflows/release.yml) (`uv build` + `uv publish` with Trusted Publishing).

1. Ensure `main` is green (CI) and docs are up to date ([CLI guide](docs/cli.md), [configuration](docs/configuration.md)).
2. Agree the SemVer bump (breaking CLI changes usually mean a major or an intentional minor while still Beta).
3. Update `version` in [`pyproject.toml`](pyproject.toml).
4. Open a PR for the version bump, merge to `main`.
5. Create a GitHub Release for the new tag (for example `v2.0.0`) whose target is the merge commit on `main`. Put the release notes in the GitHub Release description (drawn from merged PRs as needed).
6. Confirm the **Python Publish Release** workflow succeeds on [PyPI](https://pypi.org/project/github-rest-cli/).

Do not tag a release until the version in `pyproject.toml` matches the tag.

## Pull requests

1. Create a branch from `main`
2. Keep changes focused
3. Run lint and tests before opening a PR
4. Link related issues (for example, `Fixes #72`)
