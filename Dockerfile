FROM ghcr.io/acsone/odoo-bedrock:16.0-py310-latest

RUN set -e \
  && apt update \
  && apt -y install --no-install-recommends postgresql-client \
  && apt -y clean \
  && rm -rf /var/lib/apt/lists/*

COPY ./container/entrypoint-dbbase /odoo/start-entrypoint.d/

# Install dependencies first, separately from the project.
# They don't change so often, so by doing this we benefit from the layers cache.
COPY ./release-deps /tmp/release-deps
RUN pip install --no-index --no-deps /tmp/release-deps/*.whl

# Now install the project.
# This is the part that changes most often so we do it last.
COPY ./release /tmp/release
RUN pip install --no-index --no-deps /tmp/release/*.whl

