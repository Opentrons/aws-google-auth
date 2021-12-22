#!/usr/bin/env python3

__strict__ = True

from getpass import getpass
from .cli_args import CommandLineArgs


class UserInput(CommandLineArgs):
    """
        For any missing properties which require user input as an option,
        this class will get the user input.
    """

    def __init__(self):
        """
            class constructor.
                - evaluate select properties.
                - where appropriate solicit user input.
        """
        super().__init__()

    @staticmethod
    def get_int(prompt: str, min: int, max: int) -> int:
        """
            prompt user for an integer within the inclusive bounds of
            min and max where min/max are not None.

            :param prompt: str
            :param min: int|None
            :param max: int|None
            :return: int
        """
        bounds = f"open->" if min is None else bounds = f"{min}->"
        bounds = f"{bounds}open" if max is None else f"{bounds}{max}"
        if (min is not None) and (max is not None) and (min >= max):
            raise Exception(
                f"programming error: "
                f"min ({min}) must be less than max ({max})")
        while True:
            try:
                ans = int(input(f"{prompt} ({bounds}): "))
            except ValueError:
                print(f"Invalid input. Expect int between {bounds}. "
                      "Try again.")
            if (min is not None) and (ans < min):
                print(f"Invalid input.  Answer must be greater than {min}")
            elif (max is not None) and (ans > max):
                print(f"Invalid input.  Answer must be less than {max}")
            else:
                return ans

    @staticmethod
    def get_yes_no(prompt: str) -> bool:
        """
            Prompt user for a yes/no, y/n answer.

            :param prompt: str
            :return: bool
        """
        expected = ["yes", "no", "y", "n"]
        while True:
            ans = input(f"{prompt} (y/n): ").strip().lower()
            if ans in expected:
                return ans[0] == "y"
            else:
                print(f"Invalid input.  Expect {expected}")

    @staticmethod
    def get_str(prompt: str, allow_empty: bool) -> str:
        """
            Prompt user for an arbitrary string input.

            :param prompt: str
            :param allow_empty: bool
            :return: str
        """
        while True:
            ans = input(f"{prompt}: ").strip()
            if not allow_empty and (ans == ""):
                print("input cannot be empty.  Try again.")
                continue
            else:
                return ans

    @staticmethod
    def get_password(prompt: str) -> str:
        """
            Prompt for a password (mask input)

            :param prompt: str
            :return: str
        """
        return getpass(f"{prompt}: ")
