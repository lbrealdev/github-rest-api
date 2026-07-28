# CLI guide

Command reference for `github-rest-cli`. The CLI uses nested groups:

```text
github-rest-cli <command> <subcommand> [options]
```

For tokens and PAT scopes, see [Authentication](authentication.md). For settings files and API URL, see [Configuration](configuration.md).

## Global options

```shell
github-rest-cli --help
github-rest-cli --version
```

| Option | Description |
| --- | --- |
| `-h` / `--help` | Show help |
| `-v` / `--version` | Show package version |

## Command groups

| Group | Purpose |
| --- | --- |
| `repo` | Get, list, create, update, and delete repositories |
| `dependabot` | Enable or disable Dependabot security updates |
| `environment` | Create, list, get, and delete deployment environments |

```shell
github-rest-cli repo --help
github-rest-cli dependabot --help
github-rest-cli environment --help
```

## Implemented commands and GitHub APIs

| CLI command | HTTP / path | GitHub docs |
| --- | --- | --- |
| `repo get` | `GET /repos/{owner}/{repo}` | [Get a repository](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#get-a-repository) |
| `repo list` | `GET /user/repos` | [List repositories for the authenticated user](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#list-repositories-for-the-authenticated-user) |
| `repo list --org` | `GET /orgs/{org}/repos` | [List organization repositories](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#list-organization-repositories) |
| `repo create` (user) | `POST /user/repos` | [Create a repository for the authenticated user](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#create-a-repository-for-the-authenticated-user) |
| `repo create` (org) | `POST /orgs/{org}/repos` | [Create an organization repository](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#create-an-organization-repository) |
| `repo create` (template) | `POST /repos/{template_owner}/{template_repo}/generate` | [Create a repository using a template](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#create-a-repository-using-a-template) |
| `repo update` | `PATCH /repos/{owner}/{repo}` | [Update a repository](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#update-a-repository) |
| `repo delete` | `DELETE /repos/{owner}/{repo}` | [Delete a repository](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#delete-a-repository) |
| `dependabot enable` | Dependabot security updates | [Enable Dependabot security updates](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#enable-dependabot-security-updates) |
| `dependabot disable` | Dependabot security updates | [Disable Dependabot security updates](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#disable-dependabot-security-updates) |
| `environment create` | `PUT /repos/{owner}/{repo}/environments/{environment_name}` | [Create or update an environment](https://docs.github.com/en/rest/deployments/environments?apiVersion=2026-03-10#create-or-update-an-environment) |
| `environment list` | `GET /repos/{owner}/{repo}/environments` | [List environments](https://docs.github.com/en/rest/deployments/environments?apiVersion=2026-03-10#list-environments) |
| `environment get` | `GET /repos/{owner}/{repo}/environments/{environment_name}` | [Get an environment](https://docs.github.com/en/rest/deployments/environments?apiVersion=2026-03-10#get-an-environment) |
| `environment delete` | `DELETE /repos/{owner}/{repo}/environments/{environment_name}` | [Delete an environment](https://docs.github.com/en/rest/deployments/environments?apiVersion=2026-03-10#delete-an-environment) |

## `repo`

### `repo get`

Fetch details for one repository.

**API:** `GET /repos/{owner}/{repo}` — [Get a repository](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#get-a-repository)

```shell
github-rest-cli repo get --name my-repo
github-rest-cli repo get --name my-repo --org my-org
github-rest-cli repo get --name my-repo --format json
```

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `-n` / `--name` | Yes | — | Repository name |
| `-o` / `--org` | No | authenticated user | Organization owner |
| `-f` / `--format` | No | `table` | Output format: `table` or `json` |

Table mode shows a key/value detail view (`Field` | `Value`) with curated fields: `name`, `full_name`, `owner`, `description`, `visibility`, `default_branch`, `language`, `topics`, `html_url`, `created_at`, `updated_at`, `pushed_at`, `fork`, `archived`, `disabled`, `is_template`.

JSON mode returns the full raw GitHub repository object from the API.

### `repo list`

List repositories for the authenticated user, or for an organization with `--org`.

**API:**

- Authenticated user: `GET /user/repos` — [List repositories for the authenticated user](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#list-repositories-for-the-authenticated-user)
- Organization (`--org`): `GET /orgs/{org}/repos` — [List organization repositories](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#list-organization-repositories)

`--per-page` and `--page` map to GitHub's `per_page` and `page` query parameters. `--all` follows [Link-header pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api?apiVersion=2026-03-10). All pagination, sorting, and output flags work the same for both endpoints.

```shell
github-rest-cli repo list
github-rest-cli repo list --per-page 50 --sort pushed
github-rest-cli repo list --page 2 --per-page 30
github-rest-cli repo list --all --format json
github-rest-cli repo list --role owner --format json
github-rest-cli repo list --org my-org
github-rest-cli repo list --org my-org --per-page 50 --all --format json
```

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `-o` / `--org` | No | authenticated user | List repositories owned by an organization |
| `--per-page` | No | `20` | Results per page (`per_page`, max 100) |
| `-p` / `--page` | No | `1` | Page number to fetch (ignored with `--all`) |
| `--all` | No | off | Fetch every page by following `Link` headers |
| `-s` / `--sort` | No | `pushed` | Sort field (e.g. `pushed`, `updated`, `created`) |
| `-r` / `--role` | No | unset | Filter by affiliation/role (`type` query parameter) |
| `-f` / `--format` | No | `table` | Output format: `table` or `json` |

`--role` maps to GitHub's `type` parameter, whose accepted values differ per endpoint: `all`, `owner`, `public`, `private`, `member` for the user endpoint, and `all`, `public`, `private`, `forks`, `sources`, `member` for the organization endpoint.

`--format` only changes presentation. Table and JSON use the same repository set and the same summary fields: `name`, `owner`, `url`, `visibility`. With `--all`, that set is the concatenated result of every page.

### `repo create`

Create a repository. Visibility defaults to **public** when none of the visibility flags is passed.

With `--template OWNER/REPO`, the CLI uses the template generate endpoint instead of the normal create APIs. `--template` cannot be combined with `--empty`. Template create supports `--public` / `--private` only (not `--internal`).

**API:**

- User: `POST /user/repos` — [Create a repository for the authenticated user](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#create-a-repository-for-the-authenticated-user)
- Organization: `POST /orgs/{org}/repos` — [Create an organization repository](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#create-an-organization-repository)
- Template: `POST /repos/{template_owner}/{template_repo}/generate` — [Create a repository using a template](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#create-a-repository-using-a-template)

```shell
github-rest-cli repo create --name my-new-repo
github-rest-cli repo create --name my-new-repo --private
github-rest-cli repo create --name my-new-repo --public
github-rest-cli repo create --name my-new-repo --internal
github-rest-cli repo create --name my-new-repo --org my-org
github-rest-cli repo create --name my-new-repo --empty
github-rest-cli repo create --name my-app --template owner/template-repo
github-rest-cli repo create --name my-app --template owner/template-repo --private --include-all-branches
github-rest-cli repo create --name my-app --template owner/template-repo --org my-org
```

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `-n` / `--name` | Yes | — | Repository name |
| `-o` / `--org` | No | authenticated user | Create under an organization |
| `--public` | No | default when omitted | Public repository |
| `--private` | No | — | Private repository |
| `--internal` | No | — | Internal repository (org; not supported with `--template`) |
| `-e` / `--empty` | No | off | Create without an initial commit / README |
| `--template` | No | unset | Template repository as `OWNER/REPO` |
| `--include-all-branches` | No | off | Include all branches from the template (requires `--template`) |

`--public`, `--private`, and `--internal` are mutually exclusive. `--template` and `--empty` cannot be used together.

### `repo update`

Update settings on an existing repository. Pass at least one change option.

**API:** `PATCH /repos/{owner}/{repo}` — [Update a repository](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#update-a-repository)

```shell
github-rest-cli repo update --name my-repo --description "Updated description"
github-rest-cli repo update --name my-repo --new-name renamed-repo
github-rest-cli repo update --name my-repo --private
github-rest-cli repo update --name my-repo --homepage https://example.com --default-branch main
github-rest-cli repo update --name my-repo --org my-org --archived
github-rest-cli repo update --name my-repo --unarchived
github-rest-cli repo update --name my-repo --as-template
github-rest-cli repo update --name my-repo --no-template
```

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `-n` / `--name` | Yes | — | Current repository name |
| `-o` / `--org` | No | authenticated user | Organization owner |
| `--new-name` | No | unset | Rename the repository |
| `--description` | No | unset | Short description |
| `--homepage` | No | unset | Homepage URL |
| `--public` | No | unset | Make the repository public |
| `--private` | No | unset | Make the repository private |
| `--internal` | No | unset | Make the repository internal |
| `--default-branch` | No | unset | Default branch name |
| `--archived` | No | unset | Archive the repository |
| `--unarchived` | No | unset | Unarchive the repository |
| `--as-template` | No | unset | Mark the repository as a template |
| `--no-template` | No | unset | Unmark the repository as a template |

`--public`, `--private`, and `--internal` are mutually exclusive. `--archived` and `--unarchived` are mutually exclusive. `--as-template` and `--no-template` are mutually exclusive.

### `repo delete`

Delete a repository. Prompts for confirmation unless `--yes` is passed.

**API:** `DELETE /repos/{owner}/{repo}` — [Delete a repository](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#delete-a-repository)

```shell
github-rest-cli repo delete --name my-repo
github-rest-cli repo delete --name my-repo --org my-org
github-rest-cli repo delete --name my-repo --yes
```

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `-n` / `--name` | Yes | — | Repository name |
| `-o` / `--org` | No | authenticated user | Organization owner |
| `-y` / `--yes` | No | off | Skip confirmation prompt |

## `dependabot`

### `dependabot enable` / `dependabot disable`

Enable or disable Dependabot security updates for a repository.

**API:**

- Enable — [Enable Dependabot security updates](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#enable-dependabot-security-updates)
- Disable — [Disable Dependabot security updates](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#disable-dependabot-security-updates)

```shell
github-rest-cli dependabot enable --name my-repo
github-rest-cli dependabot disable --name my-repo
github-rest-cli dependabot enable --name my-repo --org my-org
```

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `-n` / `--name` | Yes | — | Repository name |
| `-o` / `--org` | No | authenticated user | Organization owner |

## `environment`

### `environment create`

Create a deployment environment on a repository.

**API:** `PUT /repos/{owner}/{repo}/environments/{environment_name}` — [Create or update an environment](https://docs.github.com/en/rest/deployments/environments?apiVersion=2026-03-10#create-or-update-an-environment)

```shell
github-rest-cli environment create --name my-repo --env production
github-rest-cli environment create --name my-repo --env staging --org my-org
```

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `-n` / `--name` | Yes | — | Repository name |
| `-e` / `--env` | Yes | — | Environment name |
| `-o` / `--org` | No | authenticated user | Organization owner |

### `environment list`

List the deployment environments of a repository.

**API:** `GET /repos/{owner}/{repo}/environments` — [List environments](https://docs.github.com/en/rest/deployments/environments?apiVersion=2026-03-10#list-environments)

```shell
github-rest-cli environment list --name my-repo
github-rest-cli environment list --name my-repo --org my-org
github-rest-cli environment list --name my-repo --per-page 50 --page 2
github-rest-cli environment list --name my-repo --all --format json
github-rest-cli environment list --name my-repo --format json
```

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `-n` / `--name` | Yes | — | Repository name |
| `-o` / `--org` | No | authenticated user | Organization owner |
| `--per-page` | No | `20` | Results per page (`per_page`, max 100) |
| `-p` / `--page` | No | `1` | Page number to fetch (ignored with `--all`) |
| `--all` | No | off | Fetch every page by following `Link` headers |
| `-f` / `--format` | No | `table` | Output format: `table` or `json` |

Table mode shows the summary fields `name`, `id`, `protection_rules`, `created_at`, `updated_at`, where `protection_rules` lists the configured rule types. JSON mode returns the full API payload, including `total_count`.

### `environment get`

Fetch details for one deployment environment.

**API:** `GET /repos/{owner}/{repo}/environments/{environment_name}` — [Get an environment](https://docs.github.com/en/rest/deployments/environments?apiVersion=2026-03-10#get-an-environment)

```shell
github-rest-cli environment get --name my-repo --env production
github-rest-cli environment get --name my-repo --env production --org my-org
github-rest-cli environment get --name my-repo --env production --format json
```

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `-n` / `--name` | Yes | — | Repository name |
| `-e` / `--env` | Yes | — | Environment name |
| `-o` / `--org` | No | authenticated user | Organization owner |
| `-f` / `--format` | No | `table` | Output format: `table` or `json` |

Table mode shows a key/value detail view (`Field` | `Value`) with the fields `name`, `id`, `node_id`, `url`, `html_url`, `created_at`, `updated_at`, `protection_rules`, `deployment_branch_policy`. JSON mode returns the full raw environment object.

### `environment delete`

Delete a deployment environment. Prompts for confirmation unless `--yes` is passed.

**API:** `DELETE /repos/{owner}/{repo}/environments/{environment_name}` — [Delete an environment](https://docs.github.com/en/rest/deployments/environments?apiVersion=2026-03-10#delete-an-environment)

```shell
github-rest-cli environment delete --name my-repo --env production
github-rest-cli environment delete --name my-repo --env production --org my-org
github-rest-cli environment delete --name my-repo --env production --yes
```

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `-n` / `--name` | Yes | — | Repository name |
| `-e` / `--env` | Yes | — | Environment name |
| `-o` / `--org` | No | authenticated user | Organization owner |
| `-y` / `--yes` | No | off | Skip confirmation prompt |

Deleting an environment also deletes any secrets and protection rules attached to it.

## Output format

`repo get`, `repo list`, `environment get`, and `environment list` support:

- `table` (default) — PrettyTable display
- `json` — JSON string suitable for piping or scripting

For `repo get` and `environment get`, table is a curated key/value detail view; JSON is the full API payload.
For `repo list`, table and JSON both use the summary fields `name`, `owner`, `url`, `visibility`.
For `environment list`, table uses summary fields while JSON is the full API payload.

```shell
github-rest-cli repo list --format json
github-rest-cli repo get --name my-repo --format table
github-rest-cli environment list --name my-repo --format json
```
