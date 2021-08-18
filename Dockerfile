FROM quay.io/acsone/odoo-bedrock:10.0-py27-latest

RUN set -e \
  && apt update \
  && apt -y install --no-install-recommends postgresql-client \
  && apt -y clean \
  && rm -rf /var/lib/apt/lists/*

COPY ./container/entrypoint-dbbase /odoo/start-entrypoint.d/

# Install dependencies first, separately from the project.
# They don't change so often, so by doing this we benefit from the layers cache.
COPY ./release /tmp/release
RUN pip install --no-index --no-deps /tmp/release/*.whl

# Now install the project.
# This is the part that changes most often so we do it last.
COPY ./release-project /tmp/release-project
RUN pip install --no-index --no-deps /tmp/release-project/*.whl
