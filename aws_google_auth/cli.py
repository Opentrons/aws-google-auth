#!/usr/bin/env python3

__strict__ = True

from sys import exit
from logging import exception
from parse_args import parse_args
from process_auth import process_auth
from resolve_config import resolve_config
from google import ExpectedGoogleException
from supported_python import exit_if_unsupported_python


def cli(cli_args: list) -> None:
    """
        Process command-line arguments and execute
        the program payload.

        param cli_args: list
        return: None
    """
    try:
        exit_if_unsupported_python()
        args = parse_args(args=cli_args)
        config = resolve_config(args)
        process_auth(args, config)

    except ExpectedGoogleException as ex:
        print(ex)
        exit(1)

    except KeyboardInterrupt:
        pass

    except Exception as ex:
        exception(ex)
