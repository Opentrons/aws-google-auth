#!/usr/bin/env python3

__strict__ = True

import logging
import keyring
from logging import info
from logging import debug
from base64 import b64decode
from logging import getLogger
from argparse import Namespace
from tzlocal import get_localzone
from aws_google_auth import amazon
from aws_google_auth import google
from aws_google_auth.util import Util


def process_auth(args: Namespace, config):
    # Set up logging
    getLogger().setLevel(getattr(logging, args.log_level.upper(), None))

    if config.region is None:
        config.region = Util.get_input("AWS Region: ")
        debug(f"{__name__}: region is: {config.region}")

    # If there is a valid cache and the user opted to use it, use that instead
    # of prompting the user for input (it will also ignore any set variables
    # such as username or sp_id and idp_id, as those are built into the SAML
    # response). The user does not need to be prompted for a password if the
    # SAML cache is used.
    if args.saml_assertion:
        saml_xml = b64decode(args.saml_assertion)

    elif args.saml_cache and config.saml_cache:
        saml_xml = config.saml_cache
        info(f"{__name__}: SAML cache found")

    else:

        # No cache, continue without.
        info(f"{__name__}: SAML cache not found")

        if config.username is None:
            config.username = Util.get_input("Google username: ")
            debug(f"{__name__}: username is: {config.username}")

        if config.idp_id is None:
            config.idp_id = Util.get_input("Google IDP ID: ")
            debug(f"{__name__}: idp is: {config.idp_id}")

        if config.sp_id is None:
            config.sp_id = Util.get_input("Google SP ID: ")
            debug(f"{__name__}: sp is: {config.sp_id}")

        # There is no way (intentional) to pass in the password via the command
        # line nor environment variables. This prevents password leakage.
        keyring_password = None
        if config.keyring:
            keyring_password = keyring.get_password("aws-google-auth",
                                                    config.username)

            if keyring_password:
                config.password = keyring_password

            else:
                config.password = Util.get_password("Google Password: ")

        else:
            config.password = Util.get_password("Google Password: ")

        # Validate Options
        config.raise_if_invalid()

        google_client = google.Google(config,
                                      save_failure=args.save_failure_html,
                                      save_flow=args.save_saml_flow)

        google_client.do_login()

        saml_xml = google_client.parse_saml()

        debug(f"{__name__}: saml assertion is: {saml_xml}")

        # If we logged in correctly, and we are using keyring, then store
        # the password

        if config.keyring and keyring_password is None:
            keyring.set_password("aws-google-auth",
                                 config.username,
                                 config.password)

    # We now have a new SAML value that can get cached (If the user asked
    # for it to be)
    if args.saml_cache:
        config.saml_cache = saml_xml

    # The amazon_client now has the SAML assertion it needed (Either via the
    # cache or freshly generated). From here, we can get the roles and continue
    # the rest of the workflow regardless of cache.
    amazon_client = amazon.Amazon(config, saml_xml)
    roles = amazon_client.roles

    # Determine the provider and the role arn (if the user provided
    # isn't an option)
    if config.role_arn in roles and not config.ask_role:
        config.provider = roles[config.role_arn]

    else:
        if config.account and config.resolve_aliases:
            aliases = amazon_client.resolve_aws_aliases(roles)
            config.role_arn, config.provider = Util.pick_a_role(
                roles, aliases, config.account)

        elif config.account:
            config.role_arn, config.provider = Util.pick_a_role(
                roles, account=config.account)

        elif config.resolve_aliases:
            aliases = amazon_client.resolve_aws_aliases(roles)
            config.role_arn, config.provider = Util.pick_a_role(
                roles, aliases)

        else:
            config.role_arn, config.provider = Util.pick_a_role(roles)

    if not config.quiet:
        print("Assuming " + config.role_arn)
        print("Credentials Expiration: " + format(
            amazon_client.expiration.astimezone(get_localzone())))

    if config.print_creds:
        amazon_client.print_export_line()

    if config.profile:
        config.write(amazon_client)
