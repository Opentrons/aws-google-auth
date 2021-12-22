#!/usr/bin/env python3

__strict__ = True

from os import getenv
from .utilities import Utilities
from aws_google_auth import amazon
from .exceptions import InvalidEnvironmentVariable

DEFAULT_AWS_PROFILE = "identity"  # This is an opentrons thing!


class Base(Utilities):
    """
        Base Configuration Class
    """

    def __init__(self):
        """
            class constructor.
                - set defaults which may be overridden by env var.
        """
        super().__init__()
        self.options = {}
        self.profile = getenv("AWS_PROFILE", DEFAULT_AWS_PROFILE)
        self.log_level = getenv("SSO_LOG_LEVEL", "warn")
        self.username = getenv("GOOGLE_USERNAME", None)
        self.idp_id = getenv("GOOGLE_IDP_ID", None)
        self.sp_id = getenv("GOOGLE_SP_ID", None)
        self.region = getenv("AWS_DEFAULT_REGION", None)
        self._min_duration = 900
        self._max_duration = 43200
        assert self._min_duration < self._max_duration, \
            "Min must be less than max duration."
        try:
            self.duration = int(getenv("DURATION", self._max_duration))
        except ValueError:
            raise InvalidEnvironmentVariable(
                f"DURATION must be 0-{self._max_duration}")

        self.auto_duration = getenv("AUTO_DURATION", False)
        self.account = getenv("AWS_ACCOUNT", None)
        self.bg_response = getenv("GOOGLE_BG_RESPONSE", None)
        self.saml_assertion = getenv("SAML_ASSERTION", None)
        self.role_arn = getenv('AWS_ROLE_ARN', None)
        self.ask_role = True
        self.__saml_cache = None
        self.print_creds = False
        self.resolve_aliases = False
        self.save_failure_html = False
        self.save_saml_flow = False
        self.keyring = False
        self.u2f_disabled = True  # Disabled for now
        self.quiet = False
        self.password = None

    @property
    def max_duration(self):
        return self._max_duration

    @property
    def saml_cache_file(self):
        return self.credentials_file.replace(
            "credentials", f"saml_cache_{self.idp_id}.xml")

    # Will return a SAML cache, ONLY if it's valid. If invalid or not set, will
    # return None. If the SAML cache isn't valid, we'll remove it from the
    # in-memory object. On the next write(), it will be purged from disk.
    @property
    def saml_cache(self):
        if not amazon.Amazon.is_valid_saml_assertion(self.__saml_cache):
            self.__saml_cache = None
        return self.__saml_cache

    @saml_cache.setter
    def saml_cache(self, value):
        self.__saml_cache = value
