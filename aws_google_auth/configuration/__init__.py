#!/usr/bin/env python3

__strict__ = True

from validator import Validator


class Configuration(Validator):
    """
        Configuration class.

        Order of precedence:
            - command-line arguments, which overrides...
            - environment variables, which overrides...
            - configuration file, which overrides...
            - hard-coded defaults in Configuration class.
    """

    def __init__(self):
        """
            class constructor.
                - set defaults
        """
        super().__init__()
