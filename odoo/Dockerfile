FROM camptocamp/odoo-project:10.0-2.0.0
MAINTAINER Camptocamp

# Install additional debian packages if needed
 RUN set -x; \
         apt-get update \
         && apt-get install -y --no-install-recommends \
         parallel \
         && apt-get clean \
         && rm -rf /var/lib/apt/lists/*

# Install additional python packages if needed
COPY ./requirements.txt /opt/odoo
RUN cd /opt/odoo && pip install -r requirements.txt

COPY ./importer.sh bin/

ENV ADDONS_PATH="/opt/odoo/local-src, \
  /opt/odoo/external-src/enterprise, \
  /opt/odoo/external-src/odoo-cloud-platform, \
  /opt/odoo/external-src/sale-workflow, \
  /opt/odoo/external-src/server-tools, \
  /opt/odoo/external-src/stock-logistics-workflow, \
  /opt/odoo/external-src/l10n-belgium, \
  /opt/odoo/external-src/account-financial-tools, \
  /opt/odoo/external-src/bank-payment, \
  /opt/odoo/external-src/account-invoicing, \
  /opt/odoo/src/addons" \
  LIMIT_TIME_CPU=86400 \
  LIMIT_TIME_REAL=86400 \
  LIMIT_MEMORY_SOFT=1342177280 \
  LIMIT_MEMORY_HARD=1610612736
