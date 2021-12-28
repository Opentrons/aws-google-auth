#!/usr/bin/env python3

__strict__ = True

from os import getenv
from lxml import etree
from typing import Optional
from datetime import datetime
from lxml.etree import _Element
from .utilities import Utilities
from .exceptions import InvalidEnvironmentVariable

DEFAULT_AWS_PROFILE: str = "sts"
DEFAULT_MIN_DURATION: int = 900
DEFAULT_MAX_DURATION: int = 43200
DEFAULT_LOG_LEVEL: str = "warn"


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
        self.options: dict = {}
        self.profile: str = getenv("AWS_PROFILE", DEFAULT_AWS_PROFILE)
        self.log_level: str = getenv("SSO_LOG_LEVEL", DEFAULT_LOG_LEVEL)
        self.username: str = getenv("GOOGLE_USERNAME", "")
        self.idp_id: str = getenv("GOOGLE_IDP_ID", "")
        self.sp_id: str = getenv("GOOGLE_SP_ID", "")
        self.region: str = getenv("AWS_DEFAULT_REGION", "")
        self._min_duration: int = 900
        self._max_duration: int = 43200
        assert self._min_duration < self._max_duration, \
            "Min must be less than max duration."
        try:
            self.duration: int = int(getenv("DURATION", self._max_duration))
        except ValueError:
            raise InvalidEnvironmentVariable(
                f"DURATION must be 0-{self._max_duration}")

        self.auto_duration: bool = getenv("AUTO_DURATION", False)
        self.account: str = getenv("AWS_ACCOUNT", "")
        self.bg_response: str = getenv("GOOGLE_BG_RESPONSE", "")
        self.saml_assertion: bytes = bytes(getenv("SAML_ASSERTION", "")
                                           .encode('utf-8'))
        self.role_arn: str = getenv('AWS_ROLE_ARN', "")
        self.ask_role: bool = True
        self.__saml_cache: bytes = bytes("".encode('utf-8'))
        self.print_creds: bool = False
        self.resolve_aliases: bool = False
        self.save_failure_html: bool = False
        self.save_saml_flow: bool = False
        self.keyring: bool = False
        self.u2f_disabled: bool = True  # Disabled for now
        self.quiet: bool = False
        self.password: str = ""
        self.provider: str = ""  # Defined programmatically

    @property
    def max_duration(self) -> int:
        """
            max lifetime (duration) of saml token
            :return: int
        """
        return self._max_duration

    @max_duration.setter
    def max_duration(self, v: int) -> None:
        """
            max lifetime (duration) of saml token
            :param v: int
            :return: None
        """
        if v <= 0:
            raise ValueError("max_duration cannot be less than or 0")
        if v <= self._min_duration:
            raise ValueError("max_duration must be greater than min_duration")
        self._max_duration = v

    @property
    def min_duration(self) -> int:
        """
            min lifetime (duration) of saml token
            :return: int
        """
        return self._min_duration

    @min_duration.setter
    def min_duration(self, v: int) -> None:
        """
            min lifetime (duration) of saml token
            :param v: int
            :return: None
        """
        if v <= 0:
            raise ValueError("min_duration cannot be less than or 0")
        if v >= self._max_duration:
            raise ValueError("min_duration must be greater than min_duration")
        self._min_duration = v

    @property
    def saml_cache_file(self) -> str:
        """
            Return the SAML cache file name.
            :return: str
        """
        return self.credentials_file.replace(
            "credentials", f"saml_cache_{self.idp_id}.xml")

    @property
    def saml_cache(self) -> bytes:
        """
            Will return a SAML cache, ONLY if it's valid. If invalid or
            not set, will return None. If the SAML cache isn't valid, we'll
            remove it from the in-memory object. On the next write(), it will
            be purged from disk.
            :return: bytes
        """
        return bytes("".encode('utf-8')) \
            if not self.is_valid_saml_assertion(self.__saml_cache) \
            else self.__saml_cache

    @saml_cache.setter
    def saml_cache(self, value: bytes) -> None:
        """
            Set the saml_cache property
        :param value: bytes
        :return: None
        """
        self.__saml_cache: bytes = value

    @staticmethod
    def is_valid_saml_assertion(saml_xml: bytes) -> bool:
        """
            Return boolean response whether SAML assertion is valid.
            :param saml_xml: bytes
            :return: bool
        """
        # noinspection PyBroadException
        try:
            assert saml_xml is not None  # Bail and return False
            assert saml_xml != bytes("")  # Bail and return False

            doc: _Element = etree.fromstring(saml_xml)
            tag: str = "{urn:oasis:names:tc:SAML:2.0:assertion}Conditions"
            conditions = list(doc.iter(tag=tag))
            now = datetime.utcnow()
            not_before = datetime.strptime(
                conditions[0].get("NotBefore", ""),
                "%Y-%m-%dT%H:%M:%S.%fZ")
            not_on_or_after = datetime.strptime(
                conditions[0].get("NotOnOrAfter", ""),
                "%Y-%m-%dT%H:%M:%S.%fZ")
            return not_before <= now < not_on_or_after
        except Exception:
            return False
