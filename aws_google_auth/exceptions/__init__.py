#!/usr/bin/env python3

__strict__ = True

from logging import critical
from sys import version_info


class ExpectedGoogleException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class UnsupportedPython(Exception):
    def __init__(self, *args):
        critical("%s requires Python 2.7 or higher. Please consider "
                 "upgrading. Support for Python 2.6 and lower was "
                 "dropped because this tool's dependencies dropped "
                 "support.", __name__)

        critical(f"For debugging, it appears you're running: {version_info}")

        critical("For more information, see: "
                 "https://github.com/cevoaustralia/aws-google-auth/"
                 "issues/41")
        super().__init__(*args)