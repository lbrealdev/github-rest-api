"""Main config module"""

from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    # Default environment variables prefix.
    envvar_prefix="GITHUB",
    # Source configuration files.
    settings_files=["../../settings.toml", "../../.secrets.toml"],
    environments=["development", "testing", "production"],
    env_switcher="SET_ENV",
    # The script will not work if the variables
    # defined in the Validator class are not defined.
    validators=[
        Validator("API_URL", must_exist=True, cont="github"),
        
        Validator("AUTH_TOKEN", must_exist=True),
        
        Validator(
            "USER",
            must_exist=True,
            messages={"must_exist_true": "GITHUB_USER is not defined."}
        )
    ],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
