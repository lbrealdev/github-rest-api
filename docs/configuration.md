# Configuration

`github-rest-cli` uses Dynaconf for settings. Prefer environment variables; optional files are supported for local development.

For creating a GitHub token and required scopes, see [Authentication](authentication.md).

## Environment variables (recommended)

| Variable | Setting | Required | Description |
| --- | --- | --- | --- |
| `GITHUB_AUTH_TOKEN` | `AUTH_TOKEN` | Yes | GitHub personal access token |
| `GITHUB_API_URL` | `API_URL` | No | GitHub REST API base URL (default: `https://api.github.com`) |
| `SET_ENV` | environment switcher | No | Active Dynaconf environment (`development`, `testing`, `production`, …) |

Example:

```shell
export GITHUB_AUTH_TOKEN="<github-auth-token>"
# optional:
export GITHUB_API_URL="https://api.github.com"
```

Dynaconf uses the `GITHUB_` prefix, so `AUTH_TOKEN` in a settings file maps to `GITHUB_AUTH_TOKEN` in the environment. Environment variables override file values.

## Optional settings files

When present in the **current working directory**, Dynaconf loads (in order):

1. `settings.toml` — non-secret defaults
2. `.secrets.toml` — local secrets (gitignored via `.secrets.*`)

An installed package does not ship these files; env vars alone are enough for normal use. Repository clones may include a sample `settings.toml` with `API_URL`.

### Recommended layout

Put non-secret defaults in `settings.toml`:

```toml
# settings.toml
[default]
API_URL = "https://api.github.com"
```

Put credentials in `.secrets.toml` (do **not** commit this file):

```toml
# .secrets.toml
[default]
AUTH_TOKEN = "ghp_your_token_here"
```

Then run from that directory:

```shell
github-rest-cli repo list
```

Optional environment selection:

```shell
export SET_ENV=development
github-rest-cli repo list
```

Matching sections in the files (for example `[development]`) are used when `SET_ENV` is set.

### Security notes

- Prefer `.secrets.toml` or `GITHUB_AUTH_TOKEN` for tokens. Never commit PATs.
- `.secrets.*` is listed in `.gitignore`.
- Files are read from the process **current working directory**, not necessarily the package install location.

## Contributor tooling

List defined parameters:

```shell
just dl
# equivalent: just dynaconf-list
```

Validate parameters:

```shell
just dv
# equivalent: just dynaconf-validate
```

Validation expects `dynaconf_validators.toml` at the project root.

Implementation lives in `src/github_rest_cli/config.py`.

## References

- [Authentication](authentication.md)
- [CLI guide](cli.md)
- [dynaconf/dynaconf](https://github.com/dynaconf/dynaconf)
- [Dynaconf documentation](https://www.dynaconf.com/)
- [Dynaconf API](https://www.dynaconf.com/api/)
