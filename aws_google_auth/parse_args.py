#!/usr/bin/env python3

__strict__ = True

from os import getenv
from argparse import Namespace
from version import __version__
from argparse import ArgumentParser


def parse_args(args: list) -> Namespace:
    """
        Parse command-line arguments.

        :param args: list
        :return: Namespace
    """

    parser = ArgumentParser(
        prog="aws-google-auth",
        description="Acquire temporary AWS credentials via Google SSO",
    )

    google_username = getenv("GOOGLE_USERNAME", "")
    parser.add_argument(
        "-u", "--username",
        type=str,
        default=google_username,
        help=f"Google Apps username ({google_username})")

    google_idp_id = getenv("GOOGLE_IDP_ID", "")
    parser.add_argument(
        "-I", "--idp-id",
        type=str,
        default=google_idp_id,
        help=f"Google SSO IDP identifier ({google_idp_id})")

    google_sp_id = getenv("GOOGLE_SP_ID")
    parser.add_argument(
        "-S", "--sp-id",
        type=str,
        default=google_sp_id,
        help=f"Google SSO SP identifier ({google_sp_id})")

    aws_default_region = getenv("AWS_DEFAULT_REGION", "")
    parser.add_argument(
        "-R", "--region",
        type=str,
        default=aws_default_region,
        help=f"AWS region endpoint ({aws_default_region})")

    duration_group = parser.add_mutually_exclusive_group()

    default_duration = 43200
    try:
        duration = int(getenv("DURATION", default_duration))

    except ValueError:
        duration = default_duration

    duration_group.add_argument(
        "-d", "--duration",
        type=int,
        default=duration,
        help="Credential duration in seconds "
             f"(defaults to value of {duration}, "
             f"then falls back to {default_duration})")

    auto_duration = getenv("AUTO_DURATION",
                           "false").lower().strip() == "true"
    duration_group.add_argument(
        "--auto-duration",
        action="store_true",
        default=auto_duration,
        help=f"Tries to use the longest allowed duration ({auto_duration})")

    aws_profile = getenv("AWS_PROFILE", "sts")
    parser.add_argument(
        "-p", "--profile",
        help=f"AWS profile (defaults to value of {aws_profile}, "
             "then falls back to \"sts\")")

    parser.add_argument(
        "-A", "--account",
        help="Filter for specific AWS account.")

    parser.add_argument(
        "-D", "--disable-u2f",
        action="store_true",
        help="Disable U2F functionality.")

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet output")

    google_bg_response = getenv("GOOGLE_BG_RESPONSE", "")
    parser.add_argument(
        "--bg-response",
        type=str,
        default=google_bg_response,
        help="Override default bgresponse "
             f"challenge token ({google_bg_response}")

    saml_assertion = getenv("SAML_ASSERTION", "")
    parser.add_argument(
        "--saml-assertion",
        dest="saml_assertion",
        type=str,
        default=saml_assertion,
        help=f"Base64 encoded SAML assertion to use ({saml_assertion}).")

    parser.add_argument(
        "--no-cache",
        dest="saml_cache",
        action="store_false",
        help="Do not cache the SAML Assertion.")

    parser.add_argument(
        "--print-creds",
        action="store_true",
        help="Print Credentials.")

    parser.add_argument(
        "--resolve-aliases",
        action="store_true",
        help="Resolve AWS account aliases.")

    parser.add_argument(
        "--save-failure-html",
        action="store_true",
        help="Write HTML failure responses to file for troubleshooting.")

    parser.add_argument(
        "--save-saml-flow",
        action="store_true",
        help="Write all GET and PUT requests and HTML responses "
             "to/from Google to files for troubleshooting.")

    role_group = parser.add_mutually_exclusive_group()
    role_group.add_argument(
        "-a", "--ask-role",
        action="store_true",
        help="Set true to always pick the role")

    role_group.add_argument(
        "-r", "--role-arn",
        help="The ARN of the role to assume")

    parser.add_argument(
        "-k", "--keyring",
        action="store_true",
        help="Use keyring for storing the password.")

    default_log_level = getenv("SSO_LOG_LEVEL", "warn")
    parser.add_argument(
        "-l", "--log",
        dest="log_level",
        choices=["debug", "info", "warn"],
        default=default_log_level,
        help=f"Select log level (default: {default_log_level})")

    version = __version__
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {version}")

    return parser.parse_args(args)
