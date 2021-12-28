#!/usr/bin/env python3

__strict__ = True

from os import open
from os import utime
from os import mkdir
from os import fdopen
from os import O_CREAT
from os import O_APPEND
from os.path import exists
from os.path import dirname
from os.path import expanduser
from botocore.session import Session


class Utilities(object):
    """
        Base class providing utility methods.
    """

    def __init__(self):
        """
            class constructor
        """
        self.__boto_session = Session()

    @property
    def credentials_file(self) -> str:
        """
            read-only property returns AWS credentials file.
            :return: str
        """
        return expanduser(
            self.__boto_session.get_config_variable('credentials_file'))

    @property
    def config_file(self) -> str:
        """
            read-only property returns AWS config file.
            :return: str
        """
        return expanduser(
            self.__boto_session.get_config_variable('config_file'))

    def ensure_config_files_exist(self):
        """
            if a given file does not exist, then
            create the file as an empty config file.

            :return: None
        """
        for file in [self.config_file, self.credentials_file]:
            directory = dirname(file)
            if not exists(directory):
                mkdir(directory, 0o700)
            if not exists(file):
                self.touch(file)

    @staticmethod
    def touch(file_name, mode=0o600):
        flags = O_CREAT | O_APPEND
        with fdopen(open(file_name, flags, mode)) as f:
            try:
                utime(file_name, None)
            finally:
                f.close()

    @staticmethod
    def config_profile(profile: str):
        """
            For the "~/.aws/config" file, we use the format
            "[profile testing]" for the 'testing' profile.
            The credential file will just be "[testing]" in
            that case.

            For more information, see
            https://docs.aws.amazon.com/cli/latest/userguide/
            cli-multiple-profiles.html
        """
        return profile \
            if str(profile).lower() == 'default' else f"profile {profile}"

    @staticmethod
    def coalesce(*argument_list: any) -> any:
        """
            Accept the first defined non-None argument.

            param argument_list: any
            return: any
        """
        for _, value in enumerate(argument_list):
            if value is not None:
                return value
        return None
