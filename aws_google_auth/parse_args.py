#!/usr/bin/env python3

__strict__ = True

from os import getenv
from version import __version__
from argparse import ArgumentParser
from configuration import Configuration


def parse_args() -> Configuration:
    """
        Parse command-line arguments and reconcile
        to both environment variables and configuration
        file (optional).

        Order of precedence:
            - command-line arguments, which overrides...
            - environment variables, which overrides...
            - configuration file, which overrides...
            - hard-coded defaults in Configuration class.

        :return: Configuration
    """

    def coalesce(*argument_list: any) -> any:
        """
            Accept the first defined non-None argument.
            :param argument_list: any
            :return: any
        """
        for _, value in enumerate(argument_list):
            if value is not None:
                return value
        return None

    parser = ArgumentParser(
        prog="aws-google-auth",
        description="Acquire temporary AWS credentials via Google SSO",
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}")

    config = Configuration()

    config.load(config.profile)

    config.profile = getenv("AWS_PROFILE", config.profile)
    parser.add_argument(
        "-p", "--profile",
        dest="profile",
        default=config.profile,
        help=f"AWS profile")

    config.log_level = getenv("SSO_LOG_LEVEL", config.log_level)
    parser.add_argument(
        "-l", "--log",
        dest="log_level",
        choices=["debug", "info", "warn"],
        default=config.log_level,
        help=f"Select log level")

    config.username = getenv("GOOGLE_USERNAME", config.username)
    parser.add_argument(
        "-u", "--username",
        dest="username",
        type=str,
        default=config.username,
        help=f"Google username")

    config.idp_id = getenv("GOOGLE_IDP_ID", config.idp_id)
    parser.add_argument(
        "-I", "--idp-id",
        dest="idp_id",
        type=str,
        default=config.idp_id,
        help=f"Google SSO IDP identifier")

    config.sp_id = getenv("GOOGLE_SP_ID", config.sp_id)
    parser.add_argument(
        "-S", "--sp-id",
        dest="sp_id",
        type=str,
        default=config.sp_id,
        help=f"Google SSO SP identifier")

    config.region = getenv("AWS_DEFAULT_REGION", config.region)
    parser.add_argument(
        "-R", "--region",
        dest="region",
        type=str,
        default=config.region,
        help=f"AWS region endpoint")

    duration_group = parser.add_mutually_exclusive_group()

    config.duration = int(getenv("DURATION", config.duration))
    duration_group.add_argument(
        "-d", "--duration",
        dest="duration",
        type=int,
        default=config.duration,
        help="Credential duration in seconds")

    config.auto_duration = getenv("AUTO_DURATION", config.auto_duration)
    duration_group.add_argument(
        "--auto-duration",
        dest="auto_duration",
        action="store_true",
        default=config.auto_duration,
        help=f"Tries to use the longest allowed duration "
             f"({config.max_duration})")

    config.account = getenv("AWS_ACCOUNT", config.account)
    parser.add_argument(
        "-A", "--account",
        type=str,
        dest="account",
        default=config.account,
        help=f"Filter for specific AWS account.")

    config.bg_response = getenv("GOOGLE_BG_RESPONSE", config.bg_response)
    parser.add_argument(
        "--bg-response",
        type=str,
        dest="bg_response",
        default=config.bg_response,
        help="Override default bgresponse challenge token")

    config.saml_assertion = getenv("SAML_ASSERTION", config.saml_assertion)
    parser.add_argument(
        "--saml-assertion",
        dest="saml_assertion",
        type=str,
        default=config.saml_assertion,
        help="Base64 encoded SAML assertion to use")

    role_group = parser.add_mutually_exclusive_group()
    config.role_arn = getenv('AWS_ROLE_ARN', config.role_arn)
    role_group.add_argument(
        "-r", "--role-arn",
        dest="role_arn",
        default=config.role_arn,
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

    parser.add_argument(
        "-D", "--disable-u2f",
        dest="u2f_disabled",
        action="store_true",
        help="Disable U2F functionality.")

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

    config.profile = args.profile
    config.log_level = args.log_level
    config.username = args.username
    config.idp_id = args.idp_id
    config.sp_id = args.sp_id
    config.region = args.region
    config.duration = args.duration
    config.auto_duration = args.auto_duration
    config.account = args.account
    config.bg_response = args.bg_response
    config.saml_assertion = args.saml_assertion
    config.role_arn = args.role_arn
    config.ask_role = args.ask_role and config.ask_role
    config.saml_cache = None if args.no_cache else config.saml_cache_file
    config.print_creds = args.print_creds
    config.resolve_aliases = args.resolve_aliases
    config.save_failure_html = args.save_failure_html
    config.save_saml_flow = args.save_saml_flow
    config.keyring = coalesce(args.keyring, config.keyring)
    config.u2f_disabled = args.u2f_disabled
    config.quiet = args.quiet

    return config
