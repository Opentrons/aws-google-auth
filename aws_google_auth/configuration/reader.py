#!/usr/bin/env python3

__strict__ = True

from .writer import Writer
from configparser import RawConfigParser


class Reader(Writer):
    """
        Configuration reader class
    """

    def __init__(self):
        """
            class constructor
        """
        super().__init__()

    def load(self) -> None:
        """
            - Read the ~/.aws/config file and override ALL values
              currently stored in the configuration object.

                               *** WARNING ***
                      This is potentially destructive!
                    it's important to only run this in the
                    beginning of the object initialization.

            - Do not read ~/.aws/credentials since this tool's use case is to
              obtain them and anything in that file *should* be obliterated.

            return: None
        """
        self.ensure_config_files_exist()

        profile_string = self.config_profile(self.profile)

        config_parser = RawConfigParser()
        config_parser.read(self.config_file)

        if config_parser.has_section(profile_string):
            self.ask_role = self.coalesce(
                config_parser[profile_string].getboolean(
                    "google_config.ask_role", None), self.ask_role)

            self.keyring = self.coalesce(
                config_parser[profile_string].getboolean(
                    "google_config.keyring", None), self.keyring)

            self.duration = self.coalesce(config_parser[profile_string].getint(
                "google_config.duration", None), self.duration)

            self.idp_id = self.coalesce(config_parser[profile_string].get(
                "google_config.google_idp_id", None), self.idp_id)

            self.region = self.coalesce(config_parser[profile_string].get(
                "region", None), self.region)

            self.role_arn = self.coalesce(config_parser[profile_string].get(
                "google_config.role_arn", None), self.role_arn)

            self.sp_id = self.coalesce(config_parser[profile_string].get(
                "google_config.google_sp_id", None), self.sp_id)

            self.u2f_disabled = self.coalesce(
                config_parser[profile_string].getboolean(
                    "google_config.u2f_disabled", None), self.u2f_disabled)

            self.username = self.coalesce(config_parser[profile_string].get(
                "google_config.google_username", None), self.username)

            self.bg_response = self.coalesce(config_parser[profile_string].get(
                "google_config.bg_response", None), self.bg_response)

            self.account = self.coalesce(config_parser[profile_string].get(
                "account", None), self.account)
        try:
            with open(self.saml_cache_file, 'r') as f:
                self.__saml_cache = f.read().encode("utf-8")
        except IOError:
            pass
