#!/usr/bin/env python3

__strict__ = True

from sys import version_info
from logging import critical
from sys import exit


def exit_if_unsupported_python():
    if version_info.major == 2 and version_info.minor < 7:
        critical("%s requires Python 2.7 or higher. Please consider "
                 "upgrading. Support for Python 2.6 and lower was "
                 "dropped because this tool's dependencies dropped "
                 "support.", __name__)

        critical(f"For debugging, it appears you're running: {version_info}")

        critical("For more information, see: "
                 "https://github.com/cevoaustralia/aws-google-auth/"
                 "issues/41")

        exit(1)
