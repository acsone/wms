FROM camptocamp/odoo-project:9.0
MAINTAINER Camptocamp

# Install additional debian packages if needed
# RUN set -x; \
#         apt-get update \
#         && apt-get install -y --no-install-recommends \
#         python-shapely \
#         && apt-get clean \
#         && rm -rf /var/lib/apt/lists/*

# Install additional python packages if needed
# COPY ./requirements.txt ./
# RUN pip install -r requirements.txt

ENV ADDONS_PATH="/opt/odoo/local-src, \
  /opt/odoo/external-src/enterprise, \
  /opt/odoo/external-src/server-tools, \
  /opt/odoo/external-src/stock-logistics-workflow, \
  /opt/odoo/src/addons"
