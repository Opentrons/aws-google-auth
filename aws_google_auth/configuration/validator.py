#!/usr/bin/env python3

__strict__ = True

from .cli_args import CommandLineArgs


class Validator(CommandLineArgs):
    """
        Validate configuration and provide users guidance when
        things are wrong.
    """

    def __init__(self):
        """
            class constructor.
                - keep things sane by validating all config values.
                - If an input is invalid, prompt the user for the
                  information if possible or throw an exception.
        """
        super().__init__()
        try:
            self.expect_int("_max_duration", min=0, max=65535)
            self.expect_int("_min_duration", min=0, max=self._max_duration - 1)
            self.expect_int("duration", min=self._min_duration,
                            max=self._max_duration)

            boolean_attrs = [
                "ask_role", "keyring", "auto_duration",
                "u2f_disabled", "quiet"]
            for v in boolean_attrs:
                self.expect_bool(v)

            string_attrs = [
                "profile", "region", "idp_id", "sp_id",
                "username", "password", "account"]
            for v in string_attrs:
                self.expect_str(v)

            self.expect_str("role_arn", none_allowed=True)

            arn_prefix = ["arn:aws:iam::", "arn:aws-us-gov:iam::"]
            assert (arn_prefix[0] in self.role_arn) or \
                   (arn_prefix[1] in self.role_arn), "Expected role_arn to " \
                                                     "contain one of " \
                                                     f"{arn_prefix}" \
                                                     f"Got '{self.role_arn}'."
        except AssertionError as e:
            print("---Invalid input error---\n\n"
                  "After loading the configuration file, environment "
                  "variables, and parsing any command-line arguments, an "
                  "invalid parameter was discovered.\n\n"
                  f"Error: {e}\n\n")

    def expect_attr(self, n: str) -> any:
        """
            Perform a check to ensure we have an expected attribute.
            param n: str
            return: any
        """
        assert hasattr(self, n), f"expected attribute {n} not found."
        return getattr(self, n)

    def expect_bool(self, n: str) -> None:
        """
            Perform a type check on boolean attributes of self.
            param n: string (object name)
        """
        o = self.expect_attr(n)
        assert o.__class__ is bool, f"Expected {n} to be boolean. " \
                                    f"Got {o.__class__}"

    def expect_int(self, n: str, min: int = None, max: int = None) -> None:
        """
             Perform a type check on int attributes of self.
            :param n: string (object name)
            :param min: minimum value or none (disables value check)
            :param max: maximum value or none (disables value check)
         """
        o = self.expect_attr(n)
        assert o.__class__ is int, f"Expected {n} to be int. " \
                                   f"Got {o.__class__}"
        if min is not None:
            assert min <= o, f"Bound check fail. {n} less than {min}"
        if max is not None:
            assert max >= o, f"Bound check fail. {n} greater than {max}"

    def expect_str(self, n: str, none_allowed: bool) -> None:
        """
             Perform a type check on int attributes of self.
             :param n: string (object name)
             :param none_allowed: bool (allows None value)
         """
        o = self.expect_attr(n)

        if none_allowed and o is None:
            return
        assert o.__class__ is str, f"Expected {n} to be int. " \
                                   f"Got {o.__class__}"
