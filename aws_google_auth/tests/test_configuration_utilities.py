#!/usr/bin/env python3

__strict__ = True

import unittest
from os import mkdir
from os import remove
from uuid import uuid4
from shutil import rmtree
from os.path import exists
from os.path import expanduser
from aws_google_auth.configuration.utilities import Utilities


class TestConfigurationUtilitiesClass(unittest.TestCase):
    def test_strictness(self):
        """
            Test strictness.
        """
        self.assertTrue(__strict__, "expect __strict__ is True")

    def test_initial_state(self):
        """
            Verify the initial state of the Utilities class
        """
        o = Utilities()
        # Internal state is private...not much to test here.

    def test_credentials_file(self):
        """
            Test the credentials file.
        """
        o = Utilities()
        expected = expanduser('~/.aws/credentials')
        self.assertTrue(o.credentials_file == expected, "filename mismatch")

        with open(o.credentials_file, 'r') as f:
            _ = f.read()

        self.assertTrue(type(o.credentials_file) is str,
                        "filename expects str")

    def test_config_file(self):
        """
            Test the config file.
        """
        o = Utilities()
        expected = expanduser('~/.aws/config')
        self.assertTrue(o.config_file == expected, "filename mismatch")

        with open(o.config_file, 'r') as f:
            _ = f.read()

        self.assertTrue(type(o.config_file) is str, "filename expects str")

    def test_ensure_config_files_exist(self):
        """
            Test that if a config file does not exist it will be created.
            This is going to get potentially destructive, but it should make
            a copy of what exists before doing anything. It should restore
            things to original state before stopping--even if things fail.
        """
        has_backup: bool = False
        config_dir = expanduser("~/.aws")
        config_file = expanduser(f"{config_dir}/config")
        creds_file = expanduser(f"{config_dir}/credentials")
        backup_dir = expanduser("~/.aws.bak")
        backup_config = expanduser(f"{backup_dir}/config")
        backup_creds = expanduser(f"{backup_dir}/credentials")

        def backup_config_files(delete_source: bool = False):
            """
                create a backup o four configuration files.
            """
            self.assertTrue(exists(config_dir), "missing config_dir")
            self.assertTrue(exists(config_file), "missing config_file")
            self.assertTrue(exists(creds_file), "missing creds_file")
            if exists(backup_dir):
                print("removing old backup")
                rmtree(backup_dir)
            mkdir(backup_dir)
            if exists(config_file):
                print("config_file exists.  create backup.")
                with open(config_file, 'r') as source:
                    with open(backup_config, 'w') as backup:
                        backup.write(source.read())
            if exists(creds_file):
                print("creds_file exists.  create backup.")
                with open(creds_file, 'r') as source:
                    with open(backup_creds, 'w') as backup:
                        backup.write(source.read())
            self.assertTrue(exists(backup_dir), "missing backup_dir")
            self.assertTrue(exists(backup_config), "missing backup_config")
            self.assertTrue(exists(backup_creds), "missing backup_creds")
            if delete_source and exists(config_dir):
                print("deleting config_dir after backup")
                rmtree(config_dir)
            return True

        def restore_config_files(cleanup_files: bool = False):
            """
                restore the backup files to the original directory.
            """
            if has_backup:
                self.assertTrue(exists(backup_dir), "missing backup_dir")
                self.assertTrue(exists(backup_config), "missing backup_config")
                self.assertTrue(exists(backup_creds), "missing backup_creds")
                if exists(config_dir):
                    rmtree(config_dir)
                mkdir(config_dir)
                with open(backup_config, 'r') as source:
                    with open(config_file, 'w') as target:
                        target.write(source.read())
                with open(backup_creds, 'r') as source:
                    with open(creds_file, 'w') as target:
                        target.write(source.read())
                if cleanup_files:
                    rmtree(backup_dir)
            else:
                print("no backup exists")

        o = Utilities()
        ex = None
        try:
            has_backup = backup_config_files(True)
            self.assertTrue(has_backup, "expected backup")
            self.assertTrue(not exists(config_dir))
            self.assertTrue(not exists(config_file))
            self.assertTrue(not exists(creds_file))
            o.ensure_config_files_exist()
            self.assertTrue(exists(config_dir))
            self.assertTrue(exists(config_file))
            self.assertTrue(exists(creds_file))
            with open(config_file, 'r') as f:
                self.assertTrue(len(f.read()) == 0, "expect empty file.")
            with open(creds_file, 'r') as f:
                self.assertTrue(len(f.read()) == 0, "expect empty file.")
            restore_config_files(False)  # restore the files so we can test.
            with open(config_file, 'r') as f:
                self.assertTrue(len(f.read()) > 0, "expect non-empty file.")
            with open(creds_file, 'r') as f:
                self.assertTrue(len(f.read()) > 0, "expect non-empty file.")
        except Exception as e:
            print(f"exception: {e}")
            ex = e
        finally:
            print("finishing up")
            if ex is None:
                restore_config_files(True)
            else:
                print("Restoring config files ...but not deleting backup")
                restore_config_files(False)
                raise ex

    def test_touch_method(self):
        """
            Test the touch() method.
        """
        o = Utilities()
        filename = f"/tmp/test-{uuid4()}.txt"
        self.assertTrue(not exists(filename), "expected no such file")
        o.touch(filename)
        self.assertTrue(exists(filename))
        o.touch(filename)
        self.assertTrue(exists(filename))
        remove(filename)
        self.assertTrue(not exists(filename))

    def test_config_profile(self):
        """
            test that config_profile() returns a full profile name.
        """
        o = Utilities()
        self.assertTrue(o.config_profile("default") == "default")
        self.assertTrue(o.config_profile("p") == "profile p")
        self.assertTrue(o.config_profile("no") == "profile no")
        self.assertTrue(o.config_profile("identity") == "profile identity")
        try:
            self.assertTrue(o.config_profile("") == "profile ")
            self.fail("empty string should raise exception")
        except ValueError as e:
            self.assertTrue(f"{e}" == "config_profile(): empty profile")

    def test_coalesce(self):
        """
            Given a list of elements where the leading edge of the list is a
            None value, expect that coalesce() will return the first
            (left-most) non-None value.
        """
        o = Utilities()
        data = [None, None, "hi", None, "error"]
        self.assertTrue(o.coalesce(data) == "hi")
