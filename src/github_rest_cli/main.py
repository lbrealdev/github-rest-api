import logging
from importlib.metadata import version

from github_rest_cli.parser import build_parser

__version__ = version("github-rest-cli")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def cli():
    parser = build_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
