#!/usr/bin/env python3

__strict__ = True

from sys import exit
from sys import version_info
from aws_google_auth.process_auth import process_auth
from aws_google_auth.exceptions import UnsupportedPython
from aws_google_auth.exceptions import ExpectedGoogleException
from aws_google_auth.configuration import Configuration


def check_python_version():
    if version_info.major == 2 and version_info.minor < 7:
        raise UnsupportedPython()


def main():
    """
        Process command-line arguments and execute the program payload.

        param cli_args: list
        return: None
    """
    try:
        check_python_version()
        config = Configuration()
        process_auth(config)

    except UnsupportedPython as ex:
        print(ex)
        exit(3)

    except ExpectedGoogleException as ex:
        print(ex)
        exit(2)

    except KeyboardInterrupt:
        pass

    except Exception as ex:
        print(f"unhandled exception\n{ex}")
        exit(1)


if __name__ == '__main__':
    main()
