from argparse import Namespace

from github_rest_cli.api import dependabot_security


def run_dependabot(args: Namespace) -> None:
    dependabot_security(args.name, args.control, args.org)
