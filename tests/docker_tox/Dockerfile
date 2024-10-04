
# Uses the latest version of Ubuntu as base image
FROM ubuntu:24.04

# Adds some metadata to the resulting Docker image via labels, the label names are standardized by the Open Container Initiative (OCI) in their Image
# Specification Annotation
LABEL org.opencontainers.image.authors="David Neumann <david.neumann@lecode.de>"
LABEL org.opencontainers.image.url="https://github.com/virelay/virelay"
LABEL org.opencontainers.image.documentation="https://github.com/lecode-official/lecode-server/tree/main/docs"
LABEL org.opencontainers.image.source="https://github.com/virelay/virelay/blob/master/tox.dockerfile"
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.vendor="ViRelAy"
LABEL org.opencontainers.image.licenses="AGPL-3.0-or-later"
LABEL org.opencontainers.image.title="tox"
LABEL org.opencontainers.image.description="A Ubuntu-based image, which can be used to run tox on all supported Python versions."

# Sets the working directory, into which the repository on which tox is run, will be mounted
RUN mkdir /opt/virelay
WORKDIR /opt/virelay

# Installs the packages required to add PPAs to the package manager, which is necessary to install to install older and newer Python versions
RUN apt-get update --assume-yes && \
    apt-get install --assume-yes --no-install-recommends software-properties-common && \
    rm -rf /var/lib/apt/lists/*

# By default, pipx installs the apps in the home directory of the user, but we want to install the apps in a system-wide directory, because this
# container is intended to be run as the same user as the user who runs the Docker container on the host system (when tox runs, it creates a .tox
# directory in the current working directory, which would be owned by the root user; the same is true for the documentation build, which creates a
# build and a doctree directory in the docs directory, which would also be owned by the root user; when first running tox using Docker and then
# running tox on the host system, would fail, because tox on the host system does not have the permissions to access these directories; running the
# Docker container as the same user as the user who runs the Docker container on the host system, ensures that the files created by tox and the
# documentation build are owned by the user)
ENV PIPX_HOME=/opt/pipx
ENV PIPX_BIN_DIR=/usr/local/bin

# Adds the deadsnakes PPA to the package manager, which contains older and newer Python versions, installs all Python versions supported by the
# project, which will be used to run the unit tests, installs git, which is required by setuptools to install the project in the virtual environments
# created by tox, installs pipx, which is used to install the latest version of tox (Ubuntu 24.04 ships with an outdated version of tox), and finally
# installs tox
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update --assume-yes && \
    apt-get install --assume-yes --no-install-recommends \
        git \
        python3.10-dev \
        python3.11-dev \
        python3.12-dev \
        pipx && \
    pipx install tox && \
    rm -rf /var/lib/apt/lists/*

# Sets the entrypoint of the Docker container to "tox", so that users can directly add the tox command line arguments to the "docker run" command;
# also, sets the working directory of tox to a directory inside the container, so that running tox inside the container does not mess up the tox
# files on the host system; this directory is ephemeral and will be deleted when the container is removed
ENTRYPOINT ["tox", "--workdir", "/opt/tox"]
