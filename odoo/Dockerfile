FROM camptocamp/odoo-project:10.0-2.2.0
MAINTAINER Camptocamp

# Install additional debian packages if needed
 RUN set -x; \
         apt-get update \
         && apt-get install -y --no-install-recommends \
         parallel \
         && apt-get clean \
         && rm -rf /var/lib/apt/lists/*

COPY ./before-migrate-entrypoint.d/* odoo/before-migrate-entrypoint.d/
COPY ./start-entrypoint.d/* odoo/start-entrypoint.d/
RUN chmod +x odoo/before-migrate-entrypoint.d/* \
    && chmod +x odoo/start-entrypoint.d/*

# Install additional python packages if needed
COPY ./requirements.txt /opt/odoo
RUN cd /opt/odoo && pip install -r requirements.txt

COPY ./importer.sh bin/

# Copy custom runtests file
COPY ./bin/runtests odoo/bin/

ENV ADDONS_PATH="/opt/odoo/local-src, \
  /opt/odoo/external-src/enterprise, \
  /opt/odoo/external-src/odoo-cloud-platform, \
  /opt/odoo/external-src/sale-workflow, \
  /opt/odoo/external-src/server-tools, \
  /opt/odoo/external-src/stock-logistics-warehouse, \
  /opt/odoo/external-src/stock-logistics-workflow, \
  /opt/odoo/external-src/l10n-belgium, \
  /opt/odoo/external-src/account-financial-tools, \
  /opt/odoo/external-src/bank-payment, \
  /opt/odoo/external-src/account-invoicing, \
  /opt/odoo/external-src/account-analytic, \
  /opt/odoo/external-src/connector, \
  /opt/odoo/external-src/queue, \
  /opt/odoo/src/addons" \
  LIMIT_TIME_CPU=86400 \
  LIMIT_TIME_REAL=86400 \
  LIMIT_MEMORY_SOFT=1342177280 \
  LIMIT_MEMORY_HARD=1610612736
