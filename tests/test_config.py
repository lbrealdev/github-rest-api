import inspect

from github_rest_cli import api
from github_rest_cli import config as config_module
from github_rest_cli.config import DEFAULT_API_URL, settings
from github_rest_cli.globals import get_api_url


def test_settings_files_are_basenames():
    source = inspect.getsource(config_module)
    assert 'settings_files=["settings.toml", ".secrets.toml"]' in source
    assert "../" not in source


def test_get_api_url_default():
    url = get_api_url()
    assert url == DEFAULT_API_URL.rstrip("/")
    assert not url.endswith("/")


def test_build_url_uses_default_api_url():
    assert api.build_url("user") == f"{DEFAULT_API_URL}/user"
    assert api.build_url("repos", "owner", "repo") == (
        f"{DEFAULT_API_URL}/repos/owner/repo"
    )


def test_build_url_uses_custom_api_url(mocker):
    mocker.patch(
        "github_rest_cli.api.get_api_url",
        return_value="https://github.example.com/api/v3",
    )

    assert api.build_url("user") == "https://github.example.com/api/v3/user"


def test_get_api_url_from_settings():
    original = settings.get("API_URL", DEFAULT_API_URL)
    try:
        settings.set("API_URL", "https://github.example.com/api/v3/")
        assert get_api_url() == "https://github.example.com/api/v3"
    finally:
        settings.set("API_URL", original)
