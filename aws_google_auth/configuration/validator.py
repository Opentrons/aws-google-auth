#!/usr/bin/env python3

__strict__ = True

from re import compile
from typing import Callable
from .user_input import UserInput
from .exceptions import TypeCheckException
from .exceptions import StringValidationError
from .exceptions import IntegerMinBoundCheckError
from .exceptions import IntegerMaxBoundCheckError


class Validator(UserInput):
    """
        Validate configuration and provide users guidance when
        things are wrong.  This will prompt users for input where
        appropriate.
    """

    def __init__(self):
        """
            class constructor.
                - keep things sane by validating all config values.
                - If an input is invalid, prompt the user for the
                  information if possible or throw an exception.
        """
        super().__init__()

        # ToDo: verify these regexes work.
        regex_profile = "^[a-zA-Z][a-zA-Z0-9_\\-]*[a-zA-Z0-9]*$"

        regex_regions = "^us-(east|west)-[12]$"

        regex_base64 = "^(?:[A-Za-z0-9+/]{4})*" \
                       "(?:[A-Za-z0-9+/]{2}==" \
                       "|[A-Za-z0-9+/]{3}=)?$"

        regex_username = "^[a-zA-Z]+[_\\-]{0,1}[a-zA-Z0-9]+\\." \
                         "[a-zA-Z]+[-]{0,1}[a-zA-Z0-9]+$"

        regex_password = "".join([
            "^(?:",
            "(?=.*[a-z])",  # Lower-case letter ahead,
            "(?:",  # and
            "(?=.*[A-Z])",  # Upper-case letter, and
            "(?=.*[\\d\\W])",  # Number (\d) or symbol (\W),
            ")|",  # or
            "(?=.*\\W)",  # symbol, and
            "(?=.*[A-Z])",  # an upper-case letter, and
            "(?=.*\\d)",  # a number ahead.
            ")."
            "{12,}$"])  # password is at least 12 characters.

        # https://docs.aws.amazon.com/organizations/latest/APIReference/
        # API_Account.html
        regex_account = "^[0-9]{12}$"

        # see https://docs.aws.amazon.com/IAM/latest/UserGuide/
        # reference_identifiers.html
        regex_role_arn = "".join([
            "^arn:",
            "aws(-us-gov){0,1}:",
            "iam:(us-(east|west)-[12]){0,1}:",
            "([0-9]{12}){0,1}:",
            "role(\\/.*){0,1}$"
        ])

        self.expect_int("_max_duration",
                        min=0, max=1048576, input_method=self.get_int)

        self.expect_int("_min_duration",
                        min=0,
                        max=self._max_duration - 1,
                        input_method=self.get_int)

        self.expect_int("duration",
                        min=self._min_duration,
                        max=self._max_duration,
                        input_method=self.get_int)

        self.expect_bool("ask_role",
                         input_method=self.get_yes_no)

        self.expect_bool("keyring",
                         input_method=self.get_yes_no)

        self.expect_bool("auto_duration",
                         input_method=self.get_yes_no)

        # self.expect_bool("u2f_disabled",
        #                  input_method=self.get_yes_no)

        self.expect_bool("quiet",
                         input_method=self.get_yes_no)

        self.expect_str(
            n="profile",
            allow_empty=False,
            allow_none=False,
            input_method=self.get_str,
            validation=regex_profile)
        self.expect_str(
            n="region",
            allow_empty=False,
            allow_none=False,
            input_method=self.get_str,
            validation=regex_regions)
        self.expect_str(
            n="idp_id",
            allow_empty=False,
            allow_none=False,
            input_method=self.get_str,
            validation=regex_base64)
        self.expect_str(
            n="sp_id",
            allow_empty=False,
            allow_none=False,
            input_method=self.get_str,
            validation=regex_base64)
        self.expect_str(
            n="username",
            allow_empty=False,
            allow_none=False,
            input_method=self.get_str,
            validation=regex_username)
        self.expect_str(
            n="password",
            allow_empty=False,
            allow_none=False,
            input_method=self.get_password,
            validation=regex_password)
        self.expect_str(
            n="account",
            allow_empty=False,
            allow_none=False,
            input_method=self.get_str,
            validation=regex_account)
        self.expect_str(
            n="role_arn",
            allow_empty=True,
            allow_none=False,
            input_method=self.select_role,
            validation=regex_role_arn)

    def expect_attr(self, n: str) -> any:
        """
            Perform a check to ensure we have an expected attribute.

            param n: str
            return: any
        """
        assert hasattr(self, n), f"expected attribute {n} not found."
        return getattr(self, n)

    def expect_bool(self, n: str, input_method: Callable) -> None:
        """
            Perform a type check on boolean attributes.
                - expect a boolean
                - if None, get user input
                - else throw exception
            :param n: string (object name)
            :param input_method: Callable (user input method)
        """
        o = self.expect_attr(n)
        if o.__class__ is bool:
            return
        elif o is None:
            setattr(self, n, input_method(n))
        else:
            raise TypeCheckException("boolean", n, o.__class__)

    def expect_int(self, n: str,
                   min: int = None,
                   max: int = None,
                   input_method: Callable = None) -> None:
        """
             Perform a type check on int attributes of self.
                 - Expect integer
                 - Expect non-None type
            :param n: string (object name)
            :param min: int: minimum value or none (disables value check)
            :param max: int: maximum value or none (disables value check)
            :param input_method: Callable (user input method)
         """
        o = self.expect_attr(n)
        if o.__class__ is int:
            if (min is not None) and (min > o):
                raise IntegerMinBoundCheckError(n, o, min)
            if (max is not None) and (max < o):
                raise IntegerMaxBoundCheckError(n, o, max)
            return
        elif o is None and input_method is not None:
            setattr(self, n, input_method(n, min, max))
        else:
            raise TypeCheckException("int", n, o.__class__)

    def expect_str(self, n: str,
                   allow_empty: bool,
                   allow_none: bool,
                   input_method: Callable,
                   validation: str) -> None:
        """
             Perform a type check on int attributes of self.

             - expect string type if none_allowed is False
             - expect string or None if none_allowed is True

             :param n: string (object name)
             :param allow_empty: bool (allow an empty string)
             :param allow_none: bool (allow None value)
             :param input_method: Callable (user prompt method).
             :param validation: str (regex for evaluating string value)
         """
        o = self.expect_attr(n)
        if allow_empty and (o == ""):
            return
        elif allow_none and (o is None):
            return
        elif (o == "") or (o is None):
            o = input_method(n, allow_empty)

        if o.__class__ is str:
            pattern = compile(validation)
            if pattern.match(o) is None:
                raise StringValidationError(n, validation)
            setattr(self, n, o)
        else:
            raise TypeCheckException("string", n, o.__class__)
