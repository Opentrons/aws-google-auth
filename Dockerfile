# Dockerfile
# (c) 2021 Sam Caldwell.  Opentrons, Inc.  All Rights Reserved.
#
# This file defines a docker image for use with aws-google-auth
# which aims to abstract the end users from python dependencies.
#
# Ubuntu Base image stage
#
FROM --platform=amd64 ubuntu:latest AS base

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /opt/app

RUN apt-get update -y --fix-missing && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
                    ca-certificates openssl libssl-dev python3 \
                    python3-dev python3-pip python3-certifi \
                    python3-lxml libusb-dev libffi-dev zlib1g-dev \
                    libjpeg-dev libtiff-dev tcl-dev tk-dev \
                    libopenjp2-7-dev liblcms2-dev libfreetype-dev

RUN apt-get install -y --no-install-recommends \
    $(apt-cache search linux-headers-$(uname -r | awk -F \. '{print $1"."$2}') | head -n1 | awk '{print $1}')

RUN pip3 install cython

RUN addgroup --system --gid 1337 service && \
    adduser --system --uid 1337 --gid 1337 --shell /bin/bash --disabled-password --home /opt/app service && \
    chown -R service:service /opt/app && \
    id service
#
# Setup Stage (copies local content)
#
FROM base AS setup

USER root

ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY main.py .

RUN chmod +x  /opt/app/main.py

COPY aws_google_auth ./aws_google_auth

RUN pip3 install fido2
#
# Runtime Stage switches to the service user
# and cleans up / hardens the environment.
#
FROM setup AS runtime

USER root

RUN chown -R service:service /opt/app

RUN rm -rf /var/cache/apt /var/cache/debconf /var/log/apt/eipp.log.xz /var/lib/apt /var/lib/dpkg && \
    echo "" > /var/log/bootstrap.log && \
    echo "" > /var/log/apt/history.log && \
    echo "" > /var/log/apt/term.log && \
    echo "" > /var/log/dpkg.log && \
    echo "" > /var/log/lastlog && \
    echo "" > /var/log/faillog && \
    rm -rf /usr/games /usr/local/games && \
    userdel games && \
    userdel news && \
    userdel www-data && \
    userdel irc && \
    userdel list && \
    userdel backup && \
    userdel mail && \
    userdel man

USER service

ENTRYPOINT [ "/opt/app/main.py" ]
