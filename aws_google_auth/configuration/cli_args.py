#!/usr/bin/env python3

__strict__ = True

from .reader import Reader
from ..version import __version__
from argparse import ArgumentParser


class CommandLineArgs(Reader):
    """
        Parse the command-line arguments and
        if appropriate override the config file
        parameters.
    """

    def __init__(self):
        """
            class constructor.

            Parse command-line arguments and reconcile
            to both environment variables and configuration
            file (optional).
        """
        super().__init__()

        parser = ArgumentParser(
            prog="aws-google-auth",
            description="Acquire temporary AWS credentials via Google SSO")

        parser.add_argument(
            "-V", "--version",
            action="version",
            version=f"%(prog)s {__version__}")

        self.load()  # Loads the default profile...

        parser.add_argument(
            "-l", "--log",
            dest="log_level",
            choices=["debug", "info", "warn"],
            default=self.log_level,
            help="Select log level")

        parser.add_argument(
            "-u", "--username",
            dest="username",
            type=str,
            default=self.username,
            help="Google username")

        parser.add_argument(
            "-I", "--idp-id",
            dest="idp_id",
            type=str,
            default=self.idp_id,
            help="Google SSO IDP identifier")

        parser.add_argument(
            "-S", "--sp-id",
            dest="sp_id",
            type=str,
            default=self.sp_id,
            help="Google SSO SP identifier")

        parser.add_argument(
            "-R", "--region",
            dest="region",
            type=str,
            default=self.region,
            help="AWS region endpoint")

        duration_group = parser.add_mutually_exclusive_group()

        duration_group.add_argument(
            "-d", "--duration",
            dest="duration",
            type=int,
            default=self.duration,
            help="Credential duration in seconds")

        duration_group.add_argument(
            "--auto-duration",
            dest="auto_duration",
            action="store_true",
            default=self.auto_duration,
            help="Tries to use the longest allowed duration "
                 f"({self.max_duration})")

        parser.add_argument(
            "-A", "--account",
            type=str,
            dest="account",
            default=self.account,
            help="Filter for specific AWS account.")

        parser.add_argument(
            "--bg-response",
            type=str,
            dest="bg_response",
            default=self.bg_response,
            help="Override default bgresponse challenge token")

        parser.add_argument(
            "--saml-assertion",
            dest="saml_assertion",
            type=str,
            default=self.saml_assertion,
            help="Base64 encoded SAML assertion to use")

        role_group = parser.add_mutually_exclusive_group()

        role_group.add_argument(
            "-r", "--role-arn",
            dest="role_arn",
            default=self.role_arn,
            help="The ARN of the role to assume")

        role_group.add_argument(
            "-a", "--ask-role",
            dest="ask_role",
            action="store_true",
            help="Set true to always pick the role")

        parser.add_argument(
            "--no-cache",
            dest="no_cache",
            action="store_false",
            help="Do not cache the SAML Assertion.")

        parser.add_argument(
            "--print-creds",
            dest="print_creds",
            action="store_true",
            help="Print Credentials.")

        parser.add_argument(
            "--resolve-aliases",
            dest="resolve_aliases",
            action="store_true",
            help="Resolve AWS account aliases.")

        parser.add_argument(
            "--save-failure-html",
            dest="save_failure_html",
            action="store_true",
            help="Write HTML failure responses to file for troubleshooting.")

        parser.add_argument(
            "--save-saml-flow",
            dest="save_saml_flow",
            action="store_true",
            help="Write all GET and PUT requests and HTML responses "
                 "to/from Google to files for troubleshooting.")

        parser.add_argument(
            "-k", "--keyring",
            dest="keyring",
            action="store_true",
            help="Use keyring for storing the password.")

        # parser.add_argument(
        #     "-D", "--u2f_disabled",
        #     dest="u2f_disabled",
        #     action="store_true",
        #     help="Disable U2F functionality.")

        parser.add_argument(
            "-q", "--quiet",
            action="store_true",
            help="Quiet output")
        #
        # -----------------------------------------------------
        # parse arguments
        # -----------------------------------------------------
        #
        args = parser.parse_args()

        self.profile = args.profile
        self.log_level = args.log_level
        self.username = args.username
        self.idp_id = args.idp_id
        self.sp_id = args.sp_id
        self.region = args.region
        self.duration = args.duration
        self.auto_duration = args.auto_duration
        self.account = args.account
        self.bg_response = args.bg_response
        self.saml_assertion = args.saml_assertion
        self.role_arn = args.role_arn
        self.ask_role = args.ask_role and self.ask_role
        self.saml_cache = None if args.no_cache else self.saml_cache_file
        self.print_creds = args.print_creds
        self.resolve_aliases = args.resolve_aliases
        self.save_failure_html = args.save_failure_html
        self.save_saml_flow = args.save_saml_flow
        self.keyring = self.coalesce(args.keyring, self.keyring)
        self.u2f_disabled = args.u2f_disabled
        self.quiet = args.quiet
