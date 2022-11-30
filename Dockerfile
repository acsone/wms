# syntax=docker/dockerfile:1.4
FROM ghcr.io/acsone/odoo-bedrock:16.0-py310-latest

RUN set -e \
  && apt update \
  && apt -y install --no-install-recommends postgresql-client \
  && apt -y clean \
  && rm -rf /var/lib/apt/lists/*

# install dependencies that change infrequently first, so that they are cached as a layer
COPY requirements.txt /tmp/requirements.txt
RUN --mount=type=bind,target=/release,source=.,from=release \
  pip install --no-deps --no-index /release/*.whl

COPY ./container/entrypoint-dbbase /odoo/start-entrypoint.d/

# Install the app in editable mode
COPY . /app
RUN --mount=type=bind,target=/release-build,source=.,from=release-build \
  pip install --no-deps --no-index --find-links /release-build --editable /app
