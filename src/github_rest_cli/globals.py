import logging

from dynaconf.base import ValidationError

from github_rest_cli.config import AUTH_TOKEN_VALIDATOR, DEFAULT_API_URL, settings

logger = logging.getLogger(__name__)


def get_api_url() -> str:
    return settings.get("API_URL", DEFAULT_API_URL).rstrip("/")


def get_headers():
    try:
        AUTH_TOKEN_VALIDATOR.validate(settings)
    except ValidationError as e:
        logger.error(str(e))
        raise SystemExit(1)

    return {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"token {settings.AUTH_TOKEN}",
    }
