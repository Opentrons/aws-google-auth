#!/usr/bin/env python3

__strict__ = True

import sys
from aws_google_auth.cli import cli


def main():
    cli_args = sys.argv[1:]
    cli(cli_args)


if __name__ == '__main__':
    main()
