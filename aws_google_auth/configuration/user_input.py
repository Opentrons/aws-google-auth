#!/usr/bin/env python3

__strict__ = True

from getpass import getpass
from typing import Optional

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

    @staticmethod
    def select_role(roles: dict,
                    aliases: list = None,
                    account: Optional[str] = None) -> str:
        """
            Select role ARN from a list of known ARNs.

            :param roles: dict (dictionary of iam roles)
            :param aliases: list
            :param account: str
            :return:
            :return: str
        """
        if account:
            filtered_roles = {role: principal for role, principal in
                              roles.items() if (account in role)}
        else:
            filtered_roles = roles

        if aliases:
            enriched_roles = {}
            for role, principal in filtered_roles.items():
                enriched_roles[role] = [
                    aliases[role.split(':')[4]],
                    role.split('role/')[1],
                    principal
                ]
            enriched_roles = OrderedDict(sorted(enriched_roles.items(),
                                                key=lambda t: (
                                                    t[1][0], t[1][1])))

            ordered_roles = OrderedDict()
            for role, role_property in enriched_roles.items():
                ordered_roles[role] = role_property[2]

            enriched_roles_tab = []
            for i, (role, role_property) in enumerate(
                    enriched_roles.items()):
                enriched_roles_tab.append(
                    [i + 1, role_property[0], role_property[1]])

            while True:
                print(tabulate(enriched_roles_tab,
                               headers=['No', 'AWS account', 'Role'], ))
                prompt = 'Type the number (1 - {:d}) of the role to assume: '.format(
                    len(enriched_roles))
                choice = Util.get_input(prompt)

                try:
                    return list(ordered_roles.items())[int(choice) - 1]
                except (IndexError, ValueError):
                    print("Invalid choice, try again.")
        else:
            while True:
                for i, role in enumerate(filtered_roles):
                    print("[{:>3d}] {}".format(i + 1, role))

                prompt = 'Type the number (1 - {:d}) of the role to assume: '.format(
                    len(filtered_roles))
                choice = Util.get_input(prompt)

                try:
                    return list(filtered_roles.items())[int(choice) - 1]
                except (IndexError, ValueError):
                    print("Invalid choice, try again.")
