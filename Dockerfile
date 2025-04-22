# syntax=docker/dockerfile:1.4

#######################################################################################
# base stage, with the non-python runtime dependencies
#

FROM ghcr.io/acsone/odoo-bedrock:16.0-py311-jammy-latest as base

# Install apt runtime dependencies.
# - postgresql-client for comfort in the shell container and for db dump to work
# - expect to have unbuffer in CI
# - gettext for click-odoo-makepot in CI
RUN set -e \
  && apt update \
  && apt -y install --no-install-recommends \
       postgresql-client \
       expect \
       gettext \
       libcups2 \
       xmlsec1 \
  && apt -y clean \
  && rm -rf /var/lib/apt/lists/*

  # we'll use build isolation so we don't need setuptools and wheel in the venv
RUN pip uninstall -y setuptools wheel

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

#######################################################################################
# builds-deps stage, where we download requirements-build.txt,
# and install tools necessary to build source distributions.
#

FROM base as build-deps

# Install git.
RUN set -e \
  && apt update \
  && apt -y install --no-install-recommends \
       git \
       openssh-client \
       python3.11-dev \
       build-essential \
       libpq-dev \
       libcups2-dev \
       libxmlsec1-dev \
       pkg-config \
  && apt -y clean \
  && rm -rf /var/lib/apt/lists/*

# Configure ssh.
RUN mkdir $HOME/.ssh \
 && ssh-keyscan github.com >> $HOME/.ssh/known_hosts \
 && ssh-keyscan gitlab.acsone.eu >> $HOME/.ssh/known_hosts


# Install the app dependencies in the venv. We use --no-deps to avoid installing
# things that would not have been locked.
COPY requirements*.txt /tmp/
RUN --mount=type=ssh \
    --mount=type=cache,target=/root/.cache/uv,id=uv-jammy \
    --mount=from=ghcr.io/astral-sh/uv:latest,source=/uv,target=/bin/uv \
    uv pip install \
      --no-deps \
      --build-constraint=/tmp/requirements-build.txt \
      -r /tmp/requirements.txt \
      -r /tmp/requirements-test.txt \
 && find $VIRTUAL_ENV/lib/python3.*/site-packages/odoo/addons/*/i18n -type f ! -name 'fr*.po' ! -name 'nl*.po' ! -name 'en*.po' ! -name '*.pot' -delete


 #######################################################################################
# dependencies stage, copy the venv from build-deps, so we have a light layer
# without all the build tools.
#

FROM base as dependencies


# Install python dependencies we built in the build stage.
# Use --no-deps and --no-index to be sure to not download anything else.

COPY --from=build-deps /odoo /odoo

# Additional entry point scripts.
COPY ./container/entrypoint-dbbase /odoo/start-entrypoint.d/


#######################################################################################
# runtime stage, installs the app in editable mode, on top of dependencies.
#

FROM dependencies AS runtime

# Install the app in editable mode.
# TODO Ideally, we should use --no-index here to check that everything is installed
# but that prevents accessing the build dependencies.
COPY . /app
RUN python -m compileall /app
RUN --mount=type=cache,target=/root/.cache/uv,id=uv-jammy \
    --mount=from=ghcr.io/astral-sh/uv:latest,source=/uv,target=/bin/uv \
  uv pip install \
      --no-deps \
      --build-constraint=/app/requirements-build.txt \
      --editable /app
