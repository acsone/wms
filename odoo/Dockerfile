FROM camptocamp/odoo-project:10.0-3.1.1
MAINTAINER Camptocamp

# Steps are grouped by dependency
# and ordered by compromizing cost and frequency

## Base requirements (Libs and packages)
# frequency: rarely
# cost:      high

COPY ./*requirements.txt /odoo/

RUN set -x; \
        apt-get update \
        && apt-get install -y --no-install-recommends \
        parallel \
        python-cups \
        # needed by pyodbc
        unixodbc \
        # common requirement for builds
        python-dev build-essential \
        # needed to build Cryptography
        libssl-dev libffi-dev \
        # needed to build pyodbc
        unixodbc-dev autoconf libtool pkg-config \
        && cd /odoo \
        && find . -maxdepth 1 -name "*requirements.txt" ! -name src_requirements.txt ! -name base_requirements.txt | xargs -I{} pip install -r {} \
        # cleaning of dev packages
        && apt-get remove -y build-essential python-dev \
        libssl-dev libffi-dev unixodbc-dev autoconf libtool pkg-config \
        && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false -o APT::AutoRemove::SuggestsImportant=false \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

## Tools of odoo-template
# frequency: seldom
# cost:      light

# Entrypoints
COPY ./before-migrate-entrypoint.d/* /before-migrate-entrypoint.d/
COPY ./start-entrypoint.d/* /start-entrypoint.d/
# FIXME Temp fix as bin/docker-entrypoint.sh is broken on docker-odoo-project-3.0.0
COPY ./before-migrate-entrypoint.d/* /odoo/before-migrate-entrypoint.d/
COPY ./start-entrypoint.d/* /odoo/start-entrypoint.d/

RUN chmod +x /before-migrate-entrypoint.d/* \
    && chmod +x /start-entrypoint.d/*
# CSV Loader
# `parallel` + `importer.sh` are needed to load heavy files
COPY ./bin/importer.sh /odoo-bin/
COPY ./bin/csv-split.py /odoo-bin/

## Prepare pip install
# frequency: never
# cost     : very light
COPY ./setup.py /odoo/

# Configure ODBC
COPY ./archives/iseriesaccess_7.1.0-1.0_amd64.deb /tmp
RUN dpkg -i /tmp/iseriesaccess_7.1.0-1.0_amd64.deb \
    && rm /tmp/iseriesaccess_7.1.0-1.0_amd64.deb \
    && ln -s /opt/ibm/iSeriesAccess/lib64/libcwbcore.so /usr/lib/libcwbcore.so \
    && mkdir /home/odoo
COPY ./.odbc.ini /home/odoo/.odbc.ini
# Place coveragerc where coverage will be launched
COPY ./.coveragerc /.coveragerc

COPY ./bin/install_cloud_platform.sh /odoo-bin/

## Main activity
# frequency: always
# costs:     very high to very light
COPY ./src /odoo/src
COPY ./external-src /odoo/external-src
COPY ./local-src /odoo/local-src
COPY ./data /odoo/data
COPY ./songs /odoo/songs
COPY ./VERSION /odoo/
COPY ./migration.yml /odoo/

# depends on ./setup.py ./src, ./songs and ./VERSION
RUN cd /odoo && pip install -r src_requirements.txt

## Environment
# frequency: sometimes
# cost:      very light
ENV ADDONS_PATH="/odoo/local-src, \
  /odoo/external-src/enterprise, \
  /odoo/external-src/odoo-cloud-platform, \
  /odoo/external-src/account-analytic, \
  /odoo/external-src/account-closing, \
  /odoo/external-src/account-financial-reporting, \
  /odoo/external-src/account-financial-tools, \
  /odoo/external-src/account-invoicing, \
  /odoo/external-src/account-reconcile, \
  /odoo/external-src/bank-payment, \
  /odoo/external-src/connector, \
  /odoo/external-src/l10n-belgium, \
  /odoo/external-src/product-attribute, \
  /odoo/external-src/purchase-workflow, \
  /odoo/external-src/queue, \
  /odoo/external-src/report-print-send, \
  /odoo/external-src/reporting-engine, \
  /odoo/external-src/sale-workflow, \
  /odoo/external-src/server-tools, \
  /odoo/external-src/stock-logistics-warehouse, \
  /odoo/external-src/stock-logistics-workflow, \
  /odoo/external-src/web, \
  /odoo/external-src/partner-contact, \
  /odoo/external-src/connector-interfaces, \
  /odoo/external-src/mis-builder, \
  /odoo/src/addons" \
  LIMIT_TIME_CPU=86400 \
  LIMIT_TIME_REAL=86400 \
  LIMIT_MEMORY_SOFT=1342177280 \
  LIMIT_MEMORY_HARD=1610612736
