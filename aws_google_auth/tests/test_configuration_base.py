#!/usr/bin/env python3

__strict__ = True

import unittest

from os import getenv
from botocore.session import Session
from aws_google_auth.configuration.base import Base
from aws_google_auth.configuration.base import DEFAULT_AWS_PROFILE
from aws_google_auth.configuration.base import DEFAULT_MIN_DURATION
from aws_google_auth.configuration.base import DEFAULT_MAX_DURATION
from aws_google_auth.configuration.base import DEFAULT_LOG_LEVEL


class TestConfigurationBaseClass(unittest.TestCase):
    def test_strictness(self):
        """
            Test strictness.
        """
        self.assertTrue(__strict__, "expect __strict__ is True")

    def test_constant_aws_profile(self):
        """
            Make sure we didn't accidentally fudge the default aws profile
        """
        self.assertTrue(DEFAULT_AWS_PROFILE == "sts", "expect sts")

    def test_constant_min_max_duration(self):
        """
            Make sure we didn't accidentally fudge the min/max durations
        """
        self.assertTrue(type(DEFAULT_MIN_DURATION) is int)
        self.assertTrue(type(DEFAULT_MAX_DURATION) is int)
        self.assertTrue(DEFAULT_MIN_DURATION >= 900)
        self.assertTrue(DEFAULT_MAX_DURATION <= 43200)
        self.assertTrue(DEFAULT_MIN_DURATION < DEFAULT_MAX_DURATION)

    def test_constant_log_level(self):
        """
            Make sure we didn't accidentally fudge the log level default.
        """
        self.assertTrue(type(DEFAULT_LOG_LEVEL) is str)
        self.assertTrue(DEFAULT_LOG_LEVEL.lower() in ["debug", "warn", "info"])

    def test_initial_state(self):
        """
            Instantiate the class and test the initial state.
            This also means doing some pre-checks to ensure the
            environment variables are not set.
        """
        #  Pre-flight check
        for var in ["AWS_PROFILE", "SSO_LOG_LEVEL", "AWS_PROFILE",
                    "SSO_LOG_LEVEL", "GOOGLE_USERNAME", "GOOGLE_IDP_ID",
                    "GOOGLE_SP_ID", "AWS_DEFAULT_REGION"]:
            self.assertTrue(getenv(var, "not_set") == "not_set")

        #  Create the class instance.
        o = Base()

        #  Inspect the state.
        self.assertTrue(hasattr(o, 'options'))
        self.assertTrue(type(o.options) is dict, "expects dict")
        self.assertTrue(o.options == {}, "expect empty dict")

        self.assertTrue(hasattr(o, 'profile'))
        self.assertTrue(type(o.profile), "expects string")
        self.assertTrue(o.profile == DEFAULT_AWS_PROFILE, "expect default")

        self.assertTrue(hasattr(o, 'log_level'))
        self.assertTrue(type(o.log_level) is str, "expects string")
        self.assertTrue(o.log_level == DEFAULT_LOG_LEVEL, "expect default")

        self.assertTrue(hasattr(o, 'username'))
        self.assertTrue(type(o.username) is str, "expects string")
        self.assertTrue(o.username == "", "username expect empty by default")

        self.assertTrue(hasattr(o, 'idp_id'))
        self.assertTrue(type(o.idp_id) is str, "expects string)")
        self.assertTrue(o.idp_id == "", "idp_id should be empty by default")

        self.assertTrue(hasattr(o, 'sp_id'))
        self.assertTrue(type(o.sp_id) is str, "expects string)")
        self.assertTrue(o.sp_id == "", "sp_id should be empty by default")

        self.assertTrue(hasattr(o, 'region'))
        self.assertTrue(type(o.region) is str, "expects string)")
        self.assertTrue(o.region == "", "region should be empty by default")

        self.assertTrue(hasattr(o, '_min_duration'))
        self.assertTrue(type(o._min_duration) is int, "expects int)")
        self.assertTrue(o._min_duration == DEFAULT_MIN_DURATION)

        self.assertTrue(hasattr(o, '_max_duration'))
        self.assertTrue(type(o._max_duration) is int, "expects int)")
        self.assertTrue(o._max_duration == DEFAULT_MAX_DURATION)

        self.assertTrue(hasattr(o, 'duration'))
        self.assertTrue(type(o.duration) is int, "expects int)")
        self.assertTrue(o.duration == DEFAULT_MAX_DURATION)

        self.assertTrue(hasattr(o, 'auto_duration'))
        self.assertTrue(type(o.auto_duration) is bool, "expects bool)")
        self.assertTrue(not o.auto_duration, "expects false")

        self.assertTrue(hasattr(o, 'account'))
        self.assertTrue(type(o.account) is str, "expects string)")
        self.assertTrue(o.account == "", "account should be empty by default")

        self.assertTrue(hasattr(o, 'bg_response'))
        self.assertTrue(type(o.bg_response) is str, "expects string)")
        self.assertTrue(o.bg_response == "", "expects empty string")

        self.assertTrue(hasattr(o, 'saml_assertion'))
        self.assertTrue(type(o.saml_assertion) is bytes, "expects bytes)")
        self.assertTrue(o.saml_assertion == b'', "expects empty bytes")

        self.assertTrue(hasattr(o, 'role_arn'))
        self.assertTrue(type(o.role_arn) is str, "expects string)")
        self.assertTrue(o.role_arn == "", "expects empty string")

        self.assertTrue(hasattr(o, 'ask_role'))
        self.assertTrue(type(o.ask_role) is bool, "expects bool)")
        self.assertTrue(o.ask_role, "Expects True")

        sc = o.saml_cache
        self.assertTrue(type(sc) is bytes, f"expects bytes got {type(sc)}")
        self.assertTrue(sc == bytes("".encode('utf-8')))

        self.assertTrue(type(o.print_creds) is bool, "expects bool)")
        self.assertTrue(not o.print_creds, "Expects False")

        self.assertTrue(type(o.resolve_aliases) is bool, "expects bool)")
        self.assertTrue(not o.resolve_aliases, "Expects False")

        self.assertTrue(type(o.save_failure_html) is bool, "expects bool)")
        self.assertTrue(not o.save_failure_html, "Expects False")

        self.assertTrue(type(o.save_saml_flow) is bool, "expects bool)")
        self.assertTrue(not o.save_saml_flow, "Expects False")

        self.assertTrue(type(o.keyring) is bool, "expects bool)")
        self.assertTrue(not o.keyring, "Expects False")

        self.assertTrue(type(o.u2f_disabled) is bool, "expects bool)")
        self.assertTrue(o.u2f_disabled, "Expects True")

        self.assertTrue(type(o.quiet) is bool, "expects bool)")
        self.assertTrue(not o.quiet, "Expects False")

        self.assertTrue(type(o.password) is str, "expects str)")
        self.assertTrue(o.password == "", "Expects empty string")

        self.assertTrue(type(o.provider) is str, "expects str)")
        self.assertTrue(o.provider == "", "Expects empty string")

    def test_property_max_duration(self):
        """
            Test the readonly max_duration property
                : max_duration > 0
                : max_duration > min_duration
        """
        o = Base()
        o._min_duration = 0
        o._max_duration = 100
        self.assertTrue(o._max_duration == o.max_duration)
        for i in range(1, 10):
            o.max_duration = i
            self.assertTrue(o._max_duration == i)
        try:
            o.max_duration = 0
            self.fail("min cannot be zero")
        except ValueError:
            pass
        try:
            o.max_duration = -1
            self.fail("min cannot be less than zero")
        except ValueError:
            pass
        try:
            o.max_duration = o.min_duration
            self.fail("max cannot be min")
        except ValueError:
            pass
        try:
            o.min_duration = 100
            o.max_duration = 99
            self.fail("min cannot be greater than max")
        except ValueError:
            pass

    def test_property_min_duration(self):
        """
            Test the readonly min_duration property
                : min_duration > 0
                : min_duration < max_duration
        """
        o = Base()
        o._max_duration = DEFAULT_MAX_DURATION
        o._min_duration = 1
        self.assertTrue(o._min_duration == o.min_duration)
        for i in range(1, 10):
            o.min_duration = i
            self.assertTrue(o._min_duration == i)
        try:
            o.min_duration = 0
            self.fail("min cannot be zero")
        except ValueError:
            pass
        try:
            o.min_duration = -1
            self.fail("min cannot be less than 0")
        except ValueError:
            pass
        try:
            o.max_duration = o.min_duration
            self.fail("min and max cannot be the same")
        except ValueError:
            pass
        try:
            o.min_duration = 10
            o.max_duration = 9
            self.fail("min cannot be greater than max")
        except ValueError:
            pass

    def test_property_saml_cache_file(self):
        """
            Test the SAML cache file name property.
        """
        o = Base()
        f = o.saml_cache_file
        self.assertTrue(type(f) is str, "expected string from property.")
        e = o.credentials_file.replace(
            "credentials", f"saml_cache_{o.idp_id}.xml")
        self.assertTrue(f == e, "expected output not found.")

    def test_property_saml_cache(self):
        """
            Test the saml cache setter.
        """
        b = bytes("".encode('utf-8'))
        o = Base()
        o.saml_cache = b
        self.assertTrue(o.saml_cache == b,
                        "saml_cache mismatch\n"
                        f"saml_cache: '{o.saml_cache}'\n"
                        f"expected  : '{b}'")
