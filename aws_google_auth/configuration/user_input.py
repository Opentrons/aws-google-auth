#!/usr/bin/env python3

__strict__ = True

from collections import OrderedDict
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

        def set_min(inp: int) -> str:
            if min is None:
                return "open"
            else:
                return f"{inp}"

        def set_max(inp: int) -> str:
            if max is None:
                return "open"
            else:
                f"{max}"

        bounds = f"{set_min(min)}->{set_max(max)}"
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
        while True:
            ans = getpass(f"{prompt}: ")
            if ans.strip() == "":
                print("input cannot be empty.  Try again.")
                continue
            else:
                return ans

    @staticmethod
    def filter_roles(roles: dict, acct: str) -> dict:
        """
            return a filtered dictionary of roles
            :param roles: dict
            :param acct: str
            :return: dict
        """
        # r -> role
        # p -> principal
        return roles if acct in [None, ""] else {
            r: p for r, p in roles.items() if (acct in r)
        }

    @staticmethod
    def display_choices(options: dict, exit_option: bool = True) -> (int, int):
        """
            Display menu options.
            :param options: dict
            :param exit_option: bool
            :return: (int, int)
        """

        def print_menu_line(o: int, msg: str):
            print(f"[{o} -> {msg}")

        def print_divider(o: int):
            print("-" * o)

        for n, message in enumerate(options):
            print_menu_line(n, message)

        print_divider(10)

        if exit_option:
            max = (len(options) + 1) if exit_option else len(options)
            print_menu_line(max, "exit this tool")
            print_divider(10)
            return 0, max
        else:
            return 0, len(options)

    def select_choice(self,
                      opts: dict,
                      exit_option: bool = True) -> int:
        """
            Get user input (choice)
            :param opts: list[int] : list of options.
            :param exit_option: bool (do we check for an exit request (q)?)
            :return: str
        """
        while True:
            min, max = self.display_choices(opts, exit_option=exit_option)
            try:
                inp = int(
                    input("Select option {min}...{max} and press enter: "))
                if exit_option and (inp == max):
                    print("terminating (user requested)")
                    exit(0)
                assert inp in range(min, max)
                return inp
            except (ValueError, AssertionError):
                print(f"Invalid option.  Must be {min} - {max}")

    def select_role(self,
                    roles: dict,
                    aliases: list = [],
                    account: str = "") -> str:
        """
            Select role ARN from a list of known ARNs.
            :param roles: dict (dictionary of iam roles)
            :param aliases: list
            :param account: str
            :return: str
        """
        filtered_roles: dict = self.filter_roles(roles, account)

        if aliases in [None, []]:
            choice = self.select_choice(filtered_roles, exit_option=True)
            try:
                return list(filtered_roles.items())[choice - 1]
            except IndexError:
                raise Exception("select_role() programming error")
        else:
            enriched_roles = {}
            for role, principal in filtered_roles.items():
                enriched_roles[role] = [
                    aliases[role.split(':')[4]],
                    role.split('role/')[1],
                    principal
                ]
            enriched_roles = OrderedDict(
                sorted(enriched_roles.items(),
                       key=lambda t: (t[1][0], t[1][1])))

            ordered_roles = OrderedDict()
            for role, role_property in enriched_roles.items():
                ordered_roles[role] = role_property[2]

            enriched_roles_tab = []
            for i, (role, role_property) in enumerate(
                    enriched_roles.items()):
                enriched_roles_tab.append(
                    [i + 1, role_property[0], role_property[1]])

            # enriched_roles_tab headers=['No', 'AWS account', 'Role']
            choice = self.select_choice(enriched_roles_tab, exit_option=True)
            try:
                return list(ordered_roles.items())[choice - 1]
            except IndexError:
                raise Exception("select_role() programming error (enriched)")
