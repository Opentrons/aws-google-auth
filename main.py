#!/usr/bin/env python3

__strict__ = True

from sys import argv
from aws_google_auth.cli import cli


def main():
    cli(argv[1:])


if __name__ == '__main__':
    main()
