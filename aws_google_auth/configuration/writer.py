#!/usr/bin/env python3

__strict__ = True

from .base import Base
from filelock import FileLock
from configparser import RawConfigParser


class Writer(Base):
    """
        Configuration Writer Class
    """
    def __init__(self):
        """
            class constructor
        """
        super().__init__()

    def write(self, amazon_object: any) -> None:
        """
           Write the configuration (and credentials) out to disk.
           This allows for regular AWS tooling (aws cli and boto) to use
           the credentials in the profile the user specified.

            param amazon_object: any
            :return: None
        """
        self.ensure_config_files_exist()

        assert self.profile is not None, \
            "Can not store config/credentials if the AWS_PROFILE is None."

        config_file_lock = FileLock(self.config_file + '.lock')
        config_file_lock.acquire()
        try:
            # Write to the configuration file
            profile = self.config_profile(self.profile)
            parser = RawConfigParser()
            parser.read(self.config_file)

            if not parser.has_section(profile):
                # self.profile is the section header 'profile <profile name>'
                parser.add_section(profile)

            # Log level is not saved.
            parser.set(profile, "google_config.google_username", self.username)
            parser.set(profile, "google_config.google_idp_id", self.idp_id)
            parser.set(profile, "google_config.google_sp_id", self.sp_id)
            parser.set(profile, "region", self.region)
            parser.set(profile, "google_config.duration", f"{self.duration}")
            # Auto Duration does not persist.
            # Account does not persist.
            parser.set(profile, "google_config.bg_response", self.bg_response)
            # SAML Assertion does not persist.
            parser.set(profile, "google_config.role_arn", self.role_arn)
            parser.set(profile, "google_config.ask_role", f"{self.ask_role}")
            # SAML Cache does not persist.
            # print_creds does not persist.
            # resolve_addresses does not persist
            # save_failure_html does not persist
            parser.set(profile, "google_config.keyring", f"{self.keyring}")
            parser.set(profile, "google_config.u2f_disabled",
                       f"{self.u2f_disabled}")
            # quiet does not persist
            # password does not persist
            with open(self.config_file, 'w+') as f:
                parser.write(f)
        except IOError as e:
            print(f"Error writing config file({self.config_file}: {e}")
        finally:
            config_file_lock.release()

            # Write to the credentials file (only if we have credentials)
            if amazon_object is not None:
                credentials_file_lock = FileLock(
                    f"{self.credentials_file}.lock")
                credentials_file_lock.acquire()
                try:
                    credentials_parser = RawConfigParser()
                    credentials_parser.read(self.credentials_file)
                    if not credentials_parser.has_section(self.profile):
                        credentials_parser.add_section(self.profile)
                    credentials_parser.set(
                        self.profile,
                        'aws_access_key_id',
                        amazon_object.access_key_id)
                    credentials_parser.set(
                        self.profile,
                        'aws_secret_access_key',
                        amazon_object.secret_access_key)
                    credentials_parser.set(
                        self.profile, 'aws_security_token',
                        amazon_object.session_token)
                    credentials_parser.set(
                        self.profile,
                        'aws_session_expiration',
                        amazon_object.expiration.strftime(
                            '%Y-%m-%dT%H:%M:%S%z'))
                    credentials_parser.set(
                        self.profile, 'aws_session_token',
                        amazon_object.session_token)
                    with open(self.credentials_file, 'w+') as f:
                        credentials_parser.write(f)
                finally:
                    credentials_file_lock.release()

            if self.__saml_cache is not None:
                saml_cache_file_lock = FileLock(f"{self.saml_cache_file}.lock")
                saml_cache_file_lock.acquire()
                try:
                    with open(self.saml_cache_file, 'w') as f:
                        f.write(self.__saml_cache.decode("utf-8"))
                finally:
                    saml_cache_file_lock.release()
