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
                - load configuration file
                - apply environment variables
                - apply cli args
                - get user input where inputs are missing
                - validate state to provide good user feedback
                - load any cache
        """
        super().__init__()
