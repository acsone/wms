FROM camptocamp/odoo-project:10.0-2.6.1
MAINTAINER Camptocamp

COPY ./requirements.txt /opt/odoo

RUN set -x; \
         apt-get update \
         && apt-get install -y --no-install-recommends \
         parallel \
         python-cups \
         # needed by pyodbc
         unixodbc \
         # common requirement for builds
         build-essential python-dev \
         # needed to build Cryptography
         libssl-dev libffi-dev \
         # needed to build pyodbc
         unixodbc-dev autoconf libtool pkg-config \
         && cd /opt/odoo \
         && pip install -r requirements.txt \
         && apt-get remove -y build-essential libssl-dev libffi-dev python-dev \
         unixodbc-dev autoconf libtool pkg-config \
         && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false -o APT::AutoRemove::SuggestsImportant=false \
         && apt-get clean \
         && rm -rf /var/lib/apt/lists/*

COPY ./before-migrate-entrypoint.d/* odoo/before-migrate-entrypoint.d/
COPY ./start-entrypoint.d/* odoo/start-entrypoint.d/
RUN chmod +x odoo/before-migrate-entrypoint.d/* \
    && chmod +x odoo/start-entrypoint.d/*

# Install additional python packages if needed
COPY ./requirements.txt /opt/odoo
RUN cd /opt/odoo && pip install -r requirements.txt

# Configure ODBC
COPY ./archives/iseriesaccess_7.1.0-1.0_amd64.deb /tmp
RUN dpkg -i /tmp/iseriesaccess_7.1.0-1.0_amd64.deb \
    && rm /tmp/iseriesaccess_7.1.0-1.0_amd64.deb \
    && ln -s /opt/ibm/iSeriesAccess/lib64/libcwbcore.so /usr/lib/libcwbcore.so \
    && mkdir /home/odoo
COPY ./.odbc.ini /home/odoo/.odbc.ini

COPY ./bin/importer.sh bin/
COPY ./bin/install_cloud_platform.sh bin/
COPY ./bin/csv-split.py bin/

# Copy custom runtests file
COPY ./bin/runtests odoo/bin/
COPY ./bin/runmigration odoo/bin/
COPY ./bin/list_dependencies.py odoo/bin/

ENV ADDONS_PATH="/opt/odoo/local-src, \
  /opt/odoo/external-src/enterprise, \
  /opt/odoo/external-src/odoo-cloud-platform, \
  /opt/odoo/external-src/account-analytic, \
  /opt/odoo/external-src/account-closing, \
  /opt/odoo/external-src/account-financial-tools, \
  /opt/odoo/external-src/account-invoicing, \
  /opt/odoo/external-src/bank-payment, \
  /opt/odoo/external-src/connector, \
  /opt/odoo/external-src/l10n-belgium, \
  /opt/odoo/external-src/product-attribute, \
  /opt/odoo/external-src/purchase-workflow, \
  /opt/odoo/external-src/queue, \
  /opt/odoo/external-src/report-print-send, \
  /opt/odoo/external-src/sale-workflow, \
  /opt/odoo/external-src/server-tools, \
  /opt/odoo/external-src/stock-logistics-warehouse, \
  /opt/odoo/external-src/stock-logistics-workflow, \
  /opt/odoo/external-src/web, \
  /opt/odoo/external-src/partner-contact, \
  /opt/odoo/external-src/connector-interfaces, \
  /opt/odoo/src/addons" \
  LIMIT_TIME_CPU=86400 \
  LIMIT_TIME_REAL=86400 \
  LIMIT_MEMORY_SOFT=1342177280 \
  LIMIT_MEMORY_HARD=1610612736
