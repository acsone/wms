FROM quay.io/acsone/odoo-bedrock:10.0-py27-latest

RUN set -e \
  && apt update \
  && apt -y install --no-install-recommends postgresql-client \
  && apt -y clean \
  && rm -rf /var/lib/apt/lists/*

COPY ./container/entrypoint-dbbase /odoo/start-entrypoint.d/

# use this COPY for a regular docker build, otherwise use
# podman build --volume ${PWD}/release:/tmp/release
# to get a smaller image
#COPY ./release /tmp/release

RUN pip install --no-index --no-deps /tmp/release/*.whl
